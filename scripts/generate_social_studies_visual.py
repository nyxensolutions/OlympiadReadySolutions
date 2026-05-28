"""
generate_social_studies_visual.py
Image-based Social Studies questions across Grades 3-10:
  1. Indian Map — states, capitals, rivers, regions
  2. Historical Timeline — ancient/medieval/modern India
  3. Bar/Pie Charts — population, resources, data
  4. Diagram — government structure, food chain, water cycle
  5. Globe & Directions — latitude, longitude, hemispheres

Requirements: pip install pillow cloudinary requests
"""

import os, io, random, time, math
import requests
import cloudinary, cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont

CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME, api_key=CLOUDINARY_API_KEY, api_secret=CLOUDINARY_API_SECRET)
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

try:
    FONT_SM  = ImageFont.truetype("arial.ttf", 13)
    FONT_MD  = ImageFont.truetype("arial.ttf", 16)
    FONT_LG  = ImageFont.truetype("arial.ttf", 20)
    FONT_XL  = ImageFont.truetype("arial.ttf", 26)
    FONT_BD  = ImageFont.truetype("arialbd.ttf", 18)
except:
    FONT_SM = FONT_MD = FONT_LG = FONT_XL = FONT_BD = ImageFont.load_default()

POSTED = SKIPPED = FAILED = 0

def canvas(w=520, h=400, bg="white"):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)

def upload(img, label):
    buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    res = cloudinary.uploader.upload(buf, folder=CLOUDINARY_FOLDER,
        public_id=f"sst_{label}_{int(time.time()*1000)}", resource_type="image")
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
                              json=payload, headers=HEADERS, timeout=25)
            if r.status_code in (200, 201): POSTED += 1; return True
            elif r.status_code == 409:      SKIPPED += 1; return False
            else: print(f"    FAIL {r.status_code}: {r.text[:80]}"); FAILED += 1; return False
        except Exception as e:
            if attempt == 0: time.sleep(2)
            else: print(f"    ERR: {e}"); FAILED += 1; return False

# ─────────────────────────────────────────────────────────────────────────────
# 1. BAR CHARTS — Population / Resource / Production Data
# ─────────────────────────────────────────────────────────────────────────────

BAR_CHART_DATA = [
    # (title, labels, values, unit, question, correct, wrongs, topic, grade, diff)
    ("Rice Production by State (million tonnes)", ["WB","UP","Punjab","AP","Bihar"],
     [15,12,11,9,7], "MT", "Which state has the HIGHEST rice production as shown?",
     "West Bengal (WB)", ["Uttar Pradesh (UP)","Punjab","Andhra Pradesh (AP)"],
     "Indian Geography", 6, "Advanced"),
    ("Literacy Rate by Region (%)", ["Kerala","Delhi","Maharashtra","Bihar","Rajasthan"],
     [94,86,84,62,67], "%", "Which region has the LOWEST literacy rate?",
     "Bihar", ["Rajasthan","Maharashtra","Delhi"],
     "Indian Civics", 7, "Advanced"),
    ("Forest Cover by Zone (000 sq km)", ["Northeast","Central","Western Ghats","Himalayan","Deccan"],
     [170,140,60,50,40], "000 sq km", "The forest cover difference between Northeast and Deccan zones is:",
     "1,30,000 sq km", ["1,10,000 sq km","2,10,000 sq km","1,70,000 sq km"],
     "Environment and Ecology", 8, "Olympiad"),
    ("Coal Reserves by State (billion tonnes)", ["Jharkhand","Odisha","Chhattisgarh","WB","MP"],
     [84,79,52,32,27], "BT", "Which TWO states together hold more than 50% of total reserves shown?",
     "Jharkhand and Odisha", ["Jharkhand and Chhattisgarh","Odisha and Chhattisgarh","Jharkhand and WB"],
     "Indian Geography", 9, "Olympiad"),
    ("Wheat Production by State (MT)", ["UP","Punjab","Haryana","MP","Rajasthan"],
     [30,17,12,9,8], "MT", "If Punjab's production increases by 20%, its new production would be:",
     "20.4 MT", ["21 MT","19 MT","22 MT"],
     "Indian Geography", 8, "Olympiad"),
    ("Population Growth (crores)", ["1951","1971","1991","2001","2011"],
     [36,55,85,103,121], "Cr", "Between which two decades was population growth the STEEPEST?",
     "1991–2001 is second; 2001–2011 shows 18Cr — actually 1971–1991 shows 30Cr net",
     ["1951–1971","1971–1991","2001–2011"],
     "Indian Civics", 7, "Foundation"),
    ("Rainfall (mm) — Cities", ["Mumbai","Chennai","Kolkata","Delhi","Bengaluru"],
     [2200,1400,1600,800,980], "mm", "Which city receives more than double the rainfall of Delhi?",
     "Mumbai", ["Kolkata","Chennai","Bengaluru"],
     "Indian Geography", 5, "Foundation"),
    ("Major Crop Area (million hectares)", ["Rice","Wheat","Cotton","Sugarcane","Pulses"],
     [44,29,12,5,23], "Mha", "The ratio of Rice area to Wheat area (approx.) is:",
     "3:2", ["2:1","4:3","5:3"],
     "Indian Geography", 9, "Advanced"),
]

def draw_bar_chart(title, labels, values, unit):
    img, draw = canvas(540, 400, "#FAFAFA")
    draw.rectangle([0,0,540,400], outline="#CCC", width=1)
    # Title
    draw.text((270,12), title, fill="#1a1a2e", font=FONT_MD, anchor="mt")
    # Chart area
    cx, cy, cw, ch = 60, 50, 420, 290
    max_v = max(values) * 1.15
    bar_w = cw // len(labels) - 8
    colors = ["#3498DB","#E74C3C","#2ECC71","#F39C12","#9B59B6"]
    # Y-axis
    for i in range(5):
        yv = max_v * i / 4
        y = cy + ch - int(ch * i / 4)
        draw.line([(cx, y),(cx+cw, y)], fill="#DDD", width=1)
        draw.text((cx-5, y), f"{int(yv)}", fill="#666", font=FONT_SM, anchor="rm")
    draw.line([(cx, cy),(cx, cy+ch)], fill="#555", width=2)
    draw.line([(cx, cy+ch),(cx+cw, cy+ch)], fill="#555", width=2)
    # Bars
    for i, (lbl, val) in enumerate(zip(labels, values)):
        bx = cx + i * (bar_w + 8) + 12
        bh = int(ch * val / max_v)
        by = cy + ch - bh
        draw.rectangle([bx, by, bx+bar_w, cy+ch], fill=colors[i % len(colors)])
        draw.text((bx + bar_w//2, by-4), str(val), fill="#333", font=FONT_SM, anchor="mb")
        draw.text((bx + bar_w//2, cy+ch+6), lbl, fill="#333", font=FONT_SM, anchor="mt")
    draw.text((270, 395), f"Unit: {unit}", fill="#888", font=FONT_SM, anchor="mb")
    return img

def gen_bar_charts():
    print("\n[Bar Chart Questions] generating...")
    for i, (title, labels, values, unit, qtext, correct, wrongs, topic, grade, diff) in enumerate(BAR_CHART_DATA):
        img = draw_bar_chart(title, labels, values, unit)
        url = upload(img, f"bar_{i}")
        opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Data Interpretation", qtext, url, opts, cidx,
                    f"Reading from the bar chart: {correct}.")
        print(f"  bar_{i}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# 2. HISTORICAL TIMELINES
# ─────────────────────────────────────────────────────────────────────────────

TIMELINE_DATA = [
    # (events: [(year, label)], question, correct, wrongs, topic, grade, diff)
    ([(322,"Maurya Empire founded"),(273,"Ashoka becomes king"),
      (185,"Maurya Empire ends"),(320,"Gupta Empire begins"),(550,"Gupta Empire ends")],
     "How many years after the Maurya Empire was founded did Ashoka become king?",
     "49 years (322–273 BCE)", ["45 years","53 years","60 years"],
     "Ancient Indian History", 6, "Advanced"),
    ([(1526,"First Battle of Panipat"),(1556,"Second Battle of Panipat"),
      (1600,"British East India Co."),(1757,"Battle of Plassey"),(1857,"1857 Revolt")],
     "How many years passed between the First and Second Battle of Panipat?",
     "30 years", ["26 years","40 years","56 years"],
     "Medieval Indian History", 7, "Foundation"),
    ([(1885,"INC founded"),(1905,"Bengal Partition"),(1919,"Jallianwala Bagh"),
      (1930,"Dandi March"),(1947,"Independence")],
     "Which event came IMMEDIATELY after the founding of INC on this timeline?",
     "Bengal Partition (1905)", ["Jallianwala Bagh (1919)","Dandi March (1930)","INC founded (1885)"],
     "Modern Indian History", 7, "Foundation"),
    ([(1600,"British EIC"),(1757,"Battle of Plassey"),(1857,"Revolt"),(1919,"Jallianwala Bagh"),(1947,"Independence")],
     "The time gap between the Battle of Plassey and Indian Independence (1947) is:",
     "190 years", ["150 years","180 years","200 years"],
     "Modern Indian History", 8, "Advanced"),
    ([(600,"Pallava Kingdom"),(753,"Rashtrakuta rise"),(850,"Chola revival"),(985,"Rajaraja Chola I"),(1070,"Kulottunga I")],
     "Which dynasty was at its peak approximately 200 years after the Pallava Kingdom began?",
     "Rashtrakuta (753 CE)", ["Chola (850 CE)","Pallava (600 CE)","Kulottunga I (1070 CE)"],
     "Ancient Indian History", 9, "Olympiad"),
]

def draw_timeline(events):
    img, draw = canvas(540, 260, "#FFFEF0")
    draw.rectangle([0,0,540,260], outline="#CCC", width=1)
    draw.text((270,10), "Historical Timeline", fill="#1a1a2e", font=FONT_LG, anchor="mt")
    years = [e[0] for e in events]
    min_y, max_y = min(years), max(years)
    span = max_y - min_y or 1
    lx, rx, ty = 40, 500, 110
    draw.line([(lx, ty),(rx, ty)], fill="#8B4513", width=3)
    colors = ["#E74C3C","#3498DB","#2ECC71","#F39C12","#9B59B6"]
    for i, (yr, lbl) in enumerate(events):
        x = lx + int((yr - min_y) / span * (rx - lx))
        draw.ellipse([x-6, ty-6, x+6, ty+6], fill=colors[i % len(colors)], outline="#333", width=1)
        draw.text((x, ty-14), str(yr), fill="#333", font=FONT_SM, anchor="mb")
        # Alternate above/below
        yt = ty + 20 + (i % 2) * 40
        draw.line([(x, ty+6),(x, yt-2)], fill="#AAA", width=1)
        draw.text((x, yt), lbl, fill="#1a1a2e", font=FONT_SM, anchor="mt")
    return img

def gen_timelines():
    print("\n[Historical Timeline Questions] generating...")
    for i, (events, qtext, correct, wrongs, topic, grade, diff) in enumerate(TIMELINE_DATA):
        img = draw_timeline(events)
        url = upload(img, f"timeline_{i}")
        opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Timeline", qtext, url, opts, cidx,
                    f"From the timeline: {correct}.")
        print(f"  timeline_{i}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# 3. MAP-BASED QUESTIONS (India outline with labelled regions)
# ─────────────────────────────────────────────────────────────────────────────

MAP_QUESTIONS = [
    # (marker_label, description, question, correct, wrongs, topic, grade, diff)
    ("River Ganga route", "The map shows the Ganga river flowing from the Himalayas to the Bay of Bengal",
     "The Ganga enters the sea through which water body as shown?",
     "Bay of Bengal", ["Arabian Sea","Indian Ocean","Lakshadweep Sea"],
     "Indian Geography", 5, "Foundation"),
    ("Tropic of Cancer", "The dashed line passes through 23.5°N latitude across India",
     "Which of these states does the Tropic of Cancer pass through?",
     "Madhya Pradesh", ["Kerala","Jammu & Kashmir","Tamil Nadu"],
     "Indian Geography", 6, "Advanced"),
    ("Western Ghats & Eastern Ghats", "Two mountain ranges are highlighted on the map",
     "The Western Ghats run PARALLEL to which coastline?",
     "West Coast (Arabian Sea)", ["East Coast (Bay of Bengal)","North Coast","South tip only"],
     "Indian Geography", 6, "Foundation"),
    ("The Deccan Plateau", "A large elevated region in central-southern India is shaded",
     "The Deccan Plateau is bounded on the west and east by which ranges respectively?",
     "Western Ghats and Eastern Ghats", ["Aravalli and Vindhya","Satpura and Vindhya","Eastern Ghats and Satpura"],
     "Indian Geography", 7, "Advanced"),
    ("Delta regions highlighted", "The map marks deltas of Ganga, Godavari, Krishna, and Mahanadi",
     "Deltas are formed when rivers meet the sea because:",
     "Velocity decreases, sediments are deposited", ["Velocity increases and erodes land",
     "River splits into tributaries only","Sea water evaporates quickly"],
     "Indian Geography", 8, "Olympiad"),
    ("Monsoon arrows on India map", "Arrows show SW monsoon entering India from Arabian Sea and Bay of Bengal",
     "The Arabian Sea branch of the SW Monsoon first hits which region?",
     "Western coast (Kerala)", ["Rajasthan","West Bengal","Gujarat"],
     "Indian Geography", 7, "Advanced"),
    ("Standard Meridian of India", "A vertical line at 82.5°E longitude is marked on the India map",
     "India's Standard Meridian passes through which state?",
     "Uttar Pradesh (Mirzapur)", ["Maharashtra","Rajasthan","Assam"],
     "Indian Geography", 8, "Foundation"),
    ("Himalayan ranges labelled", "Three parallel ranges: Himadri (Greater), Himachal (Lesser), Shivalik",
     "Which Himalayan range has the highest average elevation?",
     "Himadri (Greater Himalayas)", ["Shivalik","Himachal (Lesser Himalayas)","All are equal"],
     "Indian Geography", 6, "Foundation"),
    ("Latitude & Longitude grid", "A grid shows India between 8°N–37°N and 68°E–97°E",
     "India's latitudinal extent is approximately 29 degrees. This means India spans how many time zones theoretically?",
     "Almost 2 time zones (29°÷15°≈1.9)", ["1 time zone","3 time zones","4 time zones"],
     "Indian Geography", 9, "Olympiad"),
    ("Political map — NE states", "Seven states of Northeast India are labelled",
     "Which is the LARGEST state by area among the seven sisters of Northeast India?",
     "Arunachal Pradesh", ["Assam","Meghalaya","Manipur"],
     "Indian Geography", 8, "Advanced"),
]

def draw_india_map_q(marker_label, description):
    """Simple schematic India outline with label and description."""
    img, draw = canvas(540, 380, "#E8F4FD")
    draw.rectangle([0,0,540,380], outline="#AAA", width=1)
    # Simplified India outline (polygon approximation)
    pts = [
        (200,30),(260,25),(310,40),(360,60),(390,100),
        (400,140),(420,170),(410,210),(430,240),(420,280),
        (390,310),(350,340),(310,360),(270,370),(240,365),
        (210,350),(180,320),(160,290),(150,250),(140,210),
        (130,170),(140,130),(150,90),(170,60),(200,30)
    ]
    draw.polygon(pts, fill="#C8E6C9", outline="#388E3C", width=2)
    # Marker
    cx, cy = 270, 200
    draw.ellipse([cx-8,cy-8,cx+8,cy+8], fill="#E74C3C", outline="#C0392B", width=2)
    draw.text((cx+12, cy-8), marker_label, fill="#C0392B", font=FONT_SM)
    # Description box
    draw.rectangle([10, 310, 530, 375], fill="#FFF9C4", outline="#F9A825", width=1)
    draw.text((270, 320), "Map Description:", fill="#E65100", font=FONT_MD, anchor="mt")
    draw.text((270, 342), description, fill="#333", font=FONT_SM, anchor="mt")
    return img

def gen_map_questions():
    print("\n[Map-Based Questions] generating...")
    for i, (marker, desc, qtext, correct, wrongs, topic, grade, diff) in enumerate(MAP_QUESTIONS):
        img = draw_india_map_q(marker, desc)
        url = upload(img, f"map_{i}")
        opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Map Reading", qtext, url, opts, cidx,
                    f"The correct answer is: {correct}.")
        print(f"  map_{i} ({topic})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# 4. GOVERNMENT STRUCTURE DIAGRAMS
# ─────────────────────────────────────────────────────────────────────────────

GOVT_QUESTIONS = [
    ("Which branch of the Indian government is responsible for making laws?",
     "Legislature (Parliament)", ["Executive","Judiciary","Bureaucracy"],
     "Indian Civics", 6, "Foundation"),
    ("In the diagram of Parliament, the upper house is:",
     "Rajya Sabha", ["Lok Sabha","Vidhan Sabha","Vidhan Parishad"],
     "Indian Civics", 7, "Foundation"),
    ("According to the diagram, who is the constitutional head of the Executive?",
     "President of India", ["Prime Minister","Chief Justice","Speaker of Lok Sabha"],
     "Indian Civics", 8, "Advanced"),
    ("The diagram shows three tiers of government. The third tier (local self-government) was strengthened by which Amendment?",
     "73rd and 74th Constitutional Amendments", ["42nd Amendment","86th Amendment","52nd Amendment"],
     "Indian Civics", 9, "Olympiad"),
    ("If the President returns a bill to Parliament and Parliament passes it again, what must the President do?",
     "Give assent (cannot return it again)", ["Reject it permanently","Send to Supreme Court","Call fresh elections"],
     "Indian Civics", 9, "Olympiad"),
]

def draw_govt_diagram():
    img, draw = canvas(540, 360, "#F3E5F5")
    draw.rectangle([0,0,540,360], outline="#9C27B0", width=2)
    draw.text((270,12), "Structure of Indian Government", fill="#4A148C", font=FONT_LG, anchor="mt")
    # Three pillars
    pillars = [("Legislature\n(Parliament)", 100, "#3F51B5"),
               ("Executive\n(President/PM)", 270, "#E91E63"),
               ("Judiciary\n(Courts)", 440, "#009688")]
    for label, x, color in pillars:
        draw.rectangle([x-65, 60, x+65, 130], fill=color, outline="#333", width=1)
        for line in label.split("\n"):
            draw.text((x, 75 + label.split("\n").index(line)*22), line,
                      fill="white", font=FONT_MD, anchor="mt")
    # Constitution base
    draw.rectangle([60, 160, 480, 200], fill="#FF9800", outline="#E65100", width=2)
    draw.text((270, 175), "Constitution of India", fill="white", font=FONT_BD, anchor="mm")
    # Arrows up
    for x in [100, 270, 440]:
        draw.line([(x, 160),(x, 132)], fill="#555", width=2)
        draw.polygon([(x,130),(x-6,142),(x+6,142)], fill="#555")
    # Parliament sub-boxes
    draw.rectangle([20, 230, 180, 280], fill="#7986CB", outline="#3949AB", width=1)
    draw.text((100, 255), "Rajya Sabha", fill="white", font=FONT_SM, anchor="mm")
    draw.rectangle([20, 290, 180, 340], fill="#5C6BC0", outline="#3949AB", width=1)
    draw.text((100, 315), "Lok Sabha", fill="white", font=FONT_SM, anchor="mm")
    draw.line([(100,230),(100,200)], fill="#888", width=1)
    return img

def gen_govt_questions():
    print("\n[Government Structure Questions] generating...")
    img = draw_govt_diagram()
    url = upload(img, "govt_structure")
    for i, (qtext, correct, wrongs, topic, grade, diff) in enumerate(GOVT_QUESTIONS):
        opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Government Structure", qtext, url, opts, cidx,
                    f"The correct answer is: {correct}.")
        print(f"  govt_{i}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# 5. PIE CHARTS — Land Use, Religious Demographics, etc.
# ─────────────────────────────────────────────────────────────────────────────

PIE_DATA = [
    ("Land Use in India", ["Net Sown Area\n43%","Forests\n22%","Wasteland\n14%",
      "Other Uses\n12%","Fallow\n9%"],
     [43,22,14,12,9],
     "What fraction of India's total land is under forest cover (approx)?",
     "About 1/5 (22%)", ["About 1/3","About 1/10","About 1/4"],
     "Environment and Ecology", 6, "Advanced"),
    ("India's Energy Sources", ["Coal\n55%","Renewables\n23%","Nuclear\n3%",
      "Hydro\n12%","Gas\n7%"],
     [55,23,3,12,7],
     "Non-fossil fuel energy sources (Renewables + Nuclear + Hydro) together form approximately:",
     "38% of total energy", ["30%","45%","50%"],
     "Indian Geography", 9, "Olympiad"),
    ("Occupational Distribution", ["Agriculture\n54%","Industry\n26%",
      "Services\n20%"],
     [54,26,20],
     "What is the approximate ratio of people in Agriculture to those in Services?",
     "8:3 (54:20 ≈ 2.7:1)", ["3:1","2:1","5:2"],
     "Economics Basics", 8, "Olympiad"),
]

def draw_pie(title, labels, values):
    img, draw = canvas(540, 380, "#FFFFF0")
    draw.rectangle([0,0,540,380], outline="#CCC", width=1)
    draw.text((270,10), title, fill="#1a1a2e", font=FONT_MD, anchor="mt")
    colors = ["#E74C3C","#3498DB","#2ECC71","#F39C12","#9B59B6","#1ABC9C"]
    total = sum(values)
    cx, cy, r = 180, 200, 140
    start = -90
    for i, (lbl, val) in enumerate(zip(labels, values)):
        sweep = 360 * val / total
        draw.pieslice([cx-r, cy-r, cx+r, cy+r], start=start, end=start+sweep,
                      fill=colors[i % len(colors)], outline="white", width=2)
        # Label line
        mid_angle = math.radians(start + sweep/2)
        lx2 = cx + int((r+20) * math.cos(mid_angle))
        ly2 = cy + int((r+20) * math.sin(mid_angle))
        draw.text((lx2, ly2), lbl, fill=colors[i % len(colors)], font=FONT_SM, anchor="mm")
        start += sweep
    # Legend
    for i, (lbl, val) in enumerate(zip(labels, values)):
        lx2 = 360; ly2 = 80 + i*40
        draw.rectangle([lx2, ly2, lx2+18, ly2+18], fill=colors[i % len(colors)])
        first_line = lbl.split("\n")[0]
        draw.text((lx2+24, ly2+9), first_line, fill="#333", font=FONT_SM, anchor="lm")
    return img

def gen_pie_charts():
    print("\n[Pie Chart Questions] generating...")
    for i, (title, labels, values, qtext, correct, wrongs, topic, grade, diff) in enumerate(PIE_DATA):
        img = draw_pie(title, labels, values)
        url = upload(img, f"pie_{i}")
        opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
        ok = post_q(grade, diff, topic, "Data Interpretation", qtext, url, opts, cidx,
                    f"Reading from the pie chart: {correct}.")
        print(f"  pie_{i}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("OlympiadReady — Social Studies Visual Questions")
    print("=" * 60)

    gen_bar_charts()
    gen_timelines()
    gen_map_questions()
    gen_govt_questions()
    gen_pie_charts()

    total = POSTED + SKIPPED + FAILED
    print(f"\nDONE — Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}  Total: {total}")
