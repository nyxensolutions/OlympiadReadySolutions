"""
Science-Biology, Science-Chemistry, Science-Physics Gr9 Olympiad
10 questions each with generated matplotlib/PIL images
"""
import sys, io, time, re, requests, cloudinary, cloudinary.uploader, pyodbc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle, FancyBboxPatch
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

cloudinary.config(cloud_name="dyommthef", api_key="414698218814162",
                  api_secret="fIHmpWwiIllKPs2qbEeHVNzMMP4")

ADMIN_URL = "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net/api/admin/add-question"
ADMIN_KEY = "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt"
DB_CONN   = ("DRIVER={ODBC Driver 18 for SQL Server};"
             "SERVER=tcp:olympiadready-np.database.windows.net,1433;"
             "DATABASE=OlympiadReady;UID=nyxen-admin;PWD=Olympiad@2026;"
             "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30")

TS = str(int(time.time()))

# ── upload helpers ─────────────────────────────────────────────────────────────
def upload_fig(fig, name):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    r = cloudinary.uploader.upload(buf, public_id=f"questions/{name}_{TS}",
                                   overwrite=False, resource_type="image")
    return r["secure_url"]

def post_direct(q):
    """Insert directly into DB, bypassing API."""
    import json, uuid
    conn = pyodbc.connect(DB_CONN)
    c = conn.cursor()
    # check duplicate
    c.execute("SELECT 1 FROM QuestionBank WHERE Subject=? AND Grade=? AND SubTopic=? AND QuestionText=?",
              q["subject"], q["grade"], q["subTopic"], q["questionText"])
    if c.fetchone():
        conn.close()
        return "DUP"
    qid = str(uuid.uuid4()).upper()
    opts = json.dumps(q["options"])
    c.execute("""INSERT INTO QuestionBank
                 (QuestionBankId, Subject, Grade, Difficulty, Topic, SubTopic,
                  QuestionText, OptionsJson, CorrectAnswer, Explanation, ImageUrl, CreatedAt)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,GETUTCDATE())""",
              qid, q["subject"], q["grade"], q["difficulty"],
              q["topic"], q["subTopic"], q["questionText"],
              opts, q["correctAnswer"], q["explanation"],
              q.get("imageUrl"))
    conn.commit()
    conn.close()
    return "OK"

# ══════════════════════════════════════════════════════════════════════════════
# IMAGE GENERATORS
# ══════════════════════════════════════════════════════════════════════════════

def make_dt_graph():
    """Distance-time graph: 0-4s → 60m, then 4-8s → 60m still (stop), then 8-12s → 90m"""
    fig, ax = plt.subplots(figsize=(6,4))
    t = [0, 4, 8, 12]
    d = [0, 60, 60, 90]
    ax.plot(t, d, "b-o", lw=2.5, ms=7)
    ax.fill_between(t, d, alpha=0.08, color="blue")
    ax.set_xlabel("Time (s)", fontsize=12)
    ax.set_ylabel("Distance (m)", fontsize=12)
    ax.set_title("Distance-Time Graph of a Moving Object", fontsize=13, fontweight="bold")
    ax.set_xticks(t); ax.set_yticks([0,30,60,90])
    ax.grid(True, ls="--", alpha=0.5)
    ax.annotate("Object\nstationary", xy=(6,60), xytext=(5.5,40),
                fontsize=10, color="red",
                arrowprops=dict(arrowstyle="->", color="red"))
    fig.tight_layout()
    return fig

def make_vt_graph():
    """Velocity-time graph: uniform accel 0→20 m/s in 5s, then constant 20 m/s for 5s"""
    fig, ax = plt.subplots(figsize=(6,4))
    t = [0, 5, 10]
    v = [0, 20, 20]
    ax.plot(t, v, "r-o", lw=2.5, ms=7)
    ax.fill_between(t, v, alpha=0.12, color="red")
    ax.set_xlabel("Time (s)", fontsize=12)
    ax.set_ylabel("Velocity (m/s)", fontsize=12)
    ax.set_title("Velocity-Time Graph", fontsize=13, fontweight="bold")
    ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10])
    ax.set_yticks([0,5,10,15,20])
    ax.grid(True, ls="--", alpha=0.5)
    # shade area under curve
    ax.text(2.5, 5, "Area = Distance\n(0 to 5s)", ha="center", fontsize=9, color="darkred")
    ax.text(7.5, 10, "Area = Distance\n(5 to 10s)", ha="center", fontsize=9, color="darkred")
    fig.tight_layout()
    return fig

def make_momentum_collision():
    """Two trolleys before/after inelastic collision"""
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    for ax in axes:
        ax.set_xlim(0, 10); ax.set_ylim(0, 4)
        ax.axis("off")

    def draw_cart(ax, x, y, label, color):
        ax.add_patch(FancyBboxPatch((x, y), 2, 1.2, boxstyle="round,pad=0.1",
                                    fc=color, ec="black", lw=1.5))
        ax.text(x+1, y+0.6, label, ha="center", va="center", fontsize=10, fontweight="bold")
        for cx in [x+0.4, x+1.6]:
            ax.add_patch(Circle((cx, y), 0.3, fc="gray", ec="black"))

    # Before
    draw_cart(axes[0], 0.5, 1.5, "A\n3 kg\n6 m/s →", "#4fc3f7")
    draw_cart(axes[0], 6.5, 1.5, "B\n2 kg\nAt rest", "#ef9a9a")
    axes[0].set_title("BEFORE collision", fontsize=12, fontweight="bold")
    axes[0].annotate("", xy=(4.5, 2.1), xytext=(3, 2.1),
                     arrowprops=dict(arrowstyle="->", color="blue", lw=2))

    # After (perfectly inelastic)
    draw_cart(axes[1], 3, 1.5, "A+B\n5 kg\n? m/s →", "#a5d6a7")
    axes[1].set_title("AFTER (stick together)", fontsize=12, fontweight="bold")
    axes[1].annotate("", xy=(6.5, 2.1), xytext=(5.2, 2.1),
                     arrowprops=dict(arrowstyle="->", color="green", lw=2))

    fig.suptitle("Conservation of Momentum — Inelastic Collision", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig

def make_lever():
    """Lever principle of moments diagram"""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    # beam
    ax.plot([1, 9], [2.5, 2.5], "k-", lw=5)
    # pivot (triangle)
    triangle = plt.Polygon([[5,2.5],[4.3,1.2],[5.7,1.2]], fc="#ffd54f", ec="black", lw=2)
    ax.add_patch(triangle)
    # left load
    ax.annotate("", xy=(2.5, 2.5), xytext=(2.5, 4.2),
                arrowprops=dict(arrowstyle="-|>", color="blue", lw=2.5))
    ax.text(2.5, 4.4, "F₁ = 80 N", ha="center", fontsize=11, color="blue", fontweight="bold")
    ax.text(2.5, 1.8, "d₁ = 3 m", ha="center", fontsize=10, color="blue")
    ax.annotate("", xy=(5, 2.0), xytext=(2.5, 2.0),
                arrowprops=dict(arrowstyle="<->", color="blue", lw=1.5))
    # right load
    ax.annotate("", xy=(7.5, 2.5), xytext=(7.5, 4.2),
                arrowprops=dict(arrowstyle="-|>", color="red", lw=2.5))
    ax.text(7.5, 4.4, "F₂ = ?", ha="center", fontsize=11, color="red", fontweight="bold")
    ax.text(7.5, 1.8, "d₂ = 2 m", ha="center", fontsize=10, color="red")
    ax.annotate("", xy=(7.5, 2.0), xytext=(5, 2.0),
                arrowprops=dict(arrowstyle="<->", color="red", lw=1.5))
    ax.text(5, 0.7, "Pivot", ha="center", fontsize=10, color="gray")
    ax.set_title("Principle of Moments — Find F₂", fontsize=13, fontweight="bold")
    fig.tight_layout()
    return fig

def make_sound_wave():
    """Transverse sound wave with labeled wavelength and amplitude"""
    fig, ax = plt.subplots(figsize=(7, 3.5))
    x = np.linspace(0, 4*np.pi, 400)
    y = 2 * np.sin(x)
    ax.plot(x, y, "b-", lw=2.5)
    ax.axhline(0, color="gray", lw=1, ls="--")
    # label wavelength (one full cycle: 0 to 2π)
    ax.annotate("", xy=(2*np.pi, -2.6), xytext=(0, -2.6),
                arrowprops=dict(arrowstyle="<->", color="green", lw=2))
    ax.text(np.pi, -3.1, "λ = 0.85 m", ha="center", fontsize=11, color="green", fontweight="bold")
    # label amplitude
    ax.annotate("", xy=(np.pi/2, 2), xytext=(np.pi/2, 0),
                arrowprops=dict(arrowstyle="<->", color="red", lw=2))
    ax.text(np.pi/2 + 0.4, 1, "A", fontsize=12, color="red", fontweight="bold")
    ax.set_xlabel("Distance (m)", fontsize=11)
    ax.set_ylabel("Displacement", fontsize=11)
    ax.set_title("Transverse Wave  (Speed of sound = 340 m/s)", fontsize=12, fontweight="bold")
    ax.set_xticks([]); ax.set_ylim(-3.5, 3)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig

def make_work_incline():
    """Block on inclined plane — work-energy"""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlim(0, 8); ax.set_ylim(0, 6); ax.axis("off")
    # incline
    triangle = plt.Polygon([[1,1],[7,1],[7,5]], fc="#e3f2fd", ec="#1565c0", lw=2.5)
    ax.add_patch(triangle)
    # height arrow
    ax.annotate("", xy=(7.5, 5), xytext=(7.5, 1),
                arrowprops=dict(arrowstyle="<->", color="green", lw=2))
    ax.text(7.8, 3, "h = 4 m", fontsize=11, color="green", fontweight="bold", va="center")
    # block
    block = FancyBboxPatch((3.5, 2.7), 0.8, 0.8, boxstyle="round,pad=0.05",
                           fc="#ff7043", ec="black", lw=1.5)
    ax.add_patch(block)
    ax.text(3.9, 3.1, "m=5kg", ha="center", fontsize=9, fontweight="bold", color="white")
    # arrow along incline
    ax.annotate("", xy=(5.5, 4.0), xytext=(4.0, 3.2),
                arrowprops=dict(arrowstyle="->", color="blue", lw=2))
    ax.text(3, 4.8, "g = 10 m/s²", fontsize=11, color="gray")
    ax.set_title("Block slides down frictionless incline\nFind KE at the bottom", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig

def make_buoyancy():
    """Buoyancy / Archimedes — apparent weight diagram"""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, 6); ax.set_ylim(0, 7); ax.axis("off")
    # water
    water = FancyBboxPatch((0.5, 1), 5, 4, boxstyle="square",
                           fc="#bbdefb", ec="#1976d2", lw=2, alpha=0.6)
    ax.add_patch(water)
    ax.text(3, 5.3, "Water (ρ = 1000 kg/m³)", ha="center", fontsize=10, color="#1565c0")
    # object
    obj = FancyBboxPatch((2, 2), 2, 2, boxstyle="round,pad=0.1",
                         fc="#ffa726", ec="#e65100", lw=2)
    ax.add_patch(obj)
    ax.text(3, 3, "Object\n500 g", ha="center", va="center", fontsize=10, fontweight="bold")
    # Weight arrow down
    ax.annotate("", xy=(3, 1.2), xytext=(3, 2),
                arrowprops=dict(arrowstyle="-|>", color="red", lw=2.5))
    ax.text(3.2, 1.0, "W = 5 N\n(True weight)", fontsize=9, color="red")
    # Buoyant force up
    ax.annotate("", xy=(3, 5.0), xytext=(3, 4),
                arrowprops=dict(arrowstyle="-|>", color="blue", lw=2.5))
    ax.text(3.2, 5.1, "Fb (Buoyant force)", fontsize=9, color="blue")
    # spring balance
    ax.text(0.7, 6.3, "Spring balance reads: 3 N", fontsize=10, color="darkgreen", fontweight="bold")
    ax.set_title("Archimedes' Principle — Buoyancy", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig

def make_free_fall():
    """Free fall distances at t=0,1,2,3s"""
    fig, ax = plt.subplots(figsize=(4, 5.5))
    ax.set_xlim(0, 5); ax.set_ylim(-5, 1); ax.axis("off")
    heights = [0, -5, -20, -45]
    labels  = ["t = 0 s\nh = 0 m", "t = 1 s\nh = 5 m", "t = 2 s\nh = 20 m", "t = 3 s\nh = 45 m"]
    colors  = ["#1565c0","#1976d2","#42a5f5","#90caf9"]
    for i, (h, lbl, c) in enumerate(zip(heights, labels, colors)):
        ax.add_patch(Circle((2.5, h/10), 0.25, fc=c, ec="black", lw=1.5))
        ax.text(3.2, h/10, lbl, va="center", fontsize=10, color="black")
    ax.annotate("", xy=(2.5, -4.7), xytext=(2.5, 0.3),
                arrowprops=dict(arrowstyle="-|>", color="red", lw=2, ls="--"))
    ax.text(1.5, -2.5, "g = 10 m/s²\n(downward)", ha="center", fontsize=10, color="red")
    ax.set_title("Free Fall — Distances at Each Second\n(s = ½gt²)", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig

def make_gravitational_satellite():
    """Two satellites at r and 2r around a planet — Kepler's 3rd"""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-3.5, 3.5); ax.set_ylim(-3.5, 3.5); ax.set_aspect("equal"); ax.axis("off")
    # planet
    ax.add_patch(Circle((0,0), 0.5, fc="#ffa726", ec="black", lw=2))
    ax.text(0, 0, "Planet", ha="center", va="center", fontsize=9, fontweight="bold")
    # orbit 1
    ax.add_patch(Circle((0,0), 1.5, fc="none", ec="#42a5f5", lw=1.5, ls="--"))
    ax.add_patch(Circle((1.5,0), 0.2, fc="#42a5f5", ec="black", lw=1.5))
    ax.text(1.5, 0.4, "Satellite A\nr = R", ha="center", fontsize=10, color="#1565c0")
    ax.annotate("", xy=(0.85, 0), xytext=(0,0),
                arrowprops=dict(arrowstyle="<->", color="#1565c0", lw=1.5))
    ax.text(0.4, 0.2, "R", fontsize=10, color="#1565c0", fontweight="bold")
    # orbit 2
    ax.add_patch(Circle((0,0), 3.0, fc="none", ec="#ef5350", lw=1.5, ls="--"))
    ax.add_patch(Circle((0,3.0), 0.2, fc="#ef5350", ec="black", lw=1.5))
    ax.text(0.5, 3.1, "Satellite B\nr = 2R", ha="left", fontsize=10, color="#c62828")
    ax.annotate("", xy=(0, 1.6), xytext=(0,0),
                arrowprops=dict(arrowstyle="<->", color="#c62828", lw=1.5))
    ax.text(0.15, 2.2, "2R", fontsize=10, color="#c62828", fontweight="bold")
    ax.set_title("Two Satellites — Kepler's Third Law\nT² ∝ r³", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig

def make_newtons_second():
    """Force diagram: net force on block"""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    # block
    block = FancyBboxPatch((3.5, 2), 3, 2, boxstyle="round,pad=0.1",
                           fc="#ffe082", ec="#f57f17", lw=2.5)
    ax.add_patch(block)
    ax.text(5, 3, "m = 4 kg", ha="center", va="center", fontsize=12, fontweight="bold")
    # F1 right
    ax.annotate("", xy=(9, 3), xytext=(6.5, 3),
                arrowprops=dict(arrowstyle="-|>", color="blue", lw=3))
    ax.text(9.2, 3, "F₁ = 50 N", fontsize=11, color="blue", fontweight="bold", va="center")
    # F2 left
    ax.annotate("", xy=(0.8, 3), xytext=(3.5, 3),
                arrowprops=dict(arrowstyle="-|>", color="red", lw=3))
    ax.text(0.1, 3, "F₂ = 18 N", fontsize=11, color="red", fontweight="bold", va="center")
    # friction label
    ax.text(5, 1.5, "Surface: frictionless", ha="center", fontsize=10, color="gray", style="italic")
    ax.plot([1, 9], [1.9, 1.9], color="gray", lw=2)
    ax.set_title("Newton's Second Law — Find Acceleration", fontsize=13, fontweight="bold")
    fig.tight_layout()
    return fig


# ── Chemistry image generators ────────────────────────────────────────────────

def make_bohr_atom(protons, neutrons, shells, symbol, name):
    """Bohr model of an atom"""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(-4, 4); ax.set_ylim(-4, 4); ax.set_aspect("equal"); ax.axis("off")
    radii = [0.7, 1.5, 2.5, 3.3]
    shell_colors = ["#ff8a65","#ffb74d","#aed581","#4dd0e1"]
    # nucleus
    ax.add_patch(Circle((0,0), 0.55, fc="#ef5350", ec="#b71c1c", lw=2, zorder=5))
    ax.text(0, 0.12, f"{protons}p", ha="center", fontsize=9, fontweight="bold", color="white", zorder=6)
    ax.text(0, -0.18, f"{neutrons}n", ha="center", fontsize=9, fontweight="bold", color="white", zorder=6)
    for i, (n_e, r, c) in enumerate(zip(shells, radii[:len(shells)], shell_colors)):
        ax.add_patch(Circle((0,0), r, fc="none", ec=c, lw=1.5, ls="--"))
        angle = np.linspace(0, 2*np.pi, n_e, endpoint=False)
        for a in angle:
            ax.add_patch(Circle((r*np.cos(a), r*np.sin(a)), 0.13, fc="#42a5f5", ec="black", lw=1))
        shell_name = ["K","L","M","N"][i]
        ax.text(r*np.cos(np.pi/6)+0.15, r*np.sin(np.pi/6)+0.15, f"{shell_name}({n_e})",
                fontsize=8.5, color=c, fontweight="bold")
    ax.set_title(f"Bohr Model: {name} ({symbol}, Z={protons})", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig

def make_chromatography():
    """Paper chromatography — Rf value"""
    fig, ax = plt.subplots(figsize=(4, 6))
    ax.set_xlim(0, 4); ax.set_ylim(0, 10); ax.axis("off")
    # paper
    paper = FancyBboxPatch((0.5, 0.5), 3, 9, boxstyle="square",
                           fc="#fffde7", ec="#bdbdbd", lw=2)
    ax.add_patch(paper)
    # solvent front
    ax.plot([0.5, 3.5], [8.5, 8.5], "b--", lw=2)
    ax.text(3.6, 8.5, "Solvent\nfront\n(9.6 cm)", fontsize=9, color="blue", va="center")
    # baseline
    ax.plot([0.5, 3.5], [1.5, 1.5], "k-", lw=2)
    ax.text(3.6, 1.5, "Baseline\n(0 cm)", fontsize=9, va="center")
    # spot A
    ax.add_patch(Circle((2, 7.2), 0.22, fc="#ef5350", ec="none", alpha=0.8))
    ax.text(2, 7.7, "Spot A\n(7.2 cm)", ha="center", fontsize=9, color="#c62828")
    # spot B
    ax.add_patch(Circle((2, 5.5), 0.22, fc="#7e57c2", ec="none", alpha=0.8))
    ax.text(2, 6.0, "Spot B\n(5.5 cm)", ha="center", fontsize=9, color="#4527a0")
    # height arrow
    ax.annotate("", xy=(0.7, 8.5), xytext=(0.7, 1.5),
                arrowprops=dict(arrowstyle="<->", color="gray", lw=1.5))
    ax.set_title("Paper Chromatography\nRf = Distance of spot / Distance of solvent front",
                 fontsize=11, fontweight="bold")
    fig.tight_layout()
    return fig

def make_distillation():
    """Simple distillation apparatus"""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    ax.set_title("Simple Distillation Apparatus", fontsize=13, fontweight="bold")
    # Round-bottom flask
    flask_x, flask_y = 1.5, 1.5
    ax.add_patch(Circle((flask_x, flask_y+0.5), 1.2, fc="#e3f2fd", ec="#1565c0", lw=2))
    ax.add_patch(FancyBboxPatch((flask_x-0.2, flask_y+1.5), 0.4, 0.6,
                                boxstyle="square", fc="#e3f2fd", ec="#1565c0", lw=2))
    ax.text(flask_x, flask_y+0.3, "Mixture\n(ethanol+water)", ha="center", fontsize=8.5)
    # thermometer
    ax.plot([flask_x+0.2, flask_x+0.5], [flask_y+2.1, flask_y+2.5], "r-", lw=3)
    ax.text(flask_x+0.7, flask_y+2.6, "Thermometer", fontsize=8.5, color="red")
    # condenser (angled tube)
    ax.annotate("", xy=(7.5, 2.5), xytext=(2.5, 4.5),
                arrowprops=dict(arrowstyle="-", color="#1565c0", lw=6, alpha=0.3))
    ax.annotate("", xy=(7.5, 2.5), xytext=(2.5, 4.5),
                arrowprops=dict(arrowstyle="-", color="#42a5f5", lw=3))
    ax.text(5, 4.0, "Condenser\n(water-cooled)", ha="center", fontsize=9, color="#0d47a1")
    # water in/out
    ax.text(3.5, 5.2, "Water in →", fontsize=8.5, color="blue")
    ax.text(6.5, 2.0, "← Water out", fontsize=8.5, color="blue")
    # collection flask
    ax.add_patch(Circle((8.5, 1.5), 0.9, fc="#f3e5f5", ec="#6a1b9a", lw=2))
    ax.text(8.5, 1.5, "Distillate\n(ethanol)", ha="center", fontsize=8.5)
    # heat source
    ax.add_patch(FancyBboxPatch((0.5, 0.3), 2, 0.5, boxstyle="round",
                                fc="#ff8a65", ec="#bf360c", lw=1.5))
    ax.text(1.5, 0.55, "Heat source", ha="center", fontsize=8.5, color="white", fontweight="bold")
    fig.tight_layout()
    return fig

def make_electrolysis():
    """Electrolysis of water — anode/cathode"""
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.set_xlim(0, 8); ax.set_ylim(0, 7); ax.axis("off")
    ax.set_title("Electrolysis of Dilute H₂SO₄", fontsize=13, fontweight="bold")
    # container
    ax.add_patch(FancyBboxPatch((0.5, 0.5), 7, 5, boxstyle="square",
                                fc="#e3f2fd", ec="#1565c0", lw=2.5, alpha=0.5))
    ax.text(4, 3.2, "Dilute H₂SO₄\n(electrolyte)", ha="center", fontsize=11, color="#0d47a1")
    # cathode (-)
    ax.add_patch(FancyBboxPatch((1, 1), 0.6, 4, boxstyle="square",
                                fc="#78909c", ec="black", lw=2))
    ax.text(1.3, 5.8, "Cathode (−)", ha="center", fontsize=10, fontweight="bold", color="#37474f")
    ax.text(1.3, 0.3, "H₂ gas\n↑", ha="center", fontsize=9.5, color="#1565c0")
    for y in [3.5, 4.2, 4.9]:
        ax.add_patch(Circle((1.9, y), 0.12, fc="#bbdefb", ec="blue"))
        ax.text(2.1, y, "H⁺→e⁻", fontsize=7.5, color="blue", va="center")
    # anode (+)
    ax.add_patch(FancyBboxPatch((6.4, 1), 0.6, 4, boxstyle="square",
                                fc="#ff8a65", ec="black", lw=2))
    ax.text(6.7, 5.8, "Anode (+)", ha="center", fontsize=10, fontweight="bold", color="#bf360c")
    ax.text(6.7, 0.3, "O₂ gas\n↑", ha="center", fontsize=9.5, color="#c62828")
    # battery
    ax.text(4, 6.5, "Battery / DC Source  (+) ————— (−)", ha="center",
            fontsize=10, color="black", fontweight="bold")
    fig.tight_layout()
    return fig

def make_dilution():
    """Concentration before and after dilution"""
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    for ax in axes:
        ax.set_xlim(0, 5); ax.set_ylim(0, 8); ax.axis("off")

    def draw_beaker(ax, vol_label, conc_label, n_dots, color, title):
        # beaker shape
        ax.add_patch(FancyBboxPatch((0.5, 0.5), 4, 5.5, boxstyle="square",
                                    fc=color, ec="#1565c0", lw=2.5, alpha=0.5))
        ax.text(2.5, 6.5, title, ha="center", fontsize=11, fontweight="bold")
        ax.text(2.5, 0.2, vol_label, ha="center", fontsize=10, color="#1565c0")
        ax.text(2.5, 5.8, conc_label, ha="center", fontsize=11, color="#c62828", fontweight="bold")
        rng = np.random.default_rng(42)
        xs = rng.uniform(0.8, 4.2, n_dots)
        ys = rng.uniform(0.8, 5.2, n_dots)
        for x, y in zip(xs, ys):
            ax.add_patch(Circle((x, y), 0.18, fc="#ef5350", ec="none", alpha=0.8))

    draw_beaker(axes[0], "Volume = 100 mL", "C = 2 mol/L", 30, "#bbdefb", "BEFORE\n(Concentrated)")
    draw_beaker(axes[1], "Volume = 400 mL\n(water added)", "C = ?", 30, "#e8f5e9", "AFTER\n(Diluted)")
    axes[1].text(2.5, 3.0, "C₁V₁ = C₂V₂", ha="center", fontsize=12, color="green", fontweight="bold")
    fig.suptitle("Dilution — Conservation of Moles", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig

def make_periodic_trend():
    """Section of periodic table showing atomic radius trend"""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_xlim(0, 8); ax.set_ylim(0, 5); ax.axis("off")
    ax.set_title("Atomic Radius Trend in the Periodic Table", fontsize=13, fontweight="bold")
    elements = [
        # (symbol, period, group, Z, color)
        ("Li", 2, 1, 3,  "#ef9a9a"), ("Be", 2, 2, 4,  "#f48fb1"),
        ("B",  2, 3, 5,  "#ce93d8"), ("C",  2, 4, 6,  "#90caf9"),
        ("N",  2, 5, 7,  "#80cbc4"), ("O",  2, 6, 8,  "#a5d6a7"),
        ("Na", 3, 1, 11, "#ef5350"), ("Mg", 3, 2, 12, "#f06292"),
        ("Al", 3, 3, 13, "#ab47bc"), ("Si", 3, 4, 14, "#42a5f5"),
        ("P",  3, 5, 15, "#26a69a"), ("S",  3, 6, 16, "#66bb6a"),
    ]
    for sym, period, group, Z, c in elements:
        x = group * 1.1 - 0.5
        y = 5 - period * 1.5
        ax.add_patch(FancyBboxPatch((x-0.4, y-0.35), 0.8, 0.7,
                                    boxstyle="round,pad=0.05", fc=c, ec="black", lw=1.2))
        ax.text(x, y+0.05, sym, ha="center", va="center", fontsize=12, fontweight="bold")
        ax.text(x, y-0.2, str(Z), ha="center", va="center", fontsize=7.5, color="#333")
    # arrows showing trends
    ax.annotate("", xy=(7.2, 3.25), xytext=(0.5, 3.25),
                arrowprops=dict(arrowstyle="-|>", color="blue", lw=2))
    ax.text(3.8, 3.55, "Atomic radius decreases →", ha="center", fontsize=9.5, color="blue")
    ax.annotate("", xy=(0.5, 0.5), xytext=(0.5, 3.25),
                arrowprops=dict(arrowstyle="-|>", color="red", lw=2))
    ax.text(0.3, 1.8, "Atomic\nradius\nincreases\n↓", ha="center", fontsize=8.5, color="red")
    fig.tight_layout()
    return fig

def make_mole_molecule():
    """CO2 molecule diagram with mole concept"""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_xlim(0, 8); ax.set_ylim(0, 5); ax.axis("off")
    ax.set_title("CO₂ Molecule — Mole Concept", fontsize=13, fontweight="bold")
    # molecule
    ax.add_patch(Circle((2, 2.5), 0.6, fc="#ef5350", ec="black", lw=2))
    ax.text(2, 2.5, "O", ha="center", va="center", fontsize=16, fontweight="bold", color="white")
    ax.add_patch(Circle((4, 2.5), 0.75, fc="#78909c", ec="black", lw=2))
    ax.text(4, 2.5, "C", ha="center", va="center", fontsize=16, fontweight="bold", color="white")
    ax.add_patch(Circle((6, 2.5), 0.6, fc="#ef5350", ec="black", lw=2))
    ax.text(6, 2.5, "O", ha="center", va="center", fontsize=16, fontweight="bold", color="white")
    ax.plot([2.6, 3.25], [2.5, 2.5], "k-", lw=3)
    ax.plot([4.75, 5.4], [2.5, 2.5], "k-", lw=3)
    ax.plot([2.6, 3.25], [2.65, 2.65], "k-", lw=3)
    ax.plot([4.75, 5.4], [2.65, 2.65], "k-", lw=3)
    # data box
    box_text = ("Molar mass of CO₂ = 44 g/mol\n"
                "Avogadro's number = 6.022 × 10²³\n"
                "1 mole CO₂ = 44 g = 6.022×10²³ molecules")
    ax.text(4, 0.8, box_text, ha="center", va="center", fontsize=10,
            bbox=dict(fc="#e8f5e9", ec="#388e3c", lw=1.5, boxstyle="round,pad=0.4"))
    fig.tight_layout()
    return fig


# ── Biology image generators ──────────────────────────────────────────────────

def make_cell_comparison():
    """Plant cell vs Animal cell side-by-side"""
    fig, axes = plt.subplots(1, 2, figsize=(9, 5))
    titles = ["Plant Cell", "Animal Cell"]
    for ax, title in zip(axes, titles):
        ax.set_xlim(0, 6); ax.set_ylim(0, 6); ax.axis("off")
        ax.set_title(title, fontsize=12, fontweight="bold")
        is_plant = (title == "Plant Cell")
        # cell wall (plant only)
        if is_plant:
            ax.add_patch(FancyBboxPatch((0.3, 0.3), 5.4, 5.4, boxstyle="square",
                                        fc="none", ec="#4caf50", lw=3))
            ax.text(3, 0.1, "Cell Wall", ha="center", fontsize=8.5, color="#2e7d32")
        # cell membrane
        shape = "square" if is_plant else "round,pad=0.3"
        ax.add_patch(FancyBboxPatch((0.6, 0.6), 4.8, 4.8, boxstyle=shape,
                                    fc="#e3f2fd", ec="#1565c0", lw=2))
        ax.text(3, 0.45, "Cell Membrane", ha="center", fontsize=8.5, color="#1565c0")
        # nucleus
        ax.add_patch(Circle((3, 3.2), 0.7, fc="#fff9c4", ec="#f57f17", lw=2))
        ax.text(3, 3.2, "Nucleus", ha="center", va="center", fontsize=8, fontweight="bold")
        # mitochondria
        ax.add_patch(FancyBboxPatch((1.2, 1.5), 1.0, 0.5, boxstyle="round,pad=0.1",
                                    fc="#ffccbc", ec="#bf360c", lw=1.5))
        ax.text(1.7, 1.75, "Mito.", ha="center", va="center", fontsize=7.5)
        # ER
        ax.add_patch(FancyBboxPatch((3.8, 1.5), 1.2, 0.4, boxstyle="round,pad=0.05",
                                    fc="#f8bbd0", ec="#880e4f", lw=1.5))
        ax.text(4.4, 1.7, "ER", ha="center", va="center", fontsize=7.5)
        # vacuole
        if is_plant:
            ax.add_patch(Circle((2.2, 3.8), 0.9, fc="#b3e5fc", ec="#0277bd", lw=1.5, alpha=0.7))
            ax.text(2.2, 3.8, "Large\nVacuole", ha="center", va="center", fontsize=7.5, color="#01579b")
        else:
            ax.add_patch(Circle((2.0, 4.0), 0.35, fc="#b3e5fc", ec="#0277bd", lw=1.5))
            ax.text(2.0, 4.5, "Small\nvacuole", ha="center", fontsize=7, color="#01579b")
        # chloroplast (plant only)
        if is_plant:
            ax.add_patch(FancyBboxPatch((3.8, 3.5), 1.3, 0.5, boxstyle="round,pad=0.1",
                                        fc="#c8e6c9", ec="#1b5e20", lw=1.5))
            ax.text(4.45, 3.75, "Chloroplast", ha="center", va="center", fontsize=7.5, color="#1b5e20")
        # centriole (animal only)
        if not is_plant:
            ax.add_patch(Circle((4.5, 4.2), 0.28, fc="#e1bee7", ec="#6a1b9a", lw=1.5))
            ax.text(4.5, 4.65, "Centriole", ha="center", fontsize=7.5, color="#6a1b9a")

    fig.suptitle("Plant Cell vs Animal Cell", fontsize=13, fontweight="bold", y=1.01)
    fig.tight_layout()
    return fig

def make_food_web():
    """Food web diagram for a grassland ecosystem"""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title("Grassland Food Web", fontsize=13, fontweight="bold")

    nodes = {
        "Grass":      (5.0, 0.5),
        "Grasshopper":(2.5, 2.0),
        "Rabbit":     (7.5, 2.0),
        "Frog":       (2.5, 3.5),
        "Fox":        (7.5, 3.5),
        "Snake":      (5.0, 3.5),
        "Hawk":       (5.0, 5.2),
    }
    node_colors = {
        "Grass":"#a5d6a7","Grasshopper":"#fff59d","Rabbit":"#ffcc80",
        "Frog":"#80cbc4","Fox":"#ef9a9a","Snake":"#ce93d8","Hawk":"#90caf9"
    }
    edges = [("Grass","Grasshopper"),("Grass","Rabbit"),
             ("Grasshopper","Frog"),("Grasshopper","Snake"),
             ("Rabbit","Fox"),("Rabbit","Snake"),
             ("Frog","Snake"),("Frog","Hawk"),
             ("Snake","Hawk"),("Fox","Hawk")]

    for (a, b) in edges:
        x1,y1 = nodes[a]; x2,y2 = nodes[b]
        ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle="-|>", color="#78909c", lw=1.5))
    for name, (x, y) in nodes.items():
        ax.add_patch(FancyBboxPatch((x-0.9, y-0.3), 1.8, 0.6,
                                    boxstyle="round,pad=0.1",
                                    fc=node_colors[name], ec="black", lw=1.5))
        ax.text(x, y, name, ha="center", va="center", fontsize=9.5, fontweight="bold")
    fig.tight_layout()
    return fig

def make_neuron():
    """Neuron structure diagram"""
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    ax.set_title("Structure of a Neuron", fontsize=13, fontweight="bold")
    # cell body
    ax.add_patch(Circle((3.0, 2.5), 0.9, fc="#fff9c4", ec="#f57f17", lw=2.5))
    ax.text(3.0, 2.5, "Cell\nBody", ha="center", va="center", fontsize=9, fontweight="bold")
    ax.text(3.0, 1.3, "Nucleus inside", ha="center", fontsize=8, color="#e65100")
    # dendrites
    for angle in [150, 180, 210]:
        a = np.radians(angle)
        ax.annotate("", xy=(3.0+0.9*np.cos(a), 2.5+0.9*np.sin(a)),
                    xytext=(3.0+1.8*np.cos(a), 2.5+1.8*np.sin(a)),
                    arrowprops=dict(arrowstyle="-|>", color="#42a5f5", lw=2))
    ax.text(1.0, 2.5, "Dendrites\n(receive signals)", ha="center", fontsize=8.5, color="#1565c0")
    # axon
    ax.plot([3.9, 8.5], [2.5, 2.5], "#ef5350", lw=4)
    ax.text(6.2, 2.9, "Axon", ha="center", fontsize=10, color="#b71c1c", fontweight="bold")
    # myelin sheath bumps
    for x in [4.5, 5.2, 5.9, 6.6, 7.3]:
        ax.add_patch(FancyBboxPatch((x-0.25, 2.2), 0.5, 0.6,
                                    boxstyle="round,pad=0.05", fc="#c8e6c9", ec="#388e3c", lw=1, alpha=0.7))
    ax.text(6.0, 1.8, "Myelin Sheath", ha="center", fontsize=8.5, color="#2e7d32")
    # axon terminal
    ax.add_patch(Circle((8.8, 2.5), 0.4, fc="#f8bbd0", ec="#880e4f", lw=2))
    ax.text(8.8, 1.8, "Axon\nTerminal\n(sends signal)", ha="center", fontsize=8, color="#880e4f")
    # direction arrow
    ax.annotate("", xy=(8.2, 3.5), xytext=(4.5, 3.5),
                arrowprops=dict(arrowstyle="-|>", color="#7b1fa2", lw=2, ls="dashed"))
    ax.text(6.3, 3.8, "Impulse direction →", fontsize=9, color="#7b1fa2", ha="center")
    fig.tight_layout()
    return fig

def make_osmosis():
    """Osmosis — three cells in different solutions"""
    fig, axes = plt.subplots(1, 3, figsize=(9, 4.5))
    titles = ["Hypotonic Solution\n(More water outside)", "Isotonic Solution\n(Equal concentration)", "Hypertonic Solution\n(Less water outside)"]
    colors = ["#bbdefb","#e8f5e9","#ffcdd2"]
    cell_sizes = [1.1, 0.8, 0.5]
    for ax, title, bg, cs in zip(axes, titles, colors, cell_sizes):
        ax.set_xlim(0, 4); ax.set_ylim(0, 5); ax.axis("off")
        ax.set_title(title, fontsize=9.5, fontweight="bold")
        ax.add_patch(FancyBboxPatch((0.2, 0.5), 3.6, 4, boxstyle="round,pad=0.1",
                                    fc=bg, ec="#90a4ae", lw=2))
        # cell
        ax.add_patch(Circle((2, 2.5), cs, fc="#fff9c4", ec="#f57f17", lw=2.5))
        ax.text(2, 2.5, "Cell", ha="center", va="center", fontsize=9, fontweight="bold")
        # dots for water molecules
        rng = np.random.default_rng(7)
        n = 20 if bg == "#bbdefb" else (12 if bg == "#e8f5e9" else 5)
        for _ in range(n):
            for trial in range(20):
                x = rng.uniform(0.3, 3.7)
                y = rng.uniform(0.6, 4.4)
                if (x-2)**2 + (y-2.5)**2 > (cs+0.25)**2:
                    ax.add_patch(Circle((x, y), 0.1, fc="#42a5f5", ec="none", alpha=0.7))
                    break
    fig.suptitle("Effect of Solution Concentration on Cell (Osmosis)", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig

def make_mitosis():
    """4-phase mitosis diagram"""
    fig, axes = plt.subplots(1, 4, figsize=(10, 3.5))
    phases = ["Prophase", "Metaphase", "Anaphase", "Telophase"]
    colors = ["#e3f2fd","#e8f5e9","#fff9c4","#fce4ec"]
    for ax, phase, c in zip(axes, phases, colors):
        ax.set_xlim(-2,2); ax.set_ylim(-2,2); ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(Circle((0,0), 1.8, fc=c, ec="#78909c", lw=2))
        ax.set_title(phase, fontsize=10, fontweight="bold")
        if phase == "Prophase":
            for a in np.linspace(0.1, np.pi-0.1, 3):
                ax.plot([-0.6*np.cos(a), 0.6*np.cos(a)],
                        [-0.5+0.4*np.sin(a), -0.5+0.4*np.sin(a)], "#1565c0", lw=4)
            ax.text(0, -1.5, "Chromosomes\ncondense", ha="center", fontsize=7.5)
        elif phase == "Metaphase":
            for x in [-0.5, 0, 0.5]:
                ax.plot([x, x], [-0.5, 0.5], "#1565c0", lw=4)
            ax.plot([-1.5, 1.5],[0,0], "#e53935", lw=1, ls="--")
            ax.text(0, -1.5, "Align at\nequatorial plate", ha="center", fontsize=7.5)
        elif phase == "Anaphase":
            for x in [-0.5, 0, 0.5]:
                ax.plot([x, x], [0.3, 1.1], "#1565c0", lw=4)
                ax.plot([x, x], [-0.3, -1.1], "#1565c0", lw=4)
            ax.text(0, -1.5, "Chromatids\nseparate", ha="center", fontsize=7.5)
        else:  # Telophase
            ax.add_patch(Circle((0, 0.8), 0.55, fc="#fff9c4", ec="#f57f17", lw=1.5))
            ax.add_patch(Circle((0,-0.8), 0.55, fc="#fff9c4", ec="#f57f17", lw=1.5))
            ax.text(0, -1.5, "Two nuclei\nform", ha="center", fontsize=7.5)
    fig.suptitle("Stages of Mitosis", fontsize=12, fontweight="bold")
    fig.tight_layout()
    return fig

def make_nitrogen_cycle():
    """Simplified nitrogen cycle"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.axis("off")
    ax.set_title("The Nitrogen Cycle", fontsize=13, fontweight="bold")
    nodes = {
        "Atmospheric N₂":  (5.0, 7.0),
        "Soil Nitrates":   (1.5, 3.5),
        "Plants":          (3.5, 1.5),
        "Animals":         (6.5, 1.5),
        "Dead Organic\nMatter": (5.0, 4.0),
        "Ammonia (NH₃)":   (8.5, 3.5),
    }
    nc = {"Atmospheric N₂":"#bbdefb","Soil Nitrates":"#c8e6c9","Plants":"#a5d6a7",
          "Animals":"#ffcc80","Dead Organic\nMatter":"#d7ccc8","Ammonia (NH₃)":"#fff9c4"}
    for name, (x,y) in nodes.items():
        ax.add_patch(FancyBboxPatch((x-1.1, y-0.4), 2.2, 0.9,
                                    boxstyle="round,pad=0.1",
                                    fc=nc[name], ec="black", lw=1.5))
        ax.text(x, y+0.05, name, ha="center", va="center", fontsize=8.5, fontweight="bold")

    edges = [
        ("Atmospheric N₂","Soil Nitrates","Nitrogen\nFixation","#1565c0"),
        ("Soil Nitrates","Plants","Absorption","#2e7d32"),
        ("Plants","Animals","Consumption","#e65100"),
        ("Animals","Dead Organic\nMatter","Death/Excretion","#795548"),
        ("Plants","Dead Organic\nMatter","Death","#795548"),
        ("Dead Organic\nMatter","Ammonia (NH₃)","Decomposition","#6a1b9a"),
        ("Ammonia (NH₃)","Soil Nitrates","Nitrification","#37474f"),
        ("Soil Nitrates","Atmospheric N₂","Denitrification","#c62828"),
    ]
    for src, dst, lbl, col in edges:
        x1,y1 = nodes[src]; x2,y2 = nodes[dst]
        ax.annotate("", xy=(x2, y2+0.35), xytext=(x1, y1-0.35),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8))
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.15, my, lbl, fontsize=7.5, color=col, ha="center",
                bbox=dict(fc="white", ec="none", alpha=0.7))
    fig.tight_layout()
    return fig

def make_digestive_system():
    """Simplified human digestive system"""
    fig, ax = plt.subplots(figsize=(5, 7))
    ax.set_xlim(0, 6); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("Human Digestive System", fontsize=13, fontweight="bold")
    organs = [
        ((3, 9.2), "Mouth", 0.5, "#ffcc80"),
        ((3, 8.1), "Oesophagus", 0.4, "#f48fb1"),
        ((3, 6.8), "Stomach", 0.8, "#ef9a9a"),
        ((3, 5.3), "Small\nIntestine", 0.75, "#a5d6a7"),
        ((3, 3.6), "Large\nIntestine", 0.75, "#80cbc4"),
        ((3, 2.2), "Rectum", 0.45, "#ce93d8"),
        ((3, 1.0), "Anus", 0.35, "#b0bec5"),
    ]
    for (x,y), name, r, c in organs:
        ax.add_patch(Circle((x,y), r, fc=c, ec="black", lw=1.8))
        ax.text(x+r+0.15, y, name, va="center", fontsize=9.5, fontweight="bold")
        if name not in ["Mouth","Anus"]:
            prev_y = organs[organs.index(((x,y),name,r,c))-1][0][1]
            ax.plot([x, x], [y+r, prev_y-organs[organs.index(((x,y),name,r,c))-1][2]],
                    "gray", lw=3)
    # accessory organs
    ax.add_patch(Circle((1.2, 6.2), 0.4, fc="#fff9c4", ec="#f57f17", lw=1.5))
    ax.text(0.3, 6.2, "Liver", va="center", fontsize=9)
    ax.add_patch(Circle((1.2, 5.3), 0.35, fc="#c8e6c9", ec="#388e3c", lw=1.5))
    ax.text(0.1, 5.3, "Pancreas", va="center", fontsize=9)
    fig.tight_layout()
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# QUESTIONS
# ══════════════════════════════════════════════════════════════════════════════

def build_questions():
    qs = []

    # ── PHYSICS ──────────────────────────────────────────────────────────────

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Motion","subTopic":"Graphs of Motion",
        "questionText":(
            "The distance-time graph above shows the motion of an object. "
            "During which time interval is the object stationary, "
            "and what is the average speed over the entire 12 seconds?"),
        "options":["A: 4–8 s; 12.5 m/s","B: 4–8 s; 7.5 m/s",
                   "C: 0–4 s; 12.5 m/s","D: 0–4 s; 7.5 m/s"],
        "correctAnswer":"B",
        "explanation":(
            "The graph is flat between 4 and 8 seconds (distance stays at 60 m), "
            "so the object is stationary in that interval. "
            "Total distance = 90 m in 12 s → average speed = 90/12 = 7.5 m/s."),
        "make": make_dt_graph, "suffix": "phys9_dtgraph"
    })

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Motion","subTopic":"Velocity-Time Graph Area",
        "questionText":(
            "In the velocity-time graph shown, the object accelerates uniformly "
            "from rest to 20 m/s in 5 s, then travels at constant velocity for "
            "another 5 s. What is the total distance covered in 10 seconds?"),
        "options":["A: 100 m","B: 125 m","C: 150 m","D: 200 m"],
        "correctAnswer":"C",
        "explanation":(
            "Distance = area under the v-t graph. "
            "Triangle (0–5 s): ½ × 5 × 20 = 50 m. "
            "Rectangle (5–10 s): 5 × 20 = 100 m. "
            "Total = 150 m."),
        "make": make_vt_graph, "suffix": "phys9_vtgraph"
    })

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Physics - Force and Laws of Motion","subTopic":"Newton's Second Law Application",
        "questionText":(
            "The diagram shows two horizontal forces acting on a 4 kg block on a "
            "frictionless surface: F₁ = 50 N to the right and F₂ = 18 N to the left. "
            "What is the acceleration of the block?"),
        "options":["A: 4 m/s²","B: 6 m/s²","C: 8 m/s²","D: 12.5 m/s²"],
        "correctAnswer":"C",
        "explanation":(
            "Net force = 50 − 18 = 32 N (rightward). "
            "Newton's 2nd law: a = F_net / m = 32 / 4 = 8 m/s²."),
        "make": make_newtons_second, "suffix": "phys9_n2law"
    })

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Physics - Force and Laws of Motion","subTopic":"Conservation of Momentum",
        "questionText":(
            "Cart A (3 kg, 6 m/s) collides with stationary cart B (2 kg) and they "
            "stick together (perfectly inelastic collision) as shown. "
            "What is their combined velocity after the collision?"),
        "options":["A: 2.4 m/s","B: 3.0 m/s","C: 3.6 m/s","D: 4.5 m/s"],
        "correctAnswer":"C",
        "explanation":(
            "By conservation of momentum: p_before = p_after. "
            "3 × 6 + 2 × 0 = (3+2) × v → 18 = 5v → v = 3.6 m/s."),
        "make": make_momentum_collision, "suffix": "phys9_momentum"
    })

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Work & Energy","subTopic":"Work-Energy on Incline",
        "questionText":(
            "A 5 kg block slides from rest down a frictionless inclined plane of "
            "vertical height 4 m as shown (g = 10 m/s²). "
            "What is the kinetic energy of the block at the bottom?"),
        "options":["A: 100 J","B: 150 J","C: 200 J","D: 250 J"],
        "correctAnswer":"C",
        "explanation":(
            "By energy conservation (frictionless): KE at bottom = loss in PE = mgh "
            "= 5 × 10 × 4 = 200 J."),
        "make": make_work_incline, "suffix": "phys9_incline"
    })

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Forces","subTopic":"Principle of Moments",
        "questionText":(
            "The lever shown has a pivot at the centre. F₁ = 80 N acts at 3 m to "
            "the left of the pivot. What force F₂ must act at 2 m to the right to "
            "keep the lever in equilibrium?"),
        "options":["A: 40 N","B: 80 N","C: 120 N","D: 160 N"],
        "correctAnswer":"C",
        "explanation":(
            "Principle of moments: clockwise moment = anticlockwise moment. "
            "F₁ × d₁ = F₂ × d₂ → 80 × 3 = F₂ × 2 → F₂ = 240/2 = 120 N."),
        "make": make_lever, "suffix": "phys9_moments"
    })

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Physics - Sound","subTopic":"Frequency from Wave Diagram",
        "questionText":(
            "The diagram shows a sound wave travelling at 340 m/s. "
            "The wavelength λ is labelled as 0.85 m. "
            "What is the frequency of this sound wave?"),
        "options":["A: 200 Hz","B: 289 Hz","C: 400 Hz","D: 510 Hz"],
        "correctAnswer":"C",
        "explanation":(
            "Speed = frequency × wavelength → f = v / λ = 340 / 0.85 = 400 Hz."),
        "make": make_sound_wave, "suffix": "phys9_soundwave"
    })

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Forces","subTopic":"Buoyancy and Apparent Weight",
        "questionText":(
            "An object of true weight 5 N is submerged in water. "
            "The spring balance reads 3 N as shown in the diagram. "
            "What is the buoyant force acting on the object?"),
        "options":["A: 1 N","B: 2 N","C: 3 N","D: 5 N"],
        "correctAnswer":"B",
        "explanation":(
            "Buoyant force = True weight − Apparent weight = 5 − 3 = 2 N. "
            "This equals the weight of water displaced (Archimedes' Principle)."),
        "make": make_buoyancy, "suffix": "phys9_buoyancy"
    })

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Gravitation","subTopic":"Free Fall Distance",
        "questionText":(
            "The diagram shows positions of a freely falling object at t = 0, 1, 2, "
            "and 3 seconds. Using s = ½gt² with g = 10 m/s², "
            "what is the distance fallen in the 3rd second alone (from t=2 to t=3)?"),
        "options":["A: 20 m","B: 25 m","C: 30 m","D: 45 m"],
        "correctAnswer":"B",
        "explanation":(
            "Distance at t=3: s₃ = ½×10×9 = 45 m. "
            "Distance at t=2: s₂ = ½×10×4 = 20 m. "
            "Distance in 3rd second = 45 − 20 = 25 m."),
        "make": make_free_fall, "suffix": "phys9_freefall"
    })

    qs.append({
        "subject":"Science-Physics","grade":9,"difficulty":"Olympiad",
        "topic":"Gravitation","subTopic":"Kepler's Third Law Satellites",
        "questionText":(
            "The diagram shows two satellites A and B orbiting a planet. "
            "Satellite A orbits at radius R with period T. "
            "Satellite B orbits at radius 2R. Using Kepler's third law (T² ∝ r³), "
            "what is the period of satellite B?"),
        "options":["A: 2T","B: 2√2 T","C: 4T","D: 8T"],
        "correctAnswer":"B",
        "explanation":(
            "T² ∝ r³ → T_B²/T_A² = (2R)³/R³ = 8 → T_B/T_A = √8 = 2√2. "
            "So T_B = 2√2 × T ≈ 2.83T."),
        "make": make_gravitational_satellite, "suffix": "phys9_kepler"
    })

    # ── CHEMISTRY ────────────────────────────────────────────────────────────

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Atomic Structure","subTopic":"Bohr Model — Electron Shells",
        "questionText":(
            "The Bohr model shown has the electron configuration K=2, L=8, M=3. "
            "Identify the element and state the number of electrons in its "
            "outermost shell."),
        "options":["A: Silicon — 4 electrons","B: Aluminium — 3 electrons",
                   "C: Phosphorus — 5 electrons","D: Magnesium — 2 electrons"],
        "correctAnswer":"B",
        "explanation":(
            "K(2) + L(8) + M(3) = 13 electrons → Atomic number 13 → Aluminium (Al). "
            "The outermost shell (M) has 3 electrons."),
        "make": lambda: make_bohr_atom(13, 14, [2,8,3], "Al", "Aluminium"),
        "suffix": "chem9_bohr_al"
    })

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Matter","subTopic":"Chromatography Rf Value",
        "questionText":(
            "In the paper chromatography diagram, the solvent front travelled 9.6 cm "
            "from the baseline. Spot A is at 7.2 cm and Spot B is at 5.5 cm. "
            "What are the Rf values of A and B respectively?"),
        "options":["A: 0.75 and 0.57","B: 0.72 and 0.50",
                   "C: 0.80 and 0.60","D: 0.65 and 0.55"],
        "correctAnswer":"A",
        "explanation":(
            "Rf = distance travelled by spot / distance travelled by solvent front. "
            "Rf(A) = 7.2/9.6 = 0.75; Rf(B) = 5.5/9.6 ≈ 0.57."),
        "make": make_chromatography, "suffix": "chem9_chroma"
    })

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Matter","subTopic":"Distillation — Component Collection Order",
        "questionText":(
            "The distillation apparatus shown is used to separate a mixture of "
            "ethanol (boiling point 78°C) and water (boiling point 100°C). "
            "What does the distillate collected first consist of, "
            "and why?"),
        "options":[
            "A: Ethanol — it has a lower boiling point and vaporises first",
            "B: Water — it has a higher boiling point and remains",
            "C: Both together — they have similar densities",
            "D: Water — it condenses faster in the condenser"],
        "correctAnswer":"A",
        "explanation":(
            "In distillation, the component with the lower boiling point vaporises "
            "first. Ethanol (78°C) vaporises before water (100°C), travels through "
            "the condenser, and is collected as the first distillate."),
        "make": make_distillation, "suffix": "chem9_distill"
    })

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Chemical Reactions","subTopic":"Electrolysis Products",
        "questionText":(
            "In the electrolysis of dilute H₂SO₄ shown, which gas is produced "
            "at the cathode and which at the anode?"),
        "options":[
            "A: Cathode → H₂ ; Anode → O₂",
            "B: Cathode → O₂ ; Anode → H₂",
            "C: Cathode → SO₂ ; Anode → H₂",
            "D: Cathode → H₂ ; Anode → SO₂"],
        "correctAnswer":"A",
        "explanation":(
            "At the cathode (negative electrode), H⁺ ions are reduced: "
            "2H⁺ + 2e⁻ → H₂↑. At the anode (positive electrode), "
            "OH⁻ ions are oxidised: 4OH⁻ → 2H₂O + O₂↑ + 4e⁻."),
        "make": make_electrolysis, "suffix": "chem9_electro"
    })

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Matter","subTopic":"Dilution Calculation",
        "questionText":(
            "100 mL of a 2 mol/L solution is diluted to 400 mL by adding water, "
            "as shown in the diagram. Using C₁V₁ = C₂V₂, "
            "what is the new concentration?"),
        "options":["A: 0.25 mol/L","B: 0.5 mol/L","C: 1.0 mol/L","D: 4.0 mol/L"],
        "correctAnswer":"B",
        "explanation":(
            "C₁V₁ = C₂V₂ → 2 × 100 = C₂ × 400 → C₂ = 200/400 = 0.5 mol/L."),
        "make": make_dilution, "suffix": "chem9_dilution"
    })

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Matter","subTopic":"Periodic Table — Atomic Radius Trend",
        "questionText":(
            "The section of the periodic table shown includes Period 2 and Period 3 "
            "elements. In which direction does atomic radius increase, "
            "and what is the correct reason?"),
        "options":[
            "A: Left to right across a period — more protons attract electrons closer",
            "B: Right to left across a period — fewer protons allow larger orbitals",
            "C: Left to right — electrons fill lower-energy orbitals",
            "D: Top to bottom — electron shells increase, but protons stay constant"],
        "correctAnswer":"A",
        "explanation":(
            "Across a period (left to right), nuclear charge (protons) increases "
            "while electrons are added to the same shell, so the effective nuclear "
            "pull increases and pulls electrons closer — atomic radius decreases "
            "left to right. Conversely, radius increases right to left. "
            "Down a group, new shells are added so radius increases."),
        "make": make_periodic_trend, "suffix": "chem9_periodic"
    })

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Chemistry - Atoms and Molecules","subTopic":"Mole Concept — CO₂",
        "questionText":(
            "Using the CO₂ diagram shown, if the molar mass of CO₂ = 44 g/mol and "
            "Avogadro's number = 6.022 × 10²³, how many molecules are in 11 g of CO₂?"),
        "options":["A: 1.505 × 10²³","B: 3.011 × 10²³",
                   "C: 6.022 × 10²³","D: 1.204 × 10²⁴"],
        "correctAnswer":"A",
        "explanation":(
            "Moles of CO₂ = 11/44 = 0.25 mol. "
            "Number of molecules = 0.25 × 6.022 × 10²³ = 1.505 × 10²³."),
        "make": make_mole_molecule, "suffix": "chem9_mole"
    })

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Atomic Structure","subTopic":"Bohr Model — Phosphorus",
        "questionText":(
            "A Bohr model shows K=2, L=8, M=5. "
            "How many valence electrons does this element have, "
            "and what is its most common oxidation state in ionic compounds?"),
        "options":["A: 3 valence electrons; +3","B: 5 valence electrons; −3",
                   "C: 5 valence electrons; +5","D: 8 valence electrons; −2"],
        "correctAnswer":"B",
        "explanation":(
            "K(2)+L(8)+M(5)=15 → Phosphorus (P). It has 5 valence electrons. "
            "Phosphorus commonly gains 3 electrons to achieve a stable octet, "
            "giving it an oxidation state of −3 in ionic compounds like Na₃P."),
        "make": lambda: make_bohr_atom(15, 16, [2,8,5], "P", "Phosphorus"),
        "suffix": "chem9_bohr_p"
    })

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Matter","subTopic":"Chromatography — Identifying Mixtures",
        "questionText":(
            "In the chromatography strip shown, a student tests an unknown dye and "
            "finds two distinct spots. Spot A has Rf = 0.75 and Spot B has Rf = 0.57. "
            "What does this result indicate?"),
        "options":[
            "A: The dye is a pure substance with two conformers",
            "B: The dye is a mixture of at least two different compounds",
            "C: The experiment failed — a pure dye always gives one spot",
            "D: The solvent was too concentrated"],
        "correctAnswer":"B",
        "explanation":(
            "Each spot represents a different compound. Two spots with different Rf "
            "values mean the original dye was a mixture of at least two components "
            "that travel at different rates through the stationary phase."),
        "make": make_chromatography, "suffix": "chem9_chroma2"
    })

    qs.append({
        "subject":"Science-Chemistry","grade":9,"difficulty":"Olympiad",
        "topic":"Chemical Reactions","subTopic":"Electrolysis Volume Ratio",
        "questionText":(
            "During electrolysis of dilute H₂SO₄ as shown, "
            "what is the ratio of the volume of gas collected at the "
            "cathode to that at the anode?"),
        "options":["A: 1 : 1","B: 1 : 2","C: 2 : 1","D: 4 : 1"],
        "correctAnswer":"C",
        "explanation":(
            "Cathode: 2H⁺ + 2e⁻ → H₂ (2 moles electrons → 1 mole H₂). "
            "Anode: 2H₂O → O₂ + 4H⁺ + 4e⁻ (4 moles electrons → 1 mole O₂). "
            "For the same charge, H₂ : O₂ = 2 : 1 by volume (equal conditions)."),
        "make": make_electrolysis, "suffix": "chem9_electro2"
    })

    # ── BIOLOGY ──────────────────────────────────────────────────────────────

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Biology - Cell Fundamental Unit of Life","subTopic":"Plant vs Animal Cell Differences",
        "questionText":(
            "Referring to the cell diagrams shown, which THREE structures are "
            "present in plant cells but absent in animal cells?"),
        "options":[
            "A: Cell wall, chloroplast, large central vacuole",
            "B: Cell wall, mitochondria, nucleus",
            "C: Cell membrane, ribosome, chloroplast",
            "D: Cell wall, centriole, large vacuole"],
        "correctAnswer":"A",
        "explanation":(
            "Plant cells have: (1) a rigid cell wall made of cellulose, "
            "(2) chloroplasts for photosynthesis, and (3) a large central vacuole "
            "for turgor. Animal cells have centrioles (absent in most plant cells), "
            "small vacuoles (not large central), no cell wall, no chloroplasts."),
        "make": make_cell_comparison, "suffix": "bio9_cells"
    })

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Ecology","subTopic":"Food Web — Trophic Levels",
        "questionText":(
            "In the food web shown, if all the foxes were removed, "
            "which of the following would be the most likely immediate consequence?"),
        "options":[
            "A: Grass population decreases",
            "B: Rabbit population increases",
            "C: Hawk population decreases",
            "D: Snake population decreases"],
        "correctAnswer":"B",
        "explanation":(
            "Foxes prey on rabbits. If foxes are removed, the rabbit population "
            "loses a predator and will increase. Hawks and snakes can partially "
            "compensate, but the immediate and most direct effect is rabbit "
            "population growth."),
        "make": make_food_web, "suffix": "bio9_foodweb"
    })

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Human Physiology","subTopic":"Neuron — Direction of Impulse",
        "questionText":(
            "In the neuron diagram, impulses travel in one direction. "
            "Which sequence correctly describes the path of a nerve impulse?"),
        "options":[
            "A: Axon terminal → Axon → Cell body → Dendrites",
            "B: Dendrites → Cell body → Axon → Axon terminal",
            "C: Cell body → Dendrites → Axon → Axon terminal",
            "D: Axon → Dendrites → Cell body → Axon terminal"],
        "correctAnswer":"B",
        "explanation":(
            "A nerve impulse is received by dendrites, passes through the cell body, "
            "travels along the axon (insulated by myelin sheath), and is transmitted "
            "to the next neuron or effector via the axon terminal."),
        "make": make_neuron, "suffix": "bio9_neuron"
    })

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Biology - Cell Fundamental Unit of Life","subTopic":"Osmosis in Different Solutions",
        "questionText":(
            "The diagram shows three cells placed in hypotonic, isotonic, and "
            "hypertonic solutions. In which solution does a cell placed in it "
            "become turgid (swollen), and why?"),
        "options":[
            "A: Hypertonic — water moves out by osmosis",
            "B: Isotonic — no net movement of water",
            "C: Hypotonic — water enters the cell by osmosis",
            "D: Hypertonic — solutes move in to equalise concentration"],
        "correctAnswer":"C",
        "explanation":(
            "In a hypotonic solution, the solute concentration outside the cell is "
            "lower than inside. Water moves in by osmosis (from low solute to high "
            "solute concentration), causing the cell to swell and become turgid."),
        "make": make_osmosis, "suffix": "bio9_osmosis"
    })

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Cell Biology","subTopic":"Mitosis — Metaphase Identification",
        "questionText":(
            "The diagram shows four stages of mitosis. In which labelled stage do "
            "chromosomes line up along the equatorial plate (middle of the cell)?"),
        "options":["A: Prophase","B: Metaphase","C: Anaphase","D: Telophase"],
        "correctAnswer":"B",
        "explanation":(
            "During metaphase, chromosomes are fully condensed and are aligned along "
            "the metaphase plate (equatorial plane) by spindle fibres attached to "
            "their centromeres. This alignment ensures equal distribution to daughter cells."),
        "make": make_mitosis, "suffix": "bio9_mitosis"
    })

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Human Physiology","subTopic":"Digestive System — Site of Absorption",
        "questionText":(
            "The digestive system diagram shows key organs. "
            "In which organ does maximum absorption of digested food occur, "
            "and what structural feature facilitates this?"),
        "options":[
            "A: Stomach — presence of gastric acid",
            "B: Large intestine — large surface area",
            "C: Small intestine — presence of villi increasing surface area",
            "D: Oesophagus — peristaltic movement"],
        "correctAnswer":"C",
        "explanation":(
            "The small intestine is the primary site of nutrient absorption. "
            "Its inner wall has finger-like projections called villi (and microvilli), "
            "which greatly increase the surface area to maximise absorption of "
            "glucose, amino acids, fatty acids, and glycerol."),
        "make": make_digestive_system, "suffix": "bio9_digest"
    })

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Biology - Natural Resources","subTopic":"Nitrogen Cycle — Process Identification",
        "questionText":(
            "In the nitrogen cycle diagram, which process directly converts "
            "atmospheric nitrogen (N₂) into ammonia (NH₃) or ammonium ions in the soil?"),
        "options":["A: Nitrification","B: Denitrification",
                   "C: Nitrogen fixation","D: Decomposition"],
        "correctAnswer":"C",
        "explanation":(
            "Nitrogen fixation is the conversion of atmospheric N₂ into ammonia or "
            "nitrates. This is carried out by nitrogen-fixing bacteria (e.g., "
            "Rhizobium in legume root nodules or free-living Azotobacter in soil). "
            "Nitrification converts NH₃ to nitrates; denitrification returns N₂ to "
            "the atmosphere; decomposition breaks organic matter into ammonia."),
        "make": make_nitrogen_cycle, "suffix": "bio9_nitrogencycle"
    })

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Ecology","subTopic":"Food Web — Energy Transfer",
        "questionText":(
            "In the food web shown, a hawk occupies which trophic level "
            "when it feeds on a snake that ate a frog?"),
        "options":["A: 2nd trophic level","B: 3rd trophic level",
                   "C: 4th trophic level","D: 5th trophic level"],
        "correctAnswer":"D",
        "explanation":(
            "Trophic levels along this chain: "
            "Grass (T1) → Grasshopper (T2) → Frog (T3) → Snake (T4) → Hawk (T5). "
            "When the hawk feeds on a snake that fed on a frog, it occupies the "
            "5th trophic level."),
        "make": make_food_web, "suffix": "bio9_foodweb2"
    })

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Biology - Cell Fundamental Unit of Life","subTopic":"Osmosis — Plasmolysis",
        "questionText":(
            "A plant cell is placed in a hypertonic solution as shown. "
            "What happens to the cell, and what is this phenomenon called?"),
        "options":[
            "A: The cell swells and bursts — cytolysis",
            "B: The cell shrinks and the cell membrane pulls away from the wall — plasmolysis",
            "C: The cell remains unchanged — isotonic balance",
            "D: The cell wall dissolves — lysis"],
        "correctAnswer":"B",
        "explanation":(
            "In a hypertonic solution, solute concentration is higher outside than "
            "inside the cell. Water exits by osmosis, causing the cytoplasm to shrink. "
            "In plant cells, the cell membrane (with cytoplasm) pulls away from the "
            "rigid cell wall — this is called plasmolysis."),
        "make": make_osmosis, "suffix": "bio9_plasmolysis"
    })

    qs.append({
        "subject":"Science-Biology","grade":9,"difficulty":"Olympiad",
        "topic":"Cell Biology","subTopic":"Mitosis — Purpose and Outcome",
        "questionText":(
            "From the mitosis diagram, what is the chromosome number in each "
            "daughter cell if the parent cell has 46 chromosomes?"),
        "options":["A: 23","B: 46","C: 92","D: 12"],
        "correctAnswer":"B",
        "explanation":(
            "Mitosis is an equational division — each daughter cell receives an exact "
            "copy of the parent cell's chromosomes. If the parent has 46 chromosomes "
            "(diploid), each of the two daughter cells will also have 46 chromosomes. "
            "(Meiosis, by contrast, halves the number to 23.)"),
        "make": make_mitosis, "suffix": "bio9_mitosis2"
    })

    return qs


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    questions = build_questions()
    ok = dup = err = 0
    for i, q in enumerate(questions, 1):
        make_fn = q.pop("make")
        suffix  = q.pop("suffix")
        try:
            fig_or_img = make_fn()
            url = upload_fig(fig_or_img, suffix)
            q["imageUrl"] = url
        except Exception as e:
            print(f"  [IMG FAIL] Q{i} {q['subTopic']}: {e}")
            continue

        res = post_direct(q)
        marker = "✓" if res=="OK" else ("~" if res=="DUP" else "✗")
        print(f"  {marker} Q{i:02d} [{q['subject']} G{q['grade']}] "
              f"{q['subTopic']} → {res}")
        if res=="OK": ok+=1
        elif res=="DUP": dup+=1
        else: err+=1
        time.sleep(0.5)

    print(f"\n  Done: {ok} posted, {dup} duplicates, {err} errors  (total={ok+dup+err})")

if __name__ == "__main__":
    main()
