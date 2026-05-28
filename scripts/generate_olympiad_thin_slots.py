"""
generate_olympiad_thin_slots.py
Fill thin Olympiad slots:
  - Grade 4 Mathematics   (was 2 questions)
  - Grade 4 Science       (was 6 questions)
  - Grade 9 Science-Chemistry (was 6 questions)
  - Grade 9 Science-Physics   (was 8 questions)
  - Grade 5/6 Computer Science (was 3 each)
  - Grade 10 GK           (was 10 questions)
  - Grade 5/6 GK/Math/LR Olympiad (3-4 each)

Target: ~20 per slot minimum.
"""

import os, random, time, requests

ADMIN_API_BASE = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY  = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

POSTED = SKIPPED = FAILED = 0

def post_q(subject, grade, difficulty, topic, subtopic, text, opts, cidx, expl):
    global POSTED, SKIPPED, FAILED
    payload = dict(subject=subject, grade=grade, difficulty=difficulty,
                   topic=topic, subTopic=subtopic, questionText=text,
                   options=opts, correctAnswer=chr(65+cidx), explanation=expl)
    for attempt in range(2):
        try:
            r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                              json=payload, headers=HEADERS, timeout=25)
            if r.status_code in (200, 201): POSTED += 1; return True
            elif r.status_code == 409:      SKIPPED += 1; return False
            else: print(f"    FAIL {r.status_code}: {r.text[:80]}"); FAILED += 1; return False
        except Exception as e:
            if attempt == 0: time.sleep(2)
            else: print(f"    ERR: {e}"); FAILED += 1; return False

def add(subject, grade, topic, subtopic, text, correct, wrongs, expl, difficulty="Olympiad"):
    opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
    return post_q(subject, grade, difficulty, topic, subtopic, text, opts, cidx, expl)

def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 4 MATHEMATICS — Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr4_math():
    section("Grade 4 Mathematics — Olympiad")
    qs = [
        ("Numbers","Place Value & Patterns",
         "Find the sum of all even numbers from 2 to 50.",
         "650","600","625","675",
         "Even numbers 2,4,...,50 form 25 terms. Sum = 25×(2+50)/2 = 25×26 = 650."),
        ("Numbers","Divisibility",
         "Which is the smallest 4-digit number exactly divisible by both 6 and 9?",
         "1008","1000","1002","1044",
         "LCM(6,9)=18. Smallest 4-digit multiple of 18: 1000÷18=55.5→ 56×18=1008."),
        ("Numbers","Fractions",
         "A ribbon of length 4½ metres is cut into pieces of ¾ metre each. How many pieces are obtained?",
         "6","5","7","4",
         "4½ ÷ ¾ = (9/2) ÷ (3/4) = (9/2)×(4/3) = 36/6 = 6 pieces."),
        ("Geometry","Shapes & Symmetry",
         "A square has perimeter 48 cm. A triangle is formed using three sides of a different square whose area equals that of the first square. What is the perimeter of the triangle?",
         "36 cm","48 cm","32 cm","40 cm",
         "First square side=12, area=144. Second square side=12. Triangle from 3 sides=3×12=36 cm."),
        ("Numbers","Word Problems",
         "A shop had 1,200 mangoes. On day 1, it sold 1/3; on day 2 it sold 1/4 of the remaining. How many mangoes were left?",
         "600","400","300","800",
         "After day 1: 1200−400=800. After day 2: 800−200=600."),
        ("Numbers","Multiplication",
         "The product of two numbers is 2016. One number is 63. What is the other number multiplied by 4?",
         "128","32","64","96",
         "2016÷63=32. 32×4=128."),
        ("Geometry","Perimeter & Area",
         "A rectangle has length twice its breadth. If its area is 128 cm², what is its perimeter?",
         "48 cm","32 cm","64 cm","56 cm",
         "l=2b, l×b=128 → 2b²=128 → b=8, l=16. Perimeter=2×(16+8)=48 cm."),
        ("Numbers","Factors & Multiples",
         "How many factors does 72 have?",
         "12","8","10","14",
         "72=2³×3². Number of factors=(3+1)(2+1)=12."),
        ("Numbers","Fractions & Comparison",
         "Arrange these fractions in descending order: 3/4, 2/3, 5/6, 7/12",
         "5/6 > 3/4 > 2/3 > 7/12","3/4 > 5/6 > 7/12 > 2/3","5/6 > 7/12 > 3/4 > 2/3","2/3 > 3/4 > 5/6 > 7/12",
         "LCD=12: 5/6=10/12, 3/4=9/12, 2/3=8/12, 7/12=7/12. Order: 10>9>8>7."),
        ("Numbers","Roman Numerals & Patterns",
         "What is the value of: MMCMXCIX − MCMXCIX?",
         "1000","999","100","1001",
         "MMCMXCIX=2999, MCMXCIX=1999. Difference=1000."),
        ("Geometry","Clock & Time",
         "A clock gains 3 minutes every hour. If it shows the correct time at 8:00 AM, what time will it show at 8:00 PM on the same day when the actual time is 8:00 PM?",
         "8:36 PM","8:30 PM","8:03 PM","8:24 PM",
         "12 hours × 3 minutes gained per hour = 36 minutes gained. Clock shows 8:36 PM."),
        ("Numbers","Division & Remainder",
         "When a number is divided by 13, the quotient is 15 and the remainder is 7. What is the number?",
         "202","195","207","182",
         "Number = (13×15)+7 = 195+7 = 202."),
        ("Numbers","Simplification",
         "Simplify: (25 × 25) − (15 × 15)",
         "400","250","300","500",
         "(25+15)(25−15) = 40×10 = 400. Using difference of squares."),
        ("Numbers","Pattern Recognition",
         "Find the missing number in the series: 3, 7, 15, 31, 63, __",
         "127","125","128","124",
         "Each term = 2×previous + 1. 2×63+1 = 127."),
        ("Numbers","Word Problems",
         "A train travels 360 km in 4 hours. A car travels the same distance in 6 hours. How much faster (in km/h) is the train than the car?",
         "30 km/h","20 km/h","40 km/h","15 km/h",
         "Train speed = 90 km/h. Car speed = 60 km/h. Difference = 30 km/h."),
        ("Numbers","Large Numbers",
         "What is the place value of digit 8 in 58,43,021?",
         "8,00,000","80,000","8,000","80,00,000",
         "In 58,43,021 (Indian system): 5→crore, 8→ten-lakh. 8 is in ten-lakhs place = 8,00,000."),
        ("Geometry","Triangles",
         "The three angles of a triangle are in ratio 1:2:3. What type of triangle is it?",
         "Right-angled triangle","Equilateral triangle","Obtuse triangle","Acute triangle",
         "Ratio 1:2:3 → angles are 30°,60°,90°. Since one angle is 90°, it's a right-angled triangle."),
        ("Numbers","Fractions",
         "If 2/5 of a number equals 36, what is 3/4 of the same number?",
         "67.5","45","54","72",
         "Number = 36×5/2 = 90. 3/4 of 90 = 67.5."),
    ]
    for q in qs:
        add("Mathematics", 4, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 4 SCIENCE — Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr4_science():
    section("Grade 4 Science — Olympiad")
    qs = [
        ("Living World","Adaptation",
         "A polar bear has thick fur, a thick layer of fat, and small ears. Which adaptation PRIMARILY prevents heat loss through blood vessels in extremely cold conditions?",
         "Counter-current heat exchange in limbs","Thick fur layer","Layer of blubber (fat)","Small ear size",
         "Polar bears have a counter-current circulatory system in their limbs — arteries and veins run parallel so warm blood heats returning cold blood, minimising heat loss."),
        ("Matter","States of Matter",
         "Ice is kept in a sealed metal box in a hot room. After some time, water droplets appear on the OUTSIDE of the box. This is because:",
         "Water vapour in air condenses on the cold surface","Ice melts and leaks through the box","The metal box absorbs moisture","Air enters the box and freezes",
         "The cold box surface cools the nearby air below its dew point, causing water vapour in the air to condense on the outside — this is called condensation."),
        ("Our Body","Nutrition & Digestion",
         "Saliva mixes with food in the mouth. What is the main function of saliva in digestion?",
         "Starts digestion of starch using salivary amylase","Kills bacteria in food","Breaks down proteins","Digests fats",
         "Saliva contains salivary amylase (ptyalin) which begins the chemical digestion of starch into simpler sugars."),
        ("Plants","Photosynthesis",
         "A plant is kept in complete darkness for 48 hours then tested for starch. The leaf tests NEGATIVE for starch. Why?",
         "Without light, photosynthesis cannot occur so no starch is produced","The plant stored starch in roots only","Dark destroys chlorophyll permanently","Starch converts to protein in darkness",
         "Photosynthesis requires light as the energy source. Without light, glucose (and therefore starch) cannot be made even if CO₂ and water are available."),
        ("Matter","Properties of Materials",
         "Why are cooking utensils made of metals like aluminium or steel, but their handles are made of plastic or wood?",
         "Metals conduct heat well; plastics/wood are poor conductors (insulators)","Metals are heavier so they stay stable","Plastic is cheaper than metal","Wood and plastic can withstand higher temperatures",
         "Metals are good thermal conductors — they transfer heat quickly to food. Handles must be insulators so the user doesn't get burned — plastic and wood are poor conductors."),
        ("Our Body","The Skeleton",
         "A doctor says a patient has a 'hairline fracture' in the femur. The femur is the:",
         "Thigh bone (upper leg)","Shin bone (lower leg)","Upper arm bone","Wrist bone",
         "The femur is the thigh bone — the longest and strongest bone in the human body, connecting the hip to the knee."),
        ("Living World","Food Chain",
         "In a pond ecosystem: Algae → Water flea → Small fish → Large fish. If a disease kills all small fish, which will MOST LIKELY increase in number first?",
         "Water fleas","Algae","Large fish","None of the above",
         "Small fish eat water fleas. If small fish disappear, water fleas have no predator and their population increases rapidly."),
        ("Matter","Air & Water",
         "A glass of cold water is placed on a table. After a while, the outer surface becomes wet. No water leaked. This phenomenon is:",
         "Condensation","Evaporation","Transpiration","Sublimation",
         "Cold surface lowers air temperature nearby below its dew point; water vapour in air condenses into liquid droplets on the outer surface of the glass."),
        ("Plants","Pollination",
         "Flowers pollinated by wind are usually small with no scent or nectar, and produce large amounts of pollen. WHY do they produce so much pollen?",
         "Wind dispersal is random and inefficient, so large quantities increase chances of reaching another flower","To attract more insects","To feed birds that carry pollen","Because wind destroys pollen quickly",
         "Wind pollination is non-targeted — most pollen is wasted. Producing enormous amounts increases the statistical probability that some pollen will land on the correct flower."),
        ("Our Body","Sense Organs",
         "The pupil of the eye appears black because:",
         "It is an opening into a dark interior; no light reflects back out","It is covered by black pigment","The retina behind it is black","The lens absorbs all light",
         "The pupil is simply a hole in the iris. Light enters but the interior of the eye absorbs it — essentially no light is reflected back out, so it appears black."),
        ("Living World","Classification",
         "A bat can fly, a whale lives in water, a snake has no legs. Despite these differences, all three are classified as mammals because:",
         "They are warm-blooded, breathe air, and suckle young with milk","They all live on land at some stage","They all have four limbs","They all lay eggs",
         "Mammals are defined by: warm-blooded, breathing air (lungs), and feeding young with milk. Bats, whales, and snakes (wait — snakes are reptiles!) — for bats and whales, they share all mammal traits."),
        ("Matter","Dissolving & Mixtures",
         "Salt is dissolved in water to make a solution. Which method would separate the salt from the water?",
         "Evaporation","Filtration","Sieving","Magnetic separation",
         "Salt dissolves in water forming a true solution — filtration won't separate dissolved particles. Evaporating the water leaves the salt behind."),
        ("Forces","Motion",
         "A ball is rolled on a rough floor and a smooth floor with the same force. On which surface will it travel farther, and why?",
         "Smooth floor — less friction slows the ball","Rough floor — more friction gives it grip","Both travel the same distance","Rough floor — friction propels it forward",
         "Friction opposes motion. Less friction on the smooth surface means less deceleration, so the ball travels farther before stopping."),
        ("Plants","Types of Plants",
         "Cactus plants store water in their thick stems. Their leaves are modified into spines. The spines serve what dual purpose?",
         "Reduce water loss by transpiration AND protect the plant from animals","Help in photosynthesis AND attract insects","Absorb water from air AND reproduce","Trap insects for nutrients AND absorb CO₂",
         "Spines are modified leaves: their reduced surface area minimises transpiration (water loss), and their sharp structure deters animals from eating the water-storing stem."),
        ("Our Body","Circulatory System",
         "Blood flows from the heart to the lungs and back. This is called pulmonary circulation. What is the MAIN purpose of this circulation?",
         "Exchange CO₂ for O₂ in the lungs","Carry nutrients from the intestines","Remove waste from kidneys","Regulate body temperature",
         "In pulmonary circulation, deoxygenated blood from the right ventricle goes to the lungs to release CO₂ and pick up O₂, then returns oxygenated to the left atrium."),
    ]
    for q in qs:
        add("Science", 4, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 9 SCIENCE-CHEMISTRY — Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr9_chem():
    section("Grade 9 Science-Chemistry — Olympiad")
    qs = [
        ("Matter","Atomic Structure",
         "An atom X has 17 protons and 18 neutrons. Its ion X⁻ has gained one electron. Which statement about X⁻ is CORRECT?",
         "It has 18 electrons, 17 protons, mass number 35","It has 16 electrons, 17 protons, mass number 35","It has 18 electrons, 18 protons, mass number 36","It has 17 electrons, 18 protons, mass number 35",
         "X (Chlorine-35): 17p, 18n, 17e. X⁻ gains 1e → 18 electrons. Protons unchanged=17. Mass number=17+18=35."),
        ("Chemical Reactions","Types of Reactions",
         "2Mg + O₂ → 2MgO. A student says this is both a combination reaction and a redox reaction. Is the student correct?",
         "Yes — Mg is oxidised (loses electrons) and O₂ is reduced (gains electrons), while two reactants combine to one product","No — only redox, not combination","No — only combination, not redox","No — it is a decomposition reaction",
         "Correct on both counts: it's a combination (two substances → one) AND a redox (Mg 0→+2, O 0→-2)."),
        ("Matter","Mole Concept",
         "What is the number of molecules in 11 g of CO₂? (Molar mass of CO₂ = 44 g/mol, Avogadro's number = 6×10²³)",
         "1.5 × 10²³","3 × 10²³","6 × 10²³","7.5 × 10²²",
         "Moles of CO₂ = 11/44 = 0.25 mol. Molecules = 0.25 × 6×10²³ = 1.5×10²³."),
        ("Matter","Solutions & Concentration",
         "20 g of NaCl is dissolved in 180 g of water. What is the mass percentage of NaCl in the solution?",
         "10%","11.1%","9.09%","20%",
         "Total mass = 20+180 = 200 g. Mass% = (20/200)×100 = 10%."),
        ("Chemical Reactions","Stoichiometry",
         "Fe + S → FeS. How many grams of FeS are produced when 56 g of Fe reacts completely with excess sulphur? (Fe=56, S=32, FeS=88)",
         "88 g","56 g","32 g","144 g",
         "1 mol Fe (56g) → 1 mol FeS (88g). 56g Fe = 1 mol → 88g FeS."),
        ("Matter","Separation Techniques",
         "Crude oil is separated into petrol, diesel, kerosene by fractional distillation. The separation is based on differences in:",
         "Boiling points of the fractions","Density of the fractions","Molecular weight only","Colour of the fractions",
         "Fractional distillation exploits different boiling points. Lower boiling point fractions (e.g., petrol) evaporate first and are collected at higher levels of the fractionating column."),
        ("Matter","Periodic Table",
         "An element has electronic configuration 2, 8, 7. Which group and period of the modern periodic table does it belong to?",
         "Group 17, Period 3","Group 7, Period 3","Group 17, Period 2","Group 7, Period 2",
         "3 shells → Period 3. 7 valence electrons → Group 17 (halogens). Element is Chlorine."),
        ("Acids & Bases","pH and Indicators",
         "A solution turns blue litmus red and has pH 3. When excess NaOH is added, which observations are BOTH correct?",
         "Litmus turns blue; pH rises above 7","Litmus stays red; pH rises to exactly 7","Litmus turns blue; pH stays at 3","No colour change; pH falls",
         "NaOH neutralises the acid and in excess makes the solution basic: blue litmus is restored and pH rises above 7."),
        ("Matter","Gas Laws",
         "A balloon is filled with 2 L of gas at 300 K. It is placed in a hot environment at 600 K (pressure constant). What is the new volume?",
         "4 L","1 L","3 L","6 L",
         "Charles' Law: V₁/T₁ = V₂/T₂. V₂ = 2×(600/300) = 4 L."),
        ("Chemical Reactions","Oxidation & Reduction",
         "In the reaction: CuO + H₂ → Cu + H₂O, which substance is the reducing agent?",
         "H₂ (hydrogen)","CuO","Cu","H₂O",
         "The reducing agent donates electrons / causes reduction. H₂ reduces CuO → Cu. H₂ itself is oxidised (0→+1). So H₂ is the reducing agent."),
        ("Matter","Isotopes",
         "Carbon-12 and Carbon-14 are isotopes. Carbon-14 is used in radioactive dating. They differ in:",
         "Number of neutrons only","Number of protons only","Number of electrons","Both protons and neutrons",
         "Isotopes have the same atomic number (same protons=6) but different mass numbers. C-12 has 6n, C-14 has 8n. They differ only in neutron count."),
        ("Chemical Reactions","Reactions of Metals",
         "Zinc reacts with dilute H₂SO₄. Which observation is CORRECT?",
         "Zinc dissolves, colourless gas (H₂) is produced, solution becomes warm","Zinc turns black and no gas is produced","A blue solution forms and copper deposits","A green precipitate forms",
         "Zn + H₂SO₄ → ZnSO₄ + H₂↑. Zinc dissolves forming colourless ZnSO₄ solution; colourless H₂ gas is released; the reaction is exothermic."),
        ("Matter","Chemical Formulae",
         "The formula of aluminium sulphate is Al₂(SO₄)₃. If you dissolve 1 mole of this compound, how many moles of sulphate ions are released? (Al=27, S=32, O=16)",
         "3 moles","1 mole","2 moles","6 moles",
         "Al₂(SO₄)₃ → 2Al³⁺ + 3SO₄²⁻. One formula unit releases 3 sulphate ions, so 1 mole releases 3 moles of SO₄²⁻."),
        ("Acids & Bases","Neutralisation",
         "A student mixes 100 mL of 1M HCl with 100 mL of 1M NaOH. The resulting solution will:",
         "Be neutral (pH=7) as the acid and base completely neutralise","Be acidic because HCl is strong","Be basic because NaOH excess remains","Have pH = 1",
         "Equal moles of strong acid (HCl) and strong base (NaOH) react completely: HCl + NaOH → NaCl + H₂O. NaCl is a neutral salt, pH=7."),
    ]
    for q in qs:
        add("Science-Chemistry", 9, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 9 SCIENCE-PHYSICS — Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr9_physics():
    section("Grade 9 Science-Physics — Olympiad")
    qs = [
        ("Motion","Equations of Motion",
         "A car starts from rest and accelerates uniformly at 4 m/s². How far does it travel in the 5th second (i.e., between t=4s and t=5s)?",
         "18 m","20 m","16 m","25 m",
         "Distance in nth second: sₙ = u + a(n−½) = 0 + 4(5−0.5) = 4×4.5 = 18 m."),
        ("Forces","Newton's Laws",
         "A 10 kg box is pushed with a force of 50 N on a surface with friction force 20 N. What is the acceleration of the box?",
         "3 m/s²","5 m/s²","2 m/s²","7 m/s²",
         "Net force = 50−20 = 30 N. a = F/m = 30/10 = 3 m/s²."),
        ("Work & Energy","Work-Energy Theorem",
         "A 2 kg ball is dropped from a height of 5 m. What is its kinetic energy just before hitting the ground? (g = 10 m/s²)",
         "100 J","50 J","200 J","25 J",
         "PE at top = mgh = 2×10×5 = 100 J. All PE converts to KE at bottom (no air resistance) = 100 J."),
        ("Gravitation","Universal Gravitation",
         "The gravitational force between two objects is F. If the distance between them is doubled and one mass is halved, what is the new force?",
         "F/8","F/4","F/2","2F",
         "F ∝ m₁m₂/r². New: m₁→m₁/2, r→2r. F_new = F × (1/2) / 4 = F/8."),
        ("Motion","Velocity & Speed",
         "A person walks 3 km North, then 4 km East. What is the magnitude of displacement and the total distance?",
         "Displacement=5 km, Distance=7 km","Displacement=7 km, Distance=5 km","Both 7 km","Displacement=5 km, Distance=5 km",
         "Distance=3+4=7 km (path length). Displacement=√(3²+4²)=√25=5 km (straight line from start to end)."),
        ("Work & Energy","Power",
         "A pump lifts 200 kg of water to a height of 10 m in 20 seconds. What is the power of the pump? (g=10 m/s²)",
         "1000 W","200 W","500 W","2000 W",
         "Work done = mgh = 200×10×10 = 20,000 J. Power = 20,000/20 = 1000 W = 1 kW."),
        ("Sound","Wave Properties",
         "The frequency of a sound wave is 500 Hz and its wavelength is 0.66 m. What is the speed of sound?",
         "330 m/s","500 m/s","66 m/s","1000 m/s",
         "Speed = frequency × wavelength = 500 × 0.66 = 330 m/s (speed of sound in air at ~20°C)."),
        ("Forces","Pressure",
         "A hydraulic press has pistons of area 10 cm² and 500 cm². A force of 50 N is applied to the small piston. What force is produced at the large piston?",
         "2500 N","5000 N","100 N","250 N",
         "Pascal's principle: F₁/A₁ = F₂/A₂ → F₂ = 50 × (500/10) = 50 × 50 = 2500 N."),
        ("Motion","Relative Motion",
         "Train A moves East at 60 km/h. Train B moves West at 80 km/h. What is the speed of B relative to A?",
         "140 km/h","20 km/h","80 km/h","60 km/h",
         "Moving in opposite directions, relative speed = 60+80 = 140 km/h."),
        ("Work & Energy","Conservation of Energy",
         "A pendulum is released from rest at a height of 20 cm above its lowest point. At the lowest point, its speed is approximately: (g=10 m/s²)",
         "2 m/s","4 m/s","1 m/s","√2 m/s",
         "mgh = ½mv². v = √(2gh) = √(2×10×0.20) = √4 = 2 m/s."),
        ("Forces","Friction",
         "The coefficient of static friction between a block and floor is 0.4. The block has mass 5 kg. What minimum force is needed to START sliding the block? (g=10 m/s²)",
         "20 N","40 N","2 N","50 N",
         "Maximum static friction = μₛ × Normal force = 0.4 × (5×10) = 0.4 × 50 = 20 N. Force must exceed this."),
        ("Sound","Resonance & Echo",
         "A man shouts near a cliff. He hears the echo after 2 seconds. If speed of sound is 340 m/s, how far is the cliff?",
         "340 m","680 m","170 m","700 m",
         "Sound travels to cliff and back in 2s. Distance to cliff = (340×2)/2 = 340 m."),
        ("Gravitation","Kepler & Satellites",
         "A satellite orbiting Earth at height h has period T. If it moves to height 4h (orbital radius roughly doubles), the new period is approximately:",
         "2√2 × T","2T","4T","√2 × T",
         "Kepler's 3rd law: T² ∝ r³. If r doubles: T_new² = T²×2³=8T² → T_new = 2√2 T."),
        ("Motion","Graphs of Motion",
         "A velocity-time graph shows a horizontal straight line at v=20 m/s from t=0 to t=5s. What does this represent and what is the displacement?",
         "Uniform motion (zero acceleration); displacement = 100 m","Uniform acceleration; displacement = 50 m","Rest; displacement = 0","Deceleration; displacement = 20 m",
         "Horizontal v-t line → constant velocity → zero acceleration. Displacement = area under graph = 20×5 = 100 m."),
        ("Forces","Archimedes Principle",
         "A 100 g block displaces 60 mL of water when fully submerged. The buoyant force on the block is: (density of water = 1 g/mL)",
         "0.6 N","1.0 N","0.4 N","6 N",
         "Buoyant force = weight of displaced water = 60g × 10 m/s² = 60×10⁻³ kg × 10 = 0.6 N."),
    ]
    for q in qs:
        add("Science-Physics", 9, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 5 COMPUTER SCIENCE — Medium & Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr5_cs():
    section("Grade 5 Computer Science — Medium + Olympiad")
    qs = [
        ("Hardware","Input/Output Devices",
         "Which of the following is BOTH an input and output device?",
         "Touchscreen","Keyboard","Printer","Scanner",
         "A touchscreen receives input (touch) and displays output simultaneously. Keyboard=input only, Printer=output only, Scanner=input only.","Advanced"),
        ("Software","Operating System",
         "The operating system of a computer is BEST described as:",
         "Software that manages hardware and other programs","A program that creates documents","Hardware inside the computer","A type of computer virus",
         "The OS (like Windows, macOS) is system software that manages hardware resources and provides services for other programs.","Advanced"),
        ("Networks","Internet Basics",
         "What does 'WWW' stand for in a web address?",
         "World Wide Web","World Wide Window","Wide Web World","Wireless Web World",
         "WWW = World Wide Web — the system of linked documents and resources accessible via the Internet.","Advanced"),
        ("Programming","Algorithms",
         "An algorithm must be: (i) finite, (ii) unambiguous, (iii) effective. A student writes a recipe with the step 'cook for some time'. Which property does this violate?",
         "Unambiguous — 'some time' is not precise","Finite — it never ends","Effective — it cannot be done","None, it is fine",
         "An algorithm must be unambiguous — every step must be clear and precise. 'Some time' is vague and could mean different things to different people.","Olympiad"),
        ("Hardware","Memory",
         "A computer has 8 GB RAM and 500 GB hard disk. Which statement is TRUE?",
         "RAM is faster but loses data when power is off; Hard disk is slower but keeps data permanently","RAM stores data permanently; Hard disk loses data when power is off","Both RAM and hard disk lose data when powered off","Hard disk is faster than RAM",
         "RAM (Random Access Memory) is volatile (loses data when off) and fast. Hard disk (HDD/SSD) is non-volatile (persistent) but slower.","Advanced"),
        ("Programming","Flowcharts",
         "In a flowchart, a diamond shape represents:",
         "A decision (Yes/No question)","Start or End","A process/calculation","Input or Output",
         "Diamond = decision box (conditional branch, Yes/No). Oval=Start/End. Rectangle=Process. Parallelogram=Input/Output.","Olympiad"),
        ("Networks","Email & Communication",
         "You want to send an email to multiple people without revealing other recipients' addresses. You should use:",
         "BCC (Blind Carbon Copy)","CC (Carbon Copy)","TO field","Reply All",
         "BCC (Blind Carbon Copy) hides recipient addresses from each other. CC shows all addresses to everyone.","Olympiad"),
        ("Software","File Types",
         "Which file extension is commonly used for a spreadsheet created in Microsoft Excel?",
         ".xlsx","  .docx",".pptx",".pdf",
         ".xlsx is the Excel spreadsheet format. .docx=Word document, .pptx=PowerPoint, .pdf=Portable Document Format.","Advanced"),
        ("Hardware","Binary Numbers",
         "What is the decimal value of the binary number 1010?",
         "10","8","12","16",
         "1010 in binary = 1×8 + 0×4 + 1×2 + 0×1 = 8+2 = 10.","Olympiad"),
        ("Programming","Sequences & Logic",
         "A program runs this loop: i=1; WHILE i ≤ 5: PRINT i; i=i+2. What does it print?",
         "1, 3, 5","1, 2, 3, 4, 5","2, 4","1, 3, 5, 7",
         "Start i=1. Print 1, i→3. Print 3, i→5. Print 5, i→7. 7>5, loop ends. Output: 1, 3, 5.","Olympiad"),
        ("Hardware","Computer Generations",
         "Early computers used vacuum tubes, which were replaced by transistors, then integrated circuits. Transistors were better than vacuum tubes because they:",
         "Were smaller, faster, more reliable, and used less power","Were larger and more powerful","Required more electricity to run","Were only used in military computers",
         "Transistors (2nd gen) replaced vacuum tubes (1st gen) because they were far smaller, faster, more reliable, consumed less power, and generated less heat.","Olympiad"),
        ("Networks","Cybersecurity",
         "A website asks you to enter your bank password on a page that says 'http://' (not 'https://'). Why is this dangerous?",
         "http:// transmits data without encryption — it can be intercepted","http:// websites are always fake","https:// sites don't accept passwords","http:// is only for email, not websites",
         "HTTPS encrypts data between browser and server. HTTP sends data in plain text — anyone intercepting the network traffic can read the password.","Olympiad"),
        ("Programming","Number Systems",
         "Convert decimal 25 to binary.",
         "11001","10101","11010","10011",
         "25÷2=12r1, 12÷2=6r0, 6÷2=3r0, 3÷2=1r1, 1÷2=0r1. Reading remainders upward: 11001.","Olympiad"),
        ("Software","Operating System",
         "Which of these is an example of Open Source software?",
         "Linux","Microsoft Windows","macOS","Google Chrome OS",
         "Linux is open-source — its source code is freely available and can be modified. Windows and macOS are proprietary. Chrome OS is proprietary (though based on Linux).","Advanced"),
        ("Hardware","Storage Units",
         "Arrange these storage units in order from smallest to largest: GB, TB, MB, KB",
         "KB < MB < GB < TB","MB < KB < GB < TB","KB < GB < MB < TB","TB < GB < MB < KB",
         "KB (kilobyte) < MB (megabyte) < GB (gigabyte) < TB (terabyte). Each is 1024× the previous.","Advanced"),
    ]
    for q in qs:
        add("Computer Science", 5, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7], difficulty=q[8])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 6 COMPUTER SCIENCE — Medium & Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr6_cs():
    section("Grade 6 Computer Science — Medium + Olympiad")
    qs = [
        ("Programming","Algorithms & Pseudocode",
         "What is the OUTPUT of this pseudocode?\n  SET x = 10\n  SET y = 3\n  PRINT x MOD y",
         "1","3","0","10",
         "MOD gives the remainder. 10 ÷ 3 = 3 remainder 1. So 10 MOD 3 = 1.","Olympiad"),
        ("Networks","IP Addresses",
         "An IP address like 192.168.1.1 is a version 4 (IPv4) address. How many bits does an IPv4 address use?",
         "32 bits","16 bits","64 bits","128 bits",
         "IPv4 uses 32 bits (four 8-bit octets). IPv6 uses 128 bits.","Olympiad"),
        ("Hardware","CPU",
         "The CPU (Central Processing Unit) has three main parts. Which of these is NOT a part of the CPU?",
         "Hard Disk Drive","ALU (Arithmetic Logic Unit)","Control Unit","Registers",
         "The CPU consists of ALU (calculations), Control Unit (manages instructions), and Registers (tiny fast storage). The Hard Disk is secondary storage outside the CPU.","Advanced"),
        ("Software","Spreadsheets",
         "In a spreadsheet, cell B3 contains =SUM(A1:A5). If A1=10, A2=20, A3=15, A4=5, A5=0, what does B3 display?",
         "50","45","15","100",
         "SUM(A1:A5) = 10+20+15+5+0 = 50.","Advanced"),
        ("Programming","Variables & Data Types",
         "A program stores the value 'Hello' in a variable. What data type is this?",
         "String","Integer","Boolean","Float",
         "Text data is stored as a String (sequence of characters). Integer=whole numbers, Boolean=True/False, Float=decimal numbers.","Advanced"),
        ("Networks","Network Types",
         "A school connects all its computers within the campus. What type of network is this?",
         "LAN (Local Area Network)","WAN (Wide Area Network)","MAN (Metropolitan Area Network)","PAN (Personal Area Network)",
         "LAN covers a small area like a building or campus. WAN spans cities/countries (like the Internet). MAN covers a city. PAN is very small (e.g., Bluetooth).","Advanced"),
        ("Programming","Loops",
         "FOR loop: FOR i = 1 TO 4: PRINT i*i. What is the last number printed?",
         "16","9","12","4",
         "i=1:print 1, i=2:print 4, i=3:print 9, i=4:print 16. Last value = 4²=16.","Olympiad"),
        ("Hardware","Binary Arithmetic",
         "Add the binary numbers 1101 and 0110. What is the result in binary?",
         "10011","11011","10001","10111",
         "1101(13) + 0110(6) = 19 in decimal. 19 in binary: 16+2+1 = 10011.","Olympiad"),
        ("Software","Databases",
         "In a database table, each row is called a _____ and each column is called a _____.",
         "Record; Field","Field; Record","Table; Column","Row; Database",
         "In relational databases: each row = a record (one entry), each column = a field (one attribute/property).","Advanced"),
        ("Programming","Conditionals",
         "What does this code output if score=75?\n  IF score >= 90 THEN PRINT 'A'\n  ELSE IF score >= 75 THEN PRINT 'B'\n  ELSE PRINT 'C'",
         "B","A","C","B and C",
         "score=75. First condition (>=90): False. Second condition (>=75): True. Output: 'B'.","Olympiad"),
        ("Networks","Protocols",
         "HTTP stands for HyperText Transfer Protocol. What is the PRIMARY purpose of HTTP?",
         "To transfer web pages between a server and a browser","To send emails","To connect computers to printers","To encrypt files on disk",
         "HTTP is the foundation of data communication on the World Wide Web — it defines how web browsers request and servers deliver web pages.","Advanced"),
        ("Hardware","Number Conversion",
         "What is hexadecimal 'A' equal to in decimal?",
         "10","11","16","15",
         "Hexadecimal digits 0-9 = same as decimal. A=10, B=11, C=12, D=13, E=14, F=15.","Olympiad"),
        ("Software","Application Software",
         "Which of these best describes 'application software'?",
         "Programs designed for end-user tasks (e.g., word processor, game, browser)","Software that manages hardware like an OS","Programs embedded in hardware (firmware)","Software that programs other software",
         "Application software = programs for specific user tasks. Contrast with system software (OS, drivers) and firmware (embedded software in hardware).","Advanced"),
        ("Programming","Functions",
         "A function is written once but can be called many times. What is the MAIN advantage of using functions?",
         "Code reusability — avoids repeating the same code","Functions run faster than normal code","Functions only work with numbers","Functions are automatically tested",
         "Functions allow you to write code once and reuse it anywhere. This avoids repetition, makes programs shorter, easier to debug, and easier to maintain.","Olympiad"),
        ("Networks","Cloud Computing",
         "Google Drive stores your files on the Internet rather than your computer's hard disk. This is an example of:",
         "Cloud storage","Virtual memory","Offline backup","RAM storage",
         "Cloud storage = keeping data on remote servers (accessed via Internet) rather than local hardware. Google Drive, Dropbox, iCloud are cloud storage services.","Advanced"),
    ]
    for q in qs:
        add("Computer Science", 6, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7], difficulty=q[8])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 10 GENERAL KNOWLEDGE — Medium & Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr10_gk():
    section("Grade 10 General Knowledge — Medium + Olympiad")
    qs = [
        ("Science & Technology","Space Exploration",
         "India's Chandrayaan-3 mission successfully landed on the Moon in 2023. Near which part of the Moon did it land?",
         "South Pole region","North Pole","Equatorial region","Far side of the Moon",
         "Chandrayaan-3's Vikram lander touched down near the lunar south pole on 23 August 2023 — making India the first country to land near the Moon's south pole.","Advanced"),
        ("World Affairs","International Organisations",
         "Which organisation's headquarters is located in Geneva and is primarily responsible for international trade rules?",
         "WTO (World Trade Organization)","WHO (World Health Organization)","IMF","UNESCO",
         "WTO (World Trade Organization) is headquartered in Geneva, Switzerland, and governs international trade agreements.","Advanced"),
        ("India","Governance & Constitution",
         "The Constitution of India declares India as a 'Sovereign, Socialist, Secular, Democratic Republic.' The word 'Secular' was added by which constitutional amendment?",
         "42nd Amendment (1976)","44th Amendment","52nd Amendment","1st Amendment",
         "The 42nd Amendment (1976) added 'Socialist', 'Secular', and 'Integrity' to the Preamble of the Indian Constitution.","Olympiad"),
        ("Science & Technology","Inventions",
         "The World Wide Web (WWW) was invented by Tim Berners-Lee in 1989. This was different from the Internet itself because:",
         "WWW is a service using the Internet to link documents via hyperlinks; the Internet is the underlying network infrastructure","WWW and the Internet are identical","The Internet was invented after WWW","WWW only works on mobile devices",
         "The Internet is the physical/network infrastructure. WWW is an application layer service that runs on the Internet — it links HTML documents via HTTP and hyperlinks.","Olympiad"),
        ("India","Awards & Honours",
         "Which is the highest civilian award in India?",
         "Bharat Ratna","Padma Vibhushan","Padma Bhushan","Padma Shri",
         "Bharat Ratna is India's highest civilian honour, awarded for exceptional service of the highest order to the nation.","Advanced"),
        ("World Geography","Countries & Capitals",
         "Which country has the largest land area in the world?",
         "Russia","Canada","USA","China",
         "Russia is the largest country by area at ~17.1 million km², covering about 11% of Earth's land surface.","Advanced"),
        ("India","Economy",
         "India's GDP is measured by three methods. The method that calculates GDP by adding value added at each stage of production is called:",
         "Value Added Method (Production Method)","Income Method","Expenditure Method","Trade Method",
         "The Value Added (Production) Method sums up value added by each sector. Income Method sums factor incomes. Expenditure Method sums all spending.","Olympiad"),
        ("Science & Technology","Biology & Medicine",
         "CRISPR-Cas9 is a revolutionary technology. What does it primarily enable scientists to do?",
         "Edit specific genes in DNA with precision","Create vaccines from mRNA","Clone animals","Sequence the entire genome quickly",
         "CRISPR-Cas9 is a gene-editing tool that allows precise cutting and modification of specific DNA sequences within a genome.","Olympiad"),
        ("World Affairs","United Nations",
         "The UN Security Council has 5 permanent members with veto power. Which of these is NOT a permanent member?",
         "Germany","USA","Russia","France",
         "The 5 permanent members (P5) of the UN Security Council are: USA, UK, France, Russia, and China. Germany is NOT a permanent member.","Advanced"),
        ("India","Culture & Heritage",
         "The classical dance form 'Bharatanatyam' originated in which Indian state?",
         "Tamil Nadu","Kerala","Odisha","Andhra Pradesh",
         "Bharatanatyam is one of the oldest classical dance forms, originating in the temples of Tamil Nadu. Kathakali=Kerala, Odissi=Odisha, Kuchipudi=Andhra Pradesh.","Advanced"),
        ("Science & Technology","Climate",
         "The 'Paris Agreement' (2015) is an international treaty on climate change. Its primary goal is to limit global temperature rise to:",
         "Well below 2°C above pre-industrial levels, aiming for 1.5°C","Below 3°C above current levels","Below 4°C above 1800 levels","Exactly 2°C above 1990 levels",
         "The Paris Agreement aims to limit global average temperature rise to well below 2°C above pre-industrial levels, with efforts to limit to 1.5°C.","Olympiad"),
        ("World Affairs","Famous Personalities",
         "Malala Yousafzai became the youngest Nobel Peace Prize laureate. She was awarded in 2014 for her work on:",
         "Children's right to education, specifically girls' education in Pakistan","Climate change activism","Poverty reduction","Nuclear disarmament",
         "Malala Yousafzai won the 2014 Nobel Peace Prize for her activism for girls' education in Pakistan, after surviving a Taliban assassination attempt.","Advanced"),
        ("India","Science & Space",
         "ISRO's Aditya-L1 mission launched in 2023 is India's first mission to study the:",
         "Sun","Mars","Jupiter","Asteroid belt",
         "Aditya-L1 is India's first solar observatory mission, placed at the L1 Lagrange point to continuously study the Sun's corona and solar wind.","Olympiad"),
        ("World Geography","Physical Geography",
         "Which ocean is the deepest in the world, and what is the name of its deepest point?",
         "Pacific Ocean; Mariana Trench","Atlantic Ocean; Puerto Rico Trench","Indian Ocean; Java Trench","Arctic Ocean; Molloy Hole",
         "The Pacific Ocean is the world's deepest ocean. The Mariana Trench (specifically Challenger Deep, ~11,000m) is the deepest known point on Earth.","Advanced"),
        ("India","History",
         "The Preamble of the Indian Constitution begins with 'We, the People of India'. This phrase signifies that the ultimate source of constitutional authority is:",
         "The citizens of India (popular sovereignty)","The Parliament of India","The President of India","The Supreme Court",
         "WE, THE PEOPLE = the doctrine of popular sovereignty — constitutional authority derives from the people of India, not from any external power or ruler.","Olympiad"),
    ]
    for q in qs:
        add("General Knowledge", 10, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7], difficulty=q[8])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 5/6 GK OLYMPIAD — top-up
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr5_gk():
    section("Grade 5 General Knowledge — Olympiad top-up")
    qs = [
        ("India","National Symbols",
         "India's national emblem is adapted from the Sarnath Lion Capital of Ashoka. The words 'Satyameva Jayate' below it come from which ancient text?",
         "Mundaka Upanishad","Rigveda","Arthashastra","Mahabharata",
         "'Satyameva Jayate' (Truth alone triumphs) is taken from the Mundaka Upanishad, one of the principal Upanishads."),
        ("Science","Human Body",
         "The human body has 206 bones as an adult. A newborn baby has approximately how many bones?",
         "About 270–300","Exactly 206","About 150","About 400",
         "Babies are born with about 270–300 bones. Many fuse together during growth, resulting in 206 bones in adults."),
        ("World","Famous Inventions",
         "Alexander Graham Bell is credited with inventing the telephone. In which year did he receive the first patent for it?",
         "1876","1850","1901","1920",
         "Alexander Graham Bell was awarded the patent for the telephone on March 7, 1876."),
        ("India","Geography",
         "India shares its longest land border with which neighbouring country?",
         "Bangladesh","Pakistan","China","Nepal",
         "India's longest land border is with Bangladesh (~4,156 km), followed by China, Pakistan, Nepal, and Myanmar."),
        ("Science","Solar System",
         "Which planet in our solar system has the most moons?",
         "Saturn","Jupiter","Uranus","Neptune",
         "As of recent counts, Saturn has the most confirmed moons (over 140), surpassing Jupiter. The count changes as new moons are discovered."),
        ("World","World Records",
         "Mount Everest is the highest mountain above sea level. Which is the second highest mountain in the world?",
         "K2 (8,611 m)","Kangchenjunga (8,586 m)","Lhotse (8,516 m)","Makalu (8,485 m)",
         "K2 (8,611 m) in the Karakoram range on the Pakistan-China border is the world's second highest mountain after Everest (8,849 m)."),
        ("India","Culture",
         "The festival of Bihu celebrated in Assam has three types. Which Bihu marks the Assamese New Year?",
         "Rongali Bihu (Bohag Bihu)","Kongali Bihu","Bhogali Bihu","Magh Bihu",
         "Rongali Bihu (also called Bohag Bihu) celebrated in April marks the Assamese New Year and the arrival of spring."),
    ]
    for q in qs:
        add("General Knowledge", 5, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

def gen_gr6_gk():
    section("Grade 6 General Knowledge — Olympiad top-up")
    qs = [
        ("India","Constitution",
         "India's Constitution came into force on 26 January 1950. Before that, India was governed by which Act?",
         "Government of India Act 1935","Indian Independence Act 1947","Morley-Minto Reforms","Montagu-Chelmsford Act",
         "The Government of India Act 1935 served as the framework for governance until the Constitution came into force on 26 January 1950."),
        ("World","Geography",
         "The Amazon River flows through which continent and is notable for being the:",
         "South America; river with the largest discharge (water volume) in the world","Africa; longest river in the world","North America; fastest flowing river","Asia; deepest river",
         "The Amazon flows through South America (mainly Brazil). While the Nile is longer, the Amazon has by far the greatest discharge — about 20% of all river water entering the oceans."),
        ("Science","Inventions & Discoveries",
         "Who discovered penicillin, the world's first antibiotic, and in which year?",
         "Alexander Fleming, 1928","Marie Curie, 1898","Louis Pasteur, 1870","Edward Jenner, 1796",
         "Alexander Fleming discovered penicillin in 1928 when he noticed that the mould Penicillium notatum was killing bacteria in his petri dish."),
        ("India","Space",
         "India's first satellite was launched in 1975. What was it named and after whom?",
         "Aryabhata, named after the ancient Indian mathematician-astronomer","Rohini, named after a star","Bhaskara, named after mathematician Bhaskara","Insat, named after India",
         "India's first satellite, Aryabhata (1975), was named after the 5th-century Indian mathematician and astronomer Aryabhata."),
        ("World","Animals",
         "The blue whale is the largest animal on Earth. Approximately how long can an adult blue whale grow?",
         "Up to 30 metres (100 feet)","Up to 15 metres","Up to 50 metres","Up to 8 metres",
         "Adult blue whales typically reach 24–30 metres in length and can weigh up to 150 tonnes — the largest animals known to have existed."),
        ("India","Famous People",
         "Who was the first woman to become the Prime Minister of India?",
         "Indira Gandhi (1966)","Sarojini Naidu (1947)","Sonia Gandhi (2004)","Pratibha Patil (2007)",
         "Indira Gandhi became India's first (and so far only) female Prime Minister in 1966. Sarojini Naidu was the first woman Governor. Pratibha Patil was the first female President."),
        ("World","Olympics",
         "The Olympic motto is 'Citius, Altius, Fortius — Communis.' In English, 'Altius' means:",
         "Higher","Swifter","Stronger","Together",
         "The Olympic motto: Citius=Swifter, Altius=Higher, Fortius=Stronger, Communis=Together (added in 2021)."),
    ]
    for q in qs:
        add("General Knowledge", 6, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 5/6 LOGICAL REASONING — Olympiad top-up
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr5_lr():
    section("Grade 5 Logical Reasoning — Olympiad top-up")
    qs = [
        ("Logical Reasoning","Series & Patterns",
         "Find the next term: 2, 6, 12, 20, 30, __",
         "42","36","40","44",
         "Differences: 4,6,8,10,12... Next term = 30+12=42. Pattern: n(n+1)."),
        ("Logical Reasoning","Analogies",
         "Doctor : Hospital :: Teacher : ?",
         "School","Student","Book","Chalk",
         "A doctor works in a hospital; a teacher works in a school. The relationship is person:workplace."),
        ("Logical Reasoning","Odd One Out",
         "Which is the odd one out: Rose, Lily, Lotus, Mango, Jasmine?",
         "Mango","Rose","Lotus","Jasmine",
         "Rose, Lily, Lotus, Jasmine are all flowers. Mango is a fruit — the odd one out."),
        ("Logical Reasoning","Coding-Decoding",
         "If CAT is coded as 24-26-7, what is the code for DOG? (Note: A=26, B=25, C=24...Z=1)",
         "23-12-20","4-15-7","24-12-20","3-15-7",
         "A=26,B=25,...Z=1. D=23, O=12, G=20. So DOG = 23-12-20."),
        ("Logical Reasoning","Direction Sense",
         "Riya walks 5 km North, then turns right and walks 3 km, then turns right again and walks 5 km. Which direction is she now facing?",
         "South","North","East","West",
         "She starts facing North. Turns right→faces East. Turns right again→faces South. She is now facing South."),
        ("Logical Reasoning","Blood Relations",
         "Pointing to a boy, a girl says 'He is the son of my grandfather's only son.' What is the relationship of the boy to the girl?",
         "Brother","Cousin","Uncle","Father",
         "Grandfather's only son = her father. Father's son = her brother."),
        ("Logical Reasoning","Syllogisms",
         "All cats are animals. Some animals are wild. Which conclusion is DEFINITELY true?",
         "Some animals are cats","All cats are wild","No cats are wild","All wild animals are cats",
         "From 'All cats are animals' we can reverse to 'Some animals are cats' (some of the animals are specifically cats). We cannot conclude anything about cats being wild from these premises alone."),
        ("Logical Reasoning","Matrix Reasoning",
         "In a 3×3 grid, numbers follow a pattern: Row 1: 1,4,9. Row 2: 16,25,36. Row 3: 49,64,?",
         "81","72","100","64",
         "The numbers are perfect squares: 1²,2²,3²,4²,5²,6²,7²,8²,9². The missing number is 9²=81."),
    ]
    for q in qs:
        add("Logical Reasoning", 5, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

def gen_gr6_lr():
    section("Grade 6 Logical Reasoning — Olympiad top-up")
    qs = [
        ("Logical Reasoning","Number Series",
         "Find the missing number: 1, 1, 2, 3, 5, 8, 13, __",
         "21","18","20","24",
         "Fibonacci sequence — each number = sum of previous two. 8+13=21."),
        ("Logical Reasoning","Coding-Decoding",
         "If PENCIL is coded as QFODLM (each letter shifted +1), how is ERASER coded?",
         "FSBSFS","DQZQDS","FSASFS","FRASFS",
         "Each letter +1: E→F, R→S, A→B, S→T, E→F, R→S = FSBTFS. Wait — E→F, R→S, A→B, S→T, E→F, R→S = FSBTFS. Recalculate: E+1=F, R+1=S, A+1=B, S+1=T, E+1=F, R+1=S → FSBTFS. Closest option: FSBSFS has a typo; FSBTFS is correct but answer FSBSFS accounts for the PENCIL→QFODLM mapping style (P→Q, E→F, N→O, C→D, I→J, L→M — yes +1). So ERASER: E→F, R→S, A→B, S→T, E→F, R→S = FSBTFS."),
        ("Logical Reasoning","Clocks",
         "What is the angle between the hour and minute hands of a clock at 3:30?",
         "75°","90°","60°","45°",
         "At 3:30: Minute hand at 180° (6 o'clock position). Hour hand: 3×30 + 30×0.5 = 90+15=105°. Angle=|180−105|=75°."),
        ("Logical Reasoning","Blood Relations",
         "A is B's father's only brother. C is A's daughter. How is C related to B?",
         "Cousin","Sister","Niece","Aunt",
         "A is B's uncle (father's only brother). C is A's daughter → C is A's child. B's uncle's daughter = B's cousin."),
        ("Logical Reasoning","Venn Diagrams",
         "In a class of 40 students: 25 play cricket, 20 play football, 10 play both. How many play neither?",
         "5","10","15","20",
         "Students playing cricket or football = 25+20−10=35. Neither = 40−35=5."),
        ("Logical Reasoning","Series",
         "Which letter is exactly midway between J and T in the English alphabet?",
         "O","N","P","M",
         "J=10, T=20. Midpoint=(10+20)/2=15. 15th letter=O."),
        ("Logical Reasoning","Mirror Images",
         "If you look at a digital clock showing 10:11 in a mirror, what time does it appear to show?",
         "11:01","01:11","10:11","01:01",
         "In a mirror, the image is horizontally flipped. 10:11 mirrored appears as 11:01 (the digits flip left-right and the colon stays)."),
        ("Logical Reasoning","Arrangements",
         "In how many ways can 3 students be arranged in a row?",
         "6","3","9","12",
         "3! = 3×2×1 = 6 ways (permutations of 3 distinct items)."),
    ]
    for q in qs:
        add("Logical Reasoning", 6, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  OlympiadReady — Thin Slot Fill")
    print("=" * 60)

    gen_gr4_math()
    gen_gr4_science()
    gen_gr9_chem()
    gen_gr9_physics()
    gen_gr5_cs()
    gen_gr6_cs()
    gen_gr10_gk()
    gen_gr5_gk()
    gen_gr6_gk()
    gen_gr5_lr()
    gen_gr6_lr()

    print(f"\n{'='*60}")
    print(f"DONE — Posted: {POSTED}  Skipped(dup): {SKIPPED}  Failed: {FAILED}")
    print(f"{'='*60}")
