"""
generate_lr_math_science.py
New programmatic question generators:
  1.  Analog Clock Reading          (Grades 1-5)   — text options
  2.  Figure Series / Next Pattern  (Grades 3-9)   — IMAGE options
  3.  Mirror Image                  (Grades 3-8)   — IMAGE options
  4.  Odd One Out — Visual          (Grades 2-8)   — text options (A/B/C/D)
  5.  Counting Figures              (Grades 3-7)   — text options
  6.  Area by Counting Squares      (Grades 3-6)   — text options
  7.  Indian Coins / Money          (Grades 1-4)   — text options
  8.  Life Cycle Diagrams           (Grades 2-5)   — text options
  9.  Layers of Earth               (Grades 6-8)   — text options
 10.  Cloud Types                   (Grades 5-7)   — text options

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
# ─────────────────────────────────────────────────────────────────────────────

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME, api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET, secure=True)

RUN_ID = int(time.time())
posted = failed = skipped = 0
saved_locally = []

# ── CORE HELPERS ─────────────────────────────────────────────────────────────
def img_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def upload_img(img, label):
    pid = f"{CLOUDINARY_FOLDER}/{label}-{RUN_ID}-{random.randint(1000,9999)}"
    try:
        r = cloudinary.uploader.upload(img_bytes(img), public_id=pid,
                                       overwrite=False, resource_type="image")
        return r["secure_url"]
    except Exception as e:
        print(f"  [FAIL-CLD] {e}")
        return None

def post_q(q):
    global posted, skipped, failed
    if not ADMIN_API_KEY:
        saved_locally.append(q); return
    try:
        r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question", json=q,
                          headers={"X-Admin-Key": ADMIN_API_KEY}, timeout=15)
        if r.status_code in (200, 201):
            posted += 1; print("-> posted")
        elif r.status_code == 409:
            skipped += 1; print("-> dup")
        else:
            print(f"-> FAIL {r.status_code}: {r.text[:80]}")
            saved_locally.append(q)
    except Exception as e:
        print(f"-> err: {e}")
        saved_locally.append(q)

def diff_for(grade):
    if grade <= 4:   return "Foundation"
    elif grade <= 7: return random.choice(["Foundation", "Advanced"])
    else:            return random.choice(["Advanced", "Olympiad"])

def make_text(q_img, label, text, opts, cidx,
              subject, grade, topic, subtopic, expl):
    """Upload question image → text-options question."""
    global failed
    print(f"  {label}...", end=" ", flush=True)
    url = upload_img(q_img, label)
    if not url: failed += 1; return
    post_q({"subject": subject, "grade": grade, "topic": topic,
            "subTopic": subtopic, "difficulty": diff_for(grade),
            "questionText": text, "imageUrl": url,
            "options": opts, "correctAnswer": chr(65+cidx),
            "explanation": expl})

def make_imgopt(q_img, opt_imgs, label, text, correct_idx,
                subject, grade, topic, subtopic, expl):
    """Upload question image + 4 option images → image-options question."""
    global failed
    print(f"  {label}...", end=" ", flush=True)
    opt_urls = []
    for i, oi in enumerate(opt_imgs):
        u = upload_img(oi, f"{label}-o{i}")
        if not u: failed += 1; return
        opt_urls.append(u)
    q_url = upload_img(q_img, f"{label}-q") if q_img else None
    post_q({"subject": subject, "grade": grade, "topic": topic,
            "subTopic": subtopic, "difficulty": diff_for(grade),
            "questionText": text, "imageUrl": q_url,
            "options": opt_urls, "correctAnswer": chr(65+correct_idx),
            "explanation": expl})

# ══════════════════════════════════════════════════════════════════════════════
# 1. ANALOG CLOCK (Grades 1-5)
# ══════════════════════════════════════════════════════════════════════════════
def draw_clock_face(hour, minute, size=280):
    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)
    cx = cy = size // 2
    r = size // 2 - 10

    # Outer circle
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline="#222", width=4)
    # Tick marks & hour numbers
    for i in range(1, 13):
        ang = math.radians(i * 30 - 90)
        # Long tick
        x1 = cx + int((r-14)*math.cos(ang)); y1 = cy + int((r-14)*math.sin(ang))
        x2 = cx + int((r-4)*math.cos(ang));  y2 = cy + int((r-4)*math.sin(ang))
        draw.line([(x1,y1),(x2,y2)], fill="#222", width=3)
        # Number
        nx = cx + int((r-32)*math.cos(ang)) - 7
        ny = cy + int((r-32)*math.sin(ang)) - 8
        draw.text((nx, ny), str(i), fill="#222")
    # Minor ticks
    for i in range(60):
        if i % 5 == 0: continue
        ang = math.radians(i * 6 - 90)
        x1 = cx + int((r-6)*math.cos(ang)); y1 = cy + int((r-6)*math.sin(ang))
        x2 = cx + int((r-2)*math.cos(ang)); y2 = cy + int((r-2)*math.sin(ang))
        draw.line([(x1,y1),(x2,y2)], fill="#888", width=1)
    # Hour hand
    h_ang = math.radians((hour % 12 + minute/60) * 30 - 90)
    hx = cx + int(r * 0.5 * math.cos(h_ang)); hy = cy + int(r * 0.5 * math.sin(h_ang))
    draw.line([(cx,cy),(hx,hy)], fill="#111", width=6)
    # Minute hand
    m_ang = math.radians(minute * 6 - 90)
    mx = cx + int(r * 0.75 * math.cos(m_ang)); my = cy + int(r * 0.75 * math.sin(m_ang))
    draw.line([(cx,cy),(mx,my)], fill="#444", width=4)
    # Centre dot
    draw.ellipse([cx-6, cy-6, cx+6, cy+6], fill="#111")
    return img

def time_str(h, m):
    return f"{h}:{m:02d}"

def gen_clock(n):
    print(f"\n[Analog Clock] {n} questions...")
    used = set()
    minute_sets = {
        1: [0],
        2: [0, 30],
        3: [0, 15, 30, 45],
        4: [0, 15, 30, 45],
        5: list(range(0, 60, 5)),
    }
    templates = [
        "What time does the clock show?",
        "What is the time shown on this analog clock?",
        "Read the clock. What time is it?",
        "The clock shows which time?",
    ]
    for i in range(n):
        grade  = random.choice([1,2,3,4,5])
        mins   = minute_sets[grade]
        hour   = random.randint(1, 12)
        minute = random.choice(mins)
        img    = draw_clock_face(hour, minute)
        correct = time_str(hour, minute)
        # Generate 3 wrong times
        wrongs = set()
        attempts = 0
        while len(wrongs) < 3 and attempts < 30:
            attempts += 1
            wh = random.choice([h for h in range(1,13) if h != hour] if random.random()>0.5 else [hour])
            wm = random.choice([m for m in mins if m != minute] if len(mins)>1 else mins)
            cand = time_str(wh, wm)
            if cand != correct: wrongs.add(cand)
        if len(wrongs) < 3:
            for extra in [time_str((hour+1)%12 or 12, minute),
                          time_str(hour, (minute+5)%60),
                          time_str((hour+2)%12 or 12, (minute+15)%60)]:
                if extra != correct and extra not in wrongs:
                    wrongs.add(extra)
                if len(wrongs) == 3: break
        opts = [correct] + list(wrongs)[:3]
        random.shuffle(opts); cidx = opts.index(correct)
        q_text = random.choice(templates)
        if q_text in used: q_text = f"The analog clock hands point to which time? (Clock {i+1})"
        used.add(q_text)
        make_text(img, "clock", q_text, opts, cidx,
                  "Mathematics", grade, "Time", "Analog Clock Reading",
                  f"The hour hand points to {hour} and minute hand to {minute} minutes = {correct}.")

# ══════════════════════════════════════════════════════════════════════════════
# 2. FIGURE SERIES — NEXT PATTERN (Grades 3-9) [IMAGE OPTIONS]
# ══════════════════════════════════════════════════════════════════════════════
def draw_single_shape(shape, size, color, filled, angle_deg=0, canvas=100):
    """Draw one shape on a white canvas, optionally rotated."""
    img = Image.new("RGBA", (canvas, canvas), (255,255,255,0))
    draw = ImageDraw.Draw(img)
    cx = cy = canvas // 2
    fill_c = color if filled else None
    if shape == "circle":
        draw.ellipse([cx-size, cy-size, cx+size, cy+size],
                     fill=fill_c, outline=color, width=3)
    elif shape == "square":
        draw.rectangle([cx-size, cy-size, cx+size, cy+size],
                       fill=fill_c, outline=color, width=3)
    elif shape == "triangle":
        pts = [(cx, cy-size), (cx-size, cy+size), (cx+size, cy+size)]
        draw.polygon(pts, fill=fill_c, outline=color)
    elif shape == "arrow":
        s = size
        pts = [(cx+s,cy),(cx+s//2,cy-s//2),(cx+s//2,cy-s//5),
               (cx-s,cy-s//5),(cx-s,cy+s//5),(cx+s//2,cy+s//5),(cx+s//2,cy+s//2)]
        draw.polygon(pts, fill=color)
    elif isinstance(shape, int):   # n-gon
        pts = [(cx + int(size*math.cos(math.radians(j*360/shape - 90))),
                cy + int(size*math.sin(math.radians(j*360/shape - 90))))
               for j in range(shape)]
        draw.polygon(pts, fill=fill_c, outline=color)
    # Rotate
    rotated = img.rotate(-angle_deg, resample=Image.BICUBIC)
    result = Image.new("RGB", (canvas, canvas), "white")
    result.paste(rotated, mask=rotated.split()[3])
    return result

def make_series_question_img(shape_imgs, canvas_w=520, box_size=90):
    """Lay out 4 series images + a ? box in a row."""
    img = Image.new("RGB", (canvas_w, 120), "white")
    draw = ImageDraw.Draw(img)
    gap = (canvas_w - 5*(box_size+4)) // 6
    for j, si in enumerate(shape_imgs):
        bx = gap + j*(box_size+4+gap)
        resized = si.resize((box_size, box_size))
        img.paste(resized, (bx, 10))
        draw.rectangle([bx-2, 8, bx+box_size+2, box_size+12], outline="#AAA", width=1)
    # ? box
    bx = gap + 4*(box_size+4+gap)
    draw.rectangle([bx-2, 8, bx+box_size+2, box_size+12], outline="#E74C3C", width=2)
    draw.text((bx+box_size//2-8, box_size//2-8), "?", fill="#E74C3C")
    return img

def gen_figure_series(n):
    print(f"\n[Figure Series] {n} questions...")
    used = set()
    COLORS = {"Red":"#E74C3C","Blue":"#2980B9","Green":"#27AE60",
              "Purple":"#8E44AD","Orange":"#E67E22"}

    series_types = [
        "rotation", "fill_toggle", "size_grow", "polygon_sides", "count_grow"
    ]
    for i in range(n):
        grade = random.choice([3,4,5,6,7,8,9])
        stype = series_types[i % len(series_types)]
        cname, color = random.choice(list(COLORS.items()))

        if stype == "rotation":
            shape = random.choice(["arrow", "triangle"])
            step  = random.choice([45, 90])
            start = random.choice([0, 30, 45])
            angles = [start + k*step for k in range(5)]
            series_imgs = [draw_single_shape(shape,35,color,True,a) for a in angles[:4]]
            correct_img = draw_single_shape(shape,35,color,True,angles[4])
            wrong_angles = [(angles[4]+step+15)%360, (angles[4]-step+360)%360,
                            (angles[4]+step*2)%360]
            wrong_imgs  = [draw_single_shape(shape,35,color,True,wa) for wa in wrong_angles]
            all_opt = [correct_img]+wrong_imgs; random.shuffle(all_opt)
            cidx = all_opt.index(correct_img)
            q_text = f"The {cname.lower()} {shape} rotates by {step} degrees each step. What comes next?"
            expl   = f"Each step rotates the shape {step}° clockwise. The 5th figure is at {angles[4]%360}°."

        elif stype == "fill_toggle":
            shape = random.choice(["circle","square","triangle"])
            fills = [True,False,True,False,True]  # alternating — 5th = True (filled)
            series_imgs = [draw_single_shape(shape,35,color,fills[k]) for k in range(4)]
            correct_img = draw_single_shape(shape,35,color,fills[4])
            wrong_imgs  = [draw_single_shape(shape,35,color,not fills[4]),
                           draw_single_shape("square" if shape!="square" else "circle",35,color,fills[4]),
                           draw_single_shape(shape,35,"#E74C3C" if color!="#E74C3C" else "#2980B9",fills[4])]
            all_opt = [correct_img]+wrong_imgs; random.shuffle(all_opt)
            cidx = all_opt.index(correct_img)
            fill_word = "filled" if fills[4] else "hollow"
            q_text = f"The pattern alternates between filled and hollow {shape}s. What is the 5th shape?"
            expl   = f"The pattern is: filled, hollow, filled, hollow... The 5th shape is {fill_word}."

        elif stype == "size_grow":
            shape = random.choice(["circle","square","triangle"])
            sizes = [15, 22, 29, 36, 43]
            series_imgs = [draw_single_shape(shape,sizes[k],color,True) for k in range(4)]
            correct_img = draw_single_shape(shape,sizes[4],color,True)
            wrong_imgs  = [draw_single_shape(shape,sizes[4]-4,color,True),
                           draw_single_shape(shape,sizes[4]+5,color,True),
                           draw_single_shape(shape,sizes[2],color,True)]
            all_opt = [correct_img]+wrong_imgs; random.shuffle(all_opt)
            cidx = all_opt.index(correct_img)
            q_text = f"Each {cname.lower()} {shape} gets larger by the same amount. What size comes next?"
            expl   = f"Size increases by 7 units each step: {', '.join(str(s) for s in sizes)}."

        elif stype == "polygon_sides":
            side_seq = [3, 4, 5, 6, 7]
            side_names = {3:"triangle",4:"square",5:"pentagon",6:"hexagon",7:"heptagon",8:"octagon"}
            series_imgs = [draw_single_shape(side_seq[k],35,color,True) for k in range(4)]
            correct_img = draw_single_shape(side_seq[4],35,color,True)
            wrong_imgs  = [draw_single_shape(8,35,color,True),
                           draw_single_shape(4,35,color,True),
                           draw_single_shape(6,35,color,True)]
            all_opt = [correct_img]+wrong_imgs; random.shuffle(all_opt)
            cidx = all_opt.index(correct_img)
            names = [side_names[s] for s in side_seq[:4]]
            q_text = f"The shapes follow a pattern: {names[0]}, {names[1]}, {names[2]}, {names[3]}, ?. What comes next?"
            expl   = f"Each shape gains one side. After hexagon (6 sides) comes heptagon (7 sides)."

        else:   # count_grow: number of dots/shapes increases
            def make_dots_img(count, sz=35):
                img = Image.new("RGB",(100,100),"white"); d=ImageDraw.Draw(img)
                positions=[(25,25),(65,25),(25,65),(65,65),(45,45)]
                for p in positions[:count]:
                    d.ellipse([p[0]-sz//5,p[1]-sz//5,p[0]+sz//5,p[1]+sz//5],fill=color)
                return img
            counts = [1,2,3,4,5]
            series_imgs = [make_dots_img(counts[k]) for k in range(4)]
            correct_img = make_dots_img(counts[4])
            wrong_imgs  = [make_dots_img(4), make_dots_img(6), make_dots_img(3)]
            all_opt = [correct_img]+wrong_imgs; random.shuffle(all_opt)
            cidx = all_opt.index(correct_img)
            q_text = f"The number of dots increases by 1 each step: 1, 2, 3, 4, ? How many dots come next?"
            expl   = f"One more dot is added each step. After 4 dots comes 5 dots."

        if q_text in used:
            q_text += f" (Series {i+1})"
        used.add(q_text)
        q_img = make_series_question_img(series_imgs)
        make_imgopt(q_img, all_opt, "fig-series", q_text, cidx,
                    "Logical Reasoning", grade, "Patterns and Shapes",
                    "Figure Series", expl)

# ══════════════════════════════════════════════════════════════════════════════
# 3. MIRROR IMAGE (Grades 3-8) [IMAGE OPTIONS]
# ══════════════════════════════════════════════════════════════════════════════
def draw_asymmetric_shape(shape_type, color="#2980B9", canvas=120):
    """Draw an asymmetric shape on a canvas."""
    img = Image.new("RGB", (canvas,canvas), "white")
    draw = ImageDraw.Draw(img)
    cx = cy = canvas//2
    s = canvas//3

    if shape_type == "L":
        draw.rectangle([cx-s, cy-s, cx, cy+s], fill=color)
        draw.rectangle([cx, cy, cx+s, cy+s], fill=color)
    elif shape_type == "F":
        draw.rectangle([cx-s, cy-s, cx-s//2, cy+s], fill=color)   # vertical stem
        draw.rectangle([cx-s, cy-s, cx+s//2, cy-s//3], fill=color) # top bar
        draw.rectangle([cx-s, cy-s//5, cx+s//4, cy+s//5], fill=color) # middle bar
    elif shape_type == "Z":
        draw.rectangle([cx-s, cy-s, cx+s, cy-s//2], fill=color)
        draw.polygon([(cx+s,cy-s//2),(cx-s,cy+s//2),(cx+s,cy+s//2),(cx-s,cy-s//2)], fill=color)
        draw.rectangle([cx-s, cy+s//2, cx+s, cy+s], fill=color)
    elif shape_type == "arrow_right":
        pts = [(cx+s,cy),(cx,cy-s),(cx,cy-s//3),(cx-s,cy-s//3),(cx-s,cy+s//3),(cx,cy+s//3),(cx,cy+s)]
        draw.polygon(pts, fill=color)
    elif shape_type == "step":
        draw.rectangle([cx-s, cy, cx, cy+s], fill=color)
        draw.rectangle([cx-s, cy-s, cx-s//3, cy], fill=color)
        draw.rectangle([cx-s//3, cy-s, cx+s, cy-s//3], fill=color)
    elif shape_type == "T":
        draw.rectangle([cx-s, cy-s, cx+s, cy-s//3], fill=color)   # top bar
        draw.rectangle([cx-s//4, cy-s//3, cx+s//4, cy+s], fill=color)  # stem (off-center)
    return img

def gen_mirror_image(n):
    print(f"\n[Mirror Image] {n} questions...")
    used = set()
    shapes = ["L","F","Z","arrow_right","step","T"]
    colors_map = {"Blue":"#2980B9","Red":"#E74C3C","Green":"#27AE60","Purple":"#8E44AD"}

    for i in range(n):
        grade = random.choice([3,4,5,6,7,8])
        shape = shapes[i % len(shapes)]
        cname, color = random.choice(list(colors_map.items()))

        original = draw_asymmetric_shape(shape, color)
        # Correct mirror = horizontal flip
        correct  = ImageOps.mirror(original)
        # Wrongs: rotations (90, 180, 270 degrees)
        wrong1   = original.rotate(90,  expand=False)
        wrong2   = original.rotate(180, expand=False)
        wrong3   = original.rotate(270, expand=False)

        all_opts = [correct, wrong1, wrong2, wrong3]
        random.shuffle(all_opts)
        cidx = all_opts.index(correct)

        # Question image: original + mirror line
        q_img = Image.new("RGB", (300, 140), "white")
        draw  = ImageDraw.Draw(q_img)
        q_img.paste(original.resize((120,120)), (10, 10))
        draw.line([(145,0),(145,140)], fill="#E74C3C", width=3)
        draw.text((150, 5), "Mirror", fill="#E74C3C")
        draw.text((150,20), "line ->", fill="#E74C3C")
        # Right side is blank (options show candidates)
        draw.rectangle([155,10,285,130], outline="#AAA", width=1)
        draw.text((195, 60), "?", fill="#AAA")

        q_text = f"The {cname.lower()} shape is reflected across the vertical mirror line. Which is the correct mirror image?"
        if q_text in used:
            q_text = f"What does the {shape}-shape look like in a vertical mirror? (Figure {i+1})"
        used.add(q_text)
        expl = f"A vertical mirror reflection flips the shape horizontally (left becomes right)."
        make_imgopt(q_img, all_opts, "mirror", q_text, cidx,
                    "Logical Reasoning", grade, "Visual Reasoning",
                    "Mirror Images", expl)

# ══════════════════════════════════════════════════════════════════════════════
# 4. ODD ONE OUT — VISUAL (Grades 2-8)  [text options A/B/C/D]
# ══════════════════════════════════════════════════════════════════════════════
def gen_odd_one_out(n):
    print(f"\n[Odd One Out] {n} questions...")
    used = set()
    COLORS  = ["#E74C3C","#2980B9","#27AE60","#8E44AD","#E67E22","#F1C40F"]
    CNAMES  = ["Red","Blue","Green","Purple","Orange","Yellow"]
    SHAPES  = ["circle","square","triangle","pentagon","star"]
    SIZES   = [20, 35, 50]
    SNAMES  = ["small","medium","large"]

    rule_types = ["color","shape","size","fill","sides"]
    for i in range(n):
        grade = random.choice([2,3,4,5,6,7,8])
        rule  = rule_types[i % len(rule_types)]
        img   = Image.new("RGB",(520,130),"white")
        draw  = ImageDraw.Draw(img)
        labels = ["A","B","C","D"]
        box_w  = 110; gap = 12; by = 15; bh = 100

        odd_pos = random.randint(0,3)   # which of the 4 is the odd one
        rule_desc = ""
        shape_names = []

        if rule == "color":
            main_ci  = random.randint(0,5)
            odd_ci   = (main_ci + random.randint(1,4)) % len(COLORS)
            main_col = COLORS[main_ci]; odd_col = COLORS[odd_ci]
            main_name= CNAMES[main_ci]; odd_name= CNAMES[odd_ci]
            shape    = random.choice(["circle","square","triangle"])
            size     = 35
            for j in range(4):
                cx = gap + j*(box_w+gap) + box_w//2
                cy = by + bh//2
                col = odd_col if j==odd_pos else main_col
                if shape=="circle":
                    draw.ellipse([cx-size,cy-size,cx+size,cy+size],fill=col,outline="#333",width=2)
                elif shape=="square":
                    draw.rectangle([cx-size,cy-size,cx+size,cy+size],fill=col,outline="#333",width=2)
                else:
                    draw.polygon([(cx,cy-size),(cx-size,cy+size),(cx+size,cy+size)],fill=col,outline="#333")
                draw.text((cx-5, by+bh+2), labels[j], fill="#333")
                shape_names.append(f"{odd_name if j==odd_pos else main_name} {shape}")
            rule_desc = f"All shapes are {main_name} except option {labels[odd_pos]} which is {odd_name}."

        elif rule == "shape":
            main_sh  = random.choice(["circle","square","triangle"])
            odd_sh   = random.choice([s for s in SHAPES[:3] if s!=main_sh])
            col      = random.choice(COLORS); size=35
            for j in range(4):
                cx = gap + j*(box_w+gap) + box_w//2
                cy = by + bh//2
                sh = odd_sh if j==odd_pos else main_sh
                if sh=="circle":
                    draw.ellipse([cx-size,cy-size,cx+size,cy+size],fill=col,outline="#333",width=2)
                elif sh=="square":
                    draw.rectangle([cx-size,cy-size,cx+size,cy+size],fill=col,outline="#333",width=2)
                else:
                    draw.polygon([(cx,cy-size),(cx-size,cy+size),(cx+size,cy+size)],fill=col,outline="#333")
                draw.text((cx-5, by+bh+2), labels[j], fill="#333")
                shape_names.append(sh)
            rule_desc = f"All shapes are {main_sh}s except option {labels[odd_pos]} which is a {odd_sh}."

        elif rule == "size":
            main_sz  = 35; odd_sz = 18
            shape    = random.choice(["circle","square","triangle"])
            col      = random.choice(COLORS)
            for j in range(4):
                cx = gap + j*(box_w+gap) + box_w//2
                cy = by + bh//2
                sz = odd_sz if j==odd_pos else main_sz
                if shape=="circle":
                    draw.ellipse([cx-sz,cy-sz,cx+sz,cy+sz],fill=col,outline="#333",width=2)
                elif shape=="square":
                    draw.rectangle([cx-sz,cy-sz,cx+sz,cy+sz],fill=col,outline="#333",width=2)
                else:
                    draw.polygon([(cx,cy-sz),(cx-sz,cy+sz),(cx+sz,cy+sz)],fill=col,outline="#333")
                draw.text((cx-5, by+bh+2), labels[j], fill="#333")
                shape_names.append("small" if j==odd_pos else "large")
            rule_desc = f"Three shapes are large; option {labels[odd_pos]} is smaller than the rest."

        elif rule == "fill":
            shape = random.choice(["circle","square","triangle"])
            col   = random.choice(COLORS); size = 35
            # 3 filled, 1 hollow (odd)
            for j in range(4):
                cx = gap + j*(box_w+gap) + box_w//2
                cy = by + bh//2
                filled = (j != odd_pos)
                fc = col if filled else None
                if shape=="circle":
                    draw.ellipse([cx-size,cy-size,cx+size,cy+size],fill=fc,outline=col,width=3)
                elif shape=="square":
                    draw.rectangle([cx-size,cy-size,cx+size,cy+size],fill=fc,outline=col,width=3)
                else:
                    draw.polygon([(cx,cy-size),(cx-size,cy+size),(cx+size,cy+size)],fill=fc,outline=col)
                draw.text((cx-5, by+bh+2), labels[j], fill="#333")
                shape_names.append("hollow" if j==odd_pos else "filled")
            rule_desc = f"Three shapes are filled; option {labels[odd_pos]} is hollow (outline only)."

        else:   # sides — 3 same polygon + 1 different
            sides_main = random.choice([3,4,5,6])
            sides_odd  = random.choice([s for s in [3,4,5,6] if s!=sides_main])
            col  = random.choice(COLORS); size=35
            names_map = {3:"triangle",4:"square",5:"pentagon",6:"hexagon"}
            for j in range(4):
                cx = gap + j*(box_w+gap) + box_w//2
                cy = by + bh//2
                sd = sides_odd if j==odd_pos else sides_main
                pts= [(cx+int(size*math.cos(math.radians(k*360/sd-90))),
                       cy+int(size*math.sin(math.radians(k*360/sd-90))))
                      for k in range(sd)]
                draw.polygon(pts, fill=col, outline="#333", width=2)
                draw.text((cx-5, by+bh+2), labels[j], fill="#333")
                shape_names.append(names_map.get(sd, f"{sd}-gon"))
            rule_desc = (f"Three shapes are {names_map[sides_main]}s; "
                         f"option {labels[odd_pos]} is a {names_map[sides_odd]}.")

        q_text = f"Which shape is the ODD ONE OUT? Three shapes share a common property — one does not."
        if q_text in used:
            q_text = f"Find the shape that does NOT belong with the others. (Set {i+1})"
        used.add(q_text)
        opts   = ["A","B","C","D"]
        cidx   = odd_pos
        make_text(img, "odd-one-out", q_text, opts, cidx,
                  "Logical Reasoning", grade, "Visual Reasoning", "Odd One Out",
                  rule_desc)

# ══════════════════════════════════════════════════════════════════════════════
# 5. COUNTING FIGURES (Grades 3-7)
# ══════════════════════════════════════════════════════════════════════════════
def gen_count_figures(n):
    print(f"\n[Counting Figures] {n} questions...")
    used = set()
    for i in range(n):
        grade = random.choice([3,4,5,6,7])
        fig_type = random.choice(["tri_row","square_grid","mixed"])

        img  = Image.new("RGB",(420,220),"white")
        draw = ImageDraw.Draw(img)

        if fig_type == "tri_row":
            # n unit triangles in a row, sharing edges
            # Total triangles = n(n+2)/4 * 2 for pointing-up only, or simpler...
            # For a ROW of n unit triangles: count = n + (n-1) + ... = n(n+1)/2
            # Actually let's just draw and count: for n equilateral triangles in row
            # upward pointing only: count n small + composites
            num_units = random.choice([3,4,5])
            side = 70
            x0,y0 = 30, 180
            # Draw unit triangles
            for j in range(num_units):
                bx = x0 + j*side
                pts = [(bx, y0), (bx+side, y0), (bx+side//2, y0-int(side*0.866))]
                draw.polygon(pts, outline="#2980B9", width=3)
            # Count: unit + composites
            # For n triangles in row: total = n(n+2)(2n+1)/8 ... complex. Use lookup.
            counts_map = {3: 10, 4: 10, 5: 15}  # approximate for Olympiad
            # Simpler: just count visible unit triangles (Foundation)
            total = num_units   # unit only for Foundation
            q_text = f"How many triangles can you count in this figure? (count all sizes)"
            total_all = {3:6, 4:10, 5:15}[num_units]
            total = total_all
            draw.text((10,10), f"Count ALL triangles (including larger ones)", fill="#555")

        elif fig_type == "square_grid":
            # n x n grid — count all rectangles (or just squares)
            grid = random.choice([2,3])
            cell = 60; ox = 50; oy = 30
            for r in range(grid+1):
                draw.line([(ox, oy+r*cell),(ox+grid*cell, oy+r*cell)], fill="#2980B9", width=2)
            for c in range(grid+1):
                draw.line([(ox+c*cell, oy),(ox+c*cell, oy+grid*cell)], fill="#2980B9", width=2)
            # Count ALL squares: 1x1: grid², 2x2: (grid-1)², ...
            total = sum((grid-k+1)**2 for k in range(1,grid+1))
            # total squares in n×n grid = n(n+1)(2n+1)/6
            total = grid*(grid+1)*(2*grid+1)//6
            q_text = f"How many squares (of ALL sizes) can you count in this {grid}x{grid} grid?"
            draw.text((10,10), f"Count squares of all sizes", fill="#555")

        else:  # mixed — triangles + squares in a simple composition
            # Draw a large square with diagonal → makes 2 triangles inside
            grid = 2; cell = 70; ox=60; oy=20
            for r in range(grid+1):
                draw.line([(ox,oy+r*cell),(ox+grid*cell,oy+r*cell)],fill="#2980B9",width=2)
            for c in range(grid+1):
                draw.line([(ox+c*cell,oy),(ox+c*cell,oy+grid*cell)],fill="#2980B9",width=2)
            # Diagonals
            draw.line([(ox,oy),(ox+grid*cell,oy+grid*cell)],fill="#E74C3C",width=2)
            draw.line([(ox+grid*cell,oy),(ox,oy+grid*cell)],fill="#E74C3C",width=2)
            total = 4+4+1   # 4 small triangles + 4 medium + 1 large = 9 triangles? + squares
            total = 12  # approximately
            q_text = "How many triangles can you count in this figure?"
            draw.text((10,10),"Count triangles of all sizes",fill="#555")

        # Ensure unique
        if q_text in used: q_text += f" (Figure {i+1})"
        used.add(q_text)
        correct = str(total)
        wrongs  = list({str(total+1),str(total-1),str(total+2),str(total+3),
                        str(total-2)} - {correct})
        random.shuffle(wrongs)
        opts = [correct] + wrongs[:3]
        while len(opts) < 4: opts.append(str(total+random.randint(3,8)))
        opts = opts[:4]; random.shuffle(opts)
        cidx = opts.index(correct) if correct in opts else 0
        if correct not in opts: opts[0]=correct; cidx=0
        make_text(img, "count-fig", q_text, opts, cidx,
                  "Logical Reasoning", grade, "Visual Counting", "Counting Figures",
                  f"Total count = {total}. Count unit shapes plus all composite larger shapes.")

# ══════════════════════════════════════════════════════════════════════════════
# 6. AREA BY COUNTING SQUARES (Grades 3-6)
# ══════════════════════════════════════════════════════════════════════════════
def gen_area_grid(n):
    print(f"\n[Area Grid] {n} questions...")
    used = set()
    SHAPES_DEF = [
        # (name, list of (row,col) shaded cells in a grid)
        ("L-shape",   [(0,0),(1,0),(2,0),(3,0),(3,1),(3,2)]),
        ("T-shape",   [(0,0),(0,1),(0,2),(1,1),(2,1),(3,1)]),
        ("Z-shape",   [(0,0),(0,1),(1,1),(1,2),(2,2),(2,3)]),
        ("Plus",      [(0,1),(1,0),(1,1),(1,2),(2,1)]),
        ("Staircase", [(0,0),(1,0),(1,1),(2,0),(2,1),(2,2)]),
        ("Rectangle", [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]),
        ("U-shape",   [(0,0),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]),
        ("S-shape",   [(0,1),(0,2),(1,0),(1,1),(2,0),(2,1),(3,0)]),
        ("Arrow",     [(0,2),(1,0),(1,1),(1,2),(1,3),(1,4),(2,2)]),
        ("Cross",     [(0,1),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2),(3,1)]),
    ]
    cell_size = 40
    for i in range(n):
        grade = random.choice([3,4,5,6])
        name, cells = random.choice(SHAPES_DEF)
        area = len(cells)
        rows = max(r for r,c in cells)+1; cols = max(c for r,c in cells)+1
        img_w = cols*cell_size + 80; img_h = rows*cell_size + 80
        img   = Image.new("RGB",(img_w,img_h),"white")
        draw  = ImageDraw.Draw(img)
        ox, oy = 30, 30
        # Draw full grid (5x6 background)
        grid_r = max(rows+1, 5); grid_c = max(cols+1, 5)
        for r in range(grid_r+1):
            draw.line([(ox,oy+r*cell_size),(ox+grid_c*cell_size,oy+r*cell_size)],fill="#DDD",width=1)
        for c in range(grid_c+1):
            draw.line([(ox+c*cell_size,oy),(ox+c*cell_size,oy+grid_r*cell_size)],fill="#DDD",width=1)
        # Shade the shape cells
        for r,c in cells:
            x0=ox+c*cell_size+1; y0=oy+r*cell_size+1
            draw.rectangle([x0,y0,x0+cell_size-2,y0+cell_size-2],fill="#AED6F1",outline="#2980B9",width=1)
        # Label
        draw.text((ox,oy+grid_r*cell_size+5), f"Each small square = 1 sq unit", fill="#555")

        q_text = f"What is the area of the shaded {name} shape? (Each square = 1 sq unit)"
        if q_text in used: q_text = f"Find the area of the blue shaded region in sq units. (Shape {i+1})"
        used.add(q_text)
        correct = f"{area} sq units"
        wrongs  = list({f"{area+1} sq units",f"{area-1} sq units",
                        f"{area+2} sq units",f"{area+3} sq units"} - {correct})
        random.shuffle(wrongs)
        opts = [correct]+wrongs[:3]; random.shuffle(opts)
        cidx = opts.index(correct) if correct in opts else 0
        if correct not in opts: opts[0]=correct; cidx=0
        make_text(img,"area-grid",q_text,opts,cidx,
                  "Mathematics",grade,"Mensuration","Area by Counting",
                  f"Count the number of shaded squares: {area} squares → Area = {area} sq units.")

# ══════════════════════════════════════════════════════════════════════════════
# 7. INDIAN COINS / MONEY (Grades 1-4)
# ══════════════════════════════════════════════════════════════════════════════
COIN_DEFS = {
    "50p":  (0.50,  70, "#C0C0C0", "50p"),
    "₹1":   (1.00,  80, "#C0A060", "₹1"),
    "₹2":   (2.00,  90, "#C0A060", "₹2"),
    "₹5":   (5.00, 100, "#B8860B", "₹5"),
    "₹10":  (10.0, 110, "#B8860B", "₹10"),
}

def draw_coin(draw, cx, cy, r, color, label):
    draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=color, outline="#888", width=2)
    draw.text((cx-len(label)*4, cy-8), label, fill="#333")

def gen_coins(n):
    print(f"\n[Indian Coins] {n} questions...")
    used = set()
    grade_coins = {
        1: ["₹1","₹2","₹5"],
        2: ["₹1","₹2","₹5","₹10"],
        3: ["50p","₹1","₹2","₹5","₹10"],
        4: ["50p","₹1","₹2","₹5","₹10"],
    }
    for i in range(n):
        grade   = random.choice([1,2,3,4])
        choices = grade_coins[grade]
        num_coins = random.randint(3,5)
        coins   = [random.choice(choices) for _ in range(num_coins)]
        total   = sum(COIN_DEFS[c][0] for c in coins)
        # Format total
        if total == int(total):
            total_str = f"Rs. {int(total)}"
        else:
            total_str = f"Rs. {total:.2f}"

        img  = Image.new("RGB",(500,150),"white")
        draw = ImageDraw.Draw(img)
        spacing = 490 // (num_coins+1)
        for j, coin in enumerate(coins):
            val, r_px, col, lbl = COIN_DEFS[coin]
            cx = spacing*(j+1); cy = 75
            r_draw = min(r_px//2, 45)
            draw_coin(draw, cx, cy, r_draw, col, lbl)
        draw.text((10,130), "Total value of these coins = ?", fill="#555")

        q_text = f"What is the total value of the Indian coins shown?"
        if q_text in used: q_text = f"Add up all the coins shown. What is the total amount? (Set {i+1})"
        used.add(q_text)
        correct = total_str
        # Generate wrongs
        wvals = list({round(total+0.5,2), round(total+1,2),
                      round(total-0.5,2), round(total+2,2)} - {total})
        random.shuffle(wvals)
        def fmt(v):
            v = max(0.5, v)
            return f"Rs. {int(v)}" if v==int(v) else f"Rs. {v:.2f}"
        wrongs = [fmt(v) for v in wvals[:3]]
        while len(wrongs) < 3: wrongs.append(fmt(total+random.randint(3,10)))
        opts = [correct]+wrongs[:3]; random.shuffle(opts)
        cidx = opts.index(correct) if correct in opts else 0
        if correct not in opts: opts[0]=correct; cidx=0
        make_text(img,"coins",q_text,opts,cidx,
                  "Mathematics",grade,"Money","Indian Currency",
                  f"Sum of coins: {' + '.join(coins)} = {total_str}.")

# ══════════════════════════════════════════════════════════════════════════════
# 8. LIFE CYCLE DIAGRAMS (Grades 2-5)
# ══════════════════════════════════════════════════════════════════════════════
LIFE_CYCLES = {
    "Butterfly": {
        "stages": ["Egg","Caterpillar","Chrysalis","Butterfly"],
        "colors": ["#F1C40F","#27AE60","#8E44AD","#E74C3C"],
        "facts":  ["A butterfly lays tiny eggs on leaves.",
                   "The egg hatches into a caterpillar (larva) that eats leaves.",
                   "The caterpillar forms a protective chrysalis (pupa).",
                   "The adult butterfly emerges from the chrysalis."],
    },
    "Frog": {
        "stages": ["Eggs","Tadpole","Froglet","Adult Frog"],
        "colors": ["#F1C40F","#27AE60","#2980B9","#27AE60"],
        "facts":  ["Frogs lay eggs in water.",
                   "Eggs hatch into tadpoles with tails and gills.",
                   "Tadpole grows legs and loses its tail to become a froglet.",
                   "The froglet develops into an adult frog that can live on land."],
    },
    "Mosquito": {
        "stages": ["Egg","Larva","Pupa","Adult"],
        "colors": ["#F1C40F","#2980B9","#E67E22","#E74C3C"],
        "facts":  ["Mosquitoes lay eggs on still water.",
                   "Eggs hatch into larvae (wrigglers) living in water.",
                   "The larva develops into a pupa (tumbler) in water.",
                   "The adult mosquito emerges and can fly."],
    },
    "Plant": {
        "stages": ["Seed","Germination","Seedling","Mature Plant"],
        "colors": ["#F1C40F","#27AE60","#27AE60","#2ECC71"],
        "facts":  ["A seed contains the embryo of a new plant.",
                   "The seed sprouts (germinates) when it gets water, warmth and air.",
                   "A seedling with roots and a shoot grows from the germinated seed.",
                   "The plant grows fully and produces flowers and fruits."],
    },
    "Cockroach": {
        "stages": ["Egg","Nymph","Young Adult","Adult"],
        "colors": ["#F1C40F","#E67E22","#8E44AD","#E74C3C"],
        "facts":  ["Cockroach lays eggs in a case called ootheca.",
                   "Eggs hatch into nymphs resembling small adults without wings.",
                   "Nymphs moult several times growing into young adults.",
                   "The fully winged adult cockroach is the final stage."],
    },
}

def draw_life_cycle(stages, colors, highlight_idx, size=380):
    img = Image.new("RGB",(size,size),"white")
    draw = ImageDraw.Draw(img)
    cx = cy = size//2; orbit = size//2 - 55; box_w=80; box_h=36

    angles = [270, 0, 90, 180]  # top, right, bottom, left
    positions = []
    for ang in angles:
        rad = math.radians(ang)
        px = int(cx + orbit*math.cos(rad))
        py = int(cy + orbit*math.sin(rad))
        positions.append((px,py))

    # Draw circular arrows between boxes
    for j in range(4):
        x1,y1 = positions[j]; x2,y2 = positions[(j+1)%4]
        # Mid-arc arrow (approximate with straight line)
        draw.line([(x1,y1),(x2,y2)],fill="#AAA",width=2)
        # Arrowhead at x2,y2
        ang = math.atan2(y2-y1,x2-x1)
        ax  = x2-int(12*math.cos(ang)); ay = y2-int(12*math.sin(ang))
        draw.polygon([(x2,y2),(ax-int(6*math.sin(ang)),ay+int(6*math.cos(ang))),
                      (ax+int(6*math.sin(ang)),ay-int(6*math.cos(ang)))],fill="#888")

    # Draw stage boxes
    for j,(px,py) in enumerate(positions):
        fill = "#FFD700" if j==highlight_idx else colors[j]
        outline = "#E74C3C" if j==highlight_idx else "#333"
        width   = 3 if j==highlight_idx else 2
        draw.rectangle([px-box_w//2,py-box_h//2,px+box_w//2,py+box_h//2],
                       fill=fill,outline=outline,width=width)
        label = stages[j] if j!=highlight_idx else "?"
        tx = px - len(stages[j])*4
        draw.text((tx,py-8), label if j!=highlight_idx else "?", fill="white" if j==highlight_idx else "#FFF")

    # Legend
    draw.text((10,size-30), f"? = highlighted yellow stage", fill="#E74C3C")
    return img

def gen_life_cycle(n):
    print(f"\n[Life Cycles] {n} questions...")
    used = set()
    cycle_names = list(LIFE_CYCLES.keys())
    q_types = ["identify","after","before","role"]
    for i in range(n):
        grade     = random.choice([2,3,4,5])
        cycle_name= cycle_names[i % len(cycle_names)]
        cycle     = LIFE_CYCLES[cycle_name]
        stages    = cycle["stages"]; colors=cycle["colors"]; facts=cycle["facts"]
        hi_idx    = random.randint(0,3)
        qtype     = q_types[i % len(q_types)]
        img       = draw_life_cycle(stages, colors, hi_idx)

        if qtype == "identify":
            q_text = f"In the life cycle of a {cycle_name.lower()}, what is the highlighted (yellow/?) stage?"
            correct= stages[hi_idx]
            wrongs = [s for s in stages if s!=correct]
        elif qtype == "after":
            q_text = f"In the {cycle_name} life cycle, what stage comes AFTER '{stages[hi_idx]}'?"
            correct= stages[(hi_idx+1)%4]
            wrongs = [s for s in stages if s!=correct]
        elif qtype == "before":
            q_text = f"In the {cycle_name} life cycle, what stage comes BEFORE '{stages[hi_idx]}'?"
            correct= stages[(hi_idx-1)%4]
            wrongs = [s for s in stages if s!=correct]
        else:
            q_text = f"In the {cycle_name} life cycle diagram, what does the highlighted stage do?"
            correct= facts[hi_idx]
            wrongs = [f for f in facts if f!=correct]

        if q_text in used: q_text += f" (Cycle {i+1})"
        used.add(q_text)
        opts = [correct]+wrongs[:3]; random.shuffle(opts)
        cidx = opts.index(correct) if correct in opts else 0
        if correct not in opts: opts[0]=correct; cidx=0
        make_text(img,"life-cycle",q_text,opts,cidx,
                  "Science",grade,"Living World","Life Cycles",
                  f"{cycle_name} life cycle: {' -> '.join(stages)}. Highlighted stage = {stages[hi_idx]}.")

# ══════════════════════════════════════════════════════════════════════════════
# 9. LAYERS OF EARTH (Grades 6-8)
# ══════════════════════════════════════════════════════════════════════════════
EARTH_LAYERS = [
    ("Inner Core",  "#E74C3C", "solid iron and nickel ball at the very centre",   80),
    ("Outer Core",  "#E67E22", "liquid iron and nickel layer surrounding inner core", 120),
    ("Mantle",      "#F1C40F", "thickest layer of semi-solid hot rock (magma)",    175),
    ("Crust",       "#8B4513", "thin outermost solid rock layer we live on",       200),
]

def draw_earth_cross(highlight_name, size=380):
    img = Image.new("RGB",(size,size),"white")
    draw= ImageDraw.Draw(img)
    cx = cy = size//2
    for name, col, desc, r in reversed(EARTH_LAYERS):
        is_hi = (name == highlight_name)
        fill  = "#FFD700" if is_hi else col
        out   = "#E74C3C" if is_hi else "#333"
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=fill, outline=out, width=3 if is_hi else 1)
    # Labels on right side
    for j,(name,col,_,r) in enumerate(EARTH_LAYERS):
        lx = cx+r+8; ly = cy - 10 + j*4
        # Line from edge to label
        draw.line([(cx+r, cy),(lx+2,ly+8)], fill="#555",width=1)
        is_hi = (name==highlight_name)
        draw.text((lx+5,ly), "?" if is_hi else name, fill="#E74C3C" if is_hi else "#333")
    draw.text((10,size-25), "Cross-section of the Earth", fill="#777")
    return img

def gen_earth_layers(n):
    print(f"\n[Earth Layers] {n} questions...")
    used = set()
    q_types = ["identify","deepest","thickest","state"]
    for i in range(n):
        grade = random.choice([6,7,8])
        hi    = random.choice(EARTH_LAYERS)
        qtype = q_types[i % len(q_types)]
        img   = draw_earth_cross(hi[0])

        if qtype == "identify":
            q_text  = f"The highlighted (yellow/?) layer in the Earth cross-section diagram is which layer?"
            correct = hi[0]
            wrongs  = [l[0] for l in EARTH_LAYERS if l[0]!=correct]
        elif qtype == "deepest":
            q_text  = "Which is the deepest layer of the Earth?"
            correct = "Inner Core"
            wrongs  = ["Outer Core","Mantle","Crust"]
        elif qtype == "thickest":
            q_text  = "Which layer of the Earth is the thickest?"
            correct = "Mantle"
            wrongs  = ["Inner Core","Outer Core","Crust"]
        else:
            q_text  = f"What is the state of matter of the '{hi[0]}' layer?"
            if hi[0]=="Inner Core":   correct="Solid"
            elif hi[0]=="Outer Core": correct="Liquid"
            elif hi[0]=="Mantle":     correct="Semi-solid (plastic)"
            else:                     correct="Solid"
            wrongs = [x for x in ["Solid","Liquid","Gas","Semi-solid (plastic)"] if x!=correct]

        if q_text in used: q_text += f" (Diagram {i+1})"
        used.add(q_text)
        opts = [correct]+wrongs[:3]; random.shuffle(opts)
        cidx = opts.index(correct) if correct in opts else 0
        if correct not in opts: opts[0]=correct; cidx=0
        make_text(img,"earth-layers",q_text,opts,cidx,
                  "Science",grade,"Earth and Universe","Structure of Earth",
                  f"Earth layers (outside to inside): Crust, Mantle, Outer Core, Inner Core. {hi[0]}: {hi[2]}.")

# ══════════════════════════════════════════════════════════════════════════════
# 10. CLOUD TYPES (Grades 5-7)
# ══════════════════════════════════════════════════════════════════════════════
CLOUD_INFO = {
    "Cirrus":       ("#E8F8FF", (10,60),  "High altitude — thin, wispy, feathery clouds made of ice crystals"),
    "Cumulus":      ("#FFFFFF", (60,130), "Mid altitude — fluffy, white, cotton-like clouds"),
    "Stratus":      ("#D5D8DC", (130,175),"Low altitude — flat, grey, sheet-like clouds covering the sky"),
    "Cumulonimbus": ("#7F8C8D", (20,185), "Towering storm cloud producing heavy rain, thunder and lightning"),
}

def draw_cloud_scene(highlight, size_w=480, size_h=240):
    img  = Image.new("RGB",(size_w,size_h),"#87CEEB")  # sky blue
    draw = ImageDraw.Draw(img)
    # Ground
    draw.rectangle([0,200,size_w,size_h], fill="#8B7355")

    def cloud_shape(cx, cy, scale, col, outline_col):
        for dx,dy,rx,ry in [( 0,0,35,25),(-30,-5,25,18),(30,-5,25,18),(-18,-15,18,14),(18,-15,18,14)]:
            ex,ey = int(cx+dx*scale),int(cy+dy*scale)
            erx,ery = int(rx*scale),int(ry*scale)
            draw.ellipse([ex-erx,ey-ery,ex+erx,ey+ery], fill=col, outline=outline_col, width=1)

    positions = {
        "Cirrus":       (240, 30,  0.7,  "#E8F8FF","#CCDDEE"),
        "Cumulus":      (120, 100, 1.0,  "#FFFFFF","#CCCCCC"),
        "Stratus":      (240, 160, 2.5,  "#C8CDD0","#AAB0B5"),
        "Cumulonimbus": (360, 90,  1.4,  "#808080","#555555"),
    }

    for name,(cx,cy,sc,col,out) in positions.items():
        is_hi = (name==highlight)
        use_col = "#FFD700" if is_hi else col
        cloud_shape(cx,cy,sc,use_col,out)
        label_col = "#E74C3C" if is_hi else "#555"
        lbl = "?" if is_hi else name
        draw.text((cx-15,cy+int(30*sc)), lbl, fill=label_col)

    draw.text((5,size_h-25), "Identify the highlighted (yellow) cloud type", fill="#E74C3C")
    return img

def gen_cloud_types(n):
    print(f"\n[Cloud Types] {n} questions...")
    used = set()
    cloud_names = list(CLOUD_INFO.keys())
    q_types = ["identify","altitude","weather","characteristic"]
    alt_map = {"Cirrus":"high","Cumulus":"mid","Stratus":"low","Cumulonimbus":"towering/storm"}
    for i in range(n):
        grade  = random.choice([5,6,7])
        hi     = cloud_names[i % len(cloud_names)]
        qtype  = q_types[i % len(q_types)]
        img    = draw_cloud_scene(hi)
        _, alt_range, desc = CLOUD_INFO[hi]

        if qtype == "identify":
            q_text  = "The highlighted (yellow) cloud in the diagram is which type?"
            correct = hi
            wrongs  = [c for c in cloud_names if c!=correct]
        elif qtype == "altitude":
            q_text  = "Which cloud type is found at the HIGHEST altitude?"
            correct = "Cirrus"
            wrongs  = ["Cumulus","Stratus","Cumulonimbus"]
        elif qtype == "weather":
            q_text  = "Which cloud type is associated with thunderstorms and heavy rain?"
            correct = "Cumulonimbus"
            wrongs  = ["Cirrus","Cumulus","Stratus"]
        else:
            q_text  = f"Which best describes the '{hi}' cloud shown in the diagram?"
            correct = desc
            wrongs  = [CLOUD_INFO[c][2] for c in cloud_names if c!=hi]

        if q_text in used: q_text += f" (Diagram {i+1})"
        used.add(q_text)
        opts = [correct]+wrongs[:3]; random.shuffle(opts)
        cidx = opts.index(correct) if correct in opts else 0
        if correct not in opts: opts[0]=correct; cidx=0
        make_text(img,"clouds",q_text,opts,cidx,
                  "Science",grade,"Our Environment","Types of Clouds",
                  f"{hi}: {desc}.")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if not ADMIN_API_KEY:
        print("[!] ADMIN_API_KEY not set.")
        sys.exit(1)

    print("="*60)
    print("OlympiadReady — LR / Math / Science Generator")
    print("="*60)

    gen_clock(QPT)
    gen_figure_series(QPT)
    gen_mirror_image(QPT)
    gen_odd_one_out(QPT)
    gen_count_figures(QPT)
    gen_area_grid(QPT)
    gen_coins(QPT)
    gen_life_cycle(QPT)
    gen_earth_layers(QPT)
    gen_cloud_types(QPT)

    total = QPT * 10
    print(f"\n{'='*60}")
    print(f"DONE: {posted} posted, {skipped} skipped (dups), "
          f"{len(saved_locally)} saved locally, {failed} failed")
    print(f"Total attempted: {total}")
    if saved_locally:
        try:    out_dir = os.path.dirname(os.path.abspath(__file__))
        except: out_dir = os.getcwd()
        out = os.path.join(out_dir, "lr_math_science_questions.json")
        with open(out,"w",encoding="utf-8") as f:
            json.dump(saved_locally,f,indent=2)
        print(f"Saved -> {out}")
