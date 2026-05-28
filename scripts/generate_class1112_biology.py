"""
generate_class1112_biology.py
Class 11-12 Biology — Batch 9
All answers verified against NCERT syllabus and SOF NSO standards.

Generators:
  1. Cell Biology            (Class 11) — 20 questions
  2. Genetics & Heredity     (Class 12) — 20 questions
  3. Human Physiology        (Class 11) — 20 questions
  4. Plant Biology           (Class 11) — 20 questions
  5. Ecology & Environment   (Class 12) — 15 questions
  6. Evolution               (Class 12) — 15 questions

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
        public_id=f"p9_{label}_{int(time.time()*1000)}", resource_type="image")
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


# ==============================================================================
# 1. CELL BIOLOGY  (Class 11)
# ==============================================================================

def draw_cell(scene="animal_cell"):
    img, draw = canvas(540, 420, "#F0FFF4")
    draw.text((20, 8), f"Cell Biology: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "animal_cell":
        cx, cy = 270, 230
        # Cell membrane
        draw.ellipse([cx-200, cy-150, cx+200, cy+150], fill="#FDFEFE", outline="#E74C3C", width=3)
        draw.text((20, 50), "Cell membrane", fill="#E74C3C", font=FONT_SM)
        # Nucleus
        draw.ellipse([cx-50, cy-45, cx+50, cy+45], fill="#D6EAF8", outline="#2980B9", width=2)
        draw.text((cx-25, cy-12), "Nucleus", fill="#2980B9", font=FONT_SM)
        # Nucleolus
        draw.ellipse([cx-18, cy-18, cx+18, cy+18], fill="#2980B9")
        draw.text((cx-20, cy-8), "Nu", fill="white", font=FONT_SM)
        # Mitochondria
        draw.ellipse([cx+65, cy-25, cx+130, cy+5], fill="#F9E79F", outline="#F39C12", width=2)
        draw.text((cx+68, cy-15), "Mito.", fill="#F39C12", font=FONT_SM)
        # Golgi
        for k in range(4):
            draw.arc([cx-110, cy+20+k*8, cx-40, cy+40+k*8], 0, 180, fill="#8E44AD", width=2)
        draw.text((cx-130, cy+55), "Golgi", fill="#8E44AD", font=FONT_SM)
        # Lysosome
        draw.ellipse([cx+65, cy+50, cx+100, cy+80], fill="#EC7063", outline="#C0392B", width=2)
        draw.text((cx+63, cy+85), "Lyso.", fill="#C0392B", font=FONT_SM)
        # Centriole
        draw.rectangle([cx-170, cy+30, cx-140, cy+60], fill="#AAB7B8", outline="#717D7E", width=1)
        draw.text((cx-185, cy+65), "Centriole", fill="#717D7E", font=FONT_SM)
        draw.text((20, 400), "Animal cell: no cell wall, no chloroplast, has centrioles", fill="#7F8C8D", font=FONT_SM)

    elif scene == "plant_cell":
        cx, cy = 270, 220
        # Cell wall (outer)
        draw.rectangle([cx-200, cy-155, cx+200, cy+155], fill="#FDFEFE", outline="#27AE60", width=4)
        draw.text((20, 50), "Cell wall (cellulose)", fill="#27AE60", font=FONT_SM)
        # Cell membrane (inner)
        draw.rectangle([cx-190, cy-145, cx+190, cy+145], outline="#E74C3C", width=2)
        # Large vacuole
        draw.ellipse([cx-80, cy-60, cx+80, cy+80], fill="#AED6F1", outline="#2980B9", width=2)
        draw.text((cx-45, cy+5), "Central vacuole", fill="#2980B9", font=FONT_SM)
        # Nucleus
        draw.ellipse([cx-160, cy-100, cx-80, cy-30], fill="#D6EAF8", outline="#2980B9", width=2)
        draw.text((cx-155, cy-70), "Nucleus", fill="#2980B9", font=FONT_SM)
        # Chloroplast
        draw.ellipse([cx+90, cy-110, cx+185, cy-70], fill="#52BE80", outline="#1E8449", width=2)
        draw.text((cx+90, cy-65), "Chloroplast", fill="#1E8449", font=FONT_SM)
        draw.text((20, 400), "Plant cell: cell wall, large vacuole, chloroplasts — no centrioles", fill="#7F8C8D", font=FONT_SM)

    elif scene == "mitosis":
        draw.text((30, 40), "Mitosis — Cell Division Stages", fill="#1A5276", font=FONT_LG)
        stages = [
            ("Interphase", "DNA replication (S phase), cell growth"),
            ("Prophase",   "Chromatin condenses into chromosomes"),
            ("Metaphase",  "Chromosomes align at cell equator (plate)"),
            ("Anaphase",   "Sister chromatids pulled to opposite poles"),
            ("Telophase",  "Nuclear envelope reforms, cytokinesis begins"),
            ("Cytokinesis","Cell splits into 2 identical daughter cells"),
        ]
        y = 90
        for stage, desc in stages:
            draw.text((30, y), stage + ":", fill="#E74C3C", font=FONT_MD)
            draw.text((170, y), desc, fill="#2C3E50", font=FONT_SM)
            y += 48
        draw.text((30, 395), "Result: 2 diploid (2n) genetically identical cells", fill="#27AE60", font=FONT_SM)

    elif scene == "organelles":
        draw.text((30, 35), "Cell Organelles and Functions", fill="#1A5276", font=FONT_LG)
        data = [
            ("Mitochondria", "Powerhouse — ATP production (aerobic respiration)", "#F39C12"),
            ("Ribosome",     "Protein synthesis (translation of mRNA)",           "#E74C3C"),
            ("Nucleus",      "Control centre — contains DNA and directs cell",     "#2980B9"),
            ("Golgi body",   "Modifies, packages, ships proteins/lipids",          "#8E44AD"),
            ("Lysosome",     "Intracellular digestion (hydrolytic enzymes)",        "#C0392B"),
            ("Chloroplast",  "Photosynthesis (plants only, has chlorophyll)",       "#27AE60"),
            ("Endoplasmic R","Rough (ribosomes): protein synthesis; Smooth: lipids","#7F8C8D"),
        ]
        y = 85
        for org, func, col in data:
            draw.text((30, y), org + ":", fill=col, font=FONT_SM)
            draw.text((175, y), func, fill="#2C3E50", font=FONT_SM)
            y += 43
    return img

CELL_QA = [
    ("animal_cell",
     "Which organelle is called the 'powerhouse of the cell'?",
     "Mitochondria (produces ATP through aerobic respiration)",
     ["Nucleus", "Ribosome", "Golgi apparatus"],
     "Mitochondria produce ATP via cellular respiration (Krebs cycle + oxidative phosphorylation). More active cells have more mitochondria."),
    ("plant_cell",
     "Which structure is present in plant cells but NOT in animal cells?",
     "Cell wall (made of cellulose) and chloroplasts",
     ["Cell membrane", "Nucleus", "Mitochondria"],
     "Plant cells have: cell wall (cellulose), chloroplasts, large central vacuole — absent in animal cells. Animal cells have centrioles."),
    ("mitosis",
     "In which phase of mitosis do chromosomes align at the cell's equatorial plate?",
     "Metaphase",
     ["Prophase", "Anaphase", "Telophase"],
     "Metaphase: chromosomes line up at the metaphase plate (cell equator). Spindle fibres attach to centromeres. Used for karyotyping."),
    ("organelles",
     "Ribosomes are responsible for:",
     "Protein synthesis (translation — reading mRNA to make polypeptides)",
     ["ATP production", "DNA replication", "Lipid synthesis"],
     "Ribosomes translate mRNA into proteins. Found free in cytoplasm (cytosolic proteins) or on rough ER (secretory proteins)."),
    ("animal_cell",
     "The fluid-mosaic model describes the structure of:",
     "Cell membrane (plasma membrane) — phospholipid bilayer with embedded proteins",
     ["Nuclear membrane", "Cell wall", "Mitochondrial matrix"],
     "Singer-Nicholson (1972) Fluid Mosaic Model: phospholipid bilayer (fluid) with proteins (mosaic) embedded. Selectively permeable."),
    ("mitosis",
     "Mitosis produces:",
     "Two genetically identical diploid (2n) daughter cells",
     ["Four haploid cells", "Two haploid cells", "Four diploid cells"],
     "Mitosis: 1 cell -> 2 identical cells (same chromosome number). Used for growth, repair, asexual reproduction. Compare: meiosis -> 4 haploid cells."),
    ("plant_cell",
     "The process by which plants make their food using sunlight is called:",
     "Photosynthesis (in chloroplasts: 6CO2 + 6H2O + light -> C6H12O6 + 6O2)",
     ["Respiration", "Transpiration", "Osmosis"],
     "Photosynthesis: light energy captured by chlorophyll in chloroplasts converts CO2 + H2O -> glucose + O2. Light and dark reactions."),
    ("organelles",
     "The Golgi apparatus functions as:",
     "The cell's post office — modifies, packages, and ships proteins and lipids",
     ["Site of ATP synthesis", "Site of DNA replication", "Site of lipid breakdown"],
     "Golgi: receives vesicles from rough ER, modifies proteins (glycosylation), packages into vesicles for secretion or lysosomes."),
    ("animal_cell",
     "Osmosis is defined as the movement of water:",
     "From a region of higher water potential (hypotonic) to lower water potential (hypertonic) through a semipermeable membrane",
     ["From high solute to low solute", "Requiring energy (active transport)", "Against concentration gradient"],
     "Osmosis: passive movement of water across semipermeable membrane from dilute (hypotonic) to concentrated (hypertonic) solution."),
    ("mitosis",
     "In which phase of the cell cycle does DNA replication occur?",
     "S phase (Synthesis phase) of Interphase",
     ["M phase (Mitosis)", "G1 phase", "G2 phase"],
     "Interphase = G1 (growth) + S (DNA synthesis/replication) + G2 (prep for division). DNA amount doubles in S phase."),
    ("organelles",
     "Lysosomes are known as the 'suicide bags' of the cell because:",
     "They contain hydrolytic enzymes that can digest the cell itself (autolysis) if ruptured",
     ["They produce ATP", "They contain DNA", "They store food"],
     "Lysosomes: membrane-bound sacs with digestive enzymes (lipases, proteases, nucleases). Digest worn-out organelles; if ruptured, digest cell itself."),
    ("plant_cell",
     "The large central vacuole in plant cells serves to:",
     "Maintain turgor pressure, store nutrients/waste, provide structural support",
     ["Produce ATP", "Synthesise proteins", "Replicate DNA"],
     "Central vacuole: occupies up to 90% of plant cell volume. Filled with cell sap; maintains turgor pressure keeping plant rigid."),
    ("mitosis",
     "During anaphase of mitosis, what moves toward the poles?",
     "Sister chromatids (after centromere splits, pulled by spindle fibres)",
     ["Whole chromosomes (unsplit)", "Nuclear envelope fragments", "Nucleolus"],
     "Anaphase: centromeres split, spindle fibres shorten, pulling sister chromatids to opposite poles. Each pole gets a full set of chromosomes."),
    ("animal_cell",
     "Active transport differs from passive transport because active transport:",
     "Requires ATP energy and moves substances against their concentration gradient",
     ["Moves substances with the gradient", "Does not require a membrane", "Only works for water"],
     "Active transport: uses energy (ATP) + carrier proteins to move substances against their concentration gradient. e.g., Na+/K+ pump."),
    ("organelles",
     "Smooth endoplasmic reticulum (SER) is primarily involved in:",
     "Lipid synthesis, detoxification, and calcium ion storage",
     ["Protein synthesis", "DNA transcription", "ATP production"],
     "SER: no ribosomes. Functions: lipid/steroid synthesis, drug detoxification (liver cells rich in SER), calcium storage (muscle cells)."),
    ("plant_cell",
     "Plasmolysis in plant cells occurs when:",
     "Plant cell loses water in hypertonic solution; cell membrane pulls away from cell wall",
     ["Water enters the cell", "Cell is placed in hypotonic solution", "Osmosis stops"],
     "Plasmolysis: in hypertonic external solution, water leaves vacuole by osmosis -> cell membrane shrinks away from wall -> cell loses turgor."),
    ("mitosis",
     "Cytokinesis in animal cells occurs by:",
     "Cleavage furrow (actin-myosin ring contracts, pinching cell in two)",
     ["Cell plate formation", "Cell wall dissolution", "Nuclear envelope breakdown"],
     "Animal cells: cytokinesis via cleavage furrow (contractile ring of actin). Plant cells: cell plate forms from Golgi vesicles along equator."),
    ("organelles",
     "Which organelle contains its own DNA and is thought to have originated from an ancient prokaryote?",
     "Mitochondria (and chloroplasts) — endosymbiotic theory",
     ["Nucleus", "Golgi apparatus", "Lysosome"],
     "Endosymbiotic theory (Lynn Margulis): mitochondria and chloroplasts originated from free-living prokaryotes engulfed by ancestral eukaryotes."),
    ("animal_cell",
     "The cell cycle is regulated at checkpoints. The G1 checkpoint mainly checks:",
     "Whether the cell has grown enough and whether DNA is undamaged before committing to division",
     ["Whether DNA replication is complete", "Whether chromosomes are aligned", "Whether cytokinesis is done"],
     "G1 checkpoint (restriction point): checks cell size, nutrient availability, DNA integrity. If conditions are right, cell proceeds to S phase."),
    ("mitosis",
     "Meiosis differs from mitosis in that meiosis:",
     "Produces 4 haploid cells; involves 2 divisions; allows genetic recombination (crossing over)",
     ["Produces 2 diploid cells", "Occurs in all body cells", "Has no DNA replication"],
     "Meiosis: 2 divisions (meiosis I + II) -> 4 haploid (n) cells. Crossing over in prophase I creates genetic diversity. For gametes."),
]

def gen_cell(n=QPT):
    print(f"[Cell Biology] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(CELL_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_cell(scene); url=upload_pil(img, f"cell_{i}")
        ok=post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                  "Cell Biology", "Cell Structure and Division",
                  qtext, url, opts, cidx, expl)
        print(f"  cell_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 2. GENETICS & HEREDITY  (Class 12)
# ==============================================================================

def draw_genetics(scene="punnett"):
    img, draw = canvas(540, 420, "#FFF8E1")
    draw.text((20, 8), f"Genetics: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "punnett":
        draw.text((30, 45), "Punnett Square: Tt x Tt (Tall x Tall)", fill="#2C3E50", font=FONT_MD)
        # Grid
        cols = ["T", "t"]; rows_p = ["T", "t"]
        ox, oy = 130, 100
        sz = 90
        draw.text((ox+sz//2-5, oy-25), "T", fill="#E74C3C", font=FONT_LG)
        draw.text((ox+sz+sz//2-5, oy-25), "t", fill="#E74C3C", font=FONT_LG)
        draw.text((ox-25, oy+sz//2-8), "T", fill="#2980B9", font=FONT_LG)
        draw.text((ox-25, oy+sz+sz//2-8), "t", fill="#2980B9", font=FONT_LG)
        combos = [["TT","Tt"],["Tt","tt"]]
        colors = [["#27AE60","#27AE60"],["#27AE60","#E74C3C"]]
        for r in range(2):
            for c in range(2):
                x1, y1 = ox+c*sz, oy+r*sz
                draw.rectangle([x1, y1, x1+sz, y1+sz], outline="#2C3E50", width=2)
                draw.text((x1+28, y1+28), combos[r][c], fill=colors[r][c], font=FONT_LG)
        draw.text((30, 310), "Ratio: 1 TT : 2 Tt : 1 tt  ->  3 Tall : 1 Short", fill="#2C3E50", font=FONT_MD)
        draw.text((30, 345), "T = dominant (Tall), t = recessive (short)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 370), "Phenotype ratio: 3:1  |  Genotype ratio: 1:2:1", fill="#7F8C8D", font=FONT_SM)

    elif scene == "dna_structure":
        draw.text((30, 40), "DNA Double Helix Structure", fill="#1A5276", font=FONT_LG)
        # Draw simple double helix representation
        for i in range(8):
            y = 90 + i * 35
            x_offset = int(50 * math.sin(i * math.pi / 3))
            draw.ellipse([130+x_offset-8, y-8, 130+x_offset+8, y+8], fill="#3498DB")
            draw.ellipse([310-x_offset-8, y-8, 310-x_offset+8, y+8], fill="#E74C3C")
            if i % 2 == 0:
                draw.line([(130+x_offset, y), (310-x_offset, y)], fill="#F39C12", width=2)
        draw.text((340, 90),  "Base pairs:", fill="#2C3E50", font=FONT_MD)
        draw.text((340, 120), "A -- T", fill="#27AE60", font=FONT_MD)
        draw.text((340, 150), "(2 H-bonds)", fill="#7F8C8D", font=FONT_SM)
        draw.text((340, 185), "G -- C", fill="#E74C3C", font=FONT_MD)
        draw.text((340, 215), "(3 H-bonds)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 380), "DNA: deoxyribose + phosphate backbone, nitrogenous bases inside", fill="#7F8C8D", font=FONT_SM)

    elif scene == "central_dogma":
        draw.text((30, 40), "Central Dogma of Molecular Biology", fill="#1A5276", font=FONT_LG)
        # DNA -> RNA -> Protein
        for x, label, col in [(80, "DNA", "#2980B9"), (250, "mRNA", "#27AE60"), (420, "Protein", "#E74C3C")]:
            draw.ellipse([x-45, 170, x+45, 230], fill=col, outline="#2C3E50", width=2)
            draw.text((x-30, 193), label, fill="white", font=FONT_MD)
        # Arrows
        draw.line([(135, 200), (205, 200)], fill="#2C3E50", width=3)
        draw.polygon([(205,200),(193,194),(193,206)], fill="#2C3E50")
        draw.text((148, 175), "Transcription", fill="#2C3E50", font=FONT_SM)
        draw.line([(295, 200), (375, 200)], fill="#2C3E50", width=3)
        draw.polygon([(375,200),(363,194),(363,206)], fill="#2C3E50")
        draw.text((305, 175), "Translation", fill="#2C3E50", font=FONT_SM)
        # Replication
        draw.line([(80, 230), (80, 275)], fill="#2980B9", width=2)
        draw.line([(80, 275), (30, 275)], fill="#2980B9", width=2)
        draw.polygon([(30,275),(42,269),(42,281)], fill="#2980B9")
        draw.text((85, 250), "Replication", fill="#2980B9", font=FONT_SM)
        draw.text((30, 320), "Transcription: DNA -> mRNA (in nucleus)", fill="#27AE60", font=FONT_SM)
        draw.text((30, 350), "Translation: mRNA -> Protein (at ribosome)", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 380), "Codon: 3 bases on mRNA | Anticodon: on tRNA", fill="#7F8C8D", font=FONT_SM)

    elif scene == "mutation":
        draw.text((30, 40), "Types of Mutations", fill="#1A5276", font=FONT_LG)
        data = [
            ("Point mutation",   "Change in a single nucleotide base",              "#E74C3C"),
            ("Substitution",     "One base replaced by another (silent/missense/nonsense)","#E74C3C"),
            ("Insertion",        "Extra nucleotide(s) added — causes frameshift",   "#9B59B6"),
            ("Deletion",         "Nucleotide(s) removed — causes frameshift",       "#9B59B6"),
            ("Chromosomal mut.", "Deletion, duplication, inversion, translocation", "#2980B9"),
            ("Down syndrome",    "Trisomy 21 (extra chromosome 21)",               "#27AE60"),
            ("Sickle cell",      "Point mutation: GAG->GTG in beta-globin gene",    "#F39C12"),
        ]
        y = 95
        for mut, desc, col in data:
            draw.text((30, y), mut + ":", fill=col, font=FONT_SM)
            draw.text((210, y), desc, fill="#2C3E50", font=FONT_SM)
            y += 43

    return img

GENETICS_QA = [
    ("punnett",
     "In a monohybrid cross between two heterozygous tall plants (Tt x Tt), the phenotype ratio is:",
     "3 Tall : 1 Short  (T is dominant over t)",
     ["1:1", "1:2:1", "All tall"],
     "Tt x Tt Punnett square: TT(1), Tt(2), tt(1). Phenotype: 3 tall (TT + 2Tt) : 1 short (tt). Law of Segregation."),
    ("dna_structure",
     "In a DNA molecule, adenine (A) always pairs with:",
     "Thymine (T) — 2 hydrogen bonds",
     ["Cytosine (C)", "Guanine (G)", "Uracil (U)"],
     "Chargaff's rule: A pairs with T (2 H-bonds); G pairs with C (3 H-bonds). In RNA, T is replaced by Uracil (U)."),
    ("central_dogma",
     "The central dogma of molecular biology states:",
     "DNA -> RNA -> Protein (information flows from DNA through RNA to protein)",
     ["Protein -> RNA -> DNA", "RNA -> DNA -> Protein", "DNA directly becomes protein"],
     "Central dogma (Crick, 1958): DNA is transcribed to mRNA; mRNA is translated to protein. DNA also undergoes replication."),
    ("punnett",
     "In a dihybrid cross RrYy x RrYy (R=Round, Y=Yellow, both dominant), the phenotype ratio is:",
     "9 Round Yellow : 3 Round Green : 3 Wrinkled Yellow : 1 Wrinkled Green",
     ["3:1", "1:2:1:2:4:2:1:2:1", "1:1:1:1"],
     "Mendel's Law of Independent Assortment: 9:3:3:1 ratio in dihybrid cross of two heterozygotes."),
    ("mutation",
     "Sickle cell anaemia is caused by:",
     "A point mutation in the beta-globin gene: GAG -> GTG, causing Glu -> Val substitution",
     ["A chromosomal deletion", "Insertion of extra chromosome", "A frameshift mutation"],
     "Sickle cell: single nucleotide change (A->T in 6th codon of beta-globin). Glutamic acid -> Valine -> abnormal HbS that deforms RBCs."),
    ("dna_structure",
     "The backbone of a DNA strand consists of:",
     "Alternating deoxyribose sugar and phosphate groups",
     ["Nitrogenous bases only", "Ribose and phosphate", "Amino acids and phosphate"],
     "DNA backbone: deoxyribose (5-carbon sugar) connected by phosphodiester bonds via phosphate groups. Bases project inward."),
    ("central_dogma",
     "How many nucleotides make up a codon in mRNA?",
     "3 nucleotides (triplet code — codes for one amino acid)",
     ["1", "2", "4"],
     "Genetic code: 3 bases = 1 codon -> 1 amino acid. 4^3 = 64 possible codons for 20 amino acids -> degeneracy. AUG = start codon."),
    ("punnett",
     "A man with blood group AB marries a woman with blood group O. What blood groups can their children have?",
     "A or B only (50% A, 50% B) — IAi x ii",
     ["A, B, AB, or O", "Only AB", "Only O"],
     "AB = IAIB. O = ii. Cross: IAi (blood group A) and IBi (blood group B). No AB or O offspring possible."),
    ("mutation",
     "Down syndrome (Trisomy 21) results from:",
     "Non-disjunction during meiosis — extra copy of chromosome 21 (47 chromosomes total)",
     ["Deletion of chromosome 21", "Translocation of chromosome 13", "Point mutation in gene"],
     "Non-disjunction: homologous chromosomes fail to separate in meiosis I or II -> gamete with 2 copies of chr.21 -> trisomy 21."),
    ("dna_structure",
     "The enzyme that synthesises a new DNA strand during replication is:",
     "DNA polymerase (adds nucleotides 5' to 3'; requires a primer)",
     ["RNA polymerase", "Helicase", "Ligase"],
     "DNA polymerase III (prokaryotes) adds dNTPs to 3' end of growing strand. Helicase unwinds DNA; Ligase joins Okazaki fragments."),
    ("central_dogma",
     "During translation, transfer RNA (tRNA) carries:",
     "A specific amino acid to the ribosome (matched by anticodon to mRNA codon)",
     ["mRNA template", "DNA instructions", "Ribosomes to mRNA"],
     "tRNA: adapter molecule. Has anticodon (3 bases complementary to mRNA codon) + carries specific amino acid at 3' end."),
    ("punnett",
     "A woman is a carrier of colourblindness (X-linked recessive: XNXn). She marries a normal man (XNY). The probability of a colourblind son is:",
     "25% of all children (50% of sons will be colourblind)",
     ["0%", "100%", "75%"],
     "Cross: XNXn x XNY -> XN XN (normal girl), XN Xn (carrier girl), XN Y (normal boy), Xn Y (colourblind boy). 1/4 total = 25%."),
    ("mutation",
     "Frameshift mutations are caused by:",
     "Insertion or deletion of nucleotides (not a multiple of 3), shifting the reading frame",
     ["Substitution of one base", "Chromosomal inversion", "UV radiation only"],
     "Frameshift: insertion/deletion of 1 or 2 bases shifts reading frame -> all downstream codons changed -> usually non-functional protein."),
    ("dna_structure",
     "The double helix of DNA was discovered by:",
     "Watson and Crick (1953), using X-ray data from Franklin and Wilkins",
     ["Griffith and Avery", "Mendel and Morgan", "Hershey and Chase"],
     "Watson & Crick (1953): proposed DNA double helix model using Rosalind Franklin's X-ray crystallography data (Photo 51)."),
    ("central_dogma",
     "The promoter region in DNA is important because:",
     "It signals where RNA polymerase should begin transcription",
     ["It codes for the first amino acid", "It acts as a stop codon", "It is where ribosomes bind"],
     "Promoter: non-coding regulatory DNA sequence upstream of a gene. RNA polymerase binds to promoter to initiate transcription."),
    ("punnett",
     "In incomplete dominance, when a red flower (RR) is crossed with a white flower (WW), the F1 offspring are:",
     "All pink (RW) — incomplete dominance, no complete dominance",
     ["All red", "3 red : 1 white", "Half red half white"],
     "Incomplete dominance: neither allele is completely dominant. RR (red) x WW (white) -> RW (pink). F2: 1 red : 2 pink : 1 white."),
    ("mutation",
     "Which chromosome abnormality causes Turner syndrome?",
     "Monosomy X (45, XO) — one X chromosome, no second sex chromosome",
     ["Trisomy 21", "XXY (Klinefelter)", "XYY"],
     "Turner syndrome: 45, X0. Female with only one X chromosome. Short stature, infertile, streak gonads. Caused by non-disjunction."),
    ("dna_structure",
     "The antiparallel nature of DNA means:",
     "The two strands run in opposite directions: one 5' to 3', the other 3' to 5'",
     ["The bases are on the outside", "Both strands run 5' to 3'", "DNA is circular in eukaryotes"],
     "Antiparallel: one strand goes 5'->3', complementary strand goes 3'->5'. DNA polymerase synthesises only in 5'->3' direction."),
    ("central_dogma",
     "The start codon in mRNA that signals the beginning of translation is:",
     "AUG (codes for methionine)",
     ["UAA", "UGA", "GUG"],
     "AUG is the universal start codon: codes for methionine. UAA, UAG, UGA are stop codons (terminate translation). GUG can rarely initiate."),
    ("mutation",
     "Which of the following is NOT a Mendelian trait?",
     "Height in humans (polygenic — multiple genes contribute)",
     ["Tongue rolling ability", "Attached/free earlobes", "ABO blood groups"],
     "Polygenic traits: controlled by multiple genes with additive effects -> continuous variation. E.g., height, skin colour, weight."),
]

def gen_genetics(n=QPT):
    print(f"[Genetics & Heredity] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(GENETICS_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_genetics(scene); url=upload_pil(img, f"gen_{i}")
        ok=post_q("Science", 12, random.choice(["Advanced","Olympiad"]),
                  "Genetics", "Heredity, DNA Structure and Mutations",
                  qtext, url, opts, cidx, expl)
        print(f"  gen_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 3. HUMAN PHYSIOLOGY  (Class 11)
# ==============================================================================

def draw_physio(scene="heart"):
    img, draw = canvas(540, 420, "#FFF0F0")
    draw.text((20, 8), f"Human Physiology: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "heart":
        cx, cy = 270, 230
        # Heart shape (simplified)
        draw.ellipse([cx-120, cy-100, cx+20, cy+60], fill="#E74C3C", outline="#922B21", width=2)
        draw.ellipse([cx-20, cy-100, cx+120, cy+60], fill="#C0392B", outline="#922B21", width=2)
        draw.polygon([(cx-120,cy),(cx,cy+130),(cx+120,cy)], fill="#E74C3C")
        # Chambers labels
        draw.text((cx-95, cy-60), "RA", fill="white", font=FONT_MD)
        draw.text((cx+55, cy-60), "LA", fill="white", font=FONT_MD)
        draw.text((cx-75, cy+20), "RV", fill="white", font=FONT_LG)
        draw.text((cx+30, cy+20), "LV", fill="white", font=FONT_LG)
        draw.text((30, 370), "RA/RV: deoxygenated blood -> lungs  |  LA/LV: oxygenated -> body", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 395), "Heart rate: ~72 bpm  |  Cardiac output = HR x stroke volume", fill="#7F8C8D", font=FONT_SM)

    elif scene == "digestion":
        draw.text((30, 40), "Human Digestive System", fill="#1A5276", font=FONT_LG)
        organs = [
            ("Mouth",        "Mechanical digestion; salivary amylase breaks starch"),
            ("Oesophagus",   "Peristalsis moves food to stomach"),
            ("Stomach",      "HCl (pH 2), pepsin breaks proteins; churning"),
            ("Small intestine","Main digestion + absorption (villi, microvilli)"),
            ("Liver",        "Produces bile (emulsifies fats)"),
            ("Pancreas",     "Produces lipase, amylase, trypsin (into SI)"),
            ("Large intestine","Water absorption; faeces formation"),
        ]
        y = 85
        for organ, func in organs:
            draw.text((30, y), organ + ":", fill="#E74C3C", font=FONT_SM)
            draw.text((200, y), func, fill="#2C3E50", font=FONT_SM)
            y += 42

    elif scene == "respiration":
        draw.text((30, 40), "Respiratory System & Gas Exchange", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Pathway: Nose -> Pharynx -> Larynx -> Trachea -> Bronchi -> Alveoli", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 115), "Alveoli: site of gas exchange (thin walls, rich blood supply)", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 150), "O2: alveoli -> blood (high pO2 in lungs, low in blood)", fill="#27AE60", font=FONT_SM)
        draw.text((30, 175), "CO2: blood -> alveoli (high pCO2 in blood, low in lungs)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 215), "Tidal volume: ~500 mL (normal breath)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 240), "Vital capacity: ~4800 mL (max breathing capacity)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 280), "Haemoglobin carries O2 (4 O2 per Hb molecule)", fill="#E74C3C", font=FONT_MD)
        draw.text((30, 315), "HbO2 (oxyhaemoglobin, bright red) <=> Hb + 4O2 (deoxyHb, dark)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 355), "CO2 transport: 70% as HCO3- ions in plasma (bicarbonate)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 385), "Diaphragm contracts -> chest expands -> air flows in", fill="#7F8C8D", font=FONT_SM)

    elif scene == "neuron":
        draw.text((30, 40), "Nervous System — Neuron Structure", fill="#1A5276", font=FONT_LG)
        # Neuron drawing
        # Dendrites
        cx, cy = 100, 220
        for ang in [-40, -20, 0, 20, 40]:
            rad = math.radians(ang)
            draw.line([(cx, cy), (cx - 60*math.cos(rad), cy - 60*math.sin(rad))],
                      fill="#3498DB", width=2)
        # Cell body
        draw.ellipse([cx-30, cy-30, cx+30, cy+30], fill="#F7DC6F", outline="#2C3E50", width=2)
        draw.text((cx-18, cy-8), "Cell\nbody", fill="#2C3E50", font=FONT_SM)
        # Axon
        draw.line([(cx+30, cy), (420, cy)], fill="#E74C3C", width=4)
        # Myelin sheaths
        for mx in [150, 220, 290, 360]:
            draw.rectangle([mx, cy-12, mx+40, cy+12], fill="#ECF0F1", outline="#BDC3C7", width=1)
        # Axon terminals
        for ty in [cy-25, cy, cy+25]:
            draw.line([(420, cy), (450, ty)], fill="#E74C3C", width=2)
            draw.ellipse([448, ty-5, 458, ty+5], fill="#27AE60")
        draw.text((30, 310), "Dendrites -> Cell body (soma) -> Axon -> Synaptic terminals", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 340), "Myelin sheath (Schwann cells): insulates axon, speeds conduction", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 370), "Action potential: Na+ rushes in (depolarisation), K+ rushes out", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 395), "Synapse: neurotransmitters (ACh, dopamine) cross synaptic cleft", fill="#7F8C8D", font=FONT_SM)

    return img

PHYSIO_QA = [
    ("heart",
     "The left ventricle of the heart pumps blood to:",
     "The entire body through the aorta (systemic circulation)",
     ["The lungs only", "The right atrium", "The coronary arteries only"],
     "Left ventricle: thickest wall, pumps oxygenated blood via aorta to all body tissues. Right ventricle -> lungs (pulmonary)."),
    ("digestion",
     "Where does the majority of nutrient absorption occur in the digestive system?",
     "Small intestine (villi and microvilli greatly increase surface area)",
     ["Stomach", "Large intestine", "Mouth"],
     "Small intestine: ~6-7 m long. Villi and microvilli (brush border) increase surface area ~600x. Absorbs glucose, amino acids, fatty acids."),
    ("respiration",
     "The primary site of gas exchange in the lungs is the:",
     "Alveoli (tiny air sacs with extremely thin walls and rich capillary network)",
     ["Trachea", "Bronchi", "Bronchioles"],
     "Alveoli: ~700 million in human lungs, total surface area ~70 m2. Walls are one cell thick -> O2/CO2 diffuse rapidly."),
    ("neuron",
     "The myelin sheath around nerve axons serves to:",
     "Insulate the axon and greatly speed up nerve impulse conduction (saltatory conduction)",
     ["Supply nutrients to the neuron", "Transmit signals between neurons", "Store neurotransmitters"],
     "Myelin (Schwann cells): fatty insulating sheath. Allows saltatory conduction (jumps between nodes of Ranvier) -> faster transmission."),
    ("heart",
     "The cardiac cycle consists of:",
     "Systole (contraction) and diastole (relaxation) — complete cycle takes ~0.8 seconds at 75 bpm",
     ["Only systole", "Only diastole", "Depolarisation and repolarisation only"],
     "Systole: ventricles contract, pump blood. Diastole: heart relaxes, fills with blood. HR 75 bpm: period = 60/75 = 0.8 s."),
    ("digestion",
     "Bile is produced by the liver and stored in the gallbladder. Its main role is:",
     "Emulsification of fats (breaking large fat globules into smaller ones for lipase to act on)",
     ["Digesting proteins", "Producing digestive enzymes", "Absorbing water"],
     "Bile: no enzymes. Contains bile salts that emulsify fats -> increases surface area for lipase (from pancreas) to digest triglycerides."),
    ("respiration",
     "Haemoglobin carries oxygen by binding to:",
     "Iron (Fe2+) in the haem group — each haemoglobin carries 4 O2 molecules",
     ["Protein (globin) part directly", "Carbon atoms in the backbone", "The porphyrin ring exclusively"],
     "Haemoglobin: 4 subunits, each with 1 haem group containing Fe2+. O2 binds to Fe2+. One Hb molecule carries up to 4 O2."),
    ("neuron",
     "A nerve impulse (action potential) is generated when:",
     "The membrane depolarises — Na+ ions rush into the neuron through voltage-gated channels",
     ["K+ ions rush into the cell", "Cl- ions leave the cell", "Ca2+ binds to receptors"],
     "Action potential: resting potential ~-70mV. Stimulus opens Na+ channels -> Na+ rushes in -> depolarisation to +30mV. Then K+ exits -> repolarisation."),
    ("heart",
     "Blood flows through the heart in the order:",
     "Vena cava -> Right atrium -> Right ventricle -> Pulmonary artery -> Lungs -> Pulmonary vein -> Left atrium -> Left ventricle -> Aorta",
     ["Aorta -> Left atrium -> Left ventricle -> Lungs", "Right ventricle -> Left ventricle -> Aorta", "Left -> Right side first"],
     "Double circulation: pulmonary (heart->lungs->heart) and systemic (heart->body->heart). Right side = deoxygenated blood."),
    ("digestion",
     "The enzyme pepsin, found in the stomach, digests:",
     "Proteins (breaks peptide bonds in an acidic environment, pH ~2)",
     ["Starch", "Fats", "Nucleic acids"],
     "Pepsin: protease secreted as pepsinogen (inactive), activated by HCl. Optimal pH ~2. Breaks proteins into polypeptides."),
    ("respiration",
     "The primary driver of inhalation is:",
     "Contraction of the diaphragm (flattens down), increasing thoracic volume, decreasing pressure",
     ["Lung expansion", "Chest wall contraction", "Relaxation of diaphragm"],
     "Breathing in: diaphragm contracts (moves down) + external intercostals contract -> chest volume increases -> pressure drops -> air flows in."),
    ("neuron",
     "Neurotransmitters are released from:",
     "Synaptic vesicles in the presynaptic terminal into the synaptic cleft",
     ["Dendrites", "Myelin sheath", "Cell body nucleus"],
     "Neurotransmitters (ACh, dopamine, serotonin): stored in vesicles at axon terminal. Released by exocytosis when action potential arrives."),
    ("heart",
     "The normal resting blood pressure is approximately:",
     "120/80 mmHg (systolic/diastolic)",
     ["80/120 mmHg", "60/40 mmHg", "200/100 mmHg"],
     "Systolic BP (120): pressure during heart contraction. Diastolic BP (80): pressure during relaxation. Hypertension: >140/90 mmHg."),
    ("digestion",
     "Salivary amylase begins the digestion of:",
     "Starch (polysaccharides) -> maltose in the mouth",
     ["Proteins", "Fats", "Cellulose"],
     "Salivary amylase: breaks starch (alpha-1,4 glycosidic bonds) -> maltose and dextrins in mouth. Denatured in stomach's acidic pH."),
    ("respiration",
     "Carbon dioxide is mainly transported in the blood as:",
     "Bicarbonate ions (HCO3-) in plasma (~70%)",
     ["Dissolved CO2 in plasma", "Bound to haemoglobin as carbaminohaemoglobin", "Carbonic acid"],
     "CO2 + H2O -> H2CO3 (carbonic anhydrase) -> H+ + HCO3-. 70% as HCO3- in plasma. 23% bound to Hb. 7% dissolved."),
    ("neuron",
     "The blood-brain barrier (BBB) is formed by:",
     "Tight junctions between endothelial cells of brain capillaries and astrocyte foot processes",
     ["Myelin sheath", "Skull and meninges only", "CSF (cerebrospinal fluid)"],
     "BBB: specialised capillaries in brain. Tight junctions prevent most molecules from entering brain. Protects brain from toxins."),
    ("heart",
     "The pacemaker of the heart (sets the rhythm) is the:",
     "Sinoatrial (SA) node in the right atrium (~72 impulses per minute)",
     ["Atrioventricular (AV) node", "Bundle of His", "Purkinje fibres"],
     "SA node: natural pacemaker. Generates electrical impulse -> atria contract -> AV node -> Bundle of His -> Purkinje fibres -> ventricles."),
    ("digestion",
     "Villi and microvilli in the small intestine are important because they:",
     "Greatly increase the surface area for absorption (~600-fold)",
     ["Produce digestive enzymes", "Store bile", "Absorb water only"],
     "Villi (finger-like projections) and microvilli (brush border) on intestinal cells increase surface area to ~200-250 m2 for efficient absorption."),
    ("respiration",
     "Vital capacity of the lungs is:",
     "Maximum volume of air that can be exhaled after a maximum inhalation (~4.8 L)",
     ["Volume of air in one normal breath", "Air remaining after maximum exhalation", "Total lung capacity"],
     "Vital capacity = Tidal Volume + Inspiratory Reserve Volume + Expiratory Reserve Volume (~4800 mL). Residual volume stays in lungs."),
    ("neuron",
     "The peripheral nervous system (PNS) consists of:",
     "All nerves outside the brain and spinal cord — somatic and autonomic divisions",
     ["Brain and spinal cord", "Only the spinal cord", "Only autonomic nerves"],
     "PNS = all neural tissue outside CNS. Somatic: voluntary muscle control. Autonomic: involuntary (sympathetic: fight/flight; parasympathetic: rest/digest)."),
]

def gen_physio(n=QPT):
    print(f"[Human Physiology] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(PHYSIO_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_physio(scene); url=upload_pil(img, f"physio_{i}")
        ok=post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                  "Human Physiology", "Organ Systems",
                  qtext, url, opts, cidx, expl)
        print(f"  physio_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 4. PLANT BIOLOGY  (Class 11)
# ==============================================================================

def draw_plant(scene="photosynthesis"):
    img, draw = canvas(540, 420, "#F0FFF0")
    draw.text((20, 8), f"Plant Biology: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "photosynthesis":
        draw.text((30, 40), "Photosynthesis: 6CO2 + 6H2O + Light -> C6H12O6 + 6O2", fill="#1E8449", font=FONT_MD)
        draw.text((30, 75), "Two Stages:", fill="#2C3E50", font=FONT_LG)
        draw.text((30, 110), "1. Light Reactions (Thylakoid membrane):", fill="#E74C3C", font=FONT_MD)
        draw.text((40, 138), "- Water is split (photolysis): 2H2O -> 4H+ + 4e- + O2", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 160), "- ATP and NADPH produced", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 182), "- Photosystems I and II (PS I: 700nm, PS II: 680nm)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 215), "2. Dark Reactions / Calvin Cycle (Stroma):", fill="#3498DB", font=FONT_MD)
        draw.text((40, 243), "- CO2 fixation by RuBiSCO enzyme", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 265), "- Uses ATP and NADPH from light reactions", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 287), "- Produces G3P -> Glucose (C3 plants)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 325), "Chlorophyll a: main pigment (absorbs red 680nm + blue 430nm)", fill="#27AE60", font=FONT_SM)
        draw.text((30, 350), "Chlorophyll b, carotenoids: accessory pigments", fill="#27AE60", font=FONT_SM)
        draw.text((30, 385), "C4 plants (sugarcane): CO2 fixed first as 4-C compound (no photorespiration)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "transpiration":
        draw.text((30, 40), "Transpiration and Water Transport", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Transpiration: loss of water vapour through stomata", fill="#2C3E50", font=FONT_MD)
        draw.text((30, 115), "Transpiration pull: main force for water ascent in xylem", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 140), "Cohesion-tension theory: water columns held by H-bonds", fill="#E74C3C", font=FONT_SM)
        draw.text((30, 180), "Xylem: transports water and minerals upward (dead cells)", fill="#3498DB", font=FONT_MD)
        draw.text((30, 215), "Phloem: transports sugars (both directions, living cells)", fill="#27AE60", font=FONT_MD)
        draw.text((30, 255), "Guard cells: control stomata opening/closing", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 280), "  - Light/Low CO2: stomata open (K+ enters guard cells)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 305), "  - Dark/High CO2/drought: stomata close (K+ leaves)", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 345), "Root pressure: lower force, significant at night", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 380), "Mineral uptake: active transport by root hair cells", fill="#7F8C8D", font=FONT_SM)

    elif scene == "hormones":
        draw.text((30, 40), "Plant Hormones (Phytohormones)", fill="#1A5276", font=FONT_LG)
        data = [
            ("Auxin (IAA)",    "Cell elongation, apical dominance, phototropism", "#E74C3C"),
            ("Gibberellin",    "Stem elongation, seed germination, fruit development", "#3498DB"),
            ("Cytokinin",      "Cell division, delay of senescence, leaf growth", "#27AE60"),
            ("Abscisic acid",  "Stress hormone: closes stomata, dormancy, seed maturation", "#E67E22"),
            ("Ethylene (gas)", "Fruit ripening, leaf/flower abscission, stress response", "#9B59B6"),
        ]
        y = 95
        for name, func, col in data:
            draw.text((30, y), name + ":", fill=col, font=FONT_MD)
            draw.text((30, y+22), func, fill="#2C3E50", font=FONT_SM)
            y += 62
        draw.text((30, 395), "Auxin discovered by Darwin (coleoptile bending experiments)", fill="#7F8C8D", font=FONT_SM)

    elif scene == "nutrition":
        draw.text((30, 40), "Mineral Nutrition and Nitrogen Cycle", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Macronutrients (large amounts): N, P, K, Ca, Mg, S", fill="#2C3E50", font=FONT_MD)
        draw.text((30, 110), "Micronutrients (trace): Fe, Mn, Zn, Cu, Mo, B, Cl", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 150), "Nitrogen fixation:", fill="#E74C3C", font=FONT_MD)
        draw.text((40, 178), "N2 (atmosphere) -> NH3 by nitrogenase enzyme", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 202), "Rhizobium bacteria in legume root nodules (symbiosis)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 240), "Nitrification: NH3 -> NO2- (Nitrosomonas) -> NO3- (Nitrobacter)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 265), "Denitrification: NO3- -> N2 (back to atmosphere)", fill="#3498DB", font=FONT_SM)
        draw.text((30, 305), "Special adaptations:", fill="#27AE60", font=FONT_MD)
        draw.text((40, 333), "Insectivorous plants: Sundew, Venus flytrap (N-poor soils)", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 357), "Parasitic plants: Cuscuta (dodder), Orobanche", fill="#2C3E50", font=FONT_SM)
    return img

PLANT_QA = [
    ("photosynthesis",
     "In photosynthesis, oxygen is released as a by-product of:",
     "Photolysis of water in the light reactions (2H2O -> 4H+ + 4e- + O2)",
     ["CO2 fixation in Calvin cycle", "Glucose breakdown", "ATP synthesis"],
     "Photolysis (light-dependent reaction at Photosystem II): water molecules split using light energy, releasing O2 as by-product."),
    ("transpiration",
     "Which tissue in plants is responsible for transporting water and minerals from roots to leaves?",
     "Xylem (dead tracheids and vessel elements)",
     ["Phloem", "Cortex", "Pith"],
     "Xylem: dead cells (tracheids, vessels) forming continuous tubes. Water moves upward via transpiration pull, cohesion-tension."),
    ("hormones",
     "The hormone responsible for fruit ripening and is a gas is:",
     "Ethylene (C2H4) — a gaseous plant hormone",
     ["Auxin", "Gibberellin", "Cytokinin"],
     "Ethylene: gaseous hormone. Promotes fruit ripening, leaf abscission, flowering in some plants. Used commercially to ripen bananas."),
    ("photosynthesis",
     "The enzyme responsible for CO2 fixation in the Calvin cycle is:",
     "RuBiSCO (Ribulose-1,5-bisphosphate carboxylase/oxygenase) — most abundant enzyme on Earth",
     ["ATP synthase", "Chlorophyllase", "Nitrogenase"],
     "RuBiSCO fixes CO2 onto RuBP (5C) -> 2 molecules of 3-phosphoglycerate (3C). It's the most abundant enzyme on Earth."),
    ("transpiration",
     "Guard cells regulate transpiration by controlling:",
     "The opening and closing of stomata",
     ["Root pressure", "Xylem diameter", "Chlorophyll production"],
     "Guard cells: kidney-shaped cells flanking stomata. Swell (turgid) in light -> stomata open. Lose water -> stomata close."),
    ("hormones",
     "Apical dominance in plants (lateral buds inhibited by main shoot) is caused by:",
     "Auxin produced at the apical bud inhibits lateral bud growth",
     ["Cytokinin", "Gibberellin", "Abscisic acid"],
     "High auxin from apical bud suppresses lateral bud growth (apical dominance). Removing apical bud -> cytokinin promotes lateral growth."),
    ("photosynthesis",
     "C4 plants (like maize and sugarcane) have an advantage over C3 plants because:",
     "They fix CO2 first as a 4-carbon compound in mesophyll cells, avoiding photorespiration at high temperatures",
     ["They have more chlorophyll", "They do not need sunlight", "They fix N2 from air"],
     "C4 plants: PEP carboxylase (no O2 affinity) fixes CO2 into 4C acid -> bundle sheath cells for Calvin cycle. No photorespiration at high T."),
    ("nutrition",
     "Rhizobium bacteria found in root nodules of legumes are important because:",
     "They fix atmospheric N2 into NH3 (ammonia), making nitrogen available to plants",
     ["They increase root surface area", "They absorb phosphorus", "They produce gibberellins"],
     "Rhizobium: symbiotic nitrogen-fixing bacteria in legume root nodules. nitrogenase enzyme converts N2 -> NH3. Legumes (peas, beans, soybean) benefit."),
    ("transpiration",
     "The translocation of sugars in plants occurs through:",
     "Phloem (sieve tubes and companion cells — source to sink, bidirectional)",
     ["Xylem", "Epidermis", "Cortex"],
     "Phloem: transports dissolved sugars (sucrose) from source (leaves) to sink (roots, fruits). Pressure flow hypothesis drives translocation."),
    ("hormones",
     "Gibberellins are responsible for:",
     "Stem elongation, seed germination, breaking dormancy, and fruit development",
     ["Root growth", "Stomata closure", "Leaf abscission"],
     "Gibberellins (GA): promote internode elongation (dwarf plants grow tall with GA). Break seed/bud dormancy, promote germination, parthenocarpy."),
    ("photosynthesis",
     "Chlorophyll a absorbs light mainly in which wavelengths?",
     "Red (~680 nm) and blue-violet (~430 nm) — reflects green (hence plants appear green)",
     ["Only green light", "UV and infrared only", "All wavelengths equally"],
     "Chlorophyll a: peak absorption at ~430 nm (blue-violet) and ~680 nm (red). Green light reflected -> plants look green to us."),
    ("nutrition",
     "A plant showing yellowing of older leaves (chlorosis) first is likely deficient in:",
     "Nitrogen or Magnesium (mobile nutrients — remobilised from older to younger leaves)",
     ["Calcium", "Iron", "Boron"],
     "Mobile nutrients: N, P, K, Mg deficiency shows in older leaves first (plant remobilises from old to young). Ca, Fe (immobile): symptoms in young leaves."),
    ("transpiration",
     "In plants, the Casparian strip in the endodermis ensures that:",
     "Water and solutes must pass through the cytoplasm (symplastic pathway) to enter the xylem, allowing selective uptake",
     ["Water can bypass cell membranes freely", "Transpiration cannot occur", "Guard cells are regulated"],
     "Casparian strip: waxy band (suberin) in endodermal cell walls blocks apoplastic pathway. Forces all water through cytoplasm (symplastic) = selective filter."),
    ("hormones",
     "Abscisic acid (ABA) is called the 'stress hormone' because it:",
     "Causes stomatal closure during drought, promotes dormancy, and inhibits growth",
     ["Promotes rapid growth", "Stimulates fruit ripening", "Activates nitrogen fixation"],
     "ABA: increases in drought/stress conditions -> closes stomata (water conservation), induces seed dormancy, promotes senescence/leaf fall."),
    ("photosynthesis",
     "Photorespiration occurs in C3 plants when:",
     "RuBiSCO reacts with O2 instead of CO2 at high temperatures, reducing photosynthetic efficiency",
     ["Light intensity is too high", "Temperature is too low", "CO2 concentration is very high"],
     "Photorespiration: high O2/low CO2 ratio -> RuBiSCO's oxygenase activity -> wasteful pathway that releases CO2. C4/CAM plants avoid this."),
    ("nutrition",
     "The process of nitrification involves:",
     "Conversion of ammonia to nitrite (Nitrosomonas) then nitrate (Nitrobacter)",
     ["Fixing atmospheric N2 to NH3", "Converting NO3- back to N2", "Decomposition of organic matter"],
     "Nitrification: NH3 -> NO2- (Nitrosomonas bacteria) -> NO3- (Nitrobacter bacteria). Aerobic process. Nitrates are the form plants absorb."),
    ("transpiration",
     "Root pressure, which causes guttation, is mainly due to:",
     "Active ion uptake into xylem creating osmotic pressure that pushes water up",
     ["Transpiration pull", "Gravity", "Phloem pressure"],
     "Root pressure: roots actively pump ions into xylem -> water enters by osmosis -> positive pressure. Causes guttation (water droplets from leaf tips at night)."),
    ("hormones",
     "Cytokinins are mainly produced in:",
     "Root tips and developing seeds/fruits (promote cell division)",
     ["Leaf tips", "Stem nodes", "Flower petals"],
     "Cytokinins: produced in dividing tissues (root meristems, developing embryos). Promote cell division (cytokinesis), delay leaf senescence, promote bud growth."),
    ("photosynthesis",
     "The light reactions of photosynthesis occur in the:",
     "Thylakoid membranes (grana) of the chloroplast",
     ["Stroma", "Cytoplasm", "Mitochondria"],
     "Thylakoid membranes: location of photosystems, ETC, ATP synthase, and photolysis. Stroma: Calvin cycle (dark reactions) occurs here."),
    ("nutrition",
     "Venus flytrap is an insectivorous (carnivorous) plant because it:",
     "Grows in nitrogen-poor soil and supplements its diet by digesting insects for nitrogen",
     ["It cannot photosynthesise", "It gets energy from insects", "It lives in dark conditions"],
     "Carnivorous plants (Venus flytrap, sundew): photosynthesise normally but live in N-poor habitats. Trap and digest insects for supplementary nitrogen."),
]

def gen_plant(n=QPT):
    print(f"[Plant Biology] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(PLANT_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_plant(scene); url=upload_pil(img, f"plant_{i}")
        ok=post_q("Science", 11, random.choice(["Advanced","Olympiad"]),
                  "Plant Biology", "Photosynthesis, Transport and Hormones",
                  qtext, url, opts, cidx, expl)
        print(f"  plant_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 5. ECOLOGY & ENVIRONMENT  (Class 12)
# ==============================================================================

def draw_ecology(scene="food_chain"):
    img, draw = canvas(540, 420, "#E8F5E9")
    draw.text((20, 8), f"Ecology: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "food_chain":
        draw.text((30, 40), "Food Chain and Energy Flow", fill="#1A5276", font=FONT_LG)
        chain = [("Sun", "#FFD700"), ("Grass (Producer)", "#27AE60"),
                 ("Grasshopper (1st Consumer)", "#F39C12"),
                 ("Frog (2nd Consumer)", "#3498DB"),
                 ("Snake (3rd Consumer)", "#E74C3C"),
                 ("Eagle (Apex predator)", "#9B59B6")]
        y = 85
        for i, (org, col) in enumerate(chain):
            draw.rectangle([60, y, 400, y+32], fill=col, outline="#2C3E50", width=1)
            draw.text((70, y+8), org, fill="white", font=FONT_SM)
            if i < len(chain)-1:
                draw.text((405, y+8), "-> 10% energy", fill="#E74C3C", font=FONT_SM)
            y += 42
        draw.text((30, 380), "10% Law (Lindemann): only 10% energy passes to next trophic level", fill="#7F8C8D", font=FONT_SM)
        draw.text((30, 400), "90% lost as heat/respiration. Short chains are more efficient.", fill="#7F8C8D", font=FONT_SM)

    elif scene == "ecosystem":
        draw.text((30, 40), "Ecosystem Components", fill="#1A5276", font=FONT_LG)
        data = [
            ("Producers", "Plants, algae, cyanobacteria (autotrophs, fix solar energy)", "#27AE60"),
            ("Primary consumers", "Herbivores (eat producers): rabbit, cow, caterpillar", "#F39C12"),
            ("Secondary consumers", "Carnivores (eat herbivores): frog, spider, small fish", "#3498DB"),
            ("Tertiary consumers", "Top carnivores: eagle, shark, lion", "#E74C3C"),
            ("Decomposers", "Bacteria, fungi: break down dead matter, recycle nutrients", "#9B59B6"),
            ("Detritivores",  "Earthworms, woodlice: feed on detritus (dead organic matter)", "#795548"),
        ]
        y = 90
        for name, desc, col in data:
            draw.text((30, y), name + ":", fill=col, font=FONT_SM)
            draw.text((210, y), desc, fill="#2C3E50", font=FONT_SM)
            y += 48

    elif scene == "biogeochemical":
        draw.text((30, 40), "Biogeochemical Cycles", fill="#1A5276", font=FONT_LG)
        draw.text((30, 80), "Carbon Cycle:", fill="#E74C3C", font=FONT_MD)
        draw.text((40, 105), "CO2 fixed by plants (photosynthesis) -> organic molecules", fill="#2C3E50", font=FONT_SM)
        draw.text((40, 127), "Released by respiration, combustion, decomposition", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 160), "Nitrogen Cycle:", fill="#3498DB", font=FONT_MD)
        draw.text((40, 185), "N2 -> NH3 (fixation) -> NO3- (nitrification) -> back to N2 (denitrification)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 220), "Water Cycle:", fill="#27AE60", font=FONT_MD)
        draw.text((40, 245), "Evaporation -> Condensation -> Precipitation -> Runoff", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 285), "Phosphorus Cycle:", fill="#F39C12", font=FONT_MD)
        draw.text((40, 310), "No atmospheric phase; weathering -> soil -> plants -> consumers", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 355), "Eutrophication: excess N & P -> algal bloom -> O2 depletion", fill="#E74C3C", font=FONT_SM)

    return img

ECOLOGY_QA = [
    ("food_chain",
     "According to the 10% law of energy transfer, if producers have 10,000 kcal, how much energy is available to secondary consumers?",
     "100 kcal  (10,000 -> 1,000 -> 100 at each trophic level)",
     ["1,000 kcal", "10 kcal", "1 kcal"],
     "10% law (Lindemann): each trophic level receives 10% of energy from below. 10,000 -> 1,000 (primary) -> 100 (secondary consumers)."),
    ("ecosystem",
     "Organisms that break down dead organic matter into inorganic nutrients are called:",
     "Decomposers (bacteria and fungi)",
     ["Producers", "Consumers", "Parasites"],
     "Decomposers (saprotrophs): bacteria and fungi secrete enzymes to digest dead matter externally -> inorganic nutrients returned to ecosystem."),
    ("biogeochemical",
     "Eutrophication of water bodies is caused by:",
     "Excess nutrients (N and P from fertilisers) causing algal blooms that deplete oxygen",
     ["Heavy metal pollution", "Oil spills", "Temperature increase only"],
     "Eutrophication: nutrient enrichment -> rapid algal growth (bloom) -> algae die -> decomposed by bacteria -> O2 depleted -> fish die."),
    ("food_chain",
     "In a food web, an organism that feeds on both plants and animals is called:",
     "Omnivore (occupies multiple trophic levels)",
     ["Carnivore", "Herbivore", "Detritivore"],
     "Omnivores: eat both plants and animals. Occupy multiple trophic levels. Examples: humans, bears, rats, cockroaches."),
    ("ecosystem",
     "The total amount of organic matter produced by producers per unit area per unit time is called:",
     "Gross Primary Productivity (GPP)",
     ["Net Primary Productivity", "Secondary productivity", "Biomass"],
     "GPP: total photosynthesis rate. NPP = GPP - Respiration. NPP is organic matter available for consumers. NPP is what ecologists usually measure."),
    ("biogeochemical",
     "Nitrogen-fixing bacteria convert atmospheric nitrogen into a form plants can use. This process requires which enzyme?",
     "Nitrogenase (inhibited by oxygen; works in anaerobic conditions)",
     ["RuBiSCO", "Nitroglycerin", "Amylase"],
     "Nitrogenase: enzyme that reduces N2 -> NH3. Very sensitive to O2 (denatured by oxygen). Leghaemoglobin in root nodules maintains low O2."),
    ("food_chain",
     "A keystone species in an ecosystem is one that:",
     "Has a disproportionately large effect on its ecosystem relative to its abundance",
     ["Is the most numerous species", "Is at the top of the food chain only", "Has the most biomass"],
     "Keystone species: removal causes major ecosystem change. E.g., sea otters (eat urchins that eat kelp); elephants (maintain savannah)."),
    ("ecosystem",
     "The greenhouse effect is caused primarily by:",
     "CO2, methane, water vapour and other gases trapping heat in the atmosphere",
     ["Ozone depletion", "Acid rain", "Nuclear radiation"],
     "Greenhouse gases (CO2, CH4, N2O, H2O): absorb infrared radiation from Earth's surface, re-emit it back, warming the atmosphere."),
    ("biogeochemical",
     "Which of the following is an example of a biotic component of an ecosystem?",
     "A grass plant (living organism)",
     ["Soil minerals", "Sunlight", "Rainfall"],
     "Biotic: all living organisms (plants, animals, fungi, bacteria). Abiotic: non-living (temperature, light, water, soil, minerals, pH)."),
    ("food_chain",
     "The pyramid of energy in an ecosystem is always:",
     "Upright (energy always decreases at each successive trophic level — 10% rule)",
     ["Inverted sometimes", "Horizontal", "Diamond-shaped"],
     "Pyramid of energy: always upright (energy lost at each level as heat). Pyramid of numbers and biomass can be inverted (e.g., in some aquatic ecosystems)."),
    ("ecosystem",
     "Primary succession occurs on:",
     "Bare, lifeless substrate (e.g., bare rock, sand dune, new volcanic land)",
     ["Cleared forest area", "Agricultural land", "After flood recedes"],
     "Primary succession: on bare substrate with no soil. Pioneer species (lichens, mosses) -> gradual soil formation -> climax community."),
    ("biogeochemical",
     "CFCs (chlorofluorocarbons) damage the ozone layer by:",
     "Releasing Cl atoms that catalytically destroy O3 molecules in the stratosphere",
     ["Adding CO2 to atmosphere", "Absorbing UV radiation directly", "Reacting with water vapour"],
     "CFC -> UV light releases Cl* -> Cl* + O3 -> ClO + O2 -> ClO + O -> Cl* + O2. One Cl atom destroys 100,000 O3 molecules."),
    ("food_chain",
     "Biodiversity hotspots are regions with:",
     "High species richness and high levels of endemism that face significant habitat loss",
     ["Low biodiversity but high productivity", "Only marine ecosystems", "Cold climates with unique species"],
     "Biodiversity hotspot (Myers): must have >1,500 endemic vascular plant species AND lost >70% of primary habitat. 36 hotspots identified globally."),
    ("ecosystem",
     "The relationship where one organism benefits and the other is neither harmed nor helped is called:",
     "Commensalism (e.g., barnacles on whales; cattle egrets following livestock)",
     ["Mutualism", "Parasitism", "Predation"],
     "Commensalism (+/0): one benefits, other unaffected. Mutualism (+/+). Parasitism (+/-). Predation (+/-). Amensalism (-/0)."),
    ("biogeochemical",
     "Which gas is primarily responsible for acid rain?",
     "Sulphur dioxide (SO2) and nitrogen oxides (NOx) from burning fossil fuels",
     ["CO2", "Methane", "CFC"],
     "Acid rain: SO2 + H2O -> H2SO3; NOx + H2O -> HNO3. pH < 5.6. Damages forests, lakes, buildings. Reduces by scrubbers on power plants."),
    ("food_chain",
     "The concept of ecological niche refers to:",
     "The role and position a species has in its environment (what it eats, where it lives, its interactions)",
     ["The physical location of an organism", "The size of an organism's habitat", "The number of offspring produced"],
     "Niche: an organism's functional role in ecosystem. No two species can occupy the same niche indefinitely (competitive exclusion principle)."),
]

def gen_ecology(n=15):
    print(f"[Ecology & Environment] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(ECOLOGY_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_ecology(scene); url=upload_pil(img, f"eco_{i}")
        ok=post_q("Science", 12, random.choice(["Advanced","Olympiad"]),
                  "Ecology", "Ecosystems and Environment",
                  qtext, url, opts, cidx, expl)
        print(f"  eco_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# 6. EVOLUTION  (Class 12)
# ==============================================================================

def draw_evolution(scene="natural_selection"):
    img, draw = canvas(540, 420, "#FFF3E0")
    draw.text((20, 8), f"Evolution: {scene.replace('_',' ').title()}", fill="#1A5276", font=FONT_MD)

    if scene == "natural_selection":
        draw.text((30, 40), "Darwin's Theory of Natural Selection", fill="#1A5276", font=FONT_LG)
        steps = [
            ("1. Variation",   "Individuals within a population vary in traits"),
            ("2. Heredity",    "Traits passed from parents to offspring"),
            ("3. Competition", "More offspring produced than can survive (struggle)"),
            ("4. Selection",   "Individuals with favourable traits survive & reproduce more"),
            ("5. Adaptation",  "Favourable traits become more common over generations"),
            ("6. Speciation",  "Accumulation of changes -> new species over time"),
        ]
        y = 90
        for step, desc in steps:
            draw.text((30, y), step + ":", fill="#E74C3C", font=FONT_MD)
            draw.text((160, y), desc, fill="#2C3E50", font=FONT_SM)
            y += 50
        draw.text((30, 400), "Darwin (1859): On the Origin of Species", fill="#7F8C8D", font=FONT_SM)

    elif scene == "evidence":
        draw.text((30, 40), "Evidence for Evolution", fill="#1A5276", font=FONT_LG)
        data = [
            ("Fossil record",    "Shows progression of forms over geological time"),
            ("Homologous organs","Same origin, different function (e.g., forelimbs: whale, bat, human)"),
            ("Analogous organs", "Different origin, same function (e.g., wings of bat vs butterfly)"),
            ("Vestigial organs", "Reduced, functionless remnants (e.g., human appendix, wisdom teeth)"),
            ("Embryology",       "Embryos of different species look similar early in development"),
            ("Biogeography",     "Species distribution matches geological/evolutionary history"),
            ("Molecular",        "DNA/protein similarities show evolutionary relationships"),
        ]
        y = 90
        for name, desc in data:
            draw.text((30, y), name + ":", fill="#E74C3C", font=FONT_SM)
            draw.text((220, y), desc, fill="#2C3E50", font=FONT_SM)
            y += 45

    elif scene == "hardy_weinberg":
        draw.text((30, 40), "Hardy-Weinberg Equilibrium", fill="#1A5276", font=FONT_LG)
        draw.text((30, 85), "p + q = 1  (allele frequencies)", fill="#E74C3C", font=FONT_LG)
        draw.text((30, 120), "p^2 + 2pq + q^2 = 1  (genotype frequencies)", fill="#E74C3C", font=FONT_LG)
        draw.text((30, 160), "p = freq of dominant allele (A)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 185), "q = freq of recessive allele (a)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 210), "p^2 = freq(AA), 2pq = freq(Aa), q^2 = freq(aa)", fill="#2C3E50", font=FONT_SM)
        draw.text((30, 250), "Conditions for equilibrium (no evolution):", fill="#3498DB", font=FONT_MD)
        conditions = ["Large population", "Random mating", "No mutation",
                      "No migration", "No natural selection"]
        y = 285
        for cond in conditions:
            draw.text((40, y), "* " + cond, fill="#2C3E50", font=FONT_SM)
            y += 23
        draw.text((30, 400), "Deviation from H-W equilibrium = evolution is occurring", fill="#E74C3C", font=FONT_SM)

    return img

EVOL_QA = [
    ("natural_selection",
     "Charles Darwin's theory of natural selection is based on the observation that:",
     "Individuals with favourable heritable variations survive and reproduce more successfully",
     ["All individuals in a population are identical", "Environment creates new traits", "Traits acquired during life are inherited"],
     "Darwin: variation exists in populations; favourable traits are heritable; individuals compete for resources; better-adapted individuals survive."),
    ("evidence",
     "Homologous organs provide evidence for evolution because they:",
     "Have the same basic structure/origin but different functions in different species (common ancestor)",
     ["Have the same function in all species", "Are found only in plants", "Appear identical in all species"],
     "Homologous organs (e.g., human arm, bat wing, whale flipper, cat foreleg): same bone structure, different functions -> divergent evolution from common ancestor."),
    ("hardy_weinberg",
     "In a population in Hardy-Weinberg equilibrium, if the frequency of the recessive allele (q) is 0.3, the frequency of carriers (heterozygotes Aa) is:",
     "2pq = 2 * 0.7 * 0.3 = 0.42  (42%)",
     ["q^2 = 0.09", "p^2 = 0.49", "2 * 0.3 = 0.6"],
     "p = 1 - q = 1 - 0.3 = 0.7. Heterozygote frequency = 2pq = 2*0.7*0.3 = 0.42. Homozygous recessive (aa) = q^2 = 0.09."),
    ("natural_selection",
     "The peppered moth (Biston betularia) example of industrial melanism demonstrates:",
     "Natural selection — dark moths survived better on soot-blackened trees during industrial revolution",
     ["Genetic drift", "Lamarckian inheritance", "Mutation alone"],
     "Before: pale moths camouflaged on lichen-covered trees. After industrialisation: dark (melanic) moths camouflaged on black soot -> selected for."),
    ("evidence",
     "Analogous organs (like wings of birds and insects) are evidence of:",
     "Convergent evolution (different origins evolving similar functions in similar environments)",
     ["Divergent evolution", "Common ancestry", "Mutation rates"],
     "Analogous organs: same function, different evolutionary origin. Convergent evolution: unrelated species independently evolve similar adaptations."),
    ("hardy_weinberg",
     "Hardy-Weinberg equilibrium will be disrupted by:",
     "Natural selection (differential survival and reproduction of genotypes)",
     ["Large population size", "Random mating", "Absence of migration"],
     "H-W equilibrium requires: large population, random mating, no selection, no mutation, no migration/gene flow. Selection disrupts equilibrium."),
    ("natural_selection",
     "Lamarck's theory of evolution was incorrect because:",
     "Acquired characteristics are not inherited (e.g., a giraffe stretching its neck does not give offspring longer necks)",
     ["Organisms do not evolve", "Natural selection was wrong", "Mutations do not exist"],
     "Lamarck: use/disuse + inheritance of acquired traits. Incorrect because: changes in somatic cells are not transmitted to gametes (Weismann's germ-plasm theory)."),
    ("evidence",
     "The vestigial organs in humans include:",
     "Appendix, coccyx (tailbone), wisdom teeth, arrector pili muscles (goosebumps)",
     ["Heart", "Liver", "Kidney"],
     "Vestigial organs: reduced, non-functional remnants of structures that were functional in ancestors. Evidence of evolutionary history."),
    ("hardy_weinberg",
     "Genetic drift is most significant in:",
     "Small populations (random changes in allele frequencies have large effects)",
     ["Large populations", "Populations with high mutation rates", "Sexually reproducing organisms only"],
     "Genetic drift: random change in allele frequency. Effect is larger in small populations. Bottleneck effect and founder effect are types of genetic drift."),
    ("natural_selection",
     "Speciation occurs when:",
     "Populations become reproductively isolated and diverge genetically until they cannot interbreed",
     ["Organisms mutate", "Two populations have the same habitat", "Organisms live longer"],
     "Speciation: process of forming new species. Allopatric (geographic isolation) or sympatric (reproductive isolation without geography). Biological species concept."),
    ("evidence",
     "Radiocarbon dating (C-14) is used to determine the age of organic fossils up to approximately:",
     "50,000 years (after that, too little C-14 remains to measure)",
     ["500 million years", "5,000 years only", "1 billion years"],
     "C-14 half-life = 5,730 years. Useful for dating up to ~50,000 years. Older fossils use other isotopes (U-238, K-40) with longer half-lives."),
    ("natural_selection",
     "The concept of 'survival of the fittest' in Darwinian evolution means:",
     "Organisms best adapted to their environment survive and reproduce more (not necessarily physically strongest)",
     ["Strongest organisms always survive", "Fastest organisms win", "Largest organisms dominate"],
     "'Fittest' = best adapted to current environment. A slow herbivore might be 'fitter' than a fast predator if predators are absent. Context-dependent."),
    ("hardy_weinberg",
     "The bottleneck effect is an example of:",
     "Genetic drift — drastic reduction in population size removes alleles by chance",
     ["Natural selection", "Mutation", "Gene flow"],
     "Bottleneck: catastrophic population reduction -> survivors carry only a subset of original alleles -> reduced genetic diversity. E.g., cheetahs, elephant seals."),
    ("evidence",
     "Coelacanth (Latimeria) is called a 'living fossil' because:",
     "It closely resembles its fossil ancestors from 400 million years ago with little change",
     ["It is the oldest living fish", "It was recently discovered in fossils only", "It went extinct and was revived"],
     "Living fossils: organisms that have changed little over millions of years. E.g., coelacanth, horseshoe crab, ginkgo tree, nautilus."),
    ("natural_selection",
     "Antibiotic resistance in bacteria is a modern example of:",
     "Natural selection — bacteria with resistance mutations survive and reproduce in presence of antibiotics",
     ["Lamarckian evolution", "Genetic drift", "Convergent evolution"],
     "Bacteria: random mutations cause resistance (pre-existing variation). Antibiotics select for resistant bacteria. Resistant bacteria reproduce -> population becomes resistant."),
]

def gen_evolution(n=15):
    print(f"[Evolution] {n} questions...")
    for i, (scene, qtext, correct, wrongs, expl) in enumerate(EVOL_QA[:n]):
        opts=[correct]+wrongs[:3]; random.shuffle(opts); cidx=opts.index(correct)
        img=draw_evolution(scene); url=upload_pil(img, f"evol_{i}")
        ok=post_q("Science", 12, random.choice(["Advanced","Olympiad"]),
                  "Evolution", "Natural Selection and Genetics",
                  qtext, url, opts, cidx, expl)
        print(f"  evol_{i} ({scene})... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.3)
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OlympiadReady -- Class 11-12 Biology (Batch 9)")
    print("=" * 60)
    print()

    gen_cell(QPT)
    gen_genetics(QPT)
    gen_physio(QPT)
    gen_plant(QPT)
    gen_ecology(15)
    gen_evolution(15)

    print("=" * 60)
    print(f"DONE -- Posted: {POSTED}  Skipped: {SKIPPED}  Failed: {FAILED}")
    print("=" * 60)
