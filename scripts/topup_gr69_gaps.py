"""
Top-up script for remaining Gr6-9 gaps:
  - Science G6 Olympiad (15q)
  - Science G7 Olympiad (15q)
  - Hindi G8 Olympiad (15q)
  - General Knowledge G9 Advanced (15q)
  - General Knowledge G9 Olympiad (15q)
  - Science G9 Foundation (15q)
  - Social Studies G9 Foundation (15q)
"""
import pyodbc, json, uuid, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DB_CONN = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tcp:olympiadready-np.database.windows.net,1433;"
    "DATABASE=OlympiadReady;UID=nyxen-admin;PWD=Olympiad@2026;"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
)

def insert(conn, q):
    c = conn.cursor()
    c.execute("SELECT 1 FROM QuestionBank WHERE Subject=? AND Grade=? AND SubTopic=? AND QuestionText=?",
              q["subject"], q["grade"], q["subTopic"], q["questionText"])
    if c.fetchone():
        return "DUP"
    c.execute("""INSERT INTO QuestionBank
                 (QuestionBankId,Subject,Grade,Difficulty,Topic,SubTopic,
                  QuestionText,OptionsJson,CorrectAnswer,Explanation,CreatedAt)
                 VALUES (?,?,?,?,?,?,?,?,?,?,GETUTCDATE())""",
              str(uuid.uuid4()).upper(), q["subject"], q["grade"], q["difficulty"],
              q["topic"], q["subTopic"], q["questionText"],
              json.dumps(q["options"]), q["correctAnswer"], q["explanation"])
    conn.commit()
    return "OK"

# ─────────────────────────────────────────────────────────────
# SCIENCE G6 OLYMPIAD (15 questions)
# Topics: Physics, Chemistry, Biology basics at Olympiad level
# ─────────────────────────────────────────────────────────────
SCI6_OLY = [
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Light and Shadow", "subTopic": "Rectilinear Propagation of Light",
        "questionText": "A pinhole camera forms an image of a candle flame. If the height of the candle is 10 cm, the distance from candle to pinhole is 50 cm, and the distance from pinhole to screen is 25 cm, what is the height of the image?",
        "options": ["A: 2.5 cm", "B: 5 cm", "C: 10 cm", "D: 20 cm"],
        "correctAnswer": "B",
        "explanation": "By similar triangles: image height / object height = image distance / object distance. Image height = 10 × (25/50) = 5 cm."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Electricity and Circuits", "subTopic": "Series and Parallel Circuits",
        "questionText": "Three identical bulbs are connected in series to a battery. One bulb fuses (breaks). What happens to the other two bulbs?",
        "options": ["A: They glow brighter", "B: They glow dimmer", "C: They go off completely", "D: They are unaffected"],
        "correctAnswer": "C",
        "explanation": "In a series circuit, the same current flows through all components. If one bulb fuses (open circuit), the circuit is broken and no current flows — all bulbs go off."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Sorting Materials", "subTopic": "Properties of Materials",
        "questionText": "A student has a mixture of iron filings, sand, salt, and wood shavings mixed with water. Which sequence of separation techniques will isolate the iron filings first and then the salt?",
        "options": [
            "A: Filtration → Evaporation → Magnetic separation",
            "B: Magnetic separation → Filtration → Evaporation",
            "C: Evaporation → Magnetic separation → Filtration",
            "D: Magnetic separation → Evaporation → Filtration"
        ],
        "correctAnswer": "B",
        "explanation": "First use a magnet to remove iron filings, then filter to remove sand and wood shavings (insoluble), then evaporate the filtrate to recover dissolved salt."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Changes Around Us", "subTopic": "Reversible and Irreversible Changes",
        "questionText": "Which of the following changes involves a chemical change that CANNOT be reversed?",
        "options": [
            "A: Melting of wax",
            "B: Dissolution of sugar in water",
            "C: Burning of magnesium ribbon",
            "D: Stretching of a rubber band"
        ],
        "correctAnswer": "C",
        "explanation": "Burning magnesium converts it to magnesium oxide (MgO) — a new substance is formed. This is an irreversible chemical change. The others are physical or reversible changes."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Motion and Measurement", "subTopic": "Types of Motion",
        "questionText": "The tip of the second hand of a clock undergoes which combination of motions?",
        "options": [
            "A: Linear motion only",
            "B: Circular motion and rotational motion",
            "C: Oscillatory motion only",
            "D: Rectilinear motion"
        ],
        "correctAnswer": "B",
        "explanation": "The tip of the second hand traces a circular path (circular motion), and the entire hand rotates about its fixed end (rotational motion). Both types are simultaneously present."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Water", "subTopic": "Water Cycle",
        "questionText": "During the water cycle, water vapour in clouds cools and condenses to form water droplets. This process releases latent heat. What effect does this released latent heat have?",
        "options": [
            "A: It cools the surrounding air further",
            "B: It warms the surrounding air, contributing to updrafts that sustain clouds",
            "C: It has no effect on surrounding air",
            "D: It causes immediate rainfall"
        ],
        "correctAnswer": "B",
        "explanation": "Condensation releases latent heat into the surrounding air. This warming creates upward air movement (updrafts) that carries more moisture upward, sustaining cloud formation and growth — a key mechanism in thunderstorm development."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Living Organisms", "subTopic": "Adaptation",
        "questionText": "A cactus stores water in its thick stem, has spines instead of leaves, and has a waxy coating. The PRIMARY function of the waxy coating is to:",
        "options": [
            "A: Protect against herbivores",
            "B: Reduce water loss through transpiration",
            "C: Absorb more sunlight for photosynthesis",
            "D: Improve wind resistance"
        ],
        "correctAnswer": "B",
        "explanation": "The waxy cuticle on a cactus stem acts as a waterproof barrier that minimises water loss through evaporation (transpiration). This is a key adaptation to the desert environment."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Air Around Us", "subTopic": "Composition of Air",
        "questionText": "A candle burns in a closed jar and goes out after some time. If the jar had a volume of 500 mL and approximately 21% was oxygen, and the candle consumed about 1/5 of the oxygen before going out, approximately how many mL of oxygen were consumed?",
        "options": ["A: 5 mL", "B: 10 mL", "C: 21 mL", "D: 100 mL"],
        "correctAnswer": "C",
        "explanation": "Total oxygen = 21% of 500 mL = 105 mL. The candle consumed 1/5 of the oxygen = 105 / 5 = 21 mL. Note: Candles typically go out when oxygen drops significantly, not all oxygen is used."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Food", "subTopic": "Nutrients and Balanced Diet",
        "questionText": "A child eats a meal of rice (carbohydrates), dal (protein), ghee (fat), orange (vitamin C), and milk (calcium). Which nutrient is MOST likely deficient in this meal for providing energy for immediate physical activity?",
        "options": [
            "A: Protein",
            "B: Fat",
            "C: Simple sugars (quick-release carbohydrates)",
            "D: Vitamin C"
        ],
        "correctAnswer": "C",
        "explanation": "Rice provides complex carbohydrates (slow-release energy). For immediate bursts of physical activity, simple sugars provide quick energy. The meal lacks quick-release carbohydrates like glucose or fructose found in fruits/sports drinks."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Magnets", "subTopic": "Magnetic Properties",
        "questionText": "Two bar magnets are placed end to end with their north poles facing each other. A small compass needle is placed exactly midway between them. In which direction will the compass needle point?",
        "options": [
            "A: Towards the north pole of magnet A",
            "B: Towards the north pole of magnet B",
            "C: Perpendicular to the line joining the magnets",
            "D: The needle will spin randomly — no stable direction"
        ],
        "correctAnswer": "D",
        "explanation": "Exactly midway between two north poles, the repulsive magnetic fields from both sides are equal and opposite, creating a point of zero field (magnetic null point). The compass needle has no net force to align it and will be unstable, spinning randomly."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Body Movements", "subTopic": "Types of Joints",
        "questionText": "A ball-and-socket joint allows movement in ALL directions. Which pair of locations in the human body BOTH have ball-and-socket joints?",
        "options": [
            "A: Elbow and knee",
            "B: Shoulder and hip",
            "C: Wrist and ankle",
            "D: Fingers and toes"
        ],
        "correctAnswer": "B",
        "explanation": "Both the shoulder (humerus in scapula socket) and the hip (femur head in pelvis socket) are ball-and-socket joints. Elbow and knee are hinge joints. Wrist and ankle are gliding joints."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Garbage In Garbage Out", "subTopic": "Decomposition and Composting",
        "questionText": "Vermicomposting uses earthworms to convert organic waste into compost. Which statement BEST explains why vermicompost is superior to chemical fertilisers for long-term soil health?",
        "options": [
            "A: Vermicompost contains nitrogen, phosphorus, and potassium like chemical fertilisers",
            "B: Vermicompost improves soil structure, moisture retention, and microbial activity — benefits chemical fertilisers do not provide",
            "C: Vermicompost is cheaper to produce",
            "D: Vermicompost kills pests in the soil"
        ],
        "correctAnswer": "B",
        "explanation": "Unlike chemical fertilisers which only add specific nutrients, vermicompost improves soil structure (aeration, water retention), introduces beneficial microorganisms, and provides slow-release nutrients — leading to long-term soil health improvement."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Fun with Magnets", "subTopic": "Electromagnets",
        "questionText": "An electromagnet is made by winding a coil around an iron nail and connecting it to a battery. If the number of turns in the coil is doubled (keeping current the same), what happens to the strength of the electromagnet?",
        "options": [
            "A: Strength halves",
            "B: Strength remains the same",
            "C: Strength approximately doubles",
            "D: Strength quadruples"
        ],
        "correctAnswer": "C",
        "explanation": "The magnetic field strength of an electromagnet is proportional to the number of turns (ampere-turns = N × I). Doubling the turns doubles the ampere-turns, approximately doubling the magnetic field strength."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Fibre to Fabric", "subTopic": "Natural and Synthetic Fibres",
        "questionText": "Cotton absorbs sweat and keeps the body cool in summer, while wool traps air and keeps the body warm in winter. The COMMON underlying reason for both properties is:",
        "options": [
            "A: Both are natural fibres",
            "B: Both have hollow or porous structures that interact differently with air and moisture",
            "C: Both come from living organisms",
            "D: Both are poor conductors of electricity"
        ],
        "correctAnswer": "B",
        "explanation": "Cotton's absorbent fibres wick moisture away and allow evaporation, cooling the body. Wool's crimped fibres trap still air (a poor heat conductor) creating insulation. Both effects arise from the porous/structured nature of the fibres and how they interact with air and moisture."
    },
    {
        "subject": "Science", "grade": 6, "difficulty": "Olympiad",
        "topic": "Electricity and Circuits", "subTopic": "Conductors and Insulators",
        "questionText": "Pure water (distilled water) does NOT conduct electricity well, but salt water (saline) conducts electricity. When salt water is electrolysed, chlorine gas is produced at one electrode. This tells us that electrical conduction in salt water is due to:",
        "options": [
            "A: Free electrons moving through the water",
            "B: Ions (charged particles) moving through the solution",
            "C: Heat generated by the current",
            "D: The electrodes themselves conducting"
        ],
        "correctAnswer": "B",
        "explanation": "Salt (NaCl) dissociates into Na⁺ and Cl⁻ ions in water. These ions carry the electric charge — Cl⁻ ions move to the anode and are discharged as Cl₂ gas. Distilled water lacks such ions, so it cannot conduct. This is ionic conduction, different from metallic (electron) conduction."
    },
]

# ─────────────────────────────────────────────────────────────
# SCIENCE G7 OLYMPIAD (15 questions)
# Topics: Physics, Chemistry, Biology at Olympiad level
# ─────────────────────────────────────────────────────────────
SCI7_OLY = [
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Heat", "subTopic": "Conduction, Convection, Radiation",
        "questionText": "A metal spoon and a wooden spoon of the same length and thickness are placed in a bowl of hot soup. After 5 minutes, the handle of the metal spoon feels much hotter. This is because metals have higher:",
        "options": [
            "A: Specific heat capacity",
            "B: Thermal conductivity",
            "C: Density",
            "D: Melting point"
        ],
        "correctAnswer": "B",
        "explanation": "Thermal conductivity measures how well a material conducts heat. Metals have high thermal conductivity — heat travels rapidly through the metal spoon to the handle. Wood has low thermal conductivity, so heat travels very slowly through the wooden spoon handle."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Light", "subTopic": "Reflection and Refraction",
        "questionText": "A ray of light travels from glass (denser medium, refractive index 1.5) into air (refractive index 1.0) at an angle of incidence of 30°. Using Snell's law (n₁sinθ₁ = n₂sinθ₂), what is the angle of refraction in air?",
        "options": ["A: 20°", "B: 30°", "C: 48.6°", "D: 90°"],
        "correctAnswer": "C",
        "explanation": "Snell's law: 1.5 × sin(30°) = 1.0 × sin(θ₂). 1.5 × 0.5 = sin(θ₂). sin(θ₂) = 0.75. θ₂ = sin⁻¹(0.75) ≈ 48.6°. Light bends away from the normal when going to a less dense medium."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Acids Bases and Salts", "subTopic": "pH Scale and Indicators",
        "questionText": "A solution turns red litmus blue and has a pH of 11. When excess HCl is added, the solution first becomes neutral (pH 7) and then acidic. At the point of neutralisation, the solution contains mainly:",
        "options": [
            "A: Sodium hydroxide and hydrochloric acid",
            "B: Salt and water only",
            "C: Salt, water, and excess base",
            "D: Only water"
        ],
        "correctAnswer": "B",
        "explanation": "At exact neutralisation (pH 7), acid and base have completely reacted: NaOH + HCl → NaCl + H₂O. The solution contains only salt (NaCl) and water. Adding more HCl after this point makes it acidic."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Physical and Chemical Changes", "subTopic": "Chemical Reactions",
        "questionText": "Iron filings are heated with sulphur powder to form iron sulphide (FeS). Which observation BEST proves this is a chemical change (not just a mixture)?",
        "options": [
            "A: The mixture becomes black",
            "B: The product FeS cannot be separated by a magnet, unlike the original iron filings",
            "C: Heat was needed to cause the change",
            "D: The sulphur melted during heating"
        ],
        "correctAnswer": "B",
        "explanation": "Iron filings are magnetic; sulphur is not. After forming FeS, the compound is NOT attracted to a magnet — proving a new substance with different properties has formed. This change in properties is definitive evidence of a chemical change."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Nutrition in Plants", "subTopic": "Photosynthesis",
        "questionText": "A variegated leaf (green and white patches) is tested for starch after keeping the plant in light. Only the green patches turn blue-black with iodine. The BEST conclusion is:",
        "options": [
            "A: White patches received less light",
            "B: White patches lack chlorophyll and cannot perform photosynthesis",
            "C: Iodine reacts only with green pigments",
            "D: White patches have no stomata for CO₂ intake"
        ],
        "correctAnswer": "B",
        "explanation": "White patches lack chlorophyll (the green pigment). Without chlorophyll to absorb light energy, photosynthesis cannot occur in those regions, so no starch is produced. This classic experiment demonstrates that chlorophyll is essential for photosynthesis."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Nutrition in Animals", "subTopic": "Digestive System",
        "questionText": "Bile produced by the liver does NOT contain any digestive enzymes. Yet bile is essential for fat digestion. The role of bile is to:",
        "options": [
            "A: Break down fat molecules chemically",
            "B: Emulsify fats — break large fat globules into smaller droplets to increase surface area for lipase action",
            "C: Neutralise stomach acid and provide an alkaline medium",
            "D: Both B and C"
        ],
        "correctAnswer": "D",
        "explanation": "Bile serves two key functions: (1) it emulsifies fats — converting large fat globules into fine droplets, massively increasing surface area for lipase to act on; and (2) it neutralises the acidic chyme from the stomach, creating the alkaline pH needed for small intestine enzymes to work."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Respiration in Organisms", "subTopic": "Aerobic and Anaerobic Respiration",
        "questionText": "During vigorous exercise, muscles switch from aerobic to anaerobic respiration and lactic acid builds up. What is the IMMEDIATE cause of the burning sensation and muscle fatigue?",
        "options": [
            "A: Depletion of oxygen in the muscles",
            "B: Accumulation of lactic acid, which lowers the pH in muscle cells",
            "C: Excess carbon dioxide in the bloodstream",
            "D: Depletion of glucose stores"
        ],
        "correctAnswer": "B",
        "explanation": "Lactic acid (C₃H₆O₃) is produced during anaerobic respiration: C₆H₁₂O₆ → 2C₃H₆O₃ + energy. The accumulation of lactic acid decreases the pH inside muscle cells, interfering with enzyme function and muscle contraction, causing the characteristic burning sensation and fatigue."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Transportation in Animals and Plants", "subTopic": "Blood and Circulatory System",
        "questionText": "Oxygenated blood flows from the heart to the body. Which sequence correctly traces the path of oxygenated blood from the lungs back to the body tissues?",
        "options": [
            "A: Lungs → Left atrium → Left ventricle → Aorta → Body",
            "B: Lungs → Right atrium → Right ventricle → Pulmonary artery → Body",
            "C: Lungs → Left ventricle → Left atrium → Aorta → Body",
            "D: Lungs → Right ventricle → Aorta → Body"
        ],
        "correctAnswer": "A",
        "explanation": "Oxygenated blood from the lungs flows via pulmonary veins → Left atrium → Left ventricle (pumped with great force) → Aorta → Body tissues. The right side of the heart handles deoxygenated blood going TO the lungs."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Forests — Our Lifeline", "subTopic": "Ecosystem and Biodiversity",
        "questionText": "Forests are called 'carbon sinks.' If a large area of forest is deforested and burned, what TWO processes simultaneously increase atmospheric CO₂?",
        "options": [
            "A: Increased evaporation and reduced rainfall",
            "B: Combustion of trees and loss of photosynthesis that was absorbing CO₂",
            "C: Soil erosion and increased runoff",
            "D: Decomposition of roots and increased wind"
        ],
        "correctAnswer": "B",
        "explanation": "Burning trees releases the carbon stored in wood as CO₂ (combustion). Simultaneously, the destroyed forest can no longer absorb CO₂ through photosynthesis (loss of carbon sink). Both effects increase net atmospheric CO₂, accelerating climate change."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Winds Storms and Cyclones", "subTopic": "Atmospheric Pressure and Winds",
        "questionText": "Cyclones (tropical storms) form only over warm ocean water (above 26°C). What is the PRIMARY energy source that drives a cyclone?",
        "options": [
            "A: Solar radiation directly heating the storm clouds",
            "B: Latent heat released when water vapour condenses inside the storm",
            "C: Earth's rotation providing rotational energy",
            "D: Pressure differences created by the cold stratosphere"
        ],
        "correctAnswer": "B",
        "explanation": "Warm ocean water evaporates rapidly, and as this moisture-laden air rises and cools, water vapour condenses into clouds and rain — releasing enormous amounts of latent heat. This heat energy warms the air further, causing it to rise faster, drawing in more warm moist air at the surface. This feedback loop is the engine of the cyclone."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Electric Current and its Effects", "subTopic": "Heating Effect and Fuse",
        "questionText": "An electric fuse is made of a thin wire with a low melting point. A 5A fuse is used in a circuit. If the current exceeds 5A, the fuse melts. The heating effect of current depends on I²R. If the current doubles (to 10A), by what factor does the heat generated change?",
        "options": ["A: 2 times", "B: 4 times", "C: 8 times", "D: 16 times"],
        "correctAnswer": "B",
        "explanation": "Heat generated H = I²Rt. If current doubles: H_new = (2I)²Rt = 4I²Rt = 4 × H_original. So heat generated increases by a factor of 4. This is why fuses blow much faster when current significantly exceeds the rated value."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Soil", "subTopic": "Soil Layers and Properties",
        "questionText": "Sandy soil has large particles and allows water to pass through quickly, while clay soil has tiny particles and retains water. Loam soil (a mixture of sand, silt, and clay) is BEST for agriculture because:",
        "options": [
            "A: It has the smallest particle size of all soil types",
            "B: It retains some moisture while also allowing excess water to drain and provides good aeration for roots",
            "C: It has the highest pH of all soil types",
            "D: It never needs irrigation"
        ],
        "correctAnswer": "B",
        "explanation": "Loam soil combines the best properties: the sand component allows drainage and aeration; the clay component retains sufficient moisture and nutrients; the silt provides a balance. This combination supports root growth, microbial activity, and plant nutrition — making it ideal for most crops."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Wastewater Story", "subTopic": "Sewage Treatment",
        "questionText": "In a sewage treatment plant, after physical screening and settling, 'activated sludge' (containing aerobic bacteria) is mixed with the sewage. The bacteria consume organic waste, lowering the BOD (Biological Oxygen Demand). A high BOD in river water indicates:",
        "options": [
            "A: Water is rich in oxygen — suitable for fish",
            "B: Water has high organic pollution — bacteria will consume dissolved oxygen, threatening aquatic life",
            "C: Water has high mineral content",
            "D: Water is highly acidic"
        ],
        "correctAnswer": "B",
        "explanation": "BOD measures the oxygen needed by microorganisms to decompose organic matter in water. High BOD means abundant organic pollutants. Bacteria breaking down this waste consume dissolved oxygen rapidly, causing oxygen depletion (hypoxia) — fish and other aquatic organisms suffocate and die."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Weather Climate and Adaptations", "subTopic": "Climate Zones and Animal Adaptations",
        "questionText": "The Arctic fox has white fur in winter and brown fur in summer. This seasonal colour change serves what PRIMARY survival advantage?",
        "options": [
            "A: White fur is warmer than brown fur",
            "B: Camouflage — white against snow in winter and brown against tundra in summer helps avoid predators and ambush prey",
            "C: White fur absorbs more sunlight to stay warm",
            "D: Brown fur repels insects in summer"
        ],
        "correctAnswer": "B",
        "explanation": "The Arctic fox's seasonal moult is an adaptation for camouflage. White fur blends with snow in winter (avoiding wolves, aiding prey ambush). Brown/grey fur matches the summer tundra. This is a classic example of seasonal adaptive colouration — a survival strategy driven by predator-prey dynamics."
    },
    {
        "subject": "Science", "grade": 7, "difficulty": "Olympiad",
        "topic": "Water — A Precious Resource", "subTopic": "Water Conservation and Management",
        "questionText": "Drip irrigation delivers water directly to plant roots through pipes with small holes. Compared to flood irrigation, drip irrigation can save up to 60% water. The PRIMARY reason for this efficiency is:",
        "options": [
            "A: Drip irrigation uses recycled water",
            "B: Drip irrigation reduces water loss through surface evaporation and runoff by delivering water precisely where needed",
            "C: Drip irrigation pumps water faster",
            "D: Drip irrigation adds fertilisers to the water"
        ],
        "correctAnswer": "B",
        "explanation": "Flood irrigation loses water through evaporation from large wet surfaces and runoff. Drip irrigation delivers water directly to the root zone in small, measured amounts — minimising evaporation (no large wet soil surface), eliminating runoff, and preventing water logging. This precision makes it 50-70% more efficient."
    },
]

# ─────────────────────────────────────────────────────────────
# HINDI G8 OLYMPIAD (15 questions)
# Topics: Prose, Poetry, Grammar, Writing — CBSE Class 8 Vasant
# ─────────────────────────────────────────────────────────────
HINDI8_OLY = [
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Vasant — Prose", "subTopic": "ध्वनि (कविता) — भाव और अर्थ",
        "questionText": "सूर्यकांत त्रिपाठी 'निराला' की कविता 'ध्वनि' में 'अभी न होगा मेरा अंत' — इस पंक्ति में कवि किस भाव को व्यक्त करता है?",
        "options": [
            "A: जीवन की नश्वरता का दुख",
            "B: जीवन के प्रति अटूट आशावाद और ऊर्जा का भाव",
            "C: प्रकृति के सौंदर्य का वर्णन",
            "D: ईश्वर से जीवन दान की प्रार्थना"
        ],
        "correctAnswer": "B",
        "explanation": "'अभी न होगा मेरा अंत' में कवि निराला ने वसंत के माध्यम से जीवन के प्रति गहरे आशावाद का भाव व्यक्त किया है। कवि कहता है कि वह अभी बहुत कुछ करना चाहता है — जीवन में शेष ऊर्जा से नई उमंग जगाना चाहता है।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Vasant — Prose", "subTopic": "लाख की चूड़ियाँ — चरित्र-चित्रण",
        "questionText": "'लाख की चूड़ियाँ' कहानी में बदलू का मानना था कि मशीन से बनी चूड़ियाँ हाथ से बनी चूड़ियों से कमतर हैं। यह विश्वास किस मूल्य को दर्शाता है?",
        "options": [
            "A: व्यापार की महत्ता",
            "B: हस्तशिल्प और व्यक्तिगत श्रम की गरिमा एवं परंपरा का सम्मान",
            "C: आधुनिकता का विरोध",
            "D: ग्रामीण जीवन की सरलता"
        ],
        "correctAnswer": "B",
        "explanation": "बदलू का दृढ़ विश्वास था कि हाथ से बनी लाख की चूड़ियों में भावना, कौशल और परंपरा होती है। मशीनी उत्पादन में ये नहीं होते। यह हस्तशिल्पियों की गरिमा और पारंपरिक कलाओं के सम्मान का प्रतीक है।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Grammar", "subTopic": "समास — भेद और उदाहरण",
        "questionText": "'राजपुत्र' में कौन-सा समास है और इसका सही विग्रह क्या है?",
        "options": [
            "A: तत्पुरुष समास — राजा का पुत्र",
            "B: द्वंद्व समास — राजा और पुत्र",
            "C: बहुव्रीहि समास — वह जो राजा का पुत्र है",
            "D: कर्मधारय समास — राजा रूपी पुत्र"
        ],
        "correctAnswer": "A",
        "explanation": "'राजपुत्र' में षष्ठी तत्पुरुष समास है — 'राजा का पुत्र'। इसमें प्रथम पद द्वितीय पद का विशेषण न होकर उससे संबंध-कारक संबंध रखता है।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Grammar", "subTopic": "वाच्य परिवर्तन",
        "questionText": "'राम ने आम खाया।' — इस कर्तृवाच्य वाक्य को कर्मवाच्य में बदलने पर सही वाक्य होगा:",
        "options": [
            "A: राम से आम खाया जाता है।",
            "B: राम द्वारा आम खाया गया।",
            "C: राम ने आम खाया था।",
            "D: आम को राम ने खाया।"
        ],
        "correctAnswer": "B",
        "explanation": "कर्मवाच्य में कर्म को प्रमुखता मिलती है। 'राम ने आम खाया' → 'राम द्वारा आम खाया गया।' कर्ता के साथ 'द्वारा' लगता है और क्रिया कर्म के अनुसार होती है।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Grammar", "subTopic": "मुहावरे और लोकोक्तियाँ",
        "questionText": "'नाकों चने चबाना' मुहावरे का सही अर्थ और उचित वाक्य-प्रयोग कौन-सा है?",
        "options": [
            "A: अर्थ: बहुत खाना — 'मोहन ने नाकों चने चबाए।'",
            "B: अर्थ: बहुत परेशान करना — 'दुश्मन ने सेना को नाकों चने चबवा दिए।'",
            "C: अर्थ: कठिन परिश्रम करना — 'उसने नाकों चने चबाकर परीक्षा पास की।'",
            "D: अर्थ: झूठ बोलना — 'उसने नाकों चने चबाकर कहानी सुनाई।'"
        ],
        "correctAnswer": "B",
        "explanation": "'नाकों चने चबाना' का अर्थ है — बहुत परेशान करना या नाकों दम करना। सही प्रयोग: 'दुश्मन ने सेना को नाकों चने चबवा दिए' — अर्थात दुश्मन ने सेना को बहुत परेशान किया।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Vasant — Poetry", "subTopic": "कबीर की साखियाँ — गूढ़ अर्थ",
        "questionText": "कबीर की साखी: 'बड़ा हुआ तो क्या हुआ, जैसे पेड़ खजूर। पंछी को छाया नहीं, फल लागे अति दूर।' — इस दोहे में कबीर किस पर व्यंग्य कर रहे हैं?",
        "options": [
            "A: खजूर के पेड़ की ऊँचाई पर",
            "B: उन महान लोगों पर जो दूसरों के किसी काम न आएँ",
            "C: धन-संपदा की निरर्थकता पर",
            "D: पक्षियों की स्वच्छंदता पर"
        ],
        "correctAnswer": "B",
        "explanation": "कबीर कहते हैं — केवल बड़ा होने से क्या लाभ? जैसे खजूर का पेड़ ऊँचा तो होता है, पर न उसकी छाया में कोई बैठ सकता है और न उसके फल आसानी से मिलते हैं। व्यंग्य उन लोगों पर है जो ऊँचे पद पर हों, पर दूसरों के कोई काम न आएँ।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Vasant — Prose", "subTopic": "बस की यात्रा — व्यंग्य",
        "questionText": "हरिशंकर परसाई की 'बस की यात्रा' में लेखक बस की जर्जर हालत का वर्णन करते हुए भी व्यंग्य करते हैं। इस पाठ का मुख्य व्यंग्य किस पर है?",
        "options": [
            "A: यात्रियों की लापरवाही पर",
            "B: सड़क परिवहन व्यवस्था की खराब दशा और प्रशासन की उदासीनता पर",
            "C: ग्रामीण जीवन की सरलता पर",
            "D: बस चालक की कुशलता पर"
        ],
        "correctAnswer": "B",
        "explanation": "परसाई ने जर्जर बस, टूटे पुर्जों और खतरनाक यात्रा के माध्यम से सरकारी परिवहन व्यवस्था और प्रशासन की उदासीनता पर तीखा व्यंग्य किया है। यह पाठ व्यंग्य-विधा का उत्कृष्ट उदाहरण है।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Grammar", "subTopic": "अलंकार — पहचान और प्रयोग",
        "questionText": "'मखमल के झूल पड़े हाथी-सा टीला' — इस पंक्ति में कौन-सा अलंकार है?",
        "options": [
            "A: उपमा अलंकार",
            "B: रूपक अलंकार",
            "C: अनुप्रास अलंकार",
            "D: उत्प्रेक्षा अलंकार"
        ],
        "correctAnswer": "A",
        "explanation": "इस पंक्ति में 'टीला' की तुलना 'हाथी' से 'सा' वाचक शब्द के द्वारा की गई है — यह उपमा अलंकार है। उपमा में: उपमेय (टीला), उपमान (हाथी), वाचक शब्द (सा), और साधारण धर्म (झूल पड़े होना) — सभी स्पष्ट हैं।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Vasant — Prose", "subTopic": "दीवानों की हस्ती — भाव-बोध",
        "questionText": "भगवती चरण वर्मा की कविता 'दीवानों की हस्ती' में कवि 'दीवानों' से किस प्रकार के लोगों का बोध कराता है?",
        "options": [
            "A: मानसिक रूप से अस्थिर लोग",
            "B: निर्मोही, निर्भय और आनंदमय जीवन जीने वाले फक्कड़ और उन्मुक्त लोग",
            "C: धन-लोलुप और स्वार्थी लोग",
            "D: सांसारिक मोह से ग्रस्त लोग"
        ],
        "correctAnswer": "B",
        "explanation": "'दीवानों की हस्ती' में कवि उन लोगों की बात करता है जो संसार के सुख-दुख में डूबे-उतराए बिना आनंद से जीते हैं। वे निर्मोही (आसक्तिरहित), उन्मुक्त, फक्कड़ और प्रकृति की तरह बहने वाले हैं — उनका जीवन ही उनकी संपदा है।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Grammar", "subTopic": "संधि-विच्छेद",
        "questionText": "'विद्यालय' का सही संधि-विच्छेद और संधि का प्रकार क्या है?",
        "options": [
            "A: विद्या + आलय — दीर्घ स्वर संधि",
            "B: विद्या + लय — यण संधि",
            "C: विद् + यालय — व्यंजन संधि",
            "D: विद्या + अलय — गुण संधि"
        ],
        "correctAnswer": "A",
        "explanation": "'विद्यालय' = विद्या + आलय। 'आ' + 'आ' = 'आ' — यह दीर्घ स्वर संधि है। दो समान स्वर (आ + आ) मिलकर दीर्घ स्वर 'आ' बनाते हैं।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Vasant — Prose", "subTopic": "भगवान के डाकिए — प्रतीकात्मकता",
        "questionText": "रामधारी सिंह 'दिनकर' की कविता 'भगवान के डाकिए' में पक्षी और बादल 'डाकिए' के रूप में किस संदेश के प्रतीक हैं?",
        "options": [
            "A: प्राकृतिक आपदाओं का संदेश",
            "B: सीमाओं से परे मानवीय एकता, प्रेम और भाईचारे का संदेश",
            "C: देशभक्ति और राष्ट्रीय एकता का संदेश",
            "D: ईश्वर की महानता का संदेश"
        ],
        "correctAnswer": "B",
        "explanation": "दिनकर ने पक्षियों और बादलों को 'भगवान के डाकिए' कहा है जो देशों की सीमाओं को नहीं मानते और प्रेम, सुगंध, और वर्षा का संदेश सब तक पहुँचाते हैं। यह मानवीय एकता और विश्व-बंधुत्व का प्रतीक है।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Writing Skills", "subTopic": "अनुच्छेद-लेखन",
        "questionText": "एक प्रभावी अनुच्छेद की संरचना में निम्नलिखित में से कौन-सा तत्त्व सबसे महत्त्वपूर्ण है?",
        "options": [
            "A: अनुच्छेद में अधिक-से-अधिक उदाहरण देना",
            "B: विषय वाक्य (topic sentence), विस्तार वाक्य, और निष्कर्ष वाक्य का क्रमबद्ध होना",
            "C: लंबे और जटिल वाक्यों का प्रयोग",
            "D: अनुच्छेद में तुकबंदी करना"
        ],
        "correctAnswer": "B",
        "explanation": "एक प्रभावी अनुच्छेद में: (1) विषय वाक्य — मुख्य विचार प्रस्तुत करता है; (2) विस्तार वाक्य — तर्क, उदाहरण और व्याख्या; (3) निष्कर्ष वाक्य — विचार को पूर्ण करता है। यह त्रिस्तरीय संरचना अनुच्छेद को स्पष्ट और प्रभावी बनाती है।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Vasant — Prose", "subTopic": "सुदामा चरित — भक्ति और मित्रता",
        "questionText": "नरोत्तम दास के 'सुदामा चरित' में कृष्ण और सुदामा की मित्रता किस मूल्य की श्रेष्ठता को उजागर करती है?",
        "options": [
            "A: धन की महत्ता",
            "B: निश्छल प्रेम और सच्ची मित्रता, जिसमें ऊँच-नीच का भेद नहीं",
            "C: भक्ति से ईश्वर को प्राप्त करने का मार्ग",
            "D: विद्या और ज्ञान की श्रेष्ठता"
        ],
        "correctAnswer": "B",
        "explanation": "सुदामा निर्धन ब्राह्मण और कृष्ण राजा थे — फिर भी कृष्ण ने सुदामा के साथ वही प्रेम और आदर दिखाया जो बचपन में था। यह पाठ निश्छल मित्रता और सामाजिक भेद-भाव से परे प्रेम का संदेश देता है।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Grammar", "subTopic": "काल — भेद और प्रयोग",
        "questionText": "'यदि वर्षा होती, तो फसल अच्छी होती।' — इस वाक्य में कौन-सा काल है और इसकी विशेषता क्या है?",
        "options": [
            "A: सामान्य भूतकाल — बीती हुई घटना",
            "B: हेतुहेतुमद् भूतकाल — जो शर्त पूरी न हुई उसका परिणाम",
            "C: संभाव्य वर्तमान काल — संभावना",
            "D: भविष्यकाल — आनेवाली घटना"
        ],
        "correctAnswer": "B",
        "explanation": "यह हेतुहेतुमद् भूतकाल (Conditional Past) है — जिसमें एक शर्त और उसका संभावित परिणाम दोनों भूतकाल में होते हैं, लेकिन वास्तव में शर्त पूरी नहीं हुई। 'यदि वर्षा होती (शर्त) → तो फसल अच्छी होती (परिणाम)' — वर्षा नहीं हुई इसलिए फसल भी अच्छी नहीं हुई।"
    },
    {
        "subject": "Hindi", "grade": 8, "difficulty": "Olympiad",
        "topic": "Vasant — Prose", "subTopic": "पानी की कहानी — वैज्ञानिक दृष्टि",
        "questionText": "'पानी की कहानी' पाठ में पानी अपनी आत्मकथा सुनाता है। पानी के अणु का वह गुण जो बताता है कि पानी उच्च तापमान पर भी बड़ी मात्रा में वाष्पित नहीं होता, वह है:",
        "options": [
            "A: कम घनत्व",
            "B: उच्च विशिष्ट ऊष्मा क्षमता (high specific heat capacity)",
            "C: पारदर्शिता",
            "D: बिना रंग का होना"
        ],
        "correctAnswer": "B",
        "explanation": "जल की उच्च विशिष्ट ऊष्मा क्षमता (4200 J/kg/°C) के कारण इसे गर्म करने में बहुत ऊर्जा लगती है और यह धीरे-धीरे ठंडा होता है। इसीलिए समुद्र, नदियाँ और मानव शरीर का तापमान स्थिर रहता है — यह जीवन के लिए महत्त्वपूर्ण है।"
    },
]

# ─────────────────────────────────────────────────────────────
# GENERAL KNOWLEDGE G9 ADVANCED (15 questions)
# ─────────────────────────────────────────────────────────────
GK9_ADV = [
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Science and Technology", "subTopic": "Space Missions",
        "questionText": "India's Chandrayaan-3 successfully landed on the Moon in August 2023. Where exactly did it land and what was the significance of that location?",
        "options": [
            "A: Near Sea of Tranquility — where Apollo 11 landed",
            "B: Near the lunar south pole — significant because of the possible presence of water ice in permanently shadowed craters",
            "C: On the lunar equator — to maximise sunlight for solar panels",
            "D: Near the lunar north pole — to study polar ice caps"
        ],
        "correctAnswer": "B",
        "explanation": "Chandrayaan-3's Vikram lander touched down near the lunar south pole (around 70°S) on 23 August 2023. India became the first country to land near the lunar south pole. The significance: permanently shadowed craters there may contain water ice — a crucial resource for future lunar missions and habitation."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Indian History", "subTopic": "Independence Movement",
        "questionText": "The Dandi March (Salt March) of 1930 was a pivotal event in India's freedom movement. Why was salt specifically chosen as the subject of civil disobedience?",
        "options": [
            "A: Salt was the most valuable commodity in British India",
            "B: The British salt tax affected every Indian regardless of class or income — making it the most unifying issue",
            "C: Salt production was entirely controlled by the British East India Company",
            "D: Gandhi chose salt because it was his personal symbol of purity"
        ],
        "correctAnswer": "B",
        "explanation": "Gandhi chose salt because the British monopoly on salt and the salt tax affected every single Indian — rich, poor, urban, rural. Salt is a basic necessity of life that everyone needs. By challenging this, Gandhi united all classes in one act of civil disobedience — making it the most powerful symbol of resistance to colonial rule."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Geography", "subTopic": "Indian Geography",
        "questionText": "The Western Ghats and Eastern Ghats are both mountain ranges on the Indian Peninsula. What is a key difference between the rivers originating from each?",
        "options": [
            "A: Western Ghats rivers flow east to the Bay of Bengal; Eastern Ghats rivers flow west to the Arabian Sea",
            "B: Western Ghats rivers are generally shorter and flow west to the Arabian Sea; Eastern Ghats rivers flow east to the Bay of Bengal and are longer",
            "C: Both flow to the Bay of Bengal",
            "D: Western Ghats rivers are longer than Eastern Ghats rivers"
        ],
        "correctAnswer": "B",
        "explanation": "The Western Ghats are a steep western escarpment close to the Arabian Sea, so rivers on their western side are short and swift (Mandovi, Zuari, Periyar). Major rivers like Godavari, Krishna, and Kaveri originate in the Western Ghats but flow eastward across the Deccan plateau to the Bay of Bengal — they are much longer."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Science", "subTopic": "Environment",
        "questionText": "The 'Great Pacific Garbage Patch' is a famous example of ocean pollution. What does it primarily consist of?",
        "options": [
            "A: Large pieces of discarded fishing nets and plastic bottles visible from space",
            "B: Microplastics — tiny plastic fragments less than 5mm, mostly invisible to the naked eye",
            "C: Industrial chemical waste from Pacific Rim countries",
            "D: Radioactive waste from nuclear submarine operations"
        ],
        "correctAnswer": "B",
        "explanation": "Contrary to popular imagination, the Great Pacific Garbage Patch is not a solid island of visible garbage. It is primarily composed of microplastics — plastic items that have broken down into tiny fragments through UV radiation and wave action. These microplastics are suspended throughout the water column, not just on the surface, and are ingested by marine life."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Current Affairs", "subTopic": "Indian Economy",
        "questionText": "India's GDP growth rate has consistently been among the highest globally. Which sector contributes the LARGEST share to India's GDP currently?",
        "options": [
            "A: Agriculture (farming, forestry, fishing)",
            "B: Industry (manufacturing, construction, mining)",
            "C: Services (IT, banking, trade, transport)",
            "D: Government expenditure"
        ],
        "correctAnswer": "C",
        "explanation": "India's Services sector contributes about 55-60% of GDP, making it the dominant sector. IT/software services, banking, financial services, retail trade, transport, and tourism are key components. Despite India's agricultural heritage, services have been the primary growth driver since the 1990s liberalisation."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Science", "subTopic": "Human Body",
        "questionText": "The human body has about 37 trillion cells. Every second, about 2-3 million red blood cells are produced. Where are red blood cells produced in adults?",
        "options": [
            "A: In the liver", "B: In the spleen", "C: In the red bone marrow", "D: In the lymph nodes"
        ],
        "correctAnswer": "C",
        "explanation": "In adults, red blood cells (and other blood cells) are produced in the red bone marrow, primarily in flat bones like the sternum, pelvis, ribs, vertebrae, and skull. In foetuses, the liver and spleen also produce blood cells, but this function shifts to bone marrow after birth."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "World Geography", "subTopic": "Continents and Countries",
        "questionText": "Which country is the world's largest by land area, and which is the most populous?",
        "options": [
            "A: Russia (largest area); China (most populous)",
            "B: Russia (largest area); India (most populous)",
            "C: Canada (largest area); China (most populous)",
            "D: China (largest area); India (most populous)"
        ],
        "correctAnswer": "B",
        "explanation": "Russia is the world's largest country by land area at 17.1 million km². India surpassed China in 2023 to become the world's most populous nation with approximately 1.44 billion people, compared to China's 1.41 billion."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Indian Constitution", "subTopic": "Fundamental Rights",
        "questionText": "The Right to Education (RTE) Act 2009 makes education compulsory for children aged 6-14 under which Fundamental Right?",
        "options": [
            "A: Right to Equality (Article 14)",
            "B: Right against Exploitation (Article 23)",
            "C: Right to Life and Personal Liberty (Article 21A)",
            "D: Right to Freedom (Article 19)"
        ],
        "correctAnswer": "C",
        "explanation": "The 86th Constitutional Amendment (2002) inserted Article 21A, making free and compulsory education a Fundamental Right for children aged 6-14. The Right to Education Act (2009) operationalised this right. Article 21A was added to expand the scope of the Right to Life under Article 21."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Science", "subTopic": "Inventions and Discoveries",
        "questionText": "CRISPR-Cas9 is a revolutionary technology that allows scientists to edit DNA. It was developed based on a natural mechanism found in:",
        "options": [
            "A: Viruses — as part of their replication machinery",
            "B: Bacteria — as an immune defence system against viral infections",
            "C: Human cells — as a DNA repair mechanism",
            "D: Yeast — used in fermentation research"
        ],
        "correctAnswer": "B",
        "explanation": "CRISPR (Clustered Regularly Interspaced Short Palindromic Repeats) is a natural immune system found in bacteria. Bacteria incorporate snippets of viral DNA into their own genome; when the virus attacks again, the CRISPR system identifies it and the Cas9 protein cuts the viral DNA. Scientists harnessed this mechanism for precise gene editing. Jennifer Doudna and Emmanuelle Charpentier won the 2020 Nobel Prize in Chemistry for this."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Indian Culture", "subTopic": "Classical Arts",
        "questionText": "UNESCO designated Yoga as part of the Intangible Cultural Heritage of Humanity in which year?",
        "options": ["A: 2010", "B: 2014", "C: 2016", "D: 2019"],
        "correctAnswer": "C",
        "explanation": "UNESCO inscribed Yoga on its Representative List of the Intangible Cultural Heritage of Humanity in December 2016. The International Day of Yoga (21 June) had been established by the UN General Assembly in 2014 following India's proposal, first observed in 2015."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Sports", "subTopic": "Indian Sports Achievements",
        "questionText": "Neeraj Chopra won India's first-ever gold medal in track and field at the Olympics. In which event and at which Olympics did he achieve this?",
        "options": [
            "A: Shot put — Tokyo 2020",
            "B: Javelin throw — Tokyo 2020",
            "C: Javelin throw — Paris 2024",
            "D: Discus throw — Tokyo 2020"
        ],
        "correctAnswer": "B",
        "explanation": "Neeraj Chopra won gold in the men's javelin throw at the Tokyo 2020 Olympics (held in 2021) with a throw of 87.58 metres. This was India's first-ever gold medal in an Olympic track and field event and only India's second individual gold (after Abhinav Bindra in 2008). He also won silver at Paris 2024."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "World History", "subTopic": "Modern History",
        "questionText": "The United Nations was founded in 1945. How many countries were original founding members?",
        "options": ["A: 30", "B: 51", "C: 60", "D: 193"],
        "correctAnswer": "B",
        "explanation": "The United Nations was established on 24 October 1945 with 51 founding member states. Today it has 193 member states. The UN replaced the earlier League of Nations (founded after WWI) and was created after WWII to maintain international peace and security."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Science", "subTopic": "Chemistry in Everyday Life",
        "questionText": "Rusting of iron is an electrochemical process requiring oxygen and water. Which condition would MOST effectively prevent rusting of an iron bridge?",
        "options": [
            "A: Painting the iron surface",
            "B: Attaching a block of zinc to the iron (cathodic protection / sacrificial anode)",
            "C: Storing the bridge in a dry environment",
            "D: Using a thicker iron alloy"
        ],
        "correctAnswer": "B",
        "explanation": "Cathodic protection uses a more reactive metal (zinc or magnesium) attached to the iron. Zinc acts as the 'sacrificial anode' — it corrodes preferentially (oxidises instead of iron), keeping the iron cathodic (protected). This is used widely for bridges, ship hulls, and underground pipelines. Painting also helps but fails when scratched; cathodic protection works even with surface damage."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Technology", "subTopic": "Digital India",
        "questionText": "UPI (Unified Payments Interface) was launched in India in 2016. Which organisation developed and governs UPI?",
        "options": [
            "A: Reserve Bank of India (RBI)",
            "B: National Payments Corporation of India (NPCI)",
            "C: Ministry of Electronics and IT",
            "D: State Bank of India"
        ],
        "correctAnswer": "B",
        "explanation": "UPI was developed by the National Payments Corporation of India (NPCI) and launched in April 2016. The RBI regulates payments systems, and the Ministry of Finance oversees financial policy, but NPCI (a non-profit organisation set up by RBI and Indian Banks' Association) created and manages UPI. India now processes more UPI transactions than all credit card transactions globally."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Advanced",
        "topic": "Environment", "subTopic": "Conservation",
        "questionText": "Project Tiger was launched in India in 1973. What is the CURRENT approximate tiger population in India according to the 2022 census?",
        "options": ["A: About 800", "B: About 1200", "C: About 3,167", "D: About 5,000"],
        "correctAnswer": "C",
        "explanation": "According to the 2022 All-India Tiger Estimation (released in 2023), India has approximately 3,167 tigers — the largest population in the world. This is a remarkable conservation success from just 1,827 in 2014 and about 1,400 in 1973 when Project Tiger was launched. India hosts about 75% of the world's wild tigers."
    },
]

# ─────────────────────────────────────────────────────────────
# GENERAL KNOWLEDGE G9 OLYMPIAD (15 questions)
# ─────────────────────────────────────────────────────────────
GK9_OLY = [
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Science", "subTopic": "Physics — Special Relativity",
        "questionText": "Einstein's Special Theory of Relativity predicts that as an object moves faster, time passes more slowly for it compared to a stationary observer. This is called time dilation. A spacecraft travels at 90% the speed of light. Compared to a clock on Earth, the spacecraft's clock runs:",
        "options": [
            "A: At the same rate",
            "B: Faster than Earth's clock",
            "C: Slower than Earth's clock (time dilation)",
            "D: Randomly faster or slower"
        ],
        "correctAnswer": "C",
        "explanation": "According to Special Relativity, moving clocks run slow — time dilation. The time dilation factor (Lorentz factor γ) at 90% the speed of light is about 2.3, meaning the spacecraft's clock runs at roughly 1/2.3 ≈ 43% the rate of Earth's clock. This is not theoretical — GPS satellites must account for relativistic time corrections or navigation errors would accumulate rapidly."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Science", "subTopic": "Biology — Genetics",
        "questionText": "In Mendelian genetics, a tall pea plant (TT) is crossed with a short pea plant (tt). In the F1 generation all plants are tall (Tt). When F1 plants are self-crossed, what ratio of tall to short plants is expected in F2?",
        "options": ["A: 1:1", "B: 2:1", "C: 3:1", "D: 4:0"],
        "correctAnswer": "C",
        "explanation": "F1 plants are all Tt (tall, as T is dominant). F1 × F1: TT : Tt : tt = 1:2:1. TT and Tt are phenotypically tall; tt is short. So phenotypic ratio = 3 tall : 1 short. This 3:1 ratio is Mendel's Law of Segregation in action — the foundation of classical genetics."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "World History", "subTopic": "Cold War",
        "questionText": "The Cuban Missile Crisis (1962) brought the world closest to nuclear war. What was the CORE cause of the crisis?",
        "options": [
            "A: Cuba invaded Florida",
            "B: The USSR placed nuclear missiles in Cuba, 90 miles from the US",
            "C: The US blockaded Soviet ships in the Atlantic",
            "D: Cuba tested its own nuclear weapon"
        ],
        "correctAnswer": "B",
        "explanation": "The Soviet Union, under Khrushchev, secretly deployed nuclear-armed ballistic missiles in Cuba — just 90 miles from Florida. US spy planes discovered them in October 1962. The 13-day crisis saw Kennedy's naval blockade and Soviet-US negotiations. It ended when the USSR removed missiles from Cuba in exchange for a US pledge not to invade Cuba and removal of US missiles from Turkey."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Science and Technology", "subTopic": "Artificial Intelligence",
        "questionText": "Large Language Models (LLMs) like GPT-4 are trained using a method where the model predicts the next word in a sequence across billions of text samples. This training approach is called:",
        "options": [
            "A: Supervised classification learning",
            "B: Reinforcement learning from human feedback (RLHF) only",
            "C: Self-supervised learning (predicting masked or next tokens)",
            "D: Unsupervised clustering"
        ],
        "correctAnswer": "C",
        "explanation": "LLMs use self-supervised learning — the model is trained to predict the next token (word/subword) given preceding context, using the text itself as the label. No human labelling of each sample is needed. This allows training on massive internet-scale datasets. RLHF (reinforcement learning from human feedback) is an additional fine-tuning step applied after the base training."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Indian History", "subTopic": "Post-Independence",
        "questionText": "Operation Blue Star (1984) was a military operation carried out in which city, and what was its primary objective?",
        "options": [
            "A: Mumbai — to suppress a communist uprising",
            "B: Amritsar — to remove armed militants who had occupied the Golden Temple",
            "C: Delhi — to protect Parliament from a terrorist attack",
            "D: Jammu — to counter Pakistani infiltration"
        ],
        "correctAnswer": "B",
        "explanation": "Operation Blue Star (June 1984) was ordered by Prime Minister Indira Gandhi to remove Sikh militant leader Jarnail Singh Bhindranwale and his armed followers from the Harmandir Sahib (Golden Temple) complex in Amritsar. The operation resulted in significant casualties and damage to the holy shrine, and contributed to the political tensions that led to Indira Gandhi's assassination in October 1984."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Science", "subTopic": "Chemistry — Elements",
        "questionText": "The element oganesson (Og, atomic number 118) is the heaviest known element and a noble gas. Yet scientists believe it may NOT behave like other noble gases. Why?",
        "options": [
            "A: It has an even atomic number",
            "B: Relativistic effects on its electron orbitals may make its outermost electrons more accessible for bonding",
            "C: It is radioactive",
            "D: It has too many protons to form a stable nucleus"
        ],
        "correctAnswer": "B",
        "explanation": "For superheavy elements, electrons near the nucleus travel at relativistic speeds (significant fraction of c). This causes relativistic orbital contraction and expansion effects, altering electron shell energies. For oganesson, relativistic effects may cause the outermost 7p electrons to be less tightly held in their shells, potentially allowing chemical bonding — unlike lighter noble gases that have completely filled, non-reactive shells."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Economics", "subTopic": "Global Economy",
        "questionText": "The BRICS grouping (originally Brazil, Russia, India, China, South Africa) expanded in 2024. What is the PRIMARY purpose/objective of BRICS?",
        "options": [
            "A: To create a military alliance against NATO",
            "B: To promote cooperation among major emerging economies and reform global governance institutions",
            "C: To establish a common currency to replace the US dollar",
            "D: To create a free trade zone among member nations"
        ],
        "correctAnswer": "B",
        "explanation": "BRICS is a forum for major emerging economies to coordinate on economic growth, political issues, and reform of global governance bodies like the IMF and World Bank (which they argue are dominated by Western interests). While some members discuss de-dollarisation, there is no formal common currency. In 2024, Saudi Arabia, UAE, Egypt, Ethiopia, and Iran joined as full members, expanding BRICS to 10 nations."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Science", "subTopic": "Space Science",
        "questionText": "A black hole's 'event horizon' is the boundary beyond which nothing, not even light, can escape. The radius of the event horizon (Schwarzschild radius) for a mass M is given by r = 2GM/c². If a black hole has a mass of 10 solar masses, its Schwarzschild radius would be approximately:",
        "options": ["A: 3 km", "B: 30 km", "C: 300 km", "D: 3,000 km"],
        "correctAnswer": "B",
        "explanation": "The Schwarzschild radius for one solar mass is approximately 3 km. For 10 solar masses, it is 10 × 3 = 30 km. So a black hole 10 times more massive than our Sun would have an event horizon of just 30 km radius — smaller than a city! For reference, the Sun itself has a radius of about 700,000 km."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Indian Constitution", "subTopic": "Parliament and Governance",
        "questionText": "India has a bicameral Parliament consisting of Lok Sabha and Rajya Sabha. In which situation does the Rajya Sabha have EQUAL powers with the Lok Sabha?",
        "options": [
            "A: Passing the Union Budget (Money Bills)",
            "B: A vote of no-confidence against the government",
            "C: Passing Constitutional Amendment Bills (under Article 368)",
            "D: Electing the Prime Minister"
        ],
        "correctAnswer": "C",
        "explanation": "Constitutional Amendment Bills (Article 368) must be passed by a special majority in BOTH Houses separately — Rajya Sabha has equal power here. Money Bills originate only in Lok Sabha and Rajya Sabha can only suggest amendments. Votes of no-confidence are only in Lok Sabha. The President is elected by an electoral college, and PM is appointed by President but must have LS majority."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Science", "subTopic": "Medicine and Health",
        "questionText": "mRNA vaccines (like those developed against COVID-19) work differently from traditional vaccines. The key innovation is that they:",
        "options": [
            "A: Inject weakened virus particles to train the immune system",
            "B: Deliver instructions (mRNA) to cells to produce a viral protein, which then triggers an immune response — without using any viral material",
            "C: Use killed virus proteins directly injected into the bloodstream",
            "D: Modify the patient's DNA to produce antibodies"
        ],
        "correctAnswer": "B",
        "explanation": "mRNA vaccines contain messenger RNA encoding a viral protein (e.g., the COVID-19 spike protein). Human cells read this mRNA and produce the protein. The immune system recognises the foreign protein and develops antibodies. Crucially: no virus is used, the mRNA is temporary and does NOT integrate into DNA (mRNA never enters the cell nucleus), and the body's own cells do the protein manufacturing."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Environment", "subTopic": "Climate Science",
        "questionText": "The 'tipping points' in climate science refer to thresholds where small changes cause large, irreversible shifts in climate systems. Which of the following is NOT considered a climate tipping point?",
        "options": [
            "A: Collapse of the West Antarctic Ice Sheet",
            "B: Thawing of Arctic permafrost releasing methane",
            "C: Dieback of the Amazon rainforest",
            "D: Gradual increase in global average temperature by 0.1°C"
        ],
        "correctAnswer": "D",
        "explanation": "Climate tipping points involve abrupt, self-reinforcing changes: Arctic permafrost thaw releases methane (a powerful greenhouse gas) accelerating warming; Amazon dieback destroys rainfall patterns; ice sheet collapse raises sea levels irreversibly. A gradual 0.1°C temperature rise is a linear change, not a tipping point — tipping points involve non-linear, runaway changes once a threshold is crossed."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "World Affairs", "subTopic": "International Relations",
        "questionText": "The International Court of Justice (ICJ) and the International Criminal Court (ICC) are both based in The Hague, Netherlands. What is the key DIFFERENCE between them?",
        "options": [
            "A: ICJ handles disputes between nations; ICC prosecutes individuals for war crimes, crimes against humanity, and genocide",
            "B: ICJ prosecutes terrorists; ICC handles trade disputes",
            "C: ICJ is a UN organ; ICC handles environmental violations",
            "D: They are the same institution with different names"
        ],
        "correctAnswer": "A",
        "explanation": "The ICJ (International Court of Justice) is the principal judicial organ of the UN — it settles legal disputes BETWEEN STATES (e.g., border disputes, treaty violations). The ICC (International Criminal Court) is an independent treaty-based court that prosecutes INDIVIDUALS for the most serious international crimes: genocide, crimes against humanity, war crimes, and the crime of aggression."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Science", "subTopic": "Nuclear Physics",
        "questionText": "Nuclear fission (used in power plants) and nuclear fusion (energy source of the Sun) both release energy. Which statement correctly explains WHY both release energy?",
        "options": [
            "A: Both convert matter directly to energy via E=mc² — the products have less mass than the reactants, and the 'missing mass' becomes energy",
            "B: Fission releases chemical energy; fusion releases nuclear energy",
            "C: Both processes produce radioactive waste which generates heat",
            "D: Both reactions require a catalyst and release the catalyst's stored energy"
        ],
        "correctAnswer": "A",
        "explanation": "In nuclear reactions, the total mass of products is LESS than the total mass of reactants. This mass defect (Δm) is converted to energy according to E = Δmc². In fission, heavy nuclei (like U-235) split into lighter fragments with less total mass. In fusion, light nuclei (hydrogen isotopes) combine to form helium with less total mass. Both release enormous energy because c² is an enormous number (≈9×10¹⁶ m²/s²)."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Indian Economy", "subTopic": "Economic Reforms",
        "questionText": "India's 1991 economic reforms (LPG reforms) were triggered by a balance of payments crisis. 'LPG' stands for Liberalisation, Privatisation, Globalisation. Which economist served as Finance Minister and was instrumental in implementing these reforms?",
        "options": [
            "A: Pranab Mukherjee",
            "B: P. Chidambaram",
            "C: Manmohan Singh",
            "D: Arun Jaitley"
        ],
        "correctAnswer": "C",
        "explanation": "Dr. Manmohan Singh served as Finance Minister in 1991 under PM Narasimha Rao and was the primary architect of India's economic reforms. He presented the landmark budget of 1991 that introduced liberalisation (reducing licences and regulations), privatisation (opening public sector to private firms), and globalisation (integrating India with world trade). He later served as Prime Minister from 2004-2014."
    },
    {
        "subject": "General Knowledge", "grade": 9, "difficulty": "Olympiad",
        "topic": "Science", "subTopic": "Quantum Physics",
        "questionText": "Schrödinger's Cat is a thought experiment in quantum mechanics. It illustrates the concept of quantum superposition — where a quantum system exists in multiple states simultaneously until observed. This principle challenges which classical assumption?",
        "options": [
            "A: That cats can survive in boxes",
            "B: That physical objects have definite properties (like alive/dead) independent of observation",
            "C: That radioactive decay is unpredictable",
            "D: That quantum systems are always larger than classical ones"
        ],
        "correctAnswer": "B",
        "explanation": "Classical physics assumes objects have definite states independent of observation (realism). Quantum mechanics says particles exist in superpositions of states — only collapsing to one state upon measurement. Schrödinger's thought experiment illustrates the absurdity of applying this quantum principle to macroscopic objects: a cat in a box is neither definitely alive nor dead until observed. It challenges classical realism at the quantum level."
    },
]

# ─────────────────────────────────────────────────────────────
# SCIENCE G9 FOUNDATION (15 questions)
# Topics: Basic concepts across Physics, Chemistry, Biology
# ─────────────────────────────────────────────────────────────
SCI9_FOUND = [
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Matter in Our Surroundings", "subTopic": "States of Matter",
        "questionText": "Which of the following is a property of gases?",
        "options": [
            "A: Fixed shape and fixed volume",
            "B: Fixed volume but no fixed shape",
            "C: No fixed shape and no fixed volume",
            "D: High density and incompressible"
        ],
        "correctAnswer": "C",
        "explanation": "Gases have no fixed shape (they take the shape of their container) and no fixed volume (they expand to fill the entire container). Gas particles have very weak intermolecular forces and move freely, which is why gases are highly compressible."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Is Matter Around Us Pure", "subTopic": "Mixtures and Solutions",
        "questionText": "A solution of salt in water is an example of a:",
        "options": [
            "A: Suspension",
            "B: Colloid",
            "C: Homogeneous mixture",
            "D: Compound"
        ],
        "correctAnswer": "C",
        "explanation": "A solution (like salt water) is a homogeneous mixture — the composition and appearance are uniform throughout. Salt particles (solute) are dissolved at the molecular/ionic level in water (solvent) and cannot be separated by filtering."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Atoms and Molecules", "subTopic": "Atomic Structure Basics",
        "questionText": "What is the charge of a proton?",
        "options": ["A: Negative charge", "B: No charge (neutral)", "C: Positive charge", "D: Depends on the element"],
        "correctAnswer": "C",
        "explanation": "Protons carry a positive charge (+1). Neutrons are neutral (no charge), and electrons carry a negative charge (-1). In a neutral atom, the number of protons equals the number of electrons, making the overall charge zero."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Structure of the Atom", "subTopic": "Bohr's Model",
        "questionText": "What is the maximum number of electrons that can be accommodated in the first electron shell (K shell)?",
        "options": ["A: 2", "B: 8", "C: 18", "D: 32"],
        "correctAnswer": "A",
        "explanation": "The first electron shell (K shell, n=1) can hold a maximum of 2 electrons. The formula for maximum electrons in a shell is 2n², where n is the shell number. For n=1: 2×1² = 2 electrons."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "The Fundamental Unit of Life", "subTopic": "Cell Organelles",
        "questionText": "The organelle called the 'powerhouse of the cell' that produces energy (ATP) is the:",
        "options": ["A: Nucleus", "B: Ribosome", "C: Mitochondria", "D: Chloroplast"],
        "correctAnswer": "C",
        "explanation": "Mitochondria are known as the 'powerhouse of the cell' because they carry out cellular respiration to produce ATP (adenosine triphosphate), the energy currency of the cell. The process uses oxygen and glucose to release energy."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Tissues", "subTopic": "Types of Tissues",
        "questionText": "Muscle tissue responsible for voluntary movements (like moving your arm) is called:",
        "options": [
            "A: Cardiac muscle",
            "B: Smooth muscle",
            "C: Skeletal (striated) muscle",
            "D: Connective tissue"
        ],
        "correctAnswer": "C",
        "explanation": "Skeletal (striated) muscle tissue is attached to bones and is under voluntary control. You consciously control these muscles to move limbs. Cardiac muscle (heart) and smooth muscle (intestines, blood vessels) are involuntary — they work without conscious control."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Motion", "subTopic": "Distance, Speed and Velocity",
        "questionText": "A car travels 100 km in 2 hours. What is its average speed?",
        "options": ["A: 50 km/h", "B: 100 km/h", "C: 200 km/h", "D: 25 km/h"],
        "correctAnswer": "A",
        "explanation": "Average speed = Total distance ÷ Total time = 100 km ÷ 2 hours = 50 km/h."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Force and Newton's Laws", "subTopic": "Newton's First Law",
        "questionText": "A book lying on a table stays at rest unless pushed. This behaviour is explained by Newton's:",
        "options": [
            "A: Second Law of Motion",
            "B: Third Law of Motion",
            "C: First Law of Motion (Law of Inertia)",
            "D: Law of Gravitation"
        ],
        "correctAnswer": "C",
        "explanation": "Newton's First Law (Law of Inertia) states that an object at rest stays at rest and an object in motion stays in motion unless acted upon by an external force. The book remains at rest because there is no net external force acting on it — it demonstrates inertia."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Gravitation", "subTopic": "Weight and Mass",
        "questionText": "The mass of a person is 60 kg on Earth. What will be their mass on the Moon?",
        "options": ["A: 10 kg", "B: 60 kg", "C: 360 kg", "D: 6 kg"],
        "correctAnswer": "B",
        "explanation": "Mass is the amount of matter in a body and remains constant everywhere in the universe. The person's mass is 60 kg on both Earth and the Moon. However, their WEIGHT (= mass × gravitational acceleration) would be less on the Moon since lunar gravity is 1/6 of Earth's gravity."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Work and Energy", "subTopic": "Work Done",
        "questionText": "A force of 10 N moves an object through a distance of 5 m in the direction of the force. What is the work done?",
        "options": ["A: 2 J", "B: 15 J", "C: 50 J", "D: 0.5 J"],
        "correctAnswer": "C",
        "explanation": "Work = Force × Distance (when force and displacement are in the same direction). Work = 10 N × 5 m = 50 J (joules). Work is done only when the object moves in the direction of the applied force."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Sound", "subTopic": "Properties of Sound",
        "questionText": "Sound travels FASTEST through which medium?",
        "options": ["A: Vacuum", "B: Air", "C: Water", "D: Steel"],
        "correctAnswer": "D",
        "explanation": "Sound is a mechanical wave that needs a medium to travel. It travels fastest through solids (like steel, ~5100 m/s) because particles are closely packed. It travels slower through liquids (~1500 m/s in water) and slowest through gases (~343 m/s in air). Sound cannot travel through vacuum (no medium)."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Natural Resources", "subTopic": "Air and Water",
        "questionText": "Which gas makes up the largest percentage of Earth's atmosphere?",
        "options": ["A: Oxygen (O₂)", "B: Carbon dioxide (CO₂)", "C: Nitrogen (N₂)", "D: Argon (Ar)"],
        "correctAnswer": "C",
        "explanation": "Nitrogen (N₂) makes up about 78% of Earth's atmosphere. Oxygen (O₂) makes up about 21%. Argon is about 0.93%, and carbon dioxide is only about 0.04%. Together, nitrogen and oxygen account for about 99% of the atmosphere."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Improvement in Food Resources", "subTopic": "Crop Production",
        "questionText": "The process of growing two or more crops on the same field at the same time is called:",
        "options": [
            "A: Crop rotation",
            "B: Mixed cropping",
            "C: Intercropping",
            "D: Monoculture"
        ],
        "correctAnswer": "B",
        "explanation": "Mixed cropping is growing two or more crops simultaneously on the same field (e.g., wheat and mustard together). Intercropping means growing two crops in definite rows. Crop rotation is growing different crops in sequence on the same land. Monoculture is growing a single crop repeatedly."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Diversity in Living Organisms", "subTopic": "Classification",
        "questionText": "Which of the following organisms belongs to the Kingdom Fungi?",
        "options": ["A: Amoeba", "B: Mushroom", "C: Moss", "D: Hydra"],
        "correctAnswer": "B",
        "explanation": "Mushrooms belong to Kingdom Fungi. Fungi are eukaryotic organisms that absorb nutrients from their environment (decomposers). Amoeba is a Protist, Moss is a plant (Kingdom Plantae), and Hydra is an animal (Kingdom Animalia)."
    },
    {
        "subject": "Science", "grade": 9, "difficulty": "Foundation",
        "topic": "Why Do We Fall Ill", "subTopic": "Diseases and Causes",
        "questionText": "Malaria is caused by which of the following?",
        "options": [
            "A: Bacteria (Mycobacterium)",
            "B: Virus (Plasmodium virus)",
            "C: Protozoan parasite (Plasmodium)",
            "D: Fungi"
        ],
        "correctAnswer": "C",
        "explanation": "Malaria is caused by Plasmodium — a protozoan parasite (not a virus or bacterium). It is transmitted to humans through the bite of infected female Anopheles mosquitoes. There are four species of Plasmodium that cause malaria in humans; P. falciparum causes the most severe form."
    },
]

# ─────────────────────────────────────────────────────────────
# SOCIAL STUDIES G9 FOUNDATION (15 questions)
# Topics: History (French Revolution, India's rise), Geography,
#         Civics, Economics
# ─────────────────────────────────────────────────────────────
SS9_FOUND = [
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "French Revolution", "subTopic": "Causes and Events",
        "questionText": "The French Revolution began in 1789. What event is considered the symbolic start of the Revolution?",
        "options": [
            "A: The execution of King Louis XVI",
            "B: The storming of the Bastille prison on 14 July 1789",
            "C: The Declaration of the Rights of Man",
            "D: Napoleon's rise to power"
        ],
        "correctAnswer": "B",
        "explanation": "The storming of the Bastille fortress-prison in Paris on 14 July 1789 is considered the symbolic start of the French Revolution. The Bastille represented royal tyranny. Its fall showed the power of the people against the monarchy. France celebrates Bastille Day (14 July) as its national day."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "People as Resource", "subTopic": "Human Capital",
        "questionText": "The term 'Human Development Index (HDI)' measures a country's development based on which THREE indicators?",
        "options": [
            "A: GDP, military strength, and population size",
            "B: Life expectancy, education level, and per capita income",
            "C: Industrial output, exports, and literacy rate",
            "D: Health, environment quality, and natural resources"
        ],
        "correctAnswer": "B",
        "explanation": "The HDI, developed by UNDP, measures human development through three dimensions: (1) Long and healthy life — measured by life expectancy at birth; (2) Knowledge — measured by mean years of schooling and expected years of schooling; (3) Decent standard of living — measured by GNI per capita. India has consistently improved its HDI ranking over decades."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Poverty as a Challenge", "subTopic": "Poverty in India",
        "questionText": "Which Indian state has the HIGHEST poverty rate approximately?",
        "options": ["A: Kerala", "B: Maharashtra", "C: Bihar", "D: Punjab"],
        "correctAnswer": "C",
        "explanation": "Bihar consistently has the highest poverty rates in India. It is a BIMARU state (Bihar, Madhya Pradesh, Rajasthan, Uttar Pradesh) characterised by high poverty, low HDI, and slow economic growth. Kerala has the lowest poverty rate and best social indicators. The North-South divide in development is a significant feature of Indian poverty distribution."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "India — Size and Location", "subTopic": "Physical Features",
        "questionText": "The Tropic of Cancer passes through how many Indian states?",
        "options": ["A: 6", "B: 8", "C: 10", "D: 5"],
        "correctAnswer": "B",
        "explanation": "The Tropic of Cancer (23.5°N latitude) passes through 8 Indian states: Gujarat, Rajasthan, Madhya Pradesh, Chhattisgarh, Jharkhand, West Bengal, Tripura, and Mizoram. It divides India into tropical (south) and subtropical (north) zones."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Physical Features of India", "subTopic": "Rivers",
        "questionText": "Which of the following rivers is a tributary of the Ganga?",
        "options": ["A: Mahanadi", "B: Godavari", "C: Yamuna", "D: Krishna"],
        "correctAnswer": "C",
        "explanation": "The Yamuna is the largest tributary of the Ganga. It originates from the Yamunotri glacier in Uttarakhand and merges with the Ganga at Prayagraj (Allahabad). Mahanadi, Godavari, and Krishna are major peninsular rivers that flow into the Bay of Bengal — they are not Ganga tributaries."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Climate", "subTopic": "Monsoon",
        "questionText": "The South-West Monsoon typically arrives in India first at which state?",
        "options": ["A: Tamil Nadu", "B: Goa", "C: Kerala", "D: Odisha"],
        "correctAnswer": "C",
        "explanation": "The South-West Monsoon typically arrives at the Kerala coast around 1 June, making it the first Indian state to receive monsoon rainfall. It then advances northward, covering the entire country by mid-July. Kerala's location at the tip of the Indian Peninsula makes it the first landmass the south-westerly winds reach after crossing the Arabian Sea."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Natural Vegetation and Wildlife", "subTopic": "Forest Types",
        "questionText": "Tropical Evergreen Forests in India are mainly found in which region?",
        "options": [
            "A: Rajasthan and Gujarat",
            "B: Andaman & Nicobar Islands, Western Ghats, and North-East India",
            "C: Punjab and Haryana",
            "D: Ladakh and Jammu & Kashmir"
        ],
        "correctAnswer": "B",
        "explanation": "Tropical Evergreen Forests grow in areas with annual rainfall above 200 cm. In India, they are found in the Andaman & Nicobar Islands, the Western Ghats (Kerala, Karnataka, Goa), and the North-Eastern states (Assam, Meghalaya, Arunachal Pradesh). These forests are dense and multi-layered with no distinct dry season."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Population", "subTopic": "Census Data",
        "questionText": "According to the 2011 Census, India's literacy rate was approximately:",
        "options": ["A: 52%", "B: 65%", "C: 74%", "D: 85%"],
        "correctAnswer": "C",
        "explanation": "India's literacy rate as per the 2011 Census was 74.04% (male: 82.14%, female: 65.46%). This showed significant improvement from 64.83% in 2001. The 2021 Census is pending, but estimates suggest literacy has improved further to around 77-78%."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Constitutional Design", "subTopic": "Indian Constitution",
        "questionText": "The Preamble of the Indian Constitution begins with the words 'We, the People of India.' This phrase signifies:",
        "options": [
            "A: That only educated people wrote the Constitution",
            "B: That sovereignty resides in the people — it is a democratic republic",
            "C: That only Hindu citizens are addressed",
            "D: That the Constitution was written by foreign experts"
        ],
        "correctAnswer": "B",
        "explanation": "'We, the People of India' signifies popular sovereignty — the ultimate authority lies with the citizens of India, not with kings, colonial rulers, or religious authorities. This is a fundamental principle of democracy: the government derives its power from the consent of the governed."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Electoral Politics", "subTopic": "Election System",
        "questionText": "India uses which electoral system for Lok Sabha elections?",
        "options": [
            "A: Proportional representation",
            "B: First-Past-The-Post (FPTP) system",
            "C: Two-round system",
            "D: Single transferable vote"
        ],
        "correctAnswer": "B",
        "explanation": "India uses the First-Past-The-Post (FPTP) system for Lok Sabha elections — the candidate with the most votes in a constituency wins, regardless of whether they have more than 50% of votes. This system is simple and produces clear majorities but may not represent minority preferences proportionally."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Working of Institutions", "subTopic": "Three Branches of Government",
        "questionText": "Which branch of the Indian government is responsible for making laws?",
        "options": [
            "A: Executive (Cabinet/Prime Minister)",
            "B: Judiciary (Supreme Court/High Courts)",
            "C: Legislature (Parliament)",
            "D: Military"
        ],
        "correctAnswer": "C",
        "explanation": "The Legislature (Parliament) is responsible for making laws. India's Parliament consists of Lok Sabha (House of the People), Rajya Sabha (Council of States), and the President. The Executive implements laws, and the Judiciary interprets them — this separation of powers is a key feature of Indian democracy."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Democratic Rights", "subTopic": "Rights in a Democracy",
        "questionText": "The Right to Information (RTI) Act was passed in India in which year?",
        "options": ["A: 1950", "B: 1991", "C: 2005", "D: 2010"],
        "correctAnswer": "C",
        "explanation": "The Right to Information Act was passed in 2005. It empowers Indian citizens to request information from government offices. The concerned authority must provide the information within 30 days. RTI has been a powerful tool for transparency, accountability, and fighting corruption. It arose from the grassroots MKSS movement in Rajasthan."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Nazism and the Rise of Hitler", "subTopic": "World War II",
        "questionText": "In which year did Adolf Hitler become Chancellor of Germany?",
        "options": ["A: 1929", "B: 1933", "C: 1939", "D: 1945"],
        "correctAnswer": "B",
        "explanation": "Adolf Hitler was appointed Chancellor of Germany on 30 January 1933 by President Hindenburg. Within months, he consolidated power, suspended democratic institutions, and established a totalitarian dictatorship. He became Führer (Supreme Leader) in 1934 after Hindenburg's death. Germany invaded Poland in 1939, starting World War II."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Food Security in India", "subTopic": "PDS and Government Schemes",
        "questionText": "The Public Distribution System (PDS) in India distributes food grains at subsidised prices. These food grains are procured and stored by which organisation?",
        "options": [
            "A: Reserve Bank of India (RBI)",
            "B: Food Corporation of India (FCI)",
            "C: National Bank for Agriculture and Rural Development (NABARD)",
            "D: Ministry of Agriculture"
        ],
        "correctAnswer": "B",
        "explanation": "The Food Corporation of India (FCI) was set up in 1965 to procure food grains from farmers at Minimum Support Price (MSP), store them in government warehouses, and distribute them through the PDS ration shops. FCI maintains buffer stocks to ensure food security and price stability throughout the country."
    },
    {
        "subject": "Social Studies", "grade": 9, "difficulty": "Foundation",
        "topic": "Russia — Socialism and Revolution", "subTopic": "Russian Revolution",
        "questionText": "The Russian Revolution of 1917 led to the establishment of the world's first socialist state. Who led the Bolshevik Revolution?",
        "options": ["A: Karl Marx", "B: Joseph Stalin", "C: Vladimir Lenin", "D: Leon Trotsky"],
        "correctAnswer": "C",
        "explanation": "Vladimir Lenin led the Bolshevik Party in the October Revolution of 1917 (also called the Bolshevik Revolution). The Bolsheviks (meaning 'majority') overthrew the Provisional Government and established Soviet rule. Karl Marx (who died in 1883) provided the ideological basis. Stalin came to power only after Lenin's death in 1924."
    },
]

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
ALL_BATCHES = [
    ("Science G6 Olympiad", SCI6_OLY),
    ("Science G7 Olympiad", SCI7_OLY),
    ("Hindi G8 Olympiad", HINDI8_OLY),
    ("General Knowledge G9 Advanced", GK9_ADV),
    ("General Knowledge G9 Olympiad", GK9_OLY),
    ("Science G9 Foundation", SCI9_FOUND),
    ("Social Studies G9 Foundation", SS9_FOUND),
]

conn = pyodbc.connect(DB_CONN)
total = ok = dup = err = 0

for batch_name, questions in ALL_BATCHES:
    for q in questions:
        total += 1
        try:
            r = insert(conn, q)
            if r == "OK":
                ok += 1
                print(f"  OK Q{total:03d} [{q['subject']} G{q['grade']} {q['difficulty']}] {q['subTopic']}")
            else:
                dup += 1
                print(f"  DUP Q{total:03d} [{q['subject']} G{q['grade']} {q['difficulty']}] {q['subTopic']}")
        except Exception as e:
            err += 1
            print(f"  FAIL Q{total:03d} [{q['subject']} G{q['grade']} {q['difficulty']}] {q['subTopic']}: {e}")

conn.close()
print(f"\n  Done: {ok} posted, {dup} duplicates, {err} errors  (total={total})\n")
