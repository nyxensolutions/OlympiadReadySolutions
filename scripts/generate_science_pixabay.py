"""
generate_science_pixabay.py
Real Pixabay photos -> Cloudinary -> Science image questions.

Subjects: Science-Biology, Science-Chemistry, Science-Physics
Grades: 9, 10, 11 (Olympiad/Advanced difficulty)
Format: real photo as questionImage, text A/B/C/D options.
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

def pixabay_fetch(query: str, idx: int = 0) -> str | None:
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
            img_bytes = dl.content
        except Exception as e:
            print(f"    [DL ERR] '{query}' hit {hi}: {e}"); continue
        pub_id = f"{CLOUDINARY_FOLDER}/sci_{query[:28].replace(' ','-')}_{RUN_ID}_{hit['id']}"
        try:
            time.sleep(1.0)
            res = cloudinary.uploader.upload(io.BytesIO(img_bytes), public_id=pub_id,
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
    print(f"\n{'='*60}\n  {title}\n{'='*60}")

# =============================================================================
# SCIENCE-BIOLOGY
# =============================================================================

BIO_QUESTIONS = [
    # Grade 9
    ("G9 Bio Cell microscope",
     "microscope biology cell slide laboratory",
     9, "Olympiad", "Science-Biology", "Cell Biology", "Cell Structure",
     "A student observes a cell under a microscope (as shown). The cell has a clearly visible cell wall and a large central vacuole. This cell is MOST LIKELY from:",
     ["A plant leaf","An animal muscle","A human cheek","A bacterial colony"], 0,
     "Plant cells have a rigid cell wall (absent in animal cells) and a large central vacuole. Animal cells lack cell walls and have only small vacuoles."),

    ("G9 Bio photosynthesis leaf",
     "green leaf plant sunlight photosynthesis",
     9, "Olympiad", "Science-Biology", "Plant Biology", "Photosynthesis",
     "The image shows a green leaf in sunlight. During photosynthesis, which gas is released from the leaf as a byproduct?",
     ["Oxygen (O2)","Carbon dioxide (CO2)","Nitrogen (N2)","Hydrogen (H2)"], 0,
     "Photosynthesis: CO2 + H2O + light -> glucose + O2. Oxygen is the byproduct, released through stomata."),

    ("G9 Bio human heart diagram",
     "human heart anatomy medical",
     9, "Advanced", "Science-Biology", "Human Physiology", "Circulatory System",
     "Looking at the image of the human heart, which chamber pumps oxygenated blood to the entire body?",
     ["Left ventricle","Right ventricle","Left atrium","Right atrium"], 0,
     "The left ventricle has the thickest muscular wall and pumps oxygenated blood at high pressure through the aorta to all body tissues."),

    ("G9 Bio food chain ecosystem",
     "food chain ecosystem predator prey nature",
     9, "Advanced", "Science-Biology", "Ecology", "Food Chains",
     "The image shows a natural ecosystem. In a food chain, which organism would occupy the FIRST trophic level?",
     ["Green plants (producers)","Herbivores","Carnivores","Decomposers"], 0,
     "The first trophic level always consists of producers — green plants that capture solar energy via photosynthesis. All other organisms depend on them."),

    ("G9 Bio bacteria microscope",
     "bacteria microscope culture petri dish",
     9, "Olympiad", "Science-Biology", "Microbiology", "Microorganisms",
     "The image shows bacteria grown on a petri dish. Bacteria are classified as prokaryotes because they:",
     ["Lack a membrane-bound nucleus","Cannot reproduce","Have no cell wall","Require oxygen to survive"], 0,
     "Prokaryotes (bacteria, archaea) lack a nuclear membrane — their DNA floats freely in the cytoplasm. Eukaryotes (plants, animals, fungi) have a true nucleus."),

    # Grade 10
    ("G10 Bio DNA double helix",
     "DNA double helix genetics molecular biology",
     10, "Olympiad", "Science-Biology", "Genetics", "DNA Structure",
     "The image shows the structure of DNA. The two strands are held together by hydrogen bonds between complementary base pairs. Which bases pair with each other?",
     ["Adenine-Thymine and Guanine-Cytosine","Adenine-Guanine and Thymine-Cytosine","Adenine-Cytosine and Guanine-Thymine","All four bases pair randomly"], 0,
     "Chargaff's rules: A pairs with T (2 hydrogen bonds), G pairs with C (3 hydrogen bonds). This complementary base pairing is the basis of DNA replication and transcription."),

    ("G10 Bio human brain",
     "human brain anatomy neuroscience",
     10, "Advanced", "Science-Biology", "Human Physiology", "Nervous System",
     "The image shows the human brain. Which part of the brain is responsible for coordinating balance and muscle movement?",
     ["Cerebellum","Cerebrum","Medulla oblongata","Hypothalamus"], 0,
     "The cerebellum (at the back of the brain) coordinates voluntary movement, balance, and fine motor skills. The cerebrum handles thinking; medulla controls involuntary functions."),

    ("G10 Bio mitosis cell division",
     "cell division mitosis biology chromosomes",
     10, "Olympiad", "Science-Biology", "Cell Biology", "Cell Division",
     "The image shows a cell undergoing division. In which phase of mitosis do chromosomes align at the cell's equatorial plate (metaphase plate)?",
     ["Metaphase","Prophase","Anaphase","Telophase"], 0,
     "During Metaphase, chromosomes are maximally condensed and align along the cell's equatorial plate. Spindle fibres attach to centromeres of each chromosome."),

    ("G10 Bio flower pollination",
     "flower pollination bee pollen nature",
     10, "Advanced", "Science-Biology", "Plant Biology", "Reproduction",
     "The image shows a bee visiting a flower for pollination. This type of pollination (by insects) is called:",
     ["Entomophily","Anemophily","Hydrophily","Ornithophily"], 0,
     "Entomophily = insect pollination. Anemophily = wind pollination. Hydrophily = water pollination. Ornithophily = bird pollination."),

    ("G10 Bio human digestive system",
     "human digestive system anatomy stomach intestine",
     10, "Advanced", "Science-Biology", "Human Physiology", "Digestion",
     "Looking at the digestive system image, where does the absorption of most nutrients (glucose, amino acids) into the bloodstream occur?",
     ["Small intestine","Large intestine","Stomach","Oesophagus"], 0,
     "The small intestine (especially jejunum and ileum) has finger-like villi and microvilli that dramatically increase surface area for nutrient absorption into blood and lymph."),

    # Grade 11
    ("G11 Bio enzyme action",
     "enzyme laboratory biochemistry protein structure",
     11, "Olympiad", "Science-Biology", "Biochemistry", "Enzymes",
     "The image represents enzyme-substrate interaction. An enzyme's activity completely stops at 70°C but returns to normal when cooled to 37°C. This suggests the enzyme was:",
     ["Temporarily inhibited (not denatured)","Permanently denatured","Destroyed by heat","Converted to a different enzyme"], 0,
     "Denaturation is permanent — the enzyme would NOT recover. The fact that activity returns means the enzyme was only temporarily inhibited at 70°C (perhaps reversibly unfolded), not denatured."),

    ("G11 Bio genetics Mendel",
     "genetics heredity pea plant Mendel experiment",
     11, "Olympiad", "Science-Biology", "Genetics", "Mendelian Genetics",
     "In Mendel's pea plant experiments (shown in image), when a tall plant (TT) was crossed with a dwarf plant (tt), ALL F1 plants were tall. This demonstrates:",
     ["Dominance — T allele masks the effect of t allele","Codominance — both alleles express equally","Incomplete dominance — blending of traits","Mutation — t allele transformed to T"], 0,
     "When TT x tt gives all Tt (tall) offspring, it shows complete dominance — the T (tall) allele is dominant over t (dwarf). Only one dominant allele is enough for the tall phenotype."),

    ("G11 Bio ecosystem food web",
     "ecosystem biodiversity forest wildlife food web",
     11, "Advanced", "Science-Biology", "Ecology", "Ecosystems",
     "The image shows a forest ecosystem. The total amount of living organic matter in an ecosystem at a given time is called:",
     ["Biomass","Biosphere","Biodiversity","Biogeography"], 0,
     "Biomass = total mass of living organisms in an ecosystem at a given time. It can be expressed as dry weight. Biosphere = entire zone of life on Earth."),

    ("G11 Bio human kidney",
     "human kidney nephron anatomy",
     11, "Advanced", "Science-Biology", "Human Physiology", "Excretion",
     "The image shows the human kidney. The functional unit of the kidney that filters blood and forms urine is called the:",
     ["Nephron","Neuron","Glomerulus alone","Ureter"], 0,
     "The nephron is the structural and functional unit of the kidney. Each kidney contains about 1 million nephrons. The glomerulus is only one part of the nephron."),

    ("G11 Bio blood cells",
     "blood cells red white platelets microscope",
     11, "Olympiad", "Science-Biology", "Human Physiology", "Blood",
     "The microscope image shows human blood cells. The biconcave, disc-shaped cells without a nucleus are:",
     ["Red blood cells (RBCs / erythrocytes)","White blood cells (WBCs)","Platelets","Plasma cells"], 0,
     "RBCs are uniquely biconcave and lack a nucleus (in mammals) — this maximises surface area for oxygen binding and allows flexibility to pass through capillaries."),
]

# =============================================================================
# SCIENCE-CHEMISTRY
# =============================================================================

CHEM_QUESTIONS = [
    # Grade 9
    ("G9 Chem lab glassware",
     "chemistry laboratory glassware beaker flask",
     9, "Advanced", "Science-Chemistry", "Lab Skills", "Laboratory Equipment",
     "The image shows common chemistry laboratory glassware. Which piece of equipment is used to measure an EXACT volume of liquid accurately?",
     ["Measuring cylinder (graduated cylinder)","Beaker","Conical flask","Test tube"], 0,
     "A graduated/measuring cylinder is used for accurate volume measurement. Beakers and conical flasks only have approximate markings and are not used for precise measurements."),

    ("G9 Chem periodic table",
     "periodic table elements chemistry science",
     9, "Olympiad", "Science-Chemistry", "Periodic Table", "Elements & Groups",
     "Looking at the periodic table image, elements in the same GROUP (vertical column) have similar chemical properties because they have:",
     ["The same number of valence electrons","The same atomic mass","The same number of neutrons","The same period number"], 0,
     "Elements in the same group have identical numbers of valence (outermost) electrons, which determines their chemical behaviour and bonding."),

    ("G9 Chem acid base litmus",
     "litmus paper acid base indicator chemistry",
     9, "Advanced", "Science-Chemistry", "Acids & Bases", "Indicators",
     "The image shows litmus paper tests. Red litmus paper turned blue when dipped in a solution. What does this tell us?",
     ["The solution is basic (alkaline)","The solution is acidic","The solution is neutral","The solution is a salt"], 0,
     "Red litmus turns blue in basic (alkaline) solutions. Blue litmus turns red in acidic solutions. No change = neutral."),

    ("G9 Chem rusting iron",
     "rusting iron metal corrosion oxidation",
     9, "Advanced", "Science-Chemistry", "Chemical Reactions", "Oxidation",
     "The image shows rusted iron. Rusting is an example of which type of chemical reaction?",
     ["Oxidation (iron reacts with oxygen and water)","Reduction","Neutralisation","Decomposition"], 0,
     "Rusting: 4Fe + 3O2 + 6H2O -> 4Fe(OH)3 -> Fe2O3.xH2O (rust). Iron is oxidised (loses electrons to oxygen). This requires both oxygen and moisture."),

    ("G9 Chem flame test colours",
     "flame test chemistry metal ions colour",
     9, "Olympiad", "Science-Chemistry", "Atomic Structure", "Spectroscopy",
     "The image shows flame tests for different metal ions. A sample gives a brick-red/orange-red flame. Which metal ion is MOST LIKELY present?",
     ["Calcium (Ca2+)","Sodium (Na+)","Potassium (K+)","Copper (Cu2+)"], 0,
     "Flame test colours: Na+=yellow/orange, K+=lilac/violet, Ca2+=brick-red, Cu2+=blue-green, Li+=crimson red. Brick-red indicates calcium."),

    # Grade 10
    ("G10 Chem electrolysis setup",
     "electrolysis electrochemistry apparatus laboratory",
     10, "Olympiad", "Science-Chemistry", "Electrochemistry", "Electrolysis",
     "The image shows an electrolysis setup. During electrolysis of dilute sulphuric acid, which gas is produced at the CATHODE (negative electrode)?",
     ["Hydrogen (H2)","Oxygen (O2)","Sulphur dioxide (SO2)","Chlorine (Cl2)"], 0,
     "At cathode: 2H+ + 2e- -> H2 (reduction). At anode: 4OH- -> 2H2O + O2 + 4e- (oxidation). Hydrogen at cathode, oxygen at anode."),

    ("G10 Chem chemical bonds",
     "molecular model chemistry bonds atoms",
     10, "Advanced", "Science-Chemistry", "Chemical Bonding", "Ionic & Covalent Bonds",
     "The image shows a molecular model. In an ionic bond (e.g., NaCl), the bond forms because:",
     ["One atom transfers electrons to another, creating oppositely charged ions that attract","Two atoms share electrons equally","Electrons are delocalised across many atoms","Protons are shared between nuclei"], 0,
     "Ionic bonding: metal (Na) loses electron -> Na+; non-metal (Cl) gains electron -> Cl-. Opposite charges attract forming the ionic bond."),

    ("G10 Chem distillation apparatus",
     "distillation apparatus chemistry laboratory",
     10, "Advanced", "Science-Chemistry", "Separation Methods", "Distillation",
     "The image shows a distillation setup. This technique separates liquids based on differences in their:",
     ["Boiling points","Densities","Melting points","Solubility"], 0,
     "Distillation separates liquids by exploiting different boiling points — the more volatile liquid evaporates first, travels through the condenser, and is collected as the distillate."),

    ("G10 Chem reaction rates",
     "chemical reaction rate chemistry experiment bubbles",
     10, "Olympiad", "Science-Chemistry", "Reaction Rates", "Factors Affecting Rate",
     "Two identical marble chips are added to two flasks of hydrochloric acid — one in powder form, one as large chips. Which reacts FASTER and why?",
     ["Powder — greater surface area exposes more reactant particles to acid","Large chips — more mass means more reactant","Both react at the same rate","Large chips — less surface area slows the reaction down less"], 0,
     "Increasing surface area (powdering the marble) exposes more reactant particles to acid molecules, increasing collision frequency and therefore reaction rate."),

    ("G10 Chem organic chemistry carbon",
     "organic chemistry molecular model carbon chain",
     10, "Olympiad", "Science-Chemistry", "Organic Chemistry", "Hydrocarbons",
     "The image shows a carbon chain molecule. The general formula CnH(2n+2) represents which class of organic compounds?",
     ["Alkanes (saturated hydrocarbons)","Alkenes","Alkynes","Alcohols"], 0,
     "Alkanes follow CnH(2n+2): methane CH4 (n=1), ethane C2H6 (n=2), propane C3H8 (n=3). They are saturated (only single C-C bonds)."),

    # Grade 11
    ("G11 Chem titration",
     "titration burette chemistry laboratory acid base",
     11, "Olympiad", "Science-Chemistry", "Analytical Chemistry", "Acid-Base Titration",
     "The image shows a titration setup with a burette. In a titration of NaOH against HCl using phenolphthalein indicator, the endpoint is reached when:",
     ["The solution turns from colourless to faint pink (and stays pink for 30s)","The solution turns from pink to colourless","The solution turns yellow","The burette reads exactly 25 mL"], 0,
     "Phenolphthalein is colourless in acid and pink in base. When titrating base into acid, at the endpoint the solution just turns faint pink (one excess drop of NaOH makes it basic)."),

    ("G11 Chem equilibrium",
     "chemical equilibrium reversible reaction chemistry",
     11, "Olympiad", "Science-Chemistry", "Chemical Equilibrium", "Le Chatelier's Principle",
     "For the reaction N2 + 3H2 <-> 2NH3 (exothermic), what happens to NH3 yield if temperature is INCREASED at constant pressure?",
     ["Yield decreases — equilibrium shifts left (endothermic direction)","Yield increases — more energy means more product","Yield stays the same","Reaction stops completely"], 0,
     "Le Chatelier's principle: increasing temperature shifts equilibrium in the endothermic direction (reverse reaction) to absorb heat. For this exothermic reaction, NH3 yield falls."),

    ("G11 Chem electrochemical cell",
     "electrochemical cell battery galvanic voltaic",
     11, "Advanced", "Science-Chemistry", "Electrochemistry", "Galvanic Cells",
     "The image shows a galvanic (voltaic) cell. In this cell, oxidation occurs at the:",
     ["Anode (negative terminal)","Cathode (positive terminal)","Salt bridge","Both electrodes equally"], 0,
     "OIL RIG: Oxidation Is Loss at the anode. Reduction Is Gain at the cathode. In galvanic cells, the anode is the negative terminal (spontaneous oxidation)."),

    ("G11 Chem spectroscopy",
     "spectroscopy chemistry light spectrum wavelength",
     11, "Olympiad", "Science-Chemistry", "Atomic Structure", "Emission Spectra",
     "The image shows atomic emission spectra. Each element produces a unique set of spectral lines because:",
     ["Electrons transition between fixed energy levels unique to each element","All elements have the same electron configuration","Light refracts differently for each element","Protons emit different wavelengths"], 0,
     "Each element's electrons occupy unique energy levels. When excited electrons fall back to lower levels, they emit photons of specific wavelengths — creating a unique fingerprint spectrum."),

    ("G11 Chem polymer plastic",
     "polymer plastic chemistry molecular chain",
     11, "Advanced", "Science-Chemistry", "Organic Chemistry", "Polymers",
     "The image shows a polymer chain. Polyethylene (polythene) is made by joining many ethylene (C2H4) monomers. This process is called:",
     ["Addition polymerisation","Condensation polymerisation","Hydrolysis","Fermentation"], 0,
     "Addition polymerisation: unsaturated monomers (with C=C double bonds) join by opening their double bonds — no atoms are lost. Condensation polymerisation releases small molecules (e.g., water)."),
]

# =============================================================================
# SCIENCE-PHYSICS
# =============================================================================

PHYS_QUESTIONS = [
    # Grade 9
    ("G9 Phys Newton cradle",
     "Newton cradle pendulum physics momentum",
     9, "Olympiad", "Science-Physics", "Forces", "Newton's Laws",
     "The image shows a Newton's cradle demonstrating conservation of momentum and energy. When one ball strikes the row, exactly one ball swings out on the other side. This demonstrates:",
     ["Both momentum AND kinetic energy are conserved in elastic collisions","Only momentum is conserved","Only energy is conserved","Neither is conserved — energy is created"], 0,
     "Newton's cradle is an elastic collision — both linear momentum and kinetic energy are conserved. This forces exactly one ball out at the same speed, not two balls at half speed."),

    ("G9 Phys rainbow light prism",
     "prism rainbow light refraction spectrum physics",
     9, "Advanced", "Science-Physics", "Light", "Dispersion",
     "The image shows white light passing through a prism and splitting into colours. This phenomenon is called dispersion and occurs because:",
     ["Different colours of light have different speeds in glass (different refractive indices)","White light contains only 3 colours","Glass absorbs some colours","Prisms generate new colours from white light"], 0,
     "Different wavelengths travel at slightly different speeds in glass, giving each colour a different refractive index. Violet bends most, red least — creating the visible spectrum."),

    ("G9 Phys magnet magnetic field",
     "magnet magnetic field lines iron filings physics",
     9, "Advanced", "Science-Physics", "Magnetism", "Magnetic Fields",
     "The image shows iron filings around a bar magnet revealing magnetic field lines. The field lines always:",
     ["Go from North pole to South pole outside the magnet","Go from South to North outside","Intersect each other","Run parallel to the magnet's length"], 0,
     "By convention, magnetic field lines exit the North pole and enter the South pole outside the magnet (and travel from South to North inside the magnet). They never cross."),

    ("G9 Phys electric circuit",
     "electric circuit components resistor battery bulb",
     9, "Advanced", "Science-Physics", "Electricity", "Electric Circuits",
     "The image shows a simple electric circuit. Two resistors of 4 ohms each are connected in PARALLEL across a 12V battery. The total current drawn from the battery is:",
     ["6 A","3 A","1.5 A","12 A"], 0,
     "Parallel: total resistance = (4×4)/(4+4) = 2 ohms. Current = V/R = 12/2 = 6 A. (Or: each branch draws 3A, total = 6A.)"),

    ("G9 Phys sound waves",
     "sound wave oscilloscope waveform frequency",
     9, "Olympiad", "Science-Physics", "Sound", "Wave Properties",
     "The image shows a sound wave on an oscilloscope. Which property of the wave determines the PITCH of the sound?",
     ["Frequency (number of cycles per second)","Amplitude (height of wave)","Wavelength in vacuum","Speed of the wave"], 0,
     "Pitch is determined by frequency — higher frequency = higher pitch. Amplitude determines loudness. Speed is constant in a given medium regardless of pitch."),

    # Grade 10
    ("G10 Phys lens ray diagram",
     "convex lens ray diagram optics physics",
     10, "Olympiad", "Science-Physics", "Light", "Lenses & Optics",
     "The image shows a ray diagram for a convex lens. When an object is placed at the focal point (F) of a convex lens, the image formed is:",
     ["At infinity — rays emerge parallel and do not converge","At 2F on the other side","Virtual and upright behind the lens","At F on the same side"], 0,
     "When the object is at F, incident rays emerge parallel after refraction — they never converge, so the image is formed at infinity. This is how a collimator works."),

    ("G10 Phys electromagnet",
     "electromagnet coil wire electric current",
     10, "Advanced", "Science-Physics", "Electromagnetism", "Electromagnets",
     "The image shows an electromagnet. Compared to a permanent magnet, the MAIN advantage of an electromagnet is:",
     ["Its magnetic strength can be controlled and switched off","It is stronger than all permanent magnets","It works without any electricity","It never loses its magnetism"], 0,
     "Electromagnets can be switched on/off and their field strength adjusted by varying current — essential for cranes, MRI machines, electric motors, relays."),

    ("G10 Phys nuclear atom model",
     "atom nucleus proton neutron electron model",
     10, "Olympiad", "Science-Physics", "Atomic Physics", "Nuclear Structure",
     "The image shows an atomic model. The nucleus of an atom contains protons and neutrons. The number of protons in the nucleus determines the element's:",
     ["Atomic number (and thus chemical identity)","Mass number","Number of electrons in ions","Isotope type"], 0,
     "The atomic number = number of protons = unique identifier of an element. Carbon always has 6 protons; changing proton count changes the element entirely."),

    ("G10 Phys reflection mirror",
     "mirror reflection angle of incidence optics",
     10, "Advanced", "Science-Physics", "Light", "Reflection",
     "The image shows light reflecting off a plane mirror. The angle of incidence is 35 degrees. What is the angle of reflection?",
     ["35 degrees","70 degrees","55 degrees","45 degrees"], 0,
     "Law of reflection: angle of incidence = angle of reflection (both measured from the normal). So reflection angle = 35 degrees."),

    ("G10 Phys transformer",
     "transformer electrical coil electricity power",
     10, "Olympiad", "Science-Physics", "Electricity", "Electromagnetic Induction",
     "The image shows an electrical transformer. A step-up transformer has 200 turns in the primary and 2000 turns in the secondary. If input voltage is 240V, the output voltage is:",
     ["2400 V","24 V","240 V","200 V"], 0,
     "Transformer equation: Vs/Vp = Ns/Np. Vs = 240 x (2000/200) = 240 x 10 = 2400 V."),

    # Grade 11
    ("G11 Phys projectile motion",
     "projectile motion trajectory physics parabola",
     11, "Olympiad", "Science-Physics", "Mechanics", "Projectile Motion",
     "The image shows a projectile's parabolic path. A ball is thrown horizontally at 20 m/s from a 80 m high cliff. How long does it take to reach the ground? (g=10 m/s2)",
     ["4 seconds","8 seconds","2 seconds","16 seconds"], 0,
     "Vertical: h = 1/2 g t^2 -> 80 = 5t^2 -> t^2=16 -> t=4 s. Horizontal velocity does NOT affect time of fall."),

    ("G11 Phys electric field",
     "electric field lines charge physics electrostatics",
     11, "Olympiad", "Science-Physics", "Electrostatics", "Electric Fields",
     "The image shows electric field lines around charges. Field lines point AWAY from a positive charge. What does the DENSITY of field lines represent?",
     ["The strength (magnitude) of the electric field","The charge of the nearest particle","The direction of force on negative charges","The electric potential"], 0,
     "Denser field lines = stronger electric field. Where lines are closer together, the field is more intense. Lines point in the direction of force on a positive test charge."),

    ("G11 Phys simple harmonic motion",
     "pendulum oscillation simple harmonic motion physics",
     11, "Advanced", "Science-Physics", "Waves & Oscillations", "Simple Harmonic Motion",
     "The image shows a pendulum. The time period of a simple pendulum depends on:",
     ["Length of the pendulum and g (gravitational acceleration) only","Mass of the bob","Amplitude of oscillation","Material of the string"], 0,
     "T = 2pi x sqrt(L/g). The period depends only on length (L) and g. Mass, material, and amplitude (for small angles) do NOT affect the period."),

    ("G11 Phys capacitor",
     "capacitor electronics circuit physics charge",
     11, "Olympiad", "Science-Physics", "Electricity", "Capacitance",
     "The image shows a capacitor in a circuit. A capacitor stores energy in the form of:",
     ["Electric field between its plates","Magnetic field around conductors","Chemical energy in electrolyte","Heat in the dielectric"], 0,
     "A capacitor stores energy as an electric field between oppositely charged plates. E = 1/2 CV^2. Inductors store energy in magnetic fields; batteries store chemical energy."),

    ("G11 Phys nuclear fission",
     "nuclear fission reactor atom splitting energy",
     11, "Olympiad", "Science-Physics", "Nuclear Physics", "Fission & Fusion",
     "The image shows nuclear fission. In a nuclear reactor, fission of U-235 releases energy because:",
     ["Products have slightly less mass than reactants; the mass difference converts to energy (E=mc2)","Protons gain kinetic energy from neutrons","Chemical bonds in uranium break releasing heat","Electrons are split from the nucleus"], 0,
     "Einstein's E=mc2: in fission, the total mass of products is slightly less than reactants (mass defect). This small mass difference converts to enormous energy (binding energy released)."),
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
    print("=" * 60)
    print("  OlympiadReady - Science Pixabay Images")
    print(f"  Total questions: {len(BIO_QUESTIONS)+len(CHEM_QUESTIONS)+len(PHYS_QUESTIONS)}")
    print("=" * 60)

    run_batch("Science-Biology (Grades 9-11)", BIO_QUESTIONS)
    run_batch("Science-Chemistry (Grades 9-11)", CHEM_QUESTIONS)
    run_batch("Science-Physics (Grades 9-11)", PHYS_QUESTIONS)

    print(f"\n{'='*60}")
    print(f"DONE - Posted: {posted}  Skipped(dup): {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
    print(f"{'='*60}")
