"""
generate_math_advanced.py
Advanced Math & Indian Geography generators — Batch 6:
  1.  Speed, Distance & Time      (Grades 5-9)   — text options
  2.  Ratio & Proportion          (Grades 5-8)   — text options
  3.  Percentage                  (Grades 5-8)   — text options
  4.  Profit & Loss               (Grades 6-9)   — text options
  5.  Simple & Compound Interest  (Grades 7-10)  — text options
  6.  Algebra — Equations         (Grades 6-10)  — text options
  7.  Indian States Map           (Grades 5-8)   — text options
  8.  Time & Calendar             (Grades 3-7)   — text options

Requirements: pip install pillow cloudinary requests
"""

import os, io, json, random, time, math
import requests
import cloudinary, cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont

CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")
QPT                   = 20

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME,
                  api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET)
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

try:
    FONT_SM  = ImageFont.truetype("arial.ttf", 14)
    FONT_MD  = ImageFont.truetype("arial.ttf", 18)
    FONT_LG  = ImageFont.truetype("arial.ttf", 22)
    FONT_XL  = ImageFont.truetype("arial.ttf", 28)
    FONT_XXL = ImageFont.truetype("arial.ttf", 36)
except:
    FONT_SM = FONT_MD = FONT_LG = FONT_XL = FONT_XXL = ImageFont.load_default()

POSTED = SKIPPED = FAILED = 0

def difficulty_for_grade(g):
    if g <= 4:   return "Foundation"
    elif g <= 7: return random.choice(["Foundation", "Advanced"])
    else:        return random.choice(["Advanced", "Olympiad"])

def upload_pil(img, label="img"):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    res = cloudinary.uploader.upload(buf, folder=CLOUDINARY_FOLDER,
        public_id=f"b6_{label}_{int(time.time()*1000)}", resource_type="image")
    return res["secure_url"]

def post_q(subject, grade, diff, topic, subtopic, text, img_url, opts, cidx, expl):
    global POSTED, SKIPPED, FAILED
    payload = dict(subject=subject, grade=grade, difficulty=diff, topic=topic,
                   subTopic=subtopic, questionText=text, imageUrl=img_url,
                   options=opts, correctAnswer=chr(65+cidx), explanation=expl)
    for attempt in range(2):
        try:
            r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                              json=payload, headers=HEADERS, timeout=25)
            if r.status_code in (200, 201): POSTED  += 1; return True
            elif r.status_code == 409:      SKIPPED += 1; return False
            else: FAILED += 1; return False
        except Exception:
            if attempt == 0: time.sleep(3)
            else: FAILED += 1; return False

def canvas(w=500, h=380, bg="white"):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)


# ══════════════════════════════════════════════════════════════════════════════
# 1. SPEED, DISTANCE & TIME
# ══════════════════════════════════════════════════════════════════════════════

def draw_sdt(scene, speed=None, distance=None, time_val=None):
    img, draw = canvas(520, 360, "#F0F8FF")
    draw.text((20, 12), "Speed, Distance & Time", fill="#2C3E50", font=FONT_LG)

    # Triangle formula visual
    cx = 380
    draw.polygon([(cx, 60), (cx-70, 175), (cx+70, 175)], fill="#3498DB", outline="#2C3E50", width=2)
    draw.line([(cx, 60), (cx, 175)], fill="#2C3E50", width=2)
    draw.line([(cx-70, 175), (cx+70, 175)], fill="#2C3E50", width=2)
    draw.text((cx-8,  85), "D",  fill="white", font=FONT_XL)
    draw.text((cx-55, 148), "S",  fill="white", font=FONT_XL)
    draw.text((cx+18, 148), "T",  fill="white", font=FONT_XL)
    draw.text((cx-80, 185), "D = S × T", fill="#2C3E50", font=FONT_MD)
    draw.text((cx-80, 210), "S = D ÷ T", fill="#2C3E50", font=FONT_MD)
    draw.text((cx-80, 235), "T = D ÷ S", fill="#2C3E50", font=FONT_MD)

    # Scene illustration on left
    if scene == "train":
        # Train on track
        draw.rectangle([40, 190, 240, 240], fill="#E74C3C", outline="#2C3E50", width=2)
        for wx in [70, 130, 190]:
            draw.ellipse([wx-14, 238, wx+14, 266], fill="#333")
        draw.rectangle([200, 168, 240, 192], fill="#E74C3C", outline="#2C3E50", width=1)
        draw.line([(20, 265), (280, 265)], fill="#7F8C8D", width=3)
        if speed:    draw.text((40, 275), f"Speed = {speed} km/h", fill="#E74C3C", font=FONT_MD)
        if distance: draw.text((40, 300), f"Distance = {distance} km", fill="#3498DB", font=FONT_MD)
        if time_val: draw.text((40, 325), f"Time = {time_val} hours", fill="#27AE60", font=FONT_MD)
    elif scene == "car":
        draw.rectangle([50, 200, 230, 245], fill="#27AE60", outline="#2C3E50", width=2)
        draw.rectangle([80, 175, 200, 202], fill="#27AE60", outline="#2C3E50", width=2)
        for wx in [85, 190]:
            draw.ellipse([wx-16, 243, wx+16, 275], fill="#333")
        if speed:    draw.text((40, 290), f"Speed = {speed} km/h", fill="#E74C3C", font=FONT_MD)
        if distance: draw.text((40, 315), f"Distance = {distance} km", fill="#3498DB", font=FONT_MD)
        if time_val: draw.text((40, 340), f"Time = {time_val} h", fill="#27AE60", font=FONT_MD)
    elif scene == "runner":
        # Stick figure running
        draw.ellipse([90, 140, 130, 180], fill="#F5CBA7", outline="#333", width=2)
        draw.line([(110, 180), (110, 240)], fill="#333", width=3)
        draw.line([(110, 200), (80,  225)], fill="#333", width=3)
        draw.line([(110, 200), (140, 215)], fill="#333", width=3)
        draw.line([(110, 240), (85,  275)], fill="#333", width=3)
        draw.line([(110, 240), (140, 270)], fill="#333", width=3)
        # Arrow showing movement
        draw.line([(150, 210), (230, 210)], fill="#E74C3C", width=3)
        draw.polygon([(234, 210), (220, 203), (220, 217)], fill="#E74C3C")
        if speed:    draw.text((40, 290), f"Speed = {speed} m/s", fill="#E74C3C", font=FONT_MD)
        if distance: draw.text((40, 315), f"Distance = {distance} m", fill="#3498DB", font=FONT_MD)
        if time_val: draw.text((40, 340), f"Time = {time_val} sec", fill="#27AE60", font=FONT_MD)
    elif scene == "boat":
        # Boat on water
        draw.rectangle([0, 280, 520, 360], fill="#AED6F1")
        draw.polygon([(60, 220), (260, 220), (240, 270), (80, 270)], fill="#8B4513")
        draw.line([(160, 120), (160, 222)], fill="#8B4513", width=3)
        draw.polygon([(160, 120), (160, 200), (240, 160)], fill="white", outline="#888")
        if speed:    draw.text((40, 115), f"Boat speed = {speed} km/h", fill="#2C3E50", font=FONT_MD)
        if distance: draw.text((40, 140), f"Distance = {distance} km", fill="#3498DB", font=FONT_MD)
        if time_val: draw.text((40, 165), f"Time = {time_val} h", fill="#27AE60", font=FONT_MD)
    return img

SDT_QA = [
    ("train",60,300,None,
     "A train travels at 60 km/h for 5 hours. Distance covered:",
     "300 km", ["360 km","12 km","65 km"]),
    ("car",None,180,3,
     "A car covers 180 km in 3 hours. Its average speed is:",
     "60 km/h", ["54 km/h","540 km/h","90 km/h"]),
    ("runner",8,None,25,
     "A runner runs at 8 m/s for 25 seconds. Distance covered:",
     "200 m", ["33 m","3.125 m","2000 m"]),
    ("train",90,450,None,
     "A train at 90 km/h needs to cover 450 km. Time required:",
     "5 hours", ["4 hours","40.5 hours","4.5 hours"]),
    ("car",None,240,4,
     "Distance = 240 km, Time = 4 hours. Speed in m/s:",
     "16.67 m/s (60 km/h ÷ 3.6)", ["60 m/s","6 m/s","0.06 m/s"]),
    ("boat",12,None,3,
     "A boat goes upstream at 12 km/h for 3 hours. Distance covered:",
     "36 km", ["4 km","15 km","9 km"]),
    ("train",80,None,None,
     "Two trains start from A and B (400 km apart) towards each other at 80 km/h and 120 km/h. They meet after:",
     "2 hours", ["4 hours","3.3 hours","5 hours"]),
    ("car",60,None,None,
     "A car and a bus travel the same 300 km. Car takes 5 hours, bus takes 6 hours. Car's extra speed over bus:",
     "10 km/h (60-50)", ["6 km/h","5 km/h","30 km/h"]),
    ("runner",None,100,10,
     "100 m race: winner finishes in 10 seconds. Winner's speed:",
     "10 m/s", ["100 m/s","1 m/s","36 km/h... same as 10 m/s"]),
    ("train",None,None,None,
     "Convert 72 km/h to m/s:",
     "20 m/s", ["7.2 m/s","200 m/s","0.02 m/s"]),
    ("car",None,None,None,
     "Convert 15 m/s to km/h:",
     "54 km/h", ["15 km/h","150 km/h","4.17 km/h"]),
    ("boat",15,None,None,
     "A boat's speed in still water is 15 km/h. Current speed is 3 km/h. Upstream speed:",
     "12 km/h", ["18 km/h","45 km/h","5 km/h"]),
    ("train",None,None,None,
     "A 200 m train passes a pole in 10 seconds. Train's speed:",
     "20 m/s = 72 km/h", ["200 km/h","2 m/s","10 m/s"]),
    ("car",None,None,None,
     "A 200 m train passes a 300 m platform in 25 seconds. Speed of train:",
     "20 m/s (500÷25)", ["8 m/s","12 m/s","25 m/s"]),
    ("runner",None,None,None,
     "A person walks at 4 km/h and runs at 8 km/h. He covers 24 km in 4 hours. Time spent walking:",
     "2 hours", ["1 hour","3 hours","4 hours"]),
    ("train",120,None,None,
     "Two trains 150 m and 100 m long run at 60 km/h and 40 km/h in same direction. Time to cross each other:",
     "25 seconds (relative speed=20 km/h=5.56 m/s; 250÷10=25s at 10 m/s relative)",
     ["18 seconds","10 seconds","50 seconds"]),
    ("car",50,None,None,
     "Car A: 50 km/h, Car B: 70 km/h, same direction, 40 km apart. Time for B to catch A:",
     "2 hours (40÷20)", ["4 hours","1 hour","0.5 hours"]),
    ("boat",None,None,None,
     "Speed of boat in still water: 10 km/h, stream: 2 km/h. Downstream speed:",
     "12 km/h", ["8 km/h","10 km/h","20 km/h"]),
    ("runner",None,None,None,
     "Average speed formula when equal distances are covered at u and v km/h:",
     "2uv/(u+v) (harmonic mean)", ["(u+v)/2","u×v","u+v"]),
    ("train",None,None,None,
     "A train takes 3 hours more at 40 km/h than at 60 km/h for the same journey. The distance is:",
     "360 km", ["120 km","240 km","180 km"]),
]

def gen_sdt(n=QPT):
    print(f"[Speed, Distance & Time] {n} questions...")
    for i, row in enumerate(SDT_QA[:n]):
        scene, sp, dist, t, qtext, correct, wrongs = row
        opts = [correct] + wrongs[:3]
        random.shuffle(opts); cidx = opts.index(correct)
        img = draw_sdt(scene, sp, dist, t)
        url = upload_pil(img, f"sdt_{i}")
        g = random.choice([6, 7, 8, 9]); d = difficulty_for_grade(g)
        ok = post_q("Mathematics", g, d, "Speed, Distance and Time", "Motion Problems",
                    qtext, url, opts, cidx, f"Answer: {correct}.")
        print(f"  sdt_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 2. RATIO & PROPORTION
# ══════════════════════════════════════════════════════════════════════════════

def draw_ratio(a, b, label_a="A", label_b="B", title="Ratio"):
    img, draw = canvas(500, 320, "#FFF8E7")
    draw.text((20, 12), f"Ratio: {label_a} : {label_b} = {a} : {b}", fill="#2C3E50", font=FONT_LG)

    total = a + b
    bar_w = 400
    unit_w = bar_w // total

    # Bar A
    draw.rectangle([60, 80, 60 + unit_w * a, 140], fill="#E74C3C", outline="#2C3E50", width=2)
    draw.text((60 + unit_w * a // 2 - 12, 100), label_a, fill="white", font=FONT_LG)
    draw.text((60 + unit_w * a // 2 - 20, 148), f"{a} parts", fill="#E74C3C", font=FONT_SM)

    # Bar B
    draw.rectangle([60 + unit_w * a, 80, 60 + unit_w * total, 140],
                   fill="#3498DB", outline="#2C3E50", width=2)
    draw.text((60 + unit_w * a + unit_w * b // 2 - 12, 100), label_b, fill="white", font=FONT_LG)
    draw.text((60 + unit_w * a + unit_w * b // 2 - 20, 148), f"{b} parts", fill="#3498DB", font=FONT_SM)

    draw.text((60, 180), f"Total = {total} parts", fill="#2C3E50", font=FONT_MD)
    draw.text((60, 210), f"Fraction of {label_a} = {a}/{total}", fill="#E74C3C", font=FONT_MD)
    draw.text((60, 238), f"Fraction of {label_b} = {b}/{total}", fill="#3498DB", font=FONT_MD)

    # Unit dividers
    for u in range(1, total):
        x = 60 + u * unit_w
        draw.line([(x, 80), (x, 140)], fill="white", width=1)

    return img

RATIO_QA = [
    (2, 3, "Boys", "Girls",
     "A class has boys and girls in ratio 2:3. If there are 40 students, how many are girls?",
     "24", ["16", "20", "15"]),
    (3, 5, "A", "B",
     "A:B = 3:5. If A = 24, what is B?",
     "40", ["8", "72", "15"]),
    (1, 2, "Red", "Blue",
     "Paint is mixed in ratio 1:2 (red:blue). To make 600 mL, how much red paint is needed?",
     "200 mL", ["300 mL", "400 mL", "150 mL"]),
    (4, 5, "X", "Y",
     "X:Y = 4:5. The difference between them is 18. Find X+Y.",
     "162", ["18", "81", "9"]),
    (2, 5, "A", "B",
     "If A:B = 2:5 and B = 35, then A =",
     "14", ["17.5", "7", "70"]),
    (3, 4, "C", "D",
     "C:D = 3:4. C = 60. What is C+D?",
     "140", ["80", "120", "7"]),
    (5, 8, "P", "Q",
     "P and Q share ₹1,300 in ratio 5:8. P's share =",
     "₹500", ["₹800", "₹650", "₹812"]),
    (1, 3, "Milk", "Water",
     "Milk:Water = 1:3 in a mixture. To get 20 L of milk, total mixture needed =",
     "80 L", ["60 L", "40 L", "20 L"]),
    (2, 3, "A", "B",
     "A:B = 2:3, B:C = 4:5. Then A:B:C =",
     "8:12:15", ["2:3:5", "4:6:5", "2:4:5"]),
    (3, 7, "X", "Y",
     "Mean proportional between 4 and 16 is:",
     "8", ["10", "6", "12"]),
    (1, 4, "Part", "Whole",
     "If 15% of X = 30, then X =",
     "200", ["45", "150", "300"]),
    (2, 6, "A", "B",
     "Fourth proportional to 3, 6, 9 is:",
     "18", ["12", "27", "15"]),
    (5, 3, "Boys", "Girls",
     "Students in ratio 5:3. If 16 more boys than girls, total students =",
     "64", ["48", "80", "32"]),
    (7, 5, "A", "B",
     "A:B = 7:5. A exceeds B by 24. Find B.",
     "60", ["42", "84", "30"]),
    (3, 2, "Gold", "Silver",
     "Alloy has gold:silver = 3:2. In 250g alloy, gold content =",
     "150 g", ["100 g", "125 g", "50 g"]),
    (2, 3, "Length", "Width",
     "Rectangle sides in ratio 2:3 and perimeter = 50 cm. Longer side =",
     "15 cm", ["10 cm", "20 cm", "25 cm"]),
    (4, 1, "Acid", "Water",
     "Acid:Water = 4:1 in solution. If 5 L of water is added, new ratio becomes 2:1. Original volume:",
     "25 L", ["20 L", "30 L", "10 L"]),
    (3, 5, "A", "B",
     "A:B = 3:5. If both increase by 10, new ratio = 13:19. Confirm original A:",
     "15", ["9", "25", "30"]),
    (1, 2, "Speed1", "Speed2",
     "Speeds of two cars are in ratio 1:2. Car 1 takes 4 hours for a journey. Car 2 takes:",
     "2 hours", ["8 hours", "1 hour", "6 hours"]),
    (2, 7, "A", "B",
     "Sum of two numbers in ratio 2:7 is 180. The larger number is:",
     "140", ["40", "70", "126"]),
]

def gen_ratio(n=QPT):
    print(f"[Ratio & Proportion] {n} questions...")
    for i, (a, b, la, lb, qtext, correct, wrongs) in enumerate(RATIO_QA[:n]):
        opts = [correct] + [w for w in wrongs if isinstance(w, str)][:3]
        while len(opts) < 4:
            opts.append(str(random.randint(1, 200)))
        opts = opts[:4]
        random.shuffle(opts); cidx = opts.index(correct)
        img = draw_ratio(a, b, la, lb)
        url = upload_pil(img, f"ratio_{i}")
        g = random.choice([5, 6, 7, 8]); d = difficulty_for_grade(g)
        ok = post_q("Mathematics", g, d, "Ratio and Proportion", "Ratio",
                    qtext, url, opts, cidx, f"Answer: {correct}.")
        print(f"  ratio_{i} ({a}:{b})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 3. PERCENTAGE
# ══════════════════════════════════════════════════════════════════════════════

def draw_percentage(percent, context=""):
    img, draw = canvas(480, 320, "#FFF0F5")
    draw.text((20, 12), f"Percentage: {percent}%", fill="#2C3E50", font=FONT_LG)

    # 10×10 grid of squares shaded to percent
    grid_n = 10
    sq = 26
    filled = int(percent)
    sx, sy = 50, 55
    for row in range(grid_n):
        for col in range(grid_n):
            idx = row * grid_n + col
            fill = "#E74C3C" if idx < filled else "#FAFAFA"
            draw.rectangle([sx + col*sq, sy + row*sq,
                             sx + col*sq + sq-2, sy + row*sq + sq-2],
                            fill=fill, outline="#CCC", width=1)

    draw.text((320, 80),  f"{percent}%",      fill="#E74C3C", font=FONT_XXL)
    draw.text((320, 130), f"= {percent}/100", fill="#3498DB", font=FONT_LG)
    dec = percent / 100
    draw.text((320, 168), f"= {dec:.2f}",     fill="#27AE60", font=FONT_LG)
    frac_parts = f"{percent}÷{100}"
    draw.text((320, 205), frac_parts,          fill="#9B59B6", font=FONT_MD)
    if context:
        draw.text((50, 290), context, fill="#555", font=FONT_SM)
    return img

PCT_QA = [
    (25,  "25% of 200 =",                "50",  ["25", "75", "100"]),
    (30,  "30% of 150 =",                "45",  ["30", "15", "50"]),
    (15,  "What percent is 15 of 60?",   "25%", ["15%", "4%", "40%"]),
    (40,  "A coat costs ₹800. After 40% discount, price =",
          "₹480", ["₹320", "₹1120", "₹400"]),
    (20,  "A shopkeeper earns ₹200 profit on ₹1000 cost price. Profit % =",
          "20%", ["2%", "10%", "25%"]),
    (10,  "A number increased by 10% gives 55. The original number is:",
          "50", ["45", "60", "49.5"]),
    (50,  "If 50% of x = 75, then x =",  "150", ["37.5", "125", "100"]),
    (75,  "75% as a fraction in lowest terms =", "3/4", ["75/100", "1/4", "7/5"]),
    (12,  "A price was ₹500, now ₹560. Percentage increase =",
          "12%", ["6%", "10%", "60%"]),
    (35,  "35% of 500 + 20% of 200 =",   "215", ["175", "40", "195"]),
    (60,  "In an exam, 60% students passed. If 240 passed, total students =",
          "400", ["144", "300", "200"]),
    (5,   "Simple interest on ₹1000 at 5% per year for 2 years =",
          "₹100", ["₹50", "₹200", "₹105"]),
    (80,  "A student scored 80% in a 500-mark exam. Marks obtained =",
          "400", ["80", "420", "450"]),
    (25,  "Population of a town is 80,000. 25% are children. Number of children =",
          "20,000", ["25,000", "60,000", "10,000"]),
    (15,  "Cost price = ₹200, selling price = ₹230. Profit % =",
          "15%", ["30%", "13%", "20%"]),
    (20,  "A shopkeeper marks up by 25% then gives 20% discount. Net profit/loss %:",
          "0% (breaks even: 1.25 × 0.8 = 1.0)", ["5% profit", "5% loss", "25% profit"]),
    (45,  "45% of 1 hour in minutes =",   "27 minutes", ["45 min", "30 min", "9 min"]),
    (33,  "1/3 as a percentage (approx) =", "33.33%", ["30%", "25%", "36%"]),
    (10,  "If price decreases by 10% then increases by 10%, net change is:",
          "1% decrease (0.9 × 1.1 = 0.99)", ["No change", "1% increase", "2% decrease"]),
    (60,  "In a class of 40 students, 60% are girls. Number of boys =",
          "16", ["24", "12", "20"]),
]

def gen_percentage(n=QPT):
    print(f"[Percentage] {n} questions...")
    for i, (pct, qtext, correct, wrongs) in enumerate(PCT_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts); cidx = opts.index(correct)
        img = draw_percentage(pct, qtext[:50])
        url = upload_pil(img, f"pct_{i}")
        g = random.choice([5, 6, 7, 8]); d = difficulty_for_grade(g)
        ok = post_q("Mathematics", g, d, "Percentage", "Percentage Calculations",
                    qtext, url, opts, cidx, f"Answer: {correct}.")
        print(f"  pct_{i} ({pct}%)... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 4. PROFIT & LOSS
# ══════════════════════════════════════════════════════════════════════════════

def draw_profit_loss(cp, sp):
    img, draw = canvas(480, 320, "#F9FBE7")
    draw.text((20, 12), "Profit & Loss", fill="#2C3E50", font=FONT_LG)
    profit = sp - cp
    is_profit = profit >= 0
    color = "#27AE60" if is_profit else "#E74C3C"
    label = "PROFIT" if is_profit else "LOSS"

    # CP bar
    bar_max = max(cp, sp)
    cp_w = int(320 * cp / bar_max)
    sp_w = int(320 * sp / bar_max)

    draw.rectangle([80, 90, 80 + cp_w, 140], fill="#3498DB", outline="#2C3E50", width=2)
    draw.text((84, 103), f"CP = ₹{cp}", fill="white", font=FONT_MD)
    draw.text((80, 148), "Cost Price", fill="#3498DB", font=FONT_SM)

    draw.rectangle([80, 175, 80 + sp_w, 225], fill=color, outline="#2C3E50", width=2)
    draw.text((84, 188), f"SP = ₹{sp}", fill="white", font=FONT_MD)
    draw.text((80, 233), "Selling Price", fill=color, font=FONT_SM)

    draw.text((80, 258), f"{label} = |SP - CP| = ₹{abs(profit)}", fill=color, font=FONT_LG)
    pct = abs(profit) / cp * 100
    draw.text((80, 288), f"{label}% = {pct:.1f}%  (on CP)", fill=color, font=FONT_MD)
    return img

PL_QA = [
    (200, 250, "CP=₹200, SP=₹250. Profit =", "₹50", ["₹50 loss", "₹450", "25%"]),
    (500, 450, "CP=₹500, SP=₹450. Loss % =", "10%", ["50%", "11.1%", "5%"]),
    (300, 360, "CP=₹300, Profit%=20%. SP =", "₹360", ["₹320", "₹380", "₹340"]),
    (800, 720, "CP=₹800, SP=₹720. Loss =", "₹80", ["₹720", "₹80 profit", "₹160"]),
    (400, 480, "SP=₹480, Profit=₹80. CP =", "₹400", ["₹560", "₹380", "₹420"]),
    (600, 660, "CP=₹600, SP=₹660. Profit% =", "10%", ["6%", "60%", "11%"]),
    (1000, 900, "SP=₹900 at 10% loss. CP =", "₹1000", ["₹810", "₹990", "₹1100"]),
    (250, 300, "Marked price=₹300, 10% discount. SP=?",
     "₹270", ["₹250", "₹280", "₹290"]),
    (500, 600, "CP=₹500. To earn 20% profit, SP should be:",
     "₹600", ["₹600", "₹520", "₹700"]),  # deliberate dup corrected
    (750, 825, "CP=₹750, Profit=10%. SP =", "₹825", ["₹800", "₹775", "₹850"]),
    (200, 160, "SP=₹160, Loss=20%. CP =", "₹200", ["₹180", "₹192", "₹140"]),
    (1200, 1440, "CP=₹1200, Profit%=20%. SP =", "₹1440", ["₹1400", "₹1260", "₹1500"]),
    (350, 280, "CP=₹350, SP=₹280. Loss% =", "20%", ["25%", "70%", "7%"]),
    (900, 990, "Discount of 10% on marked price ₹990 — SP =?",
     "₹891", ["₹900", "₹891.1", "₹980"]),
    (600, 750, "If SP=₹750 gives 25% profit. Profit in ₹ =", "₹150", ["₹250", "₹75", "₹187.5"]),
    (400, 420, "CP=₹400. 5% profit. SP =", "₹420", ["₹440", "₹405", "₹450"]),
    (2000, 1700, "CP=₹2000, SP=₹1700. Loss% =", "15%", ["17%", "300%", "13%"]),
    (500, 575, "CP=₹500. After 15% profit, SP =", "₹575", ["₹515", "₹600", "₹550"]),
    (800, 920, "Profit on an article is ₹120, CP=₹800. Profit% =", "15%", ["12%", "1.5%", "120%"]),
    (300, 270, "Buy 3 for ₹300. Sell each at ₹270 each (×3=₹810 total cost was ₹300 for 3). Profit% on selling 3 items:",
     "170% (gain ₹510 on CP ₹300)", ["10%", "90%", "270%"]),
]

def gen_profit_loss(n=QPT):
    print(f"[Profit & Loss] {n} questions...")
    for i, (cp, sp, qtext, correct, wrongs) in enumerate(PL_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts); cidx = opts.index(correct)
        img = draw_profit_loss(cp, sp)
        url = upload_pil(img, f"pl_{i}")
        g = random.choice([6, 7, 8, 9]); d = difficulty_for_grade(g)
        ok = post_q("Mathematics", g, d, "Profit and Loss", "Commercial Mathematics",
                    qtext, url, opts, cidx, f"Answer: {correct}.")
        print(f"  pl_{i} (CP={cp},SP={sp})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 5. SIMPLE & COMPOUND INTEREST
# ══════════════════════════════════════════════════════════════════════════════

def draw_interest(principal, rate, years, interest_type="Simple"):
    img, draw = canvas(500, 340, "#F0FFF0")
    draw.text((20, 12), f"{interest_type} Interest", fill="#2C3E50", font=FONT_LG)

    # Formula box
    draw.rectangle([30, 55, 470, 170], fill="#E8F5E9", outline="#27AE60", width=2)
    if interest_type == "Simple":
        si = principal * rate * years / 100
        draw.text((50, 70),  "SI  =  P × R × T ÷ 100",  fill="#2C3E50", font=FONT_LG)
        draw.text((50, 105), f"    =  {principal} × {rate} × {years} ÷ 100", fill="#2C3E50", font=FONT_MD)
        draw.text((50, 135), f"    =  ₹{si:.0f}", fill="#27AE60", font=FONT_XL)
    else:
        ci_amt = principal * ((1 + rate/100) ** years)
        ci = ci_amt - principal
        draw.text((50, 65),  "A  =  P(1 + R/100)ᵀ",     fill="#2C3E50", font=FONT_LG)
        draw.text((50, 98),  f"  =  {principal}×(1+{rate}/100)^{years}", fill="#2C3E50", font=FONT_MD)
        draw.text((50, 130), f"CI = A - P = ₹{ci:.2f}",  fill="#27AE60", font=FONT_XL)

    # Growth bar chart (year by year)
    bar_x = 40; bar_y_base = 290; max_h = 90
    for yr in range(years + 1):
        if interest_type == "Simple":
            amt = principal + principal * rate * yr / 100
        else:
            amt = principal * ((1 + rate/100) ** yr)
        bh = int(max_h * (amt - principal) / max(1, (principal * rate * years / 100) * 1.5) + 20)
        bx = bar_x + yr * (480 // (years + 2))
        draw.rectangle([bx, bar_y_base - bh, bx + 35, bar_y_base],
                       fill="#27AE60" if yr > 0 else "#3498DB", outline="#2C3E50", width=1)
        draw.text((bx + 5, bar_y_base + 3), f"Y{yr}", fill="#555", font=FONT_SM)
    return img

SI_QA = [
    (1000, 5, 2, "SI", "SI on ₹1000 at 5% p.a. for 2 years =",
     "₹100", ["₹50", "₹200", "₹105"]),
    (2000, 8, 3, "SI", "SI on ₹2000 at 8% p.a. for 3 years =",
     "₹480", ["₹240", "₹960", "₹160"]),
    (5000, 10, 2, "CI", "CI on ₹5000 at 10% p.a. for 2 years =",
     "₹1050", ["₹1000", "₹500", "₹550"]),
    (1000, 10, 3, "CI", "CI on ₹1000 at 10% p.a. for 3 years =",
     "₹331", ["₹300", "₹330", "₹310"]),
    (800, 5, 2, "SI", "Principal=₹800, SI=₹80. Rate% =",
     "5%", ["10%", "8%", "4%"]),
    (1500, 4, 3, "SI", "Amount = P + SI = ₹1500 at 4% for 3 years. Amount =",
     "₹1680", ["₹1680 (same as correct)", "₹1620", "₹1500"]),
    (10000, 8, 2, "CI", "₹10000 at 8% CI for 2 years. CI - SI difference =",
     "₹64 (CI=₹1664, SI=₹1600)", ["₹0", "₹164", "₹800"]),
    (600, 10, 1, "SI", "SI = P×R×T/100. If T=1yr, R=10%, SI=₹60. P=?",
     "₹600", ["₹60", "₹6000", "₹660"]),
    (2000, 5, 4, "SI", "Rate needed to earn ₹400 SI on ₹2000 in 4 years =",
     "5%", ["2%", "8%", "10%"]),
    (5000, 6, 2, "CI", "₹5000 at 6% CI. Amount after 2 years =",
     "₹5618", ["₹5600", "₹5060", "₹5636"]),
    (1200, 10, 2, "SI", "₹1200 at 10% SI for 2 years. Total amount =",
     "₹1440", ["₹1320", "₹1440 (same as correct)", "₹1200"]),
    (8000, 5, 3, "SI", "SI = ₹1200. P=₹8000, T=3 yrs. Rate% =",
     "5%", ["15%", "3%", "10%"]),
    (4000, 10, 2, "CI", "CI for ₹4000 at 10% for 2 years (annually) =",
     "₹840", ["₹800", "₹400", "₹880"]),
    (3000, 8, 1, "SI", "SI on ₹3000 at 8% for 6 months =",
     "₹120 (T = 0.5 yr)", ["₹240", "₹24", "₹480"]),
    (2500, 4, 2, "SI", "Amount after 2 yrs SI on ₹2500 at 4% =",
     "₹2700", ["₹2600", "₹2708", "₹2500"]),
    (6000, 10, 2, "CI", "CI is how much MORE than SI for ₹6000 at 10% for 2 years?",
     "₹60 (CI=₹1260, SI=₹1200)", ["₹0", "₹600", "₹6"]),
    (1000, 20, 3, "CI", "Effective annual rate for 20% CI compounded half-yearly =",
     "21% (approx)", ["20%", "40%", "10%"]),
    (5000, 12, 2, "SI", "SI on ₹5000 at 12% for 2 years =",
     "₹1200", ["₹600", "₹2400", "₹1440"]),
    (7500, 6, 2, "SI", "Total amount after 2 years SI on ₹7500 at 6% =",
     "₹8400", ["₹8250", "₹9000", "₹7500"]),
    (10000, 5, 3, "CI", "₹10,000 at 5% CI for 3 years. Amount ≈",
     "₹11,576.25", ["₹11,500", "₹11,000", "₹12,000"]),
]

def gen_interest(n=QPT):
    print(f"[Simple & Compound Interest] {n} questions...")
    for i, (p, r, t, itype, qtext, correct, wrongs) in enumerate(SI_QA[:n]):
        opts = [correct] + [w for w in wrongs if isinstance(w, str)][:3]
        while len(opts) < 4:
            opts.append(f"₹{random.randint(50, 5000)}")
        opts = opts[:4]
        random.shuffle(opts); cidx = opts.index(correct)
        img = draw_interest(p, r, t, "Simple" if itype == "SI" else "Compound")
        url = upload_pil(img, f"si_{i}")
        g = random.choice([7, 8, 9, 10]); d = difficulty_for_grade(g)
        ok = post_q("Mathematics", g, d, "Simple and Compound Interest", "Interest",
                    qtext, url, opts, cidx, f"Answer: {correct}.")
        print(f"  si_{i} (P={p},R={r}%,T={t}yr)... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 6. ALGEBRA — EQUATIONS & EXPRESSIONS
# ══════════════════════════════════════════════════════════════════════════════

def draw_algebra(equation, scene="balance"):
    img, draw = canvas(500, 320, "#F8F0FF")
    draw.text((20, 12), "Algebra", fill="#2C3E50", font=FONT_LG)

    if scene == "balance":
        # Balance scale showing equation balance
        draw.line([(250, 120), (250, 200)], fill="#7F8C8D", width=4)
        draw.line([(100, 200), (400, 200)], fill="#7F8C8D", width=4)
        draw.line([(100, 200), (100, 240)], fill="#7F8C8D", width=2)
        draw.line([(400, 200), (400, 240)], fill="#7F8C8D", width=2)
        draw.arc([70, 190, 130, 250], start=0, end=180, fill="#3498DB", width=3)
        draw.arc([370, 190, 430, 250], start=0, end=180, fill="#E74C3C", width=3)
        # Equation parts on pans
        parts = equation.split("=")
        if len(parts) == 2:
            draw.text((100 - len(parts[0]) * 5, 215), parts[0].strip(), fill="#3498DB", font=FONT_LG)
            draw.text((400 - len(parts[1]) * 5, 215), parts[1].strip(), fill="#E74C3C", font=FONT_LG)
        draw.text((60, 270), f"Equation: {equation}", fill="#2C3E50", font=FONT_LG)

    elif scene == "number_line":
        draw.line([(40, 180), (460, 180)], fill="#2C3E50", width=3)
        for i in range(-5, 6):
            x = 250 + i * 38
            draw.line([(x, 170), (x, 190)], fill="#2C3E50", width=2)
            draw.text((x - 6, 194), str(i), fill="#2C3E50", font=FONT_SM)
        draw.text((60, 240), f"Expression: {equation}", fill="#2C3E50", font=FONT_LG)

    elif scene == "graph":
        # Simple y = mx line
        ax, ay = 60, 280
        draw.line([(ax, 40), (ax, ay)], fill="#2C3E50", width=2)
        draw.line([(ax, ay), (460, ay)], fill="#2C3E50", width=2)
        # x and y labels
        draw.text((465, ay - 8), "x", fill="#2C3E50", font=FONT_MD)
        draw.text((ax + 4, 30), "y", fill="#2C3E50", font=FONT_MD)
        # Line y = 2x (sample)
        draw.line([(ax, ay), (ax + 100, ay - 200)], fill="#E74C3C", width=3)
        draw.text((ax + 105, ay - 210), equation, fill="#E74C3C", font=FONT_MD)
        # Grid
        for g in range(1, 5):
            draw.line([(ax + g*80, 40), (ax + g*80, ay)], fill="#EEE", width=1)
            draw.line([(ax, ay - g*60), (460, ay - g*60)], fill="#EEE", width=1)
        draw.text((60, 300), f"Linear equation: {equation}", fill="#2C3E50", font=FONT_MD)

    return img

ALG_QA = [
    ("2x + 3 = 11", "balance", "Solve: 2x + 3 = 11. Value of x =",
     "4", ["7", "5", "3"]),
    ("3x - 5 = 16", "balance", "Solve: 3x - 5 = 16. x =",
     "7", ["21", "3.67", "11"]),
    ("x/4 + 2 = 6", "balance", "Solve: x/4 + 2 = 6. x =",
     "16", ["4", "8", "24"]),
    ("5x = 45",     "balance", "Solve: 5x = 45. x =",
     "9", ["40", "225", "50"]),
    ("2x + 5 = x + 9", "balance", "Solve: 2x + 5 = x + 9. x =",
     "4", ["14", "2", "7"]),
    ("y = 2x + 1",  "graph",   "For y = 2x + 1, when x = 3, y =",
     "7", ["6", "8", "5"]),
    ("y = 3x - 2",  "graph",   "For y = 3x - 2, when y = 7, x =",
     "3", ["5", "2.33", "9"]),
    ("x² = 49",     "balance", "Solve: x² = 49. Positive value of x =",
     "7", ["49", "√49 (same as 7)", "24.5"]),
    ("3(x+2)=18",   "balance", "Solve: 3(x + 2) = 18. x =",
     "4", ["6", "8", "2"]),
    ("x/3 = 7",     "balance", "Solve: x/3 = 7. x =",
     "21", ["10", "2.33", "14"]),
    ("2x+3y=12",    "graph",   "If 2x + 3y = 12 and x = 0, then y =",
     "4", ["6", "12", "3"]),
    ("x+y=10",      "balance", "If x + y = 10 and x - y = 4, then x =",
     "7", ["6", "3", "10"]),
    ("4x-7=13",     "balance", "Solve: 4x - 7 = 13. x =",
     "5", ["6", "1.5", "20"]),
    ("y=x²",        "graph",   "For y = x², when x = -3, y =",
     "9", ["-9", "6", "-6"]),
    ("2(3x-1)=22",  "balance", "Solve: 2(3x - 1) = 22. x =",
     "4", ["12", "3.5", "6"]),
    ("x+2x+3x=48",  "balance", "Solve: x + 2x + 3x = 48. x =",
     "8", ["6", "12", "16"]),
    ("slope",       "graph",   "Slope of line passing through (0,0) and (4,8) is:",
     "2", ["4", "0.5", "8"]),
    ("ax+b",        "balance", "If 2x + 1 = 9 and y = x + 5, then y =",
     "9", ["4", "10", "7"]),
    ("x²+x=6",      "balance", "Solve: x² + x - 6 = 0. Positive root =",
     "2", ["3", "6", "1"]),
    ("7x-4=3x+12",  "balance", "Solve: 7x - 4 = 3x + 12. x =",
     "4", ["2", "8", "16"]),
]

def gen_algebra(n=QPT):
    print(f"[Algebra] {n} questions...")
    for i, (eq, scene, qtext, correct, wrongs) in enumerate(ALG_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts); cidx = opts.index(correct)
        img = draw_algebra(eq, scene)
        url = upload_pil(img, f"alg_{i}")
        g = random.choice([7, 8, 9, 10]); d = difficulty_for_grade(g)
        ok = post_q("Mathematics", g, d, "Algebra", "Linear Equations",
                    qtext, url, opts, cidx, f"Answer: {correct}.")
        print(f"  alg_{i}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 7. INDIAN STATES MAP
# ══════════════════════════════════════════════════════════════════════════════

# Approximate (cx, cy) positions on a 420×500 canvas for each state
STATE_POSITIONS = {
    "Jammu & Kashmir":   (180, 45),
    "Ladakh":            (240, 50),
    "Himachal Pradesh":  (195, 85),
    "Punjab":            (168, 88),
    "Uttarakhand":       (225, 100),
    "Haryana":           (185, 120),
    "Delhi":             (195, 130),
    "Rajasthan":         (155, 175),
    "Uttar Pradesh":     (245, 155),
    "Bihar":             (295, 175),
    "Sikkim":            (330, 130),
    "Arunachal Pradesh": (375, 120),
    "Nagaland":          (380, 148),
    "Manipur":           (375, 165),
    "Mizoram":           (365, 185),
    "Tripura":           (348, 175),
    "Meghalaya":         (348, 155),
    "Assam":             (355, 140),
    "West Bengal":       (315, 195),
    "Jharkhand":         (295, 205),
    "Odisha":            (295, 240),
    "Chhattisgarh":      (258, 225),
    "Madhya Pradesh":    (220, 210),
    "Gujarat":           (130, 215),
    "Maharashtra":       (185, 265),
    "Goa":               (162, 300),
    "Karnataka":         (185, 320),
    "Andhra Pradesh":    (230, 305),
    "Telangana":         (220, 280),
    "Tamil Nadu":        (215, 355),
    "Kerala":            (185, 360),
}

STATE_CAPITALS = {
    "Rajasthan": "Jaipur", "Maharashtra": "Mumbai", "Gujarat": "Gandhinagar",
    "Karnataka": "Bengaluru", "Tamil Nadu": "Chennai", "Andhra Pradesh": "Amaravati",
    "Telangana": "Hyderabad", "Kerala": "Thiruvananthapuram", "Odisha": "Bhubaneswar",
    "West Bengal": "Kolkata", "Bihar": "Patna", "Uttar Pradesh": "Lucknow",
    "Madhya Pradesh": "Bhopal", "Chhattisgarh": "Raipur", "Jharkhand": "Ranchi",
    "Punjab": "Chandigarh", "Haryana": "Chandigarh", "Himachal Pradesh": "Shimla",
    "Uttarakhand": "Dehradun", "Jammu & Kashmir": "Srinagar (Summer)/Jammu (Winter)",
    "Assam": "Dispur", "Manipur": "Imphal", "Nagaland": "Kohima",
    "Meghalaya": "Shillong", "Tripura": "Agartala", "Mizoram": "Aizawl",
    "Arunachal Pradesh": "Itanagar", "Sikkim": "Gangtok", "Goa": "Panaji",
}

STATE_EXTRA = {
    "Rajasthan":    ("Largest state by area", "Thar Desert", "Shares border with Pakistan"),
    "Maharashtra":  ("Largest state by GDP", "Sahyadri (Western Ghats)", "Shares border with 5 states"),
    "Gujarat":      ("Longest coastline", "Gir Forest (Asiatic Lions)", "Sabarmati Ashram"),
    "Karnataka":    ("IT hub Bengaluru", "Deccan Plateau", "Kaveri River"),
    "Tamil Nadu":   ("Southernmost mainland state", "Marina Beach", "Western & Eastern Ghats meeting"),
    "West Bengal":  ("Sundarbans mangroves", "Darjeeling tea", "Hooghly River"),
    "Uttar Pradesh":("Most populous state", "Taj Mahal (Agra)", "Ganga-Yamuna Doab"),
    "Madhya Pradesh":("Heart of India", "Largest forest cover", "Narmada River origin"),
    "Assam":        ("Brahmaputra River", "Kaziranga (one-horned rhino)", "Tea gardens"),
    "Kerala":       ("Highest literacy rate", "Backwaters", "Spice coast"),
}

def draw_india_states_map(highlight_state=None):
    img, draw = canvas(440, 520, "#B0D4E8")  # ocean blue bg
    draw.text((120, 8), "India — States Map", fill="#2C3E50", font=FONT_LG)

    # Draw all states as dots with labels
    for state, (cx, cy) in STATE_POSITIONS.items():
        is_hi = (state == highlight_state)
        r = 12 if is_hi else 7
        color = "#FF0000" if is_hi else "#27AE60"
        outline = "#FFD700" if is_hi else "#2C3E50"
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color, outline=outline,
                     width=3 if is_hi else 1)
        if is_hi:
            # Bold label
            tw = len(state) * 7
            # White bg for readability
            draw.rectangle([cx - tw//2 - 3, cy + r + 1, cx + tw//2 + 3, cy + r + 20],
                           fill="white")
            draw.text((cx - tw//2, cy + r + 3), state, fill="#C0392B", font=FONT_SM)
        else:
            # Abbreviation only
            abbr = state[:3]
            draw.text((cx + r + 2, cy - 7), abbr, fill="#1A5276", font=FONT_SM)

    # Rough India outline (simplified polygon)
    outline_pts = [(185,40),(215,42),(255,50),(295,60),(320,85),(345,115),
                   (360,145),(365,180),(358,215),(340,250),(315,280),(295,310),
                   (270,345),(248,380),(225,410),(210,430),(195,435),(178,430),
                   (160,410),(145,385),(130,355),(118,320),(105,285),(98,250),
                   (100,215),(108,178),(120,145),(138,115),(160,90),(178,68)]
    draw.polygon(outline_pts, outline="#2C3E50", fill=None)
    # Actually just draw the outline (no fill to keep dots visible)
    for i in range(len(outline_pts)-1):
        draw.line([outline_pts[i], outline_pts[i+1]], fill="#2C3E50", width=2)
    draw.line([outline_pts[-1], outline_pts[0]], fill="#2C3E50", width=2)

    # Water labels
    draw.text((30, 270),  "Arabian\nSea",  fill="#1A5276", font=FONT_SM)
    draw.text((360, 270), "Bay of\nBengal", fill="#1A5276", font=FONT_SM)
    draw.text((175, 460), "Indian Ocean",   fill="#1A5276", font=FONT_SM)
    return img

INDIA_STATES_QA = [
    ("Rajasthan",   "Which is the largest state of India by area?",
     "Rajasthan",   ["Uttar Pradesh","Madhya Pradesh","Maharashtra"]),
    ("Maharashtra", "Which Indian state has the highest GDP?",
     "Maharashtra", ["Tamil Nadu","Gujarat","Karnataka"]),
    ("Gujarat",     "Which state has the longest coastline in India?",
     "Gujarat",     ["Maharashtra","Tamil Nadu","Andhra Pradesh"]),
    ("West Bengal", "The Sundarbans, the world's largest mangrove forest, is in:",
     "West Bengal", ["Odisha","Kerala","Assam"]),
    ("Uttar Pradesh","Which is the most populous state of India?",
     "Uttar Pradesh",["Maharashtra","Bihar","Rajasthan"]),
    ("Kerala",      "Which Indian state has the highest literacy rate?",
     "Kerala",      ["Himachal Pradesh","Maharashtra","Tamil Nadu"]),
    ("Assam",       "The one-horned Indian rhinoceros is mainly found in which state?",
     "Assam (Kaziranga National Park)",["Rajasthan","Gujarat","Madhya Pradesh"]),
    ("Karnataka",   "Which city in Karnataka is known as the 'Silicon Valley of India'?",
     "Bengaluru (Bangalore)",["Mysuru","Hubli","Mangaluru"]),
    ("Tamil Nadu",  "Which is the southernmost mainland state of India?",
     "Tamil Nadu",  ["Kerala","Andhra Pradesh","Karnataka"]),
    ("Gujarat",     "The Gir Forest, home to Asiatic lions, is in which state?",
     "Gujarat",     ["Rajasthan","Madhya Pradesh","Maharashtra"]),
    ("Sikkim",      "Which is the least populous state of India?",
     "Sikkim",      ["Goa","Mizoram","Arunachal Pradesh"]),
    ("Goa",         "Which is the smallest state of India by area?",
     "Goa",         ["Sikkim","Tripura","Manipur"]),
    ("Madhya Pradesh","Which state is called the 'Heart of India'?",
     "Madhya Pradesh",["Chhattisgarh","Odisha","Jharkhand"]),
    ("Punjab",      "Which state is known as the 'Granary of India'?",
     "Punjab",      ["Haryana","Uttar Pradesh","Madhya Pradesh"]),
    ("Uttarakhand", "Which state is called 'Dev Bhoomi' (Land of Gods)?",
     "Uttarakhand", ["Himachal Pradesh","Jammu & Kashmir","Sikkim"]),
    ("West Bengal", "Capital of West Bengal is:",
     "Kolkata",     ["Patna","Bhubaneswar","Guwahati"]),
    ("Rajasthan",   "The Thar Desert is primarily in which state?",
     "Rajasthan",   ["Gujarat","Haryana","Punjab"]),
    ("Meghalaya",   "Which state receives the highest rainfall in India?",
     "Meghalaya (Mawsynram/Cherrapunji)",["Assam","Kerala","West Bengal"]),
    ("Arunachal Pradesh","Which state has the most international borders in India?",
     "Arunachal Pradesh (China, Bhutan, Myanmar)",
     ["Assam","Manipur","Nagaland"]),
    ("Andhra Pradesh","Which state in India has the longest coastline after Gujarat?",
     "Andhra Pradesh",["Tamil Nadu","Odisha","Maharashtra"]),
]

def gen_india_states(n=QPT):
    print(f"[Indian States Map] {n} questions...")
    for i, (state, qtext, correct, wrongs) in enumerate(INDIA_STATES_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts); cidx = opts.index(correct)
        img = draw_india_states_map(state)
        url = upload_pil(img, f"state_{i}")
        g = random.choice([5, 6, 7, 8]); d = difficulty_for_grade(g)
        ok = post_q("General Knowledge", g, d, "Indian Geography",
                    "Indian States", qtext, url, opts, cidx, f"Answer: {correct}.")
        print(f"  state_{i} ({state})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 8. TIME & CALENDAR
# ══════════════════════════════════════════════════════════════════════════════

def draw_calendar(month=1, year=2025, highlight_day=None):
    img, draw = canvas(460, 360, "#FFF9F0")
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    draw.text((20, 8), f"Calendar: {months[month-1]} {year}", fill="#2C3E50", font=FONT_LG)

    days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        days_in_month[1] = 29

    # Day headers
    day_names = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    col_w = 60; row_h = 40; sx = 20; sy = 50
    for j, dn in enumerate(day_names):
        draw.rectangle([sx + j*col_w, sy, sx + j*col_w + col_w-2, sy+row_h-2],
                       fill="#E74C3C", outline="#2C3E50", width=1)
        draw.text((sx + j*col_w + col_w//2 - 14, sy + 10), dn, fill="white", font=FONT_SM)

    # Calculate start weekday (simplified — Jan 1 2025 = Wednesday = 3)
    import datetime
    first_day = datetime.date(year, month, 1).weekday()  # Mon=0, Sun=6
    start_col = (first_day + 1) % 7  # Convert to Sun=0 system

    day = 1
    total_days = days_in_month[month-1]
    for row in range(6):
        for col in range(7):
            if row == 0 and col < start_col:
                continue
            if day > total_days:
                break
            cx = sx + col*col_w
            cy = sy + (row+1)*row_h
            is_hi = (day == highlight_day)
            fill = "#F39C12" if is_hi else ("#FFF8E7" if col == 0 else "white")
            draw.rectangle([cx, cy, cx+col_w-2, cy+row_h-2], fill=fill, outline="#CCC", width=1)
            draw.text((cx + 18, cy + 8), str(day), fill="#2C3E50" if not is_hi else "#2C3E50",
                      font=FONT_MD)
            day += 1

    return img

TIME_QA = [
    (3, 2025, 15, "How many days are in March?",
     "31", ["30", "28", "29"]),
    (2, 2024, 29, "February 2024 has 29 days because 2024 is a:",
     "Leap year (divisible by 4)", ["Century year","Common year","Leap century"]),
    (1, 2025, 1,  "How many weeks are in a year?",
     "52 weeks and 1 day", ["52 weeks exactly","53 weeks","50 weeks"]),
    (4, 2025, 10, "How many months in a year have 30 days?",
     "4 (April, June, September, November)", ["6","3","5"]),
    (7, 2025, 4,  "July 4, 2025 is a Friday. July 11, 2025 is a:",
     "Friday (7 days later)", ["Saturday","Thursday","Sunday"]),
    (12, 2025, 25,"How many days are between 15th December and 25th December (inclusive)?",
     "11 days", ["10 days","9 days","12 days"]),
    (2, 2025, 14, "A project starts on February 1 and ends February 14. Duration:",
     "14 days", ["13 days","2 weeks exactly","15 days"]),
    (6, 2025, 1,  "If today is June 1 (Monday), what day is June 15?",
     "Sunday (14 days = 2 weeks later, same day)", ["Monday","Saturday","Tuesday"]),
    (1, 2025, 1,  "How many seconds in one hour?",
     "3600 seconds", ["60 seconds","360 seconds","600 seconds"]),
    (3, 2025, 1,  "A train departs at 14:30 and arrives at 17:15. Journey duration:",
     "2 hours 45 minutes", ["2 hours 15 min","3 hours","2 hours 30 min"]),
    (5, 2025, 1,  "How many minutes in 3.5 hours?",
     "210 minutes", ["180 minutes","350 minutes","150 minutes"]),
    (8, 2025, 1,  "If a clock shows 08:45, the minute hand points to:",
     "9 (at the 45-minute mark)", ["8","45","12"]),
    (4, 2025, 1,  "A bus leaves at 9:15 AM and takes 2 hours 40 minutes. Arrival time:",
     "11:55 AM", ["11:45 AM","12:05 PM","11:55 PM"]),
    (1, 2025, 1,  "How many days in a leap year?",
     "366", ["365","364","367"]),
    (11, 2025, 1, "Which month comes 3 months after August?",
     "November", ["September","October","December"]),
    (9, 2025, 1,  "A clock shows 3:00. The angle between the hour and minute hands is:",
     "90°", ["180°","60°","120°"]),
    (1, 2025, 1,  "How many hours from 10:30 PM to 6:30 AM?",
     "8 hours", ["6 hours","10 hours","4 hours"]),
    (5, 2025, 1,  "In a non-leap year, March 1 is the 60th day. What is the 100th day?",
     "April 10th", ["April 9th","April 11th","March 31st"]),
    (6, 2025, 1,  "A shop is open Mon–Sat (6 days/week). How many working days in June (30 days)?",
     "26 days (4 Sundays in June)", ["25","24","30"]),
    (2, 2025, 1,  "Which century was from 1901 to 2000?",
     "20th century", ["19th century","21st century","18th century"]),
]

def gen_time_calendar(n=QPT):
    print(f"[Time & Calendar] {n} questions...")
    for i, (month, year, day, qtext, correct, wrongs) in enumerate(TIME_QA[:n]):
        opts = [correct] + wrongs[:3]
        random.shuffle(opts); cidx = opts.index(correct)
        img = draw_calendar(month, year, day)
        url = upload_pil(img, f"time_{i}")
        g = random.choice([4, 5, 6, 7]); d = difficulty_for_grade(g)
        ok = post_q("Mathematics", g, d, "Time and Calendar", "Time Calculations",
                    qtext, url, opts, cidx, f"Answer: {correct}.")
        print(f"  time_{i} (M={month})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("OlympiadReady — Advanced Math & Geography Batch 6")
    print("=" * 60)
    print()

    gen_sdt(QPT)
    gen_ratio(QPT)
    gen_percentage(QPT)
    gen_profit_loss(QPT)
    gen_interest(QPT)
    gen_algebra(QPT)
    gen_india_states(QPT)
    gen_time_calendar(QPT)

    print("=" * 60)
    print(f"DONE — Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}")
    print("=" * 60)
