"""
generate_physics_diagrams.py
Physics & Earth Science diagram generators — Batch 3:
  1.  Electric Circuits         (Grades 6-9)   — text options
  2.  Light & Optics            (Grades 6-9)   — text options
  3.  Force & Motion            (Grades 6-9)   — text options
  4.  Sound Waves               (Grades 6-8)   — text options
  5.  Magnetism                 (Grades 5-8)   — text options
  6.  Weather & Climate         (Grades 5-7)   — text options
  7.  Solar System              (Grades 4-8)   — text options
  8.  Landforms                 (Grades 4-7)   — text options
  9.  Indian Map / States       (Grades 4-8)   — text options
 10.  Measurement & Units       (Grades 4-8)   — text options

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
except:
    FONT_SM = FONT_MD = FONT_LG = FONT_XL = ImageFont.load_default()

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
        public_id=f"ph3_{label}_{int(time.time()*1000)}", resource_type="image")
    return res["secure_url"]

def post_q(subject, grade, diff, topic, subtopic, text, img_url, opts, cidx, expl):
    global POSTED, SKIPPED, FAILED
    payload = dict(subject=subject, grade=grade, difficulty=diff, topic=topic,
                   subTopic=subtopic, questionText=text, imageUrl=img_url,
                   options=opts, correctAnswer=chr(65+cidx), explanation=expl)
    try:
        r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                          json=payload, headers=HEADERS, timeout=20)
        if r.status_code in (200,201):   POSTED  += 1; return True
        elif r.status_code == 409:       SKIPPED += 1; return False
        else: FAILED += 1; print(f"    FAIL {r.status_code}"); return False
    except Exception as e:
        FAILED += 1; print(f"    ERR {e}"); return False

def canvas(w=500, h=400, bg="white"):
    img = Image.new("RGB",(w,h),bg)
    return img, ImageDraw.Draw(img)


# ══════════════════════════════════════════════════════════════════════════════
# 1. ELECTRIC CIRCUITS
# ══════════════════════════════════════════════════════════════════════════════

def draw_circuit(circuit_type="series"):
    img, draw = canvas(540, 380, "#FAFAFA")
    draw.text((20,12), f"{circuit_type.title()} Circuit", fill="#2C3E50", font=FONT_LG)

    def battery(draw, x, y):
        """Draw battery symbol at x,y"""
        draw.line([(x,y-14),(x,y+14)], fill="#E74C3C", width=3)
        draw.line([(x+6,y-8),(x+6,y+8)], fill="#E74C3C", width=6)
        draw.text((x-8,y+16),"[B]",fill="#E74C3C",font=FONT_SM)

    def bulb(draw, x, y):
        """Draw bulb symbol"""
        draw.ellipse([x-14,y-14,x+14,y+14], outline="#F39C12", width=3)
        draw.line([(x-8,y-8),(x+8,y+8)], fill="#F39C12", width=2)
        draw.line([(x+8,y-8),(x-8,y+8)], fill="#F39C12", width=2)
        draw.text((x-6,y+16),"[L]",fill="#F39C12",font=FONT_SM)

    def resistor(draw, x, y):
        """Draw resistor symbol (rectangle)"""
        draw.rectangle([x-18,y-8,x+18,y+8], outline="#3498DB", width=2)
        draw.text((x-6,y+10),"[R]",fill="#3498DB",font=FONT_SM)

    def switch(draw, x, y, closed=True):
        """Draw switch symbol"""
        draw.line([(x-15,y),(x-5,y)], fill="#2C3E50", width=3)
        if closed:
            draw.line([(x-5,y),(x+15,y)], fill="#2C3E50", width=3)
        else:
            draw.line([(x-5,y),(x+12,y-12)], fill="#2C3E50", width=3)
        draw.text((x-6,y+8),"[S]",fill="#555",font=FONT_SM)

    wire = "#2C3E50"
    w = 3

    if circuit_type == "series":
        # Rectangle loop: battery - bulb1 - bulb2 - switch
        # Top wire
        draw.line([(80,120),(460,120)], fill=wire, width=w)
        # Bottom wire
        draw.line([(80,280),(460,280)], fill=wire, width=w)
        # Left wire
        draw.line([(80,120),(80,280)], fill=wire, width=w)
        # Right wire
        draw.line([(460,120),(460,280)], fill=wire, width=w)
        # Components on top wire
        battery(draw, 140, 120)
        bulb(draw, 250, 120)
        bulb(draw, 360, 120)
        switch(draw, 460, 200, closed=True)
        draw.text((180,310), "Series: same current through all components", fill="#555", font=FONT_SM)

    elif circuit_type == "parallel":
        # Two branches
        draw.line([(60,100),(480,100)], fill=wire, width=w)  # top
        draw.line([(60,300),(480,300)], fill=wire, width=w)  # bottom
        draw.line([(60,100),(60,300)], fill=wire, width=w)   # left
        draw.line([(480,100),(480,300)], fill=wire, width=w) # right
        battery(draw, 60, 200)
        # Branch 1
        draw.line([(200,100),(200,300)], fill=wire, width=w)
        bulb(draw, 200, 180)
        # Branch 2
        draw.line([(340,100),(340,300)], fill=wire, width=w)
        bulb(draw, 340, 180)
        draw.text((150,320), "Parallel: same voltage across all branches", fill="#555", font=FONT_SM)

    elif circuit_type == "open":
        draw.line([(80,120),(460,120)], fill=wire, width=w)
        draw.line([(80,280),(460,280)], fill=wire, width=w)
        draw.line([(80,120),(80,280)], fill=wire, width=w)
        draw.line([(460,120),(460,280)], fill=wire, width=w)
        battery(draw, 140, 120)
        bulb(draw, 300, 120)
        switch(draw, 460, 200, closed=False)  # open switch
        draw.text((160,310), "Open circuit: switch open, no current flows", fill="#E74C3C", font=FONT_SM)

    return img

CIRCUIT_QA = [
    ("series","In a series circuit, if one bulb fuses, the others:",
     "All go off (circuit breaks)", ["Continue glowing", "Glow brighter", "Glow dimmer"]),
    ("parallel","In a parallel circuit, if one branch breaks, the others:",
     "Continue to work", ["All go off", "All get dimmer", "All get brighter"]),
    ("series","In a series circuit, the current through each component is:",
     "The same throughout", ["Different in each", "Zero everywhere", "Highest at battery"]),
    ("parallel","In a parallel circuit, the voltage across each branch is:",
     "The same", ["Different", "Zero", "Doubled"]),
    ("open","An open circuit means:",
     "The circuit is broken and no current flows",
     ["Current flows freely", "Extra resistance added", "Battery is dead"]),
    ("series","Which component is used to break or complete a circuit?",
     "Switch", ["Resistor", "Bulb", "Wire"]),
    ("parallel","Why are household appliances connected in parallel?",
     "Each appliance gets full voltage and works independently",
     ["To save wire", "To share current equally", "To reduce voltage"]),
    ("series","A resistor in a circuit is used to:",
     "Control/limit the flow of current",
     ["Store charge", "Increase voltage", "Convert current to AC"]),
    ("series","The unit of electric current is:",
     "Ampere (A)", ["Volt (V)", "Ohm (Ω)", "Watt (W)"]),
    ("parallel","The unit of electrical resistance is:",
     "Ohm (Ω)", ["Ampere (A)", "Volt (V)", "Coulomb (C)"]),
    ("series","Ohm's Law states that V = I × R. If voltage = 12V and resistance = 4Ω, current =",
     "3 A", ["48 A", "8 A", "1 A"]),
    ("parallel","Which device converts electrical energy into light energy?",
     "Light bulb / LED", ["Battery", "Resistor", "Switch"]),
    ("open","A fuse in a circuit is designed to:",
     "Melt and break the circuit if too much current flows",
     ["Store extra current", "Increase resistance permanently", "Boost voltage"]),
    ("series","Which of these is a conductor of electricity?",
     "Copper wire", ["Rubber", "Plastic", "Wood"]),
    ("parallel","The EMF (electromotive force) of a cell is measured in:",
     "Volts", ["Amperes", "Ohms", "Watts"]),
    ("series","Electric power = V × I. A device at 230V draws 2A. Its power is:",
     "460 W", ["115 W", "232 W", "920 W"]),
    ("series","The function of a battery in a circuit is to:",
     "Provide electrical energy (EMF)",
     ["Resist current", "Store current", "Convert current to voltage"]),
    ("parallel","An ammeter is connected in _____ in a circuit:",
     "Series", ["Parallel", "Either", "Neither"]),
    ("parallel","A voltmeter is connected in _____ in a circuit:",
     "Parallel", ["Series", "Either", "Neither"]),
    ("series","Which material is used as the filament in a traditional light bulb?",
     "Tungsten", ["Copper", "Iron", "Carbon"]),
]

def gen_circuits(n=QPT):
    print(f"[Electric Circuits] {n} questions...")
    for i, (ctype, qtext, correct, wrongs) in enumerate(CIRCUIT_QA[:n]):
        opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
        img = draw_circuit(ctype)
        url = upload_pil(img, f"circuit_{i}")
        g = random.choice([6,7,8,9]); d = difficulty_for_grade(g)
        ok = post_q("Science", g, d, "Electricity", "Electric Circuits",
                    qtext, url, opts, cidx, f"Answer: {correct}.")
        print(f"  circuit_{i} ({ctype})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 2. LIGHT & OPTICS
# ══════════════════════════════════════════════════════════════════════════════

def draw_optics(scene):
    img, draw = canvas(500, 360, "#0A0A2E")  # Dark background for light

    def ray(x1,y1,x2,y2,color="#FFD700"):
        draw.line([(x1,y1),(x2,y2)], fill=color, width=2)
        # Arrowhead
        dx,dy = x2-x1, y2-y1
        L = max(1,math.sqrt(dx*dx+dy*dy))
        ux,uy = dx/L,dy/L
        ax,ay = x2-ux*12, y2-uy*12
        draw.polygon([(x2,y2),(int(ax-uy*6),int(ay+ux*6)),(int(ax+uy*6),int(ay-ux*6))],fill=color)

    if scene == "reflection":
        draw.text((20,12), "Law of Reflection", fill="white", font=FONT_LG)
        # Mirror (vertical line at x=280)
        draw.line([(280,50),(280,320)], fill="#888", width=4)
        draw.text((290,160), "Mirror", fill="#AAA", font=FONT_MD)
        # Normal (dotted)
        for y in range(60,320,12):
            draw.point((280,y), fill="#555")
        draw.text((255,30), "Normal", fill="#555", font=FONT_SM)
        # Incident ray
        ray(80,50, 280,180, "#FFD700")
        draw.text((80,35), "Incident ray", fill="#FFD700", font=FONT_SM)
        # Reflected ray
        ray(280,180, 80,310, "#00FF88")
        draw.text((85,315), "Reflected ray", fill="#00FF88", font=FONT_SM)
        # Angle labels
        draw.text((200,145), "i", fill="#FFD700", font=FONT_LG)
        draw.text((200,210), "r", fill="#00FF88", font=FONT_LG)
        draw.text((80,340), "Angle of incidence (i) = Angle of reflection (r)", fill="#AAA", font=FONT_SM)

    elif scene == "refraction":
        draw.text((20,12), "Refraction of Light", fill="white", font=FONT_LG)
        # Interface line
        draw.line([(0,200),(500,200)], fill="#1A6B8A", width=3)
        draw.text((380,205), "Glass/Water", fill="#4ECDC4", font=FONT_SM)
        draw.text((380,175), "Air", fill="#AAA", font=FONT_SM)
        # Normal
        for y in range(30,370,12):
            draw.point((250,y), fill="#555")
        draw.text((255,20), "Normal", fill="#555", font=FONT_SM)
        # Incident ray (above surface)
        ray(100,50, 250,200, "#FFD700")
        draw.text((60,35), "Incident", fill="#FFD700", font=FONT_SM)
        # Refracted ray (bends toward normal in denser medium)
        ray(250,200, 320,350, "#00BFFF")
        draw.text((325,340), "Refracted", fill="#00BFFF", font=FONT_SM)
        # Angle labels
        draw.text((200,155), "i", fill="#FFD700", font=FONT_LG)
        draw.text((265,240), "r", fill="#00BFFF", font=FONT_LG)
        draw.text((50,340),"Light bends toward normal entering denser medium",fill="#AAA",font=FONT_SM)

    elif scene == "convex_lens":
        draw.text((20,12), "Convex (Converging) Lens", fill="white", font=FONT_LG)
        # Lens shape
        cx = 250
        for y in range(80,280):
            hw = int(30 * math.sin(math.pi * (y-80)/200))
            draw.point((cx-hw, y), fill="#4ECDC4")
            draw.point((cx+hw, y), fill="#4ECDC4")
        draw.text((cx-18, 285), "Lens", fill="#4ECDC4", font=FONT_SM)
        # Principal axis
        draw.line([(30,180),(470,180)], fill="#555", width=1)
        # Focus points
        f = 100
        draw.ellipse([cx+f-5,175,cx+f+5,185], fill="#FF6B6B")
        draw.text((cx+f-5,158), "F", fill="#FF6B6B", font=FONT_MD)
        draw.ellipse([cx-f-5,175,cx-f+5,185], fill="#FF6B6B")
        draw.text((cx-f-5,158), "F", fill="#FF6B6B", font=FONT_MD)
        # Rays converging
        ray(30,120, cx,120, "#FFD700")
        ray(cx,120, cx+f,180, "#FFD700")
        ray(30,180, cx+f,180, "#FFD700")
        ray(30,240, cx,240, "#FFD700")
        ray(cx,240, cx+f,180, "#FFD700")
        draw.text((30,300), "Parallel rays converge at focal point F", fill="#AAA", font=FONT_SM)

    elif scene == "concave_mirror":
        draw.text((20,12), "Concave Mirror", fill="white", font=FONT_LG)
        # Mirror arc on right
        for angle in range(-60, 61, 2):
            rad = math.radians(angle)
            r = 180
            x = 400 + int(r * math.cos(rad))
            y = 180 + int(r * math.sin(rad))
            draw.point((x,y), fill="#888")
        draw.text((390,280), "Mirror", fill="#AAA", font=FONT_SM)
        # Principal axis
        draw.line([(30,180),(420,180)], fill="#555",width=1)
        # Focus (halfway between mirror and centre of curvature)
        f_x = 310
        draw.ellipse([f_x-5,175,f_x+5,185], fill="#FF6B6B")
        draw.text((f_x-5,158), "F", fill="#FF6B6B", font=FONT_MD)
        # Parallel rays reflecting through focus
        ray(30,130, 380,148, "#FFD700")
        ray(380,148, f_x,180, "#FFD700")
        ray(30,180, f_x,180, "#FFD700")
        ray(30,230, 380,212, "#FFD700")
        ray(380,212, f_x,180, "#FFD700")
        draw.text((30,300), "Parallel rays reflect through focal point F", fill="#AAA", font=FONT_SM)

    return img

OPTICS_QA = [
    ("reflection","The law of reflection states that angle of incidence equals:",
     "Angle of reflection", ["Angle of refraction","90°","Angle of incidence/2"]),
    ("refraction","When light passes from air into glass (denser medium), it:",
     "Bends toward the normal (slows down)",
     ["Bends away from normal","Continues in same direction","Reflects completely"]),
    ("convex_lens","A convex lens is also called a _____ lens:",
     "Converging", ["Diverging","Concave","Plane"]),
    ("concave_mirror","A concave mirror is used in car headlights because it:",
     "Reflects parallel beams of light",
     ["Magnifies the bulb","Absorbs more light","Changes colour of light"]),
    ("reflection","Total internal reflection occurs when light travels from:",
     "Denser to rarer medium at an angle greater than critical angle",
     ["Air into water","Vacuum into glass","Rarer to denser medium"]),
    ("refraction","The phenomenon of splitting white light into colours is called:",
     "Dispersion", ["Reflection","Diffraction","Polarisation"]),
    ("convex_lens","The focal length of a lens is the distance from the lens to the:",
     "Focal point (focus)", ["Object","Image","Centre of curvature"]),
    ("concave_mirror","Mirrors used in solar cookers are:",
     "Concave mirrors (converge sunlight)", ["Convex mirrors","Plane mirrors","Diffuse mirrors"]),
    ("reflection","A convex mirror always forms an image that is:",
     "Virtual, erect and diminished",
     ["Real, inverted and enlarged","Virtual, inverted and enlarged","Real, erect and same size"]),
    ("refraction","The speed of light in vacuum is approximately:",
     "3 × 10⁸ m/s", ["3 × 10⁶ m/s","3 × 10¹⁰ m/s","3 × 10⁴ m/s"]),
    ("convex_lens","A convex lens can be used as a magnifying glass when the object is placed:",
     "Within the focal length", ["Beyond 2F","At 2F","At F"]),
    ("reflection","The image formed by a plane mirror is:",
     "Virtual, erect, laterally inverted and same size",
     ["Real, inverted and magnified","Virtual, inverted and same size","Real, erect and same size"]),
    ("refraction","A mirage is caused by:",
     "Total internal reflection of light due to hot air layers",
     ["Reflection from water surfaces","Dispersion of light","Diffraction"]),
    ("concave_mirror","Which mirror is used as a rear-view mirror in vehicles?",
     "Convex mirror (gives wider field of view)",
     ["Concave mirror","Plane mirror","Cylindrical mirror"]),
    ("refraction","The refractive index of glass is about 1.5. This means light travels in glass:",
     "1.5 times slower than in vacuum",
     ["1.5 times faster","At the same speed","2 times slower"]),
    ("convex_lens","Long-sightedness (hypermetropia) is corrected using:",
     "Convex (converging) lens", ["Concave lens","Plane mirror","Concave mirror"]),
    ("reflection","Short-sightedness (myopia) is corrected using:",
     "Concave (diverging) lens", ["Convex lens","Plane mirror","Bifocal lens"]),
    ("refraction","A rainbow is formed due to:",
     "Dispersion and total internal reflection in water droplets",
     ["Only reflection","Diffraction only","Scattering of light"]),
    ("convex_lens","Power of a lens = 1/f (in metres). A lens of focal length 25 cm has power:",
     "+4 D (dioptres)", ["-4 D","0.25 D","2.5 D"]),
    ("concave_mirror","When an object is at the focal point of a concave mirror, the image is formed at:",
     "Infinity (parallel reflected rays)", ["At F","At C","Between F and C"]),
]

def gen_optics(n=QPT):
    print(f"[Light & Optics] {n} questions...")
    for i,(scene,qtext,correct,wrongs) in enumerate(OPTICS_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_optics(scene); url=upload_pil(img,f"optics_{i}")
        g=random.choice([6,7,8,9]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Light","Optics & Reflection",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  optics_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 3. FORCE & MOTION
# ══════════════════════════════════════════════════════════════════════════════

def draw_force(scene):
    img, draw = canvas(500, 360, "#F8F9FA")
    draw.text((20,12), f"Force & Motion: {scene.replace('_',' ').title()}", fill="#2C3E50", font=FONT_MD)

    def arrow(x1,y1,x2,y2,color,label=""):
        draw.line([(x1,y1),(x2,y2)], fill=color, width=4)
        dx,dy=x2-x1,y2-y1; L=max(1,math.sqrt(dx*dx+dy*dy))
        ux,uy=dx/L,dy/L; ax,ay=x2-ux*16,y2-uy*16
        draw.polygon([(x2,y2),(int(ax-uy*8),int(ay+ux*8)),(int(ax+uy*8),int(ay-ux*8))],fill=color)
        if label: draw.text((x2+4,y2-10),label,fill=color,font=FONT_MD)

    if scene == "newtons_first":
        # Object at rest, no net force
        draw.ellipse([200,150,300,250], fill="#3498DB")
        draw.text((228,188), "Ball", fill="white", font=FONT_MD)
        # Equal forces cancel
        arrow(130,200, 195,200, "#E74C3C", "F₁")
        arrow(305,200, 370,200, "#27AE60", "F₂")
        draw.text((80,270), "F₁ = F₂  → Net force = 0 → Ball stays at rest", fill="#2C3E50", font=FONT_SM)
        draw.text((80,295), "Newton's 1st Law: An object continues in its state", fill="#555", font=FONT_SM)
        draw.text((80,315), "of rest or uniform motion unless a net force acts.", fill="#555", font=FONT_SM)

    elif scene == "newtons_second":
        # F = ma diagram
        draw.rectangle([180,150,320,250], fill="#9B59B6")
        draw.text((195,188), "Mass = 5 kg", fill="white", font=FONT_SM)
        arrow(100,200, 175,200, "#E74C3C", "F=10N")
        draw.text((80,270), "F = ma  →  10 N = 5 kg × a  →  a = 2 m/s²", fill="#2C3E50", font=FONT_MD)
        draw.text((80,305), "Newton's 2nd Law: F = mass × acceleration", fill="#555", font=FONT_SM)

    elif scene == "newtons_third":
        # Action-reaction
        draw.ellipse([100,150,200,250], fill="#E74C3C")
        draw.text((120,188),"Obj A",fill="white",font=FONT_SM)
        draw.ellipse([300,150,400,250], fill="#27AE60")
        draw.text((318,188),"Obj B",fill="white",font=FONT_SM)
        # Action
        arrow(200,185, 298,185, "#E74C3C", "Action")
        # Reaction
        arrow(300,215, 202,215, "#27AE60", "Reaction")
        draw.text((80,270), "Every action has equal and opposite reaction", fill="#2C3E50", font=FONT_MD)

    elif scene == "friction":
        # Block on surface with friction arrow
        draw.rectangle([180,180,340,260], fill="#E67E22")
        draw.text((225,212), "Block", fill="white", font=FONT_MD)
        # Applied force
        arrow(100,220, 178,220, "#27AE60", "Push")
        # Friction (opposite)
        arrow(342,220, 420,220, "#E74C3C", "Friction")
        # Surface
        draw.line([(60,261),(460,261)], fill="#7F8C8D", width=4)
        draw.text((80,290), "Friction acts opposite to direction of motion", fill="#2C3E50", font=FONT_SM)
        draw.text((80,315), "Depends on surface roughness and normal force", fill="#555", font=FONT_SM)

    elif scene == "gravity":
        # Object falling, gravitational force arrow down
        draw.ellipse([225,80,295,140], fill="#3498DB")
        draw.text((238,98), "Ball", fill="white", font=FONT_SM)
        # Weight arrow downward
        arrow(260,142, 260,300, "#E74C3C", "W=mg")
        draw.text((80,320), "Weight = mass × g  (g = 9.8 m/s² on Earth)", fill="#2C3E50", font=FONT_SM)
        draw.text((80,345), "Gravity acts downward toward Earth's centre", fill="#555", font=FONT_SM)

    return img

FORCE_QA = [
    ("newtons_first","Newton's First Law states that an object at rest will remain at rest unless acted upon by:",
     "A net (unbalanced) external force",["Gravity only","Any force","Its own inertia"]),
    ("newtons_second","According to F = ma, if force doubles and mass stays constant, acceleration:",
     "Doubles",["Halves","Stays the same","Quadruples"]),
    ("newtons_third","Newton's Third Law says that for every action, there is:",
     "An equal and opposite reaction",["A greater reaction","A smaller reaction","No reaction in vacuum"]),
    ("friction","Friction always acts in the direction _____ to motion:",
     "Opposite",["Same","Perpendicular","Diagonal"]),
    ("gravity","The weight of an object is:",
     "Mass × gravitational acceleration (W = mg)",
     ["Same as mass","Volume × density","Equal to pressure"]),
    ("newtons_first","Inertia is the tendency of an object to:",
     "Resist any change in its state of motion",
     ["Accelerate under gravity","Attract other masses","Repel forces"]),
    ("newtons_second","A force of 20 N acts on a 4 kg object. The acceleration is:",
     "5 m/s²",["80 m/s²","0.2 m/s²","16 m/s²"]),
    ("friction","Which type of friction acts on a stationary object when a force is applied but it does not move?",
     "Static friction",["Kinetic friction","Rolling friction","Fluid friction"]),
    ("gravity","On the Moon, the gravitational acceleration is about 1/6th of Earth's. If your mass is 60 kg on Earth, on the Moon your mass is:",
     "60 kg (mass doesn't change, only weight changes)",
     ["10 kg","360 kg","6 kg"]),
    ("newtons_third","A rocket moves forward because hot gases are expelled backward. This is an example of:",
     "Newton's Third Law (action-reaction)",
     ["First Law","Second Law","Law of gravitation"]),
    ("newtons_second","Which of these has greater inertia?",
     "A loaded truck at rest",["A bicycle moving at 10 km/h","A tennis ball","A feather"]),
    ("friction","Ball bearings in a machine are used to:",
     "Reduce friction by converting sliding to rolling",
     ["Increase friction","Increase weight","Convert kinetic to potential energy"]),
    ("gravity","The gravitational force between two objects increases when:",
     "Their masses increase OR distance decreases",
     ["Distance increases","Masses decrease","Both move in circles"]),
    ("newtons_first","A passenger lurches forward when a bus brakes suddenly. This is due to:",
     "Inertia of motion",["Gravity","Normal reaction","Centripetal force"]),
    ("newtons_second","Force is measured in:",
     "Newtons (N)",["Joules (J)","Watts (W)","Kilograms (kg)"]),
    ("friction","Lubricants like oil and grease reduce:",
     "Friction between moving surfaces",
     ["Gravity","Weight","Normal force"]),
    ("gravity","If a 10 kg object falls freely, its weight on Earth (g=10 m/s²) is:",
     "100 N",["10 N","1000 N","9.8 N"]),
    ("newtons_third","When you swim forward, you push water backward. This is Newton's:",
     "Third Law",["First Law","Second Law","Fourth Law"]),
    ("friction","Streamlining a car or aeroplane reduces:",
     "Air resistance (fluid friction)",
     ["Static friction","Gravitational force","Magnetic force"]),
    ("newtons_second","The SI unit of mass is:",
     "Kilogram (kg)",["Newton (N)","Pound (lb)","Gram (g)"]),
]

def gen_force_motion(n=QPT):
    print(f"[Force & Motion] {n} questions...")
    for i,(scene,qtext,correct,wrongs) in enumerate(FORCE_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_force(scene); url=upload_pil(img,f"force_{i}")
        g=random.choice([6,7,8,9]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Force and Motion","Newton's Laws",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  force_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 4. SOLAR SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

PLANETS = [
    ("Mercury", 18, "#9E9E9E", 70),
    ("Venus",   24, "#FFC107", 105),
    ("Earth",   26, "#2196F3", 145),
    ("Mars",    20, "#F44336", 185),
    ("Jupiter", 50, "#FF9800", 250),
    ("Saturn",  42, "#FFD54F", 320),  # has rings
    ("Uranus",  32, "#80DEEA", 380),
    ("Neptune", 30, "#3F51B5", 430),
]

def draw_solar_system(highlight=None):
    img, draw = canvas(520, 360, "#0A0A1A")
    draw.text((150,12), "The Solar System", fill="white", font=FONT_LG)
    # Sun
    draw.ellipse([10,145,60,195], fill="#FFC107")
    draw.text((12,198), "Sun", fill="#FFC107", font=FONT_SM)
    # Planets
    for name, r, color, x in PLANETS:
        y = 170
        is_hi = (name == highlight)
        fill = "#FFD700" if is_hi else color
        outline = "#FFFFFF" if is_hi else color
        draw.ellipse([x-r,y-r,x+r,y+r], fill=fill, outline=outline, width=2 if is_hi else 1)
        # Saturn rings
        if name == "Saturn":
            draw.ellipse([x-r-14,y-6,x+r+14,y+6], outline="#FFD54F", width=2)
        # Label
        tw = len(name)*6
        draw.text((x-tw//2, y+r+4), name, fill=fill, font=FONT_SM)
    # Orbit dotted lines
    for name, r, color, x in PLANETS:
        draw.line([(60,170),(520,170)], fill="#222233", width=1)
    return img

SOLAR_QA = [
    ("Mercury","Which is the smallest planet in our Solar System?",
     "Mercury",["Mars","Pluto","Venus"]),
    ("Venus","Which planet is known as the 'Morning Star' or 'Evening Star'?",
     "Venus",["Mars","Jupiter","Saturn"]),
    ("Earth","Which is the only planet known to support life?",
     "Earth",["Mars","Venus","Jupiter"]),
    ("Mars","Which planet is called the 'Red Planet'?",
     "Mars",["Venus","Mercury","Jupiter"]),
    ("Jupiter","Which is the largest planet in our Solar System?",
     "Jupiter",["Saturn","Uranus","Neptune"]),
    ("Saturn","Which planet is famous for its prominent ring system?",
     "Saturn",["Uranus","Jupiter","Neptune"]),
    ("Uranus","Which planet rotates on its side (axial tilt ~98°)?",
     "Uranus",["Saturn","Neptune","Venus"]),
    ("Neptune","Which is the farthest planet from the Sun?",
     "Neptune",["Uranus","Saturn","Pluto"]),
    ("Earth","How many planets are in our Solar System?",
     "8",["9","7","10"]),
    ("Jupiter","The Great Red Spot on Jupiter is:",
     "A massive storm system",["A volcano","A crater","A moon"]),
    ("Mercury","Which planet has the shortest year (fastest orbit)?",
     "Mercury (88 Earth days)",["Venus","Mars","Earth"]),
    ("Venus","Which planet has the hottest surface temperature?",
     "Venus (~465°C, due to greenhouse effect)",["Mercury","Mars","Jupiter"]),
    ("Earth","The Moon is Earth's only natural:",
     "Satellite",["Planet","Star","Asteroid"]),
    ("Saturn","Which planet has the most known moons?",
     "Saturn (over 140 moons)",["Jupiter","Uranus","Neptune"]),
    ("Mars","The largest volcano in the Solar System, Olympus Mons, is on:",
     "Mars",["Venus","Earth","Jupiter"]),
    ("Neptune","Which planet was first discovered using mathematical prediction (not direct observation)?",
     "Neptune",["Uranus","Pluto","Saturn"]),
    ("Jupiter","Jupiter is classified as a:",
     "Gas giant",["Rocky planet","Dwarf planet","Ice giant"]),
    ("Earth","The asteroid belt lies between which two planets?",
     "Mars and Jupiter",["Earth and Mars","Jupiter and Saturn","Saturn and Uranus"]),
    ("Venus","Which planet has a day longer than its year?",
     "Venus",["Mercury","Mars","Saturn"]),
    ("Uranus","Uranus and Neptune are classified as:",
     "Ice giants",["Gas giants","Rocky planets","Dwarf planets"]),
]

def gen_solar_system(n=QPT):
    print(f"[Solar System] {n} questions...")
    for i,(planet,qtext,correct,wrongs) in enumerate(SOLAR_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_solar_system(planet); url=upload_pil(img,f"solar_{i}")
        g=random.choice([4,5,6,7,8]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Solar System","Planets",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  solar_{i} ({planet})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 5. LANDFORMS
# ══════════════════════════════════════════════════════════════════════════════

def draw_landform(ltype):
    img, draw = canvas(500, 340, "#87CEEB")  # Sky blue background

    # Ground base
    draw.rectangle([0,280,500,340], fill="#8B6914")  # ground

    if ltype == "mountain":
        pts = [(250,60),(80,280),(420,280)]
        draw.polygon(pts, fill="#7F8C8D")
        # Snow cap
        draw.polygon([(250,60),(210,130),(290,130)], fill="white")
        draw.text((215,280), "Mountain", fill="#2C3E50", font=FONT_MD)
        draw.text((60,310), "Steep rocky landform, formed by tectonic uplift", fill="white", font=FONT_SM)

    elif ltype == "valley":
        # V-shape valley between hills
        draw.polygon([(0,100),(0,280),(200,280),(250,200),(300,280),(500,280),(500,100)],
                     fill="#7F8C8D")
        draw.polygon([(200,280),(250,200),(300,280)], fill="#27AE60")  # valley floor
        # River at bottom
        draw.line([(250,200),(250,280)], fill="#3498DB", width=5)
        draw.text((215,288), "Valley", fill="#2C3E50", font=FONT_MD)
        draw.text((60,315), "Low area between hills/mountains, often with river", fill="white", font=FONT_SM)

    elif ltype == "plateau":
        # Flat top elevated land
        draw.rectangle([100,140,400,280], fill="#A0522D")
        # Steep sides
        draw.polygon([(70,280),(100,140),(100,280)], fill="#8B4513")
        draw.polygon([(400,140),(430,280),(400,280)], fill="#8B4513")
        draw.text((220,200), "Plateau", fill="white", font=FONT_MD)
        draw.text((60,308), "High flat land, called 'table land'", fill="white", font=FONT_SM)

    elif ltype == "delta":
        # River splitting into distributaries at sea
        draw.rectangle([0,200,500,280], fill="#1A6B8A")  # sea
        draw.text((200,235), "Sea / Ocean", fill="white", font=FONT_MD)
        # Main river
        draw.polygon([(250,60),(235,200),(265,200)], fill="#3498DB")
        # Distributaries
        draw.polygon([(235,200),(150,200),(200,260)], fill="#3498DB")
        draw.polygon([(265,200),(350,200),(300,260)], fill="#3498DB")
        draw.polygon([(235,200),(265,200),(250,260)], fill="#3498DB")
        # Land deposits
        draw.polygon([(200,260),(250,260),(300,260),(320,200),(180,200)],
                     fill="#C2A028", outline="#8B6914")
        draw.text((210,220), "Delta", fill="#2C3E50", font=FONT_MD)
        draw.text((40,295), "Fan-shaped deposit where river meets sea", fill="#2C3E50", font=FONT_SM)

    elif ltype == "peninsula":
        draw.rectangle([0,160,500,280], fill="#1A6B8A")  # sea
        # Land jutting into sea
        draw.polygon([(100,60),(100,260),(400,260),(400,60)], fill="#27AE60")
        draw.polygon([(150,260),(350,260),(250,330)], fill="#27AE60")
        draw.text((200,240), "Peninsula", fill="white", font=FONT_MD)
        draw.text((130,308), "Land surrounded by water on 3 sides", fill="white", font=FONT_SM)

    elif ltype == "island":
        draw.rectangle([0,80,500,340], fill="#1A6B8A")  # sea
        # Island in centre
        draw.ellipse([160,130,340,270], fill="#27AE60")
        draw.ellipse([185,150,315,255], fill="#8B6914")
        draw.text((205,195), "Island", fill="white", font=FONT_MD)
        draw.text((100,295), "Land completely surrounded by water", fill="white", font=FONT_SM)

    return img

LANDFORM_QA = [
    ("mountain","A high steep landform with a narrow peak is called:",
     "Mountain",["Valley","Plateau","Peninsula"]),
    ("valley","A low-lying area between hills or mountains, often with a river, is called:",
     "Valley",["Delta","Plateau","Canyon"]),
    ("plateau","A high, flat-topped landform is called:",
     "Plateau",["Mountain","Valley","Delta"]),
    ("delta","A triangular deposit of sediment where a river meets the sea is called:",
     "Delta",["Peninsula","Island","Valley"]),
    ("peninsula","Land surrounded by water on three sides is called:",
     "Peninsula",["Island","Delta","Cape"]),
    ("island","Land completely surrounded by water is called:",
     "Island",["Peninsula","Delta","Atoll"]),
    ("mountain","The Himalayas are an example of a:",
     "Mountain range (fold mountains)",["Plateau","Delta","Valley"]),
    ("plateau","The Deccan Plateau in India is an example of a:",
     "Plateau",["Mountain","Delta","Peninsula"]),
    ("delta","The Ganges-Brahmaputra delta (Sundarbans) is located in:",
     "West Bengal (India) and Bangladesh",["Maharashtra","Gujarat","Tamil Nadu"]),
    ("peninsula","India is an example of a large:",
     "Peninsula (surrounded by Arabian Sea, Bay of Bengal, Indian Ocean)",
     ["Island","Delta","Plateau"]),
    ("valley","The Kashmir Valley lies between which mountain ranges?",
     "Himalayas and Pir Panjal",["Aravalli and Vindhya","Western and Eastern Ghats","Karakoram and Hindu Kush"]),
    ("mountain","Which is the highest mountain peak in the world?",
     "Mount Everest (8,849 m)",["K2","Kangchenjunga","Mont Blanc"]),
    ("island","Sri Lanka is an example of:",
     "An island",["A peninsula","A delta","A plateau"]),
    ("plateau","The Tibetan Plateau is often called the 'Roof of the World' because:",
     "It is the highest and largest plateau on Earth",
     ["It receives most rain","It has the most mountains","It borders all countries"]),
    ("delta","Why are deltas very fertile agricultural lands?",
     "They are made of rich alluvial soil deposited by rivers",
     ["They get more sunshine","They are near the sea","They have no rocks"]),
    ("valley","The Great Rift Valley is located in:",
     "East Africa",["South America","India","Australia"]),
    ("mountain","Fold mountains are formed by:",
     "Collision of tectonic plates (continental)",
     ["Volcanic activity","Erosion by rivers","Glacial deposits"]),
    ("plateau","A plateau that is completely surrounded by mountains is called:",
     "Intermontane plateau",["Continental plateau","Piedmont plateau","Coastal plateau"]),
    ("island","The Andaman and Nicobar Islands belong to:",
     "India",["Myanmar","Indonesia","Sri Lanka"]),
    ("delta","The Nile Delta is located in:",
     "Egypt (North Africa)",["India","China","Brazil"]),
]

def gen_landforms(n=QPT):
    print(f"[Landforms] {n} questions...")
    for i,(ltype,qtext,correct,wrongs) in enumerate(LANDFORM_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_landform(ltype); url=upload_pil(img,f"land_{i}")
        g=random.choice([4,5,6,7]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Geography","Landforms",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  land_{i} ({ltype})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 6. MAGNETISM
# ══════════════════════════════════════════════════════════════════════════════

def draw_magnet(scene):
    img, draw = canvas(480, 340, "#FAFAFA")
    draw.text((20,12), f"Magnetism: {scene.replace('_',' ').title()}", fill="#2C3E50", font=FONT_MD)

    if scene == "bar_magnet":
        # Bar magnet with field lines
        # Magnet body
        draw.rectangle([140,140,240,200], fill="#E74C3C")  # N pole (red)
        draw.rectangle([240,140,340,200], fill="#3498DB")  # S pole (blue)
        draw.text((175,158), "N", fill="white", font=FONT_XL)
        draw.text((275,158), "S", fill="white", font=FONT_XL)
        # Field lines (simplified arcs)
        for r in [40,70,100]:
            draw.arc([240-r, 170-r, 240+r, 170+r], start=270, end=90, fill="#F39C12", width=2)
        draw.text((100,240),"Magnetic field lines go N→S outside magnet", fill="#2C3E50", font=FONT_SM)

    elif scene == "attraction":
        # N-S attract
        draw.rectangle([80,140,170,200], fill="#E74C3C"); draw.text((107,162),"N",fill="white",font=FONT_XL)
        draw.rectangle([170,140,260,200], fill="#3498DB"); draw.text((197,162),"S",fill="white",font=FONT_XL)
        draw.rectangle([280,140,370,200], fill="#3498DB"); draw.text((307,162),"S",fill="white",font=FONT_XL)
        draw.rectangle([370,140,460,200], fill="#E74C3C"); draw.text((397,162),"N",fill="white",font=FONT_XL)
        # Arrows showing attraction (towards each other)
        draw.text((165,215), "← ATTRACT →", fill="#27AE60", font=FONT_MD)
        draw.text((30,260), "Unlike poles (N-S) attract each other", fill="#2C3E50", font=FONT_MD)

    elif scene == "repulsion":
        # N-N repel
        draw.rectangle([80,140,170,200], fill="#E74C3C"); draw.text((107,162),"N",fill="white",font=FONT_XL)
        draw.rectangle([170,140,260,200], fill="#3498DB"); draw.text((197,162),"S",fill="white",font=FONT_XL)
        draw.rectangle([280,140,370,200], fill="#3498DB"); draw.text((307,162),"S",fill="white",font=FONT_XL)
        draw.rectangle([370,140,460,200], fill="#E74C3C"); draw.text((397,162),"N",fill="white",font=FONT_XL)
        # Show N-N and S-S repel
        draw.text((80,215), "N|S  ← REPEL →  S|N", fill="#E74C3C", font=FONT_MD)
        draw.text((40,260),"Like poles (N-N or S-S) repel each other", fill="#2C3E50", font=FONT_MD)

    elif scene == "compass":
        # Compass with needle
        cx, cy = 240, 170
        r = 80
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], outline="#7F8C8D", width=3)
        # N S E W labels
        draw.text((cx-8, cy-r-22),"N",fill="#E74C3C",font=FONT_LG)
        draw.text((cx-8, cy+r+5),"S",fill="#3498DB",font=FONT_LG)
        draw.text((cx+r+5, cy-10),"E",fill="#2C3E50",font=FONT_LG)
        draw.text((cx-r-20, cy-10),"W",fill="#2C3E50",font=FONT_LG)
        # Needle
        draw.polygon([(cx,cy-60),(cx-10,cy),(cx,cy+20),(cx+10,cy)], fill="#E74C3C")
        draw.polygon([(cx,cy+20),(cx-8,cy),(cx,cy-20),(cx+8,cy)], fill="#888")
        draw.text((80,285),"Compass needle points to magnetic North Pole",fill="#2C3E50",font=FONT_SM)

    return img

MAGNET_QA = [
    ("bar_magnet","Magnetic field lines outside a bar magnet go from:",
     "North pole to South pole",["S to N","N to N","Randomly"]),
    ("attraction","Which poles of two magnets attract each other?",
     "Unlike poles (N-S or S-N)",["Like poles (N-N)","Like poles (S-S)","All poles"]),
    ("repulsion","Which poles of two magnets repel each other?",
     "Like poles (N-N or S-S)",["Unlike poles","N and S always","None"]),
    ("compass","A compass needle always points toward:",
     "Geographic North (magnetic north pole of Earth)",
     ["South","East","The nearest magnet"]),
    ("bar_magnet","The magnetic force is strongest at:",
     "The poles of the magnet",["The centre","The sides","Uniformly everywhere"]),
    ("attraction","Which of these materials is attracted to a magnet?",
     "Iron (ferromagnetic)",["Copper","Aluminum","Wood"]),
    ("bar_magnet","If a bar magnet is cut in half, each half:",
     "Becomes a complete magnet with N and S poles",
     ["Loses its magnetism","Has only N pole","Has only S pole"]),
    ("compass","The Earth behaves like a giant magnet because:",
     "The molten iron core generates a magnetic field",
     ["The crust is all iron","The atmosphere is magnetic","The oceans conduct electricity"]),
    ("repulsion","Electromagnets are made by:",
     "Passing electric current through a coil of wire around an iron core",
     ["Heating iron","Cooling iron rapidly","Rubbing iron with silk"]),
    ("bar_magnet","Which of these is a permanent magnet material?",
     "Neodymium (rare earth metal)",["Copper","Plastic","Rubber"]),
    ("compass","The Aurora Borealis (Northern Lights) is caused by:",
     "Charged particles from Sun interacting with Earth's magnetic field",
     ["Lightning storms","Reflection from ice","Volcanic gases"]),
    ("attraction","Magnetic induction is when:",
     "A non-magnetised iron object becomes temporarily magnetised near a magnet",
     ["A magnet repels iron","Current creates heat","Poles switch"]),
    ("bar_magnet","Lodestone is:",
     "A naturally occurring magnetic mineral (magnetite)",
     ["A type of electricity","A non-magnetic rock","A synthetic magnet"]),
    ("compass","Which direction does a compass NOT directly measure?",
     "Altitude (height)",["North","South","East"]),
    ("repulsion","MRI machines in hospitals use:",
     "Strong electromagnets",["Permanent bar magnets","Compass needles","Radio waves alone"]),
]

def gen_magnetism(n=QPT):
    n=min(n,len(MAGNET_QA))
    print(f"[Magnetism] {n} questions...")
    for i,(scene,qtext,correct,wrongs) in enumerate(MAGNET_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_magnet(scene); url=upload_pil(img,f"magnet_{i}")
        g=random.choice([5,6,7,8]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Magnetism","Magnetic Properties",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  magnet_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 7. MEASUREMENT & UNITS
# ══════════════════════════════════════════════════════════════════════════════

def draw_measurement(tool):
    img, draw = canvas(440, 320, "#FAFAFA")
    draw.text((20,12), f"Measurement: {tool}", fill="#2C3E50", font=FONT_LG)

    if tool == "ruler":
        # Ruler with cm markings
        draw.rectangle([40,120,400,180], fill="#F5DEB3", outline="#8B6914", width=2)
        for cm in range(0, 37):
            x = 40 + cm * 10
            h = 25 if cm % 5 == 0 else 15
            draw.line([(x, 120),(x, 120+h)], fill="#333", width=2 if cm%5==0 else 1)
            if cm % 5 == 0:
                draw.text((x-4, 148), str(cm//10) if cm>0 else "0", fill="#333", font=FONT_SM)
        draw.text((160, 185), "Ruler — measures LENGTH (cm/mm)", fill="#2C3E50", font=FONT_MD)

    elif tool == "weighing_scale":
        # Simple balance scale
        draw.line([(220,60),(220,140)], fill="#7F8C8D", width=4)
        draw.line([(100,140),(340,140)], fill="#7F8C8D", width=4)
        # Pans
        draw.arc([80,140,180,180], 0, 180, fill="#3498DB", width=3)
        draw.arc([280,140,380,180], 0, 180, fill="#3498DB", width=3)
        draw.text((100,185), "Weighing Scale", fill="#2C3E50", font=FONT_MD)
        draw.text((60,230), "Measures MASS / WEIGHT (kg/g)", fill="#2C3E50", font=FONT_MD)

    elif tool == "thermometer":
        # Thermometer
        draw.rectangle([210,50,230,270], fill="white", outline="#888", width=2)
        draw.rectangle([213,180,227,270], fill="#E74C3C")
        draw.ellipse([203,258,237,292], fill="#E74C3C")
        for t, y in [(-10,250),(0,230),(10,210),(20,190),(30,170),(40,150),(100,70)]:
            draw.line([(230,y),(242,y)], fill="#333", width=1)
            draw.text((244,y-8), f"{t}°C", fill="#333", font=FONT_SM)
        draw.text((100,250), "Thermometer — measures TEMPERATURE (°C)", fill="#2C3E50", font=FONT_SM)

    elif tool == "measuring_cylinder":
        # Graduated cylinder
        draw.rectangle([175,60,265,280], fill="#D6EAF8", outline="#3498DB", width=2)
        draw.ellipse([175,270,265,295], fill="#3498DB")
        draw.ellipse([175,50,265,75], outline="#3498DB", width=2)
        # Graduations
        for v, y in [(100,70),(80,110),(60,150),(40,190),(20,230),(0,270)]:
            draw.line([(265,y),(275,y)], fill="#333", width=2)
            draw.text((278,y-8), f"{v} mL", fill="#333", font=FONT_SM)
        # Water level
        draw.rectangle([177,180,263,278], fill="#3498DB")
        draw.text((60,300),"Measuring Cylinder — measures VOLUME (mL/L)",fill="#2C3E50",font=FONT_SM)

    return img

MEASURE_QA = [
    ("ruler","What instrument is used to measure the length of an object?",
     "Ruler / Metre scale",["Thermometer","Balance","Graduated cylinder"]),
    ("weighing_scale","The SI unit of mass is:",
     "Kilogram (kg)",["Newton (N)","Litre (L)","Metre (m)"]),
    ("thermometer","A thermometer is used to measure:",
     "Temperature",["Mass","Length","Volume"]),
    ("measuring_cylinder","A measuring cylinder is used to measure:",
     "Volume of a liquid",["Mass","Temperature","Length"]),
    ("ruler","1 kilometre = _____ metres:",
     "1000 m",["100 m","10 m","10,000 m"]),
    ("weighing_scale","The difference between mass and weight is:",
     "Mass is amount of matter (kg); weight is gravitational force (N)",
     ["They are identical","Mass is force, weight is matter","Mass is in Newtons"]),
    ("thermometer","The Celsius scale sets water's boiling point at:",
     "100°C",["0°C","212°C","373°C"]),
    ("measuring_cylinder","1 litre = _____ millilitres:",
     "1000 mL",["100 mL","10 mL","500 mL"]),
    ("ruler","The smallest division on a standard ruler is:",
     "1 mm (millimetre)",["1 cm","1 m","1 km"]),
    ("weighing_scale","On a beam balance, the object balances when:",
     "Masses on both pans are equal",
     ["The heavier side goes down","The lighter side goes down","Spring stretches to same length"]),
    ("thermometer","Normal human body temperature is approximately:",
     "37°C",["36°C","39°C","40°C"]),
    ("measuring_cylinder","The curved upper surface of a liquid in a cylinder is called:",
     "Meniscus",["Surface tension","Capillarity","Convex surface"]),
    ("ruler","A micrometre (μm) equals:",
     "0.000001 m (10⁻⁶ m)",["0.001 m","0.01 m","0.1 m"]),
    ("measuring_cylinder","To read a measuring cylinder accurately, the eye should be:",
     "Level with the bottom of the meniscus",
     ["Above the cylinder","Below the cylinder","Looking at an angle"]),
    ("weighing_scale","A spring balance measures:",
     "Weight (force due to gravity, in Newtons)",
     ["Mass in kg","Volume in mL","Temperature in °C"]),
]

def gen_measurement(n=QPT):
    n=min(n,len(MEASURE_QA))
    print(f"[Measurement & Units] {n} questions...")
    tools_cycle=["ruler","weighing_scale","thermometer","measuring_cylinder"]
    for i,(tool,qtext,correct,wrongs) in enumerate(MEASURE_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_measurement(tool); url=upload_pil(img,f"meas_{i}")
        g=random.choice([4,5,6,7]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Measurement","Units and Instruments",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  meas_{i} ({tool})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*60)
    print("OlympiadReady — Physics & Earth Science Generator Batch 3")
    print("="*60)
    print()

    gen_circuits(QPT)
    gen_optics(QPT)
    gen_force_motion(QPT)
    gen_solar_system(QPT)
    gen_landforms(QPT)
    gen_magnetism(QPT)
    gen_measurement(QPT)

    print("="*60)
    print(f"DONE — Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}")
    print("="*60)
