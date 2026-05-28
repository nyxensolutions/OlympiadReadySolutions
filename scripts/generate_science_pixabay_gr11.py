"""
generate_science_pixabay_gr11.py
High-quality Pixabay images -> Science-Biology, Chemistry, Physics Grade 11.

QUALITY RULES applied here:
  1. Pixabay query is EXACTLY what must be visible in the photo.
  2. Question text references a specific visible feature of the image.
  3. No question asks about something the image cannot show (e.g. no asking
     about atomic-level detail from a landscape photo).
  4. Each question is self-contained even without the image (image adds context,
     doesn't carry the entire question).
"""

import os, io, time, requests
import cloudinary, cloudinary.uploader

PIXABAY_API_KEY       = os.environ.get("PIXABAY_API_KEY", "56031484-1cf6e0a588c13eebd71681fda")
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE",
    "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY", "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME, api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET, secure=True)
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}
RUN_ID  = int(time.time())

posted = skipped = failed = 0

_dl = requests.Session()
_dl.headers.update({"User-Agent": "Mozilla/5.0 (compatible; OlympiadReady/1.0)"})

def pixabay_fetch(query, idx=0):
    params = {"key": PIXABAY_API_KEY, "q": query, "image_type": "photo",
              "orientation": "horizontal", "safesearch": "true",
              "per_page": 10, "order": "popular"}
    try:
        r = requests.get("https://pixabay.com/api/", params=params, timeout=12)
        r.raise_for_status()
        hits = r.json().get("hits", [])
    except Exception as e:
        print(f"    [PIXABAY ERR] '{query}': {e}"); return None
    if not hits:
        print(f"    [NO HITS] '{query}'"); return None
    for hi in range(min(len(hits), 5)):
        hit = hits[(idx + hi) % len(hits)]
        img_url = hit.get("previewURL") or hit.get("webformatURL")
        if not img_url: continue
        try:
            time.sleep(1.5)
            dl = _dl.get(img_url, timeout=20); dl.raise_for_status()
        except Exception as e:
            print(f"    [DL ERR] '{query}' hit {hi}: {e}"); continue
        pub_id = f"{CLOUDINARY_FOLDER}/g11_{query[:26].replace(' ','-')}_{RUN_ID}_{hit['id']}"
        try:
            time.sleep(1.0)
            res = cloudinary.uploader.upload(io.BytesIO(dl.content), public_id=pub_id,
                                             overwrite=False, resource_type="image")
            return res["secure_url"]
        except Exception as e:
            print(f"    [CDN ERR] '{query}': {e}"); continue
    return None

def post_q(grade, diff, subject, topic, subtopic, qtext, img_url, opts, cidx, expl):
    global posted, skipped, failed
    payload = dict(subject=subject, grade=grade, difficulty=diff,
                   topic=topic, subTopic=subtopic, questionText=qtext,
                   imageUrl=img_url, options=opts, correctAnswer=chr(65+cidx), explanation=expl)
    for attempt in range(2):
        try:
            r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                              json=payload, headers=HEADERS, timeout=25)
            if r.status_code in (200, 201): posted += 1; return True
            elif r.status_code == 409:      skipped += 1; return False
            else: print(f"    [API {r.status_code}] {r.text[:80]}"); failed += 1; return False
        except Exception as e:
            if attempt == 0: time.sleep(3)
            else: print(f"    [ERR] {e}"); failed += 1; return False

def run_q(label, query, grade, diff, subject, topic, subtopic, qtext, opts, cidx, expl, idx=0):
    global failed
    print(f"  {label}...", end=" ", flush=True)
    url = pixabay_fetch(query, idx)
    if not url:
        print("-> NO IMAGE, skipping"); failed += 1; return
    ok = post_q(grade, diff, subject, topic, subtopic, qtext, url, opts, cidx, expl)
    print(f"-> {'ok' if ok else 'dup/fail'}")
    time.sleep(2.0)

def section(title):
    print(f"\n{'='*65}\n  {title}\n{'='*65}")

# =============================================================================
# SCIENCE-BIOLOGY GRADE 11
# Image query is carefully chosen to match EXACTLY what the question discusses.
# =============================================================================
BIO_G11 = [
    # Image: plant cell under microscope -> question about visible plant cell structures
    ("G11 Bio plant cell microscope",
     "plant cell microscope chloroplast green",
     11, "Olympiad", "Science-Biology", "Cell Biology", "Cell Organelles",
     "The image shows a plant cell viewed through a microscope. The green disc-shaped structures visible inside the cell are chloroplasts. The PRIMARY function of chloroplasts is:",
     ["Carrying out photosynthesis — converting light energy into chemical energy (glucose)",
      "Cellular respiration — breaking down glucose for energy",
      "Protein synthesis — making enzymes for the cell",
      "Storing water and maintaining cell turgidity"],
     0,
     "Chloroplasts contain chlorophyll and are the site of photosynthesis: 6CO2 + 6H2O + light -> C6H12O6 + 6O2. They have a double membrane, stroma, and thylakoid grana where light reactions occur."),

    # Image: mitosis dividing cells -> question about the visible stage
    ("G11 Bio mitosis chromosomes",
     "mitosis cell division chromosomes aligned",
     11, "Olympiad", "Science-Biology", "Cell Biology", "Cell Division",
     "The image shows cells undergoing mitosis. In the stage where chromosomes are maximally condensed and aligned at the cell's equatorial plate (metaphase plate), spindle fibres attach to the:",
     ["Centromere of each chromosome",
      "Telomere (tips) of each chromosome",
      "Nuclear membrane",
      "Cell wall"],
     0,
     "During Metaphase: spindle fibres (microtubules) from opposite poles attach to the centromere of each chromosome via protein complexes called kinetochores. This ensures each daughter cell receives one chromatid from each chromosome."),

    # Image: neuron/nerve cell -> question about neuron structure
    ("G11 Bio neuron nerve cell",
     "neuron nerve cell biology diagram",
     11, "Olympiad", "Science-Biology", "Human Physiology", "Nervous System",
     "The image shows a neuron (nerve cell). The long fibre-like projection that carries electrical impulses AWAY from the cell body to the next neuron or effector is called the:",
     ["Axon",
      "Dendrite",
      "Myelin sheath",
      "Synapse"],
     0,
     "Axon: carries impulses away from the cell body (efferent). Dendrites: carry impulses TOWARDS the cell body (afferent). Myelin sheath: insulating layer around the axon that speeds conduction. Synapse: the gap between two neurons."),

    # Image: heart dissection or anatomical model -> question about heart chambers
    ("G11 Bio heart chambers anatomy",
     "heart anatomy chambers ventricle atrium dissection",
     11, "Olympiad", "Science-Biology", "Human Physiology", "Circulatory System",
     "The image shows the internal anatomy of the human heart. The left ventricle has significantly thicker muscular walls than the right ventricle because it must:",
     ["Pump oxygenated blood at high pressure through the aorta to the entire body (systemic circulation)",
      "Pump blood only to the lungs (a short distance)",
      "Receive blood from the pulmonary veins",
      "Filter blood like a kidney"],
     0,
     "The left ventricle pumps blood through systemic circulation — to every organ via the aorta. This requires much higher pressure than pulmonary circulation (right ventricle -> lungs). Hence the left ventricle wall is ~3x thicker."),

    # Image: pollen grains microscopy -> question about pollination biology
    ("G11 Bio pollen microscope",
     "pollen grains microscope biology flower",
     11, "Olympiad", "Science-Biology", "Plant Biology", "Reproduction",
     "The image shows pollen grains under a microscope. After a pollen grain lands on the stigma, it germinates and grows a pollen tube. The pollen tube grows through the style to the ovule carrying:",
     ["Two male gametes (sperm cells) — one fertilises the egg, one fuses with the polar nuclei (double fertilisation in angiosperms)",
      "Only one male gamete that fertilises the egg",
      "The entire pollen grain into the ovule",
      "Nutrients to feed the developing embryo"],
     0,
     "Double fertilisation (unique to angiosperms): Sperm 1 + egg -> zygote (2n) -> embryo. Sperm 2 + 2 polar nuclei -> endosperm (3n) -> food tissue for seed. This is a key feature distinguishing angiosperms from gymnosperms."),

    # Image: kidney nephron diagram/model -> question about filtration
    ("G11 Bio kidney nephron",
     "kidney nephron anatomy filtration model",
     11, "Olympiad", "Science-Biology", "Human Physiology", "Excretion",
     "The image shows the structure of a nephron in the kidney. Ultra-filtration of blood occurs in the Bowman's capsule, where blood is filtered from the:",
     ["Glomerulus — a tuft of capillaries inside the Bowman's capsule",
      "Loop of Henle",
      "Collecting duct",
      "Renal pelvis"],
     0,
     "The glomerulus is a knot of fenestrated capillaries inside the Bowman's capsule. High blood pressure forces water, glucose, salts, and urea out of blood into the Bowman's capsule (glomerular filtrate). Large proteins and blood cells are too big to pass."),

    # Image: lungs alveoli close-up -> question about gas exchange
    ("G11 Bio lungs alveoli",
     "lungs alveoli gas exchange respiratory",
     11, "Olympiad", "Science-Biology", "Human Physiology", "Respiratory System",
     "The image shows the alveoli of the lungs — tiny air sacs where gas exchange occurs. The alveoli are highly efficient for gas exchange because they have: (i) very thin walls (one cell thick), (ii) a rich capillary network, and (iii) a large total surface area. What is the approximate total surface area of human alveoli?",
     ["About 70 square metres (the size of a tennis court)",
      "About 1 square metre",
      "About 5 square metres",
      "About 500 square metres"],
     0,
     "Human lungs contain ~480 million alveoli, giving a total surface area of ~70 m2 — roughly the size of a tennis court. This enormous surface area, combined with thin walls and dense capillaries, enables efficient O2/CO2 exchange."),

    # Image: blood smear under microscope showing RBC, WBC, platelets
    ("G11 Bio blood smear microscope",
     "blood smear microscope red white cells platelets",
     11, "Olympiad", "Science-Biology", "Human Physiology", "Blood & Immunity",
     "A blood smear under a microscope (as shown) reveals different blood cell types. The most numerous cells — biconcave, enucleated (no nucleus), pink-staining cells — are red blood cells. Adult humans have approximately how many RBCs per microlitre of blood?",
     ["4.5 to 5.5 million RBCs per microlitre",
      "4,500 to 11,000 (WBC count, not RBC)",
      "150,000 to 400,000 (platelet count)",
      "1,000 to 2,000"],
     0,
     "Normal RBC count: 4.5-5.5 million/microlitre (men slightly higher than women). WBC count: 4,500-11,000/microlitre. Platelet count: 150,000-400,000/microlitre. RBCs are by far the most numerous formed elements of blood."),

    # Image: DNA gel electrophoresis
    ("G11 Bio DNA gel electrophoresis",
     "DNA gel electrophoresis genetics laboratory bands",
     11, "Olympiad", "Science-Biology", "Molecular Biology", "DNA Technology",
     "The image shows DNA gel electrophoresis. In this technique, DNA fragments are separated by size as they migrate through an agarose gel under an electric field. Smaller DNA fragments migrate:",
     ["Farther (faster) — smaller fragments face less resistance in the gel matrix",
      "Less far (slower) — smaller fragments carry less charge",
      "At the same rate regardless of size",
      "Towards the positive electrode only if they are single-stranded"],
     0,
     "DNA is negatively charged (phosphate backbone), so it migrates towards the positive electrode. Smaller fragments move faster through the agarose matrix (less resistance) and travel farther. This creates a pattern of bands used in forensics, paternity testing, and genetic research."),

    # Image: plant showing tropism (growing towards light)
    ("G11 Bio phototropism plant",
     "plant growing towards light phototropism tropism",
     11, "Olympiad", "Science-Biology", "Plant Physiology", "Plant Hormones",
     "The image shows a plant bending towards a light source (phototropism). This bending is caused by unequal distribution of the plant hormone:",
     ["Auxin (IAA) — accumulates on the shaded side, causing faster cell elongation there",
      "Gibberellin — promotes overall stem elongation equally",
      "Cytokinin — promotes cell division in roots",
      "Abscisic acid — causes stomata to close in drought"],
     0,
     "Phototropism: auxin (IAA) redistributes to the shaded side of the shoot tip. Higher auxin concentration -> faster cell elongation on shaded side -> shoot bends towards light. This was demonstrated in Went's experiment with oat coleoptiles."),
]

# =============================================================================
# SCIENCE-CHEMISTRY GRADE 11
# =============================================================================
CHEM_G11 = [
    # Image: periodic table -> question about periodicity trends
    ("G11 Chem periodic table trends",
     "periodic table elements chemistry colourful",
     11, "Olympiad", "Science-Chemistry", "Periodic Table", "Periodic Trends",
     "Looking at the periodic table, atomic radius generally DECREASES across a period (left to right). The primary reason is:",
     ["Increasing nuclear charge (more protons) pulls electrons closer while electron shielding remains nearly constant",
      "The number of electron shells increases",
      "More neutrons compress the nucleus",
      "Electrons are lost as you move right across a period"],
     0,
     "Across a period: proton count increases (greater nuclear charge) but electrons are added to the SAME shell (shielding is nearly constant). Greater nuclear attraction pulls electron cloud closer -> smaller radius. Down a group: new shells added -> radius increases."),

    # Image: chemical laboratory with glassware, colourful solutions
    ("G11 Chem molar solution preparation",
     "chemistry laboratory volumetric flask solution preparation",
     11, "Olympiad", "Science-Chemistry", "Solutions", "Molar Concentration",
     "The image shows a chemist preparing a molar solution using a volumetric flask. To prepare 500 mL of 2M NaCl solution, how many grams of NaCl are needed? (Molar mass of NaCl = 58.5 g/mol)",
     ["58.5 g",
      "117 g",
      "29.25 g",
      "23.4 g"],
     0,
     "Moles needed = Molarity x Volume(L) = 2 x 0.5 = 1 mol. Mass = moles x molar mass = 1 x 58.5 = 58.5 g. Dissolve 58.5 g NaCl in water and make up to 500 mL in a volumetric flask."),

    # Image: organic chemistry molecular models (ball-and-stick)
    ("G11 Chem organic molecular model",
     "organic chemistry molecular model ball stick carbon",
     11, "Olympiad", "Science-Chemistry", "Organic Chemistry", "Hybridisation",
     "The image shows ball-and-stick molecular models of organic compounds. In ethene (C2H4), each carbon atom is sp2 hybridised. This means the double bond consists of:",
     ["One sigma bond (sp2-sp2 overlap) AND one pi bond (sideways overlap of unhybridised p orbitals)",
      "Two sigma bonds",
      "Two pi bonds",
      "One sigma bond formed by s-orbital overlap only"],
     0,
     "sp2 hybridisation: 3 hybrid orbitals form 3 sigma bonds (C-C and 2 C-H). Each carbon retains one unhybridised p orbital perpendicular to the plane. These p orbitals overlap sideways -> pi bond. Double bond = 1 sigma + 1 pi."),

    # Image: gas jar / combustion experiment
    ("G11 Chem combustion reaction",
     "combustion chemistry burning flame experiment",
     11, "Olympiad", "Science-Chemistry", "Thermochemistry", "Enthalpy",
     "The image shows a combustion reaction. The complete combustion of methane (CH4) releases 890 kJ/mol. This means the reaction is:",
     ["Exothermic — enthalpy change (delta H) is negative; energy is released to surroundings",
      "Endothermic — energy is absorbed from surroundings",
      "Neither — enthalpy change is zero",
      "Exothermic — delta H is positive"],
     0,
     "Exothermic reactions release heat: delta H < 0 (negative). CH4 + 2O2 -> CO2 + 2H2O, delta H = -890 kJ/mol. Endothermic reactions absorb heat: delta H > 0. Combustion is always exothermic."),

    # Image: electrochemical cell / battery
    ("G11 Chem electrochemical cell battery",
     "electrochemical cell battery galvanic zinc copper",
     11, "Olympiad", "Science-Chemistry", "Electrochemistry", "Redox & EMF",
     "The image shows a galvanic cell. In the Daniell cell (Zn-Cu), the standard cell potential (E0 cell) is +1.10 V. This value is calculated as:",
     ["E0 cell = E0 cathode - E0 anode = E0(Cu2+/Cu) - E0(Zn2+/Zn) = +0.34 - (-0.76) = +1.10 V",
      "E0 cell = E0 anode - E0 cathode = -0.76 - 0.34 = -1.10 V",
      "E0 cell = sum of both electrode potentials = 0.34 + 0.76 = 1.10 V (always add)",
      "E0 cell = average of both electrode potentials"],
     0,
     "E0 cell = E0 cathode (reduction) - E0 anode (reduction). Cu2+/Cu = +0.34V (cathode, higher reduction potential). Zn2+/Zn = -0.76V (anode, lower reduction potential). E0 = 0.34-(-0.76) = +1.10V. Positive E0 means spontaneous reaction."),

    # Image: chromatography paper/plate (TLC or paper)
    ("G11 Chem paper chromatography",
     "paper chromatography separation colour pigment",
     11, "Olympiad", "Science-Chemistry", "Analytical Chemistry", "Chromatography",
     "The image shows paper chromatography separating coloured pigments. The Rf value (Retardation factor) of a spot is calculated as:",
     ["Rf = Distance travelled by spot / Distance travelled by solvent front",
      "Rf = Distance by solvent / Distance by spot",
      "Rf = Speed of spot / Total time",
      "Rf = Mass of spot / Volume of solvent"],
     0,
     "Rf = (distance moved by substance) / (distance moved by solvent front). Rf is always between 0 and 1. It identifies compounds since each substance has a characteristic Rf value in a given solvent system. Rf does not depend on the distance the solvent travels."),

    # Image: flask with coloured solution showing acid-base indicators
    ("G11 Chem acid base indicator colour",
     "acid base indicator colour change phenolphthalein litmus",
     11, "Olympiad", "Science-Chemistry", "Acids & Bases", "Buffer Solutions",
     "The image shows an indicator colour change during an acid-base reaction. A buffer solution resists changes in pH. An acidic buffer typically consists of:",
     ["A weak acid AND its conjugate base (salt with a strong base), e.g., CH3COOH + CH3COONa",
      "A strong acid and strong base in equal amounts",
      "Only a weak acid dissolved in water",
      "A strong acid with its salt"],
     0,
     "Acidic buffer: weak acid (provides H+ when base is added) + its conjugate base/salt (provides base when acid is added). E.g., acetic acid + sodium acetate maintains pH ~4.75. Henderson-Hasselbalch: pH = pKa + log([A-]/[HA])."),

    # Image: hydrocarbon organic compound structure
    ("G11 Chem alkene structure",
     "alkene chemistry organic compound structure model",
     11, "Olympiad", "Science-Chemistry", "Organic Chemistry", "Alkenes & Addition",
     "The image shows the structure of an alkene. The addition of HBr to propene (CH3-CH=CH2) follows Markovnikov's rule. The MAJOR product is:",
     ["CH3-CHBr-CH3 (2-bromopropane) — Br attaches to the more substituted carbon",
      "CH3-CH2-CH2Br (1-bromopropane) — Br attaches to the terminal carbon",
      "CH3-CH=CH-Br (no addition, substitution)",
      "CH2Br-CH2-CH3 (equal mixture only)"],
     0,
     "Markovnikov's rule: in HX addition to an alkene, H attaches to the carbon with MORE hydrogens (less substituted) and X to the carbon with FEWER hydrogens (more substituted). Propene: H goes to CH2 (=2H) and Br goes to CH (=1H) -> 2-bromopropane."),

    # Image: distillation setup or reflux condenser
    ("G11 Chem distillation reflux",
     "distillation reflux condenser chemistry laboratory organic",
     11, "Olympiad", "Science-Chemistry", "Organic Chemistry", "Purification",
     "The image shows a reflux condenser setup used in organic chemistry. Reflux is used rather than simple heating because it:",
     ["Allows the reaction to proceed at the boiling point of the solvent while preventing loss of volatile reactants or products",
      "Speeds up the reaction by increasing pressure",
      "Prevents any chemical reaction from occurring",
      "Is used only for inorganic compounds"],
     0,
     "Reflux: the condenser condenses vapours back into the flask — maintaining the reaction at boiling temperature without losing volatile compounds. Used for reactions needing prolonged heating (e.g., ester hydrolysis, Grignard reactions)."),

    # Image: nitrogen cycle diagram / soil bacteria
    ("G11 Chem nitrogen fixation soil",
     "nitrogen fixation soil bacteria agriculture legume",
     11, "Olympiad", "Science-Chemistry", "Environmental Chemistry", "Nitrogen Cycle",
     "The image shows nitrogen-fixing bacteria in soil near legume roots. Industrial nitrogen fixation (Haber Process) produces ammonia from N2 and H2. The conditions used are:",
     ["450-500 degrees C, 150-200 atm pressure, iron catalyst",
      "100 degrees C, 1 atm, platinum catalyst",
      "800 degrees C, 500 atm, no catalyst",
      "25 degrees C, 1 atm, biological enzymes"],
     0,
     "Haber Process: N2 + 3H2 <-> 2NH3. Conditions: ~450-500 C (compromise — higher T favours reactants per Le Chatelier but gives acceptable rate), 150-200 atm (high P favours product — fewer moles of gas), iron catalyst (speeds equilibrium). Yield ~15-25%."),
]

# =============================================================================
# SCIENCE-PHYSICS GRADE 11
# =============================================================================
PHYS_G11 = [
    # Image: inclined plane with object and force arrows
    ("G11 Phys inclined plane forces",
     "inclined plane physics forces friction block",
     11, "Olympiad", "Science-Physics", "Mechanics", "Forces on Inclined Plane",
     "The image shows a block on a frictionless inclined plane at angle theta. The component of gravitational force acting ALONG the incline (causing it to slide down) is:",
     ["mg sin(theta)",
      "mg cos(theta)",
      "mg tan(theta)",
      "mg / sin(theta)"],
     0,
     "Resolve gravity (mg) into two components: (1) Along the incline: mg sin(theta) — causes sliding. (2) Perpendicular to incline: mg cos(theta) — equals normal force. On a frictionless surface, acceleration = g sin(theta)."),

    # Image: wave on string / transverse wave
    ("G11 Phys transverse wave string",
     "transverse wave string vibration physics wavelength",
     11, "Olympiad", "Science-Physics", "Waves", "Wave Properties",
     "The image shows a transverse wave on a string. The distance between two consecutive crests (or troughs) is the wavelength (lambda). If the wave frequency is 400 Hz and speed is 320 m/s, the wavelength is:",
     ["0.8 m",
      "128,000 m",
      "1.25 m",
      "0.5 m"],
     0,
     "v = f x lambda. Lambda = v/f = 320/400 = 0.8 m. Always: wave speed = frequency x wavelength. Units: m/s = Hz x m."),

    # Image: convex mirror showing diverging rays
    ("G11 Phys convex mirror rays",
     "convex mirror reflection ray diagram optics",
     11, "Olympiad", "Science-Physics", "Optics", "Mirrors",
     "The image shows a convex mirror with reflected rays. A convex mirror ALWAYS forms an image that is:",
     ["Virtual, erect (upright), and diminished (smaller than object) — regardless of object position",
      "Real, inverted, and magnified for objects close to the mirror",
      "Real, erect, and same size as the object",
      "Virtual, inverted, and magnified"],
     0,
     "Convex mirrors always form virtual (behind mirror), erect, and diminished images for all real object positions. This gives a wide field of view — used in rear-view mirrors and security mirrors. Only concave mirrors can form real images."),

    # Image: spring-mass system or simple pendulum
    ("G11 Phys spring mass SHM",
     "spring mass simple harmonic motion oscillation physics",
     11, "Olympiad", "Science-Physics", "Oscillations", "Simple Harmonic Motion",
     "The image shows a spring-mass system undergoing simple harmonic motion (SHM). The time period T of a spring-mass system depends on mass m and spring constant k as:",
     ["T = 2pi x sqrt(m/k) — period increases with mass, decreases with stiffer spring",
      "T = 2pi x sqrt(k/m)",
      "T = 2pi x sqrt(g/L) — only for pendulum",
      "T = m/k"],
     0,
     "Spring-mass: T = 2pi x sqrt(m/k). Greater mass -> greater inertia -> longer period. Stiffer spring (larger k) -> stronger restoring force -> shorter period. Simple pendulum: T = 2pi x sqrt(L/g) — depends on length, not mass."),

    # Image: circuit with capacitors
    ("G11 Phys capacitor circuit parallel",
     "capacitor circuit electronics parallel series",
     11, "Olympiad", "Science-Physics", "Electricity", "Capacitors",
     "The image shows capacitors in a circuit. Three capacitors of 2 microfarads, 3 microfarads, and 6 microfarads are connected in SERIES. The equivalent capacitance is:",
     ["1 microfarad",
      "11 microfarads",
      "3.67 microfarads",
      "0.5 microfarad"],
     0,
     "Series capacitors: 1/Ceq = 1/C1 + 1/C2 + 1/C3 = 1/2 + 1/3 + 1/6 = 3/6 + 2/6 + 1/6 = 6/6 = 1. So Ceq = 1 microfarad. (Opposite to resistors: series resistors add, series capacitors give smaller equivalent.)"),

    # Image: electromagnetic spectrum chart
    ("G11 Phys electromagnetic spectrum",
     "electromagnetic spectrum wavelength radio visible gamma",
     11, "Olympiad", "Science-Physics", "Waves", "Electromagnetic Spectrum",
     "The image shows the electromagnetic spectrum. All electromagnetic waves travel at the speed of light (3x10^8 m/s) in vacuum. Which type of EM radiation has the HIGHEST frequency and MOST energy per photon?",
     ["Gamma rays (from nuclear decay — wavelength < 0.01 nm)",
      "X-rays",
      "Visible light",
      "Radio waves (lowest frequency, lowest energy)"],
     0,
     "EM spectrum in order of increasing frequency (and energy): Radio -> Microwave -> Infrared -> Visible -> UV -> X-ray -> Gamma. E = hf (Planck's equation): energy is directly proportional to frequency. Gamma rays (from nuclear reactions) have the highest frequency and most energy per photon."),

    # Image: Bernoulli's principle / fluid flow / aerofoil
    ("G11 Phys Bernoulli aerofoil",
     "Bernoulli principle aerofoil wing aircraft lift fluid",
     11, "Olympiad", "Science-Physics", "Fluid Mechanics", "Bernoulli's Principle",
     "The image shows airflow over an aerofoil (aircraft wing). Bernoulli's principle states that in a fluid flow, as speed increases, pressure:",
     ["Decreases (higher velocity = lower pressure — generating lift on the wing)",
      "Increases proportionally",
      "Remains constant regardless of speed",
      "Increases only if the fluid is compressed"],
     0,
     "Bernoulli's equation: P + 1/2 rho v^2 + rho g h = constant. As v increases, P must decrease (for total to remain constant). Air moves faster over the curved top of a wing -> lower pressure above -> higher pressure below -> net upward force = lift."),

    # Image: nuclear fission chain reaction
    ("G11 Phys nuclear fission chain reaction",
     "nuclear fission chain reaction uranium reactor",
     11, "Olympiad", "Science-Physics", "Nuclear Physics", "Fission & Chain Reaction",
     "The image shows a nuclear fission chain reaction. In a nuclear reactor, a controlled chain reaction is maintained using control rods (typically boron or cadmium). These rods work by:",
     ["Absorbing excess neutrons to prevent runaway chain reaction",
      "Reflecting neutrons back into the fuel",
      "Slowing down uranium nuclei",
      "Generating additional neutrons to sustain the reaction"],
     0,
     "Control rods (boron/cadmium) are strong neutron absorbers. By inserting/withdrawing them, operators control neutron flux: more insertion -> fewer neutrons available -> reaction slows. Fully inserted = reaction stops. Moderator (heavy water/graphite) slows neutrons; control rods absorb them."),

    # Image: Doppler effect / ambulance wave compression
    ("G11 Phys Doppler effect sound",
     "Doppler effect sound wave ambulance frequency",
     11, "Olympiad", "Science-Physics", "Waves", "Doppler Effect",
     "The image illustrates the Doppler effect: sound waves from a moving ambulance appear compressed in front and stretched behind. As the ambulance approaches you, the pitch of the siren sounds:",
     ["Higher than actual pitch — wavefronts are compressed, increasing apparent frequency",
      "Lower than actual pitch",
      "Unchanged — Doppler only affects light, not sound",
      "Higher, but only if you are also moving"],
     0,
     "Doppler effect: when a sound source approaches, wavefronts are compressed -> shorter wavelength -> higher frequency -> higher pitch. As it recedes, wavelength stretches -> lower frequency -> lower pitch. The classic 'neeeeow' sound of a passing ambulance."),

    # Image: Young's double slit experiment showing interference fringes
    ("G11 Phys double slit interference",
     "double slit experiment interference fringes light",
     11, "Olympiad", "Science-Physics", "Optics", "Wave Optics",
     "The image shows interference fringes produced in Young's double slit experiment. Bright fringes (constructive interference) occur when the path difference between waves from the two slits is:",
     ["An integer multiple of the wavelength: delta = n*lambda (n = 0, 1, 2...)",
      "An odd multiple of half-wavelength: delta = (2n-1)*lambda/2",
      "Zero only (central maximum only)",
      "Always equal to the slit width"],
     0,
     "Constructive interference: path difference = n*lambda (waves arrive in phase -> crests reinforce). Destructive interference: path difference = (n+1/2)*lambda (waves arrive out of phase -> crests cancel troughs -> dark fringe). This experiment proved the wave nature of light."),
]

# =============================================================================
# RUN
# =============================================================================
def run_batch(name, questions):
    section(name)
    print(f"  Total: {len(questions)}")
    for q in questions:
        run_q(q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10])

if __name__ == "__main__":
    print("=" * 65)
    print("  OlympiadReady - Science Pixabay Grade 11 (High Quality)")
    total = len(BIO_G11) + len(CHEM_G11) + len(PHYS_G11)
    print(f"  Total: {total} questions  |  Bio: {len(BIO_G11)}  Chem: {len(CHEM_G11)}  Phys: {len(PHYS_G11)}")
    print("=" * 65)

    run_batch("Science-Biology Grade 11", BIO_G11)
    run_batch("Science-Chemistry Grade 11", CHEM_G11)
    run_batch("Science-Physics Grade 11", PHYS_G11)

    print(f"\n{'='*65}")
    print(f"DONE - Posted: {posted}  Skipped: {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
    print(f"{'='*65}")
