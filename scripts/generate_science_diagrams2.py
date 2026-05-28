"""
generate_science_diagrams2.py
Science diagram generators — Batch 2:
  1.  Simple Machines       (Grades 4-8)   — text options
  2.  States of Matter      (Grades 4-7)   — text options
  3.  Food Web              (Grades 5-8)   — text options
  4.  Human Body Systems    (Grades 5-9)   — text options
  5.  Plant Parts           (Grades 2-6)   — text options
  6.  Digestive System      (Grades 6-9)   — text options
  7.  Weather Instruments   (Grades 5-7)   — text options
  8.  Types of Triangles    (Grades 4-8)   — text options
  9.  Angles                (Grades 4-7)   — text options
 10.  Number Patterns       (Grades 3-8)   — text options

Requirements: pip install pillow cloudinary requests
"""

import os, io, json, random, time, math, sys
import requests
import cloudinary, cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ── CONFIG ────────────────────────────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")
QPT                   = 20   # questions per type

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key    = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET,
)

HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

try:
    FONT_SM  = ImageFont.truetype("arial.ttf", 14)
    FONT_MD  = ImageFont.truetype("arial.ttf", 18)
    FONT_LG  = ImageFont.truetype("arial.ttf", 22)
    FONT_XL  = ImageFont.truetype("arial.ttf", 28)
    FONT_XXL = ImageFont.truetype("arial.ttf", 36)
except:
    FONT_SM  = ImageFont.load_default()
    FONT_MD  = FONT_SM
    FONT_LG  = FONT_SM
    FONT_XL  = FONT_SM
    FONT_XXL = FONT_SM

POSTED = 0
SKIPPED = 0
FAILED = 0

def difficulty_for_grade(grade):
    if grade <= 4:   return "Foundation"
    elif grade <= 7: return random.choice(["Foundation", "Advanced"])
    else:            return random.choice(["Advanced", "Olympiad"])

def upload_pil(img, label="img"):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    res = cloudinary.uploader.upload(buf, folder=CLOUDINARY_FOLDER,
                                     public_id=f"sd2_{label}_{int(time.time()*1000)}",
                                     resource_type="image")
    return res["secure_url"]

def post_question(subject, grade, difficulty, topic, subtopic, text, img_url, opts, correct_idx, expl):
    global POSTED, SKIPPED, FAILED
    correct_letter = chr(65 + correct_idx)
    payload = {
        "subject": subject, "grade": grade, "difficulty": difficulty,
        "topic": topic, "subTopic": subtopic,
        "questionText": text, "imageUrl": img_url,
        "options": opts, "correctAnswer": correct_letter,
        "explanation": expl,
    }
    try:
        r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                          json=payload, headers=HEADERS, timeout=20)
        if r.status_code in (200, 201):
            POSTED += 1
            return True
        elif r.status_code == 409:
            SKIPPED += 1
            return False
        else:
            FAILED += 1
            print(f"    FAIL {r.status_code}: {r.text[:80]}")
            return False
    except Exception as e:
        FAILED += 1
        print(f"    ERROR: {e}")
        return False

def make_img(w=500, h=400, bg="white"):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)

# ══════════════════════════════════════════════════════════════════════════════
# 1. SIMPLE MACHINES
# ══════════════════════════════════════════════════════════════════════════════

SIMPLE_MACHINES = {
    "Lever": {
        "description": "A rigid bar that pivots on a fulcrum to lift loads",
        "parts": ["Effort", "Fulcrum", "Load"],
        "grades": [4, 5, 6, 7, 8],
        "classes": ["Class 1 (fulcrum between effort and load)",
                    "Class 2 (load between effort and fulcrum)",
                    "Class 3 (effort between fulcrum and load)"],
    },
    "Inclined Plane": {
        "description": "A flat surface tilted at an angle to reduce effort needed",
        "grades": [4, 5, 6],
    },
    "Pulley": {
        "description": "A wheel with a groove for a rope/chain to change force direction",
        "grades": [5, 6, 7, 8],
        "types": ["Fixed pulley", "Movable pulley", "Compound pulley"],
    },
    "Wheel and Axle": {
        "description": "A larger wheel attached to a smaller axle to multiply force",
        "grades": [5, 6, 7],
    },
    "Wedge": {
        "description": "Two inclined planes joined to split or lift objects",
        "grades": [4, 5, 6],
    },
    "Screw": {
        "description": "An inclined plane wrapped around a cylinder",
        "grades": [5, 6, 7],
    },
}

def draw_lever(highlight_part=None, lever_class=1):
    img, draw = make_img(500, 340, "#F8F9FA")
    draw.text((20, 12), "Simple Machine: Lever", fill="#2C3E50", font=FONT_LG)
    # Beam
    beam_y = 200
    draw.rectangle([60, beam_y-8, 440, beam_y+8], fill="#7F8C8D")
    # Fulcrum (triangle)
    if lever_class == 1:
        ful_x = 250
    elif lever_class == 2:
        ful_x = 80
    else:
        ful_x = 420
    tri = [(ful_x, beam_y+8), (ful_x-20, beam_y+50), (ful_x+20, beam_y+50)]
    draw.polygon(tri, fill="#E74C3C" if highlight_part=="Fulcrum" else "#C0392B")
    draw.text((ful_x-18, beam_y+52), "Fulcrum", fill="#E74C3C", font=FONT_SM)
    # Effort arrow
    if lever_class == 1:
        eff_x = 100
    elif lever_class == 2:
        eff_x = 400
    else:
        eff_x = 200
    eff_color = "#27AE60" if highlight_part == "Effort" else "#2ECC71"
    draw.line([(eff_x, beam_y-8), (eff_x, beam_y-60)], fill=eff_color, width=4)
    draw.polygon([(eff_x, beam_y-70), (eff_x-10, beam_y-50), (eff_x+10, beam_y-50)], fill=eff_color)
    draw.text((eff_x-15, beam_y-90), "Effort", fill=eff_color, font=FONT_SM)
    # Load box
    if lever_class == 1:
        load_x = 390
    elif lever_class == 2:
        load_x = 220
    else:
        load_x = 90
    load_color = "#2980B9" if highlight_part == "Load" else "#3498DB"
    draw.rectangle([load_x-20, beam_y-65, load_x+20, beam_y-8], fill=load_color)
    draw.text((load_x-12, beam_y-50), "Load", fill="white", font=FONT_SM)
    return img

def draw_pulley(ptype="Fixed"):
    img, draw = make_img(400, 360, "#F8F9FA")
    draw.text((20, 12), f"Pulley: {ptype}", fill="#2C3E50", font=FONT_LG)
    cx, cy = 200, 100
    r = 45
    # Pulley wheel
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline="#7F8C8D", width=4)
    draw.ellipse([cx-12, cy-12, cx+12, cy+12], fill="#7F8C8D")
    # Rope
    draw.line([(cx-r, cy), (cx-r, 290)], fill="#8B4513", width=4)
    draw.line([(cx+r, cy), (cx+r, 290)], fill="#8B4513", width=4)
    # Load box
    draw.rectangle([cx-35, 270, cx+35, 310], fill="#3498DB")
    draw.text((cx-18, 282), "Load", fill="white", font=FONT_SM)
    # Support
    draw.line([(cx, cy-r), (cx, 20)], fill="#8B4513", width=4)
    draw.rectangle([cx-40, 10, cx+40, 25], fill="#7F8C8D")
    # Effort
    draw.text((cx+r+8, 130), "Effort", fill="#27AE60", font=FONT_SM)
    draw.polygon([(cx+r+3, 280), (cx+r+13, 260), (cx+r+23, 280)], fill="#27AE60")
    return img

def draw_inclined_plane(angle=30):
    img, draw = make_img(480, 320, "#F8F9FA")
    draw.text((20, 12), "Simple Machine: Inclined Plane", fill="#2C3E50", font=FONT_LG)
    pts = [(60, 260), (420, 260), (420, 100)]
    draw.polygon(pts, fill="#BDC3C7", outline="#7F8C8D")
    # Object on slope
    slope_x = 280
    slope_y = int(260 - (slope_x - 60) * (160/360))
    draw.ellipse([slope_x-20, slope_y-35, slope_x+20, slope_y-5], fill="#E74C3C")
    draw.text((slope_x-6, slope_y-28), "Box", fill="white", font=FONT_SM)
    # Angle label
    draw.text((80, 240), f"{angle}°", fill="#2C3E50", font=FONT_MD)
    draw.text((440, 170), "Height", fill="#2980B9", font=FONT_SM)
    draw.text((200, 268), "Length", fill="#27AE60", font=FONT_SM)
    return img

def gen_simple_machines(n=QPT):
    print(f"[Simple Machines] {n} questions...")
    machines = list(SIMPLE_MACHINES.keys())
    q_count = 0

    q_templates = [
        # (question_template, answer_key, wrong_list)
        ("Which part of a lever pivots and supports the beam?",
         "Fulcrum", ["Effort", "Load", "Axle"]),
        ("In a Class 1 lever, where is the fulcrum located?",
         "Between effort and load", ["Between load and effort arm end", "At the effort end", "At the load end"]),
        ("Which simple machine is an inclined plane wrapped around a cylinder?",
         "Screw", ["Wedge", "Lever", "Pulley"]),
        ("A ramp used to load boxes onto a truck is an example of which simple machine?",
         "Inclined Plane", ["Wedge", "Screw", "Pulley"]),
        ("Which simple machine consists of a wheel with a groove for a rope?",
         "Pulley", ["Lever", "Wedge", "Wheel and Axle"]),
        ("In a fixed pulley, what changes when you pull the rope?",
         "Direction of force", ["Magnitude of force", "Load weight", "Speed of load"]),
        ("A wedge is made up of how many inclined planes joined together?",
         "Two", ["One", "Three", "Four"]),
        ("Which simple machine multiplies force using a larger wheel and a smaller axle?",
         "Wheel and Axle", ["Pulley", "Lever", "Screw"]),
        ("Scissors are an example of which type of simple machine?",
         "Lever", ["Pulley", "Wedge", "Screw"]),
        ("A door knob is an example of which simple machine?",
         "Wheel and Axle", ["Lever", "Pulley", "Screw"]),
        ("In which class of lever is the load between the fulcrum and effort?",
         "Class 2", ["Class 1", "Class 3", "Class 4"]),
        ("A movable pulley reduces the effort needed by?",
         "Half", ["Double", "One-third", "One-fourth"]),
        ("Which simple machine is used to split wood?",
         "Wedge", ["Lever", "Screw", "Pulley"]),
        ("The mechanical advantage of a simple machine tells us:",
         "How many times it multiplies force", ["How fast it works", "How much energy it stores", "Its weight"]),
        ("A seesaw in a park is an example of which class of lever?",
         "Class 1", ["Class 2", "Class 3", "Class 4"]),
        ("Which part of a lever is acted upon by the effort?",
         "Effort arm", ["Load arm", "Fulcrum", "Beam centre"]),
        ("A wheelbarrow is an example of which class of lever?",
         "Class 2", ["Class 1", "Class 3", "Class 4"]),
        ("Tweezers are an example of which class of lever?",
         "Class 3", ["Class 1", "Class 2", "Class 4"]),
        ("Which simple machine is found in a spiral staircase?",
         "Screw", ["Inclined Plane", "Wedge", "Lever"]),
        ("A bottle opener is an example of which class of lever?",
         "Class 2", ["Class 1", "Class 3", "Class 4"]),
    ]

    machine_imgs = {
        "Lever": draw_lever,
        "Inclined Plane": lambda: draw_inclined_plane(30),
        "Pulley": lambda: draw_pulley("Fixed"),
    }

    for i in range(min(n, len(q_templates))):
        tmpl = q_templates[i]
        question_text = tmpl[0]
        correct = tmpl[1]
        wrongs = tmpl[2][:3]
        opts = [correct] + wrongs
        random.shuffle(opts)
        cidx = opts.index(correct)

        # Pick a relevant illustration
        if "lever" in question_text.lower() or "class" in question_text.lower() or "seesaw" in question_text.lower() or "wheelbarrow" in question_text.lower() or "tweezers" in question_text.lower() or "scissors" in question_text.lower() or "bottle" in question_text.lower():
            img = draw_lever(lever_class=1)
        elif "inclined" in question_text.lower() or "ramp" in question_text.lower():
            img = draw_inclined_plane()
        elif "pulley" in question_text.lower() or "rope" in question_text.lower():
            img = draw_pulley()
        else:
            img, draw2 = make_img(480, 320, "#F8F9FA")
            draw2.text((20, 20), "Simple Machines", fill="#2C3E50", font=FONT_XL)
            machine_names = list(SIMPLE_MACHINES.keys())
            for j, m in enumerate(machine_names):
                draw2.text((30, 70 + j*38), f"• {m}: {SIMPLE_MACHINES[m]['description'][:55]}", fill="#2C3E50", font=FONT_SM)

        img_url = upload_pil(img, f"machine_{i}")
        grade = random.choice([5, 6, 7, 8])
        diff = difficulty_for_grade(grade)
        expl = f"{correct}. {tmpl[0]}"
        ok = post_question("Science", grade, diff, "Simple Machines", "Types of Simple Machines",
                           question_text, img_url, opts, cidx, expl)
        status = "posted" if ok else ("skip" if SKIPPED > 0 else "fail")
        print(f"  machine_{i}... -> {status}")
        time.sleep(0.3)
        q_count += 1

    print(f"  Done: {q_count} simple machine questions\n")


# ══════════════════════════════════════════════════════════════════════════════
# 2. STATES OF MATTER
# ══════════════════════════════════════════════════════════════════════════════

def draw_particles(state, label=True):
    """Draw particle arrangement for Solid, Liquid, or Gas."""
    img, draw = make_img(400, 360, "#FAFAFA")
    title = f"State of Matter: {state}"
    draw.text((200 - len(title)*5, 12), title, fill="#2C3E50", font=FONT_MD)

    container_x1, container_y1 = 60, 60
    container_x2, container_y2 = 340, 300
    draw.rectangle([container_x1, container_y1, container_x2, container_y2],
                   outline="#7F8C8D", width=3)

    r = 14
    particle_color = {"Solid": "#3498DB", "Liquid": "#27AE60", "Gas": "#E74C3C"}[state]

    if state == "Solid":
        # Tightly packed grid
        positions = []
        for row in range(5):
            for col in range(5):
                x = 110 + col * 44
                y = 95 + row * 40
                positions.append((x, y))
        for x, y in positions:
            draw.ellipse([x-r, y-r, x+r, y+r], fill=particle_color, outline="#2C3E50")
        if label:
            draw.text((130, 310), "Tightly packed, regular arrangement", fill="#2C3E50", font=FONT_SM)

    elif state == "Liquid":
        # Close but irregular
        positions = [
            (110,100),(155,90),(200,105),(245,95),(290,100),
            (120,148),(165,140),(210,155),(258,143),(300,150),
            (105,195),(155,188),(205,200),(250,190),(295,195),
            (115,240),(160,235),(210,248),(255,238),(295,242),
        ]
        for x, y in positions:
            draw.ellipse([x-r, y-r, x+r, y+r], fill=particle_color, outline="#2C3E50")
        if label:
            draw.text((110, 310), "Close together, random arrangement", fill="#2C3E50", font=FONT_SM)

    else:  # Gas
        # Spread out randomly
        positions = [
            (100, 90),(220,75),(310,100),(85,160),(180,140),
            (300,155),(130,220),(250,210),(330,230),(105,270),
            (200,265),(305,280),
        ]
        for x, y in positions:
            draw.ellipse([x-r, y-r, x+r, y+r], fill=particle_color, outline="#2C3E50")
            # Motion arrows
            ax = x + random.choice([-1,1]) * 25
            ay = y + random.choice([-1,1]) * 18
            draw.line([(x,y),(ax,ay)], fill="#E74C3C", width=2)
        if label:
            draw.text((120, 310), "Far apart, random fast motion", fill="#2C3E50", font=FONT_SM)

    return img

def draw_state_change_diagram(highlight=None):
    """Draw state change arrows: Solid <-> Liquid <-> Gas."""
    img, draw = make_img(520, 320, "#FAFAFA")
    draw.text((150, 12), "Changes of State of Matter", fill="#2C3E50", font=FONT_LG)
    # Three boxes
    boxes = {"Solid": (60, 140), "Liquid": (220, 140), "Gas": (380, 140)}
    colors = {"Solid": "#3498DB", "Liquid": "#27AE60", "Gas": "#E74C3C"}
    for name, (bx, by) in boxes.items():
        c = colors[name]
        draw.rectangle([bx-40, by-28, bx+40, by+28], fill=c)
        draw.text((bx-20, by-10), name, fill="white", font=FONT_MD)
    # Arrows Solid->Liquid
    draw.line([(108, 132), (172, 132)], fill="#F39C12", width=3)
    draw.polygon([(176, 132),(166,126),(166,138)], fill="#F39C12")
    draw.text((118, 108), "Melting", fill="#F39C12", font=FONT_SM)
    # Liquid->Solid
    draw.line([(172, 152), (108, 152)], fill="#8E44AD", width=3)
    draw.polygon([(104,152),(114,146),(114,158)], fill="#8E44AD")
    draw.text((110, 158), "Freezing", fill="#8E44AD", font=FONT_SM)
    # Liquid->Gas
    draw.line([(268, 132), (332, 132)], fill="#F39C12", width=3)
    draw.polygon([(336,132),(326,126),(326,138)], fill="#F39C12")
    draw.text((275, 108), "Vaporisation", fill="#F39C12", font=FONT_SM)
    # Gas->Liquid
    draw.line([(332, 152), (268, 152)], fill="#8E44AD", width=3)
    draw.polygon([(264,152),(274,146),(274,158)], fill="#8E44AD")
    draw.text((268, 158), "Condensation", fill="#8E44AD", font=FONT_SM)
    # Solid->Gas (sublimation)
    draw.arc([60, 60, 420, 200], start=200, end=340, fill="#E67E22", width=2)
    draw.text((195, 55), "Sublimation", fill="#E67E22", font=FONT_SM)
    return img

MATTER_QA = [
    ("What is the arrangement of particles in a solid?",
     "Tightly packed in regular arrangement",
     ["Randomly arranged far apart", "Close together but random", "Moving freely in all directions"], "Solid"),
    ("In which state of matter do particles move the fastest?",
     "Gas",
     ["Solid", "Liquid", "Plasma"], None),
    ("Which state of matter takes the shape of its container but has a fixed volume?",
     "Liquid",
     ["Solid", "Gas", "Plasma"], "Liquid"),
    ("What is the process of converting a solid directly to gas called?",
     "Sublimation",
     ["Evaporation", "Condensation", "Melting"], None),
    ("Which state of matter has the strongest intermolecular forces?",
     "Solid",
     ["Liquid", "Gas", "They are equal in all states"], "Solid"),
    ("What happens to particles when a liquid is heated to its boiling point?",
     "They gain enough energy to escape as gas",
     ["They slow down", "They become more tightly packed", "They change colour"], "Gas"),
    ("Which change of state is the reverse of condensation?",
     "Vaporisation",
     ["Melting", "Freezing", "Sublimation"], None),
    ("In which state do particles vibrate in fixed positions?",
     "Solid",
     ["Liquid", "Gas", "All states"], "Solid"),
    ("What is the process of gas turning into liquid called?",
     "Condensation",
     ["Freezing", "Sublimation", "Evaporation"], None),
    ("Which state of matter fills the entire volume of its container?",
     "Gas",
     ["Solid", "Liquid", "Colloid"], "Gas"),
    ("Dry ice (solid CO₂) turning into gas is an example of:",
     "Sublimation",
     ["Melting", "Evaporation", "Condensation"], None),
    ("What is the freezing point of water?",
     "0°C",
     ["100°C", "4°C", "-10°C"], None),
    ("In a liquid, particles are:",
     "Close together but can flow past each other",
     ["Far apart and move freely", "Fixed in a regular grid", "Vibrating on the spot only"], "Liquid"),
    ("Which process absorbs heat energy?",
     "Melting",
     ["Freezing", "Condensation", "Deposition"], None),
    ("The boiling point of water at sea level is:",
     "100°C",
     ["0°C", "50°C", "212°F only"], None),
    ("Which state of matter is least compressible?",
     "Solid",
     ["Liquid", "Gas", "All are equally compressible"], "Solid"),
    ("What change of state occurs when you cool water vapour?",
     "Condensation",
     ["Evaporation", "Sublimation", "Melting"], None),
    ("Plasma is sometimes called the fourth state of matter. It is mostly found in:",
     "Stars and the Sun",
     ["Ice", "Oceans", "Rocks"], None),
    ("What is the process of liquid turning into solid at freezing point?",
     "Solidification / Freezing",
     ["Condensation", "Sublimation", "Evaporation"], None),
    ("Which state of matter has a definite shape and definite volume?",
     "Solid",
     ["Liquid", "Gas", "Plasma"], "Solid"),
]

def gen_states_of_matter(n=QPT):
    print(f"[States of Matter] {n} questions...")
    for i, (qtext, correct, wrongs, draw_state) in enumerate(MATTER_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts)
        cidx = opts.index(correct)
        if draw_state:
            img = draw_particles(draw_state, label=True)
        else:
            img = draw_state_change_diagram()
        img_url = upload_pil(img, f"matter_{i}")
        grade = random.choice([4, 5, 6, 7])
        diff = difficulty_for_grade(grade)
        expl = f"Answer: {correct}. {qtext}"
        ok = post_question("Science", grade, diff, "States of Matter", "Particle Theory",
                           qtext, img_url, opts, cidx, expl)
        status = "posted" if ok else "skip/fail"
        print(f"  matter_{i}... -> {status}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 3. FOOD WEB
# ══════════════════════════════════════════════════════════════════════════════

FOOD_WEBS = [
    {
        "name": "Grassland",
        "organisms": ["Grass", "Grasshopper", "Frog", "Snake", "Eagle",
                      "Rabbit", "Fox", "Deer", "Lion"],
        "links": [("Grass","Grasshopper"),("Grass","Rabbit"),("Grass","Deer"),
                  ("Grasshopper","Frog"),("Frog","Snake"),("Snake","Eagle"),
                  ("Rabbit","Fox"),("Deer","Lion")],
        "producers": ["Grass"],
        "top_pred": ["Eagle", "Lion"],
    },
    {
        "name": "Ocean",
        "organisms": ["Phytoplankton", "Zooplankton", "Small Fish", "Large Fish", "Shark", "Seal"],
        "links": [("Phytoplankton","Zooplankton"),("Zooplankton","Small Fish"),
                  ("Small Fish","Large Fish"),("Large Fish","Shark"),("Large Fish","Seal")],
        "producers": ["Phytoplankton"],
        "top_pred": ["Shark"],
    },
    {
        "name": "Forest",
        "organisms": ["Oak Tree", "Caterpillar", "Sparrow", "Hawk",
                      "Mouse", "Owl", "Mushroom"],
        "links": [("Oak Tree","Caterpillar"),("Oak Tree","Mouse"),
                  ("Caterpillar","Sparrow"),("Sparrow","Hawk"),
                  ("Mouse","Owl"),("Mushroom","Mouse")],
        "producers": ["Oak Tree", "Mushroom"],
        "top_pred": ["Hawk", "Owl"],
    },
]

def draw_food_web(web_data, highlight_org=None):
    img, draw = make_img(540, 400, "#F0FFF0")
    draw.text((10, 10), f"Food Web: {web_data['name']}", fill="#2C3E50", font=FONT_LG)

    orgs = web_data["organisms"]
    links = web_data["links"]
    n = len(orgs)

    # Position organisms in a loose grid
    positions = {}
    cols = 4
    for i, org in enumerate(orgs):
        col = i % cols
        row = i // cols
        x = 80 + col * 115
        y = 80 + row * 95
        positions[org] = (x, y)

    # Draw links
    for (src, dst) in links:
        if src in positions and dst in positions:
            x1, y1 = positions[src]
            x2, y2 = positions[dst]
            draw.line([(x1, y1), (x2, y2)], fill="#AED6F1", width=2)
            # Arrowhead
            dx, dy = x2 - x1, y2 - y1
            length = max(1, math.sqrt(dx*dx + dy*dy))
            ux, uy = dx/length, dy/length
            ax = x2 - ux*18; ay = y2 - uy*18
            draw.polygon([(x2, y2),
                           (int(ax - uy*8), int(ay + ux*8)),
                           (int(ax + uy*8), int(ay - ux*8))], fill="#5DADE2")

    # Draw organisms
    for org, (x, y) in positions.items():
        is_prod = org in web_data["producers"]
        is_top  = org in web_data["top_pred"]
        is_high = org == highlight_org
        if is_high:
            color = "#F39C12"
        elif is_prod:
            color = "#27AE60"
        elif is_top:
            color = "#E74C3C"
        else:
            color = "#3498DB"
        draw.ellipse([x-38, y-18, x+38, y+18], fill=color, outline="#2C3E50")
        tw = len(org) * 7
        draw.text((x - tw//2, y - 9), org, fill="white", font=FONT_SM)

    draw.text((10, 370), "Green=Producer  Blue=Consumer  Red=Top Predator", fill="#555", font=FONT_SM)
    return img

FOOD_WEB_QA = [
    ("In a grassland food web, which organism is the producer?",
     "Grass", ["Grasshopper", "Frog", "Eagle"], 0),
    ("In the food web shown, which organism is the top predator?",
     "Eagle", ["Snake", "Frog", "Grasshopper"], 0),
    ("What would happen to the frog population if all snakes were removed?",
     "Frog population would increase", ["Frog population would decrease", "No effect on frogs", "Frogs would become producers"], 0),
    ("In an ocean food web, phytoplankton are classified as:",
     "Producers", ["Primary consumers", "Secondary consumers", "Decomposers"], 0),
    ("A food web differs from a food chain because:",
     "It shows multiple feeding relationships",
     ["It only shows one straight chain", "It has fewer organisms", "It does not include producers"], 0),
    ("Which trophic level do herbivores belong to?",
     "Primary consumers", ["Producers", "Secondary consumers", "Decomposers"], 0),
    ("In the forest food web shown, what do caterpillars feed on?",
     "Oak Tree", ["Sparrow", "Hawk", "Mushroom"], 0),
    ("If the mouse population in the forest web collapses, which organism is most affected?",
     "Owl", ["Hawk", "Oak Tree", "Caterpillar"], 0),
    ("What is the source of all energy in a food web?",
     "Sun / Sunlight", ["Soil", "Water", "Decomposers"], 0),
    ("Decomposers in a food web break down:",
     "Dead organisms and return nutrients to soil",
     ["Living plants", "Solar energy", "Water molecules"], 0),
    ("Which term describes an organism that eats both plants and animals?",
     "Omnivore", ["Herbivore", "Carnivore", "Decomposer"], 0),
    ("In an ocean food web, what do zooplankton feed on?",
     "Phytoplankton", ["Small fish", "Sharks", "Seals"], 0),
    ("The arrows in a food web diagram show:",
     "Direction of energy transfer", ["Direction of water flow", "Who eats whom (victim to predator reversed)", "Movement of animals"], 0),
    ("Which organism has the most energy in any food web?",
     "Producers (plants)", ["Top predators", "Primary consumers", "Secondary consumers"], 0),
    ("Removing a keystone species from a food web would most likely:",
     "Cause collapse of the entire web",
     ["Have no effect", "Only affect one level", "Increase overall biodiversity"], 0),
    ("In the grassland food web, what does a rabbit eat?",
     "Grass", ["Grasshopper", "Fox", "Frog"], 0),
    ("Which level of a food pyramid has the most biomass?",
     "Producers (base)", ["Primary consumers", "Top predators", "Decomposers"], 0),
    ("A shark in the ocean food web is a:",
     "Top predator (tertiary consumer)",
     ["Producer", "Primary consumer", "Decomposer"], 0),
    ("What type of relationship exists between a frog and a snake in the food web?",
     "Predator-prey (snake eats frog)",
     ["Mutualism", "Commensalism", "Competition"], 0),
    ("If phytoplankton disappeared from the ocean, what would happen to fish?",
     "Fish population would eventually collapse",
     ["Fish would thrive", "Fish would switch to eating rocks", "No change"], 0),
]

def gen_food_web(n=QPT):
    print(f"[Food Web] {n} questions...")
    web_cycle = [FOOD_WEBS[i % len(FOOD_WEBS)] for i in range(n)]
    for i, (qa, web) in enumerate(zip(FOOD_WEB_QA[:n], web_cycle)):
        qtext, correct, wrongs, _ = qa
        opts = [correct] + wrongs
        random.shuffle(opts)
        cidx = opts.index(correct)
        img = draw_food_web(web)
        img_url = upload_pil(img, f"foodweb_{i}")
        grade = random.choice([5, 6, 7, 8])
        diff = difficulty_for_grade(grade)
        expl = f"Answer: {correct}."
        ok = post_question("Science", grade, diff, "Food Web", "Ecological Relationships",
                           qtext, img_url, opts, cidx, expl)
        status = "posted" if ok else "skip/fail"
        print(f"  foodweb_{i}... -> {status}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 4. HUMAN BODY SYSTEMS
# ══════════════════════════════════════════════════════════════════════════════

def draw_body_system(system_name):
    img, draw = make_img(480, 400, "#FFF9F0")
    draw.text((20, 12), f"Human Body: {system_name}", fill="#2C3E50", font=FONT_LG)

    if system_name == "Skeletal System":
        # Simple stick figure with key bones labeled
        # Skull
        draw.ellipse([210, 50, 270, 100], outline="#7F8C8D", width=3)
        draw.text((218, 68), "Skull", fill="#E74C3C", font=FONT_SM)
        # Spine
        for y in range(105, 230, 12):
            draw.rectangle([237, y, 243, y+9], fill="#7F8C8D")
        draw.text((248, 155), "Spine", fill="#E74C3C", font=FONT_SM)
        # Ribs
        for rib in range(4):
            ry = 120 + rib * 22
            draw.arc([200, ry, 280, ry+18], start=0, end=180, fill="#7F8C8D", width=2)
        # Arms
        draw.line([(240, 108), (170, 170)], fill="#7F8C8D", width=4)
        draw.line([(240, 108), (310, 170)], fill="#7F8C8D", width=4)
        draw.text((145, 175), "Humerus", fill="#2980B9", font=FONT_SM)
        # Legs
        draw.line([(240, 225), (210, 320)], fill="#7F8C8D", width=5)
        draw.line([(240, 225), (270, 320)], fill="#7F8C8D", width=5)
        draw.line([(210, 320), (195, 390)], fill="#7F8C8D", width=4)
        draw.line([(270, 320), (285, 390)], fill="#7F8C8D", width=4)
        draw.text((150, 340), "Femur", fill="#2980B9", font=FONT_SM)
        # Pelvis
        draw.arc([200, 210, 280, 250], start=0, end=180, fill="#7F8C8D", width=4)
        draw.text((285, 220), "Pelvis", fill="#E74C3C", font=FONT_SM)

    elif system_name == "Digestive System":
        # Mouth -> oesophagus -> stomach -> intestines
        draw.ellipse([200, 50, 280, 80], fill="#E8C4A0", outline="#8B6914")
        draw.text((216, 58), "Mouth", fill="#2C3E50", font=FONT_SM)
        # Oesophagus
        draw.rectangle([232, 82, 248, 145], fill="#F0A070")
        draw.text((252, 105), "Oesophagus", fill="#2C3E50", font=FONT_SM)
        # Stomach
        stomach = [(220,148),(200,165),(195,200),(210,225),(250,228),(270,210),(268,165),(248,148)]
        draw.polygon(stomach, fill="#E74C3C", outline="#8B0000")
        draw.text((175, 190), "Stomach", fill="#8B0000", font=FONT_SM)
        # Small intestine (coiled)
        for loop in range(4):
            lx = 180 + loop * 8
            ly = 240 + loop * 20
            draw.arc([lx, ly, lx+140, ly+22], start=0, end=180, fill="#F39C12", width=4)
            draw.arc([lx+10, ly+20, lx+145, ly+42], start=180, end=360, fill="#F39C12", width=4)
        draw.text((340, 250), "Small\nIntestine", fill="#F39C12", font=FONT_SM)
        # Large intestine
        draw.arc([150, 235, 340, 345], start=0, end=270, fill="#E67E22", width=6)
        draw.text((330, 290), "Large\nIntestine", fill="#E67E22", font=FONT_SM)

    elif system_name == "Respiratory System":
        # Nose, trachea, lungs
        draw.ellipse([215, 45, 265, 90], fill="#FFDDC1", outline="#8B6914")
        draw.text((208, 95), "Nasal cavity", fill="#2C3E50", font=FONT_SM)
        # Trachea
        draw.rectangle([232, 92, 248, 165], fill="#AED6F1")
        draw.text((252, 120), "Trachea", fill="#2980B9", font=FONT_SM)
        # Bronchi
        draw.line([(240, 165), (195, 195)], fill="#AED6F1", width=5)
        draw.line([(240, 165), (285, 195)], fill="#AED6F1", width=5)
        # Left lung
        left_lung = [(140,200),(120,230),(115,280),(130,330),(170,345),(195,330),(200,280),(190,220)]
        draw.polygon(left_lung, fill="#FFB6C1", outline="#C0392B")
        draw.text((125, 270), "Left\nLung", fill="#C0392B", font=FONT_SM)
        # Right lung
        right_lung = [(285,200),(300,225),(305,280),(295,335),(265,345),(245,325),(240,280),(250,215)]
        draw.polygon(right_lung, fill="#FFB6C1", outline="#C0392B")
        draw.text((290, 270), "Right\nLung", fill="#C0392B", font=FONT_SM)
        # Diaphragm
        draw.arc([110, 330, 370, 380], start=0, end=180, fill="#7F8C8D", width=5)
        draw.text((200, 365), "Diaphragm", fill="#7F8C8D", font=FONT_SM)

    elif system_name == "Circulatory System":
        # Heart and major vessels
        heart = [(240,160),(205,130),(185,155),(185,185),(240,220),(295,185),(295,155),(275,130)]
        draw.polygon(heart, fill="#E74C3C", outline="#8B0000")
        draw.text((218, 170), "Heart", fill="white", font=FONT_SM)
        # Aorta
        draw.line([(240, 140), (240, 70)], fill="#E74C3C", width=6)
        draw.text((245, 65), "Aorta", fill="#E74C3C", font=FONT_SM)
        # Veins
        draw.line([(240, 140), (180, 70)], fill="#3498DB", width=4)
        draw.text((120, 60), "Vena Cava", fill="#3498DB", font=FONT_SM)
        # Body circulation lines
        draw.line([(295, 175), (370, 175), (370, 320), (240, 320)], fill="#E74C3C", width=3)
        draw.line([(240, 320), (110, 320), (110, 175), (185, 175)], fill="#3498DB", width=3)
        draw.text((345, 240), "Arteries\n(oxygenated)", fill="#E74C3C", font=FONT_SM)
        draw.text((80, 240), "Veins\n(deoxygenated)", fill="#3498DB", font=FONT_SM)
        # Pulmonary
        draw.arc([190, 65, 290, 140], start=30, end=150, fill="#9B59B6", width=3)
        draw.text((168, 82), "Pulmonary\ncirculation", fill="#9B59B6", font=FONT_SM)

    else:  # Generic
        draw.text((50, 80), f"The {system_name}", fill="#2C3E50", font=FONT_XL)
        draw.text((50, 130), "works to maintain body functions.", fill="#555", font=FONT_MD)

    return img

BODY_SYSTEM_QA = [
    ("Which organ pumps blood throughout the body?",
     "Heart", ["Lungs", "Liver", "Kidney"], "Circulatory System"),
    ("The main function of the respiratory system is to:",
     "Exchange oxygen and carbon dioxide",
     ["Digest food", "Filter blood", "Transmit nerve signals"], "Respiratory System"),
    ("Which organ produces bile to help digest fats?",
     "Liver", ["Stomach", "Kidney", "Pancreas"], "Digestive System"),
    ("How many bones are in an adult human body?",
     "206", ["108", "306", "156"], "Skeletal System"),
    ("The femur is the bone of the:",
     "Upper leg (thigh)", ["Upper arm", "Lower leg", "Forearm"], "Skeletal System"),
    ("Which muscle separates the chest cavity from the abdominal cavity?",
     "Diaphragm", ["Intercostal", "Abdominal", "Pectoral"], "Respiratory System"),
    ("Where does most digestion and nutrient absorption take place?",
     "Small intestine", ["Stomach", "Large intestine", "Liver"], "Digestive System"),
    ("What do red blood cells carry?",
     "Oxygen", ["Nutrients", "Hormones", "Antibodies"], "Circulatory System"),
    ("Which blood vessels carry blood AWAY from the heart?",
     "Arteries", ["Veins", "Capillaries", "Ventricles"], "Circulatory System"),
    ("The trachea is part of which body system?",
     "Respiratory System", ["Digestive System", "Skeletal System", "Circulatory System"], "Respiratory System"),
    ("Which organ filters waste products from the blood?",
     "Kidney", ["Liver", "Spleen", "Pancreas"], "Circulatory System"),
    ("The large intestine mainly:",
     "Absorbs water and forms faeces",
     ["Digests proteins", "Produces enzymes", "Stores bile"], "Digestive System"),
    ("Which type of joints allow the widest range of movement?",
     "Ball-and-socket joints", ["Hinge joints", "Fixed joints", "Pivot joints"], "Skeletal System"),
    ("What is the name of the pipe connecting the mouth to the stomach?",
     "Oesophagus", ["Trachea", "Bronchus", "Intestine"], "Digestive System"),
    ("Oxygenated blood is carried from the lungs to the heart by the:",
     "Pulmonary vein", ["Pulmonary artery", "Aorta", "Vena cava"], "Circulatory System"),
    ("Which organ in the respiratory system exchanges gases?",
     "Alveoli in the lungs", ["Heart", "Diaphragm", "Trachea"], "Respiratory System"),
    ("Cartilage is a type of connective tissue found in joints that:",
     "Reduces friction between bones",
     ["Produces blood cells", "Contracts to create movement", "Stores minerals"], "Skeletal System"),
    ("The enzyme amylase begins breaking down which nutrient in the mouth?",
     "Starch (carbohydrates)", ["Proteins", "Fats", "Vitamins"], "Digestive System"),
    ("Platelets in the blood help with:",
     "Clotting to stop bleeding",
     ["Carrying oxygen", "Fighting infection", "Carrying hormones"], "Circulatory System"),
    ("When you inhale, the diaphragm:",
     "Contracts and moves downward",
     ["Relaxes and moves up", "Stays still", "Pushes air out"], "Respiratory System"),
]

def gen_body_systems(n=QPT):
    print(f"[Human Body Systems] {n} questions...")
    for i, (qtext, correct, wrongs, sys_name) in enumerate(BODY_SYSTEM_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts)
        cidx = opts.index(correct)
        img = draw_body_system(sys_name)
        img_url = upload_pil(img, f"body_{i}")
        grade = random.choice([6, 7, 8, 9])
        diff = difficulty_for_grade(grade)
        expl = f"Answer: {correct}."
        ok = post_question("Science", grade, diff, sys_name, "Human Body",
                           qtext, img_url, opts, cidx, expl)
        status = "posted" if ok else "skip/fail"
        print(f"  body_{i} ({sys_name})... -> {status}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 5. PLANT PARTS
# ══════════════════════════════════════════════════════════════════════════════

def draw_plant(highlight_part=None):
    img, draw = make_img(440, 420, "#F0FFF4")
    draw.text((20, 10), "Parts of a Plant", fill="#2C3E50", font=FONT_LG)
    # Roots
    root_color = "#E74C3C" if highlight_part == "Root" else "#8B6914"
    for i in range(5):
        angle = -40 + i * 20
        rad = math.radians(angle)
        ex = 220 + int(60 * math.sin(rad))
        ey = 390 + int(60 * math.cos(rad))
        draw.line([(220, 335), (ex, ey)], fill=root_color, width=3)
    draw.text((275, 365), "Root", fill=root_color, font=FONT_MD)
    # Stem
    stem_color = "#27AE60" if highlight_part == "Stem" else "#5D4037"
    draw.rectangle([213, 200, 227, 335], fill=stem_color)
    draw.text((235, 255), "Stem", fill=stem_color, font=FONT_MD)
    # Leaves
    for side, lx, ly in [(-1, 155, 255), (1, 270, 220), (-1, 140, 195)]:
        leaf_color = "#27AE60" if highlight_part == "Leaf" else "#2ECC71"
        pts = [(220, ly), (lx, ly - 30), (lx + side*30, ly + 10), (220, ly)]
        draw.polygon(pts, fill=leaf_color, outline="#1A8A40")
    draw.text((95, 230), "Leaf", fill="#27AE60" if highlight_part=="Leaf" else "#1A8A40", font=FONT_MD)
    # Flower
    flower_color = "#E74C3C" if highlight_part == "Flower" else "#FF69B4"
    petal_offsets = [(0,-30),(25,-20),(25,10),(0,25),(-25,10),(-25,-20)]
    for dx, dy in petal_offsets:
        draw.ellipse([220+dx-14, 145+dy-10, 220+dx+14, 145+dy+10], fill=flower_color)
    draw.ellipse([208, 135, 232, 160], fill="#F1C40F")  # Center
    draw.text((240, 130), "Flower", fill=flower_color, font=FONT_MD)
    # Fruit
    if highlight_part == "Fruit":
        draw.ellipse([195, 155, 245, 200], fill="#FF8C00")
        draw.text((248, 172), "Fruit", fill="#FF8C00", font=FONT_MD)
    return img

PLANT_QA = [
    ("Which part of the plant absorbs water and minerals from the soil?",
     "Root", ["Stem", "Leaf", "Flower"]),
    ("What is the main function of leaves in a plant?",
     "Photosynthesis (making food using sunlight)",
     ["Absorbing water", "Reproducing", "Supporting the plant"]),
    ("Which part of the plant transports water from roots to leaves?",
     "Stem", ["Flower", "Fruit", "Root"]),
    ("The colourful part of a flower that attracts insects is called:",
     "Petals", ["Sepals", "Stamens", "Pistil"]),
    ("Where are seeds found in a flowering plant?",
     "Inside the fruit", ["In the roots", "On the stem", "In the leaves"]),
    ("Chlorophyll is the green pigment in leaves that helps to:",
     "Absorb sunlight for photosynthesis",
     ["Absorb water", "Store starch", "Attract insects"]),
    ("Which part of the flower contains pollen?",
     "Anther (part of stamen)", ["Pistil", "Petal", "Sepal"]),
    ("The process by which plants make their own food is called:",
     "Photosynthesis", ["Respiration", "Transpiration", "Germination"]),
    ("Stomata are tiny pores found in leaves that allow:",
     "Gas exchange (CO₂ in, O₂ out)",
     ["Water absorption", "Seed dispersal", "Mineral absorption"]),
    ("Which plant organ anchors the plant and stores food in some plants?",
     "Root", ["Stem", "Leaf", "Flower"]),
    ("The green parts of a plant contain chloroplasts which carry out:",
     "Photosynthesis", ["Digestion", "Respiration only", "Transpiration only"]),
    ("What gas do plants release during photosynthesis?",
     "Oxygen", ["Carbon dioxide", "Nitrogen", "Hydrogen"]),
    ("Transpiration is the process by which plants:",
     "Lose water vapour through leaves",
     ["Absorb water through roots", "Make food", "Produce flowers"]),
    ("Which part develops from the ovule after fertilisation?",
     "Seed", ["Fruit", "Petal", "Leaf"]),
    ("Xylem tissue in a plant carries:",
     "Water and minerals upward",
     ["Sugars downward", "Oxygen to cells", "Waste to roots"]),
]

def gen_plant_parts(n=QPT):
    n = min(n, len(PLANT_QA))
    print(f"[Plant Parts] {n} questions...")
    parts_cycle = ["Root","Stem","Leaf","Flower","Fruit",None]
    for i, (qtext, correct, wrongs) in enumerate(PLANT_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts)
        cidx = opts.index(correct)
        highlight = parts_cycle[i % len(parts_cycle)]
        img = draw_plant(highlight)
        img_url = upload_pil(img, f"plant_{i}")
        grade = random.choice([3, 4, 5, 6])
        diff = difficulty_for_grade(grade)
        expl = f"Answer: {correct}."
        ok = post_question("Science", grade, diff, "Plant Biology", "Parts of a Plant",
                           qtext, img_url, opts, cidx, expl)
        status = "posted" if ok else "skip/fail"
        print(f"  plant_{i}... -> {status}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 6. TYPES OF TRIANGLES + ANGLES
# ══════════════════════════════════════════════════════════════════════════════

def draw_triangle_types():
    img, draw = make_img(540, 420, "#FAFAFA")
    draw.text((160, 10), "Types of Triangles", fill="#2C3E50", font=FONT_LG)

    types = [
        ("Equilateral", [(80,320),(180,140),(280,320)], "#3498DB",
         "All 3 sides equal\nAll angles = 60°"),
        ("Isosceles", [(330,320),(430,150),(510,320)], "#27AE60",
         "2 equal sides\n2 equal angles"),
    ]
    row2 = [
        ("Scalene", [(60,410),(200,240),(320,410)], "#E74C3C",
         "No equal sides\nNo equal angles"),
        ("Right-angled", [(350,410),(350,240),(510,410)], "#9B59B6",
         "One angle = 90°"),
    ]

    # Row 1
    for (name, pts, color, desc) in types:
        draw.polygon(pts, fill=color, outline="#2C3E50")
        bx = sum(p[0] for p in pts)//3
        by = sum(p[1] for p in pts)//3
        draw.text((bx-20, by-8), name, fill="white", font=FONT_SM)

    return img

def draw_single_triangle(tri_type):
    img, draw = make_img(380, 300, "#F8F9FA")
    draw.text((20, 12), f"Triangle: {tri_type}", fill="#2C3E50", font=FONT_LG)
    colors = {"Equilateral":"#3498DB","Isosceles":"#27AE60","Scalene":"#E74C3C","Right-angled":"#9B59B6","Obtuse":"#F39C12"}
    c = colors.get(tri_type, "#7F8C8D")
    if tri_type == "Equilateral":
        pts = [(190, 60), (80, 250), (300, 250)]
        for i, (p1, p2) in enumerate([(pts[0],pts[1]),(pts[1],pts[2]),(pts[0],pts[2])]):
            mid = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)
            draw.text((mid[0]-5, mid[1]), "=", fill="white", font=FONT_MD)
    elif tri_type == "Isosceles":
        pts = [(190, 60), (80, 260), (300, 260)]
    elif tri_type == "Right-angled":
        pts = [(80, 60), (80, 260), (300, 260)]
    elif tri_type == "Scalene":
        pts = [(120, 70), (60, 260), (320, 260)]
    elif tri_type == "Obtuse":
        pts = [(100, 260), (380, 260), (130, 120)]
    else:
        pts = [(190, 60), (80, 260), (300, 260)]
    draw.polygon(pts, fill=c, outline="#2C3E50")
    # Right angle mark
    if tri_type == "Right-angled":
        draw.rectangle([80, 240, 100, 260], outline="white", width=2)
    # Label vertices
    labels = ["A", "B", "C"]
    for (px,py), lbl in zip(pts, labels):
        draw.text((px-8, py-12), lbl, fill="white", font=FONT_MD)
    return img

TRIANGLE_QA = [
    ("A triangle with all three sides equal is called:",
     "Equilateral triangle", ["Isosceles triangle", "Scalene triangle", "Right-angled triangle"]),
    ("A triangle with exactly two equal sides is called:",
     "Isosceles triangle", ["Equilateral triangle", "Scalene triangle", "Obtuse triangle"]),
    ("A triangle with no equal sides is called:",
     "Scalene triangle", ["Isosceles triangle", "Equilateral triangle", "Acute triangle"]),
    ("A right-angled triangle has one angle equal to:",
     "90°", ["60°", "45°", "180°"]),
    ("The sum of all interior angles of a triangle is always:",
     "180°", ["90°", "270°", "360°"]),
    ("An acute triangle is one where all angles are:",
     "Less than 90°", ["Greater than 90°", "Exactly 90°", "Equal to 180°"]),
    ("An obtuse triangle has one angle that is:",
     "Greater than 90°", ["Equal to 90°", "Less than 90°", "Equal to 180°"]),
    ("In an equilateral triangle, each angle measures:",
     "60°", ["45°", "90°", "120°"]),
    ("Which type of triangle can also be right-angled?",
     "Isosceles (right isosceles triangle)", ["Equilateral", "Obtuse scalene", "Only equilateral"], ),
    ("The longest side of a right-angled triangle, opposite the right angle, is called:",
     "Hypotenuse", ["Adjacent", "Opposite", "Base"]),
    ("An isosceles triangle has base angles that are:",
     "Equal", ["Supplementary", "Complementary", "Always 90°"]),
    ("Which of these is NOT a valid triangle?",
     "Sides 3 cm, 4 cm, 8 cm (violates triangle inequality)",
     ["Sides 3,4,5", "Sides 5,5,5", "Sides 7,8,9"]),
    ("In a scalene triangle, which of the following is true?",
     "All sides are different lengths", ["Two sides are equal", "All angles are equal", "One angle is 90°"]),
    ("The triangle inequality theorem states that:",
     "Sum of any two sides must be greater than the third",
     ["All angles must equal 60°", "The hypotenuse is always 5 cm", "No two sides can be equal"]),
    ("A 3-4-5 triangle is an example of which type?",
     "Right-angled (scalene) triangle", ["Isosceles", "Equilateral", "Obtuse"]),
]

def gen_triangles(n=QPT):
    n = min(n, len(TRIANGLE_QA))
    print(f"[Types of Triangles] {n} questions...")
    tri_types = ["Equilateral","Isosceles","Scalene","Right-angled","Obtuse"]
    for i, (qtext, correct, wrongs) in enumerate(TRIANGLE_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts)
        cidx = opts.index(correct)
        tri_type = tri_types[i % len(tri_types)]
        try:
            img = draw_single_triangle(tri_type)
        except:
            img = draw_triangle_types()
        img_url = upload_pil(img, f"tri_{i}")
        grade = random.choice([4, 5, 6, 7])
        diff = difficulty_for_grade(grade)
        expl = f"Answer: {correct}."
        ok = post_question("Mathematics", grade, diff, "Geometry", "Types of Triangles",
                           qtext, img_url, opts, cidx, expl)
        status = "posted" if ok else "skip/fail"
        print(f"  tri_{i}... -> {status}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 7. ANGLES
# ══════════════════════════════════════════════════════════════════════════════

def draw_angle(degrees, label=True):
    img, draw = make_img(360, 300, "#FAFAFA")
    cx, cy = 100, 220
    r = 140
    # Base ray (horizontal)
    draw.line([(cx, cy), (cx + r, cy)], fill="#2C3E50", width=3)
    # Angled ray
    rad = math.radians(degrees)
    ex = cx + int(r * math.cos(rad))
    ey = cy - int(r * math.sin(rad))
    draw.line([(cx, cy), (ex, ey)], fill="#E74C3C", width=3)
    # Arc
    arc_r = 45
    draw.arc([cx-arc_r, cy-arc_r, cx+arc_r, cy+arc_r], start=0, end=degrees, fill="#3498DB", width=3)
    # Angle label
    mid_angle = math.radians(degrees / 2)
    lx = cx + int((arc_r + 15) * math.cos(mid_angle))
    ly = cy - int((arc_r + 15) * math.sin(mid_angle))
    draw.text((lx, ly), f"{degrees}°", fill="#E74C3C", font=FONT_MD)
    # Vertex label
    draw.text((cx - 15, cy + 5), "O", fill="#2C3E50", font=FONT_MD)
    # Angle type label
    if label:
        if degrees == 90:
            atype = "Right Angle"
            # Draw right angle mark
            draw.rectangle([cx, cy-15, cx+15, cy], outline="#2C3E50", width=2)
        elif degrees < 90:
            atype = "Acute Angle"
        elif degrees < 180:
            atype = "Obtuse Angle"
        elif degrees == 180:
            atype = "Straight Angle"
        elif degrees < 360:
            atype = "Reflex Angle"
        else:
            atype = "Complete Angle"
        draw.text((180, 30), atype, fill="#2C3E50", font=FONT_LG)
    return img

ANGLE_QA = [
    (45, "An angle less than 90° is called:", "Acute angle", ["Obtuse angle", "Right angle", "Reflex angle"]),
    (120, "An angle greater than 90° but less than 180° is:", "Obtuse angle", ["Acute angle", "Right angle", "Straight angle"]),
    (90, "An angle of exactly 90° is called:", "Right angle", ["Acute angle", "Obtuse angle", "Straight angle"]),
    (180, "An angle of exactly 180° is called:", "Straight angle", ["Right angle", "Reflex angle", "Complete angle"]),
    (270, "An angle greater than 180° but less than 360° is:", "Reflex angle", ["Obtuse angle", "Right angle", "Straight angle"]),
    (60, "Two angles that add up to 90° are called:", "Complementary angles", ["Supplementary angles", "Vertical angles", "Reflex angles"]),
    (110, "Two angles that add up to 180° are called:", "Supplementary angles", ["Complementary angles", "Adjacent angles", "Reflex angles"]),
    (360, "A full rotation (complete angle) measures:", "360°", ["180°", "270°", "90°"]),
    (45, "The complement of 45° is:", "45°", ["135°", "90°", "180°"]),
    (70, "The supplement of 70° is:", "110°", ["20°", "70°", "180°"]),
    (30, "An equilateral triangle has each angle equal to:", "60°", ["90°", "45°", "30°"]),
    (135, "The exterior angle of a regular octagon is:", "45°", ["60°", "90°", "135°"]),
    (60, "In a regular hexagon, each interior angle is:", "120°", ["60°", "90°", "150°"]),
    (90, "The angle on a straight line (one side) measures:", "180°", ["90°", "360°", "270°"]),
    (40, "If one angle of a triangle is 90° and another is 40°, the third is:", "50°", ["40°", "60°", "70°"]),
    (50, "Vertically opposite angles formed when two lines cross are:", "Equal", ["Supplementary", "Complementary", "Reflex"]),
    (130, "An exterior angle of a triangle equals:", "Sum of the two non-adjacent interior angles", ["180° minus the exterior angle", "90°", "The adjacent interior angle"]),
    (80, "The interior angles of a quadrilateral always sum to:", "360°", ["180°", "270°", "720°"]),
    (72, "The exterior angle of a regular pentagon is:", "72°", ["60°", "45°", "108°"]),
    (108, "The interior angle of a regular pentagon is:", "108°", ["72°", "120°", "90°"]),
]

def gen_angles(n=QPT):
    n = min(n, len(ANGLE_QA))
    print(f"[Angles] {n} questions...")
    for i, (deg, qtext, correct, wrongs) in enumerate(ANGLE_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts)
        cidx = opts.index(correct)
        img = draw_angle(deg)
        img_url = upload_pil(img, f"angle_{i}")
        grade = random.choice([4, 5, 6, 7])
        diff = difficulty_for_grade(grade)
        expl = f"Answer: {correct}."
        ok = post_question("Mathematics", grade, diff, "Geometry", "Angles",
                           qtext, img_url, opts, cidx, expl)
        status = "posted" if ok else "skip/fail"
        print(f"  angle_{i} ({deg}°)... -> {status}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 8. NUMBER PATTERNS / SEQUENCES
# ══════════════════════════════════════════════════════════════════════════════

def draw_number_sequence(nums, missing_idx):
    img, draw = make_img(540, 180, "#FAFAFA")
    draw.text((20, 12), "Find the Missing Number", fill="#2C3E50", font=FONT_LG)
    n = len(nums)
    box_w = 72
    start_x = (540 - n * box_w - (n-1) * 10) // 2
    for i, num in enumerate(nums):
        bx = start_x + i * (box_w + 10)
        is_missing = (i == missing_idx)
        fill = "#F39C12" if is_missing else "#3498DB"
        draw.rectangle([bx, 70, bx + box_w, 140], fill=fill, outline="#2C3E50", width=2)
        label = "?" if is_missing else str(num)
        tw = len(label) * 12
        draw.text((bx + box_w//2 - tw//2, 93), label, fill="white", font=FONT_XL)
        if i < n - 1:
            draw.text((bx + box_w + 2, 100), "→", fill="#7F8C8D", font=FONT_MD)
    return img

def gen_number_patterns(n=QPT):
    print(f"[Number Patterns] {n} questions...")

    sequences = [
        # (sequence, missing_idx, rule_desc)
        ([2, 4, 6, 8, 10, 12], 5, "Even numbers +2"),
        ([1, 3, 5, 7, 9, 11], 4, "Odd numbers +2"),
        ([1, 4, 9, 16, 25, 36], 5, "Perfect squares"),
        ([1, 2, 4, 8, 16, 32], 4, "Powers of 2 ×2"),
        ([2, 6, 18, 54, 162], 4, "×3 each time"),
        ([100, 90, 80, 70, 60, 50], 5, "-10 each time"),
        ([1, 1, 2, 3, 5, 8, 13], 5, "Fibonacci sequence"),
        ([5, 10, 20, 40, 80, 160], 5, "×2 each time"),
        ([3, 6, 12, 24, 48, 96], 4, "×2 each time"),
        ([81, 27, 9, 3, 1], 4, "÷3 each time"),
        ([0, 1, 4, 9, 16, 25], 4, "n²: 0,1,4,9,16,25"),
        ([1, 8, 27, 64, 125, 216], 5, "n³: perfect cubes"),
        ([2, 5, 10, 17, 26, 37], 5, "+3,+5,+7,+9... (odd numbers)"),
        ([1, 3, 6, 10, 15, 21], 5, "Triangular numbers"),
        ([7, 14, 21, 28, 35, 42], 5, "Multiples of 7"),
        ([4, 8, 12, 16, 20, 24], 4, "Multiples of 4"),
        ([1, 2, 3, 5, 8, 13, 21], 6, "Fibonacci"),
        ([256, 128, 64, 32, 16, 8], 5, "÷2 each time"),
        ([10, 100, 1000, 10000], 3, "×10 each time"),
        ([500, 250, 125, 62, 31], 4, "÷2 each time (approx)"),
    ]

    for i, (seq, missing_idx, rule) in enumerate(sequences[:n]):
        correct = seq[missing_idx]
        # Generate wrong answers
        diff_val = seq[1] - seq[0] if len(seq) > 1 else 1
        wrong_offsets = random.sample([x for x in [-diff_val, -correct//2, correct+diff_val, correct*2, correct-1, correct+1, correct+3, correct-3] if x != correct and x > 0], 3)
        opts_raw = [str(correct)] + [str(w) for w in wrong_offsets[:3]]
        random.shuffle(opts_raw)
        cidx = opts_raw.index(str(correct))

        # Build display sequence with ? at missing_idx
        display_seq = seq[:missing_idx+1]  # show up to missing
        img = draw_number_sequence(display_seq, missing_idx)
        seq_str = ", ".join(str(x) for x in display_seq[:missing_idx]) + ", ?"
        qtext = f"What is the missing number in the sequence: {seq_str}?"

        img_url = upload_pil(img, f"numseq_{i}")
        grade = random.choice([3, 4, 5, 6, 7, 8])
        diff = difficulty_for_grade(grade)
        expl = f"Answer: {correct}. Pattern: {rule}."
        ok = post_question("Mathematics", grade, diff, "Number Patterns", "Sequences",
                           qtext, img_url, opts_raw, cidx, expl)
        status = "posted" if ok else "skip/fail"
        print(f"  numseq_{i} ({rule})... -> {status}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("OlympiadReady — Science Diagrams & Math Generator Batch 2")
    print("=" * 60)
    print()

    gen_simple_machines(QPT)
    gen_states_of_matter(QPT)
    gen_food_web(QPT)
    gen_body_systems(QPT)
    gen_plant_parts(min(QPT, len(PLANT_QA)))
    gen_triangles(min(QPT, len(TRIANGLE_QA)))
    gen_angles(min(QPT, len(ANGLE_QA)))
    gen_number_patterns(QPT)

    print("=" * 60)
    print(f"DONE — Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}")
    print("=" * 60)
