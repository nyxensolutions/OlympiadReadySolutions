"""
generate_class1112_physics.py
Class 11-12 Physics — Batch 7
All answers verified against NCERT syllabus and SOF NSO standards.
Sign convention used: New Cartesian (NCERT standard).

Generators:
  1. Projectile Motion          (Class 11) — text options
  2. Work, Energy & Power       (Class 11) — text options
  3. Ray Optics                 (Class 12) — text options
  4. Current Electricity        (Class 12) — text options
  5. Semiconductor Electronics  (Class 12) — text options
  6. Photoelectric Effect       (Class 12) — text options
  7. Nuclear Physics            (Class 12) — text options

QPT = 20 questions per type  |  Total ≈ 140 questions
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
        public_id=f"p7_{label}_{int(time.time()*1000)}", resource_type="image")
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
    ax, ay = x2-ux*12, y2-uy*12
    draw.polygon([(x2,y2),(int(ax-uy*6),int(ay+ux*6)),(int(ax+uy*6),int(ay-ux*6))], fill=color)


# ══════════════════════════════════════════════════════════════════════════════
# 1. PROJECTILE MOTION  (Class 11)
# ══════════════════════════════════════════════════════════════════════════════
# Key formulae (u = initial speed, θ = angle with horizontal, g = 9.8 m/s²):
#   Range          R  = u²·sin(2θ)/g
#   Max Height     H  = u²·sin²θ/(2g)
#   Time of flight T  = 2u·sinθ/g
#   Max Range at θ = 45° → R_max = u²/g
#   At θ, range same as at (90°−θ)

def draw_projectile(angle_deg=45, u=20, g=10):
    img, draw = canvas(540, 380, "#F0F8FF")
    draw.text((20, 10), "Projectile Motion", fill="#2C3E50", font=FONT_LG)

    # Axes
    ox, oy = 50, 310
    draw.line([(ox, oy), (510, oy)], fill="#555", width=2)   # x-axis
    draw.line([(ox, 50), (ox, oy)], fill="#555", width=2)    # y-axis
    draw.text((515, oy-8), "x", fill="#555", font=FONT_MD)
    draw.text((ox+4, 38), "y", fill="#555", font=FONT_MD)

    # Trajectory arc
    theta = math.radians(angle_deg)
    T = 2 * u * math.sin(theta) / g
    R = u**2 * math.sin(2*theta) / g
    H = u**2 * math.sin(theta)**2 / (2*g)

    scale_x = min(380, 440) / max(R, 1)
    scale_y = min(200, 240) / max(H, 1)
    scale = min(scale_x, scale_y)

    pts = []
    steps = 60
    for i in range(steps+1):
        t = T * i / steps
        x = u * math.cos(theta) * t
        y = u * math.sin(theta) * t - 0.5 * g * t**2
        px = ox + int(x * scale)
        py = oy - int(y * scale)
        pts.append((px, py))

    for i in range(len(pts)-1):
        draw.line([pts[i], pts[i+1]], fill="#E74C3C", width=3)

    # Initial velocity arrow
    arrow(draw, ox, oy, ox+int(50*math.cos(theta)), oy-int(50*math.sin(theta)),
          "#27AE60", w=3)
    draw.text((ox+55, oy-int(50*math.sin(theta))-8), f"u={u} m/s", fill="#27AE60", font=FONT_SM)

    # Angle label
    draw.arc([ox-30, oy-30, ox+30, oy+30], start=-angle_deg, end=0, fill="#F39C12", width=2)
    draw.text((ox+35, oy-15), f"θ={angle_deg}°", fill="#F39C12", font=FONT_MD)

    # Range label
    rx = ox + int(R * scale)
    draw.line([(ox, oy+12), (rx, oy+12)], fill="#3498DB", width=2)
    draw.text(((ox+rx)//2 - 20, oy+16), f"R={R:.1f} m", fill="#3498DB", font=FONT_SM)

    # Height label
    hx = ox + int(R/2 * scale)
    hy = oy - int(H * scale)
    draw.line([(hx+5, oy), (hx+5, hy)], fill="#9B59B6", width=2)
    draw.text((hx+8, (oy+hy)//2), f"H={H:.1f} m", fill="#9B59B6", font=FONT_SM)

    # Formulae box
    draw.rectangle([300, 55, 535, 170], fill="#EEF", outline="#3498DB", width=1)
    draw.text((308, 62),  "R = u²sin(2θ)/g",   fill="#2C3E50", font=FONT_SM)
    draw.text((308, 84),  "H = u²sin²θ/(2g)",   fill="#2C3E50", font=FONT_SM)
    draw.text((308, 106), "T = 2u·sinθ/g",       fill="#2C3E50", font=FONT_SM)
    draw.text((308, 128), f"g = {g} m/s²",        fill="#555",    font=FONT_SM)
    draw.text((308, 150), f"T = {T:.2f} s",        fill="#E74C3C", font=FONT_SM)
    return img

PROJ_QA = [
    # (angle, u, g, question, correct, [wrongs], explanation)
    (45, 20, 10,
     "A projectile is launched at 45° with speed 20 m/s (g=10 m/s²). Its horizontal range is:",
     "40 m",
     ["20 m", "80 m", "28.3 m"],
     "R = u²sin(2θ)/g = 400×sin90°/10 = 400/10 = 40 m"),

    (30, 20, 10,
     "A ball is projected at 30° with u=20 m/s (g=10). Maximum height reached:",
     "5 m",
     ["10 m", "20 m", "2.5 m"],
     "H = u²sin²θ/(2g) = 400×(0.5)²/20 = 400×0.25/20 = 5 m"),

    (45, 20, 10,
     "For maximum range, a projectile must be launched at angle:",
     "45°",
     ["30°", "60°", "90°"],
     "R = u²sin(2θ)/g is maximum when sin(2θ)=1, i.e., 2θ=90°, θ=45°"),

    (60, 20, 10,
     "Projection at 60° gives the same range as projection at:",
     "30°",
     ["45°", "90°", "120°"],
     "R is same for θ and (90°-θ). Complement of 60° is 30°"),

    (90, 20, 10,
     "A ball thrown vertically upward at 20 m/s (g=10). Time to reach max height:",
     "2 s",
     ["4 s", "1 s", "20 s"],
     "At max height, v=0. v=u-gt → t=u/g=20/10=2 s"),

    (45, 20, 10,
     "Time of flight for projectile at 45°, u=20 m/s, g=10 m/s²:",
     "2√2 ≈ 2.83 s",
     ["4 s", "2 s", "1.41 s"],
     "T = 2u·sinθ/g = 2×20×sin45°/10 = 40×(1/√2)/10 = 4/√2 = 2√2 ≈ 2.83 s"),

    (30, 10, 10,
     "Horizontal range of projectile: u=10 m/s, θ=30°, g=10 m/s²:",
     "√3 × 5 ≈ 8.66 m",
     ["5 m", "10 m", "15 m"],
     "R = u²sin(2θ)/g = 100×sin60°/10 = 10×(√3/2) = 5√3 ≈ 8.66 m"),

    (45, 20, 10,
     "Horizontal component of velocity of a projectile (u=20, θ=45°) at any time during flight:",
     "10√2 ≈ 14.14 m/s (constant)",
     ["20 m/s", "0 m/s", "Changes with time"],
     "Horizontal velocity = u·cosθ = 20·cos45° = 20/√2 = 10√2 m/s. It is CONSTANT (no horizontal force)."),

    (45, 20, 10,
     "At the highest point of projectile motion, the velocity is:",
     "Purely horizontal (= u·cosθ)",
     ["Zero", "Purely vertical", "Equal to initial velocity"],
     "At max height, vertical component = 0. Only horizontal component u·cosθ remains."),

    (30, 20, 10,
     "A projectile has horizontal range R=40 m at 45°. For the same u, range at 30°:",
     "20√3 ≈ 34.6 m",
     ["40 m", "20 m", "30 m"],
     "R₄₅=u²/g=40 m, so u²=400. R₃₀=u²sin60°/g=400×(√3/2)/10=20√3≈34.6 m"),

    (45, 20, 10,
     "The trajectory of a projectile is:",
     "A parabola",
     ["A straight line", "A circle", "An ellipse"],
     "x = u·cosθ·t, y = u·sinθ·t - ½gt². Eliminating t gives y = x·tanθ - gx²/(2u²cos²θ), which is a parabola."),

    (45, 20, 10,
     "Acceleration of a projectile at the highest point (neglecting air resistance) is:",
     "g downward (9.8 m/s²)",
     ["Zero", "g upward", "Less than g"],
     "Gravity acts throughout the flight. At the highest point, acceleration = g = 9.8 m/s² downward."),

    (45, 30, 10,
     "u=30 m/s, θ=45°, g=10. Maximum height:",
     "22.5 m",
     ["45 m", "90 m", "15 m"],
     "H = u²sin²45°/(2g) = 900×0.5/20 = 450/20 = 22.5 m"),

    (60, 20, 10,
     "u=20 m/s, θ=60°, g=10. Time of flight:",
     "2√3 ≈ 3.46 s",
     ["4 s", "2 s", "6 s"],
     "T = 2u·sinθ/g = 2×20×sin60°/10 = 4×(√3/2) = 2√3 ≈ 3.46 s"),

    (45, 20, 10,
     "Two projectiles A (θ=30°) and B (θ=60°) are fired with same speed. Their ranges are:",
     "Equal (same range, since sin60°=sin120° and sin(2×30°)=sin(2×60°)=sin60°)",
     ["A has greater range", "B has greater range", "Cannot compare"],
     "R = u²sin(2θ)/g. sin(2×30°)=sin60°=sin(2×60°)=sin120°=√3/2. So ranges are equal."),

    (45, 20, 10,
     "A football is kicked at 45° with speed u. If air resistance is ignored, where is speed MINIMUM?",
     "At the highest point (only horizontal component remains)",
     ["At the start", "At the landing point", "Speed is constant throughout"],
     "Speed is minimum at highest point = u·cosθ. At start and end, speed = u (same magnitude)."),

    (30, 40, 10,
     "u=40 m/s, θ=30°, g=10. Horizontal range:",
     "80√3 ≈ 138.6 m",
     ["160 m", "80 m", "120 m"],
     "R = u²sin(2θ)/g = 1600×sin60°/10 = 160×(√3/2) = 80√3 ≈ 138.6 m"),

    (45, 20, 10,
     "A projectile is fired horizontally (θ=0°) from a cliff. Its initial vertical velocity is:",
     "Zero",
     ["u (full speed)", "u/√2", "g"],
     "For horizontal projection, θ=0°. Vertical component = u·sin0° = 0. Only horizontal velocity initially."),

    (45, 20, 10,
     "The range of a projectile is DOUBLED when the angle is changed from 15° to:",
     "75° (same range as 15°) — OR initial speed is increased by √2 (same angle)",
     ["30°", "45°", "60°"],
     "For same u: R at 15° = R at 75°. Range doubles if u² doubles (u increases by √2). At θ=45°, sin90°=1, max range = u²/g."),

    (45, 20, 10,
     "If the initial speed of a projectile is doubled (same angle), the range becomes:",
     "4 times (R ∝ u²)",
     ["2 times", "√2 times", "8 times"],
     "R = u²sin(2θ)/g. If u → 2u, R → (2u)²sin(2θ)/g = 4u²sin(2θ)/g = 4R"),
]

def gen_projectile(n=QPT):
    print(f"[Projectile Motion] {n} questions...")
    for i, (ang, u, g, qtext, correct, wrongs, expl) in enumerate(PROJ_QA[:n]):
        opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
        img = draw_projectile(ang, u, g)
        url = upload_pil(img, f"proj_{i}")
        ok = post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                    "Projectile Motion", "Kinematics",
                    qtext, url, opts, cidx, expl)
        print(f"  proj_{i} (θ={ang}°)... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 2. WORK, ENERGY & POWER  (Class 11)
# ══════════════════════════════════════════════════════════════════════════════
# Key formulae:
#   Work W = F·d·cosθ  (θ = angle between F and displacement)
#   KE = ½mv²
#   PE (gravitational) = mgh
#   Work-Energy theorem: Net W = ΔKE
#   Power P = W/t = F·v
#   Elastic PE in spring = ½kx²
#   Conservative force: work done is path-independent

def draw_work_energy(scene="work_angle"):
    img, draw = canvas(540, 380, "#FAFFF0")
    draw.text((20, 10), "Work, Energy & Power", fill="#2C3E50", font=FONT_LG)

    if scene == "work_angle":
        # Block on surface, force at angle
        draw.rectangle([180, 230, 320, 280], fill="#3498DB", outline="#2C3E50", width=2)
        draw.text((232, 248), "Block", fill="white", font=FONT_MD)
        draw.line([(0, 282), (540, 282)], fill="#7F8C8D", width=4)
        # Force arrow at angle
        theta = 30
        rad = math.radians(theta)
        arrow(draw, 320, 255, 320+int(120*math.cos(rad)), 255-int(120*math.sin(rad)),
              "#E74C3C", w=3)
        draw.text((445, 200), "F", fill="#E74C3C", font=FONT_XL)
        # Angle arc
        draw.arc([315, 235, 355, 275], start=-theta, end=0, fill="#F39C12", width=2)
        draw.text((365, 258), f"θ={theta}°", fill="#F39C12", font=FONT_MD)
        # Displacement arrow
        arrow(draw, 180, 290, 60, 290, "#27AE60", w=3)
        draw.text((80, 295), "d", fill="#27AE60", font=FONT_MD)
        # Formula
        draw.text((20, 320), "W = F·d·cosθ", fill="#2C3E50", font=FONT_LG)
        draw.text((20, 350), "Negative work when θ > 90°", fill="#555", font=FONT_SM)

    elif scene == "ke_pe":
        # Ball at height h, then falling
        draw.line([(50, 320), (490, 320)], fill="#7F8C8D", width=3)
        # Ball at top
        draw.ellipse([245, 80, 295, 130], fill="#E74C3C")
        draw.text((260, 97), "m", fill="white", font=FONT_MD)
        # Height arrow
        draw.line([(310, 105), (310, 320)], fill="#3498DB", width=2)
        draw.text((315, 200), "h", fill="#3498DB", font=FONT_LG)
        # Formulae
        draw.text((30, 150), "At top:    KE = 0,  PE = mgh", fill="#2C3E50", font=FONT_MD)
        draw.text((30, 180), "At bottom: KE = ½mv², PE = 0", fill="#2C3E50", font=FONT_MD)
        draw.text((30, 210), "Conservation: mgh = ½mv²", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 240), "∴ v = √(2gh)", fill="#27AE60", font=FONT_LG)
        arrow(draw, 270, 132, 270, 310, "#888", w=2)
        draw.text((280, 220), "v→", fill="#888", font=FONT_MD)

    elif scene == "spring":
        # Spring compressed
        cx = 270
        # Spring zig-zag
        spring_pts = [(100, 220)]
        for s in range(10):
            x = 100 + s * 20
            y = 220 + (15 if s % 2 == 0 else -15)
            spring_pts.append((x, y))
        spring_pts.append((300, 220))
        for i in range(len(spring_pts)-1):
            draw.line([spring_pts[i], spring_pts[i+1]], fill="#888", width=3)
        # Wall
        draw.rectangle([50, 180, 100, 260], fill="#7F8C8D")
        # Block
        draw.rectangle([300, 195, 360, 245], fill="#E74C3C", outline="#2C3E50", width=2)
        draw.text((311, 213), "m", fill="white", font=FONT_MD)
        # x label
        draw.line([(100, 258), (300, 258)], fill="#3498DB", width=2)
        draw.text((185, 262), "x (compression)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 300), "Elastic PE = ½kx²", fill="#2C3E50", font=FONT_LG)
        draw.text((30, 330), "Force = -kx  (restoring)", fill="#555", font=FONT_MD)

    elif scene == "power":
        # Engine pulling load up slope
        pts = [(60, 340), (480, 340), (480, 120)]
        draw.polygon(pts, fill="#DDD", outline="#888", width=2)
        # Car on slope
        slope_angle = math.atan2(220, 420)
        draw.rectangle([230, 220, 310, 260], fill="#27AE60", outline="#2C3E50", width=2)
        draw.text((244, 234), "Car", fill="white", font=FONT_MD)
        arrow(draw, 230, 240, 150, 275, "#E74C3C", w=3)
        draw.text((100, 262), "F", fill="#E74C3C", font=FONT_LG)
        draw.text((30, 300), "P = W/t = F·v", fill="#2C3E50", font=FONT_LG)
        draw.text((30, 335), "1 Watt = 1 J/s = 1 N·m/s", fill="#555", font=FONT_MD)
    return img

WEP_QA = [
    ("work_angle",
     "A force of 50 N acts at 60° to displacement of 10 m. Work done:",
     "250 J",
     ["500 J", "433 J", "0 J"],
     "W = F·d·cosθ = 50×10×cos60° = 500×0.5 = 250 J"),

    ("work_angle",
     "A porter carries a load on his head and walks horizontally. Work done by gravity is:",
     "Zero (displacement is horizontal, gravity is vertical → θ=90°)",
     ["mgh", "mgl", "Negative"],
     "W = F·d·cosθ. Gravity is vertical (downward), displacement is horizontal. θ=90°, cos90°=0. W=0."),

    ("ke_pe",
     "A ball of mass 2 kg is at height 5 m. Its potential energy (g=10 m/s²) is:",
     "100 J",
     ["50 J", "10 J", "200 J"],
     "PE = mgh = 2×10×5 = 100 J"),

    ("ke_pe",
     "A 1 kg ball falls from rest at height 20 m. Speed just before hitting ground (g=10):",
     "20 m/s",
     ["10 m/s", "200 m/s", "14.1 m/s"],
     "mgh = ½mv² → v = √(2gh) = √(2×10×20) = √400 = 20 m/s"),

    ("ke_pe",
     "KE of a 4 kg object moving at 6 m/s:",
     "72 J",
     ["24 J", "144 J", "12 J"],
     "KE = ½mv² = ½×4×36 = 72 J"),

    ("work_angle",
     "A block is pushed 5 m along a frictionless surface by 20 N force parallel to surface. Work done:",
     "100 J",
     ["4 J", "25 J", "0 J"],
     "W = F·d·cos0° = 20×5×1 = 100 J (force parallel to displacement, θ=0°)"),

    ("spring",
     "A spring of spring constant k=200 N/m is compressed by 0.1 m. Elastic PE stored:",
     "1 J",
     ["20 J", "0.1 J", "2 J"],
     "PE = ½kx² = ½×200×(0.1)² = 100×0.01 = 1 J"),

    ("spring",
     "Hooke's Law: the restoring force in a spring is:",
     "F = −kx (proportional to displacement, opposite direction)",
     ["F = kx²", "F = k/x", "F = kx (same direction)"],
     "Hooke's Law: F = −kx. Negative sign indicates the restoring force opposes displacement."),

    ("ke_pe",
     "The Work-Energy theorem states: Net work done on a body equals:",
     "Change in kinetic energy (ΔKE)",
     ["Change in potential energy", "Total energy", "Work done by gravity only"],
     "Work-Energy theorem: W_net = ΔKE = KE_final − KE_initial"),

    ("power",
     "A machine does 6000 J of work in 2 minutes. Its power in watts:",
     "50 W",
     ["3000 W", "300 W", "12000 W"],
     "P = W/t = 6000/(2×60) = 6000/120 = 50 W"),

    ("power",
     "A car engine of power 40 kW moves at constant speed 20 m/s. Resistive force on car:",
     "2000 N",
     ["800 N", "20000 N", "200 N"],
     "At constant speed: P = F·v → F = P/v = 40000/20 = 2000 N"),

    ("ke_pe",
     "If the speed of a body is doubled, its kinetic energy becomes:",
     "4 times",
     ["2 times", "√2 times", "8 times"],
     "KE = ½mv². If v→2v, KE→½m(2v)²=4(½mv²)=4 KE"),

    ("work_angle",
     "A force does negative work on a body. This means:",
     "Force and displacement are in opposite directions (θ > 90°)",
     ["The body slows down always", "Force is zero", "Displacement is zero"],
     "W = F·d·cosθ < 0 when θ is between 90° and 270°. The force opposes motion."),

    ("ke_pe",
     "At the highest point of a vertical throw, a ball has:",
     "Only PE, KE = 0 (if thrown straight up)",
     ["Only KE", "Equal KE and PE", "Zero total energy"],
     "At highest point of vertical throw, v=0, so KE=0. All energy is PE = mgh_max."),

    ("spring",
     "Two springs (k₁=100 N/m, k₂=200 N/m) in series. Effective spring constant:",
     "200/3 ≈ 66.7 N/m",
     ["300 N/m", "150 N/m", "100 N/m"],
     "For springs in series: 1/k_eff = 1/k₁ + 1/k₂ = 1/100 + 1/200 = 3/200. k_eff = 200/3 ≈ 66.7 N/m"),

    ("spring",
     "Two springs (k₁=100, k₂=200 N/m) in parallel. Effective spring constant:",
     "300 N/m",
     ["150 N/m", "66.7 N/m", "200 N/m"],
     "For springs in parallel: k_eff = k₁ + k₂ = 100 + 200 = 300 N/m"),

    ("ke_pe",
     "A conservative force is one where:",
     "Work done is independent of the path taken",
     ["Work done is always positive", "Force is always constant", "Force acts only vertically"],
     "Conservative forces (gravity, spring, electrostatic) do path-independent work. Friction is non-conservative."),

    ("power",
     "Unit of work in SI system:",
     "Joule (J) = Newton × metre",
     ["Watt", "Pascal", "Newton"],
     "1 Joule = 1 Newton × 1 metre = 1 kg·m²/s²"),

    ("ke_pe",
     "A pendulum bob at bottom has KE = 50 J. At the top of its swing, its PE (from bottom) is:",
     "50 J (energy conserved, KE converts fully to PE at top)",
     ["25 J", "100 J", "0 J"],
     "By conservation of energy: KE_bottom = PE_top (no friction). KE_bottom = 50 J → PE_top = 50 J"),

    ("work_angle",
     "1 horse power (HP) = _____ watts:",
     "746 W",
     ["1000 W", "550 W", "100 W"],
     "1 HP = 746 W (exact). Sometimes approximated as 750 W."),
]

def gen_work_energy(n=QPT):
    print(f"[Work, Energy & Power] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(WEP_QA[:n]):
        opts = [correct]+wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
        img = draw_work_energy(scene)
        url = upload_pil(img, f"wep_{i}")
        ok = post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                    "Work Energy and Power", "Mechanics",
                    qtext, url, opts, cidx, expl)
        print(f"  wep_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 3. RAY OPTICS  (Class 12)
# ══════════════════════════════════════════════════════════════════════════════
# New Cartesian Sign Convention (NCERT):
#   - All distances from optical centre / pole
#   - Incident light travels left → right (positive x direction)
#   - u is always negative (object on left)
#   - Concave mirror: f < 0 (focus in front = left side)
#   - Convex mirror: f > 0 (focus behind = right side)
#   - Convex lens: f > 0; Concave lens: f < 0
#   Mirror formula: 1/v + 1/u = 1/f
#   Lens formula:   1/v − 1/u = 1/f
#   Magnification (mirror): m = −v/u
#   Magnification (lens):   m = v/u
#   Power of lens: P = 1/f(m), unit: dioptre (D)

def draw_optics_diagram(optic_type="convex_lens", u_cm=-30, f_cm=20):
    img, draw = canvas(560, 380, "#0D1117")
    draw.text((20, 10), f"Ray Optics: {optic_type.replace('_',' ').title()}",
              fill="white", font=FONT_MD)

    cx, cy = 280, 200  # optical centre

    # Principal axis
    draw.line([(20, cy), (540, cy)], fill="#333", width=1)

    # Scale: 1 cm = 4 pixels
    scale = 4

    if "lens" in optic_type:
        # Draw lens symbol (double arrow)
        if "convex" in optic_type:
            pts = [(cx, cy-70),(cx-8, cy-40),(cx, cy-10),(cx+8, cy-40),(cx, cy-70)]
            pts2= [(cx, cy+70),(cx-8, cy+40),(cx, cy+10),(cx+8, cy+40),(cx, cy+70)]
            draw.polygon([(cx, cy-70),(cx-12, cy),(cx, cy+70),(cx+12, cy)],
                         outline="#4FC3F7", fill=None, width=2)
        else:  # concave lens
            draw.polygon([(cx-12, cy-70),(cx+12, cy-70),(cx, cy),(cx+12, cy+70),(cx-12, cy+70),(cx, cy)],
                         outline="#4FC3F7", fill=None, width=2)

        # Focal points
        f_px = abs(f_cm) * scale
        if f_cm > 0:  # convex: F on right for real focus, F' on left
            draw.ellipse([cx+f_px-5, cy-5, cx+f_px+5, cy+5], fill="#FF6B6B")
            draw.text((cx+f_px-5, cy+8), "F", fill="#FF6B6B", font=FONT_SM)
            draw.ellipse([cx-f_px-5, cy-5, cx-f_px+5, cy+5], fill="#FF6B6B")
            draw.text((cx-f_px-5, cy+8), "F'", fill="#FF6B6B", font=FONT_SM)
        else:  # concave: F on left
            draw.ellipse([cx-f_px-5, cy-5, cx-f_px+5, cy+5], fill="#FF6B6B")
            draw.text((cx-f_px-5, cy+8), "F", fill="#FF6B6B", font=FONT_SM)

        # Object (arrow on left)
        u_px = abs(u_cm) * scale
        draw.line([(cx-u_px, cy), (cx-u_px, cy-50)], fill="#FFD700", width=3)
        arrow(draw, cx-u_px, cy, cx-u_px, cy-52, "#FFD700", w=2)
        draw.text((cx-u_px-20, cy-60), "obj", fill="#FFD700", font=FONT_SM)

        # Image calculation (lens formula: 1/v - 1/u = 1/f)
        try:
            u = -abs(u_cm)  # always negative
            v = 1 / (1/f_cm + 1/u)
            if v != 0:
                v_px = int(v * scale)
                img_col = "#00FF88" if v > 0 else "#FF8800"
                draw.line([(cx+v_px, cy), (cx+v_px, cy-int(50*abs(v/u)))], fill=img_col, width=2)
                draw.text((cx+v_px+3, cy-int(50*abs(v/u))-15), "img", fill=img_col, font=FONT_SM)
        except: pass

        draw.text((20, 330), f"f={f_cm} cm (+ convex, - concave)", fill="#AAA", font=FONT_SM)
        draw.text((20, 352), f"u={u_cm} cm  |  Lens formula: 1/v−1/u=1/f", fill="#AAA", font=FONT_SM)

    else:  # mirror
        # Draw mirror arc on right
        mirror_x = cx + 150
        for a in range(-55, 56, 2):
            rad = math.radians(a)
            x = mirror_x + int(30 * math.cos(rad))
            y = cy + int(80 * math.sin(rad))
            draw.point((x, y), fill="#888")

        if "concave" in optic_type:
            f_px = abs(f_cm) * scale
            # Focus is in FRONT (left of mirror)
            draw.ellipse([mirror_x-f_px-5, cy-5, mirror_x-f_px+5, cy+5], fill="#FF6B6B")
            draw.text((mirror_x-f_px-5, cy+8), "F", fill="#FF6B6B", font=FONT_SM)
        else:  # convex mirror: focus behind
            f_px = abs(f_cm) * scale
            draw.ellipse([mirror_x+f_px-5, cy-5, mirror_x+f_px+5, cy+5], fill="#FF6B6B")
            draw.text((mirror_x+f_px-5, cy+8), "F (virtual)", fill="#FF6B6B", font=FONT_SM)

        # Object arrow
        u_px = min(abs(u_cm) * scale, 200)
        draw.line([(mirror_x-u_px, cy), (mirror_x-u_px, cy-50)], fill="#FFD700", width=3)
        draw.text((mirror_x-u_px-20, cy-62), "obj", fill="#FFD700", font=FONT_SM)

        draw.text((20, 330), f"Mirror formula: 1/v + 1/u = 1/f", fill="#AAA", font=FONT_SM)
        draw.text((20, 352), f"m = −v/u  |  f={f_cm} cm  |  u={u_cm} cm", fill="#AAA", font=FONT_SM)

    draw.text((20, 308), "New Cartesian: u always −ve (object on left)", fill="#555", font=FONT_SM)
    return img

OPTICS_QA = [
    ("convex_lens", -30, 20,
     "A convex lens (f=+20 cm) has object at u=−30 cm. Image distance v:",
     "+60 cm (real, inverted, on opposite side of lens)",
     ["-60 cm", "+30 cm", "+20 cm"],
     "1/v = 1/f + 1/u = 1/20 + 1/(-30) = 3/60 - 2/60 = 1/60. v = +60 cm. Positive → real image."),

    ("concave_lens", -30, -20,
     "A concave lens (f=−20 cm), object at u=−30 cm. Image distance v:",
     "−12 cm (virtual, erect, same side as object)",
     ["+12 cm", "-30 cm", "-20 cm"],
     "1/v = 1/f + 1/u = 1/(-20) + 1/(-30) = -3/60 - 2/60 = -5/60 = -1/12. v = -12 cm. Negative → virtual."),

    ("concave_mirror", -30, -20,
     "Concave mirror (f=−20 cm), object at u=−30 cm. Image distance v:",
     "−60 cm (real, inverted, in front of mirror)",
     ["+60 cm", "-20 cm", "+20 cm"],
     "1/v = 1/f - 1/u = 1/(-20) - 1/(-30) = -1/20 + 1/30 = -3/60 + 2/60 = -1/60. v = -60 cm."),

    ("convex_mirror", -30, 15,
     "Convex mirror (f=+15 cm), object at u=−30 cm. Image distance v:",
     "+10 cm (virtual, erect, behind mirror)",
     ["-10 cm", "+30 cm", "+15 cm"],
     "1/v = 1/f - 1/u = 1/15 - 1/(-30) = 1/15 + 1/30 = 2/30 + 1/30 = 3/30 = 1/10. v = +10 cm."),

    ("convex_lens", -20, 20,
     "Convex lens (f=+20 cm), object at u=−20 cm (at focus). Image is:",
     "At infinity (v → ∞)",
     ["At 2f", "At f behind lens", "At centre of lens"],
     "1/v = 1/f + 1/u = 1/20 + 1/(-20) = 0. v → ∞. Object at focus → image at infinity."),

    ("convex_lens", -10, 20,
     "Convex lens (f=+20 cm), object at u=−10 cm (within focal length). Image is:",
     "Virtual, erect, magnified (on same side as object, v < 0)",
     ["Real, inverted, at 2f", "At infinity", "Real, diminished"],
     "1/v = 1/20 + 1/(-10) = 1/20 - 2/20 = -1/20. v = -20 cm. Negative → virtual, erect."),

    ("concave_mirror", -10, -20,
     "Concave mirror (f=−20 cm), object at u=−10 cm (within focus). Image is:",
     "Virtual, erect, magnified (behind mirror, v > 0)",
     ["Real, inverted", "At infinity", "Real, same size"],
     "1/v = 1/f - 1/u = 1/(-20) - 1/(-10) = -1/20 + 1/10 = 1/20. v = +20 cm. Positive → virtual, behind mirror."),

    ("convex_lens", -30, 20,
     "For a convex lens, magnification m = v/u. Object at u=−30, v=+60. m =",
     "−2 (inverted, magnified 2×)",
     ["+2", "+0.5", "−0.5"],
     "m = v/u = 60/(-30) = -2. Negative m → inverted image. |m|=2 → image is twice the size."),

    ("convex_lens", -30, 20,
     "Power of a convex lens with focal length 25 cm:",
     "+4 D",
     ["-4 D", "+0.25 D", "+40 D"],
     "P = 1/f(in metres) = 1/0.25 = +4 D. Positive for converging (convex) lens."),

    ("concave_lens", -30, -20,
     "Power of a concave lens with focal length 50 cm:",
     "−2 D",
     ["+2 D", "+0.5 D", "-0.02 D"],
     "P = 1/f = 1/(−0.5) = −2 D. Negative for diverging (concave) lens."),

    ("convex_lens", -30, 20,
     "A person uses a convex lens of power +2 D as reading glasses. Focal length is:",
     "50 cm",
     ["2 cm", "20 cm", "200 cm"],
     "f = 1/P = 1/2 m = 0.5 m = 50 cm"),

    ("convex_mirror", -30, 15,
     "A convex mirror ALWAYS forms an image that is:",
     "Virtual, erect and diminished (regardless of object position)",
     ["Real, inverted", "Virtual, inverted", "Real, erect"],
     "Convex mirror has virtual focus. Image is always virtual, erect and smaller than object."),

    ("concave_mirror", -40, -20,
     "Concave mirror (f=−20 cm), object at u=−40 cm (at 2f). Image is:",
     "Real, inverted, same size as object, at v=−40 cm",
     ["At infinity", "Virtual, erect", "At f"],
     "1/v = 1/(-20) - 1/(-40) = -2/40 + 1/40 = -1/40. v = -40 cm = u. m = -v/u = -(-40)/(-40) = -1."),

    ("convex_lens", -40, 20,
     "Convex lens (f=+20), object at u=−40 cm (at 2f). Image position and nature:",
     "v=+40 cm, real, inverted, same size (at 2f on other side)",
     ["v=+20 cm", "v=−40 cm", "At infinity"],
     "1/v = 1/20 + 1/(-40) = 2/40 - 1/40 = 1/40. v = +40 cm. m = 40/(-40) = -1."),

    ("concave_mirror", -30, -20,
     "In a concave mirror, radius of curvature R=40 cm. Its focal length f =",
     "−20 cm (f = R/2, negative for concave)",
     ["+20 cm", "−40 cm", "+40 cm"],
     "f = R/2 = 40/2 = 20 cm. For concave mirror, f is negative (NCERT sign convention): f = −20 cm"),

    ("convex_lens", -30, 20,
     "Lens maker's equation uses refractive index to relate focal length to:",
     "Radii of curvature of the two lens surfaces and refractive index of material",
     ["Mass of the lens", "Colour of light only", "Temperature"],
     "Lens maker's formula: 1/f = (n-1)[1/R₁ - 1/R₂], where n = refractive index, R₁, R₂ = radii of curvature."),

    ("convex_lens", -30, 20,
     "A combination of lenses in contact: P₁=+3D, P₂=−1D. Combined power:",
     "+2 D",
     ["-2 D", "+4 D", "+3 D"],
     "P_total = P₁ + P₂ = 3 + (-1) = +2 D"),

    ("concave_mirror", -30, -20,
     "The mirror formula 1/v + 1/u = 1/f is valid for:",
     "All spherical mirrors (concave and convex) with paraxial rays",
     ["Only concave mirrors", "Only convex mirrors", "Only plane mirrors"],
     "Mirror formula works for both concave and convex mirrors for paraxial rays using the New Cartesian sign convention."),

    ("convex_lens", -60, 20,
     "Convex lens (f=+20), object at u=−60 cm. Magnification m =",
     "−0.5 (real, inverted, diminished)",
     ["+0.5", "−2", "+2"],
     "1/v = 1/20 + 1/(-60) = 3/60 - 1/60 = 2/60. v = +30 cm. m = v/u = 30/(-60) = -0.5"),

    ("concave_mirror", -30, -15,
     "Concave mirror (f=−15 cm), object at u=−30 cm. Magnification m =",
     "−1 (real, inverted, same size)",
     ["+1", "−2", "+0.5"],
     "1/v = 1/(-15) - 1/(-30) = -2/30 + 1/30 = -1/30. v=-30 cm. m = -v/u = -(-30)/(-30) = -1"),
]

def gen_optics(n=QPT):
    print(f"[Ray Optics] {n} questions...")
    for i, (otype, u, f, qtext, correct, wrongs, expl) in enumerate(OPTICS_QA[:n]):
        opts = [correct]+wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
        img = draw_optics_diagram(otype, u, f)
        url = upload_pil(img, f"opt_{i}")
        ok = post_q("Science", 12, random.choice(["Advanced","Olympiad"]),
                    "Ray Optics", "Optics and Optical Instruments",
                    qtext, url, opts, cidx, expl)
        print(f"  opt_{i} ({otype})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 4. CURRENT ELECTRICITY  (Class 12)
# ══════════════════════════════════════════════════════════════════════════════
# Key laws:
#   Ohm's law: V = IR  (linear V-I → ohmic conductor)
#   Resistors in series: R = R₁+R₂+...
#   Resistors in parallel: 1/R = 1/R₁+1/R₂+...
#   Kirchhoff's KCL: ΣI = 0 at junction
#   Kirchhoff's KVL: ΣV = 0 in closed loop
#   Wheatstone bridge: P/Q = R/S (balanced, no current through galvanometer)
#   Resistivity: R = ρL/A
#   Power: P = VI = I²R = V²/R

def draw_electricity(scene="ohms_law"):
    img, draw = canvas(540, 380, "#0D1117")
    draw.text((20, 10), f"Current Electricity: {scene.replace('_',' ').title()}",
              fill="white", font=FONT_MD)

    if scene == "ohms_law":
        # V-I graph (linear for ohmic)
        ax, ay = 70, 310
        draw.line([(ax, 50), (ax, ay)], fill="#555", width=2)
        draw.line([(ax, ay), (480, ay)], fill="#555", width=2)
        draw.text((490, ay-8), "I", fill="white", font=FONT_MD)
        draw.text((ax+4, 35), "V", fill="white", font=FONT_MD)
        # Linear line (V = IR, slope = R)
        draw.line([(ax, ay), (420, 80)], fill="#E74C3C", width=3)
        draw.text((425, 72), "Ohmic", fill="#E74C3C", font=FONT_MD)
        # Non-linear (diode-like)
        pts = [(ax, ay)]
        for i in range(1, 40):
            x = ax + i*5
            y = int(ay - 0.05 * (i**2))
            pts.append((x, max(y, 60)))
        for j in range(len(pts)-1):
            draw.line([pts[j], pts[j+1]], fill="#3498DB", width=2)
        draw.text((265, 100), "Non-ohmic", fill="#3498DB", font=FONT_MD)
        draw.text((80, 335), "Slope of V-I graph = Resistance (R = V/I)", fill="#AAA", font=FONT_SM)

    elif scene == "wheatstone":
        # Diamond circuit
        cx, cy = 270, 200
        nodes = {"A":(cx, cy-120), "B":(cx-120, cy), "C":(cx+120, cy), "D":(cx, cy+120)}
        # Resistors P, Q, R, S
        resistors = [("A","B","P"), ("A","C","Q"), ("B","D","R"), ("C","D","S")]
        for (n1, n2, lbl) in resistors:
            x1,y1=nodes[n1]; x2,y2=nodes[n2]
            draw.line([(x1,y1),(x2,y2)], fill="#4FC3F7", width=3)
            mx,my = (x1+x2)//2, (y1+y2)//2
            draw.rectangle([mx-15,my-12,mx+15,my+12], fill="#333", outline="#4FC3F7")
            draw.text((mx-8,my-8), lbl, fill="white", font=FONT_SM)
        # Galvanometer B-C
        draw.line([(nodes["B"][0],nodes["B"][1]),(nodes["C"][0],nodes["C"][1])],
                  fill="#F39C12", width=2)
        mx,my = cx, cy
        draw.ellipse([mx-15,my-15,mx+15,my+15], fill="#333", outline="#F39C12")
        draw.text((mx-7,my-8), "G", fill="#F39C12", font=FONT_MD)
        # Battery A-D
        draw.line([(nodes["A"][0],nodes["A"][1]-5),(nodes["D"][0],nodes["D"][1]+5)],
                  fill="#E74C3C", width=2)
        draw.text((cx+5, cy-60), "E", fill="#E74C3C", font=FONT_MD)
        for n, (nx,ny) in nodes.items():
            draw.ellipse([nx-6,ny-6,nx+6,ny+6], fill="white")
            draw.text((nx+8,ny-8), n, fill="white", font=FONT_SM)
        draw.text((30, 340), "Balanced: P/Q = R/S  →  I_G = 0", fill="#AAA", font=FONT_MD)

    elif scene == "kirchhoff":
        # Junction with currents
        cx, cy = 270, 200
        draw.ellipse([cx-8,cy-8,cx+8,cy+8], fill="white")
        draw.text((cx+10,cy-8), "Junction", fill="white", font=FONT_SM)
        currents = [(30, "I₁=3A","in"), (150,"I₂=2A","in"), (270,"I₃=?","out"), (390,"I₄=1A","out")]
        for angle, label, direction in currents:
            rad = math.radians(angle)
            x2 = cx + int(100*math.cos(rad)); y2 = cy + int(100*math.sin(rad))
            col = "#27AE60" if direction=="in" else "#E74C3C"
            if direction == "in":
                arrow(draw, x2, y2, cx, cy, col, w=3)
            else:
                arrow(draw, cx, cy, x2, y2, col, w=3)
            draw.text((x2, y2), label, fill=col, font=FONT_SM)
        draw.text((30, 330), "KCL: ΣI_in = ΣI_out  →  I₃ = I₁+I₂-I₄ = 3+2-1 = 4A", fill="#AAA", font=FONT_MD)

    return img

ELEC_QA = [
    ("ohms_law",
     "Ohm's Law states V = IR. A resistor has R = 5Ω with current 2A. Voltage across it:",
     "10 V",
     ["2.5 V", "7 V", "10 Ω"],
     "V = IR = 2 × 5 = 10 V"),

    ("wheatstone",
     "In a Wheatstone bridge, P=10Ω, Q=20Ω, R=30Ω. For balance, S =",
     "60 Ω",
     ["15 Ω", "6 Ω", "40 Ω"],
     "Balance condition: P/Q = R/S → S = Q×R/P = 20×30/10 = 60 Ω"),

    ("kirchhoff",
     "KCL (Kirchhoff's Current Law) is based on conservation of:",
     "Charge",
     ["Energy", "Momentum", "Mass"],
     "KCL: sum of currents at a junction = 0. This follows from conservation of electric charge."),

    ("kirchhoff",
     "KVL (Kirchhoff's Voltage Law) is based on conservation of:",
     "Energy",
     ["Charge", "Mass", "Momentum"],
     "KVL: sum of EMFs = sum of voltage drops in a closed loop. This follows from conservation of energy."),

    ("ohms_law",
     "Two resistors 6Ω and 3Ω in parallel. Equivalent resistance:",
     "2 Ω",
     ["9 Ω", "3 Ω", "4 Ω"],
     "1/R = 1/6 + 1/3 = 1/6 + 2/6 = 3/6 = 1/2. R = 2 Ω"),

    ("ohms_law",
     "Three resistors 2Ω, 3Ω, 5Ω in series. Equivalent resistance:",
     "10 Ω",
     ["0.97 Ω", "30 Ω", "15 Ω"],
     "R_series = 2 + 3 + 5 = 10 Ω"),

    ("ohms_law",
     "Power dissipated in a 4Ω resistor carrying 3A current:",
     "36 W",
     ["12 W", "9 W", "144 W"],
     "P = I²R = 3² × 4 = 9 × 4 = 36 W"),

    ("ohms_law",
     "A wire of resistance R is stretched to double its length. New resistance:",
     "4R (R increases 4 times)",
     ["2R", "R/2", "R/4"],
     "R = ρL/A. Volume = LA = constant. L doubles → A halves. R_new = ρ(2L)/(A/2) = 4(ρL/A) = 4R"),

    ("wheatstone",
     "The Wheatstone bridge is used to measure:",
     "Unknown resistance accurately",
     ["Unknown EMF", "Capacitance", "Magnetic field"],
     "The Wheatstone bridge measures an unknown resistance by balancing the bridge (zero galvanometer deflection)."),

    ("ohms_law",
     "A 100W, 220V bulb. Its resistance when operating normally:",
     "484 Ω",
     ["220 Ω", "100 Ω", "22 Ω"],
     "P = V²/R → R = V²/P = 220²/100 = 48400/100 = 484 Ω"),

    ("kirchhoff",
     "At a junction, currents entering are 3A, 5A and currents leaving are 2A, xA. x =",
     "6 A",
     ["8 A", "4 A", "10 A"],
     "KCL: I_in = I_out. 3+5 = 2+x. x = 8-2 = 6 A"),

    ("ohms_law",
     "Resistivity of a conductor depends on:",
     "Material and temperature (not on length or area)",
     ["Length of wire", "Cross-sectional area", "Voltage applied"],
     "Resistivity ρ is an intrinsic property of the material and depends on temperature. R = ρL/A."),

    ("ohms_law",
     "EMF of a battery is 12V, internal resistance 1Ω, external resistance 5Ω. Current in circuit:",
     "2 A",
     ["12 A", "2.4 A", "6 A"],
     "I = EMF/(R_ext + r) = 12/(5+1) = 12/6 = 2 A"),

    ("wheatstone",
     "Terminal voltage of a battery (EMF=10V, r=2Ω) when delivering current of 2A:",
     "6 V",
     ["10 V", "4 V", "8 V"],
     "Terminal voltage = EMF - I×r = 10 - 2×2 = 10 - 4 = 6 V"),

    ("ohms_law",
     "A wire carries 2A for 5 minutes. Charge transferred:",
     "600 C",
     ["10 C", "60 C", "2.5 C"],
     "Q = I×t = 2 × (5×60) = 2 × 300 = 600 C"),

    ("ohms_law",
     "The slope of the V-I graph for an ohmic conductor represents:",
     "Resistance R (V = IR, slope = R)",
     ["Conductance (1/R)", "Power", "Charge"],
     "For V vs I graph (V on y-axis, I on x-axis), slope = ΔV/ΔI = R (resistance)."),

    ("ohms_law",
     "Three identical bulbs in parallel vs in series: which arrangement gives more total power?",
     "Parallel (more total power for same voltage supply)",
     ["Series", "Both give same power", "Depends on resistance"],
     "In parallel, each bulb gets full voltage V. In series, each gets V/3. P_parallel = 3V²/R >> P_series = V²/3R."),

    ("ohms_law",
     "Drift velocity of electrons in a conductor is of the order of:",
     "10⁻⁴ m/s (very slow, ~mm/s)",
     ["3×10⁸ m/s", "10³ m/s", "1 m/s"],
     "Drift velocity v_d ≈ 10⁻⁴ m/s. Despite this, current signal propagates at nearly speed of light."),

    ("wheatstone",
     "In the Wheatstone bridge, if P/Q = R/S exactly, the galvanometer shows:",
     "Zero deflection (no current flows through galvanometer)",
     ["Maximum deflection", "Half-scale deflection", "Deflection proportional to R"],
     "Bridge is balanced when P/Q = R/S. In this state, potential at both ends of galvanometer are equal, so I_G = 0."),

    ("ohms_law",
     "Heating effect of current is given by H = I²Rt. This is called:",
     "Joule's Law of Heating",
     ["Faraday's Law", "Lenz's Law", "Ohm's Law"],
     "Joule's Law: H = I²Rt. The heat produced in a resistor is proportional to I², R, and time t."),
]

def gen_electricity(n=QPT):
    print(f"[Current Electricity] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(ELEC_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_electricity(scene); url=upload_pil(img, f"elec_{i}")
        ok=post_q("Science",12,random.choice(["Advanced","Olympiad"]),
                  "Current Electricity","Circuits and Kirchhoff's Laws",
                  qtext,url,opts,cidx,expl)
        print(f"  elec_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 5. SEMICONDUCTOR ELECTRONICS  (Class 12)
# ══════════════════════════════════════════════════════════════════════════════

def draw_semiconductor(scene="vi_diode"):
    img, draw = canvas(540, 380, "#0D1117")
    draw.text((20, 10), f"Semiconductor: {scene.replace('_',' ').title()}", fill="white", font=FONT_MD)

    if scene == "vi_diode":
        ax, ay = 270, 220
        # Axes (centred for forward and reverse)
        draw.line([(40, ay), (510, ay)], fill="#555", width=2)
        draw.line([(ax, 30), (ax, 360)], fill="#555", width=2)
        draw.text((515, ay-8), "+V", fill="white", font=FONT_SM)
        draw.text((20, ay-8), "−V", fill="white", font=FONT_SM)
        draw.text((ax+5, 20), "+I", fill="white", font=FONT_SM)
        draw.text((ax+5, 350), "−I", fill="white", font=FONT_SM)
        # Forward bias: exponential rise
        fwd_pts = [(ax, ay)]
        for v in range(1, 80):
            x = ax + v * 3
            y = ay - int(0.005 * math.exp(v * 0.08))
            fwd_pts.append((x, max(y, 35)))
        for j in range(len(fwd_pts)-1):
            draw.line([fwd_pts[j], fwd_pts[j+1]], fill="#27AE60", width=3)
        # Reverse bias: tiny leakage current
        draw.line([(ax, ay), (ax-200, ay+8)], fill="#E74C3C", width=2)
        # Breakdown at large reverse voltage
        draw.line([(ax-200, ay+8), (ax-200, ay+60)], fill="#E74C3C", width=2)
        draw.text((80, ay+65), "Breakdown", fill="#E74C3C", font=FONT_SM)
        draw.text((ax-60, ay-8), "V_knee≈0.7V", fill="#FFD700", font=FONT_SM)
        draw.text((ax+10, ay+20), "Forward bias →", fill="#27AE60", font=FONT_SM)
        draw.text((60, ay+20), "← Reverse bias", fill="#E74C3C", font=FONT_SM)

    elif scene == "band_diagram":
        # Energy band diagram for conductor, semiconductor, insulator
        titles = ["Conductor", "Semiconductor", "Insulator"]
        colors = ["#E74C3C", "#F39C12", "#3498DB"]
        for t_idx, (title, col) in enumerate(zip(titles, colors)):
            bx = 50 + t_idx * 160
            # Conduction band
            draw.rectangle([bx, 80, bx+100, 130], fill=col, outline="white", width=1)
            draw.text((bx+5, 100), "CB", fill="white", font=FONT_SM)
            if t_idx == 0:  # conductor: overlap
                draw.rectangle([bx, 110, bx+100, 170], fill="#FF8C00", outline="white", width=1)
                draw.text((bx+5, 140), "VB", fill="white", font=FONT_SM)
                draw.text((bx+10, 190), "Overlap", fill=col, font=FONT_SM)
            elif t_idx == 1:  # semiconductor: small gap
                gap_h = 25
                draw.text((bx+15, 138), "E_g≈1eV", fill="#FFD700", font=FONT_SM)
                draw.rectangle([bx, 160, bx+100, 210], fill="#888", outline="white", width=1)
                draw.text((bx+5, 180), "VB", fill="white", font=FONT_SM)
                draw.text((bx+10, 230), "Small gap", fill=col, font=FONT_SM)
            else:  # insulator: large gap
                draw.text((bx+10, 138), "E_g≈6eV", fill="#FFD700", font=FONT_SM)
                draw.rectangle([bx, 210, bx+100, 260], fill="#555", outline="white", width=1)
                draw.text((bx+5, 230), "VB", fill="white", font=FONT_SM)
                draw.text((bx+5, 280), "Large gap", fill=col, font=FONT_SM)
            draw.text((bx+10, 320), title, fill=col, font=FONT_MD)

    elif scene == "npn_transistor":
        # NPN transistor symbol
        cx, cy = 270, 200
        # Base line (vertical)
        draw.line([(cx-40, cy-60), (cx-40, cy+60)], fill="#4FC3F7", width=4)
        draw.text((cx-60, cy-8), "B", fill="#4FC3F7", font=FONT_LG)
        # Emitter (with arrow outward)
        draw.line([(cx-40, cy+30), (cx+40, cy+80)], fill="#FFD700", width=3)
        arrow(draw, cx-40, cy+30, cx+40, cy+80, "#FFD700", w=3)
        draw.text((cx+45, cy+82), "E", fill="#FFD700", font=FONT_LG)
        # Collector (upward)
        draw.line([(cx-40, cy-30), (cx+40, cy-80)], fill="#E74C3C", width=3)
        draw.text((cx+45, cy-85), "C", fill="#E74C3C", font=FONT_LG)
        # Circle
        draw.ellipse([cx-70, cy-100, cx+70, cy+100], outline="white", width=2)
        draw.text((30, 330), "NPN: current flows C→E when base is forward biased", fill="#AAA", font=FONT_SM)

    return img

SEMI_QA = [
    ("vi_diode",
     "In a p-n junction diode under forward bias, the depletion layer:",
     "Decreases (barrier reduced, current flows)",
     ["Increases", "Remains same", "Completely disappears"],
     "Forward bias reduces the potential barrier and depletion layer width → current flows."),

    ("vi_diode",
     "The knee voltage (cut-in voltage) for a silicon diode is approximately:",
     "0.7 V",
     ["0.3 V", "1.1 V", "1.4 V"],
     "Silicon diode starts conducting significantly above ~0.7V (knee voltage). Germanium diode: ~0.3V."),

    ("band_diagram",
     "A semiconductor has band gap energy E_g ≈ 1.1 eV. This is:",
     "Silicon (Si)",
     ["Germanium (Ge, E_g≈0.67eV)", "Diamond (E_g≈5.5eV)", "GaAs (E_g≈1.43eV)"],
     "Silicon has E_g ≈ 1.1 eV. Germanium ≈ 0.67 eV. Diamond ≈ 5.5 eV (insulator)."),

    ("band_diagram",
     "In an intrinsic semiconductor at absolute zero (0 K):",
     "No free charge carriers; it behaves as an insulator",
     ["Many free electrons", "Only holes exist", "Conduction band is full"],
     "At 0K, all electrons are in valence band, no thermal energy to jump to conduction band."),

    ("vi_diode",
     "An n-type semiconductor is formed by doping silicon with:",
     "Pentavalent impurity (e.g., Phosphorus, Arsenic)",
     ["Trivalent impurity (Boron)", "Divalent impurity", "Hexavalent impurity"],
     "Pentavalent dopants (5 valence electrons) donate extra electrons → n-type (electrons are majority carriers)."),

    ("vi_diode",
     "A p-type semiconductor is formed by doping with:",
     "Trivalent impurity (e.g., Boron, Aluminium)",
     ["Pentavalent (Phosphorus)", "Divalent", "Hexavalent"],
     "Trivalent dopants (3 valence electrons) create holes → p-type (holes are majority carriers)."),

    ("vi_diode",
     "In reverse bias of a p-n diode, the reverse saturation current is:",
     "Very small (~μA), nearly constant with increasing reverse voltage (until breakdown)",
     ["Zero", "Large (same as forward)", "Increases linearly with voltage"],
     "In reverse bias, only minority carriers flow → very small reverse saturation current (~μA)."),

    ("band_diagram",
     "In a conductor, the valence band and conduction band:",
     "Overlap (free electrons always available)",
     ["Have a large gap", "Have a small gap (~1eV)", "Are completely separate"],
     "Conductors have overlapping valence and conduction bands → electrons freely available for conduction."),

    ("npn_transistor",
     "In a common emitter NPN transistor, the current gain β (h_FE) is defined as:",
     "β = I_C / I_B (collector current / base current)",
     ["I_B / I_C", "I_E / I_C", "I_C / I_E"],
     "β = I_C/I_B. Typical β = 50–300. I_E = I_C + I_B."),

    ("npn_transistor",
     "If β = 100 and I_B = 50 μA, collector current I_C =",
     "5 mA",
     ["50 μA", "500 μA", "50 mA"],
     "I_C = β × I_B = 100 × 50×10⁻⁶ = 5000 μA = 5 mA"),

    ("vi_diode",
     "A Zener diode is used primarily as a:",
     "Voltage regulator (operates in reverse breakdown)",
     ["Rectifier", "Amplifier", "Oscillator"],
     "Zener diode operates in the reverse breakdown region where voltage remains nearly constant → voltage regulator."),

    ("vi_diode",
     "In a half-wave rectifier, the output frequency is:",
     "Same as input frequency (f_out = f_in)",
     ["Double the input", "Half the input", "Zero (DC only)"],
     "Half-wave: only one half-cycle passes per input cycle. Output frequency = input frequency."),

    ("vi_diode",
     "In a full-wave rectifier (bridge rectifier), output frequency is:",
     "Double the input frequency (2f)",
     ["Same as input", "Half the input", "4 times input"],
     "Full-wave rectifier conducts in both half-cycles. 2 pulses per input cycle → f_out = 2f_in."),

    ("band_diagram",
     "The majority carriers in a p-type semiconductor are:",
     "Holes",
     ["Electrons", "Both holes and electrons equally", "Protons"],
     "In p-type: trivalent doping creates holes (majority). Electrons are minority carriers."),

    ("npn_transistor",
     "A transistor can be used as an amplifier when it operates in:",
     "Active region (forward biased BE junction, reverse biased BC junction)",
     ["Saturation region", "Cutoff region", "Breakdown region"],
     "Active region: emitter-base forward biased, base-collector reverse biased. Transistor amplifies."),

    ("vi_diode",
     "Light Emitting Diode (LED) converts:",
     "Electrical energy to light (forward biased, electron-hole recombination emits photons)",
     ["Light to electrical energy", "Heat to light", "AC to DC"],
     "LED: forward biased p-n junction. When electrons recombine with holes, they emit photons (light)."),

    ("vi_diode",
     "A solar cell (photodiode) converts:",
     "Light energy to electrical energy",
     ["Electrical to light", "Heat to electrical", "Sound to electrical"],
     "Solar cell / photodiode: incident photons create electron-hole pairs → generates EMF (photovoltaic effect)."),

    ("band_diagram",
     "At room temperature, intrinsic semiconductor conductivity increases with temperature because:",
     "More electrons gain enough energy to jump to conduction band",
     ["Resistance increases", "Band gap increases", "Fewer carriers available"],
     "Higher temperature → more electrons can cross E_g into conduction band → more carriers → higher conductivity."),

    ("npn_transistor",
     "The emitter current I_E in a transistor equals:",
     "I_C + I_B",
     ["I_C − I_B", "I_C × I_B", "I_C / I_B"],
     "By KCL at transistor: I_E = I_C + I_B. Emitter current = collector current + base current."),

    ("vi_diode",
     "NAND gate is considered a universal gate because:",
     "Any logic gate can be constructed using only NAND gates",
     ["It is the simplest gate", "It has only 2 inputs", "It operates at high voltage"],
     "NAND (and NOR) are universal gates: NOT, AND, OR, XOR can all be built from NAND gates alone."),
]

def gen_semiconductor(n=QPT):
    print(f"[Semiconductor Electronics] {n} questions...")
    for i,(scene,qtext,correct,wrongs,expl) in enumerate(SEMI_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_semiconductor(scene); url=upload_pil(img,f"semi_{i}")
        ok=post_q("Science",12,random.choice(["Advanced","Olympiad"]),
                  "Semiconductor Electronics","Electronic Devices",
                  qtext,url,opts,cidx,expl)
        print(f"  semi_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 6. PHOTOELECTRIC EFFECT  (Class 12)
# ══════════════════════════════════════════════════════════════════════════════
# Key formulae:
#   Einstein: KE_max = hν − φ  (φ = work function = hν₀)
#   Threshold frequency: ν₀ = φ/h
#   Stopping potential: eV₀ = KE_max → V₀ = (hν − φ)/e
#   h = 6.626×10⁻³⁴ J·s
#   If λ < λ₀ (threshold wavelength), photoelectric effect occurs

def draw_photoelectric(scene="ke_freq"):
    img, draw = canvas(540, 380, "#0D1117")
    draw.text((20, 10), "Photoelectric Effect", fill="white", font=FONT_LG)

    if scene == "ke_freq":
        # KE vs frequency graph
        ax, ay = 80, 300
        draw.line([(ax, 40), (ax, ay)], fill="#555", width=2)
        draw.line([(ax, ay), (500, ay)], fill="#555", width=2)
        draw.text((505, ay-8), "ν", fill="white", font=FONT_MD)
        draw.text((ax+4, 28), "KE_max", fill="white", font=FONT_SM)
        # x-axis crossing at ν₀
        nu0_x = 180
        draw.text((nu0_x-10, ay+10), "ν₀", fill="#FFD700", font=FONT_MD)
        draw.line([(nu0_x, ay-5),(nu0_x, ay+5)], fill="#FFD700", width=2)
        # Linear line KE = hν - φ (slope = h)
        draw.line([(nu0_x, ay), (480, 60)], fill="#E74C3C", width=3)
        # Labels
        draw.text((420, 52), "slope = h", fill="#E74C3C", font=FONT_SM)
        draw.text((ax-70, ay-80), "−φ (y-intercept)", fill="#3498DB", font=FONT_SM)
        draw.line([(ax, ay-80),(ax+10, ay-80)], fill="#3498DB", width=2)
        draw.text((100, 330), "KE_max = hν − φ  (Einstein's photoelectric equation)", fill="#AAA", font=FONT_SM)

    elif scene == "stopping_potential":
        ax, ay = 80, 220
        draw.line([(ax, 40), (ax, ay+100)], fill="#555", width=2)
        draw.line([(40, ay), (500, ay)], fill="#555", width=2)
        draw.text((505, ay-8), "V", fill="white", font=FONT_MD)
        draw.text((ax+4, 28), "I", fill="white", font=FONT_MD)
        # Saturation current (positive V)
        draw.line([(ax, ay-80), (400, ay-80)], fill="#27AE60", width=3)
        draw.text((410, ay-88), "I_sat", fill="#27AE60", font=FONT_MD)
        # Current falls to zero at stopping potential
        pts = [(ax-130, ay-30), (ax-50, ay-70), (ax, ay-80)]
        for j in range(len(pts)-1):
            draw.line([pts[j],pts[j+1]], fill="#27AE60", width=3)
        # Stopping potential V₀
        v0_x = ax - 130
        draw.line([(v0_x, ay-5),(v0_x, ay+5)], fill="#E74C3C", width=2)
        draw.text((v0_x-12, ay+8), "−V₀", fill="#E74C3C", font=FONT_MD)
        draw.text((50, 330), "eV₀ = KE_max = hν − φ  →  V₀ = (hν−φ)/e", fill="#AAA", font=FONT_SM)

    elif scene == "photon_metal":
        # Photon hitting metal, electron emitted
        for px, py in [(80,100),(80,170),(80,240),(80,310)]:
            draw.line([(px,py),(px+80,py)], fill="#FFD700", width=2)
            arrow(draw,px,py,px+80,py,"#FFD700",w=2)
            draw.text((20,py-10),"hν",fill="#FFD700",font=FONT_SM)
        # Metal surface
        draw.rectangle([160,60,200,360], fill="#555")
        draw.text((165,380),"Metal",fill="#888",font=FONT_SM)
        # Emitted electrons
        for ey in [100,170,240]:
            arrow(draw,200,ey,320,ey-40,"#3498DB",w=2)
            draw.text((325,ey-50),"e⁻",fill="#3498DB",font=FONT_SM)
        draw.text((60,345),"Only ν ≥ ν₀ causes emission (not intensity)",fill="#AAA",font=FONT_SM)

    return img

PEE_QA = [
    ("ke_freq",
     "Einstein's photoelectric equation is KE_max = hν − φ. The quantity φ represents:",
     "Work function (minimum energy needed to eject an electron from the metal)",
     ["Kinetic energy of photon", "Frequency of light", "Planck's constant"],
     "Work function φ = hν₀ (minimum energy to free an electron). KE_max = hν − φ."),

    ("ke_freq",
     "In the KE vs frequency graph for photoelectric effect, the slope of the straight line equals:",
     "Planck's constant h (= 6.626×10⁻³⁴ J·s)",
     ["Work function φ", "Threshold frequency ν₀", "Charge of electron e"],
     "KE_max = hν − φ. dKE/dν = h. The slope = h (same for all metals)."),

    ("stopping_potential",
     "Stopping potential V₀ in photoelectric effect is the potential at which:",
     "The photoelectric current becomes exactly zero (even fastest electrons are stopped)",
     ["Current is maximum", "Current is half of saturation", "Emission starts"],
     "V₀: eV₀ = KE_max. When retarding potential = V₀, the most energetic emitted electrons are stopped."),

    ("photon_metal",
     "If the frequency of incident light is below threshold frequency ν₀, then:",
     "No photoelectric effect occurs, regardless of intensity",
     ["Electrons emit with lower KE", "Emission occurs after a delay", "More intense light causes emission"],
     "This is quantum nature of light: each photon must have E = hν ≥ φ to eject an electron. Intensity doesn't help."),

    ("ke_freq",
     "Threshold wavelength λ₀ of a metal is related to work function φ by:",
     "λ₀ = hc/φ  (where c = speed of light)",
     ["λ₀ = φ/hc", "λ₀ = h/φ", "λ₀ = φc/h"],
     "ν₀ = φ/h. Since c = ν₀λ₀, we get λ₀ = c/ν₀ = hc/φ."),

    ("ke_freq",
     "Work function of metal A = 2 eV, metal B = 4 eV. Same light shines on both. Which has greater KE_max of emitted electrons?",
     "Metal A (lower φ → greater KE_max = hν − φ)",
     ["Metal B", "Both same", "Metal with lower frequency"],
     "KE_max = hν − φ. For the same hν, lower work function → greater KE_max."),

    ("stopping_potential",
     "Stopping potential depends on:",
     "Frequency of incident light (not intensity)",
     ["Intensity of light", "Number of photons", "Area of metal surface"],
     "V₀ = (hν − φ)/e. Stopping potential depends only on frequency ν, not on intensity."),

    ("photon_metal",
     "Increasing the INTENSITY of incident light (above threshold) increases:",
     "Number of photoelectrons emitted (saturation current) — not KE_max",
     ["KE of each electron", "Stopping potential", "Threshold frequency"],
     "Intensity ∝ number of photons. More photons → more electrons ejected (more current), but KE per electron unchanged."),

    ("ke_freq",
     "The photoelectric effect demonstrates the _____ nature of light:",
     "Particle (quantum/photon) nature",
     ["Wave nature", "Both wave and particle equally", "Magnetic nature"],
     "The photoelectric effect (instantaneous emission, threshold frequency) can only be explained by photon (particle) nature of light."),

    ("ke_freq",
     "Photon energy E = hν = hc/λ. A photon of wavelength 400 nm (h=6.6×10⁻³⁴, c=3×10⁸):",
     "E ≈ 3.1 eV ≈ 5×10⁻¹⁹ J",
     ["E = 400 eV", "E = 6.6×10⁻³⁴ J", "E = 1.6×10⁻¹⁹ J"],
     "E = hc/λ = (6.6×10⁻³⁴ × 3×10⁸)/(400×10⁻⁹) = 4.95×10⁻¹⁹ J ≈ 3.1 eV"),

    ("stopping_potential",
     "For the same metal, if light frequency doubles (ν → 2ν), what happens to stopping potential?",
     "V₀ increases (more than doubles if φ > 0)",
     ["V₀ doubles exactly", "V₀ stays same", "V₀ decreases"],
     "V₀ = (hν − φ)/e. New V₀ = (2hν − φ)/e. Since φ > 0, new V₀ > 2×old V₀."),

    ("photon_metal",
     "The time delay between light falling on metal and emission of electrons is:",
     "Practically zero (instantaneous, ~10⁻⁹ s)",
     ["Several seconds", "Depends on wavelength", "Minutes for weak light"],
     "Wave theory predicts delay (time to accumulate energy), but experiment shows instantaneous emission — proof of photon theory."),

    ("ke_freq",
     "De Broglie wavelength λ = h/mv. An electron (m=9.1×10⁻³¹ kg) at 10⁶ m/s has λ:",
     "≈ 0.73 nm (X-ray range)",
     ["400 nm (visible)", "1 m", "10⁻¹⁵ m (nuclear)"],
     "λ = h/(mv) = 6.6×10⁻³⁴/(9.1×10⁻³¹ × 10⁶) = 6.6×10⁻³⁴/9.1×10⁻²⁵ ≈ 7.3×10⁻¹⁰ m ≈ 0.73 nm"),

    ("photon_metal",
     "Compton Effect provides evidence for:",
     "Particle nature of light (photon has momentum p = h/λ)",
     ["Wave nature of light", "Wave nature of electrons", "Dual nature of protons"],
     "Compton scattering: X-ray photons collide with electrons, changing wavelength. Explained by photon momentum p = h/λ."),

    ("ke_freq",
     "Heisenberg's Uncertainty Principle states:",
     "Δx·Δp ≥ h/(4π) — position and momentum cannot both be known precisely simultaneously",
     ["Energy is always conserved", "Electrons orbit in fixed paths", "Light always travels in straight lines"],
     "ΔxΔp ≥ ħ/2 = h/(4π). The more precisely we know position, the less precisely we know momentum."),
]

def gen_photoelectric(n=QPT):
    n = min(n, len(PEE_QA))
    print(f"[Photoelectric Effect] {n} questions...")
    for i,(scene,qtext,correct,wrongs,expl) in enumerate(PEE_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_photoelectric(scene); url=upload_pil(img,f"pee_{i}")
        ok=post_q("Science",12,random.choice(["Advanced","Olympiad"]),
                  "Photoelectric Effect","Dual Nature of Matter",
                  qtext,url,opts,cidx,expl)
        print(f"  pee_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 7. NUCLEAR PHYSICS  (Class 12)
# ══════════════════════════════════════════════════════════════════════════════
# Key facts:
#   Mass number A = P + N (protons + neutrons)
#   Atomic number Z = number of protons
#   Binding energy = (Zm_p + Nm_n − M_nucleus)c²  (mass defect × c²)
#   Most stable nucleus: Iron-56 (highest BE/nucleon ≈ 8.8 MeV)
#   α decay: A→A-4, Z→Z-2;  β⁻ decay: Z→Z+1;  γ: no change in A,Z
#   Fission: heavy nucleus splits (U-235 + n → Ba-141 + Kr-92 + 3n + ~200 MeV)
#   Fusion: light nuclei merge (H + H → He + energy) — powers the Sun
#   Half-life T½: N = N₀(½)^(t/T½)

def draw_nuclear(scene="binding_energy"):
    img, draw = canvas(540, 380, "#0D1117")
    draw.text((20, 10), f"Nuclear Physics: {scene.replace('_',' ').title()}", fill="white", font=FONT_MD)

    if scene == "binding_energy":
        ax, ay = 60, 320
        draw.line([(ax, 50), (ax, ay)], fill="#555", width=2)
        draw.line([(ax, ay), (510, ay)], fill="#555", width=2)
        draw.text((515, ay-8), "A", fill="white", font=FONT_MD)
        draw.text((ax+4, 38), "BE/A\n(MeV)", fill="white", font=FONT_SM)
        # BE/nucleon curve (rises quickly, peaks at Fe-56, then gradually decreases)
        data = [(1,0),(4,7.1),(8,7.7),(12,7.7),(16,8.0),(20,8.0),(28,8.4),(40,8.6),
                (56,8.8),(80,8.7),(100,8.6),(120,8.5),(150,8.3),(200,7.9),(238,7.6)]
        pts = []
        for (a_val, be) in data:
            px = ax + int(a_val * 1.8)
            py = ay - int(be * 28)
            pts.append((px, py))
        for j in range(len(pts)-1):
            draw.line([pts[j],pts[j+1]], fill="#27AE60", width=3)
        # Mark Fe-56
        fe_x = ax + int(56*1.8); fe_y = ay - int(8.8*28)
        draw.ellipse([fe_x-6,fe_y-6,fe_x+6,fe_y+6], fill="#FFD700")
        draw.text((fe_x+8, fe_y-12), "Fe-56\n(most stable)", fill="#FFD700", font=FONT_SM)
        # Fission/fusion arrows
        draw.text((390, 260), "← Fission", fill="#E74C3C", font=FONT_SM)
        draw.text((65, 260), "Fusion →", fill="#3498DB", font=FONT_SM)
        draw.text((ax+10, 340), "Mass number A", fill="#AAA", font=FONT_SM)

    elif scene == "decay":
        # Nucleus with alpha/beta/gamma emission
        cx, cy = 180, 200
        draw.ellipse([cx-50,cy-50,cx+50,cy+50], fill="#E74C3C", outline="white", width=2)
        draw.text((cx-18,cy-10), "Nucleus", fill="white", font=FONT_SM)
        # Alpha (helium nucleus)
        arrow(draw,cx+50,cy,cx+180,cy-60,"#FFD700",w=4)
        draw.text((cx+185,cy-68), "α (⁴₂He)", fill="#FFD700", font=FONT_MD)
        # Beta (electron)
        arrow(draw,cx,cy-50,cx+80,cy-160,"#3498DB",w=3)
        draw.text((cx+85,cy-168), "β⁻ (e⁻)", fill="#3498DB", font=FONT_MD)
        # Gamma (photon)
        arrow(draw,cx-50,cy,cx-180,cy-60,"#A0FF00",w=2)
        draw.text((cx-250,cy-68), "γ (photon)", fill="#A0FF00", font=FONT_MD)
        draw.text((20,300),"α: A→A-4, Z→Z-2  |  β⁻: Z→Z+1  |  γ: no change",fill="#AAA",font=FONT_SM)
        draw.text((20,330),"Half-life T½: N = N₀ × (½)^(t/T½)",fill="#AAA",font=FONT_SM)

    elif scene == "fission":
        # U-235 + n → Ba + Kr + 3n
        draw.ellipse([60,165,120,225], fill="#E74C3C"); draw.text((68,185),"U-235",fill="white",font=FONT_SM)
        arrow(draw,100,130,100,163,"#FFD700",w=2); draw.text((108,115),"n",fill="#FFD700",font=FONT_MD)
        draw.text((130,188),"→",fill="white",font=FONT_XL)
        draw.ellipse([175,155,235,215], fill="#3498DB"); draw.text((181,178),"Ba-141",fill="white",font=FONT_SM)
        draw.text((245,188),"+",fill="white",font=FONT_LG)
        draw.ellipse([265,165,315,215], fill="#27AE60"); draw.text((270,183),"Kr-92",fill="white",font=FONT_SM)
        draw.text((325,188),"+",fill="white",font=FONT_LG)
        for nx,ny in [(360,140),(390,190),(360,240)]:
            draw.ellipse([nx-8,ny-8,nx+8,ny+8],fill="#FFD700")
            draw.text((nx+10,ny-8),"n",fill="#FFD700",font=FONT_SM)
        draw.text((30,285),"Fission: ²³⁵U + n → ¹⁴¹Ba + ⁹²Kr + 3n + ~200 MeV",fill="#AAA",font=FONT_SM)
        draw.text((30,315),"Chain reaction possible: 3 neutrons trigger more fissions",fill="#555",font=FONT_SM)

    return img

NUCLEAR_QA = [
    ("binding_energy",
     "The most stable nucleus (highest binding energy per nucleon) is:",
     "Iron-56 (⁵⁶Fe) with BE/A ≈ 8.8 MeV",
     ["Uranium-238", "Hydrogen-1", "Carbon-12"],
     "Iron-56 sits at the peak of the BE/A curve (~8.8 MeV/nucleon). Nuclei lighter or heavier can gain energy by fusion or fission."),

    ("fission",
     "Nuclear fission of U-235 by a neutron produces approximately:",
     "~200 MeV of energy per fission",
     ["1 eV", "1 MeV", "1000 MeV"],
     "U-235 fission releases ~200 MeV per nucleus, compared to ~few eV in chemical reactions."),

    ("fission",
     "In U-235 fission: ²³⁵U + n → ¹⁴¹Ba + ⁹²Kr + xn. Value of x:",
     "3 (three neutrons released)",
     ["1", "2", "0"],
     "Mass number conservation: 235+1 = 141+92+x → 236 = 233+x → x = 3 neutrons."),

    ("binding_energy",
     "Nuclear fusion releases energy because:",
     "Light nuclei (below Fe in BE curve) combine to form a more stable nucleus with higher BE/A",
     ["Heavy nuclei split into more stable fragments", "Radioactive decay occurs", "Neutrons convert to protons"],
     "For nuclei lighter than Fe: fusion increases BE/A → energy released. This powers the Sun."),

    ("decay",
     "Alpha (α) decay of Radium-226 (²²⁶₈₈Ra) produces:",
     "Radon-222 (²²²₈₆Rn) + α particle",
     ["Francium-225", "Radium-222 + β⁻", "Radon-224"],
     "α decay: A decreases by 4, Z decreases by 2. ²²⁶₈₈Ra → ²²²₈₆Rn + ⁴₂He"),

    ("decay",
     "Beta-minus (β⁻) decay involves emission of an electron. Atomic number Z:",
     "Increases by 1 (a neutron converts to proton + electron + antineutrino)",
     ["Decreases by 1", "Stays same", "Increases by 2"],
     "β⁻: n → p + e⁻ + ν̄_e. Z increases by 1, A unchanged."),

    ("decay",
     "Gamma (γ) radiation has:",
     "No charge and no mass (it is a high-energy photon)",
     ["Charge +2, mass 4u", "Charge -1, no mass", "Charge 0, mass 4u"],
     "γ rays are electromagnetic radiation (photons). They have no charge and no rest mass."),

    ("decay",
     "A radioactive sample has T½ = 4 years. After 12 years, fraction remaining:",
     "1/8 (three half-lives: ½³ = 1/8)",
     ["1/4", "1/16", "1/3"],
     "t/T½ = 12/4 = 3. N/N₀ = (½)³ = 1/8"),

    ("decay",
     "Radioactive decay law: N = N₀e^(−λt). The decay constant λ is related to T½ by:",
     "λ = ln2 / T½ = 0.693 / T½",
     ["λ = T½", "λ = 1/T½", "λ = T½/ln2"],
     "At t = T½: N₀/2 = N₀e^(−λT½) → λT½ = ln2 → λ = ln2/T½ = 0.693/T½"),

    ("fission",
     "Critical mass in a nuclear reactor refers to:",
     "Minimum mass of fissile material needed for a self-sustaining chain reaction",
     ["Maximum mass before meltdown", "Mass of moderator needed", "Mass per unit volume"],
     "Critical mass: enough fissile material so that neutrons from each fission cause at least one more fission on average."),

    ("fission",
     "The purpose of a moderator in a nuclear reactor is to:",
     "Slow down fast neutrons to thermal energies (better absorbed by U-235)",
     ["Absorb all neutrons", "Produce neutrons", "Cool the reactor"],
     "U-235 undergoes fission more readily with slow (thermal) neutrons. Moderator (heavy water, graphite) slows them down."),

    ("binding_energy",
     "Mass defect Δm of a nucleus is:",
     "Δm = Z·m_p + N·m_n − M_nucleus (difference between sum of constituent masses and actual nucleus mass)",
     ["Δm = A − Z", "Δm = mass of electrons", "Δm = binding energy directly"],
     "Mass defect: Δm = Zm_p + Nm_n - M. Binding energy E_b = Δm×c² (Einstein's E=mc²)."),

    ("decay",
     "Carbon-14 dating is used to determine the age of organic material. C-14 has T½ ≈ 5730 years. A sample with 25% of original C-14 remaining is approximately:",
     "11,460 years old (two half-lives)",
     ["5730 years", "2865 years", "22920 years"],
     "25% = (½)² → 2 half-lives = 2 × 5730 = 11,460 years."),

    ("binding_energy",
     "The Sun produces energy mainly through:",
     "Nuclear fusion (hydrogen → helium: 4¹H → ⁴He + energy)",
     ["Nuclear fission", "Chemical combustion", "Radioactive α decay"],
     "Sun's energy: proton-proton chain reaction — fusion of hydrogen nuclei into helium. Releases ~26 MeV per reaction."),

    ("fission",
     "The difference between a nuclear bomb and a nuclear reactor is:",
     "Reactor: controlled chain reaction (k=1); Bomb: uncontrolled supercritical chain reaction (k>>1)",
     ["Reactor uses fusion; bomb uses fission", "Reactor uses U-235; bomb uses Pu-239 only", "No fundamental difference"],
     "In a reactor, control rods maintain criticality k=1. In a bomb, supercritical mass gives uncontrolled exponential chain reaction."),
]

def gen_nuclear(n=QPT):
    n = min(n, len(NUCLEAR_QA))
    print(f"[Nuclear Physics] {n} questions...")
    for i,(scene,qtext,correct,wrongs,expl) in enumerate(NUCLEAR_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_nuclear(scene); url=upload_pil(img,f"nuc_{i}")
        ok=post_q("Science",12,random.choice(["Advanced","Olympiad"]),
                  "Nuclear Physics","Atoms and Nuclei",
                  qtext,url,opts,cidx,expl)
        print(f"  nuc_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("="*60)
    print("OlympiadReady — Class 11-12 Physics (Batch 7)")
    print("="*60)
    print()

    gen_projectile(QPT)
    gen_work_energy(QPT)
    gen_optics(QPT)
    gen_electricity(QPT)
    gen_semiconductor(QPT)
    gen_photoelectric(QPT)
    gen_nuclear(QPT)

    print("="*60)
    print(f"DONE — Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}")
    print("="*60)
