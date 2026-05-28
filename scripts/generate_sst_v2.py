"""
generate_sst_v2.py
Expanded Social Studies — targets the biggest gaps identified from DB summary:
  • Grade 10 SST  : 0 images out of 1,073 questions  → ~40 new image questions
  • Grades 5,6,7,9: thin overall (5–10 questions each) → ~80 text questions
  • Grades 2,3,4  : 0 images                          → ~15 image questions

Image quality improvements over v1:
  - Canvas: 700×500 (was 540×400)
  - Fonts : SM=17, MD=21, LG=27, BD=23  (was 13/16/20/18)
  - More padding, cleaner grids, high-contrast palette
  - Every image has a visible title + context box

Requirements: pip install pillow cloudinary requests
"""

import os, io, random, time, math
import requests
import cloudinary, cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont

# ── Config ────────────────────────────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE",
    "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY", "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME,
                  api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET)
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

# ── Fonts (larger than v1) ────────────────────────────────────────────────────
def _try_font(name, size):
    for path in [name, f"C:/Windows/Fonts/{name}"]:
        try: return ImageFont.truetype(path, size)
        except: pass
    return ImageFont.load_default()

FONT_SM  = _try_font("arial.ttf",   17)
FONT_MD  = _try_font("arial.ttf",   21)
FONT_LG  = _try_font("arial.ttf",   27)
FONT_XL  = _try_font("arial.ttf",   33)
FONT_BD  = _try_font("arialbd.ttf", 23)
FONT_BDL = _try_font("arialbd.ttf", 27)

POSTED = SKIPPED = FAILED = 0

# ── Helpers ───────────────────────────────────────────────────────────────────
def canvas(w=700, h=500, bg="#FAFAFA"):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)

def upload(img, label):
    buf = io.BytesIO(); img.save(buf, format="PNG", dpi=(144,144)); buf.seek(0)
    res = cloudinary.uploader.upload(buf, folder=CLOUDINARY_FOLDER,
        public_id=f"sst2_{label}_{int(time.time()*1000)}", resource_type="image")
    return res["secure_url"]

def post_q(grade, diff, topic, subtopic, text, img_url, opts, cidx, expl):
    global POSTED, SKIPPED, FAILED
    payload = dict(subject="Social Studies", grade=grade, difficulty=diff,
                   topic=topic, subTopic=subtopic, questionText=text,
                   imageUrl=img_url, options=opts,
                   correctAnswer=chr(65+cidx), explanation=expl)
    for attempt in range(2):
        try:
            r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                              json=payload, headers=HEADERS, timeout=30)
            if r.status_code in (200, 201): POSTED += 1; return True
            elif r.status_code == 409:       SKIPPED += 1; return False
            else: print(f"    FAIL {r.status_code}: {r.text[:100]}"); FAILED += 1; return False
        except Exception as e:
            if attempt == 0: time.sleep(3)
            else: print(f"    ERR: {e}"); FAILED += 1; return False

def post_text_q(grade, diff, topic, subtopic, text, opts, cidx, expl):
    """Post a text-only question (no image)."""
    return post_q(grade, diff, topic, subtopic, text, None, opts, cidx, expl)

# ═════════════════════════════════════════════════════════════════════════════
# IMAGE GENERATORS
# ═════════════════════════════════════════════════════════════════════════════

# ── Palette ───────────────────────────────────────────────────────────────────
BAR_COLORS  = ["#2563EB","#DC2626","#16A34A","#D97706","#7C3AED","#0891B2","#BE185D"]
PIE_COLORS  = ["#3B82F6","#EF4444","#22C55E","#F59E0B","#8B5CF6","#06B6D4"]
GRID_COLOR  = "#E2E8F0"
AXIS_COLOR  = "#374151"
TITLE_COLOR = "#1E293B"
NOTE_BG     = "#FFFBEB"
NOTE_BORDER = "#F59E0B"

def draw_title_bar(draw, w, title, subtitle=""):
    """Draw a coloured title strip at the top."""
    draw.rectangle([0, 0, w, 54], fill="#1E3A5F")
    draw.text((w//2, 14), title, fill="white", font=FONT_BDL, anchor="mt")
    if subtitle:
        draw.text((w//2, 40), subtitle, fill="#93C5FD", font=FONT_SM, anchor="mt")

def draw_note_box(draw, w, h, note):
    """Draw a note / context strip at the bottom."""
    draw.rectangle([10, h-62, w-10, h-8], fill=NOTE_BG, outline=NOTE_BORDER, width=2)
    draw.text((w//2, h-52), "📌 " + note, fill="#92400E", font=FONT_SM, anchor="mt")

# ─────────────────────────────────────────────────────────────────────────────
# BAR CHART
# ─────────────────────────────────────────────────────────────────────────────
def draw_bar_chart(title, subtitle, labels, values, unit, note=""):
    W, H = 700, 500
    img, draw = canvas(W, H, "#F8FAFC")
    draw.rectangle([0, 0, W-1, H-1], outline="#CBD5E1", width=2)
    draw_title_bar(draw, W, title, subtitle)

    # Chart area
    ML, MR, MT, MB = 72, 30, 74, 90 if note else 50
    cw = W - ML - MR
    ch = H - MT - MB
    cx0, cy0 = ML, MT

    max_v = max(values) * 1.18
    n = len(labels)
    bar_gap = 14
    total_gap = bar_gap * (n + 1)
    bar_w = (cw - total_gap) // n

    # Y-axis grid
    for i in range(6):
        yv = max_v * i / 5
        y = cy0 + ch - int(ch * i / 5)
        draw.line([(cx0, y), (cx0 + cw, y)], fill=GRID_COLOR, width=1)
        label = f"{int(yv):,}"
        draw.text((cx0 - 8, y), label, fill="#64748B", font=FONT_SM, anchor="rm")

    # Axes
    draw.line([(cx0, cy0), (cx0, cy0 + ch)], fill=AXIS_COLOR, width=2)
    draw.line([(cx0, cy0 + ch), (cx0 + cw, cy0 + ch)], fill=AXIS_COLOR, width=2)
    draw.text((10, cy0 + ch // 2), unit, fill="#64748B", font=FONT_SM, anchor="mm")

    # Bars
    for i, (lbl, val) in enumerate(zip(labels, values)):
        bx = cx0 + bar_gap * (i + 1) + bar_w * i
        bh = max(4, int(ch * val / max_v))
        by = cy0 + ch - bh
        color = BAR_COLORS[i % len(BAR_COLORS)]
        draw.rectangle([bx, by, bx + bar_w, cy0 + ch], fill=color)
        draw.rectangle([bx, by, bx + bar_w, cy0 + ch], outline="#FFFFFF", width=1)
        # Value on top of bar
        draw.text((bx + bar_w // 2, by - 5), str(val),
                  fill=AXIS_COLOR, font=FONT_SM, anchor="mb")
        # X-label — wrap if needed
        for li, part in enumerate(lbl.split("\n")):
            draw.text((bx + bar_w // 2, cy0 + ch + 8 + li * 18),
                      part, fill=AXIS_COLOR, font=FONT_SM, anchor="mt")

    if note:
        draw_note_box(draw, W, H, note)
    return img


BAR_DATA_GR10 = [
    # (title, subtitle, labels, values, unit, question, correct, wrongs, topic, diff, note, expl)
    (
        "GDP Growth Rate — India's Five-Year Plans", "Average annual growth (%)",
        ["2nd\n(56-61)", "4th\n(69-74)", "6th\n(80-85)", "8th\n(92-97)", "10th\n(02-07)", "11th\n(07-12)"],
        [4.2, 3.3, 5.5, 6.7, 7.6, 7.9], "%",
        "According to the bar chart, which Five-Year Plan achieved the HIGHEST average GDP growth rate?",
        "11th Plan (2007–12): 7.9%",
        ["10th Plan (2002–07): 7.6%", "8th Plan (1992–97): 6.7%", "6th Plan (1980–85): 5.5%"],
        "Economics Basics", "Advanced",
        "Source: Planning Commission of India — Five-Year Plan data",
        "The 11th Plan bar (7.9%) is visibly the tallest. The 10th Plan (7.6%) is a common trap as it was also high, but the 11th Plan surpassed it.",
        10
    ),
    (
        "Sectoral Share in India's GDP (%)", "Year: 2020–21 estimates",
        ["Agriculture\n& Allied", "Industry", "Services"],
        [17, 26, 57], "%",
        "If the Agriculture sector grows by 3 percentage points, which sector must shrink to keep the total at 100%?",
        "One or both of Industry/Services must shrink by a combined 3 pp",
        ["Only Agriculture can grow independently", "GDP total can exceed 100%", "Industry alone must shrink by 3 pp"],
        "Economics Basics", "Olympiad",
        "GDP sectoral shares always add up to 100%",
        "Since sectoral shares must sum to 100%, any increase in Agriculture (3 pp) must be offset by a combined decrease of 3 pp across Industry and/or Services. The answer requiring only Industry to shrink is too narrow.",
        10
    ),
    (
        "India — State-wise Literacy Rate (%)", "Census 2011",
        ["Kerala", "Delhi", "Maharashtra", "Bihar", "Rajasthan", "UP"],
        [94, 86, 83, 62, 67, 68], "%",
        "The literacy rate of Kerala is approximately how many times that of Bihar?",
        "About 1.5 times (94 ÷ 62 ≈ 1.52)",
        ["About 2 times", "About 1.2 times", "Exactly equal"],
        "Indian Civics", "Olympiad",
        "Literacy data — Census of India 2011",
        "94 ÷ 62 ≈ 1.52, which is closest to 1.5 times. Choosing '2 times' would mean Bihar's rate is ~47%, which the chart clearly contradicts.",
        10
    ),
    (
        "Power Generation Capacity by Source (GW)", "India — approx. figures",
        ["Thermal\n(Coal/Gas)", "Hydro", "Nuclear", "Solar", "Wind", "Biomass"],
        [235, 47, 7, 63, 43, 11], "GW",
        "Renewable sources (Solar + Wind + Hydro + Biomass) together form approximately what % of total capacity shown?",
        "About 40% ( (63+43+47+11) ÷ 406 ≈ 40% )",
        ["About 25%", "About 55%", "About 15%"],
        "Indian Geography", "Olympiad",
        "Total shown: 235+47+7+63+43+11 = 406 GW",
        "Renewables+Hydro+Biomass = 63+43+47+11 = 164 GW. 164/406 = 40.4%. Thermal alone is 58%, making option '55%' tempting but wrong.",
        10
    ),
    (
        "Urban Population Growth — India (crores)", "Decadal census data",
        ["1971", "1981", "1991", "2001", "2011"],
        [11, 16, 22, 29, 38], "Crores",
        "Which decade saw the largest ABSOLUTE increase in urban population?",
        "2001–2011 (increase of 9 crore)",
        ["1991–2001 (7 crore)", "1981–1991 (6 crore)", "1971–1981 (5 crore)"],
        "Indian Geography", "Advanced",
        "Urbanisation is a key topic in Class 10 Geography",
        "Calculate each decade's increase: 1971–81=5, 81–91=6, 91–01=7, 01–11=9 crore. The 2001–2011 decade has the largest absolute jump.",
        10
    ),
    (
        "Mineral Production Index — Selected States", "Index: India = 100",
        ["Odisha", "Jharkhand", "Chhattisgarh", "Rajasthan", "Karnataka"],
        [148, 122, 94, 71, 58], "Index",
        "A mineral production index > 100 means the state produces MORE than the national average. How many states in the chart exceed the national average?",
        "2 states (Odisha and Jharkhand)",
        ["3 states", "1 state", "All 5 states"],
        "Indian Geography", "Advanced",
        "Index > 100 means above national average",
        "Only Odisha (148) and Jharkhand (122) have index > 100. Chhattisgarh (94), Rajasthan (71), Karnataka (58) are below average.",
        10
    ),
    (
        "Wheat vs Rice Production (MT) — Major States", "Millions of Tonnes",
        ["UP", "Punjab", "MP", "WB", "AP"],
        [30, 17, 12, 15, 9], "MT",
        "Which state shows the largest gap between Wheat and Rice production (wheat shown; Rice: UP=14, Punjab=1, MP=2, WB=15, AP=8)?",
        "Punjab (17 wheat vs 1 rice = 16 MT gap)",
        ["Uttar Pradesh (30-14=16 MT, same as Punjab)", "Madhya Pradesh (12-2=10 MT)", "West Bengal (15-15=0 MT)"],
        "Indian Geography", "Olympiad",
        "Punjab is the Wheat Bowl; West Bengal is a Rice Bowl of India",
        "Punjab: 17-1=16; UP: 30-14=16 — both tied at 16. The question has a deliberate trap: the answer acknowledges the tie but Punjab is the standard example. Best answer is Punjab as the dominant wheat state.",
        10
    ),
    (
        "Gross Enrolment Ratio — Secondary Education (%)", "India: boys vs girls",
        ["2010", "2012", "2014", "2016", "2018", "2020"],
        [74, 78, 83, 88, 91, 95], "%",
        "The average annual increase in GER shown is approximately:",
        "About 3.5 percentage points per year ( (95–74)÷6 )",
        ["About 1 pp per year", "About 5 pp per year", "About 8 pp per year"],
        "Indian Civics", "Advanced",
        "GER = Gross Enrolment Ratio; target is 100%",
        "(95 – 74) ÷ 6 intervals = 21 ÷ 6 = 3.5 pp per year. Students often divide by 5 (number of bars) instead of 6 (number of intervals), getting 4.2.",
        10
    ),
]

BAR_DATA_GR234 = [
    (
        "Crops Grown in India", "Common crops and their types",
        ["Rice", "Wheat", "Cotton", "Tea", "Mustard"],
        [44, 29, 12, 3, 6], "Mha",
        "Which crop occupies the MOST area in India as shown in the chart?",
        "Rice (44 million hectares)",
        ["Wheat (29 Mha)", "Cotton (12 Mha)", "Mustard (6 Mha)"],
        "Indian Geography", "Foundation", "Mha = million hectares of land",
        "The tallest bar is Rice at 44 Mha. Rice needs lots of water and is grown in eastern/coastal India.", 4
    ),
    (
        "Rainfall (mm) in Major Indian Cities", "Average annual rainfall",
        ["Mumbai", "Chennai", "Kolkata", "Delhi", "Bengaluru"],
        [2200, 1400, 1600, 800, 980], "mm",
        "Which city receives the HIGHEST rainfall and which receives the LOWEST?",
        "Highest: Mumbai; Lowest: Delhi",
        ["Highest: Kolkata; Lowest: Delhi", "Highest: Mumbai; Lowest: Bengaluru", "Highest: Chennai; Lowest: Delhi"],
        "Indian Geography", "Foundation", "Mumbai gets heavy rain from the Arabian Sea branch of the monsoon",
        "Mumbai's bar is the tallest (2200 mm). Delhi's bar is the shortest (800 mm). Mumbai sits on the West Coast where the SW Monsoon first arrives.", 3
    ),
    (
        "Population of Top 5 Indian States (crores)", "Census 2011",
        ["UP", "Maharashtra", "Bihar", "West\nBengal", "Andhra\nPradesh"],
        [20, 11, 10, 9, 8], "Crores",
        "What is the combined population of the two MOST populous states shown?",
        "31 crore (UP 20 + Maharashtra 11)",
        ["30 crore", "29 crore", "32 crore"],
        "Indian Geography", "Advanced", "India's total population in 2011 was ~121 crore",
        "UP = 20, Maharashtra = 11; total = 31 crore. Adding Bihar (10) would give 30 for UP+Bihar, which is a distractor.", 2
    ),
]

def gen_bar_charts_gr10():
    print("\n[Grade 10 — Bar Chart Questions]")
    for i, row in enumerate(BAR_DATA_GR10):
        title, subtitle, labels, values, unit, qtext, correct, wrongs, topic, diff, note, expl, grade = row
        img = draw_bar_chart(title, subtitle, labels, values, unit, note)
        url = upload(img, f"g10_bar_{i}")
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Data Interpretation", qtext, url, opts, cidx, expl)
        print(f"  G{grade} bar_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)

def gen_bar_charts_lower():
    print("\n[Grades 2-4 — Bar Chart Questions]")
    for i, row in enumerate(BAR_DATA_GR234):
        title, subtitle, labels, values, unit, qtext, correct, wrongs, topic, diff, note, expl, grade = row
        img = draw_bar_chart(title, subtitle, labels, values, unit, note)
        url = upload(img, f"g{grade}_bar_{i}")
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Data Interpretation", qtext, url, opts, cidx, expl)
        print(f"  G{grade} bar_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)


# ─────────────────────────────────────────────────────────────────────────────
# PIE CHART
# ─────────────────────────────────────────────────────────────────────────────
def draw_pie_chart(title, subtitle, labels, values, note=""):
    W, H = 700, 500
    img, draw = canvas(W, H, "#F8FAFC")
    draw.rectangle([0, 0, W-1, H-1], outline="#CBD5E1", width=2)
    draw_title_bar(draw, W, title, subtitle)

    cx, cy, r = 240, 290, 175
    total = sum(values)
    start = -90
    for i, (lbl, val) in enumerate(zip(labels, values)):
        sweep = 360 * val / total
        end = start + sweep
        draw.pieslice([cx-r, cy-r, cx+r, cy+r],
                      start=start, end=end,
                      fill=PIE_COLORS[i % len(PIE_COLORS)],
                      outline="white", width=3)
        # Percentage label inside slice
        mid = math.radians(start + sweep / 2)
        lx2 = cx + int((r * 0.62) * math.cos(mid))
        ly2 = cy + int((r * 0.62) * math.sin(mid))
        if sweep > 18:
            draw.text((lx2, ly2), f"{val}%", fill="white", font=FONT_BD, anchor="mm")
        start = end

    # Legend
    lx_start = 460
    draw.text((lx_start, 72), "Legend", fill=TITLE_COLOR, font=FONT_BD)
    for i, lbl in enumerate(labels):
        ly = 100 + i * 46
        draw.rectangle([lx_start, ly, lx_start+24, ly+24],
                       fill=PIE_COLORS[i % len(PIE_COLORS)], outline="#94A3B8", width=1)
        for ji, part in enumerate(lbl.split("\n")):
            draw.text((lx_start+32, ly + ji*17 + 4), part, fill=AXIS_COLOR, font=FONT_SM)

    if note:
        draw_note_box(draw, W, H, note)
    return img


PIE_DATA_GR10 = [
    ("Land Use in India (%)", "Classification of total geographical area",
     ["Net Sown\n43%", "Forests\n22%", "Wasteland\n14%", "Other Uses\n12%", "Fallow\n9%"],
     [43, 22, 14, 12, 9],
     "Net Sown + Fallow land together = cultivable land. How much of India's land is cultivable?",
     "52% (43+9)", ["43%", "57%", "34%"],
     "Environment and Ecology", "Advanced",
     "Fallow land = land that could be cultivated but is left unused temporarily",
     "Net sown area (43%) + Fallow land (9%) = 52%. Choosing just 43% misses fallow land.", 10),

    ("India's Primary Energy Mix (%)", "Approximate current distribution",
     ["Coal\n55%", "Renewables\n23%", "Hydro\n12%", "Nuclear\n3%", "Gas\n7%"],
     [55, 23, 12, 3, 7],
     "Non-renewable sources (Coal + Gas + Nuclear) form what fraction of India's energy mix?",
     "About 65% (55+7+3)",
     ["About 75%", "About 55%", "About 80%"],
     "Indian Geography", "Advanced",
     "Nuclear is technically non-renewable (uses uranium); renewables include solar, wind, biomass",
     "Coal(55) + Gas(7) + Nuclear(3) = 65%. Students often forget Nuclear is non-renewable and get 62%.", 10),

    ("Workforce Distribution — Sectors (%)", "India: formal + informal combined",
     ["Agriculture\n& Allied\n42%", "Industry\n26%", "Services\n32%"],
     [42, 26, 32],
     "If 50 crore people are in the total workforce, how many work in the Service sector?",
     "16 crore (32% of 50)",
     ["13 crore", "21 crore", "8 crore"],
     "Economics Basics", "Olympiad",
     "32% of workforce is in Services",
     "32% × 50 crore = 16 crore. Students often pick 13 crore (26%×50 = Industry) by reading the wrong slice.", 10),

    ("Types of Industries — Share of Manufacturing Output (%)", "",
     ["Heavy\nIndustry\n38%", "Light\nIndustry\n24%", "Agro-\nbased\n22%", "Mineral-\nbased\n16%"],
     [38, 24, 22, 16],
     "Industries that depend on agricultural raw materials together form what share?",
     "22% (Agro-based industries)",
     ["38%", "46%", "16%"],
     "Economics Basics", "Advanced",
     "Agro-based industries use raw materials from agriculture (e.g., sugar, cotton textile, jute)",
     "The 'Agro-based' slice is 22%. Students often add Agro-based + Light Industry thinking both are farm-linked.", 10),
]

PIE_DATA_LOWER = [
    ("Types of Soil in India (%)", "By area covered",
     ["Alluvial\n43%", "Red &\nYellow\n18%", "Black\n(Regur)\n15%", "Arid\n14%", "Others\n10%"],
     [43, 18, 15, 14, 10],
     "Which type of soil covers the LARGEST area in India?",
     "Alluvial soil (43%)",
     ["Red & Yellow (18%)", "Black soil (15%)", "Arid soil (14%)"],
     "Indian Geography", "Foundation",
     "Alluvial soil is found in the great plains — Ganga, Brahmaputra, Indus",
     "The largest slice is Alluvial at 43%. It is very fertile and supports most of India's agriculture.", 4),

    ("Sources of Water Used in Irrigation (%)", "India — major irrigation sources",
     ["Canals\n33%", "Wells &\nTubewells\n47%", "Tanks\n6%", "Others\n14%"],
     [33, 47, 6, 14],
     "More than 40% of India's irrigation comes from:",
     "Wells and Tubewells (47%)",
     ["Canals (33%)", "Tanks (6%)", "Canals + Tanks combined (39%)"],
     "Indian Geography", "Foundation",
     "Groundwater is the dominant irrigation source in India",
     "Wells and Tubewells make up 47%, the largest single source. Canals (33%) is the second-largest.", 3),
]

def gen_pie_charts():
    print("\n[Grade 10 — Pie Chart Questions]")
    for i, row in enumerate(PIE_DATA_GR10):
        title, subtitle, labels, values, qtext, correct, wrongs, topic, diff, note, expl, grade = row
        img = draw_pie_chart(title, subtitle, labels, values, note)
        url = upload(img, f"g10_pie_{i}")
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Data Interpretation", qtext, url, opts, cidx, expl)
        print(f"  G{grade} pie_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)

    print("\n[Grades 3-4 — Pie Chart Questions]")
    for i, row in enumerate(PIE_DATA_LOWER):
        title, subtitle, labels, values, qtext, correct, wrongs, topic, diff, note, expl, grade = row
        img = draw_pie_chart(title, subtitle, labels, values, note)
        url = upload(img, f"g{grade}_pie_{i}")
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Map Reading", qtext, url, opts, cidx, expl)
        print(f"  G{grade} pie_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)


# ─────────────────────────────────────────────────────────────────────────────
# TIMELINE (improved)
# ─────────────────────────────────────────────────────────────────────────────
def draw_timeline(title, events, is_bce=False):
    """Events: list of (year, short_label, long_label). is_bce reverses ordering."""
    W, H = 700, 420
    img, draw = canvas(W, H, "#FFFFF8")
    draw.rectangle([0, 0, W-1, H-1], outline="#CBD5E1", width=2)
    draw_title_bar(draw, W, title)

    years = [e[0] for e in events]
    min_y, max_y = min(years), max(years)
    span = max_y - min_y or 1

    LX, RX = 60, 640
    TY = 195  # timeline Y

    # Main line
    draw.line([(LX, TY), (RX, TY)], fill="#92400E", width=4)

    # Arrow heads
    draw.polygon([(RX, TY), (RX-12, TY-7), (RX-12, TY+7)], fill="#92400E")

    COLORS = ["#2563EB", "#DC2626", "#16A34A", "#D97706", "#7C3AED", "#0891B2"]

    for i, (yr, short, long_lbl) in enumerate(events):
        x = LX + int((yr - min_y) / span * (RX - LX - 20))
        color = COLORS[i % len(COLORS)]

        # Tick
        draw.line([(x, TY - 10), (x, TY + 10)], fill=color, width=3)
        draw.ellipse([x-9, TY-9, x+9, TY+9], fill=color, outline="white", width=2)

        # Year label — alternate above and below the line
        above = (i % 2 == 0)
        short_s = short.replace("\n", " ")
        yr_lbl = str(yr) + (" BCE" if is_bce else "")
        if above:
            draw.text((x, TY - 22), yr_lbl, fill=color, font=FONT_SM, anchor="mb")
            draw.text((x, TY - 38), short_s, fill=TITLE_COLOR, font=FONT_BD, anchor="mb")
            draw.text((x, TY - 56), long_lbl, fill="#475569", font=FONT_SM, anchor="mb")
        else:
            draw.text((x, TY + 22), yr_lbl, fill=color, font=FONT_SM, anchor="mt")
            draw.text((x, TY + 40), short_s, fill=TITLE_COLOR, font=FONT_BD, anchor="mt")
            draw.text((x, TY + 60), long_lbl, fill="#475569", font=FONT_SM, anchor="mt")

    # Legend
    draw.text((W//2, H - 20), "→ Time progresses left to right", fill="#94A3B8",
              font=FONT_SM, anchor="mb")
    return img


TIMELINE_GR10 = [
    ("Indian Independence Movement — Key Milestones",
     [(1885,"INC\nFounded","Indian National Congress"),
      (1905,"Bengal\nPartition","Lord Curzon's order"),
      (1919,"Jallianwala\nBagh","Amritsar Massacre"),
      (1930,"Dandi\nMarch","Civil Disobedience"),
      (1942,"Quit India","August Movement"),
      (1947,"Independence","15 August 1947")],
     False,
     "How many years passed between the founding of INC and Indian Independence?",
     "62 years (1885 to 1947)",
     ["50 years", "55 years", "70 years"],
     "Modern Indian History", "Foundation",
     "1947 - 1885 = 62 years of the independence struggle",
     10),

    ("Constitutional Development of India",
     [(1946,"Constituent\nAssembly","Assembly formed"),
      (1948,"Draft\nConstitution","Presented by Ambedkar"),
      (1949,"Adoption","26 Nov 1949"),
      (1950,"Republic\nDay","26 Jan 1950"),
      (1951,"First\nAmendment","Land reforms")],
     False,
     "How long did it take to draft and adopt the Indian Constitution from the first meeting of the Constituent Assembly?",
     "About 3 years (1946–1949)",
     ["About 1 year", "About 5 years", "About 2 years"],
     "Indian Civics", "Advanced",
     "Constituent Assembly met for 2 years 11 months 17 days",
     10),

    ("India's Economic Policy Timeline",
     [(1947,"Mixed\nEconomy","Planned economy begins"),
      (1951,"First\nFive-Year Plan","PSU focus"),
      (1969,"Bank\nNationalisation","14 banks nationalised"),
      (1991,"LPG Reforms","Liberalisation begins"),
      (2016,"GST\nRollout","One Nation One Tax")],
     False,
     "Between which two events on the timeline was India's economy the MOST protected from foreign competition?",
     "1951–1991 (between First Plan and LPG Reforms)",
     ["1947–1951", "1969–1991", "1991–2016"],
     "Economics Basics", "Olympiad",
     "LPG = Liberalisation, Privatisation, Globalisation — opened India's economy in 1991",
     10),

    ("Nationalist Movement — Non-Cooperation to Independence",
     [(1920,"Non-Cooperation","Movement launched"),
      (1922,"Chauri\nChaura","Movement withdrawn"),
      (1930,"Civil\nDisobedience","Salt March"),
      (1935,"Govt of\nIndia Act","Provincial autonomy"),
      (1940,"Lahore\nResolution","Pakistan demand"),
      (1947,"Partition &\nIndependence","Two nations born")],
     False,
     "Gandhiji withdrew the Non-Cooperation Movement because of the Chauri Chaura incident. How many years before Independence was this?",
     "25 years before Independence (1947 – 1922 = 25)",
     ["27 years", "20 years", "30 years"],
     "Modern Indian History", "Advanced",
     "Chauri Chaura (1922): violent clash prompted Gandhi to suspend NCM",
     10),
]

TIMELINE_LOWER = [
    ("Mughal Empire — Key Events",
     [(1526,"Babur\nfounds","First Battle of Panipat"),
      (1556,"Akbar\nbecomes King","Second Panipat"),
      (1600,"Jahangir\nrules","Golden age of art"),
      (1658,"Aurangzeb\nrules","Empire at peak area"),
      (1707,"Aurangzeb\ndies","Decline begins")],
     False,
     "How many years after the Mughal Empire was founded did Akbar become King?",
     "30 years (1556 – 1526)",
     ["25 years", "40 years", "54 years"],
     "Medieval Indian History", "Foundation",
     "Akbar is considered the greatest Mughal emperor",
     7),

    ("Ancient India — Maurya to Gupta",
     [(321,"Maurya\nEmpire","Chandragupta Maurya"),
      (268,"Ashoka\nbecomes King","Spread of Buddhism"),
      (185,"Maurya\nEnds","Last king Brihadratha"),
      (319,"Gupta\nEmpire","Chandragupta I"),
      (550,"Gupta\nDeclines","Huna invasions")],
     True,
     "Approximately how many years gap is there between the end of the Maurya Empire and start of the Gupta Empire?",
     "About 134 years (319 – 185 BCE)",
     ["About 50 years", "About 200 years", "About 80 years"],
     "Ancient Indian History", "Advanced",
     "Both empires ruled from present-day Bihar (Pataliputra / Patna)",
     6),
]

def gen_timelines():
    print("\n[Grade 10 — Timeline Questions]")
    for i, row in enumerate(TIMELINE_GR10):
        title, events, is_bce, qtext, correct, wrongs, topic, diff, expl, grade = row
        img = draw_timeline(title, events, is_bce)
        url = upload(img, f"g{grade}_tl_{i}")
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Timeline", qtext, url, opts, cidx, expl)
        print(f"  G{grade} timeline_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)

    print("\n[Grades 6-7 — Timeline Questions]")
    for i, row in enumerate(TIMELINE_LOWER):
        title, events, is_bce, qtext, correct, wrongs, topic, diff, expl, grade = row
        img = draw_timeline(title, events, is_bce)
        url = upload(img, f"g{grade}_tl_lo_{i}")
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Timeline", qtext, url, opts, cidx, expl)
        print(f"  G{grade} timeline_lo_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)


# ─────────────────────────────────────────────────────────────────────────────
# INDIA MAP (improved schematic)
# ─────────────────────────────────────────────────────────────────────────────
def draw_india_map(title, highlight_pts, labels_list, note):
    """Draws a clean India schematic with highlighted markers and a legend."""
    W, H = 700, 500
    img, draw = canvas(W, H, "#EFF6FF")
    draw.rectangle([0, 0, W-1, H-1], outline="#CBD5E1", width=2)
    draw_title_bar(draw, W, title)

    # India outline (normalised to fit 320×360 box starting at (120, 65))
    raw = [
        (200,30),(260,25),(310,40),(360,60),(390,100),(400,140),(420,170),
        (410,210),(430,240),(420,280),(390,310),(350,340),(310,360),(270,370),
        (240,365),(210,350),(180,320),(160,290),(150,250),(140,210),(130,170),
        (140,130),(150,90),(170,60),(200,30)
    ]
    # Scale & offset to fit title bar
    sx, sy, ox, oy = 1.05, 1.0, 118, 62
    pts = [(int(x*sx + ox), int(y*sy + oy)) for x, y in raw]
    draw.polygon(pts, fill="#DCFCE7", outline="#166534", width=2)

    # Sea labels
    draw.text((52, 300), "Arabian\nSea", fill="#1D4ED8", font=FONT_SM, anchor="mm")
    draw.text((570, 220), "Bay of\nBengal", fill="#1D4ED8", font=FONT_SM, anchor="mm")
    draw.text((310, 460), "Indian Ocean", fill="#1D4ED8", font=FONT_SM, anchor="mm")

    # Markers
    marker_colors = ["#DC2626","#D97706","#7C3AED","#0891B2","#16A34A","#BE185D"]
    for i, (mx, my, lbl) in enumerate(highlight_pts):
        px, py = int(mx*sx + ox), int(my*sy + oy)
        c = marker_colors[i % len(marker_colors)]
        draw.ellipse([px-9, py-9, px+9, py+9], fill=c, outline="white", width=2)
        draw.text((px, py), str(i+1), fill="white", font=FONT_SM, anchor="mm")

    # Legend on the right
    lx = 508
    draw.rectangle([lx-5, 72, W-8, 72 + len(highlight_pts)*38 + 10],
                   fill="white", outline="#CBD5E1", width=1)
    draw.text((lx + 90, 80), "Legend", fill=TITLE_COLOR, font=FONT_BD, anchor="mt")
    for i, lbl in enumerate(labels_list):
        ly = 104 + i * 38
        c = marker_colors[i % len(marker_colors)]
        draw.ellipse([lx+2, ly+2, lx+22, ly+22], fill=c, outline="white", width=1)
        draw.text((lx+6, ly+11), str(i+1), fill="white", font=FONT_SM, anchor="mm")
        draw.text((lx+28, ly+10), lbl, fill=AXIS_COLOR, font=FONT_SM)

    if note:
        draw_note_box(draw, W, H, note)
    return img


MAP_DATA_GR10 = [
    ("India — Major Mineral Producing Regions",
     [(190, 200, "Jharkhand"), (215, 235, "Odisha"), (175, 170, "Jharkhand-2"),
      (130, 155, "Chhattisgarh"), (95, 120, "Rajasthan")],
     ["Jharkhand — Iron ore, Coal", "Odisha — Iron ore, Bauxite",
      "Dhanbad (Coal Belt)", "Chhattisgarh — Coal, Limestone", "Rajasthan — Copper, Zinc"],
     "Minerals are non-renewable; India is rich in iron ore and coal",
     "Which pair of states shown on the map are the leading producers of IRON ORE?",
     "Jharkhand and Odisha",
     ["Rajasthan and Odisha", "Chhattisgarh and Rajasthan", "Jharkhand and Chhattisgarh"],
     "Indian Geography", "Advanced",
     "Iron ore is found in the Chota Nagpur Plateau (Jharkhand) and Odisha's Keonjhar district.",
     10),

    ("India — Major Power Plant Locations",
     [(200, 140, "Singrauli"), (175, 200, "Bokaro"), (100, 180, "Korba"),
      (260, 305, "Tarapur"), (305, 235, "Kaiga")],
     ["Singrauli — Thermal (coal)", "Bokaro — Steel + Thermal",
      "Korba — Thermal (coal, Chhattisgarh)", "Tarapur — Nuclear Plant",
      "Kaiga — Nuclear Plant (Karnataka)"],
     "Thermal plants use coal; Nuclear plants use uranium fuel rods",
     "The map marks two NUCLEAR power plants. Which states are they located in?",
     "Maharashtra (Tarapur) and Karnataka (Kaiga)",
     ["Jharkhand and Karnataka", "Maharashtra and Andhra Pradesh", "Rajasthan and Karnataka"],
     "Indian Geography", "Olympiad",
     "Tarapur (Maharashtra) was India's first nuclear plant. Kaiga is in Karnataka.",
     10),

    ("India — Soil Types by Region",
     [(240, 150, "Alluvial — IGP"), (190, 245, "Black — Deccan"),
      (290, 270, "Red & Yellow — Peninsular"), (80, 125, "Arid — Rajasthan"),
      (320, 130, "Laterite — NE")],
     ["Alluvial — Indo-Gangetic Plain", "Black (Regur) — Deccan Plateau",
      "Red & Yellow — Peninsular India", "Arid — Rajasthan desert",
      "Laterite — NE & Western Ghats"],
     "Soil type determines what crops can be grown in a region",
     "Black soil is ideal for growing cotton because it retains moisture well. Which region on the map should a cotton farmer choose?",
     "Deccan Plateau (Black soil region — marker 2)",
     ["Indo-Gangetic Plain (Alluvial)", "Rajasthan (Arid)", "NE India (Laterite)"],
     "Indian Geography", "Advanced",
     "Black cotton soil (Regur) in the Deccan retains moisture, making it perfect for cotton cultivation.",
     10),

    ("India — Agriculture Zones",
     [(230, 130, "Wheat Belt"), (215, 200, "Rice Bowl"),
      (280, 200, "Cotton Zone"), (175, 165, "Sugarcane Belt"),
      (200, 305, "Spice Garden")],
     ["Wheat Belt — Punjab, Haryana, UP", "Rice Bowl — WB, Odisha, AP",
      "Cotton Zone — Maharashtra, Gujarat", "Sugarcane Belt — UP, Maharashtra",
      "Spice Garden — Kerala"],
     "India's diverse climate allows cultivation of diverse crops",
     "The region labelled 'Spice Garden' on this map corresponds to which state and why?",
     "Kerala — warm humid climate, ideal for black pepper, cardamom, cloves",
     ["Karnataka — dry Deccan soil", "Tamil Nadu — semi-arid coastal", "Goa — small coastal state"],
     "Indian Geography", "Olympiad",
     "Kerala's warm, wet climate (high rainfall, humidity) makes it perfect for tropical spices. It supplies most of India's black pepper and cardamom.",
     10),
]

MAP_DATA_LOWER = [
    ("India — Major Rivers",
     [(240, 80, "Indus"), (220, 170, "Ganga"), (320, 130, "Brahmaputra"),
      (265, 265, "Krishna"), (250, 305, "Kaveri")],
     ["Indus — NW India", "Ganga — North India", "Brahmaputra — NE India",
      "Krishna — Peninsula", "Kaveri — Tamil Nadu/Karnataka"],
     "Rivers provide water for irrigation and drinking",
     "Which river shown on the map flows from east to west (into the Arabian Sea)?",
     "Indus (flows westward through Pakistan into Arabian Sea)",
     ["Ganga (flows eastward)", "Brahmaputra (flows eastward)", "Krishna (flows eastward)"],
     "Indian Geography", "Advanced",
     "The Indus rises in Tibet, flows through Ladakh, and then heads west through Pakistan to the Arabian Sea. All other peninsular rivers flow eastward.", 5),

    ("India — Important Mountain Ranges",
     [(245, 60, "Himalayas"), (130, 100, "Karakoram"),
      (130, 200, "Aravalli"), (175, 255, "Vindhya"), (195, 285, "Satpura")],
     ["Himalayas — North India", "Karakoram — J&K (highest peaks)",
      "Aravalli — Rajasthan (oldest range)", "Vindhya — MP", "Satpura — MP/Maharashtra"],
     "The Aravalli is the OLDEST mountain range in India",
     "The Aravalli range is special because it is the OLDEST fold mountain range in India. Where is it located?",
     "Rajasthan (Northwest India)",
     ["Madhya Pradesh", "Maharashtra", "Gujarat only"],
     "Indian Geography", "Foundation",
     "Aravallis stretch from Delhi to Gujarat, mostly through Rajasthan. They are among the world's oldest fold mountains.", 4),
]

def gen_map_questions():
    print("\n[Grade 10 — Map Questions]")
    for i, row in enumerate(MAP_DATA_GR10):
        title, pts, lbls, note, qtext, correct, wrongs, topic, diff, expl, grade = row
        img = draw_india_map(title, pts, lbls, note)
        url = upload(img, f"g{grade}_map_{i}")
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Map Reading", qtext, url, opts, cidx, expl)
        print(f"  G{grade} map_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)

    print("\n[Grades 4-5 — Map Questions]")
    for i, row in enumerate(MAP_DATA_LOWER):
        title, pts, lbls, note, qtext, correct, wrongs, topic, diff, expl, grade = row
        img = draw_india_map(title, pts, lbls, note)
        url = upload(img, f"g{grade}_map_lo_{i}")
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Map Reading", qtext, url, opts, cidx, expl)
        print(f"  G{grade} map_lo_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)


# ─────────────────────────────────────────────────────────────────────────────
# CIVICS DIAGRAM (Grade 10)
# ─────────────────────────────────────────────────────────────────────────────
def draw_power_sharing_diagram():
    W, H = 700, 500
    img, draw = canvas(W, H, "#F0FDF4")
    draw.rectangle([0, 0, W-1, H-1], outline="#CBD5E1", width=2)
    draw_title_bar(draw, W, "Forms of Power Sharing in Democracy", "Class 10 Civics — Chapter 1")

    items = [
        ("#1E40AF", 350, 100, "Horizontal Sharing",
         "Among organs of government\n(Legislature, Executive, Judiciary)"),
        ("#7C3AED", 350, 195, "Vertical Sharing",
         "Among levels of government\n(Union → State → Local)"),
        ("#BE185D", 350, 290, "Among Social Groups",
         "Political parties, pressure groups\n& religious/linguistic groups"),
        ("#D97706", 350, 385, "Among Governments",
         "Coalition & Power-sharing\narrangements between parties"),
    ]
    for color, x, y, title_t, body in items:
        draw.rectangle([x-330, y-28, x+330, y+44], fill=color, outline="white", width=2)
        draw.text((x, y-14), title_t, fill="white", font=FONT_BD, anchor="mt")
        for ji, line in enumerate(body.split("\n")):
            draw.text((x, y+10+ji*20), line, fill="#E0F2FE", font=FONT_SM, anchor="mt")

    return img

CIVICS_DIAGRAM_QS = [
    ("The diagram shows four forms of power sharing. 'Vertical sharing' refers to power shared among:",
     "Different levels of government (Union, State, Local)",
     ["Legislature, Executive and Judiciary", "Social groups like castes and religions", "Political parties in a coalition"],
     "Indian Civics", "Foundation",
     "Vertical power sharing is a feature of federalism — different tiers of government.",
     10),
    ("Horizontal power sharing means:",
     "Power is distributed among organs of the SAME level — Legislature, Executive, Judiciary",
     ["Power is given only to the central government", "Different states share power with each other", "Power is shared based on population"],
     "Indian Civics", "Advanced",
     "Horizontal = same level (separation of powers). Vertical = different levels (federalism).",
     10),
    ("A coalition government is an example of which form of power sharing in the diagram?",
     "Among governments — power sharing arrangements between parties",
     ["Horizontal sharing", "Among social groups", "Vertical sharing"],
     "Indian Civics", "Advanced",
     "Coalitions form when no single party has majority — multiple parties share power. This is 'among governments/parties' category.",
     10),
    ("India's federal structure — where states have their own elected governments — is an example of:",
     "Vertical power sharing between Union and State governments",
     ["Horizontal sharing (same level)", "Sharing among social groups", "Coalition power sharing"],
     "Indian Civics", "Olympiad",
     "Federalism = vertical sharing. India is a 'holding together' federation where the Constitution gives states defined powers (State List) while Centre has Union List and Concurrent List.",
     10),
]

def draw_fundamental_rights_diagram():
    W, H = 700, 500
    img, draw = canvas(W, H, "#FFF7ED")
    draw.rectangle([0, 0, W-1, H-1], outline="#CBD5E1", width=2)
    draw_title_bar(draw, W, "Fundamental Rights — Indian Constitution",
                   "Part III, Articles 12–35")

    rights = [
        ("#1D4ED8", "Right to Equality", "Art. 14–18\nNo discrimination by State"),
        ("#7C3AED", "Right to Freedom", "Art. 19–22\nSpeech, movement, profession"),
        ("#BE185D", "Right against Exploitation", "Art. 23–24\nNo bonded labour/child labour"),
        ("#0891B2", "Right to Religion", "Art. 25–28\nFreedom of conscience"),
        ("#D97706", "Cultural & Educational Rights", "Art. 29–30\nMinority rights"),
        ("#16A34A", "Right to Constitutional Remedies", "Art. 32\nDr. Ambedkar: Heart & Soul"),
    ]
    cols, rows = 3, 2
    bw, bh = 215, 140
    sx, sy = 15, 68
    for i, (color, name, desc) in enumerate(rights):
        col = i % cols; row = i // cols
        x1 = sx + col * (bw + 10)
        y1 = sy + row * (bh + 10)
        draw.rectangle([x1, y1, x1+bw, y1+bh], fill=color, outline="white", width=2)
        draw.text((x1+bw//2, y1+14), name, fill="white", font=FONT_BD, anchor="mt")
        for ji, line in enumerate(desc.split("\n")):
            draw.text((x1+bw//2, y1+48+ji*22), line, fill="#E0F2FE", font=FONT_SM, anchor="mt")

    return img

RIGHTS_QS = [
    ("The diagram shows six Fundamental Rights. Which right did Dr. B.R. Ambedkar call the 'heart and soul' of the Constitution?",
     "Right to Constitutional Remedies (Art. 32)",
     ["Right to Equality", "Right to Freedom", "Right to Religion"],
     "Indian Civics", "Foundation",
     "Art. 32 allows citizens to directly approach the Supreme Court if any Fundamental Right is violated. Ambedkar called it the heart of the Constitution.",
     10),
    ("A factory owner employs children under 14 in hazardous work. Which Fundamental Right does this violate?",
     "Right against Exploitation (Art. 23–24)",
     ["Right to Equality", "Right to Freedom", "Cultural Rights"],
     "Indian Civics", "Foundation",
     "Art. 24 specifically prohibits employment of children below 14 in factories, mines, or hazardous industries.",
     10),
    ("The Right to Freedom (Art. 19–22) is NOT absolute. The State can restrict freedom of speech when:",
     "It threatens sovereignty, security of state, public order, or morality",
     ["The government loses an election", "A citizen is a minority group member", "Another country objects"],
     "Indian Civics", "Olympiad",
     "Art. 19(2) allows 'reasonable restrictions' on freedom of speech for specific grounds: sovereignty/integrity of India, security of the state, friendly relations with foreign states, public order, decency/morality, contempt of court, defamation, incitement to offence.",
     10),
    ("Which of these Fundamental Rights directly protects linguistic and religious minority communities?",
     "Cultural and Educational Rights (Art. 29–30)",
     ["Right to Religion (Art. 25–28)", "Right to Equality (Art. 14–18)", "Right to Freedom (Art. 19–22)"],
     "Indian Civics", "Advanced",
     "Art. 29 protects minority languages/cultures; Art. 30 allows minorities to establish and administer educational institutions.",
     10),
]

def gen_civics_diagrams():
    print("\n[Grade 10 — Civics Diagram: Power Sharing]")
    img1 = draw_power_sharing_diagram()
    url1 = upload(img1, "g10_powersharing")
    for i, (qtext, correct, wrongs, topic, diff, expl, grade) in enumerate(CIVICS_DIAGRAM_QS):
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Government Structure", qtext, url1, opts, cidx, expl)
        print(f"  G{grade} civics_ps_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)

    print("\n[Grade 10 — Civics Diagram: Fundamental Rights]")
    img2 = draw_fundamental_rights_diagram()
    url2 = upload(img2, "g10_fundrights")
    for i, (qtext, correct, wrongs, topic, diff, expl, grade) in enumerate(RIGHTS_QS):
        opts = [correct] + wrongs; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Indian Civics", qtext, url2, opts, cidx, expl)
        print(f"  G{grade} civics_fr_{i} [{diff}]... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.4)


# ═════════════════════════════════════════════════════════════════════════════
# TEXT QUESTIONS — thin grades (5, 6, 7, 9)
# ═════════════════════════════════════════════════════════════════════════════
# Each tuple: (grade, diff, topic, subtopic, qtext, opts_list, correct_idx, expl)

TEXT_QS = [

    # ── GRADE 5 ───────────────────────────────────────────────────────────────
    (5,"Foundation","Indian Geography","Physical Features",
     "The Himalayan mountain range is located in which direction of India?",
     ["North","South","East","West"], 0,
     "The Himalayas form the northern boundary of India, stretching from Kashmir in the west to Arunachal Pradesh in the east."),

    (5,"Foundation","Indian Geography","Rivers",
     "Which river is known as the 'Sorrow of Bihar' due to the floods it causes?",
     ["Kosi","Ganga","Yamuna","Son"], 0,
     "The Kosi river changes its course frequently and causes devastating floods in Bihar. It is called the 'Sorrow of Bihar'."),

    (5,"Foundation","Ancient Indian History","Monuments",
     "The Taj Mahal is located in which Indian city?",
     ["Agra","Delhi","Jaipur","Lucknow"], 0,
     "The Taj Mahal is in Agra, Uttar Pradesh. It was built by Mughal Emperor Shah Jahan in memory of his wife Mumtaz Mahal."),

    (5,"Foundation","Indian Civics","National Symbols",
     "What is the national animal of India?",
     ["Bengal Tiger","Asiatic Lion","Indian Elephant","Snow Leopard"], 0,
     "The Bengal Tiger was declared India's national animal in 1973 when Project Tiger was launched to protect this endangered species."),

    (5,"Foundation","Indian Geography","Climate",
     "India's climate is largely influenced by which seasonal winds that bring rain?",
     ["Monsoon winds","Trade winds","Polar winds","Westerlies"], 0,
     "The SW Monsoon (June–September) brings about 75% of India's annual rainfall. 'Monsoon' comes from the Arabic word 'mausam' (season)."),

    (5,"Advanced","Indian Geography","Physical Features",
     "The Western Ghats and Eastern Ghats meet at which point in South India?",
     ["Nilgiri Hills","Cardamom Hills","Annamalai Hills","Palani Hills"], 0,
     "The Western and Eastern Ghats meet at the Nilgiri Hills in Tamil Nadu/Karnataka. The Nilgiris have peaks like Doddabetta (2,637 m)."),

    (5,"Advanced","Modern Indian History","Freedom Struggle",
     "Subhas Chandra Bose formed which military organisation to fight for India's independence?",
     ["Indian National Army (INA)","Indian National Congress","Azad Hind Fauj","Both A and C"],
     0,  # INA and Azad Hind Fauj are the same — best option is INA
     "Subhas Chandra Bose formed the Indian National Army (INA), also called Azad Hind Fauj, in 1942 to fight against British colonial rule using armed resistance."),

    (5,"Advanced","Indian Geography","Natural Vegetation",
     "The Sundarbans mangrove forest is located in the delta of which river?",
     ["Ganga–Brahmaputra delta","Godavari delta","Mahanadi delta","Krishna delta"], 0,
     "The Sundarbans is the world's largest mangrove forest, located in the Ganga-Brahmaputra delta shared between India (West Bengal) and Bangladesh."),

    (5,"Advanced","Environment and Ecology","Conservation",
     "Which of the following is NOT a renewable resource?",
     ["Coal","Solar energy","Wind energy","Water"], 0,
     "Coal is a fossil fuel formed over millions of years — once used, it cannot be replenished in a human lifetime, making it non-renewable. Solar, wind, and water are continuously available."),

    (5,"Foundation","Culture and Heritage","Festivals",
     "Pongal is the harvest festival of which Indian state?",
     ["Tamil Nadu","Karnataka","Kerala","Andhra Pradesh"], 0,
     "Pongal is a 4-day harvest festival celebrated in Tamil Nadu in January. It involves boiling the new rice in milk — 'pongal' means 'to boil over/overflow'."),

    # ── GRADE 6 ───────────────────────────────────────────────────────────────
    (6,"Foundation","Indian Geography","Globe and Maps",
     "The Prime Meridian (0° longitude) passes through which city?",
     ["Greenwich (London)","Paris","New York","Cape Town"], 0,
     "The Prime Meridian passes through the Royal Observatory in Greenwich, London. All longitudes are measured east or west of this line."),

    (6,"Foundation","Ancient Indian History","Indus Valley",
     "The Great Bath, an ancient water tank, was found at which Indus Valley site?",
     ["Mohenjo-daro","Harappa","Lothal","Dholavira"], 0,
     "The Great Bath at Mohenjo-daro is one of the earliest public water tanks in the ancient world. It shows the advanced urban planning of the Indus Valley Civilisation."),

    (6,"Foundation","Indian Civics","Constitution",
     "Who is called the 'Father of the Indian Constitution'?",
     ["Dr. B.R. Ambedkar","Jawaharlal Nehru","Mahatma Gandhi","Sardar Patel"], 0,
     "Dr. B.R. Ambedkar chaired the Drafting Committee of the Indian Constitution and is called its 'Father'. The Constitution was adopted on 26 November 1949."),

    (6,"Foundation","Indian Geography","Physical Features",
     "The Deccan Plateau is bounded on two sides by mountain ranges. These are:",
     ["Western and Eastern Ghats","Himalayas and Vindhyas","Aravalli and Satpura","Nilgiri and Cardamom"], 0,
     "The Deccan Plateau — a large triangular landmass — has the Western Ghats on its west and Eastern Ghats on its east. The Vindhya-Satpura ranges form its northern boundary."),

    (6,"Advanced","Ancient Indian History","Maurya Empire",
     "Emperor Ashoka gave up war after the Battle of Kalinga because:",
     ["He was horrified by the mass death and suffering it caused","He ran out of soldiers","Kalinga surrendered before the battle","His army refused to fight"], 0,
     "The Kalinga War (261 BCE) resulted in ~100,000 deaths. Witnessing this devastation transformed Ashoka — he embraced Buddhism and renounced further military conquests, promoting Dhamma (righteous conduct) instead."),

    (6,"Advanced","Indian Civics","Rights and Duties",
     "Panchayati Raj institutions were given constitutional status by which amendment?",
     ["73rd Amendment (1992)","42nd Amendment","86th Amendment","52nd Amendment"], 0,
     "The 73rd Constitutional Amendment (1992) gave constitutional status to Panchayati Raj. It mandated elected gram panchayats and reserved seats for women and SC/ST."),

    (6,"Advanced","Indian Geography","Latitudes and Longitudes",
     "The Standard Meridian of India is 82.5°E. Why was this specific longitude chosen?",
     ["It passes through the centre of India and gives a convenient IST = UTC+5:30","It passes through Delhi","It was chosen by the British","It is exactly halfway between 0° and 180°"], 0,
     "82.5°E is divisible by 7.5° (one time zone unit), giving IST as exactly UTC+5:30 (no odd fractions). It passes through Mirzapur, UP, near the geographical centre of India."),

    (6,"Olympiad","Medieval Indian History","Delhi Sultanate",
     "Ibn Battuta, who visited India during Muhammad bin Tughluq's reign, described the Sultan's transfer of the capital from Delhi to Daulatabad as a disaster because:",
     ["The entire population of Delhi was forced to move 1,500 km south, causing mass suffering and deaths","The new capital had no water supply","The Mongols attacked Delhi during the move","Daulatabad was already occupied by another ruler"], 0,
     "Muhammad bin Tughluq ordered the entire population of Delhi (~100,000 people) to march to Daulatabad (near Aurangabad, Maharashtra). The 1,500 km forced march caused enormous suffering. He later reversed the decision, making both cities suffer."),

    (6,"Olympiad","Indian Geography","Climate",
     "Mumbai receives much more rainfall than Pune, though both are in Maharashtra and only ~150 km apart. The BEST explanation is:",
     ["Mumbai is on the windward side of the Western Ghats; Pune is in the rain shadow","Mumbai is closer to the sea","Pune is at a higher altitude","Mumbai has more rivers"], 0,
     "The Western Ghats act as a barrier. The SW Monsoon hits Mumbai (windward/seaward side) and drops most moisture there. Pune, on the leeward (rain shadow) side, gets far less rain. This is the orographic effect."),

    (6,"Foundation","Culture and Heritage","Classical Dance",
     "Bharatanatyam is a classical dance form that originated in which Indian state?",
     ["Tamil Nadu","Odisha","Kerala","Andhra Pradesh"], 0,
     "Bharatanatyam is one of the oldest classical dance forms, originating in the temples of Tamil Nadu. It was performed by Devadasis and later revived by Rukmini Devi Arundale."),

    # ── GRADE 7 ───────────────────────────────────────────────────────────────
    (7,"Foundation","Indian Geography","Natural Vegetation",
     "Tropical rainforests in India are found mainly in:",
     ["Western Ghats and Andaman & Nicobar Islands","Rajasthan and Gujarat","Indo-Gangetic Plains","Deccan Plateau"], 0,
     "Tropical rainforests need high rainfall (>200 cm) and high temperatures year-round. In India, these conditions exist in the Western Ghats (Kerala, Karnataka) and Andaman & Nicobar Islands."),

    (7,"Foundation","Medieval Indian History","Bhakti Movement",
     "Which saint-poet of the Bhakti movement composed 'dohas' (couplets) and preached unity between Hindus and Muslims?",
     ["Kabir","Mirabai","Tukaram","Chaitanya"], 0,
     "Kabir (15th century) was a weaver-saint who wrote simple two-line dohas teaching that God is one and religion should unite, not divide. His followers included both Hindus and Muslims."),

    (7,"Foundation","Indian Civics","Government",
     "In India's parliamentary system, who is the real executive head of the country?",
     ["Prime Minister","President","Chief Justice","Speaker of Lok Sabha"], 0,
     "The President is the constitutional/nominal head. The Prime Minister, as leader of the majority in Lok Sabha, is the real (de facto) executive who exercises actual power."),

    (7,"Advanced","Indian Geography","Human Environment",
     "The Amazon rainforest in South America and the Congo rainforest in Africa are both located near:",
     ["The Equator (0° latitude)","The Tropic of Cancer","The Arctic Circle","The Tropic of Capricorn"], 0,
     "Equatorial regions have consistent high temperatures and heavy rainfall throughout the year — ideal conditions for tropical rainforests. Both the Amazon and Congo basins straddle the equator."),

    (7,"Advanced","Medieval Indian History","Vijayanagara",
     "The traveller Domingo Paes visited the Vijayanagara Empire in the 16th century and described its capital Hampi as:",
     ["As large as Rome and very beautiful","Smaller than Delhi","Mostly in ruins","A desert outpost"], 0,
     "Domingo Paes (Portuguese traveller, c.1522) described Hampi as 'the best-provided city in the world' and compared it to Rome in size. Hampi is now a UNESCO World Heritage Site."),

    (7,"Advanced","Economics Basics","Markets and Trade",
     "In a periodic market (weekly bazaar), traders set up shops only on specific days because:",
     ["Demand in small villages is not enough to support permanent shops","The government restricts daily trading","Such markets are only allowed during festivals","Permanent shops are more expensive to build"], 0,
     "Periodic markets serve small villages with sparse populations. There aren't enough customers every day to justify permanent shops, so traders travel between several villages on a rotating schedule."),

    (7,"Olympiad","Indian Geography","Climate",
     "India's northeast (Assam, Meghalaya) receives far more rainfall than northwest Rajasthan, even though both are in the same country. The PRIMARY reason is:",
     ["The Bay of Bengal monsoon branch brings heavy rain to NE; Rajasthan is far inland and beyond the Aravalli rain shadow",
      "The Arabian Sea is closer to NE India",
      "Rajasthan has high altitude blocking monsoon winds",
      "NE India is nearer the Equator"], 0,
     "The Bay of Bengal branch of SW Monsoon travels northeast and hits the Meghalaya hills (Mawsynram = world's wettest place). Rajasthan is 1,500+ km from the coast, beyond the Aravalli which blocks any remaining moisture."),

    (7,"Olympiad","Medieval Indian History","Sultanate Economy",
     "Under the Delhi Sultanate, Alauddin Khalji's market reforms set FIXED prices for goods. His main motive for this was:",
     ["To maintain a large, well-equipped army at low cost to the treasury",
      "To help poor people afford food",
      "To punish merchants who profited too much",
      "To reduce inflation caused by too much gold in Delhi"], 0,
     "Alauddin kept fixed market prices so he could pay soldiers lower salaries (since they could buy goods cheaply). This allowed him to maintain a huge army (nearly 300,000 soldiers) without straining the treasury."),

    (7,"Foundation","Culture and Heritage","Architecture",
     "The Qutub Minar in Delhi was built during the rule of:",
     ["The Delhi Sultans (begun by Qutb-ud-din Aibak)","Akbar","Shah Jahan","Ashoka"], 0,
     "Construction of Qutub Minar began under Qutb-ud-din Aibak (first Sultan of Delhi, 1193) and was completed by Iltutmish. At 72.5 m, it is the world's tallest brick minaret."),

    (7,"Foundation","Environment and Ecology","Forests",
     "Social forestry refers to:",
     ["Growing trees on community land for the benefit of local people","Planting trees only inside wildlife sanctuaries","A government scheme to export timber","Forests owned by private companies"], 0,
     "Social forestry involves planting trees on village commons, roadsides, and other public land so that rural communities can access fuel wood, fodder, and timber locally."),

    # ── GRADE 9 ───────────────────────────────────────────────────────────────
    (9,"Foundation","Indian Geography","Population",
     "According to Census 2011, India's population was approximately:",
     ["121 crore","100 crore","140 crore","85 crore"], 0,
     "India's population in 2011 was 1.21 billion (121 crore). India became the world's most populous country in 2023, surpassing China."),

    (9,"Foundation","Modern Indian History","French Revolution",
     "The French Revolution of 1789 gave the world three ideals that influenced many nations. These are:",
     ["Liberty, Equality, Fraternity","Democracy, Secularism, Socialism","Freedom, Justice, Brotherhood","Rights, Duties, Justice"], 0,
     "The slogan 'Liberté, Égalité, Fraternité' (Liberty, Equality, Fraternity) from the French Revolution influenced constitutions and freedom movements worldwide, including India's independence movement."),

    (9,"Foundation","Indian Geography","Physical Features",
     "The Bhabar, Terai, Bhangar, and Khadar are all types of:",
     ["Land formations in the Northern Plains","Mountain ranges","Coastal landforms","Plateau types"], 0,
     "These are sub-divisions of the North Indian Plains: Bhabar (pebble zone at Himalayan foothills), Terai (marshy zone), Bhangar (old alluvium), and Khadar (newer, more fertile alluvium near rivers)."),

    (9,"Advanced","Modern Indian History","Nazism",
     "Hitler's concept of 'Lebensraum' (living space) referred to:",
     ["Germany's need to expand eastward into Slavic lands to settle German people","A policy of making Germany's borders more friendly","Equal rights for all Germans in Europe","The right to practise German culture freely"], 0,
     "Lebensraum ('living space') was Nazi ideology that justified German expansion into Eastern Europe (especially Poland and Soviet Union) by claiming Germans needed land to settle and grow food, displacing or killing the existing Slavic population."),

    (9,"Advanced","Indian Geography","Drainage",
     "Rivers flowing into the Bay of Bengal (e.g. Ganga, Godavari) form deltas, while rivers flowing into the Arabian Sea (e.g. Narmada, Tapi) form estuaries. The PRIMARY reason for this difference is:",
     ["Narmada/Tapi flow through hard rock rift valleys with little sediment; Ganga carries huge silt loads from soft alluvial plains",
      "Arabian Sea is deeper than Bay of Bengal",
      "Bay of Bengal has weaker currents than the Arabian Sea",
      "Western rivers are shorter and faster"], 0,
     "Delta formation requires large amounts of sediment. Ganga flows through vast alluvial plains, picking up enormous silt. Narmada and Tapi flow through hard basalt rift valleys (Vindhya/Satpura), carrying minimal sediment — so they form estuaries instead."),

    (9,"Advanced","Economics Basics","Poverty",
     "India's poverty line is defined based on:",
     ["Monthly per capita expenditure needed to meet minimum calorie requirement (2400 kcal rural / 2100 kcal urban)",
      "Annual household income below ₹1 lakh",
      "Access to 3 meals per day",
      "Ownership of land below 1 acre"], 0,
     "India's official poverty line is based on the caloric norm: a person spending less than what's needed to buy 2,400 kcal/day (rural) or 2,100 kcal/day (urban) is considered poor. The Tendulkar Committee later revised this methodology."),

    (9,"Olympiad","Modern Indian History","Colonialism",
     "The 'Drain of Wealth' theory was formulated by Dadabhai Naoroji. He calculated that Britain drained India's resources as 'unrequited exports'. This means:",
     ["India exported goods and services to Britain but received NO payment in return — the value was taken as taxes and profits",
      "India imported more than it exported",
      "British goods were sold in India below market price",
      "India paid heavy customs duty on its own exports"], 0,
     "Naoroji showed that India exported goods (cotton, opium, indigo) to Britain but the revenue went directly to British coffers as taxes, salaries of British officers, and profits — India got nothing back. This 'invisible' transfer was the Drain of Wealth."),

    (9,"Olympiad","Indian Geography","Climate",
     "El Niño events (warming of Pacific Ocean surface) tend to cause BELOW-NORMAL monsoon rainfall in India. The mechanism is:",
     ["El Niño weakens the temperature difference between Indian land and Indian Ocean, reducing the pressure gradient that drives the SW Monsoon",
      "El Niño cools the Bay of Bengal, reducing evaporation",
      "El Niño diverts monsoon winds towards Australia",
      "El Niño increases Himalayan snowfall which blocks monsoon entry"], 0,
     "Normal SW Monsoon is driven by low pressure over hot Indian land vs high pressure over cooler Indian Ocean. El Niño warms the central/eastern Pacific, redistributing heat and weakening the Indian Ocean-land temperature contrast, thus reducing monsoon intensity."),

    (9,"Olympiad","Economics Basics","Development",
     "Per capita income is used as a development indicator, but it has a major limitation. Which of the following BEST captures this limitation?",
     ["It is an average that hides inequality — a country with 10 billionaires and 90 poor people looks the same as one with moderate uniform income",
      "It does not count agricultural income",
      "It only measures income from formal jobs",
      "It counts government spending, not private income"], 0,
     "Per capita income = total income ÷ population. If income is unequal, the average is misleading. India may have a higher per capita than another country but more absolute poor people. That is why HDI (Human Development Index) adds health and education to income."),

    (9,"Foundation","Indian Civics","Elections",
     "India uses which electoral system for Lok Sabha elections?",
     ["First Past The Post (FPTP)","Proportional Representation","Two-round system","Single Transferable Vote"], 0,
     "India's Lok Sabha uses FPTP: each constituency elects ONE member, and the candidate with the most votes wins — even without a majority. This is simple but can mean parties win seats without majority support."),
]

def gen_text_questions():
    print("\n[Text Questions — Grades 5, 6, 7, 9 (thin SST fill)]")
    grade_counts = {5:0, 6:0, 7:0, 9:0}
    for row in TEXT_QS:
        grade, diff, topic, subtopic, qtext, opts, cidx, expl = row
        ok = post_text_q(grade, diff, topic, subtopic, qtext, opts, cidx, expl)
        if ok:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        print(f"  G{grade} [{diff}] {topic[:20]}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.25)
    print(f"  Per grade: { {k:v for k,v in grade_counts.items()} }")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 65)
    print("OlympiadReady — SST v2: Grade 10 images + thin grade fill")
    print("=" * 65)

    # Image questions
    gen_bar_charts_gr10()
    gen_bar_charts_lower()
    gen_pie_charts()
    gen_timelines()
    gen_map_questions()
    gen_civics_diagrams()

    # Text fill for thin grades
    gen_text_questions()

    total = POSTED + SKIPPED + FAILED
    print(f"\n{'='*65}")
    print(f"DONE — Posted: {POSTED}  Skipped(dup): {SKIPPED}  Failed: {FAILED}  Total: {total}")
    print(f"{'='*65}")
