"""
generate_diagrams.py
Generates programmatic diagram-based questions for Math, Science, and
advanced Logical Reasoning across grades 1-10.
Uploads images to Cloudinary and posts to the Admin API.

Requirements: pip install pillow cloudinary requests
"""

import os, io, json, random, time, math, sys
import requests
import cloudinary
import cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont

# ── CONFIG ────────────────────────────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")
QUESTIONS_PER_TYPE    = 20
# ─────────────────────────────────────────────────────────────────────────────

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME, api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET, secure=True)

RUN_ID = int(time.time())
posted = 0
failed = 0
saved_locally = []

# ── HELPERS ───────────────────────────────────────────────────────────────────
def img_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def upload(img, label):
    pid = f"{CLOUDINARY_FOLDER}/{label}-{RUN_ID}-{random.randint(1000,9999)}"
    try:
        r = cloudinary.uploader.upload(img_bytes(img), public_id=pid,
                                       overwrite=False, resource_type="image")
        return r["secure_url"]
    except Exception as e:
        print(f"  [FAIL] Cloudinary: {e}")
        return None

def post(q):
    global posted
    if not ADMIN_API_KEY:
        saved_locally.append(q)
        return
    try:
        r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question", json=q,
                          headers={"X-Admin-Key": ADMIN_API_KEY}, timeout=15)
        if r.status_code in (200,201):
            posted += 1
            print("-> posted")
        else:
            print(f"-> FAIL {r.status_code}: {r.text[:80]}")
            saved_locally.append(q)
    except Exception as e:
        print(f"-> error: {e}")
        saved_locally.append(q)

def difficulty_for_grade(grade):
    """Return difficulty based on grade level: Foundation / Advanced / Olympiad."""
    if grade <= 4:
        return "Foundation"
    elif grade <= 7:
        return random.choice(["Foundation", "Advanced"])
    else:
        return random.choice(["Advanced", "Olympiad"])

def make(img, label, text, opts, cidx, subject, grade, topic, subtopic, diff, expl):
    print(f"  upload {label}...", end=" ", flush=True)
    url = upload(img, label)
    if not url:
        global failed; failed += 1; return
    print("[OK]", end=" ", flush=True)
    post({"subject": subject, "grade": grade, "topic": topic, "subTopic": subtopic,
          "difficulty": diff, "questionText": text, "imageUrl": url,
          "options": opts, "correctAnswer": chr(65+cidx), "explanation": expl})

# ══════════════════════════════════════════════════════════════════════════════
# MATH GENERATORS
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. Number Line (Grades 1-4) ───────────────────────────────────────────────
def gen_number_line(n):
    print(f"\n[Number Line] {n} questions...")
    used = set()
    for i in range(n):
        grade = random.choice([1,2,3,4])
        max_val = {1:10, 2:20, 3:50, 4:100}[grade]
        start = random.randint(0, max_val-6)
        marked = start + random.randint(1,5)

        img = Image.new("RGB", (500, 120), "white")
        draw = ImageDraw.Draw(img)
        # Line
        draw.line([(30,60),(470,60)], fill="#333333", width=3)
        step = 440 // 6
        # Draw 7 tick marks
        for j in range(7):
            x = 30 + j*step
            val = start + j
            draw.line([(x,45),(x,75)], fill="#333333", width=2)
            if val == marked:
                draw.ellipse([x-12,43,x+12,67], fill="#E74C3C")
                draw.text((x-5,47), "?", fill="white")
            else:
                draw.text((x-6,78), str(val) if val != marked else "?", fill="#333333")
        # Arrow ends
        draw.polygon([(470,56),(470,64),(482,60)], fill="#333333")
        draw.polygon([(30,56),(30,64),(18,60)], fill="#333333")

        q_text = f"The red dot on the number line is at which number? (Line starts at {start})"
        if q_text in used:
            q_text = f"What number does the red marker show on the number line? (Range {start}-{start+6})"
        used.add(q_text)

        wrong = list({marked+1, marked-1, marked+2, marked-2} - {marked})
        wrong = [w for w in wrong if 0 <= w <= max_val]
        while len(wrong) < 3:
            wrong.append(random.randint(0, max_val))
            wrong = list(set(wrong) - {marked})
        opts = [str(marked)] + [str(w) for w in wrong[:3]]
        random.shuffle(opts)
        cidx = opts.index(str(marked))
        make(img, "number-line", q_text, opts, cidx,
             "Mathematics", grade, "Number System", "Number Line", "Foundation",
             f"The red dot is positioned at {marked} on the number line.")

# ── 2. Fraction Bar (Grades 3-6) ──────────────────────────────────────────────
def gen_fraction_bar(n):
    print(f"\n[Fraction Bar] {n} questions...")
    used = set()
    templates = [
        "What fraction of the bar is shaded in {color}?",
        "The shaded portion represents which fraction?",
        "Which fraction is shown by the highlighted part of the bar?",
        "What fraction of the whole bar is coloured?",
    ]
    colors_map = {"blue":"#2980B9","red":"#E74C3C","green":"#27AE60","orange":"#E67E22"}
    for i in range(n):
        grade = random.choice([3,4,5,6])
        denom = random.choice([2,3,4,5,6,8,10])
        numer = random.randint(1, denom-1)
        color_name, fill_color = random.choice(list(colors_map.items()))

        img = Image.new("RGB", (500, 120), "white")
        draw = ImageDraw.Draw(img)
        bar_w = 440; bar_h = 60; bx = 30; by = 30
        cell_w = bar_w // denom
        for j in range(denom):
            x = bx + j*cell_w
            fill = fill_color if j < numer else "#EEEEEE"
            draw.rectangle([x+1,by+1,x+cell_w-1,by+bar_h-1], fill=fill, outline="#333333")
        # label fraction below
        draw.text((bx + bar_w//2 - 20, by+bar_h+8), f"Whole = 1", fill="#555555")

        q_text = random.choice(templates).format(color=color_name)
        if q_text in used:
            q_text = f"What fraction does the {color_name} shaded part represent? ({numer}/{denom} bar)"
        used.add(q_text)

        correct = f"{numer}/{denom}"
        wrongs = set()
        for _ in range(20):
            if len(wrongs) >= 3: break
            wn = random.randint(1,denom-1)
            wd = random.choice([2,3,4,5,6,8])
            cand = f"{wn}/{wd}"
            if cand != correct:
                wrongs.add(cand)
        opts = [correct] + list(wrongs)[:3]
        random.shuffle(opts)
        cidx = opts.index(correct)
        make(img, "fraction-bar", q_text, opts, cidx,
             "Mathematics", grade, "Fractions", "Fraction Representation", "Foundation",
             f"{numer} out of {denom} equal parts are shaded, so the fraction is {numer}/{denom}.")

# ── 3. Bar Graph (Grades 3-7) ─────────────────────────────────────────────────
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
ITEMS  = ["Books","Apples","Cars","Goals","Students","Marks","Trees","Flowers"]

def gen_bar_graph(n):
    print(f"\n[Bar Graph] {n} questions...")
    used = set()
    q_templates = [
        "In which {month_or_item} was the value highest?",
        "Which {month_or_item} shows the maximum value in the graph?",
        "According to the bar graph, {month_or_item} with the lowest value is?",
        "What is the total of the two highest bars in the graph?",
    ]
    bar_colors = ["#2980B9","#E74C3C","#27AE60","#E67E22","#8E44AD"]
    for i in range(n):
        grade = random.choice([3,4,5,6,7])
        num_bars = random.choice([4,5,6])
        labels = random.sample(MONTHS[:6] if grade <=5 else MONTHS, num_bars)
        values = [random.randint(10,100) for _ in range(num_bars)]
        item = random.choice(ITEMS)
        color = random.choice(bar_colors)

        img = Image.new("RGB", (500, 320), "white")
        draw = ImageDraw.Draw(img)
        chart_x, chart_y, chart_w, chart_h = 60, 20, 400, 240
        max_v = max(values)
        # Y axis
        draw.line([(chart_x, chart_y),(chart_x, chart_y+chart_h)], fill="#333", width=2)
        # X axis
        draw.line([(chart_x, chart_y+chart_h),(chart_x+chart_w, chart_y+chart_h)], fill="#333", width=2)
        # Y grid lines and labels
        for g in range(5):
            yv = (g+1) * (max_v//5 + 1)
            y  = chart_y + chart_h - int(yv/max_v * chart_h)
            draw.line([(chart_x,y),(chart_x+chart_w,y)], fill="#DDDDDD", width=1)
            draw.text((5, y-7), str(yv), fill="#555555")
        # Bars
        bw = (chart_w // num_bars) - 10
        for j,(lbl,val) in enumerate(zip(labels,values)):
            bx = chart_x + 10 + j*(chart_w//num_bars)
            bh = int(val/max_v * chart_h)
            by = chart_y + chart_h - bh
            draw.rectangle([bx, by, bx+bw, chart_y+chart_h], fill=color, outline="#333")
            draw.text((bx+2, chart_y+chart_h+4), lbl, fill="#333")
            draw.text((bx+2, by-16), str(val), fill="#333")
        draw.text((chart_x+chart_w//2-30, chart_y+chart_h+22), item, fill="#333")

        max_idx = values.index(max(values))
        min_idx = values.index(min(values))
        top2_sum = sum(sorted(values, reverse=True)[:2])

        # Pick question type
        qtype = i % 3
        if qtype == 0:
            q_text = f"According to the bar graph, which {labels[0][0].lower()}... period had the highest number of {item.lower()}?"
            q_text = f"Which bar in the graph shows the highest value of {item.lower()}?"
            correct = labels[max_idx]
            opts = [correct] + random.sample([l for l in labels if l != correct], min(3,len(labels)-1))
            while len(opts) < 4:
                opts.append(random.choice(MONTHS))
            opts = opts[:4]; random.shuffle(opts); cidx = opts.index(correct)
            expl = f"{correct} has the highest value of {max(values)} {item.lower()}."
        elif qtype == 1:
            q_text = f"Which period shows the minimum number of {item.lower()} in the graph?"
            correct = labels[min_idx]
            opts = [correct] + random.sample([l for l in labels if l != correct], min(3,len(labels)-1))
            while len(opts) < 4:
                opts.append(random.choice(MONTHS))
            opts = opts[:4]; random.shuffle(opts); cidx = opts.index(correct)
            expl = f"{correct} has the lowest value of {min(values)} {item.lower()}."
        else:
            q_text = f"What is the sum of the two highest values shown in the {item.lower()} bar graph?"
            correct = str(top2_sum)
            sv = sorted(values, reverse=True)
            wrongs = [str(sv[0]+sv[2]), str(sv[0]+sv[1]+sv[2]), str(sv[0]*2)]
            opts = list({correct}|set(wrongs))[:4]
            while len(opts)<4: opts.append(str(top2_sum+random.randint(1,10)))
            opts = opts[:4]; random.shuffle(opts)
            cidx = opts.index(correct) if correct in opts else 0
            if correct not in opts: opts[0]=correct; cidx=0
            expl = f"The two highest values are {sv[0]} and {sv[1]}, sum = {top2_sum}."

        if q_text in used:
            q_text += f" (Graph set {i+1})"
        used.add(q_text)
        make(img, "bar-graph", q_text, opts, cidx,
             "Mathematics", grade, "Data Handling", "Bar Graphs", "Foundation", expl)

# ── 4. Geometry — Angles and Shapes (Grades 4-8) ─────────────────────────────
def gen_geometry(n):
    print(f"\n[Geometry] {n} questions...")
    used = set()
    for i in range(n):
        grade = random.choice([4,5,6,7,8])
        qtype = random.choice(["angle","triangle","rectangle"])

        img = Image.new("RGB", (400, 300), "white")
        draw = ImageDraw.Draw(img)

        if qtype == "angle":
            angle_val = random.choice([30,45,60,90,120,135,150])
            cx,cy = 200,200
            # Draw angle
            draw.line([(cx,cy),(cx+150,cy)], fill="#333", width=3)
            rad = math.radians(angle_val)
            ex = int(cx + 140*math.cos(rad))
            ey = int(cy - 140*math.sin(rad))
            draw.line([(cx,cy),(ex,ey)], fill="#333", width=3)
            # Arc approximation
            for a in range(0, angle_val, 2):
                r = 40
                ax = int(cx + r*math.cos(math.radians(a)))
                ay = int(cy - r*math.sin(math.radians(a)))
                draw.ellipse([ax-2,ay-2,ax+2,ay+2], fill="#E74C3C")
            draw.text((cx+50,cy-30), f"{angle_val}°?", fill="#E74C3C")
            draw.text((cx+5,cy+5), "O", fill="#333")

            angle_type = ("acute" if angle_val < 90 else
                          "right" if angle_val == 90 else
                          "obtuse" if angle_val < 180 else "straight")
            q_text = f"The angle shown measures {angle_val} degrees. What type of angle is this?"
            if q_text in used:
                q_text = f"An angle of {angle_val}° is drawn. Classify this angle."
            used.add(q_text)
            all_types = ["acute","right","obtuse","straight","reflex"]
            opts = [angle_type] + [t for t in all_types if t != angle_type][:3]
            random.shuffle(opts); cidx = opts.index(angle_type)
            expl = f"An angle of {angle_val}° is classified as {angle_type} ({('<90' if angle_val<90 else '=90' if angle_val==90 else '>90 and <180')})."

        elif qtype == "triangle":
            a,b = random.randint(3,12), random.randint(3,12)
            # Right triangle
            x0,y0 = 80,220; x1,y1 = x0+a*20,y0; x2,y2 = x0,y0-b*20
            draw.polygon([(x0,y0),(x1,y1),(x2,y2)], outline="#2980B9", width=3)
            # Right angle box
            draw.rectangle([x0,y0-15,x0+15,y0], outline="#2980B9", width=2)
            draw.text(((x0+x1)//2-8, y0+8), f"{a} cm", fill="#333")
            draw.text((x0-35, (y0+y2)//2), f"{b} cm", fill="#333")
            draw.text(((x1+x2)//2+5, (y1+y2)//2), "?", fill="#E74C3C")
            area = (a*b)/2
            q_text = f"A right triangle has base {a} cm and height {b} cm. What is its area?"
            if q_text in used:
                q_text = f"Find the area of the right triangle with base {a} cm and height {b} cm."
            used.add(q_text)
            correct = str(area) if area == int(area) else f"{area}"
            correct = f"{int(area) if area==int(area) else area} sq cm"
            w1 = f"{a*b} sq cm"; w2 = f"{a+b} sq cm"; w3 = f"{int((a*b)/3)} sq cm"
            opts = list({correct,w1,w2,w3})[:4]
            while len(opts)<4: opts.append(f"{random.randint(1,30)} sq cm")
            opts=opts[:4]; random.shuffle(opts)
            cidx = opts.index(correct) if correct in opts else 0
            if correct not in opts: opts[0]=correct; cidx=0
            expl = f"Area of triangle = (1/2) x base x height = (1/2) x {a} x {b} = {(a*b)//2} sq cm."

        else:  # rectangle
            l,w = random.randint(4,15), random.randint(2,10)
            x0,y0,x1,y1 = 80,80,80+l*18,80+w*18
            draw.rectangle([x0,y0,x1,y1], outline="#27AE60", width=3)
            draw.text(((x0+x1)//2-15,y0-20), f"{l} cm", fill="#333")
            draw.text((x1+5,(y0+y1)//2-8), f"{w} cm", fill="#333")
            draw.text(((x0+x1)//2-10,(y0+y1)//2-8), "Area = ?", fill="#E74C3C")
            area = l*w
            perim = 2*(l+w)
            ask = random.choice(["area","perimeter"])
            correct = f"{area} sq cm" if ask=="area" else f"{perim} cm"
            q_text = (f"A rectangle has length {l} cm and width {w} cm. Find its area." if ask=="area"
                      else f"A rectangle has length {l} cm and width {w} cm. Find its perimeter.")
            if q_text in used:
                q_text += f" (Diagram {i+1})"
            used.add(q_text)
            wrongs = [f"{area+l} sq cm",f"{area-w} sq cm",f"{perim} sq cm"] if ask=="area" else \
                     [f"{area} cm",f"{l+w} cm",f"{perim+2} cm"]
            opts = list({correct}|set(wrongs))[:4]
            while len(opts)<4: opts.append(f"{random.randint(1,50)} {'sq cm' if ask=='area' else 'cm'}")
            opts=opts[:4]; random.shuffle(opts)
            cidx = opts.index(correct) if correct in opts else 0
            if correct not in opts: opts[0]=correct; cidx=0
            expl = (f"Area = length x width = {l} x {w} = {area} sq cm." if ask=="area"
                    else f"Perimeter = 2(l+w) = 2({l}+{w}) = {perim} cm.")

        diff = difficulty_for_grade(grade)
        make(img, "geometry", q_text, opts, cidx,
             "Mathematics", grade, "Geometry", "Shapes and Measurement", diff, expl)

# ── 5. Pie Chart (Grades 5-8) ─────────────────────────────────────────────────
def gen_pie_chart(n):
    print(f"\n[Pie Chart] {n} questions...")
    used = set()
    for i in range(n):
        grade = random.choice([5,6,7,8])
        num_slices = random.choice([3,4,5])
        labels = random.sample(["Cricket","Football","Tennis","Swimming","Basketball",
                                 "Science","Maths","English","Art","History"], num_slices)
        raw = [random.randint(10,50) for _ in range(num_slices)]
        total = sum(raw)
        percs = [round(v/total*100) for v in raw]
        # Adjust last to make sum 100
        percs[-1] = 100 - sum(percs[:-1])

        img = Image.new("RGB", (500, 300), "white")
        draw = ImageDraw.Draw(img)
        cx,cy,r = 180,150,120
        colors = ["#E74C3C","#2980B9","#27AE60","#E67E22","#8E44AD"]
        start_angle = 0
        for j,(lbl,pct) in enumerate(zip(labels,percs)):
            sweep = pct * 3.6
            draw.pieslice([cx-r,cy-r,cx+r,cy+r], start=start_angle,
                          end=start_angle+sweep, fill=colors[j%len(colors)], outline="white")
            # Label in middle of slice
            mid_a = math.radians(start_angle + sweep/2)
            tx = int(cx + (r*0.6)*math.cos(mid_a))
            ty = int(cy + (r*0.6)*math.sin(mid_a))
            draw.text((tx-10,ty-8), f"{pct}%", fill="white")
            start_angle += sweep
        # Legend
        for j,(lbl,_) in enumerate(zip(labels,percs)):
            lx = 340; ly = 60+j*35
            draw.rectangle([lx,ly,lx+18,ly+18], fill=colors[j%len(colors)])
            draw.text((lx+24,ly+2), lbl, fill="#333")

        max_idx = percs.index(max(percs))
        min_idx = percs.index(min(percs))
        q_text = f"According to the pie chart, which category has the largest share?"
        if q_text in used:
            q_text = f"The pie chart shows preferences. Which item is most popular?"
        if q_text in used:
            q_text = f"Pie chart question #{i+1}: which segment covers the greatest percentage?"
        used.add(q_text)
        correct = labels[max_idx]
        wrongs = [l for l in labels if l != correct]
        # Pad to 3 wrongs if fewer than 3 labels available (e.g. 3-slice chart)
        ALL_LABELS = ["Cricket","Football","Tennis","Swimming","Basketball",
                      "Science","Maths","English","Art","History"]
        extra = [l for l in ALL_LABELS if l not in labels]
        random.shuffle(extra)
        while len(wrongs) < 3:
            wrongs.append(extra.pop(0))
        opts = [correct] + wrongs[:3]
        random.shuffle(opts); cidx = opts.index(correct)
        diff = difficulty_for_grade(grade)
        expl = f"{correct} has the largest slice at {percs[max_idx]}%."
        make(img, "pie-chart", q_text, opts, cidx,
             "Mathematics", grade, "Data Handling", "Pie Charts", diff, expl)

# ── 6. Number Pattern / Series (Grades 3-8) ───────────────────────────────────
def gen_number_series(n):
    print(f"\n[Number Series] {n} questions...")
    used = set()
    for i in range(n):
        grade = random.choice([3,4,5,6,7,8])
        ptype = random.choice(["arithmetic","geometric","square","fibonacci","skip"])

        if ptype == "arithmetic":
            start = random.randint(1,20); step = random.randint(2,15)
            series = [start + j*step for j in range(6)]
            ans = series[-1]; shown = series[:-1]
            rule = f"Add {step} each time"
        elif ptype == "geometric":
            start = random.choice([1,2,3]); ratio = random.choice([2,3])
            series = [start * ratio**j for j in range(5)]
            ans = series[-1]; shown = series[:-1]
            rule = f"Multiply by {ratio} each time"
        elif ptype == "square":
            start = random.randint(1,5)
            series = [(start+j)**2 for j in range(5)]
            ans = series[-1]; shown = series[:-1]
            rule = f"Perfect squares starting from {start}²"
        elif ptype == "fibonacci":
            a,b = random.randint(1,5), random.randint(1,5)
            series = [a,b]
            for _ in range(4): series.append(series[-1]+series[-2])
            ans = series[-1]; shown = series[:-1]
            rule = "Each term = sum of two previous terms"
        else:  # skip counting
            start = random.randint(2,10); skip = random.randint(3,10)
            series = [start+j*skip for j in range(6)]
            ans = series[-1]; shown = series[:-1]
            rule = f"Skip count by {skip}"

        img = Image.new("RGB", (500, 140), "white")
        draw = ImageDraw.Draw(img)
        # Draw boxes with numbers
        bw = 60; gap = 12; total_w = len(shown)*bw + (len(shown)+1)*gap + bw + gap
        x0 = (500 - total_w)//2
        for j,val in enumerate(shown):
            bx = x0 + j*(bw+gap)
            draw.rectangle([bx,30,bx+bw,90], fill="#AED6F1", outline="#2980B9", width=2)
            draw.text((bx+bw//2-12,50), str(val), fill="#333")
        # Question box
        qx = x0 + len(shown)*(bw+gap)
        draw.rectangle([qx,30,qx+bw,90], fill="#FADBD8", outline="#E74C3C", width=2)
        draw.text((qx+bw//2-5,50), "?", fill="#E74C3C")
        draw.text((x0,105), "Find the next number in the series", fill="#555555")

        q_text = f"What is the next number in the series: {', '.join(str(s) for s in shown)}, ?"
        if q_text in used:
            q_text += f" (Pattern: {ptype})"
        used.add(q_text)
        wrongs = list({ans+random.randint(1,step if ptype=='arithmetic' else 3),
                       ans-random.randint(1,3), ans+random.randint(4,10)} - {ans})
        opts = [str(ans)] + [str(w) for w in wrongs[:3]]
        while len(opts)<4: opts.append(str(ans+random.randint(1,5)))
        opts=opts[:4]; random.shuffle(opts)
        cidx = opts.index(str(ans)) if str(ans) in opts else 0
        if str(ans) not in opts: opts[0]=str(ans); cidx=0
        diff = difficulty_for_grade(grade)
        make(img, "number-series", q_text, opts, cidx,
             "Mathematics", grade, "Patterns", "Number Series", diff,
             f"Pattern: {rule}. Next number = {ans}.")

# ══════════════════════════════════════════════════════════════════════════════
# SCIENCE GENERATORS
# ══════════════════════════════════════════════════════════════════════════════

# ── 7. Food Chain Diagram (Grades 4-7) ────────────────────────────────────────
FOOD_CHAINS = [
    (["Grass","Grasshopper","Frog","Snake","Eagle"], 4),
    (["Leaves","Caterpillar","Robin","Hawk"], 4),
    (["Algae","Small Fish","Big Fish","Shark"], 5),
    (["Grass","Rabbit","Fox","Lion"], 5),
    (["Plankton","Small Fish","Tuna","Shark"], 6),
    (["Grass","Deer","Tiger"], 4),
    (["Wheat","Mouse","Owl"], 5),
    (["Grass","Cow","Human"], 4),
    (["Algae","Shrimp","Penguin","Leopard Seal"], 6),
    (["Berries","Squirrel","Hawk"], 5),
    (["Grass","Zebra","Cheetah"], 5),
    (["Leaves","Aphid","Ladybird","Sparrow"], 4),
    (["Phytoplankton","Zooplankton","Herring","Dolphin"], 6),
    (["Rice","Locust","Lizard","Eagle"], 4),
    (["Grass","Rabbit","Snake","Peacock"], 5),
]

def gen_food_chain(n):
    print(f"\n[Food Chain] {n} questions...")
    used = set()
    q_types = [
        ("producer",   "Which organism is the PRODUCER (first) in this food chain?",              0),
        ("top",        "Which is the TOP consumer (last) in this food chain?",                    -1),
        ("primary",    "Which organism is the PRIMARY consumer (eats the producer directly)?",     1),
        ("second_last","Which organism is directly eaten by the last (top) consumer?",            -2),
    ]
    for i in range(n):
        chain, grade = random.choice(FOOD_CHAINS)
        qtype_name, q_template, idx = random.choice(q_types)
        # Guard: second_last needs at least 3 organisms
        if idx == -2 and len(chain) < 3:
            idx = -1; qtype_name = "top"
            q_template = "Which is the TOP consumer (last) in this food chain?"

        img = Image.new("RGB", (500, 130), "white")
        draw = ImageDraw.Draw(img)
        box_w = 80; gap = (500 - len(chain)*box_w) // (len(chain)+1)
        colors = ["#27AE60","#F39C12","#E67E22","#E74C3C","#8E44AD"]
        for j,org in enumerate(chain):
            bx = gap + j*(box_w+gap); by = 30
            draw.rectangle([bx,by,bx+box_w,by+55], fill=colors[j%len(colors)], outline="#333", width=2)
            draw.text((bx+5,by+15), org, fill="white")
            if j < len(chain)-1:
                ax = bx+box_w+gap//2
                draw.polygon([(ax-8,50),(ax+8,50),(ax,65)], fill="#333")

        correct = chain[idx]
        # Unique question text using chain endpoints — avoids "(Chain X)" suffixes
        q_text = f"In the food chain {chain[0]} -> {chain[-1]}, {q_template[0].lower()}{q_template[1:]}"
        if q_text in used:
            q_text = f"Food chain: {' -> '.join(chain)}. {q_template}"
        if q_text in used:
            q_text = f"{q_template} ({chain[0]} to {chain[-1]})"
        used.add(q_text)
        wrongs = [c for c in chain if c != correct]
        opts = [correct] + wrongs[:3]
        while len(opts)<4: opts.append(random.choice(["Eagle","Worm","Deer","Ant","Fox"]))
        opts=opts[:4]; random.shuffle(opts); cidx=opts.index(correct)
        diff = "Foundation" if grade<=5 else "Advanced"
        expl = f"In this food chain ({' -> '.join(chain)}), the {qtype_name} is {correct}."
        make(img, "food-chain", q_text, opts, cidx,
             "Science", grade, "Living World", "Food Chain", diff, expl)

# ── 8. Plant Parts Diagram (Grades 2-5) ───────────────────────────────────────
PLANT_PARTS = {
    "Root":    "absorbs water and minerals from soil",
    "Stem":    "transports water from roots to leaves",
    "Leaf":    "makes food for the plant through photosynthesis",
    "Flower":  "helps in reproduction of the plant",
    "Fruit":   "protects seeds and helps in seed dispersal",
    "Seed":    "grows into a new plant",
}

def gen_plant_parts(n):
    print(f"\n[Plant Parts] {n} questions...")
    used = set()
    for i in range(n):
        part = random.choice(list(PLANT_PARTS.keys()))
        func = PLANT_PARTS[part]
        grade = random.choice([2,3,4,5])

        img = Image.new("RGB", (400, 320), "white")
        draw = ImageDraw.Draw(img)
        # Simple plant diagram
        cx = 200
        # Soil line
        draw.line([(30,240),(370,240)], fill="#8B4513", width=4)
        draw.rectangle([30,240,370,300], fill="#D2B48C")
        # Root
        root_color = "#FFD700" if part=="Root" else "#8B4513"
        draw.line([(cx,240),(cx,290)], fill=root_color, width=4)
        draw.line([(cx,270),(cx-30,290)], fill=root_color, width=3)
        draw.line([(cx,270),(cx+30,290)], fill=root_color, width=3)
        # Stem
        stem_color = "#FFD700" if part=="Stem" else "#2E8B57"
        draw.line([(cx,240),(cx,120)], fill=stem_color, width=6)
        # Leaf
        leaf_color = "#FFD700" if part=="Leaf" else "#27AE60"
        draw.ellipse([cx-50,140,cx+10,180], fill=leaf_color, outline="#1E8449")
        draw.ellipse([cx,130,cx+60,165], fill=leaf_color, outline="#1E8449")
        # Flower
        flower_color = "#FFD700" if part=="Flower" else "#E74C3C"
        for a in range(0,360,60):
            px = int(cx + 25*math.cos(math.radians(a)))
            py = int(120 + 25*math.sin(math.radians(a)))
            draw.ellipse([px-12,py-12,px+12,py+12], fill=flower_color)
        draw.ellipse([cx-10,110,cx+10,130], fill="#F1C40F")
        # Arrow pointing to highlighted part
        draw.text((20,10), f"Highlighted part = {part if part!='?' else '?'}", fill="#E74C3C")
        draw.text((20,35), "(shown in yellow)", fill="#777777")

        func_short = func[:50]
        q_text = f"The yellow highlighted part of the plant is shown. What is its main function?"
        if q_text in used:
            q_text = f"The {part.lower()} is highlighted in the plant diagram. What does it do?"
        if q_text in used:
            q_text = f"Plant diagram #{i+1}: the highlighted yellow part — what is its role?"
        used.add(q_text)
        correct = func.split(" and ")[0].capitalize() + "."
        correct = func.capitalize()
        all_funcs = list(PLANT_PARTS.values())
        wrongs = [f for f in all_funcs if f != func]
        random.shuffle(wrongs)
        opts = [func.capitalize()] + [w.capitalize() for w in wrongs[:3]]
        random.shuffle(opts); cidx = opts.index(func.capitalize())
        make(img, "plant-parts", q_text, opts, cidx,
             "Science", grade, "Plants Around Us", "Parts of a Plant", "Foundation",
             f"The {part} {func}.")

# ── 9. Simple Electric Circuit (Grades 6-9) ───────────────────────────────────
def gen_circuit(n):
    print(f"\n[Electric Circuit] {n} questions...")
    used = set()
    for i in range(n):
        grade = random.choice([6,7,8,9])
        circuit_type = random.choice(["series","parallel","open"])

        img = Image.new("RGB", (500, 280), "white")
        draw = ImageDraw.Draw(img)

        if circuit_type == "series":
            # Battery
            draw.rectangle([30,120,70,160], fill="#F1C40F", outline="#333", width=2)
            draw.text((35,130), "BATT", fill="#333")
            # Wire top
            draw.line([(50,120),(50,60),(430,60)], fill="#333", width=3)
            # Bulb 1
            draw.ellipse([150,40,200,80], outline="#E74C3C", width=3)
            draw.text((158,53), "B1", fill="#E74C3C")
            # Bulb 2
            draw.ellipse([280,40,330,80], outline="#E74C3C", width=3)
            draw.text((288,53), "B2", fill="#E74C3C")
            # Wire bottom
            draw.line([(430,60),(430,160),(70,160)], fill="#333", width=3)
            draw.text((180,180), "Series Circuit: B1 and B2 connected in SERIES", fill="#555")
            q_text = "In the circuit shown, the bulbs B1 and B2 are connected in series. If B1 is removed, what happens to B2?"
            correct = "B2 also goes off — the circuit is broken"
            opts = [correct,
                    "B2 stays on — it has its own path",
                    "B2 glows brighter",
                    "B2 glows dimmer but stays on"]
            cidx = 0

        elif circuit_type == "parallel":
            # Battery
            draw.rectangle([30,100,70,180], fill="#F1C40F", outline="#333", width=2)
            draw.text((32,130), "BATT", fill="#333")
            draw.line([(50,100),(50,50),(450,50),(450,100)], fill="#333", width=3)
            draw.line([(50,180),(50,230),(450,230),(450,180)], fill="#333", width=3)
            # Branch 1
            draw.line([(200,50),(200,100)], fill="#333", width=3)
            draw.ellipse([180,100,240,150], outline="#2980B9", width=3)
            draw.text((193,118), "B1", fill="#2980B9")
            draw.line([(210,150),(210,230)], fill="#333", width=3)
            # Branch 2
            draw.line([(320,50),(320,100)], fill="#333", width=3)
            draw.ellipse([300,100,360,150], outline="#2980B9", width=3)
            draw.text((313,118), "B2", fill="#2980B9")
            draw.line([(330,150),(330,230)], fill="#333", width=3)
            draw.text((140,245), "Parallel Circuit", fill="#555")
            q_text = "In the parallel circuit shown, if B1 is removed, what happens to B2?"
            correct = "B2 continues to glow normally"
            opts = [correct,
                    "B2 also goes off",
                    "B2 glows dimmer",
                    "The battery will drain immediately"]
            cidx = 0

        else:  # open circuit
            draw.rectangle([30,120,70,160], fill="#F1C40F", outline="#333", width=2)
            draw.text((35,130), "BATT", fill="#333")
            draw.line([(50,120),(50,60),(200,60)], fill="#333", width=3)
            # Gap (open switch)
            draw.line([(200,60),(220,40)], fill="#333", width=3)
            draw.text((215,20), "Switch", fill="#E74C3C")
            draw.text((225,55), "(OPEN)", fill="#E74C3C")
            draw.line([(240,60),(430,60)], fill="#333", width=3)
            draw.ellipse([350,40,410,80], outline="#333", width=3)
            draw.text((366,53), "Bulb", fill="#333")
            draw.line([(430,60),(430,160),(70,160)], fill="#333", width=3)
            q_text = "The circuit diagram shows an open switch. What will happen to the bulb?"
            correct = "The bulb will not glow (circuit is incomplete)"
            opts = [correct,
                    "The bulb will glow brightly",
                    "The bulb will glow dimly",
                    "The battery will explode"]
            cidx = 0

        if q_text in used:
            q_text += f" (Circuit diagram {i+1})"
        used.add(q_text)
        make(img, "circuit", q_text, opts, cidx,
             "Science", grade, "Electricity and Magnetism", "Electric Circuits",
             "Advanced",
             f"In a {circuit_type} circuit: {opts[0]}")

# ── 10. Water Cycle Diagram (Grades 5-7) ─────────────────────────────────────
WATER_CYCLE_PARTS = {
    "Evaporation":    "Water from oceans/lakes turns into water vapour due to sun's heat",
    "Condensation":   "Water vapour cools and forms clouds (tiny water droplets)",
    "Precipitation":  "Water falls from clouds as rain, snow or hail",
    "Transpiration":  "Plants release water vapour through their leaves",
    "Collection":     "Rainwater collects in oceans, rivers and lakes",
    "Infiltration":   "Water seeps into the ground to form groundwater",
}

def _draw_water_cycle_base(draw):
    """Draw the common water cycle background: sky, ground, ocean, sun, cloud."""
    draw.rectangle([0, 0, 500, 200], fill="#D6EAF8")   # sky
    draw.rectangle([0, 200, 500, 280], fill="#D2B48C")  # ground
    # Ocean
    draw.ellipse([20, 175, 210, 235], fill="#3498DB")
    draw.text((80, 195), "Ocean", fill="white")
    # Sun
    draw.ellipse([420, 10, 485, 75], fill="#F1C40F")
    for a in range(0, 360, 30):
        sx = int(452 + 50 * math.cos(math.radians(a)))
        sy = int(42  + 50 * math.sin(math.radians(a)))
        draw.line([(452, 42), (sx, sy)], fill="#F1C40F", width=2)
    # Cloud
    draw.ellipse([200, 30, 330, 100], fill="white", outline="#95A5A6", width=2)
    draw.ellipse([230, 15, 310,  65], fill="white", outline="#95A5A6", width=2)
    draw.text((235, 55), "Cloud", fill="#7F8C8D")
    # Plant (simple, for transpiration context)
    draw.line([(340, 200), (340, 140)], fill="#27AE60", width=5)
    draw.ellipse([310, 120, 360, 155], fill="#27AE60")
    draw.ellipse([335, 110, 380, 148], fill="#27AE60")

def _highlight_label(draw, text, color="#E74C3C"):
    """Draw a highlighted banner at the bottom."""
    draw.rectangle([10, 248, 490, 276], fill="#FADBD8")
    draw.text((20, 254), text, fill=color)

def _draw_water_cycle_evaporation(draw):
    _draw_water_cycle_base(draw)
    # Bold upward wavy arrows from ocean to cloud — highlighted in red/orange
    for x in [80, 105, 130]:
        for y in range(175, 50, -18):
            draw.ellipse([x-5, y-5, x+5, y+5], fill="#E74C3C")
        # Arrowhead at top
        draw.polygon([(x, 50), (x-7, 65), (x+7, 65)], fill="#E74C3C")
    _highlight_label(draw, "EVAPORATION highlighted: water rises from ocean as vapour")

def _draw_water_cycle_condensation(draw):
    _draw_water_cycle_base(draw)
    # Small droplets forming around the cloud — highlighted
    for dx, dy in [(200,80),(215,65),(230,58),(250,50),(270,58),(290,65),(310,78)]:
        draw.ellipse([dx-6,dy-6,dx+6,dy+6], fill="#2980B9", outline="#1A5276", width=1)
    # Arrow from vapour stream into cloud
    draw.line([(150, 120), (200, 80)], fill="#E74C3C", width=3)
    draw.polygon([(200,80),(188,88),(194,72)], fill="#E74C3C")
    draw.text((110, 125), "Water\nvapour", fill="#E74C3C")
    _highlight_label(draw, "CONDENSATION highlighted: vapour cools and forms cloud droplets")

def _draw_water_cycle_precipitation(draw):
    _draw_water_cycle_base(draw)
    # Rain drops falling from cloud — highlighted
    for rx in range(215, 325, 18):
        draw.line([(rx, 100), (rx - 12, 155)], fill="#E74C3C", width=2)
        draw.polygon([(rx-12,155),(rx-18,140),(rx-6,140)], fill="#E74C3C")
    draw.text((200, 160), "Rain / Snow", fill="#E74C3C")
    _highlight_label(draw, "PRECIPITATION highlighted: water falls from clouds as rain/snow")

def _draw_water_cycle_transpiration(draw):
    _draw_water_cycle_base(draw)
    # Arrows from plant leaves upward — highlighted
    for x in [325, 345, 360]:
        draw.line([(x, 140), (x - 5, 100)], fill="#E74C3C", width=2)
        draw.polygon([(x-5,100),(x-11,115),(x+1,115)], fill="#E74C3C")
    draw.text((290, 85), "Water\nvapour", fill="#E74C3C")
    _highlight_label(draw, "TRANSPIRATION highlighted: plants release water vapour from leaves")

def _draw_water_cycle_collection(draw):
    _draw_water_cycle_base(draw)
    # Arrows flowing from land into the ocean — highlighted
    for ox in [280, 310, 340]:
        draw.line([(ox, 210), (210, 210)], fill="#E74C3C", width=2)
        draw.polygon([(210,210),(225,204),(225,216)], fill="#E74C3C")
    # River line
    draw.line([(210,210),(330,210)], fill="#3498DB", width=4)
    draw.text((250, 218), "Runoff to\nocean/lake", fill="#E74C3C")
    _highlight_label(draw, "COLLECTION highlighted: rainwater collects in oceans/rivers/lakes")

def _draw_water_cycle_infiltration(draw):
    _draw_water_cycle_base(draw)
    # Downward arrows into ground — highlighted
    for x in [250, 290, 330]:
        draw.line([(x, 200), (x, 240)], fill="#E74C3C", width=2)
        draw.polygon([(x,240),(x-7,228),(x+7,228)], fill="#E74C3C")
    draw.text((220, 248), "Water seeping\ninto ground", fill="#E74C3C")
    _highlight_label(draw, "INFILTRATION highlighted: water seeps into ground -> groundwater")

WATER_CYCLE_DRAW_FN = {
    "Evaporation":   _draw_water_cycle_evaporation,
    "Condensation":  _draw_water_cycle_condensation,
    "Precipitation": _draw_water_cycle_precipitation,
    "Transpiration": _draw_water_cycle_transpiration,
    "Collection":    _draw_water_cycle_collection,
    "Infiltration":  _draw_water_cycle_infiltration,
}

def gen_water_cycle(n):
    print(f"\n[Water Cycle] {n} questions...")
    used = set()
    parts = list(WATER_CYCLE_PARTS.keys())
    for i in range(n):
        part = parts[i % len(parts)]   # cycle through all parts evenly
        defn = WATER_CYCLE_PARTS[part]
        grade = random.choice([5,6,7])

        img = Image.new("RGB", (500, 280), "white")
        draw = ImageDraw.Draw(img)
        # Draw the process-specific diagram
        WATER_CYCLE_DRAW_FN[part](draw)

        q_text = f"In the water cycle diagram, what does '{part}' mean?"
        if q_text in used:
            q_text = f"The water cycle step called '{part}' is highlighted. What happens during this step?"
        used.add(q_text)
        all_defns = list(WATER_CYCLE_PARTS.values())
        wrongs = [d for d in all_defns if d != defn]
        random.shuffle(wrongs)
        opts = [defn] + wrongs[:3]
        random.shuffle(opts); cidx = opts.index(defn)
        diff = "Foundation" if grade <= 6 else "Advanced"
        make(img, f"water-cycle-{part.lower()}", q_text, opts, cidx,
             "Science", grade, "Our Environment", "Water Cycle", diff,
             f"{part}: {defn}")

# ── 11. Venn Diagram (Grades 5-9) ─────────────────────────────────────────────
def gen_venn(n):
    print(f"\n[Venn Diagram] {n} questions...")
    used = set()
    # Each entry: (label_a, label_b, both_list, only_a_list, only_b_list)
    # Varied intersection sizes: 2, 3, 4, 5 elements so correct answer varies
    venn_sets = [
        ("Even numbers",    "Multiples of 3",  [6,12],           [2,4,8,10,14],  [3,9,15,21]),
        ("Multiples of 2",  "Multiples of 4",  [4,8,12,16],      [2,6,10,14],    [20,24,28]),
        ("Factors of 24",   "Factors of 36",   [1,2,3,4,6,12],   [8,24],         [9,18,36]),
        ("Prime numbers",   "Odd numbers",     [3,5,7,11],       [2],            [1,9,15,25]),
        ("Multiples of 5",  "Multiples of 3",  [15,30,45],       [5,10,20,25],   [3,6,9,12]),
        ("Factors of 12",   "Factors of 18",   [1,2,3,6],        [4,12],         [9,18]),
        ("Multiples of 6",  "Multiples of 9",  [18,36],          [6,12,24,30],   [9,27,45]),
        ("Square numbers",  "Even numbers",    [4,16,36],        [1,9,25,49],    [2,6,8,10]),
    ]
    for i in range(n):
        set_a, set_b, both, only_a, only_b = random.choice(venn_sets)
        grade = random.choice([5,6,7,8,9])
        # Show a subset of elements to avoid overcrowding (but use true counts)
        show_both   = both[:4]
        show_only_a = only_a[:3]
        show_only_b = only_b[:3]
        num_both = len(show_both)
        num_a    = len(show_only_a)
        num_b    = len(show_only_b)

        # ---- Draw using RGBA so overlap region is visually distinct ----
        img = Image.new("RGBA", (500, 300), (255,255,255,255))
        # Circle A (blue, semi-transparent)
        circle_a = Image.new("RGBA", (500, 300), (0,0,0,0))
        d_a = ImageDraw.Draw(circle_a)
        d_a.ellipse([40, 70, 280, 240], fill=(41,128,185,100), outline=(41,128,185,255))
        # Circle B (green, semi-transparent)
        circle_b = Image.new("RGBA", (500, 300), (0,0,0,0))
        d_b = ImageDraw.Draw(circle_b)
        d_b.ellipse([220, 70, 460, 240], fill=(39,174,96,100), outline=(39,174,96,255))
        # Compose
        img = Image.alpha_composite(img, circle_a)
        img = Image.alpha_composite(img, circle_b)
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)

        # Labels below circles
        draw.text((90, 248),  set_a, fill="#1A5276")
        draw.text((300, 248), set_b, fill="#1E8449")
        draw.text((215, 52),  "Both", fill="#333333")

        # Numbers in only-A region (left of overlap ~x=230)
        for j, v in enumerate(show_only_a):
            draw.text((75 + (j%2)*30, 110 + (j//2)*30), str(v), fill="#2980B9")
        # Numbers in intersection region (~x=230-270)
        for j, v in enumerate(show_both):
            draw.text((228 + (j%2)*22, 100 + (j//2)*28), str(v), fill="#333333")
        # Numbers in only-B region (right of overlap ~x=290)
        for j, v in enumerate(show_only_b):
            draw.text((320 + (j%2)*30, 110 + (j//2)*30), str(v), fill="#27AE60")

        q_text = f"In the Venn diagram of {set_a} and {set_b}, how many elements are in the intersection (both circles)?"
        if q_text in used:
            q_text = f"Venn diagram: how many numbers belong to both {set_a} and {set_b}?"
        used.add(q_text)

        correct = str(num_both)
        # Generate meaningfully different wrong answers
        wrong_candidates = list({str(num_a), str(num_b),
                                  str(num_a + num_b),
                                  str(num_both + 1), str(max(1, num_both - 1))} - {correct})
        random.shuffle(wrong_candidates)
        opts = [correct] + wrong_candidates[:3]
        while len(opts) < 4:
            opts.append(str(random.randint(1, 8)))
        opts = list(dict.fromkeys(opts))[:4]   # deduplicate, keep order
        while len(opts) < 4:
            opts.append(str(random.randint(1, 10)))
        random.shuffle(opts)
        cidx = opts.index(correct) if correct in opts else 0
        if correct not in opts:
            opts[0] = correct; cidx = 0
        diff = "Advanced" if grade >= 7 else "Foundation"
        make(img, "venn", q_text, opts, cidx,
             "Mathematics", grade, "Sets", "Venn Diagrams", diff,
             f"Numbers in both sets: {show_both} — count = {num_both}.")

# ── 12. LR Matrix Pattern (Grades 4-8) ────────────────────────────────────────
# Map hex codes to readable color names
HEX_TO_NAME = {
    "#E74C3C": "Red",
    "#2980B9": "Blue",
    "#27AE60": "Green",
    "#8E44AD": "Purple",
    "#E67E22": "Orange",
    "#F1C40F": "Yellow",
}
SIZE_LABELS = ["Small", "Medium", "Large"]
# Each palette is 3 hex colors → used as row colors
COLOR_PALETTES = [
    ["#E74C3C", "#2980B9", "#27AE60"],   # Red, Blue, Green
    ["#E74C3C", "#8E44AD", "#E67E22"],   # Red, Purple, Orange
    ["#2980B9", "#27AE60", "#F1C40F"],   # Blue, Green, Yellow
    ["#8E44AD", "#E67E22", "#2980B9"],   # Purple, Orange, Blue
]

def gen_matrix(n):
    print(f"\n[Matrix Pattern] {n} questions...")
    used = set()
    shape_choices = ["circle", "square", "triangle"]
    for i in range(n):
        grade = random.choice([4, 5, 6, 7, 8])
        shape = shape_choices[i % len(shape_choices)]
        palette = COLOR_PALETTES[i % len(COLOR_PALETTES)]
        # Row → color, Column → size (small/medium/large)
        row_colors = palette  # row 0,1,2 → palette[0,1,2]

        img = Image.new("RGB", (400, 400), "white")
        draw = ImageDraw.Draw(img)
        cell = 110; pad = 25

        for row in range(3):
            for col in range(3):
                cx = pad + col * cell + cell // 2
                cy = pad + row * cell + cell // 2
                size = 18 + col * 16   # col 0=small, 1=medium, 2=large
                color = row_colors[row]
                is_missing = (row == 2 and col == 2)
                if is_missing:
                    draw.rectangle([cx-cell//2+5, cy-cell//2+5,
                                    cx+cell//2-5, cy+cell//2-5],
                                   outline="#E74C3C", width=2)
                    draw.text((cx-8, cy-8), "?", fill="#E74C3C")
                else:
                    if shape == "circle":
                        draw.ellipse([cx-size, cy-size, cx+size, cy+size],
                                     fill=color, outline="#333", width=2)
                    elif shape == "square":
                        draw.rectangle([cx-size, cy-size, cx+size, cy+size],
                                       fill=color, outline="#333", width=2)
                    else:
                        draw.polygon([(cx, cy-size), (cx-size, cy+size), (cx+size, cy+size)],
                                     fill=color, outline="#333", width=2)

        # Determine correct answer using color NAMES (not hex)
        correct_color_name = HEX_TO_NAME[row_colors[2]]   # row 2 color
        correct_size_name  = "Large"                        # col 2 = large
        correct = f"{correct_size_name} {correct_color_name} {shape}"

        # Build 3 wrong options using color names
        other_colors = [HEX_TO_NAME[c] for c in row_colors[:2]]  # names of row 0 and 1
        wrongs = [
            f"Small {other_colors[0]} {shape}",
            f"Medium {other_colors[1]} {shape}",
            f"Large {other_colors[0]} {shape}",
        ]
        # Make sure none accidentally equal correct
        wrongs = [w for w in wrongs if w != correct]
        opts = [correct] + wrongs[:3]
        while len(opts) < 4:
            opts.append(f"Small {other_colors[0]} {shape}")
        opts = opts[:4]
        random.shuffle(opts)
        cidx = opts.index(correct) if correct in opts else 0
        if correct not in opts:
            opts[0] = correct; cidx = 0

        q_text = f"In the 3x3 matrix, each row has a different colour and each column has a different size ({shape}s). What goes in the missing (?) cell?"
        alt_q  = f"The matrix pattern has {shape}s changing colour by row and size by column. What is the missing piece in the bottom-right cell?"
        if q_text in used:
            q_text = alt_q
        if q_text in used:
            q_text = f"Matrix pattern: {shape}s with row colours {', '.join(HEX_TO_NAME[c] for c in row_colors)}. What is the missing cell?"
        used.add(q_text)

        diff = "Advanced" if grade >= 6 else "Foundation"
        make(img, "matrix-pattern", q_text, opts, cidx,
             "Logical Reasoning", grade, "Patterns and Shapes", "Matrix Patterns", diff,
             f"Row 3 colour = {correct_color_name}, Column 3 size = Large. Missing cell = {correct}.")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if not ADMIN_API_KEY:
        print("[!] ADMIN_API_KEY not set. Set ADMIN_API_KEY env var.")
        sys.exit(1)

    print("=" * 60)
    print("OlympiadReady Diagram Generator")
    print("=" * 60)

    gen_number_line(QUESTIONS_PER_TYPE)
    gen_fraction_bar(QUESTIONS_PER_TYPE)
    gen_bar_graph(QUESTIONS_PER_TYPE)
    gen_geometry(QUESTIONS_PER_TYPE)
    gen_pie_chart(QUESTIONS_PER_TYPE)
    gen_number_series(QUESTIONS_PER_TYPE)
    gen_food_chain(QUESTIONS_PER_TYPE)
    gen_plant_parts(QUESTIONS_PER_TYPE)
    gen_circuit(QUESTIONS_PER_TYPE)
    gen_water_cycle(QUESTIONS_PER_TYPE)
    gen_venn(QUESTIONS_PER_TYPE)
    gen_matrix(QUESTIONS_PER_TYPE)

    total = QUESTIONS_PER_TYPE * 12
    print(f"\n{'='*60}")
    print(f"DONE: {posted} posted, {len(saved_locally)} saved locally, {failed} failed")
    print(f"Total attempted: {total}")
    if saved_locally:
        try:
            out_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            out_dir = os.getcwd()
        out = os.path.join(out_dir, "diagram_questions.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(saved_locally, f, indent=2)
        print(f"Saved locally -> {out}")
