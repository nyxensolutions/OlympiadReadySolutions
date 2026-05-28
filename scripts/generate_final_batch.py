"""
generate_final_batch.py
Final generators — Batch 5:
  1.  Number System / Place Value   (Grades 1-5)   — text options
  2.  Fractions & Decimals          (Grades 3-7)   — text options
  3.  Ratio & Proportion            (Grades 5-8)   — text options
  4.  Percentage                    (Grades 5-8)   — text options
  5.  Geometry: Perimeter & Area    (Grades 4-8)   — text options
  6.  Data Handling / Graphs        (Grades 4-8)   — text options
  7.  Indian History & Heritage     (Grades 5-9)   — text options
  8.  Environment & Conservation    (Grades 4-8)   — text options
  9.  LR: Blood Relations           (Grades 5-9)   — text options
 10.  LR: Direction & Distance      (Grades 5-9)   — text options

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
        public_id=f"f5_{label}_{int(time.time()*1000)}", resource_type="image")
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
            if r.status_code in (200,201):   POSTED  += 1; return True
            elif r.status_code == 409:       SKIPPED += 1; return False
            else: FAILED += 1; return False
        except Exception:
            if attempt == 0: time.sleep(3)
            else: FAILED += 1; return False

def canvas(w=500, h=380, bg="white"):
    img = Image.new("RGB",(w,h),bg)
    return img, ImageDraw.Draw(img)


# ══════════════════════════════════════════════════════════════════════════════
# 1. NUMBER SYSTEM & PLACE VALUE
# ══════════════════════════════════════════════════════════════════════════════

def draw_place_value(number, highlight_pos=None):
    img, draw = canvas(500, 320, "#FFF8DC")
    draw.text((20,12), "Place Value Chart", fill="#2C3E50", font=FONT_LG)

    num_str = str(number)
    places = ["Ten Crores","Crores","Ten Lakhs","Lakhs","Ten Thousands",
              "Thousands","Hundreds","Tens","Ones"]
    # Pad to 9 digits
    padded = num_str.zfill(9)

    col_w = 52
    start_x = 10
    for i, (place, digit) in enumerate(zip(places, padded)):
        bx = start_x + i * col_w
        is_hi = (i == 9 - len(num_str) + num_str.index(num_str[0]) if highlight_pos is None else highlight_pos == 8-i)
        fill = "#F39C12" if is_hi else ("#3498DB" if digit != '0' else "#BDC3C7")
        draw.rectangle([bx, 60, bx+col_w-2, 110], fill=fill, outline="#2C3E50", width=1)
        draw.text((bx+col_w//2-6, 76), digit, fill="white", font=FONT_LG)
        # Place label (vertical-ish — abbreviated)
        abbrev = place.replace("Ten ","T.").replace("Crores","Cr").replace("Lakhs","L").replace("Thousands","Th").replace("Hundreds","H").replace("Tens","T").replace("Ones","O")
        draw.text((bx+2, 115), abbrev[:5], fill="#2C3E50", font=FONT_SM)

    draw.text((20, 160), f"Number: {int(number):,}", fill="#2C3E50", font=FONT_XL)

    # Indian system labelling
    commas = []
    rev = num_str[::-1]
    parts = [rev[0:3], rev[3:5], rev[5:7], rev[7:9]]
    indian = ",".join(p[::-1] for p in parts if p)[::-1].lstrip(",")
    draw.text((20, 210), f"Indian notation: {indian[::-1] if len(num_str)>3 else num_str}", fill="#555", font=FONT_MD)
    draw.text((20, 250), f"International: {int(number):,}", fill="#555", font=FONT_MD)
    return img

NUMPLACE_QA = [
    (1234567, "What is the place value of 3 in 1,234,567?",
     "Thirty thousands (30,000)",["Three hundreds","Three thousands","Three hundred thousands"]),
    (9087654, "In the number 9,087,654, the digit 0 represents:",
     "0 (zero — it is a placeholder in the ten-lakhs place)",
     ["900,000","0 hundreds","1 unit"]),
    (5000000, "50,00,000 in words (Indian system) is:",
     "Fifty lakhs",["Five crores","Five million","Fifty thousands"]),
    (10000000,"1,00,00,000 (Indian system) is:",
     "One crore",["Ten lakhs","One million","Ten millions"]),
    (7654321, "What is the face value of 5 in 7,654,321?",
     "5 (face value is always the digit itself)",
     ["50,000","500","5,000"]),
    (3456789, "The number 34,56,789 has how many digits?",
     "7",["6","8","5"]),
    (100000, "1,00,000 equals:",
     "One lakh",["Ten thousand","One million","Ten lakh"]),
    (1000000,"Ten lakhs equals:",
     "10,00,000",["1,00,000","1,000","10,000"]),
    (2345678,"Which digit is in the lakhs place of 23,45,678?",
     "3",["2","4","5"]),
    (8765432,"The difference between the place value and face value of 7 in 87,65,432 is:",
     "7,00,000 - 7 = 6,99,993",
     ["700,000","7","699,993 (same)"]),
    (1234567,"If you interchange the digits in the thousands and tens place of 1,234,567, you get:",
     "1,234,567 → 1,237,564... thousands=4, tens=6 → 1,236,547",
     ["1,234,576","1,264,537","1,234,657"]),
    (9999999,"What is the largest 7-digit number?",
     "99,99,999",["9,999,999","1,00,00,000","99,999,99"]),
    (1000000,"What is the smallest 7-digit number?",
     "10,00,000 (Ten lakhs)",["1,000,000","99,99,999","9,99,999"]),
    (5432100,"In 54,32,100, the digit 3 is in which place?",
     "Ten-thousands (3 is in the ten-thousands place)",
     ["Thousands","Lakhs","Hundreds"]),
    (1234567,"The expanded form of 3,504 is:",
     "3000 + 500 + 0 + 4",["3,504","350 + 4","3500 + 4"]),
    (9800000,"98,00,000 in words is:",
     "Ninety-eight lakhs",["Nine crores eight lakhs","Ninety-eight million","Nine hundred eighty thousand"]),
    (1000000,"How many lakhs make one crore?",
     "100 lakhs",["10 lakhs","1000 lakhs","50 lakhs"]),
    (3000000,"30,00,000 ÷ 100 =",
     "30,000 (thirty thousand)",["3,000","3,00,000","3,000,000"]),
    (7654321,"Successor of 99,99,999 is:",
     "1,00,00,000 (one crore)",["99,99,998","9,99,99,999","1,00,000"]),
    (4567890,"Predecessor of 1,00,00,000 is:",
     "99,99,999",["1,00,00,001","9,99,99,999","99,999"]),
]

def gen_place_value(n=QPT):
    print(f"[Place Value] {n} questions...")
    for i,(num,qtext,correct,wrongs) in enumerate(NUMPLACE_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_place_value(num); url=upload_pil(img,f"pv_{i}")
        g=random.choice([3,4,5]); d=difficulty_for_grade(g)
        ok=post_q("Mathematics",g,d,"Number System","Place Value",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  pv_{i}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.25)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 2. FRACTIONS & DECIMALS VISUAL
# ══════════════════════════════════════════════════════════════════════════════

def draw_fraction_visual(numerator, denominator, show_decimal=False):
    img, draw = canvas(440, 300, "#FFF0F5")
    draw.text((20,12), f"Fraction: {numerator}/{denominator}", fill="#2C3E50", font=FONT_LG)
    # Draw divided rectangle
    total_parts = denominator
    part_w = min(320 // total_parts, 60)
    total_w = part_w * total_parts
    start_x = (440 - total_w) // 2
    y1, y2 = 70, 160
    for p in range(total_parts):
        bx = start_x + p * part_w
        fill = "#E74C3C" if p < numerator else "#FAFAFA"
        draw.rectangle([bx, y1, bx+part_w-2, y2], fill=fill, outline="#2C3E50", width=2)
    draw.text((start_x, y2+10), f"{numerator} shaded out of {denominator} equal parts", fill="#2C3E50", font=FONT_MD)
    frac_val = numerator / denominator
    draw.text((start_x, y2+38), f"= {numerator}/{denominator}", fill="#E74C3C", font=FONT_XL)
    if show_decimal:
        draw.text((start_x+80, y2+38), f"= {frac_val:.3f}".rstrip('0').rstrip('.'), fill="#3498DB", font=FONT_XL)
    # Percentage
    draw.text((start_x, y2+75), f"= {frac_val*100:.1f}%", fill="#27AE60", font=FONT_LG)
    return img

FRACTIONS_QA = [
    (1,2,"What fraction of the figure is shaded if 1 out of 2 equal parts is coloured?",
     "1/2",["1/3","2/3","1/4"]),
    (3,4,"3/4 as a decimal is:",
     "0.75",["0.34","0.743","7.5"]),
    (1,5,"1/5 as a percentage is:",
     "20%",["15%","25%","10%"]),
    (2,3,"Which fraction is greater: 2/3 or 3/4?",
     "3/4 (since 9/12 > 8/12)",["2/3","They are equal","Cannot compare"]),
    (3,8,"3/8 + 1/8 = ?",
     "4/8 = 1/2",["2/8","4/16","5/8"]),
    (5,6,"5/6 - 1/6 = ?",
     "4/6 = 2/3",["6/6","4/12","5/12"]),
    (3,5,"3/5 × 10 = ?",
     "6",["30/50","2","15/3"]),
    (2,4,"Which of these is an equivalent fraction of 2/4?",
     "1/2",["2/8","4/6","3/5"]),
    (7,10,"7/10 as a decimal is:",
     "0.7",["7.0","0.07","0.77"]),
    (1,4,"1/4 + 1/4 + 1/4 = ?",
     "3/4",["3/12","1/4","3/8"]),
    (2,5,"A pizza is cut into 5 equal slices. Ram eats 2 slices. What fraction is left?",
     "3/5",["2/5","2/3","3/10"]),
    (3,10,"0.3 as a fraction is:",
     "3/10",["3/100","1/3","30/100"]),
    (1,3,"1/3 of 27 = ?",
     "9",["3","8","7"]),
    (3,4,"A class of 40 students — 3/4 are present. How many students are present?",
     "30",["10","25","35"]),
    (5,8,"5/8 as a percentage (approximate) is:",
     "62.5%",["58%","55%","65%"]),
    (2,3,"2/3 ÷ 1/3 = ?",
     "2",["2/9","1/2","6"]),
    (3,7,"Which fraction is closest to 1/2 ? (3/7, 4/9, 5/11, 2/5)",
     "5/11 ≈ 0.454, closest to 0.5",["3/7 ≈ 0.429","4/9 ≈ 0.444","2/5 = 0.4"]),
    (4,5,"A bottle is 4/5 full. It has 800 mL. The full capacity is:",
     "1000 mL",["900 mL","960 mL","640 mL"]),
    (1,8,"What is 0.125 as a fraction?",
     "1/8",["1/4","1/5","1/12"]),
    (5,9,"Arrange in ascending order: 1/2, 5/9, 4/7",
     "1/2 < 4/7 < 5/9",["5/9 < 4/7 < 1/2","4/7 < 1/2 < 5/9","1/2 = 5/9"]),
]

def gen_fractions(n=QPT):
    print(f"[Fractions & Decimals] {n} questions...")
    for i,(num,den,qtext,correct,wrongs) in enumerate(FRACTIONS_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_fraction_visual(num,den,show_decimal=True); url=upload_pil(img,f"frac_{i}")
        g=random.choice([4,5,6,7]); d=difficulty_for_grade(g)
        ok=post_q("Mathematics",g,d,"Fractions and Decimals","Fractions",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  frac_{i} ({num}/{den})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.25)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 3. PERIMETER & AREA (Geometry)
# ══════════════════════════════════════════════════════════════════════════════

def draw_shape_with_dims(shape, dims, highlight=True):
    img, draw = canvas(460, 340, "#F8FBFF")
    draw.text((20,12), f"Geometry: {shape}", fill="#2C3E50", font=FONT_LG)
    color = "#3498DB"
    if shape == "Rectangle":
        l, w = dims
        bx1,by1,bx2,by2 = 80,80,380,220
        draw.rectangle([bx1,by1,bx2,by2], fill="#AED6F1", outline=color, width=3)
        # Dimension labels
        draw.text(((bx1+bx2)//2-12, by2+8), f"{l} cm", fill="#E74C3C", font=FONT_MD)
        draw.text((bx1-45, (by1+by2)//2-10), f"{w} cm", fill="#E74C3C", font=FONT_MD)
        draw.text((80,260), f"Area = l × w = {l} × {w} = {l*w} cm²", fill="#2C3E50", font=FONT_MD)
        draw.text((80,290), f"Perimeter = 2(l+w) = 2×{l+w} = {2*(l+w)} cm", fill="#2C3E50", font=FONT_MD)
    elif shape == "Square":
        s = dims[0]
        draw.rectangle([110,70,370,240], fill="#A9DFBF", outline="#27AE60", width=3)
        draw.text((215,248), f"{s} cm", fill="#E74C3C", font=FONT_MD)
        draw.text((80,270), f"Area = s² = {s}² = {s*s} cm²", fill="#2C3E50", font=FONT_MD)
        draw.text((80,300), f"Perimeter = 4s = 4×{s} = {4*s} cm", fill="#2C3E50", font=FONT_MD)
    elif shape == "Triangle":
        b, h = dims
        pts=[(230,70),(80,270),(380,270)]
        draw.polygon(pts, fill="#FAD7A0", outline="#E67E22", width=3)
        draw.text((185,278), f"base = {b} cm", fill="#E74C3C", font=FONT_MD)
        draw.line([(230,70),(230,270)], fill="#999", width=2)
        draw.text((235,165), f"h={h}", fill="#999", font=FONT_SM)
        draw.text((80,300), f"Area = ½×b×h = ½×{b}×{h} = {b*h//2} cm²", fill="#2C3E50", font=FONT_MD)
    elif shape == "Circle":
        r = dims[0]
        cx,cy=230,165
        draw.ellipse([cx-r*4,cy-r*4,cx+r*4,cy+r*4], fill="#D2B4DE", outline="#9B59B6", width=3)
        draw.line([(cx,cy),(cx+r*4,cy)], fill="#E74C3C", width=2)
        draw.text((cx+r*2, cy-18), f"r={r} cm", fill="#E74C3C", font=FONT_MD)
        draw.text((60,290), f"Area = πr² ≈ 3.14×{r}² = {3.14*r*r:.1f} cm²", fill="#2C3E50", font=FONT_MD)
        draw.text((60,318), f"Circumference = 2πr ≈ {2*3.14*r:.1f} cm", fill="#2C3E50", font=FONT_MD)
    return img

GEO_QA = [
    ("Rectangle",(8,5),"A rectangle has length 8 cm and width 5 cm. Its area is:",
     "40 cm²",["13 cm²","26 cm²","80 cm²"]),
    ("Rectangle",(12,7),"A rectangle's perimeter is 38 cm. If length = 12 cm, width is:",
     "7 cm",["19 cm","14 cm","26 cm"]),
    ("Square",(6,),"A square has side 6 cm. Its area is:",
     "36 cm²",["24 cm²","12 cm²","30 cm²"]),
    ("Square",(9,),"A square's perimeter is 36 cm. Its side length is:",
     "9 cm",["4 cm","12 cm","6 cm"]),
    ("Triangle",(10,6),"A triangle with base 10 cm and height 6 cm has area:",
     "30 cm²",["60 cm²","16 cm²","15 cm²"]),
    ("Circle",(7,),"A circle with radius 7 cm has area approximately (π ≈ 22/7):",
     "154 cm²",["44 cm²","22 cm²","308 cm²"]),
    ("Circle",(14,),"A circle with diameter 14 cm has circumference approximately:",
     "44 cm",["154 cm","28 cm","88 cm"]),
    ("Rectangle",(15,10),"A room is 15 m × 10 m. The cost of tiling at ₹80/m² is:",
     "₹12,000",["₹2,000","₹24,000","₹1,500"]),
    ("Square",(5,),"The area of a square is 64 cm². Its side is:",
     "8 cm",["16 cm","4 cm","32 cm"]),
    ("Triangle",(12,8),"A right-angled triangle has legs 3 cm and 4 cm. Its hypotenuse is:",
     "5 cm",["7 cm","6 cm","12 cm"]),
    ("Rectangle",(6,4),"Which has greater area: a 6×4 rectangle or a 5×5 square?",
     "5×5 square (25 cm² vs 24 cm²)",["6×4 rectangle","They are equal","Cannot compare"]),
    ("Circle",(10,),"The area of a circle doubles if the radius is:",
     "Multiplied by √2 (≈ 1.41)",["Doubled","Tripled","Halved"]),
    ("Square",(7,),"If the side of a square is doubled, its area becomes:",
     "4 times the original",["2 times","3 times","8 times"]),
    ("Rectangle",(20,5),"A rectangular garden is 20 m × 5 m. Fencing cost ₹50/m. Total fencing cost:",
     "₹2,500",["₹5,000","₹1,000","₹4,500"]),
    ("Triangle",(10,8),"The area of an equilateral triangle with side 6 cm is:",
     "9√3 ≈ 15.6 cm²",["36 cm²","18 cm²","12 cm²"]),
    ("Circle",(5,),"A circular track has radius 35 m. One round = (π=22/7):",
     "220 m",["110 m","70 m","440 m"]),
    ("Square",(8,),"Diagonal of a square with side 8 cm = ?",
     "8√2 ≈ 11.3 cm",["16 cm","8 cm","4√2 cm"]),
    ("Rectangle",(9,6),"A rectangular plot 9 m × 6 m. A path 1 m wide runs inside. Inner area:",
     "7×4 = 28 m²",["54 m²","48 m²","14 m²"]),
    ("Circle",(3,),"The ratio of circumference to diameter of any circle is:",
     "π (pi) ≈ 3.14159...",["2","√2","22"]),
    ("Triangle",(5,4),"In a triangle, if base = 5 and height = 4, area = ?",
     "10 sq units",["20","9","14"]),
]

def gen_geometry(n=QPT):
    print(f"[Perimeter & Area] {n} questions...")
    for i,(shape,dims,qtext,correct,wrongs) in enumerate(GEO_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_shape_with_dims(shape,dims); url=upload_pil(img,f"geo_{i}")
        g=random.choice([5,6,7,8]); d=difficulty_for_grade(g)
        ok=post_q("Mathematics",g,d,"Geometry","Perimeter and Area",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  geo_{i} ({shape})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.25)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 4. DATA HANDLING / GRAPHS
# ══════════════════════════════════════════════════════════════════════════════

def draw_bar_chart(data, title="Bar Chart"):
    img, draw = canvas(500, 360, "#FAFAFA")
    draw.text((20,12), title, fill="#2C3E50", font=FONT_LG)
    colors=["#E74C3C","#3498DB","#27AE60","#F39C12","#9B59B6","#1ABC9C"]
    max_val = max(v for _,v in data)
    chart_h = 220; chart_y_top = 50; chart_x = 60; bar_w = min(55, (400//len(data))-10)
    # Axes
    draw.line([(chart_x,chart_y_top),(chart_x,chart_y_top+chart_h)], fill="#2C3E50", width=3)
    draw.line([(chart_x,chart_y_top+chart_h),(460,chart_y_top+chart_h)], fill="#2C3E50", width=3)
    # Y-axis labels
    for val in range(0,max_val+1,max(1,max_val//5)):
        y = chart_y_top + chart_h - int(val/max_val * chart_h)
        draw.line([(chart_x-5,y),(chart_x,y)], fill="#2C3E50", width=1)
        draw.text((20,y-8), str(val), fill="#555", font=FONT_SM)
    # Bars
    for i,(label,val) in enumerate(data):
        bx = chart_x + 15 + i*(bar_w+15)
        bh = int(val/max_val * chart_h)
        by = chart_y_top + chart_h - bh
        draw.rectangle([bx,by,bx+bar_w,chart_y_top+chart_h], fill=colors[i%len(colors)], outline="#2C3E50",width=1)
        draw.text((bx+bar_w//2-len(str(val))*4, by-18), str(val), fill="#2C3E50", font=FONT_SM)
        lbl = label[:6]
        draw.text((bx+bar_w//2-len(lbl)*4, chart_y_top+chart_h+5), lbl, fill="#2C3E50", font=FONT_SM)
    return img

def draw_line_graph(data, title="Line Graph"):
    img, draw = canvas(500, 340, "#FAFAFA")
    draw.text((20,12), title, fill="#2C3E50", font=FONT_LG)
    max_val = max(v for _,v in data); min_val = min(v for _,v in data)
    chart_h=220; chart_y_top=50; chart_x=60; chart_w=400
    draw.line([(chart_x,chart_y_top),(chart_x,chart_y_top+chart_h)], fill="#2C3E50", width=3)
    draw.line([(chart_x,chart_y_top+chart_h),(chart_x+chart_w,chart_y_top+chart_h)], fill="#2C3E50", width=3)
    n=len(data); x_gap=chart_w//(n-1) if n>1 else 1
    points=[]
    for i,(label,val) in enumerate(data):
        px=chart_x+i*x_gap; py=chart_y_top+chart_h-int((val-0)/(max_val+1)*chart_h)
        points.append((px,py))
        draw.ellipse([px-5,py-5,px+5,py+5],fill="#E74C3C")
        draw.text((px-len(label)*4,chart_y_top+chart_h+5),label,fill="#555",font=FONT_SM)
        draw.text((px-10,py-18),str(val),fill="#2C3E50",font=FONT_SM)
    for i in range(len(points)-1):
        draw.line([points[i],points[i+1]],fill="#3498DB",width=3)
    return img

GRAPH_DATA_SETS = [
    ("Monthly Rainfall", [("Jan",20),("Feb",15),("Mar",25),("Apr",40),("May",60),("Jun",180)]),
    ("Favourite Sports",  [("Cricket",45),("Football",30),("Badminton",15),("Tennis",10)]),
    ("Scores in Test",    [("Arjun",85),("Priya",92),("Rahul",78),("Sneha",95),("Vivek",88)]),
    ("Temp (°C)",         [("Mon",28),("Tue",30),("Wed",27),("Thu",32),("Fri",35),("Sat",33)]),
    ("Books Read",        [("Jan",3),("Feb",4),("Mar",2),("Apr",5),("May",4),("Jun",6)]),
]

GRAPH_QA = [
    (0,"bar","In the rainfall bar chart, which month has the highest rainfall?",
     "June (180 mm)",["March","April","May"]),
    (0,"bar","In the rainfall chart, what is the total rainfall for Jan and Feb?",
     "35 mm (20+15)",["25","15","40"]),
    (1,"bar","In the Favourite Sports chart, how many more students prefer Cricket than Football?",
     "15 (45-30)",["30","75","45"]),
    (1,"bar","What fraction of students prefer Badminton in the sports chart?",
     "15/100 = 3/20",["1/4","1/3","1/6"]),
    (2,"bar","In the Scores chart, who scored highest?",
     "Sneha (95)",["Priya","Arjun","Vivek"]),
    (2,"bar","What is the average score in the test? (85+92+78+95+88)/5",
     "87.6",["88","85","90"]),
    (3,"line","In the temperature line graph, on which day was it hottest?",
     "Friday (35°C)",["Thursday","Saturday","Monday"]),
    (3,"line","In the temperature graph, the temperature rose from Monday to Tuesday by:",
     "2°C (28→30)",["5°C","3°C","7°C"]),
    (4,"line","In the Books Read graph, in which month were the most books read?",
     "June (6 books)",["May","February","April"]),
    (4,"line","What is the total books read in the first 3 months?",
     "9 (3+4+2)",["7","12","8"]),
    (0,"bar","A bar chart and a pie chart both show the SAME data. The bar chart is better when:",
     "Comparing quantities directly",["Showing parts of a whole","Showing trends over time","Showing percentages"]),
    (1,"bar","In a pictograph, each symbol = 5 students. If 4 symbols shown, how many students?",
     "20",["4","25","45"]),
    (2,"bar","Mean (average) of 5, 8, 11, 14, 17 is:",
     "11",["9","13","10"]),
    (3,"line","Median of 3, 7, 9, 12, 15 is:",
     "9 (middle value)",["7","12","10"]),
    (4,"line","Mode of 4, 5, 5, 6, 5, 7, 8, 5 is:",
     "5 (appears most often)",["4","6","7"]),
    (0,"bar","Range of data set 15, 28, 7, 42, 19 is:",
     "35 (42-7)",["27","15","42"]),
    (1,"bar","A pie chart shows 90° for 'Science'. What percentage does Science represent?",
     "25% (90/360 × 100)",["90%","45%","30%"]),
    (2,"bar","In a frequency table, the tally |||| | represents:",
     "6",["5","4","7"]),
    (3,"line","A line graph is most useful for showing:",
     "Trends / changes over time",["Parts of a whole","Comparisons","Frequency"]),
    (4,"line","If data values are 10, 20, 30, 40, 50, the mean is:",
     "30",["25","35","20"]),
]

def gen_graphs(n=QPT):
    print(f"[Data Handling & Graphs] {n} questions...")
    for i,(ds_idx,gtype,qtext,correct,wrongs) in enumerate(GRAPH_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        title,data = GRAPH_DATA_SETS[ds_idx]
        if gtype=="bar":
            img=draw_bar_chart(data,title)
        else:
            img=draw_line_graph(data,title)
        url=upload_pil(img,f"graph_{i}")
        g=random.choice([5,6,7,8]); d=difficulty_for_grade(g)
        ok=post_q("Mathematics",g,d,"Data Handling","Charts and Graphs",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  graph_{i} ({gtype})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.25)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 5. LR: BLOOD RELATIONS
# ══════════════════════════════════════════════════════════════════════════════

def draw_family_tree(members, relations):
    img, draw = canvas(520, 380, "#FFF8E7")
    draw.text((150,12), "Family Tree", fill="#2C3E50", font=FONT_LG)
    # Draw nodes and edges
    for name,(x,y),gender in members:
        color="#3498DB" if gender=="M" else "#E74C3C"
        shape_r=28
        if gender=="M":
            draw.rectangle([x-shape_r,y-shape_r,x+shape_r,y+shape_r],fill=color,outline="#2C3E50",width=2)
        else:
            draw.ellipse([x-shape_r,y-shape_r,x+shape_r,y+shape_r],fill=color,outline="#2C3E50",width=2)
        tw=len(name)*7
        draw.text((x-tw//2,y-10),name,fill="white",font=FONT_MD)
    for (n1,n2,rel) in relations:
        pos1=next(p for n,p,g in members if n==n1)
        pos2=next(p for n,p,g in members if n==n2)
        draw.line([pos1,pos2],fill="#7F8C8D",width=2)
        mx=(pos1[0]+pos2[0])//2; my=(pos1[1]+pos2[1])//2
        draw.text((mx+3,my-8),rel,fill="#555",font=FONT_SM)
    draw.text((20,345),"■ = Male   ● = Female",fill="#555",font=FONT_MD)
    return img

FAMILY1 = ([("Ram",(100,80),"M"),("Sita",(250,80),"F"),("Lakshman",(400,80),"M"),
             ("Ravi",(180,200),"M"),("Gita",(320,200),"F")],
           [("Ram","Sita","couple"),("Sita","Ravi","son"),("Sita","Gita","daughter"),("Lakshman","Ram","brother")])

FAMILY2 = ([("Raj",(120,70),"M"),("Priya",(300,70),"F"),("Mohan",(120,200),"M"),
             ("Anita",(300,200),"F"),("Dev",(210,320),"M")],
           [("Raj","Priya","married"),("Raj","Mohan","father"),("Priya","Anita","daughter"),("Mohan","Dev","son"),("Anita","Dev","siblings")])

BLOOD_QA = [
    (FAMILY1,"In the family tree, what is Ravi's relationship to Ram?",
     "Son",["Brother","Nephew","Father"]),
    (FAMILY1,"How is Lakshman related to Ravi?",
     "Uncle (Lakshman is Ram's brother, Ram is Ravi's father)",
     ["Brother","Father","Grandfather"]),
    (FAMILY1,"Gita calls Ram her:",
     "Father",["Uncle","Brother","Grandfather"]),
    (FAMILY2,"Dev's mother is Mohan's:",
     "Sister-in-law (Anita is married to Mohan's sibling... or mother of Dev through Anita)",
     ["Wife","Mother","Daughter"]),
    (FAMILY1,"If Ram and Sita have a third child (a boy), he would be Gita's:",
     "Brother",["Cousin","Uncle","Father"]),
    (FAMILY1,"Pointing to a photo, Ravi says 'He is my father's brother's son.' This person is Ravi's:",
     "Cousin",["Brother","Uncle","Nephew"]),
    (FAMILY2,"Raj is Priya's:",
     "Husband",["Father","Son","Brother"]),
    (FAMILY1,"If Sita's father is alive, what is he to Ravi?",
     "Maternal grandfather",["Paternal grandfather","Uncle","Great-uncle"]),
    (FAMILY2,"Dev calls Raj his:",
     "Grandfather (Raj is Mohan's father, Mohan is Dev's father)",
     ["Father","Uncle","Grand-uncle"]),
    (FAMILY1,"Gita's mother's brother is her:",
     "Maternal uncle (mama)",["Paternal uncle","Father","Cousin"]),
    (FAMILY1,"'A is B's sister. B is C's brother. C is D's father. How is A related to D?'",
     "Aunt (A is father's sister)",["Sister","Mother","Grandmother"]),
    (FAMILY2,"'P's mother is Q's daughter. How is Q related to P?'",
     "Maternal grandmother",["Mother","Aunt","Sister"]),
    (FAMILY1,"'X is Y's son. Y is Z's father. Z is W's brother. What is X to W?'",
     "Paternal uncle",["Brother","Father","Cousin"]),
    (FAMILY2,"'A's father's only daughter is B. How is B related to A?'",
     "Sister",["Mother","Aunt","Cousin"]),
    (FAMILY1,"'If M is the son of N, and N is the sister of O, then M is O's:'",
     "Nephew",["Son","Cousin","Uncle"]),
]

def gen_blood_relations(n=QPT):
    n=min(n,len(BLOOD_QA))
    print(f"[Blood Relations] {n} questions...")
    families=[FAMILY1,FAMILY2]
    for i,(fam,qtext,correct,wrongs) in enumerate(BLOOD_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        members,relations=fam
        img=draw_family_tree(members,relations); url=upload_pil(img,f"blood_{i}")
        g=random.choice([5,6,7,8,9]); d=difficulty_for_grade(g)
        ok=post_q("Logical Reasoning",g,d,"Blood Relations","Family Tree",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  blood_{i}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.25)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 6. LR: DIRECTION & DISTANCE
# ══════════════════════════════════════════════════════════════════════════════

def draw_direction_path(steps):
    """steps = list of (direction, distance, label) e.g. [('N',3,''),('E',4,'')]"""
    img, draw = canvas(480, 440, "#F0FFF0")
    draw.text((20,12), "Direction & Distance Problem", fill="#2C3E50", font=FONT_LG)
    # Compass rose
    cx,cy=400,60; r=30
    draw.text((cx-6,cy-r-16),"N",fill="#E74C3C",font=FONT_MD)
    draw.text((cx-6,cy+r+2),"S",fill="#3498DB",font=FONT_MD)
    draw.text((cx+r+4,cy-8),"E",fill="#2C3E50",font=FONT_MD)
    draw.text((cx-r-18,cy-8),"W",fill="#2C3E50",font=FONT_MD)
    draw.line([(cx,cy-r),(cx,cy+r)],fill="#888",width=2)
    draw.line([(cx-r,cy),(cx+r,cy)],fill="#888",width=2)
    # Draw path
    scale=25; px,py=240,280  # start point
    dirs={"N":(0,-1),"S":(0,1),"E":(1,0),"W":(-1,0),"NE":(1,-1),"NW":(-1,-1),"SE":(1,1),"SW":(-1,1)}
    draw.ellipse([px-8,py-8,px+8,py+8],fill="#27AE60")
    draw.text((px+5,py-20),"Start",fill="#27AE60",font=FONT_SM)
    step_colors=["#E74C3C","#3498DB","#E67E22","#9B59B6","#1ABC9C"]
    for si,(direction,distance,lbl) in enumerate(steps):
        dx,dy=dirs.get(direction,(0,0)); ex=px+dx*distance*scale; ey=py+dy*distance*scale
        draw.line([(px,py),(ex,ey)],fill=step_colors[si%len(step_colors)],width=3)
        # Arrowhead
        draw.polygon([(ex,ey),(ex-dx*8-dy*6,ey-dy*8+dx*6),(ex-dx*8+dy*6,ey-dy*8-dx*6)],fill=step_colors[si%len(step_colors)])
        mx=(px+ex)//2; my=(py+ey)//2
        step_label=f"{si+1}.{direction},{distance}km"
        draw.text((mx+4,my-8),step_label,fill=step_colors[si%len(step_colors)],font=FONT_SM)
        px,py=ex,ey
    draw.ellipse([px-8,py-8,px+8,py+8],fill="#E74C3C")
    draw.text((px+5,py-20),"End",fill="#E74C3C",font=FONT_SM)
    return img

DIRECTION_QA = [
    ([("N",3,""),("E",4,"")],"A man walks 3 km North then 4 km East. How far is he from start?",
     "5 km (Pythagoras: √(3²+4²)=5)",["7 km","1 km","6 km"]),
    ([("E",5,""),("N",0,""),("W",3,"")],"Arjun walks 5 km East, then 3 km West. Net displacement is:",
     "2 km East",["8 km","5 km","3 km"]),
    ([("N",6,""),("E",8,"")],"Walking 6 km North and 8 km East. Straight-line distance from start:",
     "10 km (√(6²+8²)=10)",["14 km","2 km","7 km"]),
    ([("W",4,""),("S",3,"")],"A person walks 4 km West then 3 km South. Distance from origin:",
     "5 km",["7 km","1 km","12 km"]),
    ([("N",5,""),("E",5,"")],"If you face North and turn 90° clockwise, you now face:",
     "East",["West","South","Northeast"]),
    ([("E",3,""),("S",4,"")],"Starting from home facing East, Priya turns right. She now faces:",
     "South",["North","West","East"]),
    ([("N",10,""),("E",6,""),("S",10,"")],"Ram walks 10 km North, 6 km East, then 10 km South. He is now:",
     "6 km East of start",["10 km North","Back at start","6 km West"]),
    ([("W",7,""),("N",0,""),("E",7,"")],"Seema walks West 7 km, then turns and walks East 7 km. She is:",
     "Back at starting point",["14 km West","7 km West","7 km East"]),
    ([("N",4,""),("E",3,""),("S",4,""),("W",3,"")],"If a person walks 4 km North, 3 km East, 4 km South, 3 km West — final position:",
     "Back at starting point (a rectangle)",["3 km East","4 km North","1 km Northeast"]),
    ([("N",5,""),("E",12,"")],"Walking 5 km North then 12 km East, straight-line from start:",
     "13 km (5-12-13 right triangle)",["17 km","7 km","10 km"]),
    ([("S",6,""),("E",8,"")],"If you face East and turn anti-clockwise 90°, you face:",
     "North",["South","West","East"]),
    ([("N",3,""),("W",4,"")],"3 km North then 4 km West, distance from start:",
     "5 km",["7 km","1 km","6 km"]),
    ([("E",10,""),("N",0,"")],"You are facing South. After turning 180°, you face:",
     "North",["East","West","Southwest"]),
    ([("N",8,""),("E",6,""),("S",3,"")],"After walking 8 km N, 6 km E, 3 km S, how far North are you from start?",
     "5 km North",["8 km","3 km","11 km"]),
    ([("W",5,""),("S",5,"")],"A bird flies 5 km West then 5 km South. Straight-line distance:",
     "5√2 ≈ 7.07 km",["10 km","0 km","5 km"]),
]

def gen_directions(n=QPT):
    n=min(n,len(DIRECTION_QA))
    print(f"[Direction & Distance] {n} questions...")
    for i,(steps,qtext,correct,wrongs) in enumerate(DIRECTION_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_direction_path(steps); url=upload_pil(img,f"dir_{i}")
        g=random.choice([5,6,7,8,9]); d=difficulty_for_grade(g)
        ok=post_q("Logical Reasoning",g,d,"Direction and Distance","Navigation",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  dir_{i}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.25)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 7. ENVIRONMENT & CONSERVATION
# ══════════════════════════════════════════════════════════════════════════════

def draw_environment(scene):
    img, draw = canvas(500, 360, "#E8F5E9")
    draw.text((20,12), f"Environment: {scene.replace('_',' ').title()}", fill="#2C3E50", font=FONT_MD)

    if scene == "3r_reduce":
        # 3R triangle
        labels=[("Reduce","#E74C3C",240,100),("Reuse","#3498DB",140,250),("Recycle","#27AE60",340,250)]
        draw.polygon([(240,70),(100,280),(380,280)],fill="#F9F9F9",outline="#2C3E50",width=3)
        for label,color,lx,ly in labels:
            draw.ellipse([lx-45,ly-25,lx+45,ly+25],fill=color)
            tw=len(label)*7; draw.text((lx-tw//2,ly-10),label,fill="white",font=FONT_MD)
        draw.text((70,310),"3R Principle: Reduce, Reuse, Recycle",fill="#2C3E50",font=FONT_MD)

    elif scene == "greenhouse":
        # Earth with atmosphere layers
        draw.ellipse([150,80,350,280],fill="#4FC3F7",outline="#0288D1",width=3)
        draw.text((210,168),"Earth",fill="white",font=FONT_LG)
        # Atmosphere ring
        draw.ellipse([120,50,380,310],outline="#FF8F00",width=4)
        draw.text((260,55),"Atmosphere",fill="#FF8F00",font=FONT_SM)
        # Sun rays
        for angle in [30,60,90,120]:
            rad=math.radians(angle); sx=500+int(200*math.cos(rad)); sy=80+int(200*math.sin(rad))
            draw.line([(500,80),(sx,sy)],fill="#FFD700",width=2)
        draw.text((30,320),"Greenhouse gases trap heat → global warming",fill="#2C3E50",font=FONT_SM)

    elif scene == "deforestation":
        # Trees on left, stumps on right
        for tx,ty in [(80,200),(120,180),(160,200)]:
            draw.polygon([(tx,ty-80),(tx-30,ty),(tx+30,ty)],fill="#27AE60")
            draw.rectangle([tx-8,ty,tx+8,ty+40],fill="#8B4513")
        # Stumps on right
        for sx,sy in [(280,240),(340,240),(400,240)]:
            draw.rectangle([sx-15,sy-15,sx+15,sy],fill="#8B4513")
            draw.ellipse([sx-15,sy-20,sx+15,sy],fill="#A0522D")
        draw.text((210,200),"→",fill="#E74C3C",font=FONT_XXL)
        draw.text((50,295),"Deforestation: loss of forests due to human activity",fill="#2C3E50",font=FONT_SM)

    elif scene == "water_conservation":
        # Tap with drop
        draw.rectangle([210,50,270,120],fill="#888")
        draw.rectangle([175,110,305,140],fill="#888")
        # Water drop
        pts=[(240,145),(215,200),(240,230),(265,200)]
        draw.polygon(pts,fill="#3498DB")
        # X over tap (wastage)
        draw.line([(180,55),(300,130)],fill="#E74C3C",width=4)
        draw.line([(300,55),(180,130)],fill="#E74C3C",width=4)
        draw.text((80,275),"Save water — every drop counts!",fill="#2C3E50",font=FONT_LG)
        draw.text((80,310),"Only 3% of Earth's water is fresh water",fill="#555",font=FONT_MD)

    return img

ENV_QA = [
    ("3r_reduce","The 3R principle stands for:",
     "Reduce, Reuse, Recycle",["Read, Research, Report","Run, Rest, Recover","Red, Round, Rigid"]),
    ("greenhouse","Greenhouse gases that cause global warming include:",
     "CO₂, methane, water vapour, nitrous oxide",
     ["Oxygen, nitrogen, argon","Helium, neon","Hydrogen, oxygen"]),
    ("deforestation","Deforestation leads to:",
     "Loss of biodiversity, soil erosion and climate change",
     ["More rainfall","Cooler temperatures","Better air quality"]),
    ("water_conservation","Only about _____ % of Earth's water is fresh water:",
     "3%",["97%","50%","25%"]),
    ("3r_reduce","Which of these is an example of REDUCING waste?",
     "Using a refillable water bottle instead of disposable ones",
     ["Throwing old newspapers away","Buying a new phone every year","Leaving lights on"]),
    ("greenhouse","The main cause of global warming is:",
     "Increased greenhouse gases from burning fossil fuels",
     ["More trees","Ozone layer","Volcanic eruptions"]),
    ("deforestation","Afforestation means:",
     "Planting trees in areas where there were none",
     ["Cutting trees","Removing roots","Mining for minerals"]),
    ("water_conservation","Drip irrigation helps to:",
     "Deliver water directly to plant roots, reducing waste",
     ["Increase water usage","Flood crops","Evaporate water faster"]),
    ("3r_reduce","Biodegradable waste can be:",
     "Broken down naturally by microorganisms",
     ["Recycled into plastic","Converted to oil","Turned into electricity directly"]),
    ("greenhouse","Which gas is mainly responsible for ozone layer depletion?",
     "CFCs (chlorofluorocarbons)",["CO₂","Methane","Nitrogen"]),
    ("deforestation","The Amazon Rainforest is called the 'lungs of the Earth' because:",
     "It produces 20% of the world's oxygen through photosynthesis",
     ["It stores rainwater","Animals breathe there","It has the most animals"]),
    ("water_conservation","Rainwater harvesting involves:",
     "Collecting and storing rainwater for future use",
     ["Boiling rain water","Releasing water into drains","Filtering seawater"]),
    ("3r_reduce","Composting is an example of which R?",
     "Recycle (organic waste → compost/fertiliser)",
     ["Reduce","Reuse","Remove"]),
    ("greenhouse","The Kyoto Protocol and Paris Agreement are international treaties for:",
     "Reducing greenhouse gas emissions",
     ["Nuclear disarmament","Ocean conservation","Protecting rainforests only"]),
    ("deforestation","Soil erosion is caused by:",
     "Removal of vegetation / deforestation, wind and water",
     ["Planting more trees","Increased rainfall only","Building dams"]),
]

def gen_environment(n=QPT):
    n=min(n,len(ENV_QA))
    print(f"[Environment & Conservation] {n} questions...")
    scenes=["3r_reduce","greenhouse","deforestation","water_conservation"]
    for i,(scene,qtext,correct,wrongs) in enumerate(ENV_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_environment(scene); url=upload_pil(img,f"env_{i}")
        g=random.choice([5,6,7,8]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Environment","Conservation and Ecology",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  env_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.25)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*60)
    print("OlympiadReady — Final Generator Batch 5")
    print("="*60)
    print()

    gen_place_value(QPT)
    gen_fractions(QPT)
    gen_geometry(QPT)
    gen_graphs(QPT)
    gen_blood_relations(QPT)
    gen_directions(QPT)
    gen_environment(QPT)

    print("="*60)
    print(f"DONE — Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}")
    print("="*60)
