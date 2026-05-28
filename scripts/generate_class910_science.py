"""
generate_class910_science.py
Class 9-10 Science -- Batch 10
NCERT syllabus + SOF NSO standards.

Generators:
  1. Motion & Forces          (Class 9)  -- 20 questions
  2. Light: Reflection/Refraction (Cls 10) -- 20 questions
  3. Electricity & Magnetism  (Class 10) -- 20 questions
  4. Chemical Reactions       (Class 10) -- 20 questions
  5. Matter & Its States      (Class 9)  -- 15 questions
  6. Life Processes           (Class 10) -- 15 questions

Total = 110 questions
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
QPT = 20

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME,
                  api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET)
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

try:
    FONT_SM  = ImageFont.truetype("arial.ttf", 13)
    FONT_MD  = ImageFont.truetype("arial.ttf", 17)
    FONT_LG  = ImageFont.truetype("arial.ttf", 21)
    FONT_XL  = ImageFont.truetype("arial.ttf", 27)
except:
    FONT_SM = FONT_MD = FONT_LG = FONT_XL = ImageFont.load_default()

POSTED = SKIPPED = FAILED = 0

def upload_pil(img, label):
    buf = io.BytesIO()
    img.save(buf, format="PNG"); buf.seek(0)
    r = cloudinary.uploader.upload(buf, folder=CLOUDINARY_FOLDER,
        public_id=f"p10_{label}_{int(time.time()*1000)}", resource_type="image")
    return r["secure_url"]

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

def canvas(w=540, h=400, bg="white"):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)

def arrow(draw, x1, y1, x2, y2, color="#2C3E50", w=2):
    draw.line([(x1,y1),(x2,y2)], fill=color, width=w)
    dx, dy = x2-x1, y2-y1
    L = max(1, math.sqrt(dx*dx+dy*dy))
    ux, uy = dx/L, dy/L
    ax2, ay2 = x2-ux*12, y2-uy*12
    draw.polygon([(x2,y2),(int(ax2-uy*6),int(ay2+ux*6)),(int(ax2+uy*6),int(ay2-ux*6))], fill=color)


# ==============================================================================
# 1. MOTION & FORCES  (Class 9)
# ==============================================================================

def draw_motion(scene="velocity_time"):
    img, draw = canvas(540, 400, "#F0F8FF")
    draw.text((20, 8), f"Motion: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "velocity_time":
        ox, oy = 60, 330
        draw.line([(ox, oy), (490, oy)], fill="#555", width=2)
        draw.line([(ox, oy), (ox, 50)], fill="#555", width=2)
        draw.text((500, oy-5), "t (s)", fill="#555", font=FONT_SM)
        draw.text((ox+5, 38), "v (m/s)", fill="#555", font=FONT_SM)
        # Uniform acceleration line
        draw.line([(ox, oy), (350, 120)], fill="#E74C3C", width=3)
        draw.text((355, 115), "Uniform accel.", fill="#E74C3C", font=FONT_SM)
        # Uniform velocity (horizontal)
        draw.line([(ox, 220), (490, 220)], fill="#27AE60", width=3)
        draw.text((400, 200), "Uniform velocity", fill="#27AE60", font=FONT_SM)
        # Deceleration
        draw.line([(ox, 120), (350, oy)], fill="#3498DB", width=3)
        draw.text((355, oy-25), "Deceleration", fill="#3498DB", font=FONT_SM)
        draw.text((ox-50, oy+15), "0", fill="#555", font=FONT_SM)
        draw.text((20, 370), "Area under v-t graph = displacement  |  Slope = acceleration", fill="#7F8C8D", font=FONT_SM)

    elif scene == "equations":
        draw.text((30, 40), "Equations of Motion (Uniform Acceleration)", fill="#1A5276", font=FONT_LG)
        eqs = [
            ("v = u + at",              "v: final velocity, u: initial, a: acceleration, t: time"),
            ("s = ut + (1/2)at^2",      "s: displacement"),
            ("v^2 = u^2 + 2as",         "relates velocity and displacement"),
            ("s = (u+v)/2 * t",         "average velocity x time"),
        ]
        y = 100
        for eq, desc in eqs:
            draw.rectangle([30, y, 510, y+38], fill="#EBF5FB", outline="#2980B9", width=1)
            draw.text((40, y+8), eq, fill="#E74C3C", font=FONT_LG)
            draw.text((300, y+10), desc, fill="#7F8C8D", font=FONT_SM)
            y += 55
        draw.text((30, 340), "g = 9.8 m/s^2 (acceleration due to gravity, downward)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 368), "Free fall: u=0, a=g  |  v=gt, s=(1/2)gt^2, v^2=2gs", fill="#7F8C8D", font=FONT_SM)

    elif scene == "newtons_laws":
        draw.text((30, 35), "Newton's Laws of Motion", fill="#1A5276", font=FONT_LG)
        laws = [
            ("1st Law (Inertia):",
             "An object remains at rest or in uniform motion unless acted upon by a net external force.",
             "Inertia = tendency to resist change in motion. Mass = measure of inertia."),
            ("2nd Law (F = ma):",
             "Force = mass x acceleration. Net force causes acceleration.",
             "F (N) = m (kg) x a (m/s^2). 1 Newton = force giving 1 kg/s^2 acceleration."),
            ("3rd Law (Action-Reaction):",
             "Every action has an equal and opposite reaction (on different objects).",
             "Rocket propulsion, swimming, recoil of gun are examples."),
        ]
        y = 90
        for title, law, example in laws:
            draw.text((30, y), title, fill="#E74C3C", font=FONT_MD)
            draw.text((30, y+25), law, fill="#2C3E50", font=FONT_SM)
            draw.text((30, y+45), example, fill="#7F8C8D", font=FONT_SM)
            y += 90

    elif scene == "gravitation":
        draw.text((30, 35), "Gravitation and Weight", fill="#1A5276", font=FONT_LG)
        draw.text((30, 75), "Universal Law: F = G*m1*m2 / r^2", fill="#E74C3C", font=FONT_LG)
        draw.text((30, 110), "G = 6.674 x 10^-11 N.m^2/kg^2  (Universal gravitational constant)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 145), "g (surface) = GM/R^2 = 9.8 m/s^2  (Earth)", fill="#2C3E50", font=FONT_MD)
        draw.text((30, 185), "Weight W = mg  (in Newtons)", fill="#3498DB", font=FONT_LG)
        draw.text((30, 220), "Mass: constant everywhere | Weight: changes with location", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 255), "On Moon: g_moon = g_earth / 6 => weight = 1/6 of Earth weight", fill="#27AE60", font=FONT_MD)
        draw.text((30, 295), "Gravitational PE = mgh  (near Earth surface)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 330), "Escape velocity = sqrt(2gR) = 11.2 km/s (Earth)", fill="#9B59B6", font=FONT_SM)
        draw.text((30, 365), "Kepler's 3rd Law: T^2 proportional to r^3 (orbital period vs radius)", fill="#7F8C8D", font=FONT_SM)

    return img

MOTION_QA = [
    ("equations",
     "A car starts from rest and accelerates at 4 m/s^2 for 5 seconds. Its final velocity is:",
     "20 m/s  (v = u + at = 0 + 4*5 = 20 m/s)",
     ["10 m/s", "40 m/s", "5 m/s"],
     "v = u + at. u=0 (starts from rest), a=4, t=5. v = 0 + 4*5 = 20 m/s."),
    ("newtons_laws",
     "Newton's First Law of Motion is also called the Law of:",
     "Inertia",
     ["Action-Reaction", "Momentum", "Gravitation"],
     "Newton's 1st Law (Law of Inertia): a body continues in its state of rest or uniform motion unless acted upon by a net external force."),
    ("equations",
     "A ball is thrown vertically upward with initial velocity 20 m/s. How high does it rise? (g = 10 m/s^2)",
     "20 m  (v^2 = u^2 - 2gs; 0 = 400 - 20s; s = 20 m)",
     ["10 m", "40 m", "200 m"],
     "At max height, v=0. v^2 = u^2 - 2gs (deceleration). 0 = 400 - 2*10*s. s = 400/20 = 20 m."),
    ("velocity_time",
     "The area under a velocity-time graph gives:",
     "Displacement",
     ["Acceleration", "Speed", "Force"],
     "v-t graph: slope = acceleration, area = displacement. s-t graph: slope = velocity."),
    ("newtons_laws",
     "A 5 kg object accelerates at 3 m/s^2. The net force acting on it is:",
     "15 N  (F = ma = 5 * 3)",
     ["8 N", "1.67 N", "0.6 N"],
     "Newton's 2nd Law: F = ma = 5 * 3 = 15 N. Unit: 1 Newton = 1 kg.m/s^2."),
    ("gravitation",
     "The weight of a person of mass 60 kg on the Moon (g_moon = 1.6 m/s^2) is:",
     "96 N  (W = mg = 60 * 1.6 = 96 N)",
     ["588 N", "600 N", "10 N"],
     "W = mg. On Moon: g = 1.6 m/s^2. W = 60 * 1.6 = 96 N. On Earth: 60*9.8 = 588 N. Mass stays 60 kg everywhere."),
    ("velocity_time",
     "A body moving with uniform velocity has acceleration equal to:",
     "Zero",
     ["g (9.8 m/s^2)", "Depends on speed", "Positive"],
     "Uniform velocity = constant speed in a straight line. No change in velocity -> acceleration = 0. On v-t graph: horizontal line."),
    ("equations",
     "A train decelerates uniformly from 72 km/h to rest. If it takes 10 seconds, the deceleration is:",
     "2 m/s^2  (72 km/h = 20 m/s; a = (0-20)/10 = -2 m/s^2)",
     ["7.2 m/s^2", "0.5 m/s^2", "10 m/s^2"],
     "Convert: 72 km/h = 72/3.6 = 20 m/s. a = (v-u)/t = (0-20)/10 = -2 m/s^2. Deceleration = 2 m/s^2."),
    ("newtons_laws",
     "When a gun is fired, the gun recoils backward. This demonstrates Newton's:",
     "3rd Law -- action (bullet forward) and reaction (gun backward) are equal and opposite",
     ["1st Law", "2nd Law", "Law of Gravitation"],
     "Newton's 3rd Law: for every action, equal and opposite reaction. Bullet pushed forward (action); gun pushed backward (reaction)."),
    ("gravitation",
     "The gravitational force between two objects is proportional to:",
     "The product of their masses and inversely proportional to the square of distance (F = Gm1m2/r^2)",
     ["Sum of their masses", "Square of their masses", "Distance between them directly"],
     "Newton's Law of Gravitation: F = Gm1m2/r^2. F increases with mass, decreases with square of distance (inverse square law)."),
    ("equations",
     "A stone dropped from a height of 80 m (g = 10 m/s^2). Time to reach ground:",
     "4 seconds  (s = (1/2)gt^2 => 80 = 5t^2 => t^2=16 => t=4s)",
     ["8 seconds", "2 seconds", "16 seconds"],
     "Free fall from rest: s = (1/2)gt^2. 80 = (1/2)*10*t^2 = 5t^2. t^2 = 16. t = 4 s."),
    ("velocity_time",
     "On a distance-time graph, a straight line with positive slope represents:",
     "Uniform velocity (constant speed)",
     ["Acceleration", "Deceleration", "Rest"],
     "d-t graph: slope = velocity. Straight line -> constant slope -> uniform velocity. Curve -> changing slope -> acceleration."),
    ("newtons_laws",
     "The momentum of a 2 kg object moving at 10 m/s is:",
     "20 kg.m/s  (p = mv = 2 * 10)",
     ["5 kg.m/s", "12 kg.m/s", "0.2 kg.m/s"],
     "Momentum p = mv = 2 * 10 = 20 kg.m/s. Newton's 2nd Law: F = dp/dt (rate of change of momentum)."),
    ("gravitation",
     "The value of 'g' decreases as we:",
     "Go higher above Earth's surface OR go deep below the surface",
     ["Move along the equator", "Move toward the poles", "Increase mass of an object"],
     "g = GM/(R+h)^2. Increases as you go up. Also decreases as you go below Earth's surface. Maximum at Earth's surface. Slightly less at equator."),
    ("equations",
     "A car accelerates uniformly from 10 m/s to 30 m/s over 5 seconds. Distance covered:",
     "100 m  (s = (u+v)/2 * t = (10+30)/2 * 5 = 20*5 = 100 m)",
     ["50 m", "200 m", "150 m"],
     "s = (u+v)/2 * t = (10+30)/2 * 5 = 20 * 5 = 100 m. Or: a=(30-10)/5=4 m/s^2; s=10*5+0.5*4*25=50+50=100 m."),
    ("newtons_laws",
     "The law of conservation of momentum states that:",
     "Total momentum of an isolated system remains constant if no external force acts",
     ["Momentum is always zero", "Momentum equals force", "Only elastic collisions conserve momentum"],
     "Conservation of momentum: m1u1 + m2u2 = m1v1 + m2v2 (no external force). Basis of rocket propulsion and collision analysis."),
    ("velocity_time",
     "Uniform circular motion involves:",
     "Constant speed but changing direction -- hence there IS acceleration (centripetal)",
     ["No acceleration", "Constant velocity", "No force needed"],
     "UCM: speed constant but direction changes continuously -> velocity changes -> acceleration exists. Centripetal acceleration a=v^2/r directed toward center."),
    ("gravitation",
     "Two objects of masses 4 kg and 1 kg are separated by 2 m. If the force between them is F, what is the force when the distance is halved (1 m)?",
     "4F  (F proportional to 1/r^2; halving distance quadruples force)",
     ["2F", "F/4", "F/2"],
     "F = Gm1m2/r^2. New r = 1 m (half). F_new = Gm1m2/1^2 = 4 * Gm1m2/4 = 4F. Inverse square law."),
    ("equations",
     "A body is projected horizontally from a height of 20 m. If g = 10 m/s^2, time to fall:",
     "2 seconds  (vertical: s = (1/2)gt^2 => 20 = 5t^2 => t = 2 s)",
     ["4 seconds", "1 second", "10 seconds"],
     "Horizontal projection: no initial vertical velocity. Vertical: 20 = (1/2)*10*t^2 = 5t^2. t^2 = 4. t = 2 s."),
    ("newtons_laws",
     "An object of mass 10 kg is pushed with a force of 50 N. If friction force is 10 N, its acceleration is:",
     "4 m/s^2  (net F = 50-10 = 40 N; a = 40/10 = 4 m/s^2)",
     ["5 m/s^2", "6 m/s^2", "3 m/s^2"],
     "Net force = Applied - Friction = 50 - 10 = 40 N. a = F_net / m = 40 / 10 = 4 m/s^2."),
]

def gen_motion(n=QPT):
    print(f"[Motion & Forces] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(MOTION_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_motion(scene); url=upload_pil(img, f"mot_{i}")
        ok=post_q("Science", 9, random.choice(["Foundation","Advanced"]),
                  "Motion", "Newton's Laws and Equations of Motion",
                  qtext, url, opts, cidx, expl)
        print(f"  mot_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 2. LIGHT: REFLECTION & REFRACTION  (Class 10)
# ==============================================================================

def draw_light(scene="mirror"):
    img, draw = canvas(540, 400, "#FFFDE7")
    draw.text((20, 8), f"Light: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "mirror":
        cx, cy = 80, 220
        # Concave mirror
        for dy in range(-100, 101, 5):
            x = cx + int(dy*dy/200)
            draw.point((x, cy+dy), fill="#2C3E50")
        draw.text((15, 80), "Concave\nMirror", fill="#2C3E50", font=FONT_SM)
        # Principal axis
        draw.line([(cx, cy), (500, cy)], fill="#AAA", width=1)
        # Focus F
        fx = cx + 140
        draw.ellipse([fx-5, cy-5, fx+5, cy+5], fill="#E74C3C")
        draw.text((fx-5, cy+10), "F", fill="#E74C3C", font=FONT_MD)
        # Centre C
        cc = cx + 280
        draw.ellipse([cc-5, cy-5, cc+5, cy+5], fill="#3498DB")
        draw.text((cc-5, cy+10), "C", fill="#3498DB", font=FONT_MD)
        # Incident ray
        draw.line([(500, cy-100), (cx+5, cy-80)], fill="#F39C12", width=2)
        # Reflected ray (through F)
        draw.line([(cx+5, cy-80), (fx, cy)], fill="#27AE60", width=2)
        draw.text((200, 350), "f = R/2  |  Mirror formula: 1/v + 1/u = 1/f", fill="#2C3E50", font=FONT_MD)
        draw.text((200, 375), "Magnification m = -v/u  (negative = inverted image)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "refraction":
        # Snell's law diagram
        cx, cy = 270, 200
        # Interface
        draw.line([(0, cy), (540, cy)], fill="#3498DB", width=2)
        draw.text((450, cy+5), "Glass/Water", fill="#3498DB", font=FONT_SM)
        draw.text((450, cy-18), "Air (n=1)", fill="#7F8C8D", font=FONT_SM)
        # Normal
        draw.line([(cx, 50), (cx, 370)], fill="#AAA", width=1)
        draw.text((cx+5, 55), "Normal", fill="#AAA", font=FONT_SM)
        # Incident ray
        draw.line([(cx-130, 80), (cx, cy)], fill="#E74C3C", width=3)
        draw.text((cx-145, 70), "Incident", fill="#E74C3C", font=FONT_SM)
        # Refracted ray (bends toward normal entering denser medium)
        draw.line([(cx, cy), (cx+80, 360)], fill="#27AE60", width=3)
        draw.text((cx+82, 355), "Refracted", fill="#27AE60", font=FONT_SM)
        # Angle labels
        draw.text((cx+15, cy-60), "i", fill="#E74C3C", font=FONT_LG)
        draw.text((cx+15, cy+40), "r", fill="#27AE60", font=FONT_LG)
        draw.text((30, 360), "Snell's Law: n1*sin(i) = n2*sin(r)  |  n = c/v = sin(i)/sin(r)", fill="#2C3E50", font=FONT_SM)

    elif scene == "lens":
        # Convex lens
        cx, cy = 270, 210
        # Lens shape
        for y_off in range(-100, 101, 2):
            x_off = int(math.sqrt(max(0, 3600 - y_off*y_off)) - 55)
            draw.point((cx - x_off, cy + y_off), fill="#AED6F1")
            draw.point((cx + x_off, cy + y_off), fill="#AED6F1")
        draw.ellipse([cx-65, cy-100, cx+65, cy+100], outline="#2980B9", width=2)
        # Principal axis
        draw.line([(30, cy), (510, cy)], fill="#AAA", width=1)
        # Foci
        f = 130
        draw.ellipse([cx-f-5, cy-5, cx-f+5, cy+5], fill="#E74C3C")
        draw.text((cx-f-5, cy+8), "F1", fill="#E74C3C", font=FONT_SM)
        draw.ellipse([cx+f-5, cy-5, cx+f+5, cy+5], fill="#E74C3C")
        draw.text((cx+f-5, cy+8), "F2", fill="#E74C3C", font=FONT_SM)
        # Ray 1: parallel to axis, refracts through F2
        draw.line([(80, cy-70), (cx, cy-70)], fill="#F39C12", width=2)
        draw.line([(cx, cy-70), (cx+f, cy)], fill="#F39C12", width=2)
        draw.text((20, 360), "Lens formula: 1/v - 1/u = 1/f  |  Power P = 1/f (in metres) = Dioptres", fill="#2C3E50", font=FONT_SM)
        draw.text((20, 385), "Convex (converging): f>0  |  Concave (diverging): f<0", fill="#7F8C8D", font=FONT_SM)

    return img

def draw_light(scene="mirror"):  # noqa: F811
    img, draw = canvas(540, 400, "#FFFDE7")
    draw.text((20, 8), f"Light: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "mirror":
        cx, cy = 80, 220
        for dy in range(-100, 101, 5):
            x = cx + int(dy*dy/200)
            draw.point((x, cy+dy), fill="#2C3E50")
        draw.text((15, 80), "Concave", fill="#2C3E50", font=FONT_SM)
        draw.text((15, 98), "Mirror", fill="#2C3E50", font=FONT_SM)
        draw.line([(cx, cy), (500, cy)], fill="#AAA", width=1)
        fx = cx + 140
        draw.ellipse([fx-5, cy-5, fx+5, cy+5], fill="#E74C3C")
        draw.text((fx-5, cy+10), "F", fill="#E74C3C", font=FONT_MD)
        cc = cx + 280
        draw.ellipse([cc-5, cy-5, cc+5, cy+5], fill="#3498DB")
        draw.text((cc-5, cy+10), "C", fill="#3498DB", font=FONT_MD)
        draw.line([(500, cy-100), (cx+5, cy-80)], fill="#F39C12", width=2)
        draw.line([(cx+5, cy-80), (fx, cy)], fill="#27AE60", width=2)
        draw.text((160, 345), "f = R/2  |  1/v + 1/u = 1/f", fill="#2C3E50", font=FONT_MD)
        draw.text((160, 372), "Magnification m = -v/u", fill="#7F8C8D", font=FONT_SM)

    elif scene == "refraction":
        cx, cy = 270, 200
        draw.line([(0, cy), (540, cy)], fill="#3498DB", width=2)
        draw.text((450, cy+5), "Glass/Water", fill="#3498DB", font=FONT_SM)
        draw.text((450, cy-18), "Air (n=1)", fill="#7F8C8D", font=FONT_SM)
        draw.line([(cx, 50), (cx, 370)], fill="#AAA", width=1)
        draw.text((cx+5, 55), "Normal", fill="#AAA", font=FONT_SM)
        draw.line([(cx-130, 80), (cx, cy)], fill="#E74C3C", width=3)
        draw.text((cx-145, 70), "Incident", fill="#E74C3C", font=FONT_SM)
        draw.line([(cx, cy), (cx+80, 360)], fill="#27AE60", width=3)
        draw.text((cx+82, 355), "Refracted", fill="#27AE60", font=FONT_SM)
        draw.text((cx+15, cy-60), "i", fill="#E74C3C", font=FONT_LG)
        draw.text((cx+15, cy+40), "r", fill="#27AE60", font=FONT_LG)
        draw.text((30, 360), "Snell's Law: n1*sin(i) = n2*sin(r)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 382), "n = c/v = sin(i)/sin(r) for air-medium", fill="#7F8C8D", font=FONT_SM)

    elif scene == "lens":
        cx, cy = 270, 210
        draw.ellipse([cx-65, cy-100, cx+65, cy+100], fill="#D6EAF8", outline="#2980B9", width=2)
        draw.line([(30, cy), (510, cy)], fill="#AAA", width=1)
        f = 130
        draw.ellipse([cx-f-5, cy-5, cx-f+5, cy+5], fill="#E74C3C")
        draw.text((cx-f-5, cy+8), "F1", fill="#E74C3C", font=FONT_SM)
        draw.ellipse([cx+f-5, cy-5, cx+f+5, cy+5], fill="#E74C3C")
        draw.text((cx+f-5, cy+8), "F2", fill="#E74C3C", font=FONT_SM)
        draw.line([(80, cy-70), (cx, cy-70)], fill="#F39C12", width=2)
        draw.line([(cx, cy-70), (cx+f, cy)], fill="#F39C12", width=2)
        draw.text((20, 345), "1/v - 1/u = 1/f  |  P = 1/f (D)  |  m = v/u", fill="#2C3E50", font=FONT_SM)
        draw.text((20, 372), "Convex: converging, f>0  |  Concave: diverging, f<0", fill="#7F8C8D", font=FONT_SM)

    elif scene == "eye_defects":
        draw.text((30, 40), "Eye Defects and Correction", fill="#1A5276", font=FONT_LG)
        data = [
            ("Myopia (short-sight)", "Distant objects blurred", "Concave (diverging) lens", "#E74C3C"),
            ("Hypermetropia",        "Near objects blurred",    "Convex (converging) lens", "#3498DB"),
            ("Presbyopia",           "Both near and far blurred (old age)", "Bifocal lens", "#27AE60"),
            ("Astigmatism",          "Blurred/distorted vision", "Cylindrical lens", "#9B59B6"),
        ]
        y = 100
        for condition, cause, correction, col in data:
            draw.text((30, y), condition + ":", fill=col, font=FONT_MD)
            draw.text((30, y+22), cause + "  ->  " + correction, fill="#2C3E50", font=FONT_SM)
            y += 68
        draw.text((30, 380), "TIR: critical angle; used in optical fibres, periscopes, diamonds", fill="#7F8C8D", font=FONT_SM)

    return img

LIGHT_QA = [
    ("mirror",
     "The focal length of a concave mirror is 15 cm. Its radius of curvature is:",
     "30 cm  (R = 2f = 2 * 15 = 30 cm)",
     ["15 cm", "7.5 cm", "45 cm"],
     "For spherical mirrors: R = 2f. f = R/2. So R = 2 * 15 = 30 cm."),
    ("refraction",
     "When light travels from air to glass, it:",
     "Slows down and bends toward the normal (glass is optically denser)",
     ["Speeds up and bends away from normal", "Continues in a straight line", "Stops at the surface"],
     "Denser medium: lower speed, higher refractive index. n = c/v. Light bends toward normal in denser medium (Snell's law)."),
    ("lens",
     "A convex lens has focal length 20 cm. Its power is:",
     "+5 D  (P = 1/f(m) = 1/0.20 = +5 dioptres)",
     ["-5 D", "0.05 D", "20 D"],
     "Power P = 1/f (focal length in metres). f = 20 cm = 0.20 m. P = 1/0.20 = +5 D. Positive for convex (converging) lens."),
    ("mirror",
     "An object is placed at the centre of curvature (C) of a concave mirror. The image is:",
     "Real, inverted, same size, at C",
     ["Virtual, erect, magnified, at infinity", "Real, erect, magnified, between F and C", "Real, inverted, diminished, at F"],
     "Object at C (u=2f): using 1/v+1/u=1/f; 1/v+1/2f=1/f; 1/v=1/2f; v=2f (at C). m=-v/u=-1. Real, inverted, same size."),
    ("refraction",
     "The refractive index of glass is 1.5. Speed of light in glass is (c = 3*10^8 m/s):",
     "2 * 10^8 m/s  (v = c/n = 3*10^8/1.5)",
     ["4.5 * 10^8 m/s", "3 * 10^8 m/s", "1 * 10^8 m/s"],
     "n = c/v => v = c/n = 3*10^8/1.5 = 2*10^8 m/s. Light slows down in glass compared to vacuum."),
    ("eye_defects",
     "A person cannot see objects clearly beyond 50 cm. They suffer from:",
     "Myopia (short-sightedness) -- corrected by a concave lens",
     ["Hypermetropia", "Presbyopia", "Astigmatism"],
     "Myopia: image of distant objects forms in front of retina (eyeball too long/lens too curved). Correct with concave (diverging) lens."),
    ("lens",
     "A concave lens always forms an image that is:",
     "Virtual, erect, and diminished -- regardless of object position",
     ["Real and inverted", "Real and magnified", "Virtual and magnified"],
     "Concave (diverging) lens: always forms virtual, erect, diminished image between F and optical centre. Cannot form real image."),
    ("mirror",
     "A convex mirror is used as a rear-view mirror because it:",
     "Gives a wider field of view and always forms a virtual, erect, diminished image",
     ["Magnifies the image", "Gives an inverted image", "Gives a real image"],
     "Convex mirror: always virtual, erect, diminished. Field of view > plane mirror. Useful for seeing traffic behind. f and R are negative (sign convention)."),
    ("refraction",
     "Total internal reflection occurs when:",
     "Light travels from denser to rarer medium and angle of incidence exceeds the critical angle",
     ["Light travels from rarer to denser medium", "Angle of incidence is 0 degrees", "Refractive indices are equal"],
     "TIR: n_dense * sin(critical angle) = n_rare * sin(90) => sin(C) = n_rare/n_dense. Applications: optical fibres, diamonds, mirages."),
    ("lens",
     "An object is placed at infinity from a convex lens (f = 10 cm). The image is formed:",
     "At the focus F (10 cm from lens), real and inverted",
     ["At 2F", "At infinity", "Between F and optical centre"],
     "Object at infinity: parallel rays converge at focus. Using 1/v-1/u=1/f with u=-infinity: 1/v = 1/f. v = f = 10 cm."),
    ("mirror",
     "Using sign convention, the focal length of a convex mirror is:",
     "Positive (+f) -- as the focus is behind the mirror (virtual focus)",
     ["Negative (-f)", "Zero", "Depends on object position"],
     "New Cartesian sign convention: distances measured from pole. Convex mirror: centre of curvature and focus are behind mirror (positive side). f > 0."),
    ("refraction",
     "The phenomenon responsible for the twinkling of stars is:",
     "Atmospheric refraction (varying density layers bend starlight differently)",
     ["Dispersion", "Total internal reflection", "Diffraction"],
     "Stars twinkle (scintillation): star light refracts through multiple atmospheric layers of varying density -> apparent position shifts -> twinkling."),
    ("eye_defects",
     "Optical fibres work on the principle of:",
     "Total internal reflection (light travels through fibre by repeated TIR at walls)",
     ["Refraction only", "Dispersion", "Diffraction"],
     "Optical fibre: glass/plastic core with cladding (lower n). Light hits cladding at angle > critical angle -> TIR -> no light escapes -> transmitted far."),
    ("lens",
     "A person uses spectacles of power -2.5 D. Their defect is:",
     "Myopia (nearsightedness) -- negative power = concave lens",
     ["Hypermetropia", "Presbyopia", "No defect"],
     "Negative power -> concave (diverging) lens -> corrects myopia. Positive power -> convex (converging) -> corrects hypermetropia."),
    ("mirror",
     "The image formed by a plane mirror is:",
     "Virtual, erect, same size, and laterally inverted at same distance behind mirror",
     ["Real and inverted", "Magnified", "At infinity"],
     "Plane mirror: virtual, erect, same size, laterally inverted. Image distance = object distance. Cannot be projected on screen."),
    ("refraction",
     "A ray of light enters a glass slab (n=1.5) at angle of incidence 30 degrees. Angle of refraction:",
     "~19.5 degrees  (sin r = sin30/1.5 = 0.5/1.5 = 0.333; r = 19.5 deg)",
     ["30 degrees", "45 degrees", "10 degrees"],
     "Snell's law: n1 sin i = n2 sin r. 1*sin30 = 1.5*sin r. sin r = 0.5/1.5 = 0.333. r = arcsin(0.333) = 19.5 deg."),
    ("eye_defects",
     "Dispersion of white light through a prism produces a spectrum because:",
     "Different colours (wavelengths) have different speeds in glass, so they refract by different amounts",
     ["White light has no wavelength", "Prism splits light by amplitude", "Red light is faster in glass than violet"],
     "Dispersion: n varies with wavelength (violet has highest n, bends most; red has lowest n, bends least). VIBGYOR spectrum."),
    ("lens",
     "Two thin lenses in contact with powers P1 = +3D and P2 = -1D have combined focal length:",
     "50 cm  (P = P1+P2 = +2D; f = 1/P = 0.5 m = 50 cm)",
     ["25 cm", "100 cm", "33 cm"],
     "P_combined = P1 + P2 = 3 + (-1) = +2 D. f = 1/P = 1/2 = 0.5 m = 50 cm."),
    ("mirror",
     "The mirror formula is 1/v + 1/u = 1/f. For an object at u = -30 cm and f = -10 cm (concave), image distance v is:",
     "-15 cm  (1/v = 1/f - 1/u = -1/10 - (-1/30) = -1/10 + 1/30 = -2/30 = -1/15)",
     ["-30 cm", "+15 cm", "-10 cm"],
     "1/v = 1/f - 1/u = 1/(-10) - 1/(-30) = -1/10 + 1/30 = -3/30 + 1/30 = -2/30 = -1/15. v = -15 cm. Real, inverted image."),
    ("refraction",
     "The refractive index of diamond is ~2.42. Diamond sparkles because:",
     "Its critical angle is very small (~24 deg), so most light undergoes TIR and exits from top facets",
     ["Diamond absorbs coloured light", "Diamond has high melting point", "Diamond is transparent"],
     "Critical angle for diamond: sin C = 1/2.42 = 0.413, C = 24.4 deg. Very small! Light easily undergoes TIR -> brilliance and sparkle."),
]

def gen_light(n=QPT):
    print(f"[Light: Reflection & Refraction] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(LIGHT_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_light(scene); url=upload_pil(img, f"lgt_{i}")
        ok=post_q("Science", 10, random.choice(["Foundation","Advanced"]),
                  "Light", "Reflection, Refraction and Lenses",
                  qtext, url, opts, cidx, expl)
        print(f"  lgt_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 3. ELECTRICITY & MAGNETISM  (Class 10)
# ==============================================================================

def draw_electric(scene="circuit"):
    img, draw = canvas(540, 400, "#F8F9FF")
    draw.text((20, 8), f"Electricity: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "circuit":
        draw.text((30, 40), "Simple Electric Circuit", fill="#1A5276", font=FONT_LG)
        # Battery
        draw.rectangle([60, 160, 100, 240], fill="#FFD700", outline="#2C3E50", width=2)
        draw.text((62, 190), "V", fill="#2C3E50", font=FONT_LG)
        # Wires
        draw.line([(100, 175), (200, 175), (200, 130), (400, 130), (400, 175)], fill="#2C3E50", width=3)
        draw.line([(100, 225), (200, 225), (200, 270), (400, 270), (400, 225)], fill="#2C3E50", width=3)
        # Resistor
        draw.rectangle([360, 160, 440, 240], fill="#ECF0F1", outline="#E74C3C", width=2)
        draw.text((370, 192), "R ohm", fill="#E74C3C", font=FONT_MD)
        # Current arrow
        arrow(draw, 230, 130, 310, 130, "#27AE60", 2)
        draw.text((255, 112), "I (A)", fill="#27AE60", font=FONT_SM)
        draw.text((30, 310), "Ohm's Law: V = IR  (V:volts, I:amperes, R:ohms)", fill="#2C3E50", font=FONT_LG)
        draw.text((30, 345), "Power: P = VI = I^2*R = V^2/R  (in Watts)", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 378), "Energy: E = Pt = VIt  (in Joules or kWh)", fill="#7F8C8D", font=FONT_SM)

    return img

def draw_electric(scene="circuit"):  # noqa: F811
    img, draw = canvas(540, 400, "#F8F9FF")
    draw.text((20, 8), f"Electricity: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "circuit":
        draw.text((30, 40), "Ohm's Law and Electric Circuit", fill="#1A5276", font=FONT_LG)
        draw.rectangle([60, 155, 100, 245], fill="#FFD700", outline="#2C3E50", width=2)
        draw.text((62, 190), "V", fill="#2C3E50", font=FONT_LG)
        draw.line([(100, 170), (200, 170), (200, 130), (420, 130), (420, 170)], fill="#2C3E50", width=3)
        draw.line([(100, 230), (200, 230), (200, 270), (420, 270), (420, 230)], fill="#2C3E50", width=3)
        draw.rectangle([380, 160, 460, 240], fill="#ECF0F1", outline="#E74C3C", width=2)
        draw.text((390, 192), "R", fill="#E74C3C", font=FONT_LG)
        arrow(draw, 230, 130, 330, 130, "#27AE60", 2)
        draw.text((265, 112), "I -->", fill="#27AE60", font=FONT_SM)
        draw.text((30, 305), "Ohm's Law: V = IR", fill="#2C3E50", font=FONT_LG)
        draw.text((30, 340), "Power P = VI = I^2*R = V^2/R  (Watts)", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 372), "1 kWh = 3.6 * 10^6 J  (unit of electrical energy)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "series_parallel":
        draw.text((30, 40), "Series and Parallel Resistance", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Series:  R_total = R1 + R2 + R3 + ...", fill="#E74C3C", font=FONT_LG)
        draw.text((40, 110), "Same current through all; voltage divides", fill="#7F8C8D", font=FONT_SM)
        draw.text((40, 132), "Example: R1=2, R2=3, R3=5 => R_total = 10 ohm", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 170), "Parallel: 1/R_total = 1/R1 + 1/R2 + 1/R3 + ...", fill="#3498DB", font=FONT_LG)
        draw.text((40, 200), "Same voltage across all; current divides", fill="#7F8C8D", font=FONT_SM)
        draw.text((40, 222), "Example: R1=6, R2=3 => 1/R=1/6+1/3=1/2 => R=2 ohm", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 265), "Parallel R < smallest individual resistor", fill="#27AE60", font=FONT_MD)
        draw.text((30, 305), "Household wiring: parallel (each device gets full voltage)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 335), "Fuse: thin wire that melts at high current -> breaks circuit", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 365), "MCB (miniature circuit breaker): reusable safety device", fill="#7F8C8D", font=FONT_SM)

    elif scene == "magnetism":
        draw.text((30, 40), "Magnetic Effects of Electric Current", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Oersted's discovery: current-carrying wire creates magnetic field", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 110), "Right-hand thumb rule: thumb along current -> fingers show B field", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 148), "Solenoid = coil of wire -> acts like bar magnet (uniform B inside)", fill="#3498DB", font=FONT_MD)
        draw.text((30, 185), "Electromagnet: solenoid with iron core (temporary magnet)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 220), "Force on current-carrying conductor in B field:", fill="#27AE60", font=FONT_MD)
        draw.text((40, 248), "F = BIL*sin(theta)  |  Fleming's Left-Hand Rule", fill="#27AE60", font=FONT_SM)
        draw.text((30, 285), "DC motor: converts electrical -> mechanical energy (LHR)", fill="#9B59B6", font=FONT_SM)
        draw.text((30, 315), "Generator: converts mechanical -> electrical energy (RHR)", fill="#9B59B6", font=FONT_SM)
        draw.text((30, 355), "Faraday's Law: EMF = -d(phi)/dt  (changing flux induces EMF)", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 380), "Transformer: changes AC voltage V1/V2 = N1/N2 = I2/I1", fill="#7F8C8D", font=FONT_SM)

    elif scene == "heating":
        draw.text((30, 40), "Heating Effect of Current", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Joule's Law: H = I^2 * R * t", fill="#E74C3C", font=FONT_XL)
        draw.text((30, 125), "H = heat produced (Joules)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 150), "I = current (A), R = resistance (ohm), t = time (s)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 190), "Applications:", fill="#2C3E50", font=FONT_LG)
        apps = ["Electric bulb (tungsten filament, high R)", "Electric iron, heater, toaster",
                "Fuse (low melting point wire)", "Electric arc welding"]
        y = 230
        for app in apps:
            draw.text((40, y), "* " + app, fill="#2C3E50", font=FONT_SM)
            y += 30
        draw.text((30, 365), "Resistivity: R = rho * L / A  (rho = material property)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 390), "Nichrome: high resistivity + high melting point -> used in heaters", fill="#7F8C8D", font=FONT_SM)

    return img

ELEC_QA = [
    ("circuit",
     "A 6V battery is connected to a 2-ohm resistor. The current flowing is:",
     "3 A  (I = V/R = 6/2 = 3 A)",
     ["12 A", "0.33 A", "4 A"],
     "Ohm's Law: V = IR. I = V/R = 6/2 = 3 A."),
    ("series_parallel",
     "Three resistors of 3 ohm, 6 ohm, and 9 ohm are connected in series. Total resistance:",
     "18 ohm  (R = 3 + 6 + 9 = 18 ohm)",
     ["2 ohm", "9 ohm", "1.5 ohm"],
     "Series: R_total = R1+R2+R3 = 3+6+9 = 18 ohm. Same current flows through all resistors."),
    ("heating",
     "An electric heater of resistance 10 ohm carries 2 A for 30 minutes. Heat produced:",
     "72,000 J  (H = I^2*R*t = 4*10*1800 = 72000 J)",
     ["600 J", "1200 J", "7200 J"],
     "H = I^2*R*t. t=30 min=1800 s. H = 2^2 * 10 * 1800 = 4*10*1800 = 72,000 J."),
    ("magnetism",
     "The direction of force on a current-carrying conductor in a magnetic field is given by:",
     "Fleming's Left-Hand Rule (FBI rule)",
     ["Fleming's Right-Hand Rule", "Right-Hand Thumb Rule", "Lenz's Law"],
     "Fleming's LHR: First finger=B (field), seCond finger=I (current), thuMb=Motion (force). Used for motors."),
    ("circuit",
     "The SI unit of electric resistance is:",
     "Ohm (symbol: omega)",
     ["Ampere", "Volt", "Watt"],
     "Resistance: unit is Ohm (omega). V=IR: 1 ohm = 1 volt/ampere. Named after Georg Simon Ohm."),
    ("series_parallel",
     "Two resistors of 4 ohm and 12 ohm are connected in parallel. Their equivalent resistance is:",
     "3 ohm  (1/R = 1/4 + 1/12 = 3/12 + 1/12 = 4/12; R = 3 ohm)",
     ["16 ohm", "8 ohm", "48 ohm"],
     "1/R = 1/4 + 1/12 = 3/12 + 1/12 = 4/12. R = 12/4 = 3 ohm. Parallel R < smallest individual R (4 ohm)."),
    ("heating",
     "A 100W bulb used for 10 hours consumes:",
     "1 kWh (unit = 1 kilowatt-hour = 3.6 * 10^6 J)",
     ["10 kWh", "0.1 kWh", "100 kWh"],
     "Energy = Power * time = 100 W * 10 h = 1000 Wh = 1 kWh. 1 kWh = 3.6 * 10^6 J (SI units)."),
    ("magnetism",
     "An electric generator works on the principle of:",
     "Electromagnetic induction (Faraday's law -- changing magnetic flux induces EMF)",
     ["Magnetic effect of current", "Heating effect of current", "Ohm's Law"],
     "Generator: mechanical energy -> electrical. Coil rotates in magnetic field -> flux changes -> EMF induced (Faraday's law). AC generator."),
    ("circuit",
     "The resistance of a conductor is doubled if:",
     "Its length is doubled (R is proportional to L) OR its cross-sectional area is halved",
     ["Its temperature is halved", "Current through it is doubled", "Voltage across it is halved"],
     "R = rho*L/A. R proportional to L: doubling L doubles R. R inversely proportional to A: halving A doubles R."),
    ("series_parallel",
     "In a parallel circuit, the voltage across each branch is:",
     "Same (equal to the source voltage)",
     ["Different for each branch", "Sum of all voltages", "Zero"],
     "Parallel: all branches connected directly across the source. Each branch has the same voltage as the source. Current divides."),
    ("heating",
     "Which material is used for the filament of an electric bulb and why?",
     "Tungsten -- very high melting point (3422 deg C) and high resistivity, so it glows white-hot",
     ["Copper -- good conductor", "Nichrome -- low resistance", "Silver -- high conductivity"],
     "Tungsten: melting point 3422 deg C (highest of all metals). High resistivity -> gets very hot -> emits light. Coiled to reduce heat loss."),
    ("magnetism",
     "A step-up transformer has 100 turns in primary and 1000 turns in secondary. If primary voltage is 220V:",
     "Secondary voltage = 2200V  (V2/V1 = N2/N1 = 1000/100 = 10)",
     ["22V", "220V", "22000V"],
     "V2/V1 = N2/N1. V2 = V1 * N2/N1 = 220 * 1000/100 = 2200 V. Step-up increases voltage; step-down decreases it."),
    ("circuit",
     "Ohm's Law is valid for:",
     "Metallic conductors at constant temperature (ohmic conductors)",
     ["All conductors at all temperatures", "Diodes", "Electrolytes at all conditions"],
     "Ohm's Law: V proportional to I (V=IR) only for ohmic conductors at constant temperature. Non-ohmic: diodes, thermistors, electrolytic cells."),
    ("series_parallel",
     "Why are household electrical appliances connected in parallel?",
     "Each appliance gets the full supply voltage, and each can be operated independently",
     ["To reduce total current", "To use less wire", "To share voltage"],
     "Parallel wiring: each appliance gets full 220V (India). Independent operation (one off doesn't affect others). More current drawn as more appliances added."),
    ("heating",
     "The commercial unit of electrical energy is:",
     "Kilowatt-hour (kWh) -- also called 1 unit",
     ["Joule", "Watt", "Ampere-hour"],
     "1 kWh = 1 unit of electrical energy. 1 kWh = 1000 W * 3600 s = 3.6 * 10^6 J. Electricity bills are in kWh (units consumed)."),
    ("magnetism",
     "The right-hand thumb rule is used to determine:",
     "Direction of magnetic field around a straight current-carrying conductor",
     ["Force on a conductor in a field", "Direction of induced current", "Polarity of electromagnet end"],
     "Right-hand thumb rule: if thumb points in direction of current, curled fingers show direction of circular magnetic field."),
    ("circuit",
     "Three bulbs of equal resistance are connected in series. If one bulb fuses, the others:",
     "All go out (circuit is broken in series -- same current path)",
     ["Continue to glow at same brightness", "Glow brighter", "Two continue, one goes out"],
     "Series circuit: same current flows through all. If one component fails (open circuit), current stops -> all go out. Disadvantage of series wiring."),
    ("series_parallel",
     "The equivalent resistance of n identical resistors each of value R connected in parallel is:",
     "R/n",
     ["nR", "R", "n/R"],
     "For n identical resistors in parallel: 1/R_eq = n/R. R_eq = R/n. E.g., 5 resistors of 10 ohm in parallel: 10/5 = 2 ohm."),
    ("heating",
     "Why does nichrome wire glow but the connecting copper wires don't get hot?",
     "Nichrome has much higher resistivity than copper; more heat generated per unit length in nichrome",
     ["Copper conducts no current", "Nichrome has lower melting point", "Copper is not a metal"],
     "H = I^2*R*t. Same current, but R(nichrome) >> R(copper). Heat generated proportional to R. Copper barely heats; nichrome glows red-hot."),
    ("magnetism",
     "Lenz's Law states that the direction of induced current is such that it:",
     "Opposes the change in magnetic flux that caused it (conservation of energy)",
     ["Adds to the changing flux", "Is in the same direction as the inducing current", "Depends on the material"],
     "Lenz's Law (special case of energy conservation): induced EMF/current opposes cause. E.g., bringing N-pole toward coil induces N-pole on same face -> repulsion."),
]

def gen_electric(n=QPT):
    print(f"[Electricity & Magnetism] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(ELEC_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_electric(scene); url=upload_pil(img, f"elc_{i}")
        ok=post_q("Science", 10, random.choice(["Foundation","Advanced"]),
                  "Electricity", "Circuits, Resistance and Magnetism",
                  qtext, url, opts, cidx, expl)
        print(f"  elc_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 4. CHEMICAL REACTIONS  (Class 10)
# ==============================================================================

def draw_chem(scene="types"):
    img, draw = canvas(540, 400, "#F0FFF4")
    draw.text((20, 8), f"Chemical Reactions: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "types":
        draw.text((30, 40), "Types of Chemical Reactions", fill="#1A5276", font=FONT_LG)
        data = [
            ("Combination",     "A + B -> AB         [2H2 + O2 -> 2H2O]",             "#27AE60"),
            ("Decomposition",   "AB -> A + B          [2H2O -> 2H2 + O2]",             "#E74C3C"),
            ("Displacement",    "A + BC -> AC + B     [Fe + CuSO4 -> FeSO4 + Cu]",     "#3498DB"),
            ("Double disp.",    "AB + CD -> AD + CB   [NaCl + AgNO3 -> AgCl + NaNO3]","#9B59B6"),
            ("Redox",           "Oxidation + reduction occur simultaneously",            "#F39C12"),
            ("Neutralisation",  "Acid + Base -> Salt + Water",                          "#E67E22"),
            ("Precipitation",   "Insoluble product (precipitate) forms",                "#7F8C8D"),
        ]
        y = 90
        for name, desc, col in data:
            draw.text((30, y), name + ":", fill=col, font=FONT_SM)
            draw.text((170, y), desc, fill="#2C3E50", font=FONT_SM)
            y += 42

    elif scene == "redox":
        draw.text((30, 40), "Oxidation and Reduction (Redox)", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Oxidation: loss of electrons / gain of oxygen / loss of H", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 110), "Reduction: gain of electrons / loss of oxygen / gain of H", fill="#3498DB", font=FONT_MD)
        draw.text((30, 150), "OIL RIG: Oxidation Is Loss, Reduction Is Gain (of electrons)", fill="#F39C12", font=FONT_MD)
        draw.text((30, 195), "Example: Zn + CuSO4 -> ZnSO4 + Cu", fill="#2C3E50", font=FONT_LG)
        draw.text((40, 230), "Zn -> Zn2+ + 2e-  (oxidised, loses electrons)", fill="#E74C3C", font=FONT_SM)
        draw.text((40, 255), "Cu2+ + 2e- -> Cu  (reduced, gains electrons)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 295), "Oxidising agent: gains electrons (causes oxidation)", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 320), "Reducing agent: loses electrons (causes reduction)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 360), "Rusting: 4Fe + 3O2 + 2H2O -> 2Fe2O3.H2O (slow oxidation)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "acids_bases":
        draw.text((30, 40), "Acids, Bases and Salts", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Acid: pH < 7, releases H+ ions, turns blue litmus red", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 110), "Base: pH > 7, releases OH- ions, turns red litmus blue", fill="#3498DB", font=FONT_MD)
        draw.text((30, 140), "Neutral: pH = 7 (pure water)", fill="#27AE60", font=FONT_SM)
        draw.text((30, 175), "Strong acids: HCl, H2SO4, HNO3  (fully ionise in water)", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 200), "Weak acids: CH3COOH, H2CO3  (partially ionise)", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 235), "Neutralisation: HCl + NaOH -> NaCl + H2O", fill="#F39C12", font=FONT_MD)
        draw.text((30, 270), "Baking soda: NaHCO3 (weak base, used in cooking + antacids)", fill="#9B59B6", font=FONT_SM)
        draw.text((30, 295), "Washing soda: Na2CO3.10H2O (water softener, cleaning)", fill="#9B59B6", font=FONT_SM)
        draw.text((30, 330), "Bleaching powder: Ca(OCl)Cl  (disinfectant, whitening)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 360), "Plaster of Paris: CaSO4.1/2H2O + H2O -> CaSO4.2H2O", fill="#7F8C8D", font=FONT_SM)

    elif scene == "metals":
        draw.text((30, 40), "Metals and Non-metals", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Activity series (reactivity): K>Na>Ca>Mg>Al>Zn>Fe>Pb>H>Cu>Ag>Au", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 115), "More reactive metal displaces less reactive from solution", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 155), "Metals with O2: form oxides  (4Na + O2 -> 2Na2O)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 180), "Metals with water: Na/K react violently; Fe reacts slowly", fill="#3498DB", font=FONT_SM)
        draw.text((30, 215), "Corrosion: slow surface reaction with environment", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 248), "Prevention: galvanising, alloying, painting, electroplating", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 285), "Alloys: brass(Cu+Zn), bronze(Cu+Sn), solder(Pb+Sn), steel(Fe+C)", fill="#27AE60", font=FONT_SM)
        draw.text((30, 320), "Thermite: Fe2O3 + Al -> Al2O3 + Fe + heat (used in welding)", fill="#F39C12", font=FONT_SM)
        draw.text((30, 360), "Amphoteric: Al, Zn react with both acids AND bases", fill="#9B59B6", font=FONT_SM)

    return img

CHEM_QA = [
    ("types",
     "In the reaction 2Mg + O2 -> 2MgO, the type of reaction is:",
     "Combination reaction (two reactants combine to form one product)",
     ["Decomposition", "Displacement", "Double displacement"],
     "Combination: A + B -> AB. Here Mg and O2 combine to form MgO. Also an oxidation reaction (Mg loses electrons)."),
    ("redox",
     "In the reaction CuO + H2 -> Cu + H2O, which substance is oxidised?",
     "H2 (gains oxygen, forms H2O -- oxidation)",
     ["CuO", "Cu", "H2O"],
     "H2 gains oxygen -> oxidised (reducing agent). CuO loses oxygen -> reduced (oxidising agent). OIL RIG."),
    ("acids_bases",
     "The pH of a neutral solution (like pure water) at 25 deg C is:",
     "7  ([H+] = [OH-] = 10^-7 M)",
     ["0", "14", "1"],
     "pH = -log[H+]. Pure water: [H+] = 10^-7 M, pH = 7. Acids: pH < 7. Bases: pH > 7."),
    ("metals",
     "Iron reacts with copper sulphate solution because:",
     "Iron is more reactive than copper (higher in the activity series)",
     ["Iron is heavier than copper", "Both are metals", "CuSO4 is acidic"],
     "Fe + CuSO4 -> FeSO4 + Cu. Fe displaces Cu because Fe is more reactive (higher in reactivity series). Blue CuSO4 solution turns light green."),
    ("types",
     "Decomposition of calcium carbonate on heating (CaCO3 -> CaO + CO2) is called:",
     "Thermal decomposition (heat causes breakdown)",
     ["Combination", "Electrolytic decomposition", "Double displacement"],
     "Decomposition: AB -> A + B. Calcium carbonate (limestone) decomposes on heating to quicklime (CaO) and CO2. Used in cement industry."),
    ("redox",
     "Rusting of iron is an example of:",
     "Slow oxidation (Fe reacts with O2 and water over time)",
     ["Reduction", "Decomposition", "Neutralisation"],
     "Rusting: 4Fe + 3O2 + 6H2O -> 4Fe(OH)3 -> Fe2O3.H2O. Iron is oxidised. Electrolyte (water) acts as medium. Prevented by galvanising."),
    ("acids_bases",
     "Sodium hydroxide (NaOH) reacts with hydrochloric acid (HCl). The products are:",
     "NaCl (common salt) + H2O  (neutralisation reaction)",
     ["NaH + Cl2O", "Na + HCl2", "NaCl2 + H2O2"],
     "Neutralisation: Acid + Base -> Salt + Water. NaOH + HCl -> NaCl + H2O. Strong acid + strong base: pH of product = 7."),
    ("metals",
     "Aluminium is said to be amphoteric because it:",
     "Reacts with both acids (HCl) and bases (NaOH)",
     ["Conducts electricity", "Is a transition metal", "Has high density"],
     "Amphoteric metals: Al, Zn. React with HCl -> AlCl3 + H2. React with NaOH -> NaAlO2 + H2. Rare property."),
    ("types",
     "AgNO3 + NaCl -> AgCl (white ppt.) + NaNO3 is an example of:",
     "Double displacement / precipitation reaction",
     ["Combination", "Decomposition", "Redox"],
     "Double displacement: AB + CD -> AD + CB. Two compounds exchange ions. AgCl is insoluble (white precipitate). Used to test for chloride ions."),
    ("redox",
     "Which of the following is an oxidising agent in the reaction: Zn + H2SO4 -> ZnSO4 + H2?",
     "H2SO4 (dilute) -- H+ ions gain electrons and are reduced to H2",
     ["Zn", "ZnSO4", "H2"],
     "Zn loses electrons (oxidised, reducing agent). H+ gains electrons -> H2 (reduced, oxidising agent). Dilute H2SO4 = oxidising agent here."),
    ("acids_bases",
     "Baking soda (NaHCO3) is used in baking because when heated it:",
     "Decomposes releasing CO2 which makes the dough rise (2NaHCO3 -> Na2CO3 + H2O + CO2)",
     ["Adds sweet taste", "Provides sodium", "Acts as a preservative"],
     "NaHCO3 -> Na2CO3 + H2O + CO2 on heating. CO2 gas forms bubbles -> dough rises. Also used as antacid (neutralises stomach acid)."),
    ("metals",
     "Galvanisation is the process of coating iron with:",
     "Zinc (to prevent rusting -- zinc acts as sacrificial anode)",
     ["Copper", "Tin", "Silver"],
     "Galvanisation: iron coated with zinc. Even if zinc layer scratches, zinc (more reactive) corrodes instead of iron (sacrificial protection)."),
    ("types",
     "In a displacement reaction, a more reactive element replaces a less reactive element. Which reaction is correct?",
     "Zn + CuSO4 -> ZnSO4 + Cu  (Zn more reactive than Cu)",
     ["Cu + ZnSO4 -> CuSO4 + Zn", "Fe + MgCl2 -> FeCl2 + Mg", "Ag + NaCl -> AgCl + Na"],
     "Zn > Cu in reactivity series, so Zn displaces Cu from solution. Cu cannot displace Zn (less reactive). Fe cannot displace Mg."),
    ("acids_bases",
     "The gas produced when zinc reacts with dilute hydrochloric acid is:",
     "Hydrogen gas (Zn + 2HCl -> ZnCl2 + H2)",
     ["Oxygen", "Chlorine", "Carbon dioxide"],
     "Zn + 2HCl -> ZnCl2 + H2. Hydrogen gas produced (burns with pop sound). Test for H2: burning splint -> 'pop' sound."),
    ("redox",
     "Which of the following statements about oxidation is correct?",
     "Oxidation involves loss of electrons (increase in oxidation state)",
     ["Oxidation involves gain of electrons", "Oxidation only involves oxygen", "Oxidation and reduction are unrelated"],
     "Modern definition: oxidation = loss of electrons (increase in oxidation number). OIL RIG: Oxidation Is Loss, Reduction Is Gain (of electrons)."),
    ("metals",
     "The thermite reaction (Fe2O3 + 2Al -> Al2O3 + 2Fe) is a displacement reaction because:",
     "Aluminium (more reactive) displaces iron from its oxide",
     ["Iron is more reactive than Al", "A new compound forms", "Heat is released"],
     "Reactivity: Al > Fe. Al reduces Fe2O3 to Fe (displaces it). Produces intense heat (~2500 deg C). Used in welding railway tracks."),
    ("types",
     "Photosynthesis (6CO2 + 6H2O -> C6H12O6 + 6O2) is classified as a:",
     "Endothermic, combination-type reaction (energy absorbed from light)",
     ["Exothermic decomposition", "Neutralisation", "Double displacement"],
     "Photosynthesis: absorbs light energy (endothermic). CO2 + H2O combine to form glucose and O2. Type: combination/synthesis reaction."),
    ("acids_bases",
     "Universal indicator shows the pH of a solution by:",
     "Showing different colours at different pH values (red=acidic, green=neutral, violet=alkaline)",
     ["Turning only red or blue", "Measuring temperature", "Reacting chemically to produce gas"],
     "Universal indicator: mixture of indicators. Shows a range of colours across pH 0-14. Red-orange=acidic, green=neutral, blue-violet=alkaline."),
    ("metals",
     "Which metal is extracted by electrolysis because it cannot be reduced by carbon?",
     "Aluminium (Al is more reactive than carbon; extracted by Hall-Heroult electrolytic process)",
     ["Iron", "Copper", "Zinc"],
     "Metals more reactive than carbon (Na, K, Mg, Al, Ca) cannot be extracted by carbon reduction. Aluminium extracted by electrolysis of molten Al2O3."),
    ("redox",
     "In the reaction MnO2 + 4HCl -> MnCl2 + 2H2O + Cl2, the oxidising agent is:",
     "MnO2  (Mn reduces from +4 to +2, gains electrons -- acts as oxidising agent)",
     ["HCl", "MnCl2", "Cl2"],
     "MnO2: Mn oxidation state +4 -> +2 (gain of 2 electrons = reduction). MnO2 is the oxidising agent. HCl: Cl- -> Cl2 (loses electrons, oxidised)."),
]

def gen_chem(n=QPT):
    print(f"[Chemical Reactions] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(CHEM_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_chem(scene); url=upload_pil(img, f"rxn_{i}")
        ok=post_q("Science", 10, random.choice(["Foundation","Advanced"]),
                  "Chemical Reactions", "Types, Redox and Acids/Bases",
                  qtext, url, opts, cidx, expl)
        print(f"  rxn_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 5. MATTER & ITS STATES  (Class 9)
# ==============================================================================

def draw_matter(scene="states"):
    img, draw = canvas(540, 400, "#FFF3E0")
    draw.text((20, 8), f"Matter: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "states":
        draw.text((30, 40), "States of Matter", fill="#1A5276", font=FONT_LG)
        for x, state, color, desc in [
            (90,  "SOLID",  "#3498DB", "Fixed shape & volume\nParticles close, vibrate"),
            (270, "LIQUID", "#27AE60", "Fixed volume, no shape\nParticles slide past each other"),
            (450, "GAS",    "#E74C3C", "No fixed shape/volume\nParticles far apart, fast"),
        ]:
            draw.ellipse([x-65, 120, x+65, 250], fill=color, outline="#2C3E50", width=2)
            draw.text((x-25, 175), state, fill="white", font=FONT_SM)
            lines = desc.split("\n")
            draw.text((x-60, 265), lines[0], fill="#2C3E50", font=FONT_SM)
            draw.text((x-60, 283), lines[1], fill="#7F8C8D", font=FONT_SM)
        draw.line([(155, 185), (205, 185)], fill="#F39C12", width=3)
        draw.text((163, 168), "Melt", fill="#F39C12", font=FONT_SM)
        draw.line([(335, 185), (385, 185)], fill="#F39C12", width=3)
        draw.text((340, 168), "Evap.", fill="#F39C12", font=FONT_SM)
        draw.text((30, 360), "Sublimation: solid -> gas directly (dry ice CO2, camphor, iodine)", fill="#9B59B6", font=FONT_SM)
        draw.text((30, 385), "Plasma: 4th state -- ionised gas at very high temperature (stars, lightning)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "solutions":
        draw.text((30, 40), "Mixtures, Solutions and Separation", fill="#1A5276", font=FONT_LG)
        data = [
            ("True solution",   "Homogeneous, < 1nm particles (salt water, sugar water)", "#3498DB"),
            ("Colloid",         "1-100 nm particles, Tyndall effect (milk, fog, blood)", "#27AE60"),
            ("Suspension",      "> 100 nm, heterogeneous, settles (muddy water, chalk)", "#E74C3C"),
            ("Separation methods:", "", "#1A5276"),
            ("Filtration",      "Solid from liquid (insoluble)", "#9B59B6"),
            ("Evaporation",     "Soluble solid from solution", "#9B59B6"),
            ("Distillation",    "Liquids with different boiling points", "#9B59B6"),
            ("Chromatography",  "Dyes/pigments based on solubility", "#9B59B6"),
        ]
        y = 90
        for name, desc, col in data:
            draw.text((30, y), name, fill=col, font=FONT_SM)
            if desc:
                draw.text((220, y), desc, fill="#2C3E50", font=FONT_SM)
            y += 38

    return img

MATTER_QA = [
    ("states",
     "The process of conversion of a solid directly into vapour without passing through liquid state is called:",
     "Sublimation (e.g., dry ice, iodine, camphor, naphthalene)",
     ["Evaporation", "Condensation", "Melting"],
     "Sublimation: solid -> gas (without liquid phase). Examples: CO2 (dry ice), iodine, camphor, ammonium chloride."),
    ("solutions",
     "Which of the following shows the Tyndall effect?",
     "Colloid (e.g., milk, fog, smoke) -- scattered beam of light visible",
     ["True solution (salt water)", "Pure water", "All solutions"],
     "Tyndall effect: scattering of light by colloidal particles (1-100 nm). Beam of light visible through fog/smoke. Not seen in true solutions."),
    ("states",
     "The intermolecular forces of attraction are strongest in:",
     "Solids (particles tightly packed, high attractive forces, fixed positions)",
     ["Liquids", "Gases", "Plasma"],
     "Intermolecular forces: Solids > Liquids > Gases. Solids: strong forces, fixed lattice. Gases: very weak, particles far apart."),
    ("solutions",
     "A mixture of sand and water can be separated by:",
     "Filtration (sand is insoluble in water and forms a suspension)",
     ["Distillation", "Evaporation", "Chromatography"],
     "Sand is insoluble in water -> suspension. Filtration separates insoluble solids from liquids. Sand stays on filter paper; water passes through."),
    ("states",
     "Latent heat of vaporisation is the heat required to:",
     "Convert 1 kg of liquid to vapour at its boiling point (without change in temperature)",
     ["Raise temperature by 1 degree C", "Convert solid to liquid", "Freeze 1 kg of liquid"],
     "Latent heat of vaporisation (L_v): heat absorbed during liquid->gas at constant temperature. For water: 2.26 MJ/kg at 100 deg C."),
    ("solutions",
     "Ink is separated into its component dyes by:",
     "Chromatography (components travel at different rates on paper)",
     ["Distillation", "Filtration", "Decantation"],
     "Paper chromatography: ink components dissolve differently in solvent and travel different distances up the paper, separating by colour."),
    ("states",
     "Evaporation causes cooling because:",
     "High-energy molecules escape as vapour, leaving behind lower-energy (cooler) molecules",
     ["Water absorbs heat from surroundings", "Air cools the liquid", "Evaporation is exothermic"],
     "Evaporation: faster-moving surface molecules escape, removing kinetic energy from liquid. Average KE (temperature) of remaining liquid decreases."),
    ("solutions",
     "A solution is said to be saturated when:",
     "No more solute can dissolve at that temperature (maximum solubility reached)",
     ["It contains very little solute", "It has dissolved all available solvent", "Its pH is 7"],
     "Saturated solution: maximum amount of solute dissolved at a given temperature. Adding more solute -> precipitates. Supersaturated: unstable, excess dissolved."),
    ("states",
     "The boiling point of water decreases at higher altitudes because:",
     "Atmospheric pressure is lower, so water boils at a lower temperature",
     ["Temperature is lower", "Water has less mass", "Gravity is weaker"],
     "Boiling: vapour pressure = atmospheric pressure. At high altitude, lower atmospheric pressure -> boiling at lower temperature (< 100 deg C)."),
    ("solutions",
     "In a true solution, the solute particles are:",
     "Less than 1 nm in size -- completely dissolved, cannot be separated by filtration",
     ["Between 1-100 nm", "Greater than 100 nm", "Visible to naked eye"],
     "True solution: solute < 1 nm, transparent, homogeneous, stable, no Tyndall effect. Colloid: 1-100 nm. Suspension: >100 nm, settles."),
    ("states",
     "The density of water is maximum at:",
     "4 degrees C (anomalous expansion of water -- important for aquatic life in winter)",
     ["0 degrees C", "100 degrees C", "25 degrees C"],
     "Water at 4 deg C has maximum density. Below 4 deg C, water expands on cooling. Ice (0 deg C) is less dense than water -> floats. Lakes freeze from top."),
    ("solutions",
     "Butter is an example of which type of colloid?",
     "Emulsion (liquid dispersed in liquid -- fat droplets in water)",
     ["Gel", "Foam", "Aerosol"],
     "Colloid types: emulsion (liq in liq): milk, butter, cream. Gel (liq in solid): jelly. Foam (gas in liq): whipped cream. Aerosol (liq in gas): fog."),
    ("states",
     "Which of the following is a physical change?",
     "Dissolving sugar in water (sugar can be recovered by evaporation)",
     ["Burning of wood", "Rusting of iron", "Cooking of food"],
     "Physical change: no new substance formed, reversible. Dissolving, melting, boiling. Chemical change: new substance, often irreversible. Burning, rusting."),
    ("solutions",
     "The process of obtaining pure water from saline water (sea water) by distillation is called:",
     "Distillation (or desalination -- collecting pure steam that condenses)",
     ["Filtration", "Evaporation", "Chromatography"],
     "Distillation: heat saline water -> steam (pure water vapour) -> cool and condense. Salt remains behind. Used to make distilled water."),
    ("states",
     "Dry ice is solid CO2. When placed in air, it undergoes:",
     "Sublimation -- directly converts to CO2 gas at -78.5 deg C without becoming liquid",
     ["Melting", "Evaporation", "Condensation"],
     "Dry ice: CO2 at normal atmospheric pressure sublimes at -78.5 deg C. Cannot exist as liquid at normal pressure. Used for cold storage and special effects."),
]

def gen_matter(n=15):
    print(f"[Matter & Its States] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(MATTER_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_matter(scene); url=upload_pil(img, f"mat_{i}")
        ok=post_q("Science", 9, random.choice(["Foundation","Advanced"]),
                  "Matter", "States of Matter and Mixtures",
                  qtext, url, opts, cidx, expl)
        print(f"  mat_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 6. LIFE PROCESSES  (Class 10)
# ==============================================================================

def draw_life(scene="nutrition"):
    img, draw = canvas(540, 400, "#F0FFF0")
    draw.text((20, 8), f"Life Processes: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "nutrition":
        draw.text((30, 40), "Modes of Nutrition", fill="#1A5276", font=FONT_LG)
        data = [
            ("Autotrophic",  "Make own food (photosynthesis/chemosynthesis): plants, algae, bacteria", "#27AE60"),
            ("Heterotrophic","Depend on others for food:", "#E74C3C"),
            ("  Holozoic",   "Ingest solid food (animals, Amoeba)", "#E74C3C"),
            ("  Saprophytic","Feed on dead matter (fungi, bacteria)", "#9B59B6"),
            ("  Parasitic",  "Feed on living host (tapeworm, Cuscuta)", "#F39C12"),
            ("Mixotrophic",  "Both auto and hetero (Euglena)", "#3498DB"),
        ]
        y = 90
        for name, desc, col in data:
            draw.text((30, y), name + ":", fill=col, font=FONT_SM)
            draw.text((180, y), desc, fill="#2C3E50", font=FONT_SM)
            y += 45
        draw.text((30, 378), "Photosynthesis equation: 6CO2 + 6H2O -> C6H12O6 + 6O2 (light, chlorophyll)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "respiration":
        draw.text((30, 40), "Cellular Respiration", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Aerobic: C6H12O6 + 6O2 -> 6CO2 + 6H2O + 38 ATP", fill="#27AE60", font=FONT_MD)
        draw.text((30, 115), "Occurs in mitochondria. 38 ATP produced.", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 155), "Anaerobic (without O2):", fill="#E74C3C", font=FONT_LG)
        draw.text((40, 190), "In yeast: C6H12O6 -> 2C2H5OH + 2CO2 + 2 ATP (fermentation)", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 215), "In muscle (lactic acid): C6H12O6 -> 2C3H6O3 + 2 ATP", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 255), "Breathing rate: ~15-18 times/min (adult)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 285), "Gaseous exchange in humans: alveoli in lungs", fill="#3498DB", font=FONT_SM)
        draw.text((30, 315), "Gaseous exchange in fish: gills (dissolved O2 in water)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 345), "Gaseous exchange in plants: stomata (leaves), lenticels (stem)", fill="#3498DB", font=FONT_SM)

    elif scene == "transport":
        draw.text((30, 40), "Transportation in Living Organisms", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "In plants:", fill="#E74C3C", font=FONT_MD)
        draw.text((40, 108), "Xylem: water and minerals (roots to leaves, upward)", fill="#3498DB", font=FONT_SM)
        draw.text((40, 130), "Phloem: food/sugars (source to sink, bidirectional)", fill="#27AE60", font=FONT_SM)
        draw.text((30, 165), "In humans:", fill="#E74C3C", font=FONT_MD)
        draw.text((40, 193), "Blood: O2, CO2, nutrients, hormones, waste", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 215), "Heart: 4 chambers, double circulation", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 237), "Arteries: carry blood AWAY from heart (oxygenated)", fill="#E74C3C", font=FONT_SM)
        draw.text((40, 259), "Veins: carry blood TO heart (deoxygenated)", fill="#3498DB", font=FONT_SM)
        draw.text((40, 281), "Capillaries: site of exchange with tissues", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 320), "Lymph: carries WBCs, returns excess fluid to blood", fill="#9B59B6", font=FONT_SM)
        draw.text((30, 355), "Platelets: blood clotting (fibrinogen -> fibrin)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "excretion":
        draw.text((30, 40), "Excretion in Living Organisms", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Humans: kidneys filter blood and produce urine", fill="#E74C3C", font=FONT_MD)
        draw.text((40, 110), "Nephron: functional unit of kidney (reabsorption of glucose, water)", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 132), "Glomerular filtration -> tubular reabsorption -> secretion", fill="#7F8C8D", font=FONT_SM)
        draw.text((40, 154), "Urine: water, urea, salts, creatinine", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 190), "Plants excretion:", fill="#3498DB", font=FONT_MD)
        draw.text((40, 218), "O2 (by-product of photosynthesis) -- through stomata", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 240), "CO2 (by-product of respiration) -- through stomata", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 262), "Excess water: transpiration through stomata/lenticels", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 284), "Latex, resins, oils: stored in leaves/bark (may drop seasonally)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 325), "Dialysis: artificial kidney (filter waste from blood)", fill="#9B59B6", font=FONT_SM)
        draw.text((30, 355), "ADH (antidiuretic hormone): regulates water reabsorption in kidney", fill="#7F8C8D", font=FONT_SM)
    return img

LIFE_QA = [
    ("nutrition",
     "Autotrophic nutrition is seen in:",
     "Green plants and some bacteria (photosynthesis -- make own food from CO2 and H2O)",
     ["Fungi", "Animals", "Tapeworm"],
     "Autotrophs: synthesise own organic food from inorganic materials using light (photosynthesis) or chemical energy (chemosynthesis). Plants, algae, cyanobacteria."),
    ("respiration",
     "In aerobic respiration, glucose is completely broken down into:",
     "CO2 + H2O + ATP (38 ATP molecules per glucose)",
     ["Ethanol + CO2", "Lactic acid only", "CO2 + ATP (no water)"],
     "Aerobic: C6H12O6 + 6O2 -> 6CO2 + 6H2O + 38 ATP. Complete oxidation in mitochondria. Much more efficient than anaerobic."),
    ("transport",
     "In plants, water is transported from roots to leaves through:",
     "Xylem vessels (dead cells forming continuous tubes)",
     ["Phloem", "Stomata", "Root hairs directly"],
     "Xylem: dead tracheids and vessels. Water moves via transpiration pull (cohesion-tension). Root pressure also contributes, esp. at night."),
    ("excretion",
     "The functional unit of the human kidney is:",
     "Nephron (about 1 million nephrons per kidney)",
     ["Glomerulus", "Ureter", "Renal artery"],
     "Nephron: tubular structure. Bowman's capsule + glomerulus (filtration) -> PCT -> Loop of Henle -> DCT -> collecting duct -> urine."),
    ("nutrition",
     "The raw materials for photosynthesis are:",
     "CO2 (from air through stomata) and H2O (from soil through roots)",
     ["O2 and glucose", "N2 and CO2", "Starch and water"],
     "Photosynthesis: 6CO2 + 6H2O -> C6H12O6 + 6O2. CO2 enters through stomata. Water absorbed by roots. Light energy from sun. Chlorophyll is the pigment."),
    ("respiration",
     "Yeast produces ethanol during fermentation because:",
     "In absence of oxygen, yeast breaks glucose into ethanol and CO2 (anaerobic respiration)",
     ["Yeast contains alcohol", "Oxygen oxidises glucose to alcohol", "Temperature is too high"],
     "Anaerobic: glucose -> ethanol + CO2 + 2 ATP (in yeast). Used in bread-making (CO2 rises dough) and alcohol production."),
    ("transport",
     "Arteries are different from veins because arteries:",
     "Carry blood away from the heart, have thick elastic walls, and carry oxygenated blood (except pulmonary artery)",
     ["Carry blood to the heart", "Have thin walls", "Carry deoxygenated blood always"],
     "Arteries: thick muscular walls (high pressure blood from heart), carry blood away. Veins: thin walls, valves (prevent backflow), carry blood to heart."),
    ("excretion",
     "Plants primarily excrete oxygen as a waste product of:",
     "Photosynthesis (water is split; O2 is released through stomata)",
     ["Respiration", "Transpiration", "Nitrogen fixation"],
     "Photosynthesis: O2 is produced from water splitting (light reactions). O2 exits through stomata. CO2 is excreted during respiration."),
    ("nutrition",
     "Amoeba engulfs food by the process of:",
     "Phagocytosis (pseudopodia engulf food into food vacuole)",
     ["Osmosis", "Photosynthesis", "Diffusion"],
     "Amoeba: holozoic nutrition. Pseudopodia surround food particle -> food vacuole forms -> digestive enzymes digest food inside. Products absorbed."),
    ("respiration",
     "Breathing rate increases during exercise because:",
     "Muscles produce more CO2 -> detected by brain -> increases breathing rate to expel CO2 and take in more O2",
     ["We breathe faster out of habit", "O2 decreases first", "Lung capacity increases"],
     "CO2 increase in blood detected by medulla oblongata -> signals diaphragm/intercostals to contract faster. O2 need also increases."),
    ("transport",
     "What is the role of haemoglobin in blood?",
     "Carries oxygen from lungs to body tissues (Hb + O2 -> HbO2, bright red)",
     ["Clotting of blood", "Carrying CO2 only", "Fighting infection"],
     "Haemoglobin (Hb): red protein in RBCs. 4 haem groups, each binds 1 O2. HbO2 (oxyhaemoglobin) -> releases O2 at tissues. RBCs have no nucleus."),
    ("excretion",
     "The process of removing harmful nitrogenous waste from the body is called:",
     "Excretion (urea from protein metabolism removed via kidneys as urine)",
     ["Egestion", "Secretion", "Transpiration"],
     "Excretion: removal of metabolic waste (urea, CO2, excess salts, water). Egestion: removal of undigested food (faeces -- not a metabolic waste)."),
    ("nutrition",
     "Stomata in leaves serve the dual function of:",
     "Gas exchange (CO2 in, O2 out during photosynthesis) AND water vapour loss (transpiration)",
     ["Only CO2 entry", "Only water loss", "Nutrient absorption from air"],
     "Stomata: pores in leaf epidermis controlled by guard cells. During day: open for CO2/O2 exchange and transpiration. At night: mostly closed."),
    ("respiration",
     "Lactic acid fermentation in muscles causes:",
     "Muscle fatigue and cramps (lactic acid accumulates when O2 supply is insufficient)",
     ["Energy production equal to aerobic", "CO2 and ethanol", "More efficient ATP production"],
     "During intense exercise, O2 supply insufficient -> anaerobic: glucose -> lactic acid + 2 ATP. Lactic acid accumulation -> pain/cramps. Removed to liver later."),
    ("transport",
     "In humans, blood pressure is highest in the:",
     "Aorta (just after leaving the left ventricle -- highest pressure in the circulatory system)",
     ["Capillaries", "Veins", "Pulmonary vein"],
     "Blood pressure: highest in aorta (after ventricular contraction). Decreases as blood flows through arteries -> arterioles -> capillaries -> venules -> veins."),
]

def gen_life(n=15):
    print(f"[Life Processes] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(LIFE_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_life(scene); url=upload_pil(img, f"life_{i}")
        ok=post_q("Science", 10, random.choice(["Foundation","Advanced"]),
                  "Life Processes", "Nutrition, Respiration and Transport",
                  qtext, url, opts, cidx, expl)
        print(f"  life_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OlympiadReady -- Class 9-10 Science (Batch 10)")
    print("=" * 60)
    print()

    gen_motion(QPT)
    gen_light(QPT)
    gen_electric(QPT)
    gen_chem(QPT)
    gen_matter(15)
    gen_life(15)

    print("=" * 60)
    print(f"DONE -- Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}")
    print("=" * 60)
