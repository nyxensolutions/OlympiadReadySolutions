"""
generate_chemistry_gk.py
Chemistry, GK & Mixed generators — Batch 4:
  1.  Atoms & Molecules         (Grades 7-10)  — text options
  2.  Chemical Reactions        (Grades 7-10)  — text options
  3.  Periodic Table            (Grades 8-10)  — text options
  4.  Acids Bases Salts         (Grades 7-9)   — text options
  5.  Human Senses              (Grades 3-6)   — text options
  6.  Weather & Seasons         (Grades 3-6)   — text options
  7.  Indian Geography          (Grades 5-8)   — text options
  8.  Indian History            (Grades 5-8)   — text options
  9.  Environment & Ecology     (Grades 5-8)   — text options
 10.  Logical Reasoning: Coding (Grades 5-9)   — text options

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
        public_id=f"ch4_{label}_{int(time.time()*1000)}", resource_type="image")
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
        except Exception as e:
            if attempt == 0: time.sleep(2)
            else: FAILED += 1; return False

def canvas(w=500, h=380, bg="white"):
    img = Image.new("RGB",(w,h),bg)
    return img, ImageDraw.Draw(img)


# ══════════════════════════════════════════════════════════════════════════════
# 1. ATOMS & MOLECULES
# ══════════════════════════════════════════════════════════════════════════════

def draw_atom(element="Hydrogen", protons=1, neutrons=0, electrons=1, shells=None):
    img, draw = canvas(460, 380, "#0A0A1E")
    draw.text((20,12), f"Atom: {element}", fill="white", font=FONT_LG)
    cx, cy = 230, 200
    # Nucleus
    nuc_r = 22 + protons * 2
    draw.ellipse([cx-nuc_r,cy-nuc_r,cx+nuc_r,cy+nuc_r], fill="#E74C3C")
    draw.text((cx-18,cy-10), f"p={protons}", fill="white", font=FONT_SM)
    draw.text((cx-18,cy+2),  f"n={neutrons}", fill="white", font=FONT_SM)
    # Electron shells
    if shells is None:
        shells = [electrons]
    orbit_radii = [65, 110, 155]
    colors = ["#3498DB","#27AE60","#F39C12"]
    e_placed = 0
    for shell_idx, (count, r) in enumerate(zip(shells, orbit_radii)):
        draw.ellipse([cx-r,cy-r,cx+r,cy+r], outline=colors[shell_idx], width=2)
        for e in range(count):
            angle = math.radians(e * 360/count)
            ex = cx + int(r * math.cos(angle))
            ey = cy + int(r * math.sin(angle))
            draw.ellipse([ex-6,ey-6,ex+6,ey+6], fill=colors[shell_idx])
        e_placed += count
    draw.text((20,345), f"Protons: {protons}  Neutrons: {neutrons}  Electrons: {electrons}", fill="#AAA", font=FONT_SM)
    return img

def draw_molecule(name, atoms_desc):
    img, draw = canvas(480, 340, "#F0F8FF")
    draw.text((20,12), f"Molecule: {name}", fill="#2C3E50", font=FONT_LG)
    # Draw atoms as labelled circles
    n = len(atoms_desc)
    spacing = min(100, 400//max(n,1))
    start_x = (480 - (n-1)*spacing) // 2
    positions = []
    for i,(label,color,r) in enumerate(atoms_desc):
        x = start_x + i*spacing
        y = 170
        positions.append((x,y))
        draw.ellipse([x-r,y-r,x+r,y+r], fill=color, outline="#2C3E50")
        tw = len(label)*8
        draw.text((x-tw//2, y-10), label, fill="white", font=FONT_MD)
    # Bonds between adjacent atoms
    for i in range(len(positions)-1):
        x1,y1 = positions[i]
        x2,y2 = positions[i+1]
        draw.line([(x1+atoms_desc[i][2],y1),(x2-atoms_desc[i+1][2],y2)], fill="#7F8C8D", width=4)
    draw.text((80, 290), f"Formula: {name}", fill="#2C3E50", font=FONT_LG)
    return img

ATOMS_QA = [
    ("Hydrogen", "The atomic number of an element represents:",
     "Number of protons in the nucleus",
     ["Number of neutrons","Number of electrons in outer shell","Atomic mass"], 1,0,1,[1]),
    ("Helium", "Helium has atomic number 2 and is chemically inert because:",
     "Its outermost shell is completely filled (2 electrons)",
     ["It has no protons","It has 2 neutrons","It has no nucleus"], 2,2,2,[2]),
    ("Carbon", "Carbon has atomic number 6. Its electronic configuration is:",
     "2, 4 (2 in first shell, 4 in second)",
     ["4, 2","6","2, 2, 2"], 6,6,6,[2,4]),
    ("Nitrogen", "Which element has atomic number 7?",
     "Nitrogen (N)", ["Carbon (C)","Oxygen (O)","Fluorine (F)"], 7,7,7,[2,5]),
    ("Oxygen", "Oxygen (atomic number 8) needs _____ more electrons to complete its outer shell:",
     "2", ["1","3","4"], 8,8,8,[2,6]),
    ("Sodium", "Sodium (Na, atomic number 11) has _____ electrons in its outermost shell:",
     "1", ["2","3","4"], 11,12,11,[2,8,1]),
    ("Chlorine", "Chlorine (atomic number 17) has electronic configuration:",
     "2, 8, 7", ["2, 8, 8","2, 7, 8","2, 8, 9"], 17,18,17,[2,8,7]),
    ("Hydrogen", "An isotope of an element has:",
     "Same protons but different number of neutrons",
     ["Same neutrons, different protons","Different atomic number","Different electron count"], 1,0,1,[1]),
    ("Carbon", "The mass number of an atom is:",
     "Protons + Neutrons",
     ["Protons only","Electrons + Protons","Neutrons only"], 6,6,6,[2,4]),
    ("Helium", "The valency of an element is determined by:",
     "Electrons in the outermost shell (or how many needed to complete it)",
     ["Total electrons","Atomic mass","Number of neutrons"], 2,2,2,[2]),
    ("Oxygen", "How many atoms are in one molecule of water (H₂O)?",
     "3 (2 hydrogen + 1 oxygen)",
     ["2","4","1"], 8,8,8,[2,6]),
    ("Carbon", "The formula CO₂ represents:",
     "1 carbon atom bonded to 2 oxygen atoms",
     ["2 carbon atoms","1 carbon and 1 oxygen","3 atoms of carbon"], 6,6,6,[2,4]),
    ("Sodium", "An ion is formed when an atom:",
     "Gains or loses electrons",
     ["Gains protons","Loses neutrons","Splits in half"], 11,12,11,[2,8,1]),
    ("Nitrogen", "Which of the following is a diatomic molecule?",
     "N₂ (nitrogen gas exists as pairs of atoms)",
     ["Carbon (C)","Argon (Ar)","Helium (He)"], 7,7,7,[2,5]),
    ("Hydrogen", "Dalton's Atomic Theory states that atoms of the same element are:",
     "Identical in mass and properties",
     ["Different sizes","Different masses","Different numbers of protons"], 1,0,1,[1]),
    ("Chlorine", "The charge on a proton is:",
     "Positive (+1)", ["Negative (-1)","Neutral (0)","Zero"], 17,18,17,[2,8,7]),
    ("Carbon", "A molecule of glucose (C₆H₁₂O₆) contains how many atoms in total?",
     "24 atoms (6+12+6)", ["18","6","12"], 6,6,6,[2,4]),
    ("Helium", "Noble gases are chemically inert because they have:",
     "Complete outermost electron shells",
     ["No protons","Very high atomic mass","Very low atomic mass"], 2,2,2,[2]),
    ("Sodium", "The atomic mass unit (amu or u) is used to:",
     "Measure the mass of atoms and molecules",
     ["Measure electrical charge","Measure nuclear radius","Measure electron speed"], 11,12,11,[2,8,1]),
    ("Oxygen", "Avogadro's number (6.022 × 10²³) represents:",
     "Number of particles in one mole of a substance",
     ["Speed of light","Atomic mass of carbon","Charge on an electron"], 8,8,8,[2,6]),
]

def gen_atoms(n=QPT):
    print(f"[Atoms & Molecules] {n} questions...")
    for i,(elem,qtext,correct,wrongs,p,nt,e,shells) in enumerate(ATOMS_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_atom(elem,p,nt,e,shells); url=upload_pil(img,f"atom_{i}")
        g=random.choice([7,8,9,10]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Atoms and Molecules","Atomic Structure",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  atom_{i} ({elem})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 2. CHEMICAL REACTIONS
# ══════════════════════════════════════════════════════════════════════════════

def draw_reaction(rtype):
    img, draw = canvas(540, 360, "#FAFFF0")
    draw.text((20,12), f"Chemical Reaction: {rtype.replace('_',' ').title()}", fill="#2C3E50", font=FONT_MD)

    def beaker(draw, x, y, color, label, liquid_h=60):
        # Beaker outline
        draw.rectangle([x-30,y-liquid_h,x+30,y+60], fill=color, outline="#555", width=2)
        draw.rectangle([x-32,y+55,x+32,y+70], fill="#AAA")  # base
        draw.text((x-len(label)*4,y+72), label, fill="#2C3E50", font=FONT_SM)

    if rtype == "acid_base":
        beaker(draw, 110, 200, "#FFD700", "Acid (HCl)")
        beaker(draw, 260, 200, "#90EE90", "Base (NaOH)")
        draw.text((175,190), "+", fill="#2C3E50", font=FONT_XXL)
        draw.text((320,185), "→", fill="#E74C3C", font=FONT_XXL)
        beaker(draw, 430, 200, "#87CEEB", "Salt + Water")
        draw.text((80,300), "HCl + NaOH → NaCl + H₂O (Neutralisation)", fill="#2C3E50", font=FONT_MD)

    elif rtype == "combustion":
        # Flame
        pts = [(240,280),(200,200),(220,160),(240,130),(260,160),(280,200),(240,280)]
        draw.polygon(pts, fill="#FF4500")
        draw.polygon([(240,250),(220,200),(240,170),(260,200),(240,250)], fill="#FFD700")
        # Arrows
        draw.text((100,80), "Fuel (CH₄) + O₂  →  CO₂ + H₂O + Energy", fill="#2C3E50", font=FONT_MD)
        draw.text((100,120), "Combustion releases light and heat energy", fill="#555", font=FONT_SM)

    elif rtype == "decomposition":
        # Single reactant splits
        beaker(draw, 130, 180, "#DDA0DD", "2H₂O₂")
        draw.text((195,165), "→", fill="#E74C3C", font=FONT_XXL)
        beaker(draw, 290, 180, "#87CEEB", "2H₂O", 40)
        draw.text((350,165), "+", fill="#2C3E50", font=FONT_XXL)
        # Bubbles for O₂
        for bx,by in [(420,200),(430,170),(445,195),(415,175)]:
            draw.ellipse([bx-10,by-10,bx+10,by+10], outline="#4169E1", width=2)
        draw.text((400,248), "O₂", fill="#4169E1", font=FONT_MD)
        draw.text((60,290),"2H₂O₂ → 2H₂O + O₂ (Decomposition by catalyst)",fill="#2C3E50",font=FONT_SM)

    elif rtype == "displacement":
        beaker(draw, 110, 190, "#ADD8E6", "CuSO₄ solution")
        # Iron nail going in
        draw.rectangle([130,100,155,195], fill="#888")
        draw.text((110,82), "Fe nail", fill="#888", font=FONT_SM)
        draw.text((230,175), "→", fill="#E74C3C", font=FONT_XXL)
        beaker(draw, 360, 190, "#90EE90", "FeSO₄")
        # Copper deposit
        draw.rectangle([340,120,365,195], fill="#B87333")
        draw.text((320,102), "Cu deposit", fill="#B87333", font=FONT_SM)
        draw.text((50,300),"Fe + CuSO₄ → FeSO₄ + Cu (Displacement)",fill="#2C3E50",font=FONT_SM)

    return img

REACTION_QA = [
    ("acid_base","The reaction between an acid and a base is called:",
     "Neutralisation",["Combustion","Decomposition","Displacement"]),
    ("combustion","Combustion reactions always require:",
     "Oxygen (or an oxidiser)",["Water","A catalyst","Salt"]),
    ("decomposition","In a decomposition reaction, a single compound:",
     "Breaks down into two or more simpler substances",
     ["Combines with another","Displaces an element","Burns in air"]),
    ("displacement","In a displacement reaction, a more reactive metal:",
     "Displaces a less reactive metal from its salt solution",
     ["Combines with non-metals","Decomposes in water","Forms an acid"]),
    ("acid_base","HCl + NaOH → NaCl + H₂O. The product NaCl is:",
     "Salt",["Acid","Base","Oxide"]),
    ("combustion","The complete combustion of methane (CH₄) produces:",
     "CO₂ and H₂O",["CO and H₂","C and H₂O","CO₂ and H₂"]),
    ("decomposition","When calcium carbonate (CaCO₃) is heated, it decomposes to give:",
     "CaO + CO₂",["Ca + CO₃","CaCO₂ + O","Ca(OH)₂"]),
    ("displacement","Iron is placed in copper sulphate solution. The solution changes from:",
     "Blue to green (CuSO₄ → FeSO₄)",["Green to blue","Colourless to red","No change"]),
    ("acid_base","Which of these is a strong acid?",
     "Hydrochloric acid (HCl)",["Vinegar (acetic acid)","Lemon juice (citric acid)","Baking soda"]),
    ("combustion","Rusting of iron is an example of:",
     "Slow combustion (oxidation)",["Decomposition","Neutralisation","Displacement"]),
    ("decomposition","Electrolysis of water decomposes it into:",
     "H₂ at cathode and O₂ at anode",["O₂ at cathode and H₂ at anode","HCl and NaOH","H₂O₂"]),
    ("displacement","In the reactivity series, which metal is MOST reactive?",
     "Potassium (K)",["Gold","Copper","Iron"]),
    ("acid_base","An indicator turns red in acid and blue in base. This is most likely:",
     "Litmus",["Phenolphthalein","Methyl orange","Universal indicator"]),
    ("combustion","Which law states that mass is conserved in a chemical reaction?",
     "Law of Conservation of Mass",["Law of Definite Proportions","Avogadro's Law","Charles' Law"]),
    ("decomposition","Photosynthesis is an example of which type of reaction?",
     "Endothermic reaction (absorbs energy/light)",
     ["Exothermic","Displacement","Neutralisation"]),
    ("acid_base","Vinegar is an example of a:",
     "Weak acid (acetic acid)",["Strong acid","Strong base","Neutral salt"]),
    ("combustion","Exothermic reactions are reactions that:",
     "Release energy (heat or light)",["Absorb energy","Require electricity","Happen very slowly"]),
    ("displacement","Copper does NOT react with dilute H₂SO₄ because:",
     "Copper is below hydrogen in the reactivity series",
     ["Copper dissolves in bases","Copper is non-metallic","Copper is an alloy"]),
    ("decomposition","Which gas is produced when hydrogen peroxide decomposes?",
     "Oxygen (O₂)",["Hydrogen (H₂)","Carbon dioxide (CO₂)","Nitrogen (N₂)"]),
    ("acid_base","The pH of a neutral solution is:",
     "7",["0","14","10"]),
]

def gen_reactions(n=QPT):
    print(f"[Chemical Reactions] {n} questions...")
    rtypes=["acid_base","combustion","decomposition","displacement"]
    for i,(rtype,qtext,correct,wrongs) in enumerate(REACTION_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_reaction(rtype); url=upload_pil(img,f"rxn_{i}")
        g=random.choice([7,8,9,10]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Chemical Reactions","Types of Reactions",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  rxn_{i} ({rtype})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 3. HUMAN SENSES
# ══════════════════════════════════════════════════════════════════════════════

def draw_sense_organ(sense):
    img, draw = canvas(420, 360, "#FFF9F0")
    draw.text((20,12), f"Sense Organ: {sense.title()}", fill="#2C3E50", font=FONT_LG)

    if sense == "eye":
        # Eye outline
        draw.ellipse([80,120,340,260], fill="white", outline="#333", width=3)
        # Iris
        draw.ellipse([170,145,250,235], fill="#1A6B8A")
        # Pupil
        draw.ellipse([195,165,225,215], fill="#111")
        # Highlight
        draw.ellipse([200,168,210,178], fill="white")
        # Eyelid lines
        draw.arc([80,120,340,260], start=0, end=180, fill="#F5CBA7", width=8)
        # Labels
        draw.text((300,140), "Cornea", fill="#E74C3C", font=FONT_SM)
        draw.text((258,145), "↑", fill="#E74C3C", font=FONT_SM)
        draw.text((150,300), "Eye — sense of SIGHT", fill="#2C3E50", font=FONT_MD)

    elif sense == "ear":
        # Outer ear flap shape
        pts=[(180,80),(140,100),(110,140),(105,180),(115,220),(140,255),(175,270),(200,260),(210,240),(200,200),(215,180),(200,160),(210,130),(210,100)]
        draw.polygon(pts, fill="#F5CBA7", outline="#8B6914", width=2)
        # Ear canal
        draw.ellipse([195,185,240,225], fill="#333")
        draw.text((250,160), "Ear canal", fill="#555", font=FONT_SM)
        draw.text((90,300), "Ear — sense of HEARING", fill="#2C3E50", font=FONT_MD)

    elif sense == "nose":
        # Simple nose shape
        draw.ellipse([160,80,260,180], fill="#F5CBA7", outline="#8B6914", width=2)
        draw.ellipse([140,150,200,220], fill="#F5CBA7", outline="#8B6914", width=2)
        draw.ellipse([220,150,280,220], fill="#F5CBA7", outline="#8B6914", width=2)
        # Nostrils
        draw.ellipse([155,175,188,205], fill="#C4956A")
        draw.ellipse([232,175,265,205], fill="#C4956A")
        draw.text((100,290), "Nose — sense of SMELL", fill="#2C3E50", font=FONT_MD)

    elif sense == "tongue":
        # Tongue shape
        pts=[(210,60),(175,80),(155,120),(150,165),(160,210),(185,240),(210,255),(235,240),(260,210),(270,165),(265,120),(245,80)]
        draw.polygon(pts, fill="#FF7F7F", outline="#CC4444", width=2)
        # Taste buds (dots)
        for tx,ty in [(190,100),(215,90),(235,110),(175,140),(200,130),(225,140),(250,130),
                      (170,175),(195,165),(220,175),(245,165),(190,210),(215,200),(240,210)]:
            draw.ellipse([tx-4,ty-4,tx+4,ty+4], fill="#CC4444")
        draw.text((100,290), "Tongue — sense of TASTE", fill="#2C3E50", font=FONT_MD)

    elif sense == "skin":
        # Cross-section of skin
        draw.rectangle([50,100,380,260], fill="#F5CBA7", outline="#8B6914", width=2)
        draw.text((190,108), "Epidermis", fill="#8B6914", font=FONT_SM)
        draw.rectangle([50,145,380,260], fill="#E8A87C")
        draw.text((190,152), "Dermis", fill="#8B6914", font=FONT_SM)
        # Hair follicle
        draw.line([(210,100),(210,220)], fill="#5D4037", width=3)
        draw.text((220,200), "Hair follicle", fill="#555", font=FONT_SM)
        # Nerve ending
        draw.ellipse([150,165,170,185], fill="#3498DB")
        draw.text((100,188), "Nerve", fill="#3498DB", font=FONT_SM)
        # Sweat gland
        pts=[(300,150),(300,220),(290,240),(310,240),(300,220)]
        draw.line([(300,150),(300,230)], fill="#27AE60", width=2)
        draw.text((270,238), "Sweat", fill="#27AE60", font=FONT_SM)
        draw.text((90,290), "Skin — sense of TOUCH", fill="#2C3E50", font=FONT_MD)

    return img

SENSES_QA = [
    ("eye","Which sense organ is responsible for the sense of sight?",
     "Eyes",["Ears","Nose","Tongue"]),
    ("ear","The sense of hearing is provided by which organ?",
     "Ears",["Eyes","Nose","Skin"]),
    ("nose","Which organ gives us the sense of smell?",
     "Nose",["Tongue","Skin","Ears"]),
    ("tongue","The tongue is responsible for which sense?",
     "Taste",["Smell","Touch","Sight"]),
    ("skin","The skin provides the sense of:",
     "Touch (and also heat, cold, pain)",
     ["Sight","Smell","Hearing"]),
    ("eye","The coloured part of the eye that controls light entry is called the:",
     "Iris",["Pupil","Cornea","Retina"]),
    ("ear","The part of the ear that vibrates when sound waves enter is the:",
     "Eardrum (tympanic membrane)",["Cochlea","Pinna","Ear canal"]),
    ("nose","The sense of smell is detected by receptor cells in the:",
     "Olfactory epithelium (lining of nasal cavity)",
     ["Tongue","Cornea","Skin"]),
    ("tongue","The four basic tastes detected by the tongue are:",
     "Sweet, salty, sour and bitter (umami is the fifth)",
     ["Spicy, sweet, sour, bitter","Sweet, sour, cold, hot","Sweet, salty, spicy, bitter"]),
    ("skin","Which layer of skin contains nerve endings, sweat glands and hair follicles?",
     "Dermis",["Epidermis","Subcutaneous fat","Bone marrow"]),
    ("eye","The transparent outer covering of the eye is called the:",
     "Cornea",["Iris","Lens","Retina"]),
    ("ear","The three small bones in the middle ear are collectively called:",
     "Ossicles (malleus, incus, stapes)",
     ["Cochlea","Semicircular canals","Pinna"]),
    ("nose","Dogs have a much better sense of smell than humans because they have:",
     "More olfactory receptor cells",
     ["Larger nostrils","Better eyesight to find smells","Longer tongues"]),
    ("eye","The image formed on the retina is:",
     "Inverted (upside down) — the brain corrects this",
     ["Upright","Magnified","Identical to real object"]),
    ("skin","Goosebumps appear on the skin when we are cold because:",
     "Tiny muscles at hair follicles contract, raising the hair",
     ["Blood rushes to skin","Sweat glands expand","Nerve endings fire rapidly"]),
]

def gen_senses(n=QPT):
    n=min(n,len(SENSES_QA))
    print(f"[Human Senses] {n} questions...")
    for i,(sense,qtext,correct,wrongs) in enumerate(SENSES_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_sense_organ(sense); url=upload_pil(img,f"sense_{i}")
        g=random.choice([3,4,5,6]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Human Senses","Sense Organs",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  sense_{i} ({sense})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 4. WEATHER & SEASONS
# ══════════════════════════════════════════════════════════════════════════════

def draw_weather(scene):
    img, draw = canvas(460, 340)

    if scene == "sunny":
        img = Image.new("RGB",(460,340),"#87CEEB")
        draw = ImageDraw.Draw(img)
        draw.text((20,12),"Weather: Sunny",fill="#2C3E50",font=FONT_LG)
        # Sun
        cx,cy=230,180
        draw.ellipse([cx-50,cy-50,cx+50,cy+50],fill="#FFD700")
        for a in range(0,360,30):
            rad=math.radians(a); ex=cx+int(75*math.cos(rad)); ey=cy+int(75*math.sin(rad))
            draw.line([(cx+int(55*math.cos(rad)),cy+int(55*math.sin(rad))),(ex,ey)],fill="#FFD700",width=3)
        draw.text((140,295),"Clear skies, bright sunlight",fill="#2C3E50",font=FONT_MD)

    elif scene == "rainy":
        img = Image.new("RGB",(460,340),"#708090")
        draw = ImageDraw.Draw(img)
        draw.text((20,12),"Weather: Rainy",fill="white",font=FONT_LG)
        # Clouds
        for cx,cy,r in [(150,100,45),(190,80,55),(230,100,45),(100,110,35)]:
            draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill="#B0C4DE")
        # Rain drops
        for rx,ry in [(80,170),(120,190),(160,165),(200,185),(240,170),(280,195),(320,168),(350,185),(380,170)]:
            draw.line([(rx,ry),(rx-5,ry+25)],fill="#4169E1",width=2)
        draw.text((120,295),"Rain: water droplets fall from clouds",fill="white",font=FONT_MD)

    elif scene == "seasons":
        img = Image.new("RGB",(460,340),"#F5F5F5")
        draw = ImageDraw.Draw(img)
        draw.text((20,12),"Four Seasons",fill="#2C3E50",font=FONT_LG)
        seasons=[("Spring","#90EE90",80,100),("Summer","#FFD700",240,100),
                 ("Autumn","#FF8C00",80,220),("Winter","#ADD8E6",240,220)]
        for name,color,bx,by in seasons:
            draw.rectangle([bx-60,by-30,bx+60,by+30],fill=color)
            draw.text((bx-len(name)*5,by-10),name,fill="#2C3E50",font=FONT_MD)
        draw.text((80,295),"India has Summer, Monsoon, Winter seasons",fill="#555",font=FONT_MD)

    elif scene == "monsoon":
        img = Image.new("RGB",(460,340),"#1C3A5E")
        draw = ImageDraw.Draw(img)
        draw.text((20,12),"Indian Monsoon",fill="white",font=FONT_LG)
        # India shape (rough outline)
        india_pts=[(230,60),(280,80),(320,120),(340,160),(330,210),(300,260),(260,290),(230,310),(200,290),(160,260),(140,210),(145,165),(170,120),(200,85)]
        draw.polygon(india_pts,fill="#27AE60",outline="#2C3E50",width=2)
        # Rain arrows from SW
        for ix in range(60,230,40):
            draw.line([(ix,260),(ix+30,180)],fill="#4169E1",width=2)
            draw.polygon([(ix+30,180),(ix+22,195),(ix+38,195)],fill="#4169E1")
        draw.text((30,210),"SW Monsoon",fill="#87CEEB",font=FONT_MD)
        draw.text((50,300),"June-Sept: Southwest monsoon brings rain",fill="white",font=FONT_SM)

    return img

WEATHER_QA = [
    ("seasons","Which season in India is characterised by heavy rainfall from June to September?",
     "Monsoon (South-West Monsoon)",["Winter","Spring","Autumn"]),
    ("rainy","Clouds are formed when:",
     "Water vapour condenses around dust particles in the atmosphere",
     ["Wind blows over seas","Rivers evaporate","Ice melts on mountains"]),
    ("sunny","The instrument used to measure rainfall is called:",
     "Rain gauge",["Barometer","Thermometer","Hygrometer"]),
    ("seasons","How many main seasons does India experience in a year?",
     "3 main seasons (Summer, Monsoon, Winter)",["4","2","6"]),
    ("monsoon","The South-West Monsoon in India arrives in Kerala around:",
     "June 1st",["March 1st","December 1st","September 1st"]),
    ("rainy","Humidity refers to:",
     "The amount of water vapour present in the air",
     ["Amount of rainfall","Wind speed","Air pressure"]),
    ("sunny","Which instrument measures atmospheric pressure?",
     "Barometer",["Anemometer","Hygrometer","Rain gauge"]),
    ("rainy","Thunder is caused by:",
     "Rapid expansion of air heated by lightning",
     ["Clouds colliding","Heavy raindrops hitting ground","Hail formation"]),
    ("seasons","The North-East Monsoon mainly affects which part of India?",
     "Tamil Nadu and South-East India (October-December)",
     ["Punjab and Haryana","Rajasthan","Gujarat"]),
    ("sunny","Anemometer is used to measure:",
     "Wind speed",["Rainfall","Temperature","Humidity"]),
    ("monsoon","Which ocean current brings moisture to India's SW Monsoon?",
     "Indian Ocean / Arabian Sea currents",["Pacific Ocean","Atlantic Ocean","Arctic Ocean"]),
    ("rainy","Lightning is caused by:",
     "Build-up and discharge of static electricity between clouds",
     ["Sun's radiation","Strong winds","Rapid cooling"]),
    ("seasons","In India, the summer season is generally from:",
     "March to May",["June to September","October to February","December to February"]),
    ("sunny","Dew is formed when:",
     "Water vapour in air condenses on cool surfaces at night",
     ["Rain evaporates quickly","Rivers overflow","Ice melts in morning"]),
    ("monsoon","Western Ghats receive heavy rainfall during SW Monsoon because:",
     "They act as a barrier, causing orographic (relief) rainfall on windward side",
     ["They are near the sea","They are high altitude","They are cold regions"]),
]

def gen_weather(n=QPT):
    n=min(n,len(WEATHER_QA))
    print(f"[Weather & Seasons] {n} questions...")
    for i,(scene,qtext,correct,wrongs) in enumerate(WEATHER_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_weather(scene); url=upload_pil(img,f"weather_{i}")
        g=random.choice([4,5,6,7]); d=difficulty_for_grade(g)
        ok=post_q("Science",g,d,"Weather and Climate","Seasons and Monsoon",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  weather_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 5. INDIAN GEOGRAPHY
# ══════════════════════════════════════════════════════════════════════════════

def draw_india_map(highlight_region=None):
    img, draw = canvas(400, 460, "#E0F0FF")
    draw.text((100,12),"Map of India",fill="#2C3E50",font=FONT_LG)
    # Simplified India outline (rough polygon)
    india = [(200,50),(240,55),(280,70),(310,90),(335,120),(350,155),(345,190),
             (340,230),(320,275),(300,310),(270,340),(250,370),(230,395),(215,410),
             (200,415),(185,410),(170,395),(155,370),(140,345),(125,315),(110,280),
             (100,245),(95,210),(100,175),(110,145),(130,115),(155,90),(180,68)]
    draw.polygon(india, fill="#90EE90", outline="#2C3E50", width=2)
    # Key cities / regions
    regions = {
        "Delhi":      (200,160,"#E74C3C"),
        "Mumbai":     (130,280,"#3498DB"),
        "Chennai":    (220,350,"#E74C3C"),
        "Kolkata":    (280,240,"#E74C3C"),
        "Bengaluru":  (190,330,"#9B59B6"),
        "Himalaya":   (195,60,"#7F8C8D"),
        "Rajasthan":  (145,190,"#F39C12"),
        "Deccan":     (185,295,"#8B6914"),
    }
    for name,(rx,ry,color) in regions.items():
        is_hi = (name==highlight_region)
        fc = "#FF0000" if is_hi else color
        draw.ellipse([rx-6,ry-6,rx+6,ry+6],fill=fc)
        draw.text((rx+8,ry-8),name,fill=fc,font=FONT_SM)
    # Water bodies
    draw.text((30,280),"Arabian\nSea",fill="#2980B9",font=FONT_SM)
    draw.text((310,290),"Bay of\nBengal",fill="#2980B9",font=FONT_SM)
    draw.text((170,440),"Indian Ocean",fill="#2980B9",font=FONT_SM)
    return img

INDIA_GEO_QA = [
    ("Delhi","What is the capital city of India?",
     "New Delhi",["Mumbai","Chennai","Kolkata"]),
    ("Mumbai","Which city is known as the financial capital of India?",
     "Mumbai",["Delhi","Bengaluru","Hyderabad"]),
    ("Himalaya","The Himalayas form the northern boundary of India. Which is the highest peak in India?",
     "Kangchenjunga (in Sikkim)",["Mount Everest (Nepal)","K2 (Pakistan)","Nanda Devi"]),
    ("Rajasthan","Which is the largest state of India by area?",
     "Rajasthan",["Uttar Pradesh","Madhya Pradesh","Maharashtra"]),
    ("Deccan","The Deccan Plateau is located in:",
     "Central and South India",["North India","North-East India","Islands"]),
    ("Chennai","The Palk Strait separates India from:",
     "Sri Lanka",["Pakistan","Bangladesh","Myanmar"]),
    ("Kolkata","The Sundarbans, the world's largest mangrove forest, is located in:",
     "West Bengal (India) and Bangladesh",["Kerala","Maharashtra","Odisha"]),
    ("Delhi","The river Ganga originates from:",
     "Gangotri Glacier in Uttarakhand",["Tibet","Nepal","Himachal Pradesh"]),
    ("Mumbai","Which is the longest river in India?",
     "Ganga (about 2,525 km)",["Yamuna","Godavari","Indus"]),
    ("Rajasthan","The Thar Desert is located primarily in:",
     "Rajasthan",["Gujarat","Punjab","Haryana"]),
    ("Himalaya","Which Indian state has the longest coastline?",
     "Gujarat",["Kerala","Maharashtra","Andhra Pradesh"]),
    ("Bengaluru","Which city is known as the 'Silicon Valley of India'?",
     "Bengaluru (Bangalore)",["Hyderabad","Pune","Chennai"]),
    ("Deccan","The Western Ghats run parallel to which coast?",
     "Western (Malabar) coast",["Eastern coast","Northern coast","None"]),
    ("Chennai","Which is the southernmost tip of mainland India?",
     "Kanyakumari (Cape Comorin)",["Rameswaram","Tuticorin","Kovalam"]),
    ("Kolkata","Which river flows through Kolkata?",
     "Hooghly (a distributary of Ganga)",["Brahmaputra","Damodar","Mahanadi"]),
    ("Delhi","The Tropic of Cancer passes through how many Indian states?",
     "8 states",["6 states","10 states","5 states"]),
    ("Mumbai","Which is India's smallest state by area?",
     "Goa",["Sikkim","Tripura","Manipur"]),
    ("Himalaya","The Brahmaputra river originates from:",
     "Tibet (as Yarlung Tsangpo)",["Himachal Pradesh","Arunachal Pradesh","China directly"]),
    ("Rajasthan","Which is the coldest inhabited place in India?",
     "Dras (Ladakh) — often -40°C in winter",["Shimla","Manali","Ooty"]),
    ("Bengaluru","Lakshadweep islands are located in the:",
     "Arabian Sea",["Bay of Bengal","Indian Ocean","Pacific Ocean"]),
]

def gen_india_geo(n=QPT):
    print(f"[Indian Geography] {n} questions...")
    for i,(region,qtext,correct,wrongs) in enumerate(INDIA_GEO_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_india_map(region); url=upload_pil(img,f"indiageo_{i}")
        g=random.choice([5,6,7,8]); d=difficulty_for_grade(g)
        ok=post_q("General Knowledge",g,d,"Indian Geography","Indian States and Geography",qtext,url,opts,cidx,f"Answer: {correct}.")
        print(f"  geo_{i} ({region})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# 6. LOGICAL REASONING: CODING-DECODING
# ══════════════════════════════════════════════════════════════════════════════

def draw_coding(encoded, decoded, rule_desc):
    img, draw = canvas(500, 300, "#F0F8FF")
    draw.text((20,12), "Coding-Decoding Problem", fill="#2C3E50", font=FONT_LG)
    # Show example
    draw.rectangle([50,70,220,130], fill="#3498DB", outline="#2C3E50", width=2)
    draw.text((80,88), "Word:", fill="white", font=FONT_SM)
    draw.text((75,105), decoded, fill="#FFD700", font=FONT_LG)
    # Arrow
    draw.text((230,95), "→", fill="#E74C3C", font=FONT_XXL)
    # Code
    draw.rectangle([280,70,450,130], fill="#E74C3C", outline="#2C3E50", width=2)
    draw.text((295,88), "Code:", fill="white", font=FONT_SM)
    draw.text((290,105), encoded, fill="#FFD700", font=FONT_LG)
    # Rule
    draw.text((60,155), f"Pattern: {rule_desc}", fill="#2C3E50", font=FONT_MD)
    draw.rectangle([50,185,450,240], fill="#FFFACD", outline="#F39C12", width=2)
    draw.text((60,200), "? Find the code / decode the word ?", fill="#E74C3C", font=FONT_MD)
    return img

CODING_QA = [
    # (encoded, decoded, rule, question, correct, wrongs)
    ("DBU","CAT","+1 each letter","If CAT is coded as DBU, what is DOG coded as?",
     "EPH",["DOH","EQH","EPG"]),
    ("GJTI","FISH","+1 each letter","If FISH is coded as GJTI, what is BIRD coded as?",
     "CJSE",["BJRD","CISE","BIRE"]),
    ("NBOH","MANGO","-1 each letter (first 4 only shown)","If MANGO is coded as NBOH (first 4 letters), APPLE would be coded as?",
     "BQQMF",["APPLD","BQPME","AQQLE"]),
    ("46214","CABAL","A=1,B=2... code","In a code, A=1, B=2, C=3... What is the code for FACE?",
     "6135",["1365","6315","6153"]),
    ("TCAT","SBZS","-1 each letter","If STAR is coded as RSZQ, what is MOON coded as?",
     "LNNM",["MOON","NOON","MNNO"]),
    ("RIVER","SJWFS","+1 each letter","If RIVER is coded as SJWFS, what is LAKE coded as?",
     "MBLF",["LAKE","MBKE","LAKF"]),
    ("24","BD","A=1,B=2","In a code A=1, B=2... If 3-1-20 means CAT, what does 4-15-7 mean?",
     "DOG",["COG","DOH","DAG"]),
    ("ELPPA","APPLE","reverse letters","If APPLE is coded as ELPPA (reversed), what is MANGO coded as?",
     "OGNAM",["MGANO","ONGAM","OGAMN"]),
    ("16-5-14","PEN","A=1 number code","In a number code (A=1,B=2...), 2-15-15-11 means:",
     "BOOK",["LOOK","COOK","BOON"]),
    ("ZAP","YZO","-1 each","If ZAP = YZO (-1 each letter), what does WIN decode to?",
     "VHM",["WHM","VIM","VHN"]),
    ("QFSDJM","PENCIL","+1 each","If PENCIL is coded as QFSDJM, PAPER is coded as:",
     "QBQFS",["PAPER","QAPFR","PBPFS"]),
    ("OGVI","LIFE","N+1=O, etc: reverse +1","If LIFE = OGVI, what does DOOR decode back to?",
     "CNNO",["DOOR","DNNO","CNOP"]),
    ("3579","CEGI","odd positions A=1","If A=1,B=2... and odd numbers map to vowels positions, what is 2-1-19-5?",
     "BASE",["CASE","BAZE","BACE"]),
    ("VKPI","THIS","+2 each letter","If THIS is coded as VJKU (+2), what is GOOD coded as?",
     "IQQF",["HPPE","GOOF","IQOF"]),
    ("PHHOH","MANGO","+3 each letter","If MANGO = PDQJR (+3), APPLE = ?",
     "DSSOH",["CRRNG","ERRTJ","DRTOH"]),
    ("STUVWX","QRSTUVW","Letters shift","Which code correctly represents alphabets shifted forward by 2: A→C?",
     "C=A+2 means A is coded as C",["A is coded as Z","A is coded as B","A is coded as Y"]),
    ("246","ACE","even = vowel pos","If vowels A,E,I,O,U are coded 1,2,3,4,5, what is the code for AIR?",
     "135",["153","315","513"]),
    ("43215","EDCBA","reverse alphabet order","If Z=1, Y=2, X=3... A=26, what is the code for CAT?",
     "24-3-7",["3-1-20","24-26-7","3-26-7"]),
    ("MOUSE","PRXVH","+3 each","If MOUSE is coded as PRXVH, TABLE is coded as:",
     "WDEOH",["WDFOH","XDGPI","VDEOH"]),
    ("BCDE","ABCD","+1 shift","If +1 shift means A→B, B→C... what does HELLO decode to (reverse, -1)?",
     "GDKKN",["HELLO","IFMMP","GDLLN"]),
]

def gen_coding_decoding(n=QPT):
    print(f"[Coding-Decoding] {n} questions...")
    for i,(enc,dec,rule,qtext,correct,wrongs) in enumerate(CODING_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_coding(enc,dec,rule); url=upload_pil(img,f"code_{i}")
        g=random.choice([5,6,7,8,9]); d=difficulty_for_grade(g)
        ok=post_q("Logical Reasoning",g,d,"Coding and Decoding","Letter Coding",qtext,url,opts,cidx,f"Answer: {correct}. {rule}.")
        print(f"  code_{i}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*60)
    print("OlympiadReady — Chemistry, GK & LR Generator Batch 4")
    print("="*60)
    print()

    gen_atoms(QPT)
    gen_reactions(QPT)
    gen_senses(QPT)
    gen_weather(QPT)
    gen_india_geo(QPT)
    gen_coding_decoding(QPT)

    print("="*60)
    print(f"DONE — Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}")
    print("="*60)
