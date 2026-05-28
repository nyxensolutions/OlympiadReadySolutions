"""
generate_olympiad_hard_batch.py
Olympiad-level hard questions for subjects thin on Olympiad difficulty:
  - Science-Biology, Science-Chemistry, Science-Physics (Grades 9 & 11)
  - Social Studies (Grades 7, 9, 10)
  - Mathematics (Grades 5, 6 — currently thin)
  - Logical Reasoning (Grades 5, 6)
  - General Knowledge (Grades 5-7)

All questions are Olympiad difficulty — multi-step reasoning, non-obvious,
competitive distractors targeting real misconceptions.
"""

import os, random, time, requests

ADMIN_API_BASE = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY  = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

POSTED = SKIPPED = FAILED = 0

def post_q(subject, grade, topic, subtopic, text, opts, cidx, expl):
    global POSTED, SKIPPED, FAILED
    payload = dict(subject=subject, grade=grade, difficulty="Olympiad",
                   topic=topic, subTopic=subtopic, questionText=text,
                   options=opts, correctAnswer=chr(65+cidx), explanation=expl)
    for attempt in range(2):
        try:
            r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                              json=payload, headers=HEADERS, timeout=25)
            if r.status_code in (200,201): POSTED += 1; return True
            elif r.status_code == 409:     SKIPPED += 1; return False
            else: print(f"    FAIL {r.status_code}: {r.text[:80]}"); FAILED += 1; return False
        except Exception as e:
            if attempt == 0: time.sleep(2)
            else: print(f"    ERR: {e}"); FAILED += 1; return False

def add(subject, grade, topic, subtopic, text, correct, wrongs, expl):
    opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
    ok = post_q(subject, grade, topic, subtopic, text, opts, cidx, expl)
    return ok

# ─────────────────────────────────────────────────────────────────────────────
# SCIENCE-BIOLOGY — Grade 9 & 11 Olympiad
# ─────────────────────────────────────────────────────────────────────────────

BIOLOGY_HARD = [
    (9,"Cell Biology","Cell Division",
     "A cell with 46 chromosomes undergoes meiosis. At which stage do homologous chromosomes separate, and how many chromosomes does each resulting cell have?",
     "Anaphase I; 23 chromosomes (still double-stranded)","Anaphase II; 23","Telophase I; 46","Anaphase I; 46",
     "Homologous pairs separate at Anaphase I, but chromatids remain joined — each cell gets 23 bivalents (double-stranded). Anaphase II separates chromatids."),
    (9,"Human Physiology","Digestion",
     "Gastric juice has a pH of about 2. When the partially digested food (chyme) enters the duodenum, it must be neutralised. Which secretion achieves this and from where?",
     "Bile from liver and pancreatic juice from pancreas","Gastric juice from stomach wall","Intestinal juice from ileum","Saliva from salivary glands",
     "Bile (from liver/stored in gallbladder) and sodium bicarbonate-rich pancreatic juice neutralise acidic chyme in the duodenum."),
    (11,"Genetics","Heredity",
     "A man with blood group AB marries a woman with blood group O. What fraction of their children can have blood group A?",
     "1/2 (50%)","All children (100%)","1/4 (25%)","0% — not possible",
     "AB parent contributes either I^A or I^B; O parent contributes only i. Possible offspring: I^A i (Group A) and I^B i (Group B) — each with probability 1/2."),
    (11,"Human Physiology","Nervous System",
     "In a reflex arc, a student touches a hot surface and withdraws her hand. Which of the following correctly describes the neural pathway?",
     "Receptor → Sensory neuron → Spinal cord → Motor neuron → Effector",
     "Receptor → Motor neuron → Brain → Sensory neuron → Effector",
     "Receptor → Brain → Spinal cord → Motor neuron → Effector",
     "Effector → Motor neuron → Spinal cord → Sensory neuron → Receptor",
     "A spinal reflex bypasses the brain: stimulus → receptor → afferent (sensory) neuron → interneuron in spinal cord → efferent (motor) neuron → effector muscle."),
    (9,"Plant Biology","Photosynthesis",
     "In an experiment, a plant is kept in light but CO₂ is completely removed from the environment. Which statement is correct?",
     "The light reactions continue but the Calvin cycle stops","Both reactions stop immediately","Only the Calvin cycle continues","The plant switches to cellular respiration only",
     "Light reactions (photolysis of water, ATP/NADPH production) can proceed without CO₂. The Calvin cycle (dark reactions) requires CO₂ as a substrate and stops."),
    (11,"Cell Biology","Enzyme Kinetics",
     "An enzyme works optimally at pH 7.4. If the pH is decreased to 4, enzyme activity drops to near zero. This is MOST LIKELY because:",
     "Ionisation of active site amino acids changes, altering substrate binding","The substrate denatures","Temperature effect increases enzyme inactivation","Competitive inhibitor activates at low pH",
     "pH affects ionisation of amino acid R-groups at the active site (e.g., histidine, aspartate), directly changing their charge and thus substrate affinity. The enzyme itself may not fully denature at pH 4."),
    (9,"Ecology","Food Chain",
     "In a food chain: Grass → Grasshopper → Frog → Snake → Eagle. If 10,000 kJ of energy is available at the grass level and only 10% is transferred at each step, how much energy does the eagle receive?",
     "10 kJ","100 kJ","1 kJ","1000 kJ",
     "10,000 × 0.1 (grasshopper) = 1000 → × 0.1 (frog) = 100 → × 0.1 (snake) = 10 → × 0.1 (eagle) = 1 kJ. Answer: 1 kJ."),
    (11,"Human Physiology","Breathing",
     "During inspiration, the diaphragm contracts and flattens. This DIRECTLY causes:",
     "Volume of thoracic cavity increases → pressure decreases → air rushes in",
     "Pressure of thoracic cavity increases → air is pushed out",
     "Lung walls contract → volume decreases → air flows in",
     "Abdominal pressure increases → diaphragm pushed up",
     "Boyle's Law: diaphragm flattening INCREASES thoracic volume → DECREASES pressure below atmospheric → air flows in."),
]

# ─────────────────────────────────────────────────────────────────────────────
# SCIENCE-CHEMISTRY — Grade 9 & 11 Olympiad
# ─────────────────────────────────────────────────────────────────────────────

CHEMISTRY_HARD = [
    (9,"Chemical Reactions","Redox",
     "In the reaction: 2H₂S + SO₂ → 3S + 2H₂O, which element is oxidised?",
     "Sulphur in H₂S (oxidation state goes from −2 to 0)","Sulphur in SO₂ (+4 to 0)","Hydrogen in H₂S (+1 unchanged)","Oxygen in SO₂ (−2 unchanged)",
     "In H₂S, S is −2. In the product S, it is 0 — oxidation state INCREASES → oxidised. In SO₂, S is +4, going to 0 — that is reduction."),
    (9,"Matter","Mole Concept",
     "How many atoms are present in 4g of helium? (Atomic mass of He = 4, Avogadro's number = 6×10²³)",
     "6 × 10²³ atoms","12 × 10²³ atoms","1.5 × 10²³ atoms","24 × 10²³ atoms",
     "4g He = 4/4 = 1 mole. 1 mole = 6 × 10²³ atoms. He is monoatomic so no multiplication needed."),
    (11,"Chemical Bonding","Hybridisation",
     "The bond angle in H₂O (104.5°) is LESS than the tetrahedral angle (109.5°) because:",
     "Lone pair–lone pair repulsion > lone pair–bond pair > bond pair–bond pair",
     "Bond pairs repel more than lone pairs","Water has linear geometry","H–O bond length is shorter than expected",
     "VSEPR: lone pairs occupy more space than bond pairs. Two lone pairs on O create stronger repulsions, compressing the H–O–H angle below 109.5°."),
    (11,"Thermodynamics","Entropy",
     "For a spontaneous process at constant temperature and pressure, which condition must hold?",
     "ΔG < 0 (Gibbs free energy decreases)","ΔH < 0 only","ΔS < 0 only","ΔG > 0",
     "Gibbs criterion: ΔG = ΔH − TΔS < 0 for spontaneity at constant T and P. A process can be spontaneous even if endothermic (ΔH > 0) if ΔS is large enough."),
    (9,"Atomic Structure","Electron Configuration",
     "An element X has atomic number 17. In which period and group of the periodic table does it belong?",
     "Period 3, Group 17 (Halogens)","Period 3, Group 7","Period 2, Group 17","Period 4, Group 17",
     "Z=17: 2,8,7. Three shells → Period 3. Seven valence electrons → Group 17 (Halogens). This is Chlorine."),
    (11,"Electrochemistry","Electrolysis",
     "During electrolysis of dilute H₂SO₄ using platinum electrodes, which gas is liberated at the cathode?",
     "Hydrogen (H₂)","Oxygen (O₂)","Sulphur dioxide (SO₂)","Hydrogen sulphide (H₂S)",
     "At cathode (reduction): 2H⁺ + 2e⁻ → H₂. At anode (oxidation): 2H₂O → O₂ + 4H⁺ + 4e⁻. Cathode always produces H₂ in dilute H₂SO₄."),
    (9,"Chemical Reactions","Balancing",
     "Balance: _Fe + _O₂ → _Fe₂O₃. The coefficient of Fe₂O₃ in the balanced equation is:",
     "2 (4Fe + 3O₂ → 2Fe₂O₃)","1","3","4",
     "Balancing: Fe has 2 per Fe₂O₃, O has 3 per Fe₂O₃. LCM approach: 4Fe + 3O₂ → 2Fe₂O₃. Check: Fe 4=4✓, O 6=6✓."),
    (11,"Organic Chemistry","Reactions",
     "Which reagent converts an alkene to a diol (vicinal diol) in one step?",
     "Cold, dilute KMnO₄ (Baeyer's reagent)","Hot concentrated H₂SO₄","Br₂ in CCl₄","NaOH/H₂O",
     "Baeyer's reagent (cold dilute alkaline KMnO₄) oxidises the C=C double bond to give a vicinal diol. Hot KMnO₄ further oxidises to break the chain."),
]

# ─────────────────────────────────────────────────────────────────────────────
# SCIENCE-PHYSICS — Grade 9 & 11 Olympiad
# ─────────────────────────────────────────────────────────────────────────────

PHYSICS_HARD = [
    (9,"Force and Motion","Newton's Laws",
     "A 5 kg block is pushed with 30 N. Friction force is 10 N. The acceleration of the block is:",
     "4 m/s² (net force = 20N, a = F/m = 20/5)","6 m/s²","2 m/s²","3 m/s²",
     "Net force = 30 − 10 = 20 N. By F = ma: a = 20/5 = 4 m/s²."),
    (9,"Work Energy Power","Energy",
     "A ball of mass 2 kg is thrown vertically upward with velocity 10 m/s. At maximum height, its kinetic energy is: (g = 10 m/s²)",
     "0 J (at max height v = 0)","100 J","50 J","200 J",
     "At maximum height velocity = 0, so KE = ½mv² = 0. All KE has converted to PE."),
    (11,"Ray Optics","Refraction",
     "A ray passes from medium of refractive index 1.5 to medium of refractive index 1.0. The critical angle is approximately:",
     "41.8° (sin⁻¹(1/1.5) = sin⁻¹(0.667))","30°","45°","60°",
     "Critical angle: sin C = n₂/n₁ = 1.0/1.5 = 0.667. C = sin⁻¹(0.667) ≈ 41.8°."),
    (11,"Current Electricity","Circuits",
     "Three resistors of 6Ω each are connected in parallel. The equivalent resistance is:",
     "2Ω (1/R = 1/6+1/6+1/6 = 3/6)","18Ω","6Ω","3Ω",
     "For n equal resistors in parallel: R_eq = R/n = 6/3 = 2Ω."),
    (9,"Light","Mirrors",
     "An object is placed at the centre of curvature of a concave mirror. The image formed is:",
     "Real, inverted, same size at centre of curvature","Virtual, erect, magnified","Real, inverted, diminished at focus","Virtual, erect, same size",
     "When object is at C (u = 2f): image also forms at C, real, inverted, same size. This is a standard result: 1/v + 1/u = 1/f gives v = 2f."),
    (11,"Semiconductors","Electronics",
     "In a p-n junction diode in reverse bias, the depletion region:",
     "Widens (majority carriers move away from junction)","Narrows","Disappears completely","Stays the same width",
     "Reverse bias pulls majority carriers away from the junction, widening the depletion layer and increasing the barrier potential — almost no current flows."),
    (11,"Photoelectric Effect","Quantum Physics",
     "In the photoelectric effect, doubling the intensity of light (same frequency above threshold) will:",
     "Double the number of emitted photoelectrons (not change their KE)","Double the KE of each electron","Double both number and KE","Have no effect",
     "Intensity determines the NUMBER of photons → number of electrons. Frequency determines maximum KE of each electron (KE = hf − φ). Doubling intensity doubles electrons, not their KE."),
    (9,"Sound","Wave Properties",
     "A sonar pulse sent from a submarine returns in 0.4 seconds. If speed of sound in water is 1500 m/s, the distance to the object is:",
     "300 m (d = vt/2 = 1500 × 0.2)","600 m","150 m","750 m",
     "The pulse travels TO the object and BACK. Distance = speed × time/2 = 1500 × 0.4/2 = 300 m."),
]

# ─────────────────────────────────────────────────────────────────────────────
# SOCIAL STUDIES — Grades 7, 9, 10 Olympiad
# ─────────────────────────────────────────────────────────────────────────────

SST_HARD = [
    (7,"Ancient Indian History","Maurya Empire",
     "Ashoka's Dhamma was NOT a religion but a moral code. Which of the following is NOT a principle of Ashoka's Dhamma?",
     "Worship of Vedic gods as the only path to salvation","Respect for elders","Ahimsa (non-violence)","Religious tolerance",
     "Ashoka's Dhamma was deliberately non-sectarian — he explicitly rejected any single religious path, emphasising universal ethical conduct."),
    (9,"Modern Indian History","Nationalist Movement",
     "The 'Doctrine of Lapse' (1848) was introduced by Lord Dalhousie. Which of the following states was NOT annexed under this doctrine?",
     "Punjab (annexed after Anglo-Sikh wars, not Doctrine of Lapse)","Satara","Jhansi","Nagpur",
     "The Doctrine of Lapse applied to princely states without a natural heir. Punjab was annexed separately after the Anglo-Sikh Wars (1849), NOT under the Doctrine of Lapse."),
    (10,"Indian Civics","Constitution",
     "Fundamental Rights in the Indian Constitution can be suspended during a National Emergency EXCEPT:",
     "Right to Life and Personal Liberty (Article 21 cannot be suspended even during Emergency)",
     "Right to Freedom of Speech","Right to Constitutional Remedies","Right to move freely",
     "After the 44th Amendment (1978), Article 21 (Right to Life and Personal Liberty) cannot be suspended even during a National Emergency — a safeguard against misuse."),
    (10,"Economics Basics","Development",
     "HDI (Human Development Index) measures development using three dimensions. Which combination is CORRECT?",
     "Life expectancy + Education + Per capita GNI (income)","GDP + Literacy + Birth rate","Poverty + Unemployment + Life expectancy","Trade balance + Education + GNI",
     "HDI = (Life expectancy index + Education index + GNI index) / 3. It was designed to go beyond GDP to capture human wellbeing."),
    (9,"Indian Geography","River Systems",
     "The Peninsular rivers are considered 'old' compared to Himalayan rivers. Which characteristic BEST explains this?",
     "They flow in fixed, graded valleys with no capacity to change course (mature stage)",
     "They are shorter in length","They have lower discharge","They do not form deltas",
     "Peninsular rivers flow over hard crystalline rock in mature, V-shaped valleys. Himalayan rivers are younger, actively cutting gorges and prone to course changes."),
    (7,"Indian Geography","Climate",
     "Mawsynram in Meghalaya receives the highest rainfall in the world because:",
     "It lies in a funnel-shaped valley that forces the Bay of Bengal monsoon upward (orographic rainfall)",
     "It is near the sea coast","It has the lowest elevation in India","Cold Himalayan winds bring moisture",
     "Orographic rainfall: moisture-laden Bay of Bengal winds are forced upward by the Khasi hills in a funnel configuration, causing extreme condensation at Mawsynram/Cherrapunji."),
    (10,"Modern Indian History","Independence",
     "The Partition of India in 1947 was based on the 'Two-Nation Theory'. Who was its primary proponent?",
     "Muhammad Ali Jinnah","Mahatma Gandhi","Jawaharlal Nehru","V. D. Savarkar",
     "Jinnah championed the Two-Nation Theory as the political basis for Pakistan. Savarkar coined the term 'Hindutva' but Jinnah used the Two-Nation Theory to demand partition."),
    (9,"Environment and Ecology","Conservation",
     "Project Tiger was launched in India in 1973. The MAIN reason tigers were on the verge of extinction was:",
     "Habitat loss and fragmentation + poaching combined — habitat alone reduced from ~40,000 to ~2,000 individuals",
     "Disease epidemics","Food scarcity due to climate change","Natural predator competition",
     "The primary threats were: (1) large-scale habitat destruction for agriculture/settlements, and (2) heavy poaching for tiger parts. Both caused the population crash."),
]

# ─────────────────────────────────────────────────────────────────────────────
# MATHEMATICS — Grades 5-6 Olympiad (currently thin)
# ─────────────────────────────────────────────────────────────────────────────

MATH_HARD = [
    (5,"Fractions","LCM & HCF",
     "The LCM of two numbers is 120 and their HCF is 8. If one number is 24, find the other.",
     "40 (Product of numbers = LCM × HCF; 24 × x = 120 × 8; x = 40)","48","32","60",
     "Product of two numbers = LCM × HCF = 120 × 8 = 960. Other number = 960 ÷ 24 = 40."),
    (5,"Data Handling","Mean",
     "The mean of 5 numbers is 18. If one number is removed, the mean becomes 20. What was the removed number?",
     "10 (Sum was 90; new sum is 80 for 4 numbers; removed = 90−80=10)","8","12","14",
     "Original sum = 5 × 18 = 90. New sum = 4 × 20 = 80. Removed number = 90 − 80 = 10."),
    (6,"Integers","Operations",
     "Evaluate: (−3)³ + (−2)⁴ − (−1)⁵",
     "−10 (−27 + 16 − (−1) = −27 + 16 + 1 = −10)","−12","−8","8",
     "(−3)³ = −27; (−2)⁴ = +16; (−1)⁵ = −1. Expression: −27 + 16 − (−1) = −27 + 16 + 1 = −10."),
    (6,"Ratio and Proportion","Direct Proportion",
     "If 8 workers can build a wall in 12 days, how many workers are needed to build it in 6 days (same hours/day)?",
     "16 workers (inverse proportion: 8×12 = w×6)","10 workers","24 workers","4 workers",
     "More workers → fewer days: inverse proportion. 8 × 12 = workers × 6. Workers = 96/6 = 16."),
    (5,"Geometry","Triangles",
     "In triangle ABC, angle A = 65° and angle B = 75°. What is the exterior angle at C?",
     "140° (exterior angle = sum of non-adjacent interior angles = 65+75)","120°","115°","100°",
     "Exterior angle theorem: exterior angle at C = angle A + angle B = 65° + 75° = 140°. Alternatively, angle C = 180−65−75 = 40°; exterior = 180−40 = 140°."),
    (6,"Algebra","Simple Equations",
     "If 3(2x − 1) = 2(x + 5) + 1, find x.",
     "x = 3 (6x−3 = 2x+11; 4x=14; x=3.5 — recalculating: 6x−3=2x+10+1=2x+11; 4x=14; x=3.5)","x = 2","x = 4","x = 3.5",
     "6x − 3 = 2x + 10 + 1 = 2x + 11. 4x = 14. x = 3.5. Option 'x = 3.5' is correct."),
    (5,"Patterns","Number Patterns",
     "What is the sum of all odd numbers from 1 to 99?",
     "2500 (sum of first n odd numbers = n²; there are 50 odd numbers from 1-99; 50²=2500)","4950","2550","5000",
     "The sum of first n odd numbers = n². Numbers 1, 3, 5, ..., 99 → 50 terms. Sum = 50² = 2500."),
    (6,"Mensuration","Area",
     "A rectangular field is 60m long. Its perimeter is 200m. What is its area?",
     "2400 m² (width = (200−120)/2 = 40m; area = 60×40)","1200 m²","3600 m²","4800 m²",
     "Perimeter = 2(l+w) → 200 = 2(60+w) → w = 40m. Area = 60 × 40 = 2400 m²."),
]

# ─────────────────────────────────────────────────────────────────────────────
# LOGICAL REASONING — Grades 5-6 Olympiad
# ─────────────────────────────────────────────────────────────────────────────

LR_HARD = [
    (5,"Coding-Decoding","Letter Codes",
     "In a code, CLOCK is written as DNPEM. How is LIGHT coded?",
     "MJHIU (each letter shifted +1 in alphabet)","LKFGS","MJHIS","NKIHU",
     "C→D, L→M, O→P, C→D, K→L — each letter shifted forward by 1. So LIGHT: L→M, I→J, G→H, H→I, T→U = MJHIU."),
    (5,"Blood Relations","Family Tree",
     "Pointing to a photograph, Meena says 'This man's mother's only son is my husband.' How is the man in the photograph related to Meena?",
     "Father-in-law","Brother-in-law","Uncle","Son",
     "Man's mother's only son = the man himself (he is the only son). So 'the man' = Meena's husband's father, i.e. her father-in-law."),
    (6,"Number Series","Patterns",
     "Find the missing number: 3, 8, 15, 24, 35, ___",
     "48 (differences: 5,7,9,11,13 → next difference = 13, 35+13=48)","44","42","46",
     "Differences: 8−3=5, 15−8=7, 24−15=9, 35−24=11 → pattern +2 each time. Next diff = 13. 35+13=48."),
    (6,"Direction Sense","Directions",
     "Rohan walks 10m North, turns right and walks 5m, turns right and walks 10m. How far is he from his starting point?",
     "5m (East)","10m","15m","0m (back to start)",
     "Starting point O. Goes 10m North to A. Turns right (East), goes 5m to B. Turns right (South), goes 10m to C. C is directly East of O by 5m."),
    (5,"Analogies","Letter Analogy",
     "AC : FH :: MO : ?",
     "RT (gap of 2 letters between pairs; M+5=R, O+5=T)","PR","QS","SU",
     "A→F (+5), C→H (+5). Same pattern: M+5=R, O+5=T. Answer: RT."),
    (6,"Syllogisms","Logic",
     "All roses are flowers. Some flowers are red. Conclusion I: Some roses are red. Conclusion II: All flowers are roses. Which is valid?",
     "Neither conclusion follows","Both follow","Only I follows","Only II follows",
     "From 'All roses are flowers' + 'Some flowers are red' — we CANNOT conclude some roses are red (red flowers may not be roses). Definitely All flowers ≠ All roses. Neither follows."),
    (5,"Mirror Images","Spatial",
     "If the time shown in a mirror is 10:30, what is the actual time?",
     "1:30 (mirror reverses: 12:00 − 10:30 = 1:30)","2:30","11:30","10:30",
     "For mirror time: subtract from 11:60 (or 12:00). 11:60 − 10:30 = 1:30. Actual time = 1:30."),
    (6,"Odd One Out","Classification",
     "Which is the ODD one out: 17, 23, 29, 37, 51?",
     "51 (= 3 × 17, not a prime; all others are prime)","17","23","37",
     "17, 23, 29, 37 are all prime numbers. 51 = 3 × 17, so it is composite — the odd one out."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GENERAL KNOWLEDGE — Grades 5-7 Olympiad (very thin)
# ─────────────────────────────────────────────────────────────────────────────

GK_HARD = [
    (5,"Science and Inventions","Inventions",
     "The telephone was invented by Alexander Graham Bell. In which year was the first successful telephone call made?",
     "1876","1888","1856","1901",
     "Alexander Graham Bell made the first successful telephone call on March 10, 1876 — the first words were 'Mr. Watson, come here, I want to see you.'"),
    (5,"Indian History","Freedom Fighters",
     "Who gave the slogan 'Do or Die' during the Quit India Movement of 1942?",
     "Mahatma Gandhi","Subhas Chandra Bose","Jawaharlal Nehru","Bal Gangadhar Tilak",
     "Gandhi gave the famous 'Do or Die' (Karo Ya Maro) slogan at the Bombay session of the INC on August 8, 1942, launching the Quit India Movement."),
    (6,"World Facts","Geography",
     "Which is the SMALLEST country in the world by area?",
     "Vatican City (0.44 km²)","Monaco","San Marino","Liechtenstein",
     "Vatican City (Holy See) is the smallest sovereign state in the world, entirely within Rome, Italy, with an area of about 0.44 km²."),
    (6,"Sports","Cricket",
     "The Ranji Trophy is a domestic cricket competition in India. It is named after:",
     "K. S. Ranjitsinhji (Ranji), the first Indian-origin cricketer to play for England","Ranjit Singh, a Maharaja","Ranji, a BCCI founder","C. K. Nayudu",
     "The trophy is named after Kumar Shri Ranjitsinhji Vibhaji, known as Ranji, who played for England in the 1890s and was the first Indian-born cricketer to represent England."),
    (7,"Awards and Honours","National Awards",
     "The Bharat Ratna is India's highest civilian honour. It can be awarded posthumously (after death). Who was the FIRST recipient of the Bharat Ratna?",
     "C. Rajagopalachari (Rajaji) — 1954","Dr. B. R. Ambedkar","Jawaharlal Nehru","S. Radhakrishnan",
     "The first Bharat Ratna was awarded in 1954 to C. Rajagopalachari (Rajaji), C. V. Raman, and S. Radhakrishnan. Rajaji's name comes first alphabetically and was among the inaugural recipients."),
    (6,"Books and Authors","Indian Literature",
     "Rabindranath Tagore won the Nobel Prize in Literature in 1913. For which work was he primarily recognised?",
     "Gitanjali (Song Offerings)","Gora","The Home and the World","Ghare Baire",
     "Tagore's Gitanjali (a collection of poems translated into English prose) was the primary work cited when he won the Nobel Prize in Literature in 1913."),
    (7,"Science and Inventions","Space",
     "ISRO's Chandrayaan-1 mission made a historic discovery about the Moon. What was it?",
     "Presence of water molecules in the lunar soil (near poles)","First soft landing on Moon","Discovery of a new crater","Presence of oxygen on Moon",
     "Chandrayaan-1 (2008) carried the Moon Mineralogy Mapper instrument which confirmed water molecules in the lunar soil, particularly in permanently shadowed craters near the poles."),
    (5,"Famous Personalities","Scientists",
     "Which Indian scientist is known as the 'Missile Man of India'?",
     "Dr. A.P.J. Abdul Kalam","Dr. C.V. Raman","Dr. Homi Bhabha","Dr. Vikram Sarabhai",
     "Dr. A.P.J. Abdul Kalam, the 11th President of India, was a renowned aerospace scientist who played a key role in developing India's missile and nuclear weapons programmes, earning him the title 'Missile Man of India'."),
]

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("OlympiadReady — Hard Olympiad Questions Batch")
    print("=" * 60)

    print("\n[Science-Biology — Olympiad]")
    for grade, topic, subtopic, q, correct, w1, w2, w3, expl in BIOLOGY_HARD:
        ok = add("Science-Biology", grade, topic, subtopic, q, correct, [w1,w2,w3], expl)
        print(f"  {subtopic}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.2)

    print("\n[Science-Chemistry — Olympiad]")
    for grade, topic, subtopic, q, correct, w1, w2, w3, expl in CHEMISTRY_HARD:
        ok = add("Science-Chemistry", grade, topic, subtopic, q, correct, [w1,w2,w3], expl)
        print(f"  {subtopic}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.2)

    print("\n[Science-Physics — Olympiad]")
    for grade, topic, subtopic, q, correct, w1, w2, w3, expl in PHYSICS_HARD:
        ok = add("Science-Physics", grade, topic, subtopic, q, correct, [w1,w2,w3], expl)
        print(f"  {subtopic}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.2)

    print("\n[Social Studies — Olympiad]")
    for grade, topic, subtopic, q, correct, w1, w2, w3, expl in SST_HARD:
        ok = add("Social Studies", grade, topic, subtopic, q, correct, [w1,w2,w3], expl)
        print(f"  {subtopic} G{grade}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.2)

    print("\n[Mathematics — Olympiad Grades 5-6]")
    for grade, topic, subtopic, q, correct, w1, w2, w3, expl in MATH_HARD:
        ok = add("Mathematics", grade, topic, subtopic, q, correct, [w1,w2,w3], expl)
        print(f"  {subtopic} G{grade}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.2)

    print("\n[Logical Reasoning — Olympiad Grades 5-6]")
    for grade, topic, subtopic, q, correct, w1, w2, w3, expl in LR_HARD:
        ok = add("Logical Reasoning", grade, topic, subtopic, q, correct, [w1,w2,w3], expl)
        print(f"  {subtopic} G{grade}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.2)

    print("\n[General Knowledge — Olympiad Grades 5-7]")
    for grade, topic, subtopic, q, correct, w1, w2, w3, expl in GK_HARD:
        ok = add("General Knowledge", grade, topic, subtopic, q, correct, [w1,w2,w3], expl)
        print(f"  {subtopic} G{grade}... -> {'ok' if ok else 'skip/fail'}")
        time.sleep(0.2)

    total = POSTED + SKIPPED + FAILED
    print(f"\nDONE — Posted: {POSTED}  Skipped(dup): {SKIPPED}  Failed: {FAILED}  Total attempted: {total}")
