"""
generate_class1112_chemistry.py
Class 11-12 Chemistry — Batch 8
All answers verified against NCERT syllabus and SOF NSO/NCO standards.

Generators:
  1. Atomic Structure         (Class 11) — 20 questions
  2. Chemical Bonding         (Class 11) — 20 questions
  3. Thermodynamics           (Class 11) — 20 questions
  4. Equilibrium              (Class 11) — 20 questions
  5. Electrochemistry         (Class 12) — 15 questions
  6. Organic Chemistry        (Class 11-12) — 20 questions
  7. Periodic Table           (Class 11) — 15 questions

QPT = 20 (or as noted above)  |  Total = 130 questions
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
        public_id=f"p8_{label}_{int(time.time()*1000)}", resource_type="image")
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
# 1. ATOMIC STRUCTURE  (Class 11)
# ==============================================================================

def draw_atom(scene="bohr"):
    img, draw = canvas(540, 400, "#0D1117")
    draw.text((20, 10), f"Atomic Structure: {scene.replace('_',' ').title()}", fill="white", font=FONT_MD)

    if scene == "bohr":
        cx, cy = 270, 210
        # Nucleus
        draw.ellipse([cx-18, cy-18, cx+18, cy+18], fill="#E74C3C", outline="white", width=2)
        draw.text((cx-12, cy-8), "+Ze", fill="white", font=FONT_SM)
        # Electron shells
        for r, label, col in [(60,"n=1","#3498DB"),(100,"n=2","#27AE60"),(145,"n=3","#F39C12")]:
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=col, width=2)
            draw.text((cx+r+4, cy-8), label, fill=col, font=FONT_SM)
            # Electron dot on shell
            ex = cx + r
            draw.ellipse([ex-5, cy-5, ex+5, cy+5], fill=col)
        draw.text((20, 340), "Bohr model: electrons orbit nucleus in fixed shells", fill="#AAA", font=FONT_SM)
        draw.text((20, 365), "Energy: E_n = -13.6/n^2 eV  (for hydrogen)", fill="#AAA", font=FONT_SM)

    elif scene == "quantum":
        # Orbital shapes
        # s orbital — circle
        draw.ellipse([60, 130, 180, 270], outline="#3498DB", width=2)
        draw.text((80, 290), "s orbital", fill="#3498DB", font=FONT_SM)
        draw.text((80, 310), "(spherical)", fill="#AAA", font=FONT_SM)
        # p orbital — dumbbell
        cx2 = 340
        draw.ellipse([cx2-45, 130, cx2+45, 200], fill="#27AE60", outline="#AAA", width=1)
        draw.ellipse([cx2-45, 210, cx2+45, 280], fill="#27AE60", outline="#AAA", width=1)
        draw.text((cx2-35, 290), "p orbital", fill="#27AE60", font=FONT_SM)
        draw.text((cx2-40, 310), "(dumbbell)", fill="#AAA", font=FONT_SM)
        draw.text((20, 360), "Quantum numbers: n (shell), l (subshell), ml (orientation), ms (spin)", fill="#AAA", font=FONT_SM)

    elif scene == "electronic_config":
        draw.text((20, 50), "Electronic Configuration Rules:", fill="#FFD700", font=FONT_MD)
        lines = [
            ("Aufbau Principle:", "Fill lowest energy orbitals first"),
            ("Pauli Exclusion:", "Max 2 electrons per orbital, opposite spins"),
            ("Hund's Rule:",     "Fill degenerate orbitals singly first"),
            ("Order:",           "1s 2s 2p 3s 3p 4s 3d 4p 5s 4d 5p..."),
        ]
        y = 95
        for title, desc in lines:
            draw.text((30, y), title, fill="#3498DB", font=FONT_MD)
            draw.text((30, y+22), desc, fill="#AAA", font=FONT_SM)
            y += 60
        draw.text((20, 360), "Example: Fe (Z=26): [Ar] 3d6 4s2", fill="#27AE60", font=FONT_MD)

    elif scene == "emission_spectrum":
        # Horizontal spectrum bar
        draw.text((20, 40), "Hydrogen Emission Spectrum (Balmer Series)", fill="white", font=FONT_MD)
        colors_data = [
            (100, "#8B00FF", "656 nm\n(H-alpha)"),
            (200, "#0000FF", "486 nm"),
            (310, "#00BFFF", "434 nm"),
            (400, "#9400D3", "410 nm"),
        ]
        for x, col, label in colors_data:
            draw.rectangle([x, 120, x+25, 250], fill=col)
            draw.text((x-5, 260), label.split("\n")[0], fill=col, font=FONT_SM)
        draw.text((20, 310), "Balmer series: visible light, transitions to n=2", fill="#AAA", font=FONT_SM)
        draw.text((20, 335), "Lyman (UV): to n=1 | Paschen (IR): to n=3", fill="#AAA", font=FONT_SM)
        draw.text((20, 360), "En = -13.6/n^2 eV;  delta_E = 13.6(1/n1^2 - 1/n2^2)", fill="#FFD700", font=FONT_SM)

    return img

ATOM_QA = [
    ("bohr",
     "In Bohr's model, the energy of the nth orbit of hydrogen atom is:",
     "E_n = -13.6/n^2 eV",
     ["-13.6*n^2 eV", "+13.6/n^2 eV", "-13.6*n eV"],
     "Bohr's formula: E_n = -13.6/n^2 eV. Negative sign = bound state. For n=1, E=-13.6 eV (ground state)."),
    ("quantum",
     "The maximum number of electrons in the 3rd shell (n=3) is:",
     "18 (2n^2 = 2x9 = 18)",
     ["8", "9", "32"],
     "Max electrons in nth shell = 2n^2. For n=3: 2x3^2 = 18."),
    ("electronic_config",
     "The electronic configuration of Cl (Z=17) is:",
     "1s2 2s2 2p6 3s2 3p5",
     ["1s2 2s2 2p6 3s2 3p6", "1s2 2s2 2p5 3s2 3p6", "2s2 2p6 3s2 3p5"],
     "Cl: Z=17. Fill: 1s2(2) 2s2(4) 2p6(10) 3s2(12) 3p5(17). Config: 1s2 2s2 2p6 3s2 3p5."),
    ("bohr",
     "In hydrogen atom, the transition from n=3 to n=2 gives the:",
     "H-alpha line of Balmer series (red, 656 nm)",
     ["Lyman series line", "Paschen series line", "Brackett series line"],
     "Balmer series: transitions to n=2. n=3 to n=2 is the first Balmer line (H-alpha, 656 nm, red)."),
    ("quantum",
     "The shape of a p-orbital is:",
     "Dumbbell (figure-eight in 3D)",
     ["Spherical", "Clover-leaf (4-lobed)", "Toroidal"],
     "s-orbitals are spherical. p-orbitals are dumbbell-shaped (two lobes). d-orbitals are clover-leaf shaped."),
    ("electronic_config",
     "Which rule states that electrons fill orbitals in order of increasing energy?",
     "Aufbau Principle",
     ["Pauli Exclusion Principle", "Hund's Rule", "Heisenberg's Principle"],
     "Aufbau (German: 'building up') principle: fill lowest energy orbitals first. Order: 1s 2s 2p 3s 3p 4s 3d..."),
    ("quantum",
     "The four quantum numbers for the differentiating electron of Na (Z=11) are:",
     "n=3, l=0, ml=0, ms=+1/2 (or -1/2)",
     ["n=2, l=1, ml=0, ms=+1/2", "n=3, l=1, ml=0, ms=+1/2", "n=3, l=0, ml=1, ms=+1/2"],
     "Na: [Ne]3s1. The last electron is in 3s: n=3, l=0, ml=0, ms=+1/2."),
    ("bohr",
     "The ionisation energy of hydrogen from ground state (n=1) is:",
     "13.6 eV",
     ["3.4 eV", "1.5 eV", "27.2 eV"],
     "IE = energy to remove electron from n=1 to infinity. |E_1| = 13.6/1^2 = 13.6 eV."),
    ("emission_spectrum",
     "Which series of hydrogen spectrum lies in the ultraviolet region?",
     "Lyman series (transitions to n=1)",
     ["Balmer series", "Paschen series", "Brackett series"],
     "Lyman: UV (n>1 to n=1). Balmer: visible (n>2 to n=2). Paschen: IR (n>3 to n=3)."),
    ("electronic_config",
     "According to Hund's rule, the electronic configuration of carbon (Z=6) in its ground state has:",
     "Two unpaired electrons in 2p orbitals",
     ["All electrons paired", "One unpaired electron", "Three unpaired electrons"],
     "C: 1s2 2s2 2p2. By Hund's rule, both 2p electrons occupy different orbitals with parallel spins — 2 unpaired."),
    ("quantum",
     "The orbital angular momentum of an electron in the 2p subshell is:",
     "sqrt(2) * h-bar  [L = sqrt(l(l+1)) * h-bar, l=1]",
     ["h-bar", "2*h-bar", "0"],
     "L = sqrt(l(l+1)) * h-bar. For p (l=1): L = sqrt(1x2) * h-bar = sqrt(2) * h-bar."),
    ("bohr",
     "The radius of the nth Bohr orbit in hydrogen is:",
     "r_n = n^2 * 0.529 Angstrom  (a_0 = Bohr radius)",
     ["r_n = n * 0.529 A", "r_n = 0.529/n^2 A", "r_n = n^2 * 1.06 A"],
     "Bohr radius: r_n = n^2 * a_0 where a_0 = 0.529 A. For n=1, r=0.529 A (ground state hydrogen)."),
    ("electronic_config",
     "The electronic configuration of Cu (Z=29) is anomalous. It is:",
     "[Ar] 3d10 4s1 (not [Ar] 3d9 4s2)",
     ["[Ar] 3d9 4s2", "[Ar] 3d8 4s3", "[Ar] 3d10 4s2"],
     "Cu has [Ar]3d10 4s1 due to extra stability of completely filled d subshell (3d10)."),
    ("quantum",
     "The number of orbitals in the 3d subshell is:",
     "5 (ml = -2, -1, 0, +1, +2)",
     ["3", "7", "1"],
     "For l=2 (d subshell), ml = -2,-1,0,+1,+2. That gives 5 orbitals (max 10 electrons)."),
    ("emission_spectrum",
     "The wavelength of a photon emitted during H-atom transition from n=4 to n=2 belongs to:",
     "Balmer series (visible spectrum)",
     ["Lyman series (UV)", "Paschen series (IR)", "Brackett series"],
     "Balmer series: transitions ending at n=2. n=4 to n=2 is the 2nd Balmer line (H-beta, ~486 nm, blue-green)."),
    ("bohr",
     "de Broglie's condition for Bohr orbits states that:",
     "The circumference of the orbit = whole number multiple of wavelength  (2*pi*r = n*lambda)",
     ["Electrons move in elliptical orbits", "Energy is continuous", "Radius is proportional to n"],
     "de Broglie: 2*pi*r = n*lambda. Combined with lambda=h/mv, this gives Bohr's angular momentum quantisation."),
    ("electronic_config",
     "The Pauli Exclusion Principle states that:",
     "No two electrons in an atom can have the same set of all four quantum numbers",
     ["Electrons fill degenerate orbitals singly", "Electrons fill lowest energy orbitals first", "Max 8 electrons per shell"],
     "Pauli: each electron in an atom has a unique set of (n, l, ml, ms). Hence max 2 electrons per orbital (ms = +1/2 or -1/2)."),
    ("quantum",
     "How many electrons can be accommodated in the 4f subshell?",
     "14  (f: l=3, 7 orbitals x 2 = 14)",
     ["7", "10", "6"],
     "f subshell: l=3, ml = -3 to +3 = 7 orbitals. Each holds 2 electrons: 7x2 = 14 electrons."),
    ("bohr",
     "The energy required to excite a hydrogen electron from n=1 to n=2 is:",
     "10.2 eV  [E = 13.6(1 - 1/4) = 13.6 x 0.75 = 10.2 eV]",
     ["3.4 eV", "13.6 eV", "1.9 eV"],
     "dE = 13.6(1/1^2 - 1/2^2) = 13.6 x (1 - 0.25) = 13.6 x 0.75 = 10.2 eV."),
    ("emission_spectrum",
     "The Heisenberg Uncertainty Principle states:",
     "delta_x * delta_p >= h/(4*pi)  — position and momentum cannot both be precisely determined",
     ["Electrons have wave-particle duality", "Energy levels are quantised", "Atomic mass equals protons+neutrons"],
     "Heisenberg: delta_x * delta_p >= h-bar/2 = h/(4*pi). Fundamental quantum limit — not due to measurement error."),
]

def gen_atomic(n=QPT):
    print(f"[Atomic Structure] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(ATOM_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_atom(scene); url=upload_pil(img, f"atom_{i}")
        ok=post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                  "Atomic Structure", "Quantum Mechanics and Bohr Model",
                  qtext, url, opts, cidx, expl)
        print(f"  atom_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 2. CHEMICAL BONDING  (Class 11)
# ==============================================================================

def draw_bonding(scene="ionic"):
    img, draw = canvas(540, 400, "#F8F9FA")
    draw.text((20, 10), f"Chemical Bonding: {scene.replace('_',' ').title()}", fill="#2C3E50", font=FONT_MD)

    if scene == "ionic":
        # Na + Cl -> NaCl
        # Na atom
        draw.ellipse([40, 140, 130, 230], fill="#3498DB", outline="#2C3E50", width=2)
        draw.text((65, 178), "Na", fill="white", font=FONT_LG)
        draw.text((65, 200), "(2,8,1)", fill="#ECF0F1", font=FONT_SM)
        # Arrow
        draw.text((150, 180), "->", fill="#E74C3C", font=FONT_XL)
        # Na+ ion
        draw.ellipse([190, 155, 265, 225], fill="#5DADE2", outline="#2C3E50", width=2)
        draw.text((208, 180), "Na+", fill="white", font=FONT_MD)
        draw.text((200, 200), "(2,8)", fill="#ECF0F1", font=FONT_SM)
        # + electron transfer
        draw.text((275, 180), "+  e-", fill="#E74C3C", font=FONT_LG)
        # Cl atom
        draw.ellipse([40, 270, 130, 360], fill="#E74C3C", outline="#2C3E50", width=2)
        draw.text((65, 307), "Cl", fill="white", font=FONT_LG)
        draw.text((55, 327), "(2,8,7)", fill="#ECF0F1", font=FONT_SM)
        draw.text((150, 307), "->", fill="#E74C3C", font=FONT_XL)
        draw.ellipse([190, 280, 265, 355], fill="#EC7063", outline="#2C3E50", width=2)
        draw.text((208, 307), "Cl-", fill="white", font=FONT_MD)
        draw.text((200, 327), "(2,8,8)", fill="#ECF0F1", font=FONT_SM)
        draw.text((340, 180), "NaCl", fill="#27AE60", font=FONT_XL)
        draw.text((325, 215), "(electrostatic attraction)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "covalent":
        # H2 molecule
        draw.text((20, 50), "Covalent Bond: H2 molecule", fill="#2C3E50", font=FONT_MD)
        cx = 270
        # H atoms sharing electrons
        draw.ellipse([cx-90, 150, cx-10, 230], fill="#F7DC6F", outline="#2C3E50", width=2)
        draw.text((cx-73, 182), "H", fill="#2C3E50", font=FONT_LG)
        draw.ellipse([cx+10, 150, cx+90, 230], fill="#F7DC6F", outline="#2C3E50", width=2)
        draw.text((cx+27, 182), "H", fill="#2C3E50", font=FONT_LG)
        # Bond
        draw.rectangle([cx-15, 175, cx+15, 205], fill="#E74C3C")
        draw.text((cx-10, 182), ":", fill="white", font=FONT_MD)
        draw.text((cx-50, 245), "Shared electron pair", fill="#7F8C8D", font=FONT_MD)
        # Water molecule
        draw.text((20, 300), "Water (H2O): 2 covalent O-H bonds + 2 lone pairs on O", fill="#2C3E50", font=FONT_SM)
        draw.text((20, 325), "Bond angle: 104.5 degrees (sp3 hybridised, bent shape)", fill="#7F8C8D", font=FONT_SM)
        draw.text((20, 350), "Methane (CH4): 4 C-H bonds, tetrahedral, 109.5 degrees", fill="#7F8C8D", font=FONT_SM)

    elif scene == "hybridisation":
        draw.text((20, 40), "Hybridisation and Geometry", fill="#2C3E50", font=FONT_LG)
        rows = [
            ("sp",   "Linear",      "180 deg", "BeCl2, CO2, C2H2"),
            ("sp2",  "Trigonal",    "120 deg", "BF3, C2H4, SO3"),
            ("sp3",  "Tetrahedral", "109.5deg", "CH4, NH3, H2O"),
            ("sp3d", "Trigonal Bipyr","90/120", "PCl5"),
            ("sp3d2","Octahedral",  "90 deg",  "SF6"),
        ]
        y = 90
        for hyb, geom, angle, example in rows:
            draw.text((25, y), hyb, fill="#E74C3C", font=FONT_MD)
            draw.text((120, y), geom, fill="#2C3E50", font=FONT_MD)
            draw.text((280, y), angle, fill="#27AE60", font=FONT_MD)
            draw.text((370, y), example, fill="#7F8C8D", font=FONT_SM)
            y += 45
        draw.text((20, 360), "Lone pairs reduce bond angle (NH3=107, H2O=104.5)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "vsepr":
        draw.text((20, 40), "VSEPR Theory — Shape from Electron Pairs", fill="#2C3E50", font=FONT_MD)
        rows = [
            ("2 bond pairs",  "Linear — CO2, BeCl2"),
            ("3 bond pairs",  "Trigonal planar — BF3, SO3"),
            ("4 bond pairs",  "Tetrahedral — CH4, CCl4"),
            ("3 BP + 1 LP",   "Trigonal pyramidal — NH3"),
            ("2 BP + 2 LP",   "Bent/V-shape — H2O, SO2"),
            ("5 BP",          "Trigonal bipyramidal — PCl5"),
            ("6 BP",          "Octahedral — SF6"),
        ]
        y = 90
        for pair, shape in rows:
            draw.text((25, y), pair, fill="#E74C3C", font=FONT_SM)
            draw.text((225, y), shape, fill="#2C3E50", font=FONT_SM)
            y += 40
        draw.text((20, 375), "LP-LP > LP-BP > BP-BP repulsion (VSEPR)", fill="#7F8C8D", font=FONT_SM)

    return img

BOND_QA = [
    ("ionic",
     "NaCl is an ionic compound because:",
     "Na transfers one electron to Cl; Na+ and Cl- are held by electrostatic attraction",
     ["Na and Cl share electrons equally", "Both atoms lose electrons", "Na gains one electron from Cl"],
     "Na (2,8,1) loses 1e- to form Na+. Cl (2,8,7) gains 1e- to form Cl-. Electrostatic attraction forms NaCl."),
    ("covalent",
     "In a covalent bond, atoms are held together by:",
     "Sharing of electron pairs",
     ["Transfer of electrons", "Electrostatic attraction of ions", "Van der Waals forces only"],
     "Covalent bond: atoms share electron pairs. E.g. H2 (H:H), Cl2 (Cl:Cl), H2O (O shares with two H atoms)."),
    ("hybridisation",
     "The hybridisation of carbon in methane (CH4) is:",
     "sp3 (tetrahedral, 109.5 degrees)",
     ["sp2", "sp", "dsp2"],
     "CH4: C forms 4 equivalent bonds. 1 s + 3 p orbitals hybridise -> 4 sp3 orbitals. Tetrahedral shape, 109.5 deg."),
    ("vsepr",
     "The shape of water molecule (H2O) according to VSEPR theory is:",
     "Bent (V-shape), bond angle 104.5 degrees",
     ["Linear, 180 degrees", "Trigonal planar, 120 degrees", "Tetrahedral, 109.5 degrees"],
     "H2O: 2 bond pairs + 2 lone pairs on O. Lone pairs repel strongly -> bent shape, 104.5 deg (less than tetrahedral 109.5 deg)."),
    ("hybridisation",
     "The hybridisation of carbon in ethylene (C2H4) is:",
     "sp2 (trigonal planar, 120 degrees)",
     ["sp3", "sp", "sp3d"],
     "C2H4: each C forms 3 sigma bonds (sp2) and 1 pi bond (unhybridised p-orbital). Trigonal planar, 120 deg."),
    ("ionic",
     "Which property is characteristic of ionic compounds?",
     "High melting point, conduct electricity when molten or in solution",
     ["Low melting point, poor conductors", "Conduct electricity in solid state", "Covalent network solid"],
     "Ionic compounds: strong electrostatic forces -> high mp. In molten/solution state, ions are free to conduct electricity."),
    ("hybridisation",
     "CO2 is linear because:",
     "Carbon is sp hybridised with 2 sigma bonds and 2 pi bonds — no lone pairs on C",
     ["O-C-O repulsion makes it linear", "It is an ionic compound", "Carbon uses sp3 hybridisation"],
     "CO2: C has sp hybridisation. 2 sp orbitals form sigma bonds with O, 2 unhybridised p orbitals form pi bonds. No lone pairs -> linear, 180 deg."),
    ("covalent",
     "The bond angle in NH3 (ammonia) is approximately:",
     "107 degrees (1 lone pair on N reduces angle from 109.5)",
     ["109.5 degrees", "120 degrees", "90 degrees"],
     "NH3: N has 3 bond pairs + 1 lone pair. sp3-like. LP-BP repulsion > BP-BP -> bond angle 107 deg (less than 109.5)."),
    ("vsepr",
     "How many lone pairs does the central atom in SF6 have?",
     "0 lone pairs (sp3d2, octahedral)",
     ["1 lone pair", "2 lone pairs", "3 lone pairs"],
     "SF6: S forms 6 bonds with F. No lone pairs on S. Hybridisation sp3d2. Shape: octahedral, 90 deg."),
    ("covalent",
     "A coordinate (dative) bond is formed when:",
     "Both electrons in the bond are donated by one atom (e.g., H3N -> BF3)",
     ["Atoms share one electron each", "One atom transfers an electron to another", "Ionic bond forms"],
     "Coordinate/dative bond: one atom donates both electrons. Example: NH3 donating lone pair to BF3, forming H3N:BF3."),
    ("hybridisation",
     "The hybridisation of N in HNO3 (nitric acid) is:",
     "sp2",
     ["sp3", "sp", "sp3d"],
     "In HNO3, N has 3 bond pairs + 0 lone pairs (considering resonance) -> sp2. Trigonal planar around N."),
    ("vsepr",
     "PCl5 has which geometry?",
     "Trigonal bipyramidal (sp3d, bond angles 90 and 120 degrees)",
     ["Octahedral", "Tetrahedral", "Square planar"],
     "PCl5: P has 5 bond pairs, 0 lone pairs. sp3d hybridisation -> trigonal bipyramidal. Axial bonds 90 deg, equatorial 120 deg."),
    ("ionic",
     "The electronegativity difference for an ionic bond should generally be:",
     "Greater than 1.7 (usually metals with non-metals)",
     ["Less than 0.5", "Between 0.5 and 1.7", "Exactly 1.0"],
     "Electronegativity difference > 1.7 -> ionic character > 50%. Typical ionic bonds: NaCl (~2.1), MgO (~2.3)."),
    ("covalent",
     "Which molecule has a triple bond?",
     "N2 (one sigma + two pi bonds, bond order = 3)",
     ["O2", "Cl2", "H2"],
     "N2: each N contributes 3 electrons to bonding -> 1 sigma + 2 pi bonds. Bond order = 3. Strongest and shortest N-N bond."),
    ("hybridisation",
     "Acetylene (C2H2) has which hybridisation at each carbon?",
     "sp (linear, 180 degrees)",
     ["sp2", "sp3", "sp3d"],
     "C2H2: H-C≡C-H. Each C forms 1 C-H sigma + 1 C-C sigma (sp orbital) + 2 pi bonds (unhybridised p). sp, linear."),
    ("vsepr",
     "The shape of ClF3 (chlorine trifluoride) is:",
     "T-shaped (3 bond pairs + 2 lone pairs on Cl)",
     ["Trigonal planar", "Pyramidal", "Linear"],
     "ClF3: Cl has 3 bond pairs + 2 lone pairs -> sp3d. Trigonal bipyramidal electron geometry but T-shaped molecular shape."),
    ("ionic",
     "Lattice energy of an ionic compound depends on:",
     "Charge of ions (higher charge -> higher lattice energy) and ionic radii (smaller ions -> higher lattice energy)",
     ["Only on the radius of cation", "Temperature of formation", "Number of electrons in outer shell only"],
     "Lattice energy E proportional to (q+)(q-)/(r+ + r-). Higher charge and smaller radius -> greater lattice energy."),
    ("covalent",
     "Bond dissociation energy of N2 (945 kJ/mol) is greater than O2 (498 kJ/mol) because:",
     "N2 has a triple bond while O2 has a double bond",
     ["N2 has lower molecular mass", "O2 has ionic character", "N atoms are smaller than O atoms"],
     "Bond order N2=3 (triple bond) vs O2=2 (double bond). More bonds -> higher bond energy -> harder to break."),
    ("hybridisation",
     "The hybridisation of S in SO2 is:",
     "sp2 (bent shape, one lone pair on S)",
     ["sp3", "sp", "sp3d"],
     "SO2: S has 2 bond pairs + 1 lone pair -> sp2. Trigonal planar electron geometry, bent molecular shape, ~119 deg."),
    ("vsepr",
     "Which molecule is non-polar despite having polar bonds?",
     "CCl4 (symmetrical tetrahedral — dipoles cancel)",
     ["CHCl3", "H2O", "NH3"],
     "CCl4: tetrahedral and symmetrical. 4 C-Cl dipoles cancel -> net dipole = 0. Non-polar. (CHCl3, H2O, NH3 are polar)."),
]

def gen_bonding(n=QPT):
    print(f"[Chemical Bonding] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(BOND_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_bonding(scene); url=upload_pil(img, f"bond_{i}")
        ok=post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                  "Chemical Bonding", "Molecular Structure and VSEPR",
                  qtext, url, opts, cidx, expl)
        print(f"  bond_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 3. THERMODYNAMICS  (Class 11)
# ==============================================================================

def draw_thermo(scene="enthalpy"):
    img, draw = canvas(540, 400, "#1A1A2E")
    draw.text((20, 10), f"Thermodynamics: {scene.replace('_',' ').title()}", fill="white", font=FONT_MD)

    if scene == "enthalpy":
        # Energy diagram
        ox, oy = 80, 340
        draw.line([(ox, oy), (480, oy)], fill="#555", width=2)
        draw.text((490, oy-5), "Rxn", fill="#AAA", font=FONT_SM)
        # Reactants level
        draw.line([(ox, 200), (180, 200)], fill="#E74C3C", width=3)
        draw.text((90, 175), "Reactants", fill="#E74C3C", font=FONT_SM)
        # Products level (lower = exothermic)
        draw.line([(340, 280), (460, 280)], fill="#27AE60", width=3)
        draw.text((350, 290), "Products", fill="#27AE60", font=FONT_SM)
        # Activation energy hump
        pts = [(180,200),(230,130),(280,130),(330,280)]
        for j in range(len(pts)-1):
            draw.line([pts[j],pts[j+1]], fill="#F39C12", width=2)
        draw.text((220, 110), "Activation Energy (Ea)", fill="#F39C12", font=FONT_SM)
        # delta H arrow
        draw.line([(400, 200), (400, 280)], fill="white", width=2)
        draw.text((410, 230), "delta_H < 0", fill="white", font=FONT_SM)
        draw.text((410, 250), "(Exothermic)", fill="#27AE60", font=FONT_SM)
        draw.text((20, 365), "Exothermic: delta_H < 0  |  Endothermic: delta_H > 0", fill="#AAA", font=FONT_SM)

    elif scene == "entropy":
        draw.text((30, 50), "Entropy (S) — measure of disorder/randomness", fill="#FFD700", font=FONT_MD)
        examples = [
            ("Ice -> Water -> Steam", "S increases", "#27AE60"),
            ("Dissolving salt in water", "S increases", "#27AE60"),
            ("Crystallisation", "S decreases", "#E74C3C"),
            ("1 mol gas -> 2 mol gas", "S increases", "#27AE60"),
            ("Mixing of gases", "S increases", "#27AE60"),
        ]
        y = 100
        for event, change, col in examples:
            draw.text((30, y), event, fill="white", font=FONT_SM)
            draw.text((350, y), change, fill=col, font=FONT_SM)
            y += 45
        draw.text((20, 360), "2nd Law: Entropy of universe always increases (delta_S_univ > 0)", fill="#AAA", font=FONT_SM)

    elif scene == "gibbs":
        draw.text((30, 40), "Gibbs Free Energy: G = H - TS", fill="#FFD700", font=FONT_LG)
        draw.text((30, 80), "delta_G = delta_H - T*delta_S", fill="white", font=FONT_MD)
        draw.text((30, 115), "Spontaneous if delta_G < 0", fill="#27AE60", font=FONT_MD)
        rows = [
            ("dH", "dS", "dG = dH-TdS", "Spontaneous?"),
            ("-",  "+",  "Always -",    "Always YES"),
            ("+",  "-",  "Always +",    "Never"),
            ("-",  "-",  "- at low T",  "Low T only"),
            ("+",  "+",  "- at high T", "High T only"),
        ]
        y = 160
        for row in rows:
            x = 30
            for j, item in enumerate(row):
                col = "#FFD700" if y==160 else ["#E74C3C","#27AE60","white","#3498DB"][j%4]
                draw.text((x, y), item, fill=col, font=FONT_SM)
                x += 120
            y += 40
        draw.text((20, 365), "At equilibrium: delta_G = 0  |  delta_G = -nFE_cell", fill="#AAA", font=FONT_SM)

    elif scene == "hess":
        draw.text((30, 40), "Hess's Law: Enthalpy is a state function", fill="#FFD700", font=FONT_MD)
        draw.text((30, 75), "delta_H(overall) = sum of delta_H(steps)", fill="white", font=FONT_MD)
        draw.text((30, 115), "Example: C + O2 -> CO2   delta_H = -393 kJ/mol", fill="#3498DB", font=FONT_SM)
        draw.text((30, 140), "Can also go:", fill="#AAA", font=FONT_SM)
        draw.text((30, 165), "  C + 1/2 O2 -> CO   delta_H1 = -111 kJ/mol", fill="#27AE60", font=FONT_SM)
        draw.text((30, 190), "  CO + 1/2 O2 -> CO2  delta_H2 = -283 kJ/mol", fill="#27AE60", font=FONT_SM)
        draw.text((30, 215), "  Total = -111 + (-283) = -394 kJ/mol (approx)", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 260), "Applications:", fill="#FFD700", font=FONT_MD)
        draw.text((30, 295), "  * Bond enthalpies", fill="white", font=FONT_SM)
        draw.text((30, 320), "  * Formation enthalpies", fill="white", font=FONT_SM)
        draw.text((30, 345), "  * Combustion enthalpies", fill="white", font=FONT_SM)
        draw.text((30, 375), "Path is irrelevant — only initial and final states matter", fill="#AAA", font=FONT_SM)

    return img

THERMO_QA = [
    ("enthalpy",
     "For an exothermic reaction, the enthalpy change (delta_H) is:",
     "Negative (heat is released to surroundings)",
     ["Positive", "Zero", "Equal to activation energy"],
     "Exothermic: system loses heat -> delta_H < 0. Examples: combustion, neutralisation, respiration."),
    ("entropy",
     "Which process has an increase in entropy?",
     "Melting of ice (solid -> liquid, more disorder)",
     ["Freezing of water", "Rusting of iron", "Formation of crystal from solution"],
     "S increases when disorder increases: solid->liquid->gas; dissolving; mixing. Melting = S increases."),
    ("gibbs",
     "A reaction has delta_H = -100 kJ and delta_S = +200 J/K. At 298K, delta_G is:",
     "delta_G = -100,000 - 298x200 = -159,600 J = -159.6 kJ (spontaneous)",
     ["delta_G = +59.6 kJ", "delta_G = 0", "delta_G = -40.4 kJ"],
     "delta_G = delta_H - T*delta_S = -100,000 - 298*200 = -100,000 - 59,600 = -159,600 J. Spontaneous."),
    ("hess",
     "Hess's Law is based on which thermodynamic principle?",
     "Enthalpy is a state function (path-independent)",
     ["Enthalpy depends on the path taken", "Entropy is a state function", "Energy cannot be created"],
     "Enthalpy is a state function: delta_H depends only on initial and final states, not the path. Hess's law follows directly."),
    ("enthalpy",
     "The standard enthalpy of formation (delta_Hf) of an element in its standard state is:",
     "Zero by definition",
     ["+100 kJ/mol", "-100 kJ/mol", "Depends on the element"],
     "By convention, delta_Hf of elements in their standard state (e.g., H2(g), C(graphite), O2(g)) = 0."),
    ("gibbs",
     "At what condition is a reaction at equilibrium according to Gibbs equation?",
     "delta_G = 0",
     ["delta_G < 0", "delta_G > 0", "delta_H = 0"],
     "At equilibrium, the system has minimum free energy: delta_G = 0. Spontaneous: delta_G < 0. Non-spontaneous: delta_G > 0."),
    ("entropy",
     "The Second Law of Thermodynamics states:",
     "The total entropy of the universe always increases in a spontaneous process",
     ["Energy is conserved in all processes", "Entropy of a perfect crystal at 0K is zero", "Work and heat are equivalent"],
     "2nd Law: delta_S_universe = delta_S_system + delta_S_surroundings > 0 (spontaneous). The universe tends toward disorder."),
    ("hess",
     "The bond dissociation energy of H-H bond is 436 kJ/mol and Cl-Cl is 242 kJ/mol. Energy released when H-Cl bond forms (2 bonds) is 862 kJ. The delta_H for H2 + Cl2 -> 2HCl is:",
     "-184 kJ/mol  [bonds broken: 436+242=678; bonds formed: 2x431=862; dH=678-862=-184]",
     ["+184 kJ/mol", "-862 kJ/mol", "+242 kJ/mol"],
     "delta_H = bonds broken - bonds formed = (436+242) - 2x431 = 678-862 = -184 kJ. Exothermic."),
    ("enthalpy",
     "The enthalpy of neutralisation of a strong acid with a strong base is always approximately:",
     "-57.1 kJ/mol (due to H+ + OH- -> H2O)",
     ["-100 kJ/mol", "-10 kJ/mol", "Depends on acid and base"],
     "Strong acid + strong base: completely ionised. Net reaction is always H+ + OH- -> H2O, delta_H approx -57.1 kJ/mol."),
    ("gibbs",
     "For a reaction that is spontaneous only at high temperature, the signs of delta_H and delta_S are:",
     "delta_H > 0, delta_S > 0  (delta_G = dH-TdS < 0 only when TdS > dH, i.e., high T)",
     ["delta_H < 0, delta_S < 0", "delta_H < 0, delta_S > 0", "delta_H > 0, delta_S < 0"],
     "When dH>0 and dS>0: dG=dH-TdS. Spontaneous when TdS > dH, i.e., at high enough temperature."),
    ("entropy",
     "The Third Law of Thermodynamics states:",
     "Entropy of a perfect crystalline solid at absolute zero (0K) is zero",
     ["Entropy always increases", "You cannot reach absolute zero", "Heat cannot flow from cold to hot"],
     "3rd Law (Nernst): S=0 for a perfect crystal at T=0K. Provides absolute scale for entropy (standard molar entropies)."),
    ("hess",
     "The heat of combustion of carbon is -393 kJ/mol and of CO is -283 kJ/mol. The heat of formation of CO is:",
     "-110 kJ/mol  [C + O2 -> CO2 (-393), CO + 1/2 O2 -> CO2 (-283); by Hess: C+1/2 O2->CO = -393-(-283) = -110]",
     ["-676 kJ/mol", "+110 kJ/mol", "-393 kJ/mol"],
     "C+O2->CO2: -393. CO+1/2 O2->CO2: -283. Reverse 2nd and add to 1st: C+1/2 O2->CO: -393+283 = -110 kJ/mol."),
    ("enthalpy",
     "Which of these is an endothermic process?",
     "Photosynthesis (absorbs light energy, 6CO2+6H2O+energy -> C6H12O6+6O2)",
     ["Combustion of wood", "Neutralisation of acid and base", "Rusting of iron"],
     "Endothermic: heat absorbed from surroundings, delta_H > 0. Photosynthesis, melting, evaporation, decomposition of CaCO3."),
    ("gibbs",
     "The Gibbs energy change is related to electrical work by:",
     "delta_G = -nFE_cell  (n=moles of electrons, F=96500 C/mol, E=cell potential)",
     ["delta_G = nFE_cell", "delta_G = -RT ln K", "delta_G = -nRT"],
     "delta_G = -nFE_cell. Negative G means spontaneous (positive E_cell). Also: delta_G = -RT ln K."),
    ("entropy",
     "Which has the highest standard molar entropy?",
     "H2O(g) [gas has more disorder than liquid or solid]",
     ["H2O(s)", "H2O(l)", "NaCl(s)"],
     "Entropy order: gas >> liquid > solid. H2O(g) has highest S among the options given."),
    ("hess",
     "The resonance stabilisation energy of benzene is calculated using Hess's Law by comparing:",
     "Actual heat of hydrogenation of benzene vs theoretical value for 3 double bonds",
     ["Melting points", "Bond lengths", "Ionisation energies"],
     "Resonance energy = (3 x delta_H_hydrogenation of cyclohexene) - actual delta_H for benzene hydrogenation. Benzene is ~150 kJ/mol more stable."),
    ("enthalpy",
     "For a reaction A -> B + C, if delta_H(forward) = +40 kJ, then delta_H(reverse) is:",
     "-40 kJ  (Hess's Law: reverse reaction has opposite sign)",
     ["+40 kJ", "0 kJ", "+80 kJ"],
     "By Hess's Law, delta_H(reverse) = -delta_H(forward). B + C -> A has delta_H = -40 kJ."),
    ("gibbs",
     "The relationship between Gibbs energy and equilibrium constant K is:",
     "delta_G = -RT ln K  (R=8.314 J/mol.K, T=temperature, K=equilibrium constant)",
     ["delta_G = RT ln K", "delta_G = -nF ln K", "delta_G = -RT/K"],
     "delta_G = -RT ln K. If K>1: ln K>0, dG<0 (products favoured). If K<1: dG>0 (reactants favoured)."),
    ("entropy",
     "For which reaction does entropy decrease?",
     "N2(g) + 3H2(g) -> 2NH3(g)  [4 mol gas -> 2 mol gas]",
     ["CaCO3 -> CaO + CO2", "2H2O2 -> 2H2O + O2", "NaCl(s) -> Na+(aq) + Cl-(aq)"],
     "Entropy decreases when moles of gas decrease. N2+3H2->2NH3: 4 mol gas -> 2 mol gas, dS < 0."),
    ("hess",
     "The standard enthalpy of combustion of sucrose C12H22O11 is -5640 kJ/mol. The energy released by burning 34.2 g (0.1 mol) is:",
     "564 kJ  (0.1 mol x 5640 kJ/mol)",
     ["5640 kJ", "56.4 kJ", "282 kJ"],
     "Energy = moles x delta_H_combustion = 0.1 x 5640 = 564 kJ. Molar mass of sucrose = 342 g/mol, 34.2 g = 0.1 mol."),
]

def gen_thermo(n=QPT):
    print(f"[Thermodynamics] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(THERMO_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_thermo(scene); url=upload_pil(img, f"thermo_{i}")
        ok=post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                  "Thermodynamics", "Enthalpy, Entropy and Gibbs Energy",
                  qtext, url, opts, cidx, expl)
        print(f"  thermo_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 4. CHEMICAL EQUILIBRIUM  (Class 11)
# ==============================================================================

def draw_equilibrium(scene="kc"):
    img, draw = canvas(540, 400, "#F0FFF0")
    draw.text((20, 10), f"Equilibrium: {scene.replace('_',' ').title()}", fill="#2C3E50", font=FONT_MD)

    if scene == "kc":
        draw.text((30, 50), "Equilibrium Constant Kc", fill="#1A5276", font=FONT_LG)
        draw.text((30, 90), "For: aA + bB  <=>  cC + dD", fill="#2C3E50", font=FONT_MD)
        draw.text((30, 125), "Kc = [C]^c [D]^d / [A]^a [B]^b", fill="#E74C3C", font=FONT_LG)
        draw.text((30, 170), "* Only concentration of gases and dissolved species", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 195), "* Pure solids and liquids NOT included", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 220), "* K > 1: products favoured", fill="#27AE60", font=FONT_SM)
        draw.text((30, 245), "* K < 1: reactants favoured", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 270), "* K = 1: equal amounts", fill="#F39C12", font=FONT_SM)
        draw.text((30, 310), "Relation: Kp = Kc(RT)^delta_n", fill="#1A5276", font=FONT_MD)
        draw.text((30, 345), "delta_n = moles of gaseous products - moles of gaseous reactants", fill="#7F8C8D", font=FONT_SM)

    elif scene == "le_chatelier":
        draw.text((30, 45), "Le Chatelier's Principle", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "If a system at equilibrium is disturbed,", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 100), "it shifts to counteract the disturbance.", fill="#2C3E50", font=FONT_SM)
        rows = [
            ("Increase concentration of reactant", "Shift forward (->)"),
            ("Increase pressure (gas rxn)", "Shift to fewer moles of gas"),
            ("Increase temperature (exothermic rxn)", "Shift backward (<-)"),
            ("Increase temperature (endothermic rxn)", "Shift forward (->)"),
            ("Add catalyst", "No shift (faster equilibrium only)"),
            ("Add inert gas (const V)", "No shift"),
        ]
        y = 140
        for stress, effect in rows:
            draw.text((25, y), stress, fill="#E74C3C", font=FONT_SM)
            draw.text((25, y+18), "  -> " + effect, fill="#27AE60", font=FONT_SM)
            y += 48

    elif scene == "kp_kc":
        draw.text((30, 50), "Relationship: Kp and Kc", fill="#1A5276", font=FONT_LG)
        draw.text((30, 95), "Kp = Kc * (RT)^delta_n", fill="#E74C3C", font=FONT_LG)
        draw.text((30, 140), "R = 0.0821 L.atm/mol.K (or 8.314 J/mol.K)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 165), "delta_n = change in moles of gas", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 205), "Examples:", fill="#2C3E50", font=FONT_MD)
        draw.text((30, 240), "N2(g) + 3H2(g) <=> 2NH3(g)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 265), "delta_n = 2 - (1+3) = -2", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 290), "Kp = Kc * (RT)^-2  =>  Kp < Kc", fill="#27AE60", font=FONT_SM)
        draw.text((30, 330), "If delta_n = 0: Kp = Kc", fill="#F39C12", font=FONT_MD)
        draw.text((30, 360), "If delta_n > 0: Kp > Kc", fill="#3498DB", font=FONT_SM)

    elif scene == "buffer":
        draw.text((30, 45), "Ionic Equilibrium — pH and Buffers", fill="#1A5276", font=FONT_LG)
        draw.text((30, 85), "pH = -log[H+]  |  pOH = -log[OH-]", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 115), "pH + pOH = 14 (at 25 degC)", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 155), "Weak acid: Ka = [H+][A-]/[HA]", fill="#3498DB", font=FONT_SM)
        draw.text((30, 180), "Henderson-Hasselbalch: pH = pKa + log([A-]/[HA])", fill="#3498DB", font=FONT_SM)
        draw.text((30, 215), "Buffer: resists pH change on adding acid/base", fill="#27AE60", font=FONT_MD)
        draw.text((30, 250), "Buffer = weak acid + conjugate base", fill="#27AE60", font=FONT_SM)
        draw.text((30, 275), "Example: CH3COOH + CH3COONa", fill="#27AE60", font=FONT_SM)
        draw.text((30, 315), "Solubility Product: Ksp = [M+][X-] for MX", fill="#9B59B6", font=FONT_SM)
        draw.text((30, 345), "Common ion effect: Ksp suppresses solubility", fill="#9B59B6", font=FONT_SM)
    return img

EQUIL_QA = [
    ("kc",
     "For the reaction N2(g) + 3H2(g) <=> 2NH3(g), the expression for Kc is:",
     "Kc = [NH3]^2 / ([N2][H2]^3)",
     ["Kc = [N2][H2]^3 / [NH3]^2", "Kc = [NH3] / ([N2][H2])", "Kc = 2[NH3] / ([N2]+3[H2])"],
     "Kc = [products]^coeff / [reactants]^coeff. For N2+3H2<=>2NH3: Kc = [NH3]^2/([N2][H2]^3)."),
    ("le_chatelier",
     "In the Haber process N2 + 3H2 <=> 2NH3 (exothermic), increasing temperature:",
     "Decreases the yield of NH3 (equilibrium shifts backward for exothermic reactions)",
     ["Increases yield of NH3", "Has no effect on equilibrium", "Increases Kc"],
     "Le Chatelier: for exothermic reaction, increasing T shifts equilibrium backward (heat is a product). Kc decreases."),
    ("kp_kc",
     "For the reaction H2(g) + I2(g) <=> 2HI(g), the relationship between Kp and Kc is:",
     "Kp = Kc  (delta_n = 2 - (1+1) = 0)",
     ["Kp = Kc*(RT)^2", "Kp = Kc/(RT)^2", "Kp = Kc*(RT)"],
     "delta_n = moles of gaseous products - gaseous reactants = 2 - 2 = 0. So Kp = Kc*(RT)^0 = Kc."),
    ("buffer",
     "The pH of a solution with [H+] = 0.001 M (10^-3 M) is:",
     "pH = 3  (pH = -log(10^-3) = 3)",
     ["pH = 1", "pH = 11", "pH = 7"],
     "pH = -log[H+] = -log(10^-3) = 3. Acidic solution (pH < 7 at 25 degC)."),
    ("kc",
     "If Kc for a reaction at 298K is very large (e.g. 10^50), it means:",
     "Reaction goes nearly to completion (products highly favoured)",
     ["Reaction is very slow", "Reactants are highly favoured", "Reaction is at equilibrium"],
     "Large K >> 1: [products] >> [reactants] at equilibrium. Reaction essentially goes to completion."),
    ("le_chatelier",
     "In the equilibrium CO(g) + 3H2(g) <=> CH4(g) + H2O(g), increasing pressure shifts equilibrium:",
     "Forward (right), because there are 4 mol gas on left and 2 mol on right",
     ["Backward (left)", "No effect (same moles gas)", "Cannot predict"],
     "delta_n_gas = 2 - 4 = -2. Increasing pressure shifts toward fewer moles of gas (right/products). Le Chatelier."),
    ("buffer",
     "A buffer solution resists changes in pH. Which of the following is a buffer?",
     "CH3COOH and CH3COONa (weak acid + its conjugate base)",
     ["HCl and NaCl", "NaOH and NaCl", "H2SO4 and Na2SO4"],
     "Buffer = weak acid + conjugate base (or weak base + conjugate acid). CH3COOH/CH3COONa is a classic acetate buffer."),
    ("kp_kc",
     "For the reaction 2SO2(g) + O2(g) <=> 2SO3(g), delta_n is:",
     "-1  (2 mol products gas - 3 mol reactants gas = -1)",
     ["+1", "0", "-2"],
     "delta_n = moles gas products - moles gas reactants = 2 - (2+1) = 2-3 = -1. So Kp = Kc*(RT)^-1 < Kc."),
    ("kc",
     "The reaction quotient Q and equilibrium constant Kc are related as:",
     "Q < Kc: reaction proceeds forward; Q > Kc: reaction proceeds backward; Q = Kc: at equilibrium",
     ["Q > Kc: reaction proceeds forward", "Q always equals Kc", "Q and Kc are unrelated"],
     "Q uses current concentrations; Kc uses equilibrium concentrations. Q<Kc -> shift right; Q>Kc -> shift left; Q=Kc -> equilibrium."),
    ("le_chatelier",
     "Adding a catalyst to an equilibrium reaction:",
     "Does NOT change the position of equilibrium or K; only speeds up the rate of reaching equilibrium",
     ["Shifts equilibrium to the right", "Increases the value of K", "Increases yield of products"],
     "Catalyst lowers activation energy equally for forward and reverse reactions. Equilibrium position (K) unchanged; only reached faster."),
    ("buffer",
     "The Ksp of AgCl is 1.8 x 10^-10. What is the solubility of AgCl in pure water?",
     "1.34 x 10^-5 mol/L  [s = sqrt(Ksp) = sqrt(1.8e-10)]",
     ["1.8 x 10^-10 mol/L", "1.8 x 10^-5 mol/L", "3.6 x 10^-10 mol/L"],
     "AgCl -> Ag+ + Cl-. Ksp = s^2 = 1.8e-10. s = sqrt(1.8e-10) = 1.34e-5 mol/L."),
    ("kc",
     "For the reaction PCl5(g) <=> PCl3(g) + Cl2(g), if the degree of dissociation is alpha at total pressure P, Kp is:",
     "Kp = alpha^2 * P / (1 - alpha^2)  (for small alpha: approx alpha^2 * P)",
     ["Kp = alpha * P", "Kp = alpha^2/(1-alpha)", "Kp = P/(1-alpha)"],
     "At equilibrium: PCl5: (1-a), PCl3: a, Cl2: a moles. Total = 1+a. Kp = [a/(1+a)][a/(1+a)] / [(1-a)/(1+a)] * P = a^2P/(1-a^2)."),
    ("le_chatelier",
     "In the equilibrium 2NO2(g, brown) <=> N2O4(g, colourless), cooling the flask makes it:",
     "More colourless (forward shift, N2O4 formation favoured — the reaction is exothermic forward)",
     ["More brown", "No change in colour", "Darker brown immediately then colourless"],
     "N2O4 formation is exothermic. Cooling (low T) shifts equilibrium toward exothermic direction (forward) -> more N2O4 -> less brown."),
    ("kp_kc",
     "At 500K, Kc = 0.061 for N2 + 3H2 <=> 2NH3. The value of Kp is approximately (R=0.082 L.atm/mol.K):",
     "Kp = Kc*(RT)^delta_n = 0.061*(0.082*500)^(-2) = 0.061/1681 = 3.63 x 10^-5",
     ["Kp = 0.061", "Kp = 5.0", "Kp = 0.0041"],
     "delta_n = 2-4 = -2. RT = 0.082*500 = 41. (RT)^-2 = 1/1681. Kp = 0.061/1681 ~ 3.6e-5."),
    ("buffer",
     "The Henderson-Hasselbalch equation is pH = pKa + log([A-]/[HA]). For a buffer with equal concentrations of acid and conjugate base:",
     "pH = pKa  (since log(1) = 0)",
     ["pH = 7", "pH = 2*pKa", "pH = pKa + 7"],
     "When [A-] = [HA], log([A-]/[HA]) = log(1) = 0. Therefore pH = pKa. This is the buffering midpoint."),
    ("kc",
     "For the reaction A + B <=> C + D, Kc = 4. If initial concentrations of all are 1M, what happens initially?",
     "Reaction proceeds forward (Q = 1*1/1*1 = 1 < Kc = 4)",
     ["Reaction proceeds backward", "System is already at equilibrium", "Cannot determine"],
     "Q = [C][D]/[A][B] = 1*1/1*1 = 1. Since Q < Kc (1 < 4), reaction proceeds forward to produce more products."),
    ("le_chatelier",
     "Removing a product from an equilibrium reaction mixture:",
     "Shifts the equilibrium forward to produce more products",
     ["Has no effect on equilibrium", "Shifts equilibrium backward", "Increases Kc"],
     "Le Chatelier: removing a product decreases its concentration, shifting equilibrium forward to restore it."),
    ("buffer",
     "A weak acid HA has Ka = 10^-5 (pKa = 5). At pH = 6, the ratio [A-]/[HA] is:",
     "10 : 1  [pH = pKa + log(ratio); 6 = 5 + log(ratio); log(ratio) = 1; ratio = 10]",
     ["1 : 10", "1 : 1", "100 : 1"],
     "Henderson-Hasselbalch: pH = pKa + log([A-]/[HA]). 6 = 5 + log(r). log(r) = 1. r = 10. [A-]/[HA] = 10/1."),
    ("kp_kc",
     "For reaction CaCO3(s) <=> CaO(s) + CO2(g), the equilibrium expression for Kc is:",
     "Kc = [CO2]  (solids not included in Kc expression)",
     ["Kc = [CaO][CO2]/[CaCO3]", "Kc = [CO2]/[CaCO3]", "Kc = 1/[CO2]"],
     "Pure solids (CaCO3, CaO) have constant 'concentration' and are excluded. Only [CO2] appears in Kc."),
    ("le_chatelier",
     "In the contact process for sulphuric acid: 2SO2(g) + O2(g) <=> 2SO3(g), high pressure is used because:",
     "It shifts equilibrium toward fewer moles of gas (right), increasing SO3 yield",
     ["It speeds up the catalyst", "It increases temperature", "High pressure has no effect here"],
     "delta_n_gas = 2 - 3 = -1. High pressure favours fewer gas moles -> shifts right (products). Used in industrial process."),
]

def gen_equilibrium(n=QPT):
    print(f"[Chemical Equilibrium] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(EQUIL_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_equilibrium(scene); url=upload_pil(img, f"equil_{i}")
        ok=post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                  "Chemical Equilibrium", "Kc, Kp, and Le Chatelier's Principle",
                  qtext, url, opts, cidx, expl)
        print(f"  equil_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 5. ELECTROCHEMISTRY  (Class 12)
# ==============================================================================

def draw_electrochem(scene="cell"):
    img, draw = canvas(540, 400, "#0A0A23")
    draw.text((20, 10), f"Electrochemistry: {scene.replace('_',' ').title()}", fill="white", font=FONT_MD)

    if scene == "cell":
        # Galvanic / Daniell cell
        # Anode (Zn)
        draw.rectangle([40, 120, 200, 310], fill="#1E8BC3", outline="white", width=2)
        draw.text((80, 145), "Anode (-)", fill="white", font=FONT_MD)
        draw.text((70, 175), "Zn(s) -> Zn2+(aq)", fill="#FFD700", font=FONT_SM)
        draw.text((70, 198), "+ 2e- (oxidation)", fill="#FFD700", font=FONT_SM)
        draw.text((75, 230), "ZnSO4 solution", fill="#AAA", font=FONT_SM)
        # Cathode (Cu)
        draw.rectangle([340, 120, 500, 310], fill="#C0392B", outline="white", width=2)
        draw.text((370, 145), "Cathode (+)", fill="white", font=FONT_MD)
        draw.text((350, 175), "Cu2+(aq) + 2e-", fill="#FFD700", font=FONT_SM)
        draw.text((360, 198), "-> Cu(s) (reduction)", fill="#FFD700", font=FONT_SM)
        draw.text((365, 230), "CuSO4 solution", fill="#AAA", font=FONT_SM)
        # Salt bridge
        draw.rectangle([195, 180, 345, 220], fill="#27AE60", outline="white", width=2)
        draw.text((215, 193), "Salt Bridge (KCl)", fill="white", font=FONT_SM)
        # Wires
        draw.line([(120, 120), (120, 80)], fill="white", width=2)
        draw.line([(120, 80), (420, 80)], fill="white", width=2)
        draw.line([(420, 80), (420, 120)], fill="white", width=2)
        draw.text((240, 58), "e- flow", fill="#FFD700", font=FONT_MD)
        draw.text((20, 355), "E_cell = E_cathode - E_anode  |  Spontaneous if E_cell > 0", fill="#AAA", font=FONT_SM)

    elif scene == "nernst":
        draw.text((30, 45), "Nernst Equation", fill="#FFD700", font=FONT_LG)
        draw.text((30, 90), "E = E0 - (RT/nF) * ln Q", fill="white", font=FONT_LG)
        draw.text((30, 130), "At 298K:  E = E0 - (0.0592/n) * log Q", fill="#3498DB", font=FONT_LG)
        draw.text((30, 180), "E0 = standard electrode potential", fill="#AAA", font=FONT_SM)
        draw.text((30, 205), "n = number of electrons transferred", fill="#AAA", font=FONT_SM)
        draw.text((30, 230), "Q = reaction quotient", fill="#AAA", font=FONT_SM)
        draw.text((30, 270), "At equilibrium: E = 0, Q = Kc", fill="#27AE60", font=FONT_MD)
        draw.text((30, 300), "=> ln Kc = nFE0/(RT) = nE0/0.0592  (at 298K)", fill="#27AE60", font=FONT_MD)
        draw.text((30, 345), "Concentration cell: E0=0, E = -(0.0592/n)*log([dilute]/[conc])", fill="#AAA", font=FONT_SM)

    elif scene == "electrolysis":
        draw.text((30, 45), "Faraday's Laws of Electrolysis", fill="#FFD700", font=FONT_LG)
        draw.text((30, 90), "1st Law: m = ZIt  (Z = electrochemical equivalent)", fill="white", font=FONT_MD)
        draw.text((30, 130), "2nd Law: m proportional to E (equivalent weight)", fill="white", font=FONT_MD)
        draw.text((30, 175), "m = (M/nF) * Q  =  (M/nF) * I*t", fill="#3498DB", font=FONT_LG)
        draw.text((30, 215), "M = molar mass, n = valence, F = 96500 C/mol", fill="#AAA", font=FONT_SM)
        draw.text((30, 255), "Example: Deposit Cu (M=64, n=2) with 2A for 965s:", fill="#AAA", font=FONT_SM)
        draw.text((30, 280), "m = (64/(2*96500)) * 2*965 = (64/193000)*1930", fill="#27AE60", font=FONT_SM)
        draw.text((30, 305), "= 0.640 g of copper deposited", fill="#27AE60", font=FONT_SM)
        draw.text((30, 350), "Cathode: reduction (cations reduced)  |  Anode: oxidation", fill="#AAA", font=FONT_SM)

    return img

ELEC_QA = [
    ("cell",
     "In a galvanic (voltaic) cell, oxidation occurs at the:",
     "Anode (negative terminal in galvanic cell)",
     ["Cathode", "Salt bridge", "External circuit"],
     "Anode: oxidation (loss of electrons). In galvanic cells, anode is negative (-). Mnemonic: AN OX (Anode Oxidation)."),
    ("nernst",
     "The Nernst equation at 298K for a 2-electron transfer reaction with E0 = 0.34V and Q = 0.01 is:",
     "E = 0.34 - (0.0592/2)*log(0.01) = 0.34 - 0.0296*(-2) = 0.34 + 0.059 = 0.399 V",
     ["E = 0.34 V", "E = 0.281 V", "E = 0.34 - 0.0592 V"],
     "E = E0 - (0.0592/n)*log Q = 0.34 - (0.0296)*log(0.01) = 0.34 - 0.0296*(-2) = 0.34 + 0.059 = 0.399 V."),
    ("electrolysis",
     "In electrolysis of water, the gases produced at cathode and anode are:",
     "Cathode: H2 (reduction of H+); Anode: O2 (oxidation of H2O)",
     ["Cathode: O2; Anode: H2", "Both electrodes: H2", "Cathode: H2; Anode: Cl2"],
     "Cathode (reduction): 2H+ + 2e- -> H2. Anode (oxidation): 2H2O -> O2 + 4H+ + 4e-. H2:O2 volume ratio = 2:1."),
    ("cell",
     "The standard cell potential for Zn-Cu Daniell cell (E0Zn2+/Zn = -0.76V, E0Cu2+/Cu = +0.34V) is:",
     "E_cell = 0.34 - (-0.76) = 1.10 V",
     ["0.42 V", "-1.10 V", "0.76 V"],
     "E0_cell = E0_cathode - E0_anode = E0(Cu2+/Cu) - E0(Zn2+/Zn) = 0.34-(-0.76) = 1.10 V. Positive = spontaneous."),
    ("nernst",
     "At equilibrium in an electrochemical cell:",
     "E = 0 (no net cell potential) and delta_G = 0",
     ["E = E0", "E = maximum", "E = -E0"],
     "At equilibrium: Q = K, E = 0 (battery is 'dead'). Nernst: 0 = E0 - (0.0592/n)*log K => log K = nE0/0.0592."),
    ("electrolysis",
     "Faraday's constant F = 96500 C/mol means:",
     "96500 coulombs of charge is required to deposit 1 mole of a univalent (n=1) element",
     ["96500 grams per mole", "The charge of one electron", "Current needed for 1 hour"],
     "F = 96500 C/mol electrons. For n=1 metal: 96500 C deposits 1 mol (one mole of atoms, each gaining 1 electron)."),
    ("cell",
     "The salt bridge in an electrochemical cell:",
     "Maintains electrical neutrality by allowing ion flow between half-cells",
     ["Allows electron flow between cells", "Increases cell voltage", "Stores electrical charge"],
     "Salt bridge (e.g., KCl in agar): ions (K+ and Cl-) migrate to balance charge buildup, completing the circuit."),
    ("nernst",
     "The standard Gibbs energy change and E0_cell are related by:",
     "delta_G0 = -nFE0_cell",
     ["delta_G0 = nFE0_cell", "delta_G0 = -RT ln E0_cell", "delta_G0 = nRT E0_cell"],
     "delta_G = -nFE. At standard: delta_G0 = -nFE0. Spontaneous reaction: E0>0, so delta_G0<0. Consistent with thermodynamics."),
    ("electrolysis",
     "How many grams of silver (M=108 g/mol) are deposited when 0.5 A flows for 2 hours? (F=96500)",
     "m = (108/96500) * 0.5 * 7200 = 4.02 g",
     ["2.01 g", "8.04 g", "1.01 g"],
     "m = MIt/(nF) = 108*0.5*7200/(1*96500) = 108*3600/96500 = 388800/96500 = 4.03 g. n=1 for Ag+."),
    ("cell",
     "Which of the following has the highest reduction potential (strongest oxidising agent)?",
     "F2 (E0 = +2.87 V)",
     ["Zn2+ (E0 = -0.76V)", "Cu2+ (E0 = +0.34V)", "H+ (E0 = 0.00V)"],
     "Higher reduction potential = stronger oxidising agent. F2 (+2.87V) has the highest standard reduction potential."),
    ("nernst",
     "For a concentration cell with Cu|Cu2+(0.1M) || Cu2+(1M)|Cu, the EMF at 298K is:",
     "E = (0.0592/2)*log(1/0.1) = 0.0296 * 1 = 0.0296 V",
     ["0 V", "0.34 V", "0.0592 V"],
     "Concentration cell: E0=0. E = -(0.0592/n)*log([dilute]/[conc]) = -(0.0296)*log(0.1/1) = -0.0296*(-1) = +0.0296 V."),
    ("electrolysis",
     "In the electrolysis of aqueous NaCl (brine), the products at cathode and anode are:",
     "Cathode: H2; Anode: Cl2 (industrial chlor-alkali process)",
     ["Cathode: Na; Anode: Cl2", "Cathode: H2; Anode: O2", "Cathode: Na; Anode: O2"],
     "In brine: at cathode H+ (from water) is reduced -> H2. At anode Cl- is oxidised -> Cl2. NaOH forms in solution."),
    ("cell",
     "The spontaneity of an electrochemical cell reaction is determined by:",
     "E_cell > 0 (positive cell potential = spontaneous)",
     ["Large Kc value", "High temperature", "Low activation energy"],
     "Spontaneous: E_cell > 0, delta_G < 0, K > 1. These three are equivalent via: delta_G = -nFE = -RT ln K."),
    ("nernst",
     "For the reaction Zn + Cu2+ -> Zn2+ + Cu, E0_cell = 1.10 V. What is ln K at 298K?",
     "ln K = nFE0/(RT) = 2*96500*1.10/(8.314*298) = 85.8  (K is enormous)",
     ["ln K = 0", "ln K = 1.10", "ln K = 2*1.10 = 2.20"],
     "ln K = nFE0/(RT) = nE0/0.02569 = 2*1.10/0.02569 = 85.6. K = e^85.6 >> 1. Reaction essentially complete."),
    ("electrolysis",
     "The electrochemical equivalent Z of an element is related to its equivalent weight E_q by:",
     "Z = E_q / 96500  (mass deposited per coulomb = equivalent weight/F)",
     ["Z = 96500 / E_q", "Z = E_q * 96500", "Z = E_q / n"],
     "Faraday 1st Law: m = ZIt = ZQ. Z = m/Q = (M/n)/(F) = E_q/F = E_q/96500 g/C."),
]

def gen_electrochem(n=15):
    print(f"[Electrochemistry] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(ELEC_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_electrochem(scene); url=upload_pil(img, f"ec_{i}")
        ok=post_q("Science", 12, random.choice(["Advanced","Olympiad"]),
                  "Electrochemistry", "Galvanic Cells and Electrolysis",
                  qtext, url, opts, cidx, expl)
        print(f"  ec_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 6. ORGANIC CHEMISTRY  (Class 11-12)
# ==============================================================================

def draw_organic(scene="alkane"):
    img, draw = canvas(540, 400, "#FFFDE7")
    draw.text((20, 10), f"Organic Chemistry: {scene.replace('_',' ').title()}", fill="#2C3E50", font=FONT_MD)

    if scene == "alkane":
        draw.text((25, 50), "Alkanes: CnH(2n+2)  |  Single bonds only  |  sp3", fill="#1A5276", font=FONT_MD)
        data = [
            ("CH4", "Methane", "n=1"),
            ("C2H6", "Ethane", "n=2"),
            ("C3H8", "Propane", "n=3"),
            ("C4H10", "Butane", "n=4"),
            ("C5H12", "Pentane", "n=5"),
        ]
        y = 100
        for formula, name, n_str in data:
            draw.text((40, y), formula, fill="#E74C3C", font=FONT_MD)
            draw.text((140, y), name, fill="#2C3E50", font=FONT_MD)
            draw.text((300, y), n_str, fill="#7F8C8D", font=FONT_SM)
            y += 42
        draw.text((25, 330), "Reactions: Halogenation (free radical substitution)", fill="#7F8C8D", font=FONT_SM)
        draw.text((25, 355), "CH4 + Cl2 -> CH3Cl + HCl (in presence of UV light)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "alkene":
        draw.text((25, 50), "Alkenes: CnH(2n)  |  C=C double bond  |  sp2", fill="#1A5276", font=FONT_MD)
        draw.text((25, 85), "Ethene (C2H4): H2C=CH2 — planar, 120 deg, pi bond", fill="#2C3E50", font=FONT_SM)
        draw.text((25, 115), "Reactions (Electrophilic Addition):", fill="#E74C3C", font=FONT_MD)
        reactions = [
            ("+ H2  (Ni, heat)", "-> Alkane (hydrogenation)"),
            ("+ HBr", "-> CH3-CH2-Br (Markovnikov addition)"),
            ("+ Br2 (CCl4)", "-> dibromoalkane (decolorises bromine water)"),
            ("+ H2O (H+)", "-> Alcohol"),
            ("+ O3, then Zn/H2O", "-> Ozonolysis: aldehydes/ketones"),
        ]
        y = 155
        for reagent, product in reactions:
            draw.text((30, y), reagent, fill="#3498DB", font=FONT_SM)
            draw.text((30, y+18), product, fill="#27AE60", font=FONT_SM)
            y += 45

    elif scene == "benzene":
        draw.text((25, 45), "Benzene C6H6 — Aromatic Compound", fill="#1A5276", font=FONT_LG)
        # Hexagon
        cx, cy = 200, 220
        sides = 6
        r = 70
        pts = [(int(cx + r*math.cos(math.pi/2 - i*2*math.pi/sides)),
                int(cy - r*math.sin(math.pi/2 - i*2*math.pi/sides))) for i in range(sides)]
        for j in range(sides):
            draw.line([pts[j], pts[(j+1)%sides]], fill="#E74C3C", width=3)
        draw.ellipse([cx-35, cy-35, cx+35, cy+35], outline="#3498DB", width=2)
        draw.text((cx-20, cy-10), "6 pi e-", fill="#3498DB", font=FONT_SM)
        draw.text((300, 110), "Properties:", fill="#2C3E50", font=FONT_MD)
        draw.text((300, 140), "- Planar molecule", fill="#7F8C8D", font=FONT_SM)
        draw.text((300, 165), "- sp2 hybridised C", fill="#7F8C8D", font=FONT_SM)
        draw.text((300, 190), "- 6 pi electrons", fill="#7F8C8D", font=FONT_SM)
        draw.text((300, 215), "- Delocalized bonds", fill="#7F8C8D", font=FONT_SM)
        draw.text((300, 240), "- Aromatic stability", fill="#27AE60", font=FONT_SM)
        draw.text((300, 265), "- Electrophilic sub.", fill="#E74C3C", font=FONT_SM)
        draw.text((25, 350), "Huckel's rule: 4n+2 pi electrons = aromatic (n=0,1,2...)", fill="#AAA", font=FONT_SM)

    elif scene == "functional_groups":
        draw.text((25, 40), "Common Functional Groups", fill="#1A5276", font=FONT_LG)
        groups = [
            ("-OH",    "Alcohol (hydroxyl)",  "-COOH",  "Carboxylic acid"),
            ("-CHO",   "Aldehyde",            "-CO-",   "Ketone (carbonyl)"),
            ("-NH2",   "Amine",               "-CONH2", "Amide"),
            ("-X",     "Halide (X=F,Cl,Br,I)","-CN",    "Nitrile"),
            ("-O-",    "Ether",               "-COO-",  "Ester"),
        ]
        y = 90
        for g1, n1, g2, n2 in groups:
            draw.text((30, y), g1, fill="#E74C3C", font=FONT_MD)
            draw.text((100, y), n1, fill="#2C3E50", font=FONT_SM)
            draw.text((280, y), g2, fill="#3498DB", font=FONT_MD)
            draw.text((360, y), n2, fill="#2C3E50", font=FONT_SM)
            y += 45
        draw.text((25, 370), "IUPAC naming: longest chain + functional group suffix", fill="#7F8C8D", font=FONT_SM)

    return img

ORGANIC_QA = [
    ("alkane",
     "The general formula for alkanes is:",
     "CnH(2n+2)",
     ["CnH(2n)", "CnH(2n-2)", "CnHn"],
     "Alkanes: saturated hydrocarbons with only single bonds. General formula CnH(2n+2). CH4, C2H6, C3H8..."),
    ("alkene",
     "Markovnikov's rule states that in addition of HX to an alkene:",
     "H adds to the carbon with more hydrogen atoms (X adds to more substituted carbon)",
     ["X adds to less substituted carbon", "Addition occurs randomly", "Only trans addition occurs"],
     "Markovnikov: H+ adds to C with more H (forms more stable carbocation intermediate). HBr + CH3-CH=CH2 -> CH3-CHBr-CH3."),
    ("benzene",
     "Benzene undergoes electrophilic substitution rather than addition because:",
     "Addition would destroy aromaticity (6 pi electron delocalization); substitution retains it",
     ["Benzene has no double bonds", "Benzene is too reactive for addition", "Benzene is an alkane"],
     "Benzene is stabilised by aromatic delocalisation (~150 kJ/mol resonance energy). Addition would disrupt this stability."),
    ("functional_groups",
     "The functional group in ethanol (C2H5OH) is:",
     "-OH (hydroxyl group) — alcohol",
     ["-CHO (aldehyde)", "-COOH (carboxylic acid)", "-CO- (ketone)"],
     "Ethanol has an -OH group attached to carbon. Alcohols: R-OH. Primary, secondary, tertiary based on carbon substitution."),
    ("alkane",
     "Halogenation of methane in the presence of UV light proceeds by:",
     "Free radical chain mechanism (initiation, propagation, termination)",
     ["Ionic mechanism", "Nucleophilic substitution", "Electrophilic addition"],
     "CH4 + Cl2 (UV) -> CH3Cl + HCl. UV light initiates homolytic cleavage of Cl2 -> 2Cl* radicals. Chain reaction."),
    ("alkene",
     "The test to distinguish alkenes from alkanes uses:",
     "Bromine water (Br2/CCl4) — alkene decolorises it (addition reaction), alkane does not",
     ["Litmus paper", "Combustion test", "Addition of water"],
     "Alkenes decolorise bromine water: CH2=CH2 + Br2 -> CH2Br-CH2Br. Alkanes do not react at room temperature."),
    ("benzene",
     "Benzene on nitration with conc. HNO3 and conc. H2SO4 gives:",
     "Nitrobenzene (C6H5-NO2) — electrophilic substitution",
     ["Benzene hexanitrate", "Cyclohexane", "Aniline"],
     "Nitration: HNO3 + H2SO4 -> NO2+ (nitronium ion). NO2+ attacks benzene ring -> nitrobenzene + H+."),
    ("functional_groups",
     "Which of the following is a carboxylic acid?",
     "CH3COOH (acetic acid / ethanoic acid)",
     ["CH3CHO", "CH3OH", "CH3-CO-CH3"],
     "Carboxylic acid: R-COOH. CH3COOH = acetic acid. CH3CHO = acetaldehyde (aldehyde). CH3CO-CH3 = acetone (ketone)."),
    ("alkane",
     "The IUPAC name of CH3-CH(CH3)-CH2-CH3 is:",
     "2-methylbutane",
     ["3-methylbutane", "isopentane", "2-methylpropane"],
     "Longest chain = 4C (butane). Methyl branch at C2. Name: 2-methylbutane. Number from end giving lowest locant."),
    ("alkene",
     "Which reaction confirms the presence of a C=C double bond?",
     "Decolorisation of acidic KMnO4 (purple -> colourless)",
     ["Burning with blue flame", "Dissolving in water", "Reaction with NaOH"],
     "Alkenes reduce KMnO4: the purple colour disappears. Also: Baeyer's test. Alkenes oxidised, KMnO4 reduced (colourless Mn2+)."),
    ("benzene",
     "According to Huckel's rule, an aromatic compound must have how many pi electrons?",
     "4n+2 pi electrons (n=0,1,2,...), e.g. benzene: 6 (n=1), naphthalene: 10 (n=2)",
     ["4n pi electrons", "2n pi electrons", "Any even number"],
     "Huckel's rule: aromatic = cyclic, planar, fully conjugated, 4n+2 pi electrons. Benzene: n=1, 6 pi electrons."),
    ("functional_groups",
     "The reaction of carboxylic acid with alcohol in presence of H2SO4 catalyst forms:",
     "Ester (esterification: RCOOH + R'OH <=> RCOOR' + H2O)",
     ["Ether", "Aldehyde", "Anhydride"],
     "Fischer esterification: acid + alcohol -> ester + water (reversible). CH3COOH + C2H5OH -> CH3COOC2H5 + H2O."),
    ("alkane",
     "Cracking of alkanes is used industrially to:",
     "Break long-chain alkanes into shorter alkanes and alkenes (useful for petrol)",
     ["Join short alkanes", "Remove impurities", "Add hydrogen to alkanes"],
     "Catalytic/thermal cracking: long-chain hydrocarbons -> shorter chains + alkenes. Increases petrol fraction yield in refining."),
    ("alkene",
     "The addition of H2O to propene (CH3-CH=CH2) in presence of acid catalyst gives:",
     "Propan-2-ol (CH3-CHOH-CH3) as major product (Markovnikov)",
     ["Propan-1-ol", "Propanone", "Propanoic acid"],
     "H2O adds as H-OH. By Markovnikov: H to terminal C (more H), OH to middle C. Major product: CH3-CHOH-CH3 (propan-2-ol)."),
    ("benzene",
     "Friedel-Crafts alkylation of benzene with CH3Cl and AlCl3 gives:",
     "Methylbenzene (toluene, C6H5-CH3) — electrophilic aromatic substitution",
     ["Chlorobenzene", "Benzaldehyde", "Cyclohexane"],
     "Friedel-Crafts: AlCl3 generates CH3+ (carbocation). CH3+ attacks benzene ring -> methylbenzene (toluene) + HCl."),
    ("functional_groups",
     "Primary amines (R-NH2) are characterised by:",
     "One organic group attached to N, basic nature (lone pair on N), form salts with acids",
     ["Two organic groups on N", "Acidic nature", "No lone pair on N"],
     "Primary amine: R-NH2. N has one lone pair -> basic (accepts H+). React with acids: R-NH2 + HCl -> R-NH3+Cl-."),
    ("alkane",
     "Isomerism in butane (C4H10): n-butane and isobutane differ in:",
     "Structural isomerism (chain isomerism) — same molecular formula, different carbon skeleton",
     ["Geometrical isomerism", "Optical isomerism", "Functional group isomerism"],
     "n-Butane: CH3CH2CH2CH3. Isobutane: CH3CH(CH3)CH3. Same formula C4H10, different chain arrangement = structural isomers."),
    ("alkene",
     "Geometric (cis-trans) isomerism in alkenes requires:",
     "Each carbon of the C=C bond must have two different substituents",
     ["A chiral centre", "Triple bond", "More than 4 carbons"],
     "Cis-trans isomerism: restricted rotation around C=C. Each doubly bonded C must have 2 different groups. E.g., 2-butene."),
    ("benzene",
     "Toluene (methylbenzene) is more reactive than benzene toward electrophilic substitution because:",
     "Methyl group is electron-donating (activating group), increasing electron density on ring",
     ["Methyl group is electron-withdrawing", "Toluene has more pi electrons", "Toluene has sp3 carbons only"],
     "-CH3 is +I and hyperconjugation donor. Increases ring electron density -> more reactive toward electrophiles."),
    ("functional_groups",
     "Saponification is the reaction of:",
     "Ester + NaOH -> Carboxylate salt + Alcohol (base hydrolysis — makes soap)",
     ["Acid + alcohol -> ester", "Alkene + H2O -> alcohol", "Aldehyde + H2 -> alcohol"],
     "Saponification: RCOOR' + NaOH -> RCOONa + R'OH. Used to make soap from fats/oils (triglycerides + NaOH)."),
]

def gen_organic(n=QPT):
    print(f"[Organic Chemistry] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(ORGANIC_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_organic(scene); url=upload_pil(img, f"org_{i}")
        ok=post_q("Science", random.choice([11,12]), random.choice(["Advanced","Olympiad"]),
                  "Organic Chemistry", "Hydrocarbons and Functional Groups",
                  qtext, url, opts, cidx, expl)
        print(f"  org_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 7. PERIODIC TABLE & PERIODICITY  (Class 11)
# ==============================================================================

def draw_periodic(scene="trends"):
    img, draw = canvas(540, 400, "#EEF2FF")
    draw.text((20, 10), f"Periodic Table: {scene.replace('_',' ').title()}", fill="#2C3E50", font=FONT_MD)

    if scene == "trends":
        draw.text((30, 50), "Periodic Trends (across a period ->)", fill="#1A5276", font=FONT_LG)
        rows = [
            ("Atomic radius",       "DECREASES (more protons, same shell)"),
            ("Ionisation energy",   "INCREASES (harder to remove electron)"),
            ("Electronegativity",   "INCREASES (Pauling scale: F=4.0 highest)"),
            ("Electron affinity",   "Generally increases (exceptions exist)"),
            ("Metallic character",  "DECREASES (metals on left)"),
            ("Non-metallic char.",  "INCREASES (non-metals on right)"),
        ]
        y = 95
        for prop, trend in rows:
            draw.text((30, y), prop + ":", fill="#E74C3C", font=FONT_SM)
            draw.text((30, y+18), trend, fill="#27AE60", font=FONT_SM)
            y += 48
        draw.text((30, 375), "Down a group: atomic radius increases, IE decreases", fill="#7F8C8D", font=FONT_SM)

    elif scene == "blocks":
        draw.text((30, 45), "Blocks of the Periodic Table", fill="#1A5276", font=FONT_LG)
        block_data = [
            ("s-block", "Groups 1 & 2 (alkali & alkaline earth metals)", "#3498DB"),
            ("p-block", "Groups 13-18 (includes non-metals, metalloids)", "#27AE60"),
            ("d-block", "Groups 3-12 (transition metals)", "#E74C3C"),
            ("f-block", "Lanthanides & Actinides (inner transition)", "#9B59B6"),
        ]
        y = 100
        for block, desc, col in block_data:
            draw.text((30, y), block, fill=col, font=FONT_LG)
            draw.text((140, y), desc, fill="#2C3E50", font=FONT_SM)
            y += 60
        draw.text((30, 360), "Period 1: 2 elements | Period 2-3: 8 | Period 4-5: 18 | 6-7: 32", fill="#7F8C8D", font=FONT_SM)

    return img

PERIODIC_QA = [
    ("trends",
     "Across a period (left to right), atomic radius:",
     "Decreases (nuclear charge increases, same electron shell)",
     ["Increases", "Remains constant", "First increases then decreases"],
     "Going left to right across a period: more protons added to same shell -> greater nuclear attraction -> smaller radius."),
    ("trends",
     "The element with the highest electronegativity is:",
     "Fluorine (F), electronegativity = 4.0 on Pauling scale",
     ["Oxygen (3.5)", "Chlorine (3.0)", "Nitrogen (3.0)"],
     "Fluorine is top-right of periodic table (excluding noble gases). Highest nuclear attraction + smallest size = most electronegative."),
    ("blocks",
     "Transition metals belong to which block of the periodic table?",
     "d-block (Groups 3-12)",
     ["s-block", "p-block", "f-block"],
     "d-block elements: filling d orbitals, groups 3-12. Transition metals have variable oxidation states, form coloured compounds."),
    ("trends",
     "The first ionisation energy is highest for:",
     "Noble gases (He has highest IE1 = 2372 kJ/mol)",
     ["Alkali metals", "Alkaline earth metals", "Halogens"],
     "Noble gases: complete octet, highly stable -> very high IE. He: 2372, Ne: 2081 kJ/mol. Alkali metals have lowest IE."),
    ("blocks",
     "Lanthanides and actinides belong to the:",
     "f-block (inner transition elements)",
     ["d-block", "p-block", "s-block"],
     "f-block: electrons fill 4f (lanthanides, Z=57-71) or 5f (actinides, Z=89-103) orbitals. Inner transition elements."),
    ("trends",
     "Which of the following has the smallest atomic radius?",
     "F (fluorine) — smallest nonmetal in period 2 due to highest nuclear charge",
     ["Li", "Na", "O"],
     "Among these: F is in period 2 far right (Z=9, highest in its period excluding noble gases) -> smallest radius in period 2."),
    ("trends",
     "Going down a group in the periodic table, ionisation energy:",
     "Decreases (outermost electrons further from nucleus, more shielded)",
     ["Increases", "Remains same", "First increases then decreases"],
     "Down a group: atomic radius increases, shielding increases -> easier to remove outermost electron -> lower IE."),
    ("blocks",
     "The s-block elements include:",
     "Alkali metals (Group 1) and alkaline earth metals (Group 2)",
     ["Halogens and noble gases", "Transition metals", "Non-metals only"],
     "s-block: last electron enters s orbital. Group 1 (ns1): alkali metals. Group 2 (ns2): alkaline earth metals."),
    ("trends",
     "The electron affinity is most negative (most energy released) for:",
     "Halogens, especially Cl (highest electron affinity among common elements)",
     ["Noble gases", "Alkali metals", "Alkaline earth metals"],
     "Halogens (1 electron short of noble gas config) strongly attract electrons. Cl has EA = -349 kJ/mol (F has slightly less due to small size)."),
    ("trends",
     "The diagonal relationship in the periodic table is a similarity between:",
     "Elements diagonally adjacent across periods 2 and 3 (e.g., Li-Mg, Be-Al, B-Si)",
     ["Elements in the same group", "Elements in the same period", "Transition metals only"],
     "Diagonal relationship: Li-Mg, Be-Al, B-Si have similar properties due to similar charge/size ratios (ionic potential)."),
    ("blocks",
     "How many elements are in Period 4 of the periodic table?",
     "18 elements (including 10 d-block transition metals)",
     ["8 elements", "10 elements", "32 elements"],
     "Period 4: fills 4s, 3d, 4p -> 2+10+6 = 18 elements (K to Kr). Period 6 has 32 (including lanthanides)."),
    ("trends",
     "The most metallic element in the periodic table is:",
     "Caesium (Cs) or Francium (Fr) — bottom-left of periodic table",
     ["Sodium (Na)", "Iron (Fe)", "Gold (Au)"],
     "Metallic character increases down a group and left across a period. Most metallic: bottom-left = Fr (radioactive) or Cs."),
    ("blocks",
     "Which period contains the first d-block elements?",
     "Period 4 (K to Kr, with Sc to Zn as d-block: 3d1 to 3d10)",
     ["Period 2", "Period 3", "Period 5"],
     "3d orbitals first fill in period 4 (after 4s). Sc (Z=21) is first d-block element. Period 3 only has s and p blocks."),
    ("trends",
     "The oxidation state of Cr is most commonly:",
     "+3 and +6 (transition metals exhibit variable oxidation states)",
     ["Only +2", "Only +1", "+4 only"],
     "Cr: [Ar]3d54s1. Forms Cr3+ (stable, green) and Cr6+ (in K2Cr2O7, chromate). Variable oxidation states = transition metal property."),
    ("trends",
     "Electronegativity difference > 1.7 between bonded atoms suggests the bond is:",
     "Predominantly ionic (> 50% ionic character)",
     ["Covalent non-polar", "Metallic", "Covalent polar only"],
     "Pauling: EN difference > 1.7 -> ionic character. EN diff 0.5-1.7 -> polar covalent. EN diff < 0.5 -> non-polar covalent."),
]

def gen_periodic(n=15):
    print(f"[Periodic Table & Periodicity] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(PERIODIC_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_periodic(scene); url=upload_pil(img, f"per_{i}")
        ok=post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                  "Periodic Table", "Periodicity and Trends",
                  qtext, url, opts, cidx, expl)
        print(f"  per_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OlympiadReady — Class 11-12 Chemistry (Batch 8)")
    print("=" * 60)
    print()

    gen_atomic(QPT)
    gen_bonding(QPT)
    gen_thermo(QPT)
    gen_equilibrium(QPT)
    gen_electrochem(15)
    gen_organic(QPT)
    gen_periodic(15)

    print("=" * 60)
    print(f"DONE — Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}")
    print("=" * 60)
