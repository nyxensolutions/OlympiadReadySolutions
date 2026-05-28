"""
fix_image_questions.py
======================
Fixes bad/decorative image questions in OlympiadReady (Gr 11 & 12).

PHASE 1 - STRIP: Remove imageUrl from English, Commerce, and unrelated stock photos.
PHASE 2 - STRIP: Subject-specific questions with irrelevant generic images.
PHASE 3 - GENERATE: Proper matplotlib / PIL images for diagram-based questions.
"""

import os, io, re, time, sys
import pyodbc, requests
import cloudinary, cloudinary.uploader
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── Config ───────────────────────────────────────────────────────────────────
DB_CONN = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tcp:olympiadready-np.database.windows.net,1433;"
    "DATABASE=OlympiadReady;UID=nyxen-admin;PWD=Olympiad@2026;"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
)
CLOUDINARY_CLOUD_NAME = "dyommthef"
CLOUDINARY_API_KEY    = "414698218814162"
CLOUDINARY_API_SECRET = "fIHmpWwiIllKPs2qbEeHVNzMMP4"
CLOUDINARY_FOLDER     = "olympiadready/questions"

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME, api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET, secure=True)

RUN_ID = int(time.time())
stats  = {"stripped": 0, "generated": 0, "errors": 0}


# ── DB helpers ────────────────────────────────────────────────────────────────
def get_conn():
    return pyodbc.connect(DB_CONN)


def strip_question(qid, img_url, conn):
    """Set ImageUrl = NULL and delete from Cloudinary."""
    conn.execute("UPDATE QuestionBank SET ImageUrl = NULL WHERE QuestionBankId = ?", qid)
    conn.commit()
    _cdn_delete(img_url)
    stats["stripped"] += 1


def update_question_image(qid, new_url, conn):
    conn.execute("UPDATE QuestionBank SET ImageUrl = ? WHERE QuestionBankId = ?", new_url, qid)
    conn.commit()
    stats["generated"] += 1


# ── Cloudinary helpers ────────────────────────────────────────────────────────
def _cdn_delete(url):
    if not url: return
    m = re.search(r"/upload/(?:v\d+/)?(.+?)(?:\.\w+)?$", url)
    if m:
        try:
            cloudinary.uploader.destroy(m.group(1), resource_type="image")
        except Exception as e:
            print(f"    [CDN DEL] {m.group(1)[:40]}: {e}")


def upload_fig(fig, suffix):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    buf.seek(0); plt.close(fig)
    pub_id = f"{CLOUDINARY_FOLDER}/gen_{suffix}_{RUN_ID}"
    res = cloudinary.uploader.upload(buf, public_id=pub_id, overwrite=True, resource_type="image")
    return res["secure_url"]


def upload_pil(img, suffix):
    buf = io.BytesIO()
    img.save(buf, format="PNG"); buf.seek(0)
    pub_id = f"{CLOUDINARY_FOLDER}/gen_{suffix}_{RUN_ID}"
    res = cloudinary.uploader.upload(buf, public_id=pub_id, overwrite=True, resource_type="image")
    return res["secure_url"]


# ── Strip helper (batch by subject+grade or individual IDs) ──────────────────
def strip_by_subject_grade(subject, grade, conn):
    cur = conn.cursor()
    cur.execute("""SELECT QuestionBankId, ImageUrl FROM QuestionBank
                   WHERE Subject=? AND Grade=? AND ImageUrl LIKE '%dyommthef%'""",
                subject, grade)
    rows = cur.fetchall()
    for (qid, url) in rows:
        strip_question(qid, url, conn)
        time.sleep(0.2)
    return len(rows)


def strip_by_ids(id_list, conn):
    cur = conn.cursor()
    for qid in id_list:
        cur.execute("SELECT ImageUrl FROM QuestionBank WHERE QuestionBankId=?", qid)
        row = cur.fetchone()
        if row and row[0] and "dyommthef" in (row[0] or ""):
            strip_question(qid, row[0], conn)
            time.sleep(0.2)


def strip_by_topic(subject, grade, topic, subtopic, conn):
    cur = conn.cursor()
    cur.execute("""SELECT QuestionBankId, ImageUrl FROM QuestionBank
                   WHERE Subject=? AND Grade=? AND Topic=? AND SubTopic=?
                   AND (ImageUrl LIKE '%dyommthef%' OR ImageUrl IS NULL)""",
                subject, grade, topic, subtopic)
    rows = cur.fetchall()
    for (qid, url) in rows:
        strip_question(qid, url, conn)
        time.sleep(0.2)
    return len(rows)


# ── Generate-and-update helper ────────────────────────────────────────────────
def gen_update(subject, grade, topic, subtopic, make_fn, suffix, conn):
    """
    make_fn: callable returning matplotlib Figure OR PIL Image.
    Replaces the existing cloudinary image for the matching question.
    """
    cur = conn.cursor()
    cur.execute("""SELECT QuestionBankId, ImageUrl FROM QuestionBank
                   WHERE Subject=? AND Grade=? AND Topic=? AND SubTopic=?
                   AND (ImageUrl LIKE '%dyommthef%' OR ImageUrl IS NULL)""",
                subject, grade, topic, subtopic)
    rows = cur.fetchall()
    if not rows:
        print(f"    [NOT FOUND] {subject} G{grade} / {subtopic}")
        return
    for (qid, old_url) in rows:
        try:
            result = make_fn()
            if isinstance(result, Image.Image):
                new_url = upload_pil(result, suffix)
            else:
                new_url = upload_fig(result, suffix)
            _cdn_delete(old_url)
            update_question_image(qid, new_url, conn)
            print(f"    GEN OK  {subject} G{grade} — {subtopic}")
            time.sleep(1.2)
        except Exception as e:
            print(f"    [GEN ERR] {subject} G{grade} / {subtopic}: {e}")
            stats["errors"] += 1


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                     IMAGE GENERATORS                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def make_clock(hour, minute):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(plt.Circle((0,0), 1.15, color="#fffdf4", ec="#222", lw=3))
    for i in range(12):
        a = np.radians(90 - i*30)
        ax.plot([0.88*np.cos(a), 1.02*np.cos(a)], [0.88*np.sin(a), 1.02*np.sin(a)], "k-", lw=2.5)
        ax.text(0.74*np.cos(a), 0.74*np.sin(a), str(i or 12),
                ha="center", va="center", fontsize=10, fontweight="bold")
    for i in range(60):
        if i % 5: ax.plot([0.94*np.cos(np.radians(90-i*6)), 1.02*np.cos(np.radians(90-i*6))],
                          [0.94*np.sin(np.radians(90-i*6)), 1.02*np.sin(np.radians(90-i*6))], "k-", lw=0.7)
    ha = np.radians(90 - (hour%12)*30 - minute*0.5)
    ma = np.radians(90 - minute*6)
    ax.plot([0, 0.55*np.cos(ha)], [0, 0.55*np.sin(ha)], "#111", lw=5, solid_capstyle="round")
    ax.plot([0, 0.82*np.cos(ma)], [0, 0.82*np.sin(ma)], "#111", lw=3, solid_capstyle="round")
    ax.plot(0, 0, "ko", ms=6)
    ax.set_title(f"Clock showing {hour}:{minute:02d}", fontsize=12, pad=8)
    return fig


def make_bar_chart(labels, values, title, ylabel, color="steelblue"):
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, values, color=color, edgecolor="white", lw=1.5)
    for b, v in zip(bars, values):
        ax.text(b.get_x()+b.get_width()/2, v+max(values)*0.02, str(v),
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.set_ylim(0, max(values)*1.2); fig.tight_layout()
    return fig


def make_pie_chart(labels, sizes, title):
    fig, ax = plt.subplots(figsize=(6, 5))
    cols = ["#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f"]
    _, _, autotexts = ax.pie(sizes, labels=labels, autopct="%1.0f%%",
                             startangle=140, colors=cols, pctdistance=0.75,
                             wedgeprops=dict(edgecolor="white", lw=2))
    for t in autotexts: t.set_fontsize(10); t.set_fontweight("bold")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)
    fig.tight_layout(); return fig


def make_venn2(a_only, b_only, both, a_lbl, b_lbl, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax.add_patch(mpatches.Circle((3.5, 3), 2.2, alpha=0.35, color="royalblue"))
    ax.add_patch(mpatches.Circle((6.5, 3), 2.2, alpha=0.35, color="tomato"))
    ax.text(1.8, 5.2, a_lbl, fontsize=12, fontweight="bold", color="navy", ha="center")
    ax.text(8.2, 5.2, b_lbl, fontsize=12, fontweight="bold", color="darkred", ha="center")
    ax.text(2.6, 3, str(a_only), fontsize=16, fontweight="bold", ha="center", va="center")
    ax.text(5.0, 3, str(both),   fontsize=16, fontweight="bold", ha="center", va="center")
    ax.text(7.4, 3, str(b_only), fontsize=16, fontweight="bold", ha="center", va="center")
    ax.text(2.6, 1.2, f"Only {a_lbl}", fontsize=9, color="gray", ha="center")
    ax.text(5.0, 1.2, "Both",       fontsize=9, color="gray", ha="center")
    ax.text(7.4, 1.2, f"Only {b_lbl}", fontsize=9, color="gray", ha="center")
    fig.tight_layout(); return fig


def make_line_graph(xlbls, yvals, title, ylabel):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(xlbls, yvals, "o-", color="steelblue", lw=2.5, ms=8,
            markerfacecolor="white", markeredgewidth=2)
    for x, y in zip(xlbls, yvals):
        ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout(); return fig


def make_table(headers, rows, title):
    fig, ax = plt.subplots(figsize=(max(5, len(headers)*1.5), len(rows)*0.6+1.4))
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    tbl = ax.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(11); tbl.scale(1.2, 1.6)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor("#2c5f8a"); cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#e8f0f7")
        cell.set_edgecolor("#cccccc")
    fig.tight_layout(); return fig


def make_prob_tree(pA, pBgA, pBgnA):
    pnA = round(1-pA,2); pnBgA = round(1-pBgA,2); pnBgnA = round(1-pBgnA,2)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.set_xlim(0, 10); ax.set_ylim(-0.5, 11); ax.axis("off")
    ax.set_title("Probability Tree Diagram", fontsize=13, fontweight="bold")
    def arrow(x1,y1,x2,y2,col,lbl,lx,ly):
        ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle="->", color=col, lw=2))
        ax.text(lx,ly,lbl,fontsize=11,color=col,fontweight="bold",ha="center")
    ax.plot(0.5,5.5,"ko",ms=9); ax.text(0.1,5.7,"S",fontsize=10)
    arrow(0.5,5.5,3.5,8.0,"royalblue",f"P(A)={pA}",1.9,7.1)
    arrow(0.5,5.5,3.5,3.0,"tomato",  f"P(A')={pnA}",1.9,3.9)
    ax.plot(3.5,8.0,"o",color="royalblue",ms=9); ax.text(3.7,8.2,"A",fontsize=12,fontweight="bold",color="royalblue")
    ax.plot(3.5,3.0,"o",color="tomato",ms=9);    ax.text(3.7,2.6,"A'",fontsize=12,fontweight="bold",color="tomato")
    arrow(3.5,8.0,7.5,9.8,"royalblue",f"P(B|A)={pBgA}",5.4,9.4)
    arrow(3.5,8.0,7.5,6.5,"royalblue",f"P(B'|A)={pnBgA}",5.4,7.4)
    arrow(3.5,3.0,7.5,4.0,"tomato",f"P(B|A')={pBgnA}",5.4,3.9)
    arrow(3.5,3.0,7.5,1.5,"tomato",f"P(B'|A')={pnBgnA}",5.4,2.2)
    ax.text(7.7,9.8,f"A∩B  [{round(pA*pBgA,3)}]",fontsize=10,fontweight="bold")
    ax.text(7.7,6.5,f"A∩B' [{round(pA*pnBgA,3)}]",fontsize=10)
    ax.text(7.7,4.0,f"A'∩B [{round(pnA*pBgnA,3)}]",fontsize=10,fontweight="bold")
    ax.text(7.7,1.5,f"A'∩B'[{round(pnA*pnBgnA,3)}]",fontsize=10)
    pB = round(pA*pBgA+pnA*pBgnA,3)
    ax.text(0.2,-0.3,f"P(B)={pA}×{pBgA}+{pnA}×{pBgnA}={pB}  |  P(A|B)={round(pA*pBgA/pB,4)}",
            fontsize=10,color="#333",style="italic")
    fig.tight_layout(); return fig


def make_lp_region():
    fig, ax = plt.subplots(figsize=(6, 5.5))
    x = np.linspace(0, 8, 400)
    # Constraints: x+y<=6, 2x+y<=10, x>=0, y>=0
    verts = [(0,0),(0,6),(4,2),(5,0)]
    ax.add_patch(mpatches.Polygon(verts, closed=True, alpha=0.3,
                                   color="royalblue", label="Feasible Region"))
    ax.plot(x, np.clip(6-x, 0, 12),  "b-", lw=2, label="x + y = 6")
    ax.plot(x, np.clip(10-2*x, 0, 12),"r-", lw=2, label="2x + y = 10")
    ax.axhline(0, color="#444", lw=1.5); ax.axvline(0, color="#444", lw=1.5)
    for (px,py) in verts:
        Z = 5*px+3*py
        ax.plot(px, py, "ko", ms=8, zorder=5)
        ax.annotate(f"({px},{py})\nZ={Z}", (px,py), textcoords="offset points",
                    xytext=(10,6), fontsize=9, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color="#888", lw=0.8))
    ax.set_xlim(-0.5, 8); ax.set_ylim(-0.5, 8)
    ax.set_xlabel("x", fontsize=13); ax.set_ylabel("y", fontsize=13)
    ax.set_title("Linear Programming\nMaximise Z = 5x + 3y", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10, loc="upper right")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout(); return fig


def make_parabola():
    fig, ax = plt.subplots(figsize=(6, 5))
    y = np.linspace(-9, 9, 600); x = y**2/12
    ax.plot(x, y, "b-", lw=2.5, label="y² = 12x")
    ax.axvline(-3, color="r", ls="--", lw=2, label="Directrix x = −3")
    ax.plot(3, 0, "r*", ms=14, label="Focus (3, 0)")
    ax.axhline(0, color="#888", lw=1); ax.axvline(0, color="#888", lw=1)
    ax.set_xlim(-5, 10); ax.set_ylim(-9, 9)
    ax.set_xlabel("x", fontsize=12); ax.set_ylabel("y", fontsize=12)
    ax.set_title("Parabola: y² = 12x  (a=3)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10); ax.grid(True, alpha=0.2)
    fig.tight_layout(); return fig


def make_tangent_y_x2():
    fig, ax = plt.subplots(figsize=(5.5, 5))
    x = np.linspace(-0.5, 3.5, 400)
    ax.plot(x, x**2, "b-", lw=2.5, label="y = x²")
    tx, slope = 2, 4
    ty = tx**2
    t_x = np.linspace(tx-1.5, tx+1.5, 100)
    ax.plot(t_x, ty+slope*(t_x-tx), "r--", lw=2, label=f"Tangent at x={tx} (slope={slope})")
    ax.plot(tx, ty, "ro", ms=9, zorder=5)
    ax.annotate(f"({tx},{ty})", (tx,ty), textcoords="offset points", xytext=(10,8), fontsize=11)
    ax.axhline(0, color="#888", lw=1); ax.axvline(0, color="#888", lw=1)
    ax.set_xlim(-0.5, 3.5); ax.set_ylim(-1, 13)
    ax.set_xlabel("x", fontsize=12); ax.set_ylabel("y", fontsize=12)
    ax.set_title("y = x²  — Tangent at x = 2\nSlope = f'(2) = 2×2 = 4", fontsize=11, fontweight="bold")
    ax.legend(fontsize=10); ax.grid(True, alpha=0.2)
    fig.tight_layout(); return fig


def make_pascal():
    from math import comb
    rows = 6
    tri = [[comb(n,k) for k in range(n+1)] for n in range(rows)]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    ax.set_title("Pascal's Triangle (highlight: row 5, coefficient of x³ = ¹⁰)", fontsize=12, fontweight="bold", pad=10)
    for n, row in enumerate(tri):
        for k, val in enumerate(row):
            xp = (rows-1-n) + 2*k; yp = rows-1-n
            highlighted = (n==5 and val==10)
            fc = "#e65c00" if highlighted else ("#ddeeff" if (n+k)%2==0 else "#f5f9ff")
            ax.add_patch(mpatches.FancyBboxPatch((xp-0.46,yp-0.46),0.92,0.92,
                         boxstyle="round,pad=0.05", facecolor=fc, edgecolor="#aaa", lw=0.8))
            ax.text(xp, yp, str(val), ha="center", va="center", fontsize=11, fontweight="bold",
                    color="white" if highlighted else "#1a3a5c")
    ax.set_xlim(-1, 2*rows+1); ax.set_ylim(-0.8, rows)
    ax.text(5, -0.6, "Row 5: 1  5  10  10  5  1  → coeff of x³ = 10 (highlighted)",
            ha="center", fontsize=10, color="gray", style="italic")
    fig.tight_layout(); return fig


def make_y_abs_x():
    fig, ax = plt.subplots(figsize=(5, 4))
    x = np.linspace(-4, 4, 400)
    ax.plot(x, np.abs(x), "b-", lw=2.5, label="y = |x|")
    ax.plot(0, 0, "ro", ms=10, zorder=5, label="x=0: sharp corner\n(NOT differentiable)")
    ax.axhline(0, color="#888", lw=1); ax.axvline(0, color="#888", lw=1)
    ax.set_xlim(-4.5, 4.5); ax.set_ylim(-0.5, 4.5)
    ax.set_xlabel("x", fontsize=12); ax.set_ylabel("y", fontsize=12)
    ax.set_title("y = |x|: continuous everywhere\nnot differentiable at x = 0", fontsize=11, fontweight="bold")
    ax.legend(fontsize=10, loc="upper center"); ax.grid(True, alpha=0.2)
    fig.tight_layout(); return fig


def make_maxmin_curve():
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    x = np.linspace(-1.5, 2.5, 400)
    y = -(x**3) + 3*x  # local max at x=1 (y=2), local min at x=-1 (y=-2)
    ax.plot(x, y, "b-", lw=2.5, label="f(x) = −x³ + 3x")
    ax.plot(1, 2, "g^", ms=12, zorder=5, label="Local Max P (1, 2)\nf'=0, f''<0")
    ax.plot(-1, -2, "rv", ms=12, zorder=5, label="Local Min Q (−1, −2)\nf'=0, f''>0")
    ax.axhline(0, color="#888", lw=1); ax.axvline(0, color="#888", lw=1)
    ax.annotate("P(1,2)\nLocal Max", (1,2), textcoords="offset points", xytext=(15,10), fontsize=10)
    ax.annotate("Q(−1,−2)\nLocal Min", (-1,-2), textcoords="offset points", xytext=(10,-30), fontsize=10)
    ax.set_xlabel("x", fontsize=12); ax.set_ylabel("f(x)", fontsize=12)
    ax.set_title("f(x) = −x³ + 3x\nMaxima and Minima", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, loc="upper right"); ax.grid(True, alpha=0.2)
    fig.tight_layout(); return fig


def make_integral_area():
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    x = np.linspace(-0.3, 3.5, 400)
    ax.plot(x, x**2, "b-", lw=2.5, label="y = x²")
    xs = np.linspace(0, 3, 300)
    ax.fill_between(xs, xs**2, alpha=0.35, color="orange", label="Area = ∫₀³ x² dx = 9")
    ax.axhline(0, color="#888", lw=1); ax.axvline(0, color="#888", lw=1)
    ax.set_xlim(-0.3, 3.8); ax.set_ylim(-0.3, 10)
    ax.set_xlabel("x", fontsize=12); ax.set_ylabel("y", fontsize=12)
    ax.set_title("Area under y = x² from x=0 to x=3\n= [x³/3]₀³ = 9 sq units", fontsize=11, fontweight="bold")
    ax.legend(fontsize=10); ax.grid(True, alpha=0.2)
    fig.tight_layout(); return fig


def make_exp_growth():
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.linspace(0, 3, 300)
    for k, lbl, col in [(0.5,"k=0.5","steelblue"),(1.0,"k=1.0","tomato"),(1.5,"k=1.5","seagreen")]:
        ax.plot(x, np.exp(k*x), lw=2.5, color=col, label=f"y=y₀·e^({lbl}·x)")
    ax.set_xlabel("x", fontsize=12); ax.set_ylabel("y / y₀", fontsize=12)
    ax.set_title("dy/dx = ky  →  y = y₀ eᵏˣ\n(Exponential Growth)", fontsize=11, fontweight="bold")
    ax.legend(fontsize=10); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.grid(True, alpha=0.2); fig.tight_layout(); return fig


def make_matrix_display():
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    ax.axis("off")
    ax.set_title("Matrix A  and  det(A)", fontsize=13, fontweight="bold", pad=15)
    tbl = ax.table(
        cellText=[["2", "3"], ["1", "4"]],
        colLabels=["Col 1", "Col 2"],
        rowLabels=["Row 1", "Row 2"],
        loc="center", cellLoc="center"
    )
    tbl.auto_set_font_size(False); tbl.set_fontsize(16); tbl.scale(2, 2)
    for (r,c), cell in tbl.get_celld().items():
        cell.set_facecolor("#ddeeff" if r>0 else "#2c5f8a")
        cell.set_text_props(color="white" if r==0 else "#1a3a5c", fontweight="bold")
        cell.set_edgecolor("#aaa")
    ax.text(0.5, 0.08, "det(A) = (2×4) − (3×1) = 8 − 3 = 5",
            ha="center", va="center", transform=ax.transAxes,
            fontsize=12, color="#333", style="italic")
    fig.tight_layout(); return fig


def make_mapping_diagram():
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.axis("off")
    ax.set_title("Bijective Mapping (One-One and Onto)", fontsize=12, fontweight="bold")
    ax.add_patch(mpatches.Ellipse((1.5,2.5),1.4,4.5,fc="#ddeeff",ec="#333",lw=2))
    ax.add_patch(mpatches.Ellipse((5.5,2.5),1.4,4.5,fc="#ffe0cc",ec="#333",lw=2))
    ax.text(1.5,5.1,"Domain",ha="center",fontsize=11,fontweight="bold",color="navy")
    ax.text(5.5,5.1,"Codomain",ha="center",fontsize=11,fontweight="bold",color="darkred")
    dom=[1,2,3,4]; cod={"a":4,"b":3,"c":2,"d":1}; mapping={1:"b",2:"d",3:"a",4:"c"}
    dom_y=[4,3,2,1]; colors=["steelblue","tomato","seagreen","darkorange"]
    for v,y in zip(dom,dom_y):
        ax.plot(1.5,y,"o",color="navy",ms=10,zorder=4)
        ax.text(0.9,y,str(v),ha="center",va="center",fontsize=12,fontweight="bold",color="navy")
    for v,(ky,vy) in zip(cod.keys(), cod.items()):
        ax.plot(5.5,cod[v],"o",color="darkred",ms=10,zorder=4)
        ax.text(6.2,cod[v],v,ha="center",va="center",fontsize=12,fontweight="bold",color="darkred")
    for (dk,dv),c in zip(mapping.items(),colors):
        ax.annotate("",xy=(5.15,cod[dv]),xytext=(1.85,dom_y[dom.index(dk)]),
                    arrowprops=dict(arrowstyle="->",color=c,lw=1.8))
    ax.set_xlim(0,7); ax.set_ylim(0,6); fig.tight_layout(); return fig


def make_bst():
    nodes={"50":(5,7),"30":(3,5),"70":(7,5),"20":(2,3),"40":(4,3),"60":(6,3),"80":(8,3)}
    edges=[("50","30"),("50","70"),("30","20"),("30","40"),("70","60"),("70","80")]
    fig, ax = plt.subplots(figsize=(8,5)); ax.axis("off")
    ax.set_title("BST: Insertions 50,30,70,20,40,60,80\nIn-order: 20→30→40→50→60→70→80",
                 fontsize=11,fontweight="bold")
    for (p,c) in edges:
        px,py=nodes[p]; cx,cy=nodes[c]
        ax.annotate("",xy=(cx,cy+0.42),xytext=(px,py-0.42),
                    arrowprops=dict(arrowstyle="->",color="#555",lw=1.5))
    for v,(x,y) in nodes.items():
        col="#e65c00" if v=="50" else "#4e9ab5"
        ax.add_patch(plt.Circle((x,y),0.42,color=col,zorder=3))
        ax.text(x,y,v,ha="center",va="center",fontsize=13,fontweight="bold",color="white",zorder=4)
    ax.set_xlim(0.5,10); ax.set_ylim(1.5,8.5)
    fig.tight_layout(); return fig


def make_sorted_array_bsearch():
    arr=[2,5,8,12,16,23,38,56,72,91]; target=23; found_idx=5
    fig, ax = plt.subplots(figsize=(9,2.8)); ax.axis("off")
    ax.set_title("Binary Search for 23 in sorted array — 3 comparisons", fontsize=12,fontweight="bold")
    comparisons = {4:"1st",7:"2nd",5:"3rd (found)"}
    for i,val in enumerate(arr):
        col="#e74c3c" if val==target else ("#fff3cd" if i in comparisons else "#2c5f8a")
        ax.add_patch(mpatches.FancyBboxPatch((i*1.05,0.3),0.9,0.8,
                     boxstyle="round,pad=0.05",facecolor=col,edgecolor="white",lw=1.5))
        ax.text(i*1.05+0.45,0.7,str(val),ha="center",va="center",
                fontsize=11,fontweight="bold",color="white" if col!="#fff3cd" else "#333")
        ax.text(i*1.05+0.45,0.1,f"[{i}]",ha="center",va="center",fontsize=8,color="#666")
        if i in comparisons:
            ax.text(i*1.05+0.45,1.35,comparisons[i],ha="center",fontsize=8,
                    color="#e74c3c" if val==target else "#e65c00",fontweight="bold")
    ax.set_xlim(-0.2,10.8); ax.set_ylim(-0.1,1.8)
    fig.tight_layout(); return fig


def make_bfs_graph():
    nodes={"A":(3,3.5),"B":(1.5,2),"C":(4.5,2),"D":(0.5,0.5),"E":(2.5,0.5),"F":(5.5,0.5)}
    edges=[("A","B"),("A","C"),("B","D"),("B","E"),("C","E"),("C","F")]
    levels={"A":0,"B":1,"C":1,"D":2,"E":2,"F":2}
    cols={0:"#e65c00",1:"#2196F3",2:"#4CAF50"}
    fig, ax = plt.subplots(figsize=(6.5,4.5)); ax.axis("off")
    ax.set_title("BFS from A: guarantees shortest path\n(min edges) in unweighted graph",
                 fontsize=11,fontweight="bold")
    for (u,v) in edges:
        ux,uy=nodes[u]; vx,vy=nodes[v]
        ax.plot([ux,vx],[uy,vy],"k-",lw=1.5,zorder=1)
    for nd,(x,y) in nodes.items():
        ax.add_patch(plt.Circle((x,y),0.4,color=cols[levels[nd]],zorder=3))
        ax.text(x,y,nd,ha="center",va="center",fontsize=14,fontweight="bold",color="white",zorder=4)
    ax.legend(handles=[mpatches.Patch(color=cols[i],label=f"Level {i}") for i in range(3)],
              loc="lower right",fontsize=9)
    ax.text(3,4.3,"BFS order: A → B → C → D → E → F",ha="center",fontsize=11,style="italic")
    ax.set_xlim(-0.2,6.5); ax.set_ylim(-0.2,5.0)
    fig.tight_layout(); return fig


def make_flowchart_even_odd():
    fig, ax = plt.subplots(figsize=(4.5,7.5)); ax.axis("off")
    ax.set_title("Algorithm Flowchart: Even/Odd Check", fontsize=12,fontweight="bold")
    ax.set_xlim(0,4); ax.set_ylim(0,10)
    def oval(x,y,w,h,txt,col): ax.add_patch(mpatches.Ellipse((x+w/2,y+h/2),w,h,fc=col,ec="#333",lw=1.5)); ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=11,fontweight="bold")
    def rect(x,y,w,h,txt,col): ax.add_patch(mpatches.FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.08",fc=col,ec="#333",lw=1.5)); ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=10)
    def diamond(x,y,w,h,txt,col):
        cx,cy=x+w/2,y+h/2; dx,dy=w/2,h/2
        ax.add_patch(plt.Polygon([(cx,y+h),(x+w,cy),(cx,y),(x,cy)],fc=col,ec="#333",lw=1.5))
        ax.text(cx,cy,txt,ha="center",va="center",fontsize=9,fontweight="bold")
    def arr(x1,y1,x2,y2,col="#333"): ax.annotate("",xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle="->",color=col,lw=1.5))
    oval(1,8.8,2,0.8,"START","#4CAF50"); arr(2,8.8,2,8.5)
    rect(0.7,7.3,2.6,1.0,"INPUT  N","#fff9c4"); arr(2,7.3,2,6.9)
    diamond(0.4,5.5,3.2,1.2,"N % 2 == 0 ?","#fce4ec")
    arr(1.0,6.1,0.6,5.0,"royalblue"); ax.text(0.2,5.6,"YES",fontsize=9,color="royalblue",fontweight="bold")
    rect(-0.2,3.9,1.8,0.9,'Print\n"EVEN"',"#bbdefb")
    arr(3.0,6.1,3.4,5.0,"tomato"); ax.text(3.5,5.6,"NO",fontsize=9,color="tomato",fontweight="bold")
    rect(2.4,3.9,1.8,0.9,'Print\n"ODD"',"#ffcdd2")
    arr(0.7,3.9,1.9,3.2); arr(3.3,3.9,2.1,3.2)
    oval(1,2.2,2,0.85,"STOP","#F44336")
    ax.text(2,-0.1,"N=0 → 0%2=0 → EVEN",ha="center",fontsize=9,color="gray",style="italic")
    fig.tight_layout(); return fig


def make_lr_flowchart():
    fig, ax = plt.subplots(figsize=(8.5,3)); ax.axis("off")
    ax.set_title("Input-Output Flowchart", fontsize=12,fontweight="bold")
    steps=[("Input\n7","#4CAF50"),("× 3\n= 21","#2196F3"),("+5\n=26","#FF9800"),("÷ 2\n=13","#9C27B0"),("Output\n13","#F44336")]
    for i,(txt,col) in enumerate(steps):
        x=i*2.0+0.2
        ax.add_patch(mpatches.FancyBboxPatch((x,0.4),1.5,1.3,boxstyle="round,pad=0.08",fc=col,ec="white",lw=2))
        ax.text(x+0.75,1.05,txt,ha="center",va="center",fontsize=12,fontweight="bold",color="white")
        if i<4: ax.annotate("",xy=(x+1.7,1.05),xytext=(x+1.52,1.05),arrowprops=dict(arrowstyle="->",color="#333",lw=2))
    ax.set_xlim(0,10.5); ax.set_ylim(0,2.5)
    ax.text(5,0.1,"Input 7 → ×3 → +5 → ÷2 → Output 13",ha="center",fontsize=10,color="gray",style="italic")
    fig.tight_layout(); return fig


def make_latin_square():
    data=[["1","2","3"],["2","3","1"],["3","?","2"]]
    fig, ax = plt.subplots(figsize=(4.5,4)); ax.axis("off")
    ax.set_title("3×3 Latin Square\n(each row & column contains 1, 2, 3 exactly once)",fontsize=10,fontweight="bold")
    for r in range(3):
        for c in range(3):
            v=data[r][c]
            col="#fff3c4" if v=="?" else ("#ddeeff" if (r+c)%2==0 else "#f5f9ff")
            ax.add_patch(mpatches.FancyBboxPatch((c*1.2+0.1,(2-r)*1.2+0.1),1.1,1.1,
                         boxstyle="round,pad=0.06",fc=col,ec="#999",lw=1.5))
            ax.text(c*1.2+0.65,(2-r)*1.2+0.65,v,ha="center",va="center",fontsize=20,fontweight="bold",
                    color="#e65c00" if v=="?" else "#1a3a5c")
    ax.text(1.9,-0.1,"? = 1  (row 3 needs 1 ; col 2 needs 1)",ha="center",fontsize=10,color="gray",style="italic")
    ax.set_xlim(0,3.8); ax.set_ylim(-0.4,4)
    fig.tight_layout(); return fig


def make_coord_plot():
    fig, ax = plt.subplots(figsize=(5.5,5))
    P,Q = (1,2),(7,10)
    ax.plot([P[0],Q[0]],[P[1],Q[1]],"b-",lw=1.5,alpha=0.5)
    for (px,py,lbl) in [(P[0],P[1],"P"),(Q[0],Q[1],"Q")]:
        ax.plot(px,py,"bo",ms=10,zorder=5)
        ax.annotate(f"  {lbl}({px},{py})",(px,py),fontsize=12,fontweight="bold")
    ax.annotate("",xy=((P[0]+Q[0])/2+0.3,(P[1]+Q[1])/2),xytext=((P[0]+Q[0])/2-0.3,(P[1]+Q[1])/2))
    ax.text((P[0]+Q[0])/2+1,(P[1]+Q[1])/2-0.5,"PQ = 10",fontsize=11,color="royalblue",fontweight="bold")
    ax.axhline(0,color="#888",lw=1); ax.axvline(0,color="#888",lw=1)
    ax.grid(True,alpha=0.3); ax.set_xlabel("x",fontsize=12); ax.set_ylabel("y",fontsize=12)
    ax.set_title("P(1,2) and Q(7,10)\nPQ = √(6²+8²) = √100 = 10",fontsize=11,fontweight="bold")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout(); return fig


def make_gdp_bar():
    fig, ax = plt.subplots(figsize=(5,4))
    ax.bar(["Prev Year","Curr Year"],[150,165],color=["#4e79a7","#59a14f"],width=0.4,ec="white",lw=1.5)
    ax.text(0,152,"₹150",ha="center",fontsize=11,fontweight="bold",color="white")
    ax.text(1,167,"₹165 (+10%)",ha="center",fontsize=11,fontweight="bold")
    ax.annotate("",xy=(0.95,165),xytext=(0.05,150),arrowprops=dict(arrowstyle="->",color="green",lw=2))
    ax.set_ylabel("GDP (₹ lakh crore)",fontsize=11)
    ax.set_title("GDP Growth: 150→165 lakh crore\nGrowth Rate = (165−150)/150 × 100 = 10%",fontsize=11,fontweight="bold")
    ax.set_ylim(0,195); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout(); return fig


def make_org_chart():
    fig, ax = plt.subplots(figsize=(9,4)); ax.axis("off")
    ax.set_title("Span of Management = 8 (1 Manager : 8 Subordinates)",fontsize=12,fontweight="bold")
    def node(x,y,txt,col="#2c5f8a",w=1.4,h=0.55):
        ax.add_patch(mpatches.FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=0.06",fc=col,ec="white",lw=1.5))
        ax.text(x,y,txt,ha="center",va="center",fontsize=9,fontweight="bold",color="white")
    node(5,4.5,"Manager",col="#e65c00",w=1.6)
    xs=[0.8,1.9,3.0,4.1,5.2,6.3,7.4,8.5]
    for i,x in enumerate(xs,1):
        ax.annotate("",xy=(x,3.5),xytext=(5,4.2),arrowprops=dict(arrowstyle="->",color="#777",lw=1.2))
        node(x,3.0,f"S{i}",w=0.85,h=0.5)
    ax.text(5,2.1,"← Span of Management = 8 →",ha="center",fontsize=11,color="gray",style="italic")
    ax.set_xlim(-0.2,10); ax.set_ylim(1.5,5.5)
    fig.tight_layout(); return fig


def make_code_image(code_lines, title="Python"):
    """PIL-based code snippet image with dark theme."""
    fsize = 17; pad = 18; lh = 25
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", fsize)
        bold = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", fsize)
    except Exception:
        font = bold = ImageFont.load_default()

    max_w = max((len(l) for l in code_lines), default=40)
    W = max(500, max_w*10 + pad*2)
    H = len(code_lines)*lh + pad*2 + 30

    img = Image.new("RGB", (W, H), "#1e1e1e")
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0),(W,28)], fill="#323233")
    draw.text((10,5), f"  {title}", fill="#cccccc", font=font)

    KEYWORDS = {"def","return","if","else","elif","for","while","in",
                "import","from","class","try","except","finally","with",
                "as","print","True","False","None","and","or","not",
                "lambda","pass","break","continue","range","len","int",
                "str","list","dict","open","del","isinstance"}

    y = 32
    for line in code_lines:
        if line.startswith("#"):
            draw.text((pad, y), line, fill="#6a9955", font=font)
        else:
            # tokenize naively by spaces
            tokens = re.split(r"(\s+)", line)
            x = pad
            for tok in tokens:
                if not tok: continue
                stripped = tok.strip()
                if stripped in KEYWORDS:
                    col, f = "#569cd6", bold
                elif stripped.startswith(("'", '"')) or stripped.endswith(("'", '"')):
                    col, f = "#ce9178", font
                elif re.match(r"^-?\d+\.?\d*$", stripped):
                    col, f = "#b5cea8", font
                elif stripped.startswith("#"):
                    draw.text((x, y), tok, fill="#6a9955", font=font)
                    break
                else:
                    col, f = "#d4d4d4", font
                draw.text((x, y), tok, fill=col, font=f)
                try:
                    x += font.getbbox(tok)[2]
                except Exception:
                    x += len(tok)*10
        y += lh
    return img


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    conn = get_conn()

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 1: Strip ALL English and Commerce Gr11/12 images
    # ─────────────────────────────────────────────────────────────────────────
    print("="*65)
    print("  PHASE 1: Strip English + Commerce Gr11/12")
    print("="*65)
    for subj, gr in [("English",11),("English",12),("Commerce",11),("Commerce",12)]:
        n = strip_by_subject_grade(subj, gr, conn)
        print(f"  {subj} G{gr}: {n} stripped")

    # Restore Commerce G12 GDP and OrgChart — they'll get generated images below
    # (strip_by_subject_grade already handled them; gen_update will re-add proper images)

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 2: Strip specific questions with irrelevant generic stock photos
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "="*65)
    print("  PHASE 2: Strip other subjects with generic stock photos")
    print("="*65)

    # CS: individual IDs with generic photos
    cs_strip = [
        "538B598A-134D-4297-8007-33A90F3DE359",  # Boolean — motherboard
        "CAE92452-1DDF-4856-82CC-4A85D2B5FC6D",  # Binary convert — random screen
        "0AE1B1B7-5A80-463E-9FE0-6A4EDEC2D2E1",  # SQL — server rack
        "053EECFB-1EB2-409B-B0EB-754882C8A724",  # Python dict — dictionary book
        "B6BD72D6-E9AA-4D4A-BDBA-47A489177485",  # File handling — file folder
        "4316FCFF-4000-4946-89E6-C1C4602B83D3",  # Bubble sort — generic objects
        "CB48E802-CAB0-46A3-A71B-75AF865F7147",  # OOP — hierarchy pyramid
        "B6CE7468-CDEB-4A7A-8C19-A3F270B6B0FE",  # SQL GROUP BY — spreadsheet
        "CFECBF34-2920-4C57-99C5-AC93B5BA2343",  # pandas — generic laptop
        "F5B3A781-E5D1-461D-ABE4-552D31BDB66D",  # CPU/thread — generic CPU
    ]
    strip_by_ids(cs_strip, conn)
    print(f"  CS: {len(cs_strip)} IDs stripped")

    # LR: by topic/subtopic
    lr_strip = [
        (11,"Direction and Distance","Final Direction"),
        (11,"Spatial Reasoning","Mirror Images"),
        (11,"Analogies","Letter and Word Analogies"),
        (11,"Series and Sequences","Number Series"),
        (11,"Blood Relations","Family Relationships"),
        (11,"Direction and Distance","Shortest Path"),
        (11,"Arrangements","Linear Seating Arrangement"),
        (11,"Syllogisms","Venn Diagram Method"),
        (11,"Coding and Decoding","Letter Coding"),
        (12,"Clock and Calendar","Clocks Gaining/Losing Time"),
        (12,"Arrangements","Ranking from Both Ends"),
        (12,"Critical Reasoning","Assumptions and Conclusions"),
        (12,"Coding and Decoding","Number-Letter Coding"),
        (12,"Critical Reasoning","Statement and Argument"),
        (12,"Logical Sequences","Sequence of Events"),
        (12,"Series and Sequences","Mixed Series"),
        (12,"Logical Sequences","Input-Output Machine"),
        (12,"Arrangements","Circular Permutations"),
    ]
    for (gr,t,st) in lr_strip:
        n = strip_by_topic("Logical Reasoning", gr, t, st, conn)
        if n: print(f"  LR G{gr} {st}: {n} stripped")

    # Math: by topic/subtopic
    math_strip = [
        (11,"Sequences and Series","Arithmetic Progression"),  # stacked coins
        (11,"Statistics","Measures of Dispersion"),            # histogram
        (12,"Three-Dimensional Geometry","Direction Cosines"), # abstract 3D axes
        (12,"Vectors","Dot Product and Cross Product"),        # generic arrows
    ]
    for (gr,t,st) in math_strip:
        n = strip_by_topic("Mathematics", gr, t, st, conn)
        if n: print(f"  Math G{gr} {st}: {n} stripped")

    print(f"\n  Total stripped so far: {stats['stripped']}")

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 3: Generate proper images
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "="*65)
    print("  PHASE 3: Generate proper images")
    print("="*65)

    # ── MATH Gr11 ──
    gen_update("Mathematics",11,"Sets","Venn Diagrams",
               lambda: make_venn2(9,6,5,"A","B","Venn: |A|=14, |B|=11, |A∩B|=5"),
               "math-venn-sets11", conn)

    gen_update("Mathematics",11,"Straight Lines","Distance and Section Formula",
               make_coord_plot, "math-coord11", conn)

    gen_update("Mathematics",11,"Conic Sections","Parabola",
               make_parabola, "math-parabola11", conn)

    gen_update("Mathematics",11,"Limits and Derivatives","Derivative as Slope of Tangent",
               make_tangent_y_x2, "math-tangent11", conn)

    gen_update("Mathematics",11,"Binomial Theorem","Pascal's Triangle",
               make_pascal, "math-pascal11", conn)

    # ── MATH Gr12 ──
    gen_update("Mathematics",12,"Matrices and Determinants","Matrix Operations",
               make_matrix_display, "math-matrix12", conn)

    gen_update("Mathematics",12,"Relations and Functions","Types of Functions",
               make_mapping_diagram, "math-mapping12", conn)

    gen_update("Mathematics",12,"Continuity and Differentiability","Differentiability",
               make_y_abs_x, "math-yabsx12", conn)

    gen_update("Mathematics",12,"Applications of Derivatives","Maxima and Minima",
               make_maxmin_curve, "math-maxmin12", conn)

    gen_update("Mathematics",12,"Integrals","Definite Integral as Area",
               make_integral_area, "math-integral12", conn)

    gen_update("Mathematics",12,"Linear Programming","Graphical Method",
               make_lp_region, "math-lp12", conn)

    gen_update("Mathematics",12,"Probability","Bayes Theorem and Conditional Probability",
               lambda: make_prob_tree(0.4,0.7,0.3), "math-probtree12", conn)

    gen_update("Mathematics",12,"Differential Equations","Variable Separable Method",
               make_exp_growth, "math-expgrowth12", conn)

    # ── LR Gr11 ──
    gen_update("Logical Reasoning",11,"Clock and Calendar","Angle Between Hands",
               lambda: make_clock(3,20), "lr-clock11", conn)

    gen_update("Logical Reasoning",11,"Data Interpretation","Bar Graph",
               lambda: make_bar_chart(["Mon","Tue","Wed","Thu","Fri"],[120,150,90,180,160],
                                      "Daily Sales","Units"), "lr-bar11", conn)

    gen_update("Logical Reasoning",11,"Data Interpretation","Pie Chart",
               lambda: make_pie_chart(["Rent","Food","Transport","Savings","Misc"],
                                      [30,25,15,20,10],"Monthly Budget (₹40,000)"),
               "lr-pie11", conn)

    gen_update("Logical Reasoning",11,"Logical Sequences","Input-Output",
               make_lr_flowchart, "lr-flowchart11", conn)

    # ── LR Gr12 ──
    gen_update("Logical Reasoning",12,"Data Interpretation","Line Graph Trend Analysis",
               lambda: make_line_graph(["2019","2020","2021","2022","2023"],
                                       [40,32,48,56,60],"Revenue (₹ Lakhs)","₹ Lakhs"),
               "lr-linegraph12", conn)

    gen_update("Logical Reasoning",12,"Data Interpretation","Table Data Analysis",
               lambda: make_table(["Student","Score"],
                                  [["A","72"],["B","88"],["C","65"],["D","91"],["E","79"]],
                                  "Student Scores (out of 100)"),
               "lr-table12", conn)

    gen_update("Logical Reasoning",12,"Logical Deduction","Matrix Completion",
               make_latin_square, "lr-latinsq12", conn)

    gen_update("Logical Reasoning",12,"Syllogisms","Three-Statement Syllogism",
               lambda: make_venn2(30,15,30,"Cricket","Football",
                                  "Survey: n=100, Cricket=60, Football=45, Both=30"),
               "lr-venn12", conn)

    # ── CS Gr11 ── (code snippet images)
    gen_update("Computer Science",11,"Python Programming","List Slicing",
               lambda: make_code_image([
                   "my_list = [10, 20, 30, 40, 50, 60]",
                   "print(my_list[1:4])",
                   "",
                   "# Indices 1, 2, 3 (stop=4 exclusive)",
                   "# Output:  [20, 30, 40]",
               ], "Python — List Slicing"), "cs-listslice11", conn)

    gen_update("Computer Science",11,"Computational Thinking","Flowchart and Algorithms",
               make_flowchart_even_odd, "cs-flowchart11", conn)

    gen_update("Computer Science",11,"Python Programming","Dictionaries",
               lambda: make_code_image([
                   "d = {'a': 1, 'b': 2, 'c': 3}  # len=3",
                   "d['b'] = 10                    # update, len=3",
                   "d['d'] = 4                     # new key, len=4",
                   "del d['a']                     # delete, len=3",
                   "print(len(d))",
                   "",
                   "# Output:  3",
               ], "Python — Dictionary Operations"), "cs-dict11", conn)

    gen_update("Computer Science",11,"Python Programming","File Handling",
               lambda: make_code_image([
                   "try:",
                   "    f = open('test.txt', 'r')  # file missing",
                   "except FileNotFoundError:",
                   "    print('File missing')       # runs",
                   "finally:",
                   "    print('Done')               # always runs",
                   "",
                   "# Output:",
                   "# File missing",
                   "# Done",
               ], "Python — try/except/finally"), "cs-fileio11", conn)

    gen_update("Computer Science",11,"Algorithms","Sorting Algorithms",
               lambda: make_table(
                   ["Step","List state","Swap?"],
                   [["Start","[5, 3, 8, 1, 2]","—"],
                    ["(5,3) 5>3","[3, 5, 8, 1, 2]","Swap 1"],
                    ["(5,8) 5<8","[3, 5, 8, 1, 2]","No"],
                    ["(8,1) 8>1","[3, 5, 1, 8, 2]","Swap 2"],
                    ["(8,2) 8>2","[3, 5, 1, 2, 8]","Swap 3"],
                    ["End pass 1","3 swaps total",""]],
                   "Bubble Sort — First Pass"), "cs-bubblesort11", conn)

    # CS Gr11: Boolean logic — generate truth table
    gen_update("Computer Science",11,"Boolean Logic","Logic Gates",
               lambda: make_table(
                   ["A","B","NOT B","A AND (NOT B)","C","F = ... OR C"],
                   [["1","1","0","0","0","0"],
                    ["1","1","0","0","1","1"],
                    ["1","0","1","1","0","1"],
                    ["0","1","0","0","0","0"]],
                   "Boolean: F = A AND (NOT B) OR C\nA=1, B=1, C=0  →  F = 0"),
               "cs-booltable11", conn)

    gen_update("Computer Science",11,"Number Systems","Binary to Decimal Conversion",
               lambda: make_table(
                   ["Bit position","2⁷","2⁶","2⁵","2⁴","2³","2²","2¹","2⁰"],
                   [["Value","128","64","32","16","8","4","2","1"],
                    ["Digit","1","0","1","1","0","1","0","1"],
                    ["Product","128","0","32","16","0","4","0","1"]],
                   "10110101₂ = 128+32+16+4+1 = 181₁₀"),
               "cs-binary11", conn)

    # ── CS Gr12 ──
    gen_update("Computer Science",12,"Data Structures","Binary Search Tree",
               make_bst, "cs-bst12", conn)

    gen_update("Computer Science",12,"Python Programming","Recursion",
               lambda: make_code_image([
                   "def f(n):",
                   "    if n <= 0: return 0",
                   "    return n + f(n-2)",
                   "",
                   "print(f(6))",
                   "",
                   "# Trace: f(6)=6+f(4)=6+4+f(2)=6+4+2+f(0)",
                   "#        = 6+4+2+0 = 12",
                   "# Output:  12",
               ], "Python — Recursion"), "cs-recursion12", conn)

    gen_update("Computer Science",12,"Python Programming","List Comprehension",
               lambda: make_code_image([
                   "result = [x**2 for x in range(1, 6)",
                   "          if x % 2 != 0]",
                   "print(result)",
                   "",
                   "# range(1,6) = [1,2,3,4,5]",
                   "# odd only:    [1, 3, 5]",
                   "# squared:     [1, 9, 25]",
                   "# Output:  [1, 9, 25]",
               ], "Python — List Comprehension"), "cs-listcomp12", conn)

    gen_update("Computer Science",12,"Python Programming","Exception Handling",
               lambda: make_code_image([
                   "try:",
                   "    x = int('abc')   # raises ValueError",
                   "    print('A')       # skipped",
                   "except ValueError:",
                   "    print('B')       # runs",
                   "except Exception:",
                   "    print('C')       # not reached",
                   "else:",
                   "    print('D')       # skipped (exception raised)",
                   "finally:",
                   "    print('E')       # ALWAYS runs",
                   "",
                   "# Output:  B",
                   "#          E",
               ], "Python — Exception Handling"), "cs-exception12", conn)

    gen_update("Computer Science",12,"Python Programming","Debugging",
               lambda: make_code_image([
                   "def calculate_avg(lst):",
                   "    total = 0",
                   "    for i in range(len(lst)+1):  # BUG!",
                   "        total += lst[i]          # IndexError",
                   "    return total / len(lst)",
                   "",
                   "# range(len(lst)+1) = 0..len(lst)",
                   "# valid indices     = 0..len(lst)-1",
                   "# lst[len(lst)] -> IndexError!",
                   "# Fix: range(len(lst))",
               ], "Python — IndexError Debug"), "cs-debug12", conn)

    gen_update("Computer Science",12,"Algorithms","Binary Search",
               make_sorted_array_bsearch, "cs-bsearch12", conn)

    gen_update("Computer Science",12,"Algorithms","Graph Traversal",
               make_bfs_graph, "cs-bfs12", conn)

    gen_update("Computer Science",12,"Database Management","Advanced SQL",
               lambda: make_table(
                   ["Region","SUM(Amount)","Passes HAVING?"],
                   [["North","1,20,000","Yes (>1,00,000)"],
                    ["South","85,000","No"],
                    ["East","1,50,000","Yes"],
                    ["West","95,000","No"]],
                   "GROUP BY Region  HAVING SUM(Amount) > 1,00,000"),
               "cs-sql12", conn)

    gen_update("Computer Science",12,"Python OOP","Inheritance and Polymorphism",
               lambda: make_table(
                   ["Call","Method used","Output","Concept"],
                   [["Animal().speak()","Animal.speak()","Generic sound","Base method"],
                    ["Dog().speak()","Dog.speak()","Woof","Method Overriding"],
                    ["isinstance(Dog(),Animal)","—","True","IS-A relationship"]],
                   "Python OOP — Method Overriding (Polymorphism)"),
               "cs-oop12", conn)

    # ── Commerce Gr12: GDP and OrgChart with proper generated images ──
    # These were stripped in Phase 1; now re-add as proper generated images
    # Need to post fresh questions (stripped ImageUrl is NULL now)
    # Instead: update by topic
    gen_update("Commerce",12,"National Income","GDP and Economic Growth",
               make_gdp_bar, "com-gdp12", conn)
    gen_update("Commerce",12,"Principles of Management","Span of Management",
               make_org_chart, "com-orgchart12", conn)

    conn.close()

    print(f"\n{'='*65}")
    print(f"  DONE — Stripped: {stats['stripped']}  Generated: {stats['generated']}  Errors: {stats['errors']}")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
