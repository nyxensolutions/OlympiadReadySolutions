import pyodbc, uuid, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=olympiadready-np.database.windows.net;"
    "DATABASE=OlympiadReady;"
    "UID=nyxen-admin;PWD=Olympiad@2026"
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

questions = [

# ── Science-Biology G10 Foundation (+15q, 15→30) ──────────────────────────────
{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Cell Structure",
 "questionText":"Which organelle is called the 'brain' of the cell?",
 "options":["A: Mitochondria","B: Ribosome","C: Nucleus","D: Vacuole"],
 "correctAnswer":"C",
 "explanation":"The nucleus controls all cell activities and contains the genetic material (DNA). It is rightly called the 'brain' or 'control centre' of the cell."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Nutrition in Plants",
 "questionText":"Which gas do plants release during photosynthesis?",
 "options":["A: Carbon dioxide","B: Nitrogen","C: Oxygen","D: Hydrogen"],
 "correctAnswer":"C",
 "explanation":"During photosynthesis, plants absorb CO₂ and water, and using sunlight, produce glucose and oxygen (O₂). The oxygen is released into the atmosphere."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Human Digestive System",
 "questionText":"Where does most chemical digestion and absorption of nutrients take place?",
 "options":["A: Stomach","B: Large intestine","C: Small intestine","D: Oesophagus"],
 "correctAnswer":"C",
 "explanation":"The small intestine is the main site of digestion and absorption. Digestive enzymes from the pancreas and bile from the liver complete digestion; nutrients are absorbed through the villi into the bloodstream."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Blood",
 "questionText":"What is the main function of red blood cells (RBCs)?",
 "options":["A: Fight infection","B: Transport oxygen","C: Clot blood","D: Produce antibodies"],
 "correctAnswer":"B",
 "explanation":"Red blood cells (erythrocytes) contain haemoglobin, which binds to oxygen in the lungs and transports it to body tissues. They have no nucleus, giving more space for haemoglobin."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Reproduction — Humans",
 "questionText":"Where does fertilisation (meeting of egg and sperm) normally take place in humans?",
 "options":["A: Ovary","B: Uterus","C: Fallopian tube","D: Cervix"],
 "correctAnswer":"C",
 "explanation":"Fertilisation normally occurs in the fallopian tube (oviduct). The fertilised egg (zygote) then travels to the uterus and implants in the uterine wall for development."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Genetics — Basics",
 "questionText":"The basic unit of heredity that carries genetic information is called a:",
 "options":["A: Cell","B: Chromosome","C: Gene","D: Nucleus"],
 "correctAnswer":"C",
 "explanation":"A gene is a specific sequence of DNA that codes for a protein and determines a particular trait. Genes are located on chromosomes inside the nucleus of every cell."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Skeletal System",
 "questionText":"How many bones does the adult human body have?",
 "options":["A: 206","B: 212","C: 198","D: 300"],
 "correctAnswer":"A",
 "explanation":"The adult human skeleton has 206 bones. Babies are born with around 270–300 bones; many fuse together as they grow, leaving 206 by adulthood."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Microorganisms",
 "questionText":"Which microorganism is responsible for causing malaria?",
 "options":["A: Virus","B: Bacteria","C: Protozoan (Plasmodium)","D: Fungus"],
 "correctAnswer":"C",
 "explanation":"Malaria is caused by the protozoan parasite Plasmodium, transmitted by the bite of infected female Anopheles mosquitoes. It is not caused by bacteria or viruses."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Plant Reproduction",
 "questionText":"The transfer of pollen from the anther to the stigma of a flower is called:",
 "options":["A: Fertilisation","B: Germination","C: Pollination","D: Transpiration"],
 "correctAnswer":"C",
 "explanation":"Pollination is the transfer of pollen grains from the male anther to the female stigma. It can be done by wind, insects, water, or animals. Fertilisation follows pollination."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Food Web",
 "questionText":"Organisms that break down dead organic matter into simpler substances are called:",
 "options":["A: Producers","B: Consumers","C: Decomposers","D: Herbivores"],
 "correctAnswer":"C",
 "explanation":"Decomposers (bacteria and fungi) break down dead plants and animals into simpler inorganic substances. They recycle nutrients back into the soil, completing the food chain."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Endocrine System",
 "questionText":"Which gland is known as the 'master gland' of the body?",
 "options":["A: Thyroid","B: Adrenal","C: Pituitary","D: Pancreas"],
 "correctAnswer":"C",
 "explanation":"The pituitary gland (at the base of the brain) is called the master gland because it controls the activity of most other endocrine glands by releasing stimulating hormones."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Excretion",
 "questionText":"The functional unit of the kidney responsible for filtering blood is the:",
 "options":["A: Neuron","B: Nephron","C: Alveolus","D: Villus"],
 "correctAnswer":"B",
 "explanation":"Each kidney contains about 1 million nephrons. The nephron filters blood under pressure, reabsorbs useful substances, and produces urine from the waste products."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Nervous System",
 "questionText":"A reflex action is controlled by the:",
 "options":["A: Cerebrum","B: Cerebellum","C: Spinal cord","D: Medulla oblongata"],
 "correctAnswer":"C",
 "explanation":"Reflex actions (like pulling your hand from a hot object) are controlled by the spinal cord without involving the brain. This makes them very fast automatic responses."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Adaptation",
 "questionText":"Camouflage in animals is an example of:",
 "options":["A: Structural adaptation","B: Behavioural adaptation","C: Physiological adaptation","D: Artificial selection"],
 "correctAnswer":"A",
 "explanation":"Camouflage (body colour/pattern matching the environment) is a structural adaptation — a physical feature that helps an organism survive in its environment."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Respiratory System",
 "questionText":"Gas exchange in the human lungs takes place in tiny sacs called:",
 "options":["A: Bronchioles","B: Bronchi","C: Alveoli","D: Trachea"],
 "correctAnswer":"C",
 "explanation":"Alveoli are tiny air sacs at the end of bronchioles. They have thin walls and rich blood supply, enabling efficient diffusion of O₂ into the blood and CO₂ out of the blood."},

# ── Science-Chemistry G10 Foundation (+15q, 15→30) ────────────────────────────
{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Metals and Non-metals",
 "questionText":"Which property allows metals to be drawn into wires?",
 "options":["A: Malleability","B: Ductility","C: Conductivity","D: Lustre"],
 "correctAnswer":"B",
 "explanation":"Ductility is the property of metals that allows them to be drawn into thin wires. Malleability is being beaten into sheets. Copper and gold are highly ductile metals."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Acids and Bases",
 "questionText":"Which of the following is an example of a base?",
 "options":["A: Vinegar","B: Lemon juice","C: Sodium hydroxide (NaOH)","D: Carbonic acid"],
 "correctAnswer":"C",
 "explanation":"Sodium hydroxide (NaOH) is a strong base — it produces OH⁻ ions in solution. Vinegar (acetic acid), lemon juice (citric acid), and carbonic acid are all acids."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Physical and Chemical Changes",
 "questionText":"Which of the following is a chemical change?",
 "options":["A: Melting of ice","B: Dissolving sugar in water","C: Burning of paper","D: Cutting of wood"],
 "correctAnswer":"C",
 "explanation":"Burning paper is a chemical change — new substances (CO₂, water vapour, ash) are formed, and the change is irreversible. Melting, dissolving, and cutting are physical changes."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Periodic Table",
 "questionText":"Elements in the same group of the periodic table have similar chemical properties because they have the same number of:",
 "options":["A: Protons","B: Neutrons","C: Valence electrons","D: Energy levels"],
 "correctAnswer":"C",
 "explanation":"Elements in the same group have the same number of valence (outermost shell) electrons, which determines their chemical behaviour and reactivity."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Chemical Reactions — Types",
 "questionText":"2H₂ + O₂ → 2H₂O is an example of which type of reaction?",
 "options":["A: Decomposition","B: Displacement","C: Combination (synthesis)","D: Double displacement"],
 "correctAnswer":"C",
 "explanation":"A combination (synthesis) reaction: two or more reactants combine to form a single product. Here hydrogen and oxygen combine to form water."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Carbon Compounds",
 "questionText":"Which element forms the basis of all organic compounds?",
 "options":["A: Oxygen","B: Hydrogen","C: Nitrogen","D: Carbon"],
 "correctAnswer":"D",
 "explanation":"Carbon is the basis of all organic compounds due to its unique ability to form four covalent bonds and create long chains (catenation) with itself and other elements."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Metals — Properties",
 "questionText":"Which metal is the best conductor of electricity?",
 "options":["A: Gold","B: Copper","C: Silver","D: Aluminium"],
 "correctAnswer":"C",
 "explanation":"Silver has the highest electrical conductivity of all metals. However, copper is used in electrical wiring due to its much lower cost and nearly as good conductivity."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Corrosion",
 "questionText":"Rusting of iron is a chemical change that requires the presence of:",
 "options":["A: Water only","B: Oxygen only","C: Both water and oxygen","D: Carbon dioxide only"],
 "correctAnswer":"C",
 "explanation":"Iron rusts (forms Fe₂O₃·nH₂O) only when both water and oxygen are present simultaneously. In the absence of either, iron does not rust."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Acids and Bases — Indicators",
 "questionText":"Litmus paper turns red in:",
 "options":["A: Base","B: Neutral solution","C: Acid","D: Salt solution"],
 "correctAnswer":"C",
 "explanation":"Litmus is a natural indicator. It turns red in acidic solutions (pH < 7) and blue in basic/alkaline solutions (pH > 7). In neutral solutions it stays purple."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Soaps",
 "questionText":"Soaps work in water by forming structures called micelles, which can clean because the soap molecule has:",
 "options":["A: Two hydrophilic ends","B: Two hydrophobic ends","C: A hydrophilic head and hydrophobic tail","D: No ionic character"],
 "correctAnswer":"C",
 "explanation":"Each soap molecule has a hydrophilic (water-loving) ionic head and a hydrophobic (water-repelling) hydrocarbon tail. The tail traps grease; the head stays in water, forming a micelle that washes away dirt."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Fuels",
 "questionText":"The primary component of natural gas used for cooking is:",
 "options":["A: Ethane","B: Propane","C: Methane","D: Butane"],
 "correctAnswer":"C",
 "explanation":"Methane (CH₄) is the main component of natural gas (~80–90%). It is also the simplest alkane. CNG (Compressed Natural Gas) used in vehicles is primarily methane."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Chemical Symbols",
 "questionText":"What is the chemical symbol for gold?",
 "options":["A: Go","B: Gd","C: Ag","D: Au"],
 "correctAnswer":"D",
 "explanation":"Gold's symbol is Au, from the Latin 'Aurum'. Ag is silver (Argentum), Gd is gadolinium. Many element symbols come from their Latin names."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"States of Matter",
 "questionText":"When a substance changes directly from solid to gas without becoming liquid, the process is called:",
 "options":["A: Evaporation","B: Sublimation","C: Condensation","D: Melting"],
 "correctAnswer":"B",
 "explanation":"Sublimation is the direct transition from solid to gas phase without passing through the liquid phase. Examples: dry ice (solid CO₂) and naphthalene (camphor) sublimate at room temperature."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Mixtures",
 "questionText":"Which method is used to separate a mixture of salt and water?",
 "options":["A: Filtration","B: Magnetic separation","C: Evaporation","D: Distillation for pure water"],
 "correctAnswer":"C",
 "explanation":"Evaporation is used to recover salt from saltwater — water evaporates leaving solid salt behind. Distillation would be used if you wanted to collect the pure water."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Atomic Structure",
 "questionText":"The atomic number of an element equals the number of:",
 "options":["A: Neutrons","B: Protons","C: Electrons + Neutrons","D: Nucleons"],
 "correctAnswer":"B",
 "explanation":"The atomic number (Z) is the number of protons in the nucleus of an atom. In a neutral atom, it also equals the number of electrons. It uniquely identifies each element."},

# ── Science-Physics G10 Foundation (+15q, 15→30) ─────────────────────────────
{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Motion",
 "questionText":"A car travels 120 km in 2 hours. Its average speed is:",
 "options":["A: 240 km/h","B: 60 km/h","C: 30 km/h","D: 120 km/h"],
 "correctAnswer":"B",
 "explanation":"Speed = Distance / Time = 120 km / 2 h = 60 km/h."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Force and Newton's Laws",
 "questionText":"Newton's second law states that force equals:",
 "options":["A: Mass × Velocity","B: Mass × Acceleration","C: Weight × Speed","D: Mass / Acceleration"],
 "correctAnswer":"B",
 "explanation":"Newton's Second Law: F = ma. Force (in Newtons) = mass (kg) × acceleration (m/s²). A larger force produces greater acceleration on the same mass."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Gravity",
 "questionText":"The weight of an object is the force of gravity acting on it. Weight is measured in:",
 "options":["A: Kilograms","B: Newtons","C: Grams","D: Pascals"],
 "correctAnswer":"B",
 "explanation":"Weight is a force (W = mg), measured in Newtons (N). Mass is measured in kilograms. On Earth, 1 kg mass has a weight of approximately 9.8 N."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Work and Energy",
 "questionText":"The SI unit of work and energy is:",
 "options":["A: Watt","B: Newton","C: Joule","D: Pascal"],
 "correctAnswer":"C",
 "explanation":"Work = Force × Displacement. The SI unit of both work and energy is the Joule (J). 1 Joule = 1 Newton × 1 metre. Power is measured in Watts (J/s)."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Sound",
 "questionText":"Sound cannot travel through:",
 "options":["A: Water","B: Steel","C: Air","D: Vacuum"],
 "correctAnswer":"D",
 "explanation":"Sound is a mechanical wave that requires a medium (solid, liquid, or gas) to travel. It cannot travel through vacuum (empty space) because there are no particles to vibrate."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Light",
 "questionText":"The bending of light as it passes from one medium to another is called:",
 "options":["A: Reflection","B: Refraction","C: Diffraction","D: Dispersion"],
 "correctAnswer":"B",
 "explanation":"Refraction is the bending of light when it passes from one transparent medium to another of different density (e.g., air to glass). It occurs because light changes speed."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Electricity — Basic",
 "questionText":"Electric current is measured in:",
 "options":["A: Volts","B: Ohms","C: Watts","D: Amperes"],
 "correctAnswer":"D",
 "explanation":"Electric current (rate of flow of charge) is measured in Amperes (A) using an ammeter. Voltage in Volts, resistance in Ohms, power in Watts."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Magnets",
 "questionText":"Like poles of a magnet:",
 "options":["A: Attract each other","B: Repel each other","C: Have no effect on each other","D: Cancel each other"],
 "correctAnswer":"B",
 "explanation":"Like poles (N-N or S-S) repel each other; unlike poles (N-S) attract. This is the fundamental law of magnetism."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Heat",
 "questionText":"The transfer of heat through direct contact between objects is called:",
 "options":["A: Convection","B: Radiation","C: Conduction","D: Evaporation"],
 "correctAnswer":"C",
 "explanation":"Conduction is heat transfer through direct contact — heat flows from hotter to cooler regions. Metals are good conductors; wood and plastic are insulators. Convection occurs in fluids; radiation doesn't need a medium."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Pressure",
 "questionText":"Pressure is defined as:",
 "options":["A: Force × Area","B: Force / Area","C: Mass × Gravity","D: Weight / Volume"],
 "correctAnswer":"B",
 "explanation":"Pressure = Force / Area. Unit is Pascal (Pa = N/m²). A smaller area with the same force creates greater pressure — that's why knife edges and needles are sharp."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Floating and Sinking",
 "questionText":"Archimedes' principle states that a body immersed in a fluid experiences a buoyant force equal to:",
 "options":["A: The weight of the body","B: The volume of the fluid displaced","C: The weight of the fluid displaced","D: The density of the body"],
 "correctAnswer":"C",
 "explanation":"Archimedes' principle: buoyant force = weight of fluid displaced. An object floats if its weight equals or is less than the buoyant force (i.e., it displaces fluid equal to its own weight)."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Simple Machines",
 "questionText":"A see-saw is an example of which type of simple machine?",
 "options":["A: Pulley","B: Inclined plane","C: Lever","D: Screw"],
 "correctAnswer":"C",
 "explanation":"A see-saw (teeter-totter) is a Class 1 lever — the fulcrum is between the effort and the load. Levers help lift heavy loads with less effort."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Circuits",
 "questionText":"In a parallel circuit, if one bulb fuses, the other bulbs:",
 "options":["A: All go out","B: Get brighter","C: Continue to glow normally","D: Flicker"],
 "correctAnswer":"C",
 "explanation":"In a parallel circuit, each component has its own path from the power source. If one branch breaks, current continues to flow through the other branches — the other bulbs continue to glow."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Energy Types",
 "questionText":"A stretched rubber band has which type of energy?",
 "options":["A: Kinetic energy","B: Thermal energy","C: Potential energy","D: Chemical energy"],
 "correctAnswer":"C",
 "explanation":"A stretched rubber band has elastic potential energy — stored energy due to its deformed (stretched) state. When released, this potential energy converts to kinetic energy."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Waves",
 "questionText":"The number of complete waves passing a point per second is called:",
 "options":["A: Wavelength","B: Amplitude","C: Frequency","D: Speed"],
 "correctAnswer":"C",
 "explanation":"Frequency is the number of complete oscillations (cycles) per second. It is measured in Hertz (Hz). Wave speed = frequency × wavelength (v = fλ)."},

# ── Commerce G12 Advanced (+15q, 20→35) ───────────────────────────────────────
{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Funds Flow Statement",
 "questionText":"In a Funds Flow Statement, 'funds' typically refers to:",
 "options":["A: Cash only","B: Working capital (Current Assets − Current Liabilities)","C: Long-term loans","D: Fixed assets"],
 "correctAnswer":"B",
 "explanation":"In traditional Funds Flow analysis, 'funds' means working capital — the excess of current assets over current liabilities. A Funds Flow Statement shows changes in working capital between two periods."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Redemption of Debentures",
 "questionText":"When debentures are redeemed (repaid) at a premium, the premium amount is debited to:",
 "options":["A: Debenture Account","B: Loss on Redemption / Securities Premium Reserve","C: General Reserve","D: Share Capital"],
 "correctAnswer":"B",
 "explanation":"Premium on redemption of debentures is a capital loss. It is written off against Securities Premium Reserve (if available) or charged to Statement of Profit and Loss as 'Loss on Redemption of Debentures'."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Dividend Policy",
 "questionText":"Which dividend policy pays a fixed amount per share regardless of the company's earnings?",
 "options":["A: Stable dividend policy","B: Residual dividend policy","C: No dividend policy","D: Bonus dividend policy"],
 "correctAnswer":"A",
 "explanation":"A stable dividend policy pays a fixed, predictable dividend per share each year, giving shareholders certainty. The residual policy pays dividends only from leftover funds after investment needs are met."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Debenture Sinking Fund",
 "questionText":"A Debenture Redemption Reserve (DRR) is created to:",
 "options":["A: Increase share capital","B: Protect debenture holders by ensuring funds are available for redemption","C: Pay corporate tax","D: Distribute bonus shares"],
 "correctAnswer":"B",
 "explanation":"Companies are required to create a DRR (a portion of profits) to ensure sufficient funds are available when debentures mature. It protects investors by preventing companies from spending all profits."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Capital Market — Primary vs Secondary",
 "questionText":"An Initial Public Offering (IPO) takes place in the:",
 "options":["A: Secondary market","B: Money market","C: Primary market","D: Derivatives market"],
 "correctAnswer":"C",
 "explanation":"An IPO (Initial Public Offering) is when a company issues new shares to the public for the first time — this happens in the primary market. Secondary market (stock exchange) is where existing shares are traded between investors."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Accounting Standards",
 "questionText":"Under the Going Concern concept in accounting, it is assumed that:",
 "options":["A: The business will be liquidated soon","B: The business will continue operating for the foreseeable future","C: Assets are recorded at market value","D: All transactions are in cash"],
 "correctAnswer":"B",
 "explanation":"The Going Concern concept assumes the business will continue to operate indefinitely (not be liquidated). This justifies recording assets at cost rather than liquidation value."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Working Capital Management",
 "questionText":"The Operating Cycle (Cash Conversion Cycle) is the time taken from:",
 "options":["A: Purchase of raw materials to collection of cash from debtors","B: Sale of goods to purchase of raw materials","C: Receipt of payment to next purchase","D: Production to tax payment"],
 "correctAnswer":"A",
 "explanation":"The Operating Cycle = Raw Material period + WIP period + Finished Goods period + Debtors collection period − Creditors payment period. It measures how long cash is tied up in operations."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Insurance",
 "questionText":"The principle of 'Indemnity' in insurance means:",
 "options":["A: You can claim multiple times for the same loss","B: The insured is restored to the same financial position as before the loss","C: The insurer pays more than the actual loss","D: Premium must equal the sum assured"],
 "correctAnswer":"B",
 "explanation":"Indemnity: insurance compensates the insured for the actual financial loss suffered, not more. You cannot profit from insurance. The insured is restored to their pre-loss position."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Provision vs Reserve",
 "questionText":"The difference between a Provision and a Reserve is that:",
 "options":["A: Provisions are for known liabilities; Reserves are appropriations of profit","B: Reserves are compulsory; Provisions are optional","C: Provisions increase capital; Reserves decrease it","D: They are the same thing"],
 "correctAnswer":"A",
 "explanation":"Provisions are charges against profit for known/estimated liabilities (e.g., Provision for Bad Debts). Reserves are appropriations of profit for specific or general purposes and are only created when there is profit."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"E-Commerce",
 "questionText":"B2C (Business-to-Consumer) e-commerce refers to transactions between:",
 "options":["A: Two businesses","B: A business and its employees","C: A business and individual consumers","D: Two consumers"],
 "correctAnswer":"C",
 "explanation":"B2C e-commerce involves businesses selling directly to individual end-consumers online (e.g., Amazon, Flipkart). B2B is business-to-business; C2C is consumer-to-consumer (e.g., OLX)."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Depreciation Methods",
 "questionText":"Under the Written Down Value (WDV) method of depreciation, the annual charge:",
 "options":["A: Remains constant each year","B: Increases each year","C: Decreases each year","D: Is calculated on original cost each year"],
 "correctAnswer":"C",
 "explanation":"WDV method applies a fixed percentage to the book value (written-down value) at the beginning of each year. As WDV reduces each year, so does the depreciation charge — it decreases annually."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Span of Control",
 "questionText":"A narrow span of control means a manager supervises:",
 "options":["A: Many subordinates","B: Few subordinates","C: No subordinates","D: Only senior employees"],
 "correctAnswer":"B",
 "explanation":"Span of control = number of subordinates a manager directly supervises. Narrow span (few subordinates) leads to tall organisational structures with more management layers. Wide span leads to flat structures."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Planning",
 "questionText":"A 'strategy' in management refers to a:",
 "options":["A: Day-to-day operational plan","B: Comprehensive plan to achieve long-term organisational goals","C: Budget allocation for a quarter","D: Departmental work schedule"],
 "correctAnswer":"B",
 "explanation":"Strategy is a long-term plan that defines how an organisation will achieve its broad objectives. It considers external environment and internal resources. Tactical plans are shorter-term, operational plans are day-to-day."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Fixed and Variable Costs",
 "questionText":"As production volume increases, fixed cost per unit:",
 "options":["A: Increases","B: Remains the same","C: Decreases","D: Doubles"],
 "correctAnswer":"C",
 "explanation":"Total fixed costs remain constant regardless of output. As more units are produced, the fixed cost is spread over more units — so fixed cost per unit decreases. Variable costs per unit remain constant."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Channels of Distribution",
 "questionText":"Which channel of distribution has NO intermediary between producer and consumer?",
 "options":["A: One-level channel","B: Two-level channel","C: Zero-level (direct) channel","D: Multi-level channel"],
 "correctAnswer":"C",
 "explanation":"A zero-level (direct) channel: Producer → Consumer. No wholesaler or retailer. Examples: factory outlets, direct mail, e-commerce (producer's own website). It gives maximum control but requires more effort."},

# ── Commerce G11 Advanced (+15q, 25→40) ───────────────────────────────────────
{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Accounting Concepts",
 "questionText":"The concept that requires businesses to record transactions only when a definite monetary value can be assigned is the:",
 "options":["A: Going Concern concept","B: Money Measurement concept","C: Accrual concept","D: Consistency concept"],
 "correctAnswer":"B",
 "explanation":"Money Measurement concept: only transactions that can be expressed in monetary terms are recorded in accounts. Non-monetary information (e.g., employee morale, brand reputation) is not recorded."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Journal Entries",
 "questionText":"When goods worth ₹5,000 are purchased on credit, the journal entry is:",
 "options":["A: Debit Cash; Credit Purchases","B: Debit Purchases; Credit Creditor/Accounts Payable","C: Debit Creditor; Credit Purchases","D: Debit Sales; Credit Cash"],
 "correctAnswer":"B",
 "explanation":"Credit purchase: Purchases A/c Dr ₹5,000 (goods come in — debit the benefit received); Creditor/Accounts Payable A/c Cr ₹5,000 (liability increases — credit the giver/liability)."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Economics",
 "subTopic":"Market Structures",
 "questionText":"In a monopoly market, there is:",
 "options":["A: Many sellers, identical products","B: Few sellers, differentiated products","C: One seller with no close substitutes","D: Perfect competition among sellers"],
 "correctAnswer":"C",
 "explanation":"A monopoly exists when there is a single seller of a product with no close substitutes. The monopolist has significant market power and can influence price. Entry barriers are very high."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Economics",
 "subTopic":"Cost Concepts",
 "questionText":"Opportunity cost is best defined as:",
 "options":["A: The price paid for a product","B: The cost of the next best alternative foregone","C: The total production cost","D: The profit sacrificed"],
 "correctAnswer":"B",
 "explanation":"Opportunity cost is the value of the next best alternative that is given up when making a choice. If you choose to study instead of working, the opportunity cost is the wages you could have earned."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Entrepreneurship",
 "questionText":"A 'sole proprietorship' is a business owned and managed by:",
 "options":["A: Two partners","B: A single individual","C: Shareholders","D: The government"],
 "correctAnswer":"B",
 "explanation":"A sole proprietorship is owned and managed by one person who takes all decisions and bears all risks. It is the simplest and most common form of business organisation in India."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Ledger and Trial Balance",
 "questionText":"Which of the following accounts would appear on the debit side of a Trial Balance?",
 "options":["A: Capital Account","B: Sales Account","C: Creditors Account","D: Cash Account"],
 "correctAnswer":"D",
 "explanation":"Assets, expenses, and losses have debit balances. Cash is an asset → debit balance. Capital, sales, and creditors have credit balances (liabilities/income/equity)."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Economics",
 "subTopic":"Supply and Demand",
 "questionText":"When the price of a good rises, the quantity demanded generally:",
 "options":["A: Increases","B: Stays the same","C: Decreases","D: Doubles"],
 "correctAnswer":"C",
 "explanation":"Law of Demand: there is an inverse relationship between price and quantity demanded, ceteris paribus. As price rises, quantity demanded falls (and vice versa)."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Business Finance",
 "questionText":"Retained earnings (ploughing back of profits) is a source of:",
 "options":["A: External finance","B: Short-term finance","C: Internal finance","D: Debt finance"],
 "correctAnswer":"C",
 "explanation":"Retained earnings (undistributed profits kept in the business) are a form of internal finance — generated within the business without borrowing or issuing shares."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Errors in Accounts",
 "questionText":"An error where a transaction is not recorded at all in the books is called an error of:",
 "options":["A: Commission","B: Omission","C: Principle","D: Compensating"],
 "correctAnswer":"B",
 "explanation":"Error of Omission: a transaction is completely missed from the books. Error of Commission: wrong amount or wrong account used. Error of Principle: wrong accounting treatment (e.g., capital expenditure treated as revenue)."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Economics",
 "subTopic":"Inflation Types",
 "questionText":"Inflation caused by rising production costs (e.g., wages, raw materials) is called:",
 "options":["A: Demand-pull inflation","B: Cost-push inflation","C: Structural inflation","D: Hyperinflation"],
 "correctAnswer":"B",
 "explanation":"Cost-push inflation: rising input costs (wages, fuel, raw materials) push up production costs, which producers pass on as higher prices. Demand-pull inflation occurs when demand exceeds supply."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Consumer Rights",
 "questionText":"'Right to be heard' as a consumer right means:",
 "options":["A: Right to get full information","B: Right to file a complaint and have it considered","C: Right to fair prices","D: Right to safe products"],
 "correctAnswer":"B",
 "explanation":"Right to be Heard: consumers have the right to express their grievances and have them receive fair consideration. It includes the right to be represented in consumer forums."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Final Accounts",
 "questionText":"Gross Profit is calculated in the:",
 "options":["A: Balance Sheet","B: Cash Flow Statement","C: Trading Account","D: Profit and Loss Account"],
 "correctAnswer":"C",
 "explanation":"Gross Profit = Net Sales − Cost of Goods Sold. It is calculated in the Trading Account. Net Profit = Gross Profit − Operating Expenses, calculated in the P&L Account."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Economics",
 "subTopic":"Government Budget",
 "questionText":"A fiscal deficit occurs when the government's:",
 "options":["A: Exports exceed imports","B: Revenue receipts exceed revenue expenditure","C: Total expenditure exceeds total receipts (excluding borrowings)","D: Tax collection exceeds spending"],
 "correctAnswer":"C",
 "explanation":"Fiscal Deficit = Total Government Expenditure − Total Government Receipts (excluding borrowings). It shows the amount the government needs to borrow to meet its expenditure. A high fiscal deficit can be inflationary."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Business Ethics",
 "questionText":"Corporate Social Responsibility (CSR) refers to a company's commitment to:",
 "options":["A: Maximising shareholder profit only","B: Operating ethically and contributing to society beyond legal obligations","C: Avoiding taxes legally","D: Competing aggressively with rivals"],
 "correctAnswer":"B",
 "explanation":"CSR involves companies taking responsibility for the impact of their activities on society, environment, and stakeholders — going beyond legal requirements. India's Companies Act 2013 mandates 2% of net profit for CSR for eligible companies."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Rectification of Errors",
 "questionText":"A suspense account is opened when:",
 "options":["A: A new partner is admitted","B: The Trial Balance fails to agree and the difference is temporarily placed there","C: A fixed asset is purchased","D: Profits are distributed"],
 "correctAnswer":"B",
 "explanation":"When the Trial Balance doesn't tally, the difference is placed in a Suspense Account temporarily. As errors are located and corrected, the Suspense Account balance reduces to zero."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Economics",
 "subTopic":"Exchange Rate",
 "questionText":"If the Indian Rupee depreciates against the US Dollar, Indian exports become:",
 "options":["A: More expensive for foreign buyers","B: Cheaper for foreign buyers","C: Unaffected","D: More expensive for Indian buyers"],
 "correctAnswer":"B",
 "explanation":"Rupee depreciation means foreign currency buys more rupees. Indian goods (priced in rupees) become cheaper in dollar terms for foreign buyers → exports become more competitive and tend to increase."},

# ── Science G11 Foundation (+15q, 25→40) ──────────────────────────────────────
{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Units and Measurement",
 "questionText":"The SI unit of electric charge is:",
 "options":["A: Ampere","B: Coulomb","C: Volt","D: Ohm"],
 "correctAnswer":"B",
 "explanation":"The Coulomb (C) is the SI unit of electric charge. 1 Coulomb = the charge transferred by a current of 1 Ampere flowing for 1 second (Q = It)."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Mole Concept",
 "questionText":"Avogadro's number (6.022 × 10²³) represents the number of particles in:",
 "options":["A: 1 gram of any substance","B: 1 mole of any substance","C: 1 litre of any gas","D: 1 molecule"],
 "correctAnswer":"B",
 "explanation":"One mole of any substance contains exactly 6.022 × 10²³ particles (atoms, molecules, or ions). This is Avogadro's number (Nₐ), the foundation of the mole concept in chemistry."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Biomolecules",
 "questionText":"DNA is made up of which type of monomers?",
 "options":["A: Amino acids","B: Fatty acids","C: Nucleotides","D: Monosaccharides"],
 "correctAnswer":"C",
 "explanation":"DNA (deoxyribonucleic acid) is a polymer made of nucleotide monomers. Each nucleotide consists of a deoxyribose sugar, a phosphate group, and one of four nitrogenous bases (A, T, G, C)."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Kinematics",
 "questionText":"An object thrown horizontally from a height follows which path?",
 "options":["A: Straight line","B: Circular arc","C: Parabolic path","D: Hyperbolic path"],
 "correctAnswer":"C",
 "explanation":"A horizontally thrown projectile has constant horizontal velocity and uniform downward acceleration (gravity). The combination produces a parabolic trajectory."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Chemical Equilibrium",
 "questionText":"A reaction is said to be at chemical equilibrium when:",
 "options":["A: All reactants are converted to products","B: The forward and reverse reaction rates are equal","C: No more reaction takes place","D: Temperature equals 0°C"],
 "correctAnswer":"B",
 "explanation":"Chemical equilibrium is reached when the rate of the forward reaction equals the rate of the reverse reaction. Concentrations of reactants and products remain constant (though both reactions continue)."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Photosynthesis",
 "questionText":"Which pigment in plants is primarily responsible for absorbing light for photosynthesis?",
 "options":["A: Haemoglobin","B: Chlorophyll","C: Carotenoid","D: Melanin"],
 "correctAnswer":"B",
 "explanation":"Chlorophyll (mainly chlorophyll-a and chlorophyll-b) is the primary photosynthetic pigment in plants. It absorbs red and blue light most strongly, and reflects green light — giving leaves their colour."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Thermodynamics",
 "questionText":"The First Law of Thermodynamics states that:",
 "options":["A: Heat always flows from cold to hot","B: Energy can be created from nothing","C: Energy cannot be created or destroyed, only converted","D: Entropy always decreases"],
 "correctAnswer":"C",
 "explanation":"First Law of Thermodynamics is the Law of Conservation of Energy: total energy in an isolated system is constant. Energy can be converted from one form to another but cannot be created or destroyed."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Periodic Properties",
 "questionText":"Which property decreases as you move from left to right across a period in the periodic table?",
 "options":["A: Electronegativity","B: Atomic radius","C: Ionisation energy","D: Nuclear charge"],
 "correctAnswer":"B",
 "explanation":"Atomic radius decreases across a period (left to right) because nuclear charge (protons) increases while electrons are added to the same shell, pulling them closer to the nucleus."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Animal Kingdom",
 "questionText":"Animals that maintain a constant body temperature regardless of environment are called:",
 "options":["A: Ectotherms","B: Poikilotherms","C: Endotherms (warm-blooded)","D: Heterotrophs"],
 "correctAnswer":"C",
 "explanation":"Endotherms (warm-blooded animals) — mammals and birds — maintain a constant internal body temperature. Ectotherms (cold-blooded — reptiles, fish, amphibians) depend on external heat sources."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Waves",
 "questionText":"The speed of a wave is related to its frequency and wavelength by:",
 "options":["A: v = f + λ","B: v = f / λ","C: v = f × λ","D: v = λ / f"],
 "correctAnswer":"C",
 "explanation":"Wave speed (v) = frequency (f) × wavelength (λ). This fundamental wave equation applies to all types of waves — light, sound, water waves, etc."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Organic Nomenclature",
 "questionText":"What is the IUPAC name for CH₃-CH₂-CH₃?",
 "options":["A: Methane","B: Ethane","C: Propane","D: Butane"],
 "correctAnswer":"C",
 "explanation":"CH₃-CH₂-CH₃ has 3 carbon atoms in a straight chain. IUPAC name: propane (prop = 3 carbons, -ane = alkane). Methane=1C, Ethane=2C, Butane=4C."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Human Physiology",
 "questionText":"The normal resting heart rate for a healthy adult is approximately:",
 "options":["A: 30-40 bpm","B: 60-100 bpm","C: 120-140 bpm","D: 150-200 bpm"],
 "correctAnswer":"B",
 "explanation":"A normal resting heart rate is 60–100 beats per minute (bpm) for adults. Athletes may have lower rates (40–60 bpm). Above 100 bpm is tachycardia; below 60 bpm is bradycardia."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Optics",
 "questionText":"The focal length of a concave lens is always:",
 "options":["A: Positive","B: Negative","C: Zero","D: Infinite"],
 "correctAnswer":"B",
 "explanation":"Using the sign convention, a concave (diverging) lens has a negative focal length. A convex (converging) lens has a positive focal length."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Hydrogen Bonding",
 "questionText":"Water has an unusually high boiling point for its molecular size because of:",
 "options":["A: Van der Waals forces","B: Ionic bonds","C: Hydrogen bonding","D: Covalent bonds within the molecule"],
 "correctAnswer":"C",
 "explanation":"Water molecules form extensive hydrogen bonds (O-H···O) due to oxygen's high electronegativity. Extra energy is needed to break these bonds during boiling, giving water a higher boiling point (100°C) than expected."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Ecology",
 "questionText":"The total variety of life on Earth — including species diversity, genetic diversity, and ecosystem diversity — is called:",
 "options":["A: Ecology","B: Biodiversity","C: Evolution","D: Taxonomy"],
 "correctAnswer":"B",
 "explanation":"Biodiversity encompasses all forms of life and their interactions: species diversity (variety of species), genetic diversity (variation within species), and ecosystem diversity (variety of habitats and ecological processes)."},

]

ok = dup = err = 0
for i, q in enumerate(questions, 1):
    try:
        r = insert(conn, q)
        if r == "DUP": dup += 1
        else: ok += 1
        label = q['subject'][:22].ljust(22)
        diff = q['difficulty'][:3].upper()
        print(f"  {r}  Q{i:03d} [{label} G{q['grade']} {diff}] {q['subTopic']}")
    except Exception as e:
        err += 1
        print(f"  ERR Q{i:03d}: {e}")

print(f"\n  Done: {ok} posted, {dup} duplicates, {err} errors  (total={ok+dup+err})")
conn.close()
