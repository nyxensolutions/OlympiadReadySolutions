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

# ── Science-Biology G10 Advanced (15q) ────────────────────────────────────────
{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Photosynthesis — Light Reactions",
 "questionText":"During the light-dependent reactions of photosynthesis, water molecules are split in a process called:",
 "options":["A: Phosphorylation","B: Photolysis","C: Photorespiration","D: Photophosphorylation"],
 "correctAnswer":"B",
 "explanation":"Photolysis (photo = light, lysis = splitting) is the light-driven splitting of water (2H₂O → 4H⁺ + 4e⁻ + O₂) in the thylakoid membrane. This is the source of the oxygen released during photosynthesis."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Enzyme Activity",
 "questionText":"An enzyme's active site is complementary in shape to its substrate. This concept is described by the:",
 "options":["A: Fluid mosaic model","B: Induced-fit model","C: Lock-and-key model","D: Sliding filament model"],
 "correctAnswer":"C",
 "explanation":"The lock-and-key model (Emil Fischer, 1894) describes the active site as a rigid structure perfectly complementary to its specific substrate, like a lock and its key."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"DNA Replication",
 "questionText":"During DNA replication, the enzyme that synthesises the new DNA strand is:",
 "options":["A: RNA polymerase","B: Ligase","C: Helicase","D: DNA polymerase"],
 "correctAnswer":"D",
 "explanation":"DNA polymerase reads the template strand and adds complementary nucleotides (5'→3' direction) to synthesise the new DNA strand. Helicase unwinds DNA; ligase joins Okazaki fragments."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Mendelian Genetics",
 "questionText":"In a monohybrid cross between two heterozygous parents (Aa × Aa), the expected genotypic ratio is:",
 "options":["A: 1:2:1 (AA:Aa:aa)","B: 3:1 (dominant:recessive)","C: 1:1 (Aa:aa)","D: 2:1:1 (AA:Aa:aa)"],
 "correctAnswer":"A",
 "explanation":"Aa × Aa produces genotypes: 1 AA : 2 Aa : 1 aa (ratio 1:2:1). The phenotypic ratio is 3:1 (dominant:recessive), but the genotypic ratio is 1:2:1."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Cell Division",
 "questionText":"Crossing over between non-sister chromatids occurs during which stage of meiosis?",
 "options":["A: Metaphase I","B: Prophase I","C: Anaphase II","D: Telophase I"],
 "correctAnswer":"B",
 "explanation":"Crossing over (exchange of genetic material between non-sister chromatids of homologous chromosomes) occurs during Prophase I of meiosis, at a stage called pachytene. It generates genetic variation."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Blood Groups",
 "questionText":"A person with blood group AB has which antibodies in the plasma?",
 "options":["A: Both anti-A and anti-B","B: Only anti-A","C: Only anti-B","D: Neither anti-A nor anti-B"],
 "correctAnswer":"D",
 "explanation":"AB blood group individuals have both A and B antigens on red blood cells and neither anti-A nor anti-B antibodies in their plasma — they are universal recipients for ABO blood transfusion."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Plant Hormones",
 "questionText":"Which plant hormone promotes cell elongation and is responsible for phototropism?",
 "options":["A: Cytokinin","B: Gibberellin","C: Ethylene","D: Auxin"],
 "correctAnswer":"D",
 "explanation":"Auxin (Indole-3-acetic acid) causes cell elongation. In phototropism, auxin migrates to the shaded side of the stem, causing those cells to elongate more, bending the plant towards light."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Nervous System",
 "questionText":"The myelin sheath around axons in neurons serves to:",
 "options":["A: Provide nutrients to the axon","B: Increase the speed of nerve impulse transmission","C: Prevent action potentials","D: Synthesise neurotransmitters"],
 "correctAnswer":"B",
 "explanation":"The myelin sheath (produced by Schwann cells) insulates the axon and enables saltatory conduction — the impulse jumps between nodes of Ranvier, greatly increasing transmission speed."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Ecosystem Energy Flow",
 "questionText":"The 10% rule in ecology states that when energy is transferred from one trophic level to the next, approximately what percentage is available?",
 "options":["A: 1%","B: 10%","C: 50%","D: 90%"],
 "correctAnswer":"B",
 "explanation":"Lindeman's 10% law: only about 10% of energy at one trophic level is transferred to the next. The remaining ~90% is lost as heat, used in metabolism, or remains in uneaten biomass."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Excretory System",
 "questionText":"The process by which the proximal convoluted tubule reabsorbs glucose from the filtrate is called:",
 "options":["A: Filtration","B: Selective reabsorption","C: Tubular secretion","D: Osmosis only"],
 "correctAnswer":"B",
 "explanation":"Selective reabsorption in the PCT recovers all glucose, amino acids, most water and salts back into the blood. Glucose reabsorption is an active process (requires ATP and carrier proteins)."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Reproductive Health",
 "questionText":"The placenta in mammals serves to:",
 "options":["A: Produce eggs","B: Exchange gases, nutrients and waste between mother and foetus","C: Produce testosterone","D: Form the amniotic sac only"],
 "correctAnswer":"B",
 "explanation":"The placenta is the interface between mother and foetus — it allows diffusion of oxygen, glucose and nutrients to the foetus, and removal of CO₂ and urea from foetal blood, without direct blood mixing."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Evolution",
 "questionText":"Darwin's theory of natural selection is based on which key observation?",
 "options":["A: Organisms mutate intentionally to survive","B: Individuals with heritable advantageous traits reproduce more successfully","C: All members of a species are genetically identical","D: The environment directly alters the genome"],
 "correctAnswer":"B",
 "explanation":"Natural selection: individuals with heritable traits better suited to their environment have higher reproductive success (survival of the fittest). Over generations this changes population gene frequencies."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Food Chain and Webs",
 "questionText":"Which of the following is a primary producer in a terrestrial ecosystem?",
 "options":["A: Grasshopper","B: Snake","C: Grass","D: Frog"],
 "correctAnswer":"C",
 "explanation":"Primary producers (autotrophs) make their own food through photosynthesis. Grass is a primary producer; grasshopper, frog, and snake are consumers."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Biotechnology",
 "questionText":"Restriction enzymes used in genetic engineering cut DNA at specific sequences called:",
 "options":["A: Codons","B: Promoters","C: Palindromic recognition sequences","D: Introns"],
 "correctAnswer":"C",
 "explanation":"Restriction enzymes (endonucleases) recognise specific palindromic sequences (same sequence read 5'→3' on both strands) and cut the DNA there, producing 'sticky ends' or 'blunt ends'."},

{"subject":"Science-Biology","grade":10,"difficulty":"Advanced","topic":"Biology",
 "subTopic":"Waste Management",
 "questionText":"Biodegradable waste is broken down by:",
 "options":["A: Ultraviolet light only","B: Microorganisms (bacteria and fungi)","C: High temperature alone","D: Chemical solvents"],
 "correctAnswer":"B",
 "explanation":"Biodegradable waste (food scraps, paper, cotton) is decomposed by microorganisms — bacteria and fungi act as decomposers, breaking organic matter into simpler inorganic compounds."},

# ── Science-Chemistry G10 Advanced (15q) ──────────────────────────────────────
{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Mole Concept",
 "questionText":"How many atoms are present in 12 g of carbon-12? (Avogadro's number = 6.022×10²³)",
 "options":["A: 6.022×10²²","B: 6.022×10²³","C: 1.204×10²⁴","D: 3.011×10²³"],
 "correctAnswer":"B",
 "explanation":"The molar mass of C-12 is exactly 12 g/mol. So 12 g = 1 mole = 6.022×10²³ atoms (Avogadro's number)."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Chemical Bonding",
 "questionText":"In a covalent bond, electrons are:",
 "options":["A: Transferred from one atom to another","B: Shared between atoms","C: Only in the outer shell of one atom","D: Lost by both atoms"],
 "correctAnswer":"B",
 "explanation":"In covalent bonding (non-metals + non-metals), electrons are shared between atoms so each achieves a stable noble-gas configuration. Ionic bonding involves electron transfer."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Oxidation and Reduction",
 "questionText":"In the reaction: CuO + H₂ → Cu + H₂O, hydrogen is:",
 "options":["A: Oxidised (loses oxygen)","B: Reduced (gains oxygen)","C: Neither oxidised nor reduced","D: The oxidising agent"],
 "correctAnswer":"A",
 "explanation":"H₂ gains oxygen (to form H₂O) — it is oxidised. CuO loses oxygen — it is reduced. H₂ is the reducing agent (it reduces CuO); CuO is the oxidising agent."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Ionic Compounds",
 "questionText":"Which property distinguishes ionic compounds from covalent compounds?",
 "options":["A: They are always gaseous at room temperature","B: They do not dissolve in water","C: They conduct electricity when dissolved in water or melted","D: They have low melting points"],
 "correctAnswer":"C",
 "explanation":"Ionic compounds have free ions when dissolved or melted, making them good electrolytes (conduct electricity). Covalent compounds generally do not conduct electricity."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Periodic Table — Trends",
 "questionText":"Going down a group in the periodic table, atomic radius:",
 "options":["A: Decreases","B: Stays the same","C: Increases","D: First increases then decreases"],
 "correctAnswer":"C",
 "explanation":"Going down a group, each successive element has an additional electron shell, increasing the atomic radius (despite also having more protons, the shielding effect outweighs nuclear attraction)."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Organic Chemistry — Homologous Series",
 "questionText":"What is the general formula for alkenes?",
 "options":["A: CₙH₂ₙ₊₂","B: CₙH₂ₙ","C: CₙH₂ₙ₋₂","D: CₙHₙ"],
 "correctAnswer":"B",
 "explanation":"Alkenes have one C=C double bond. General formula: CₙH₂ₙ. Alkanes are CₙH₂ₙ₊₂; alkynes are CₙH₂ₙ₋₂."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Acids — Properties",
 "questionText":"Which of the following is a strong acid that fully dissociates in water?",
 "options":["A: Acetic acid (CH₃COOH)","B: Carbonic acid (H₂CO₃)","C: Hydrochloric acid (HCl)","D: Citric acid"],
 "correctAnswer":"C",
 "explanation":"HCl is a strong acid — it dissociates completely (HCl → H⁺ + Cl⁻). Acetic, carbonic, and citric acids are weak acids that only partially dissociate."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Electrolysis",
 "questionText":"During the electrolysis of dilute sulphuric acid, which gas is produced at the cathode?",
 "options":["A: Oxygen","B: Sulphur dioxide","C: Chlorine","D: Hydrogen"],
 "correctAnswer":"D",
 "explanation":"At the cathode (negative electrode), H⁺ ions from the acid are reduced: 2H⁺ + 2e⁻ → H₂. Oxygen is produced at the anode by oxidation of water/OH⁻."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Corrosion Prevention",
 "questionText":"Stainless steel is corrosion-resistant because it contains which element along with iron?",
 "options":["A: Copper","B: Chromium","C: Zinc","D: Nickel only"],
 "correctAnswer":"B",
 "explanation":"Stainless steel contains at least 10.5% chromium, which forms a thin invisible oxide layer (Cr₂O₃) on the surface, passivating it and preventing further corrosion."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Rate of Reaction",
 "questionText":"Which factor does NOT affect the rate of a chemical reaction?",
 "options":["A: Temperature","B: Concentration of reactants","C: Colour of the reactants","D: Presence of a catalyst"],
 "correctAnswer":"C",
 "explanation":"Reaction rate is affected by temperature, concentration, surface area, and catalysts — all of which affect collision frequency or activation energy. Colour is a physical property that does not affect reaction rate."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Carbon — Functional Groups",
 "questionText":"The functional group –OH (hydroxyl) characterises which class of organic compounds?",
 "options":["A: Aldehydes","B: Alcohols","C: Carboxylic acids","D: Esters"],
 "correctAnswer":"B",
 "explanation":"The –OH (hydroxyl) group defines alcohols (e.g., ethanol C₂H₅OH). Aldehydes have –CHO; carboxylic acids have –COOH; esters have –COO–."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Neutralisation",
 "questionText":"When an acid reacts with a base, the products are:",
 "options":["A: Only water","B: Only salt","C: Salt and water","D: Gas and salt"],
 "correctAnswer":"C",
 "explanation":"Neutralisation: acid + base → salt + water. For example: HCl + NaOH → NaCl + H₂O. This is a double displacement reaction."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Metals — Reactivity",
 "questionText":"Aluminium is above zinc in the reactivity series, yet aluminium household utensils do not corrode easily because:",
 "options":["A: Aluminium is non-reactive","B: Aluminium forms a protective oxide layer","C: Aluminium reacts only with acids","D: Aluminium is coated with zinc"],
 "correctAnswer":"B",
 "explanation":"Aluminium rapidly forms a thin, tough layer of aluminium oxide (Al₂O₃) when exposed to air. This passive layer prevents further oxidation/corrosion, making it very durable despite its high reactivity."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Chemical Formulae",
 "questionText":"The chemical formula of washing soda is:",
 "options":["A: NaHCO₃","B: Na₂CO₃·10H₂O","C: CaCO₃","D: MgSO₄·7H₂O"],
 "correctAnswer":"B",
 "explanation":"Washing soda is sodium carbonate decahydrate (Na₂CO₃·10H₂O). Baking soda is NaHCO₃; limestone is CaCO₃; Epsom salt is MgSO₄·7H₂O."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Advanced","topic":"Chemistry",
 "subTopic":"Saponification",
 "questionText":"Soaps are made by treating fats/oils with concentrated sodium hydroxide. This process is called:",
 "options":["A: Hydrogenation","B: Esterification","C: Saponification","D: Fermentation"],
 "correctAnswer":"C",
 "explanation":"Saponification is the alkaline hydrolysis of triglycerides (fats/oils) with NaOH or KOH to produce soap (sodium/potassium fatty acid salts) and glycerol."},

# ── Science-Physics G10 Advanced (15q) ────────────────────────────────────────
{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Snell's Law",
 "questionText":"The refractive index of glass with respect to air is 1.5. If the speed of light in air is 3×10⁸ m/s, the speed of light in glass is:",
 "options":["A: 4.5×10⁸ m/s","B: 3×10⁸ m/s","C: 2×10⁸ m/s","D: 1.5×10⁸ m/s"],
 "correctAnswer":"C",
 "explanation":"Refractive index n = speed in vacuum / speed in medium. So speed in glass = 3×10⁸ / 1.5 = 2×10⁸ m/s."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Kirchhoff's Laws",
 "questionText":"Three resistors of 4Ω, 6Ω, and 12Ω are connected in parallel. The equivalent resistance is:",
 "options":["A: 22Ω","B: 2Ω","C: 4Ω","D: 6Ω"],
 "correctAnswer":"B",
 "explanation":"1/R = 1/4 + 1/6 + 1/12 = 3/12 + 2/12 + 1/12 = 6/12 = 1/2. So R = 2Ω."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Lens Formula",
 "questionText":"Using the lens formula (1/v − 1/u = 1/f), if an object is placed at u = −30 cm from a convex lens of focal length f = +10 cm, the image distance v is:",
 "options":["A: +15 cm","B: −15 cm","C: +30 cm","D: +20 cm"],
 "correctAnswer":"A",
 "explanation":"1/v = 1/f + 1/u = 1/10 + 1/(−30) = 3/30 − 1/30 = 2/30. So v = 15 cm. The positive sign means the image is on the other side of the lens (real image)."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Joule's Law",
 "questionText":"A 60W bulb is switched on for 2 hours. How many units (kWh) of electrical energy does it consume?",
 "options":["A: 0.06 kWh","B: 0.12 kWh","C: 1.2 kWh","D: 0.6 kWh"],
 "correctAnswer":"B",
 "explanation":"Energy = Power × Time = 60W × 2h = 120 Wh = 0.12 kWh. (1 unit = 1 kWh = 1000 Wh)."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Fleming's Rules",
 "questionText":"Fleming's right-hand rule is used to determine the direction of induced current in:",
 "options":["A: Electric motor","B: Transformer","C: Electric generator","D: Resistor"],
 "correctAnswer":"C",
 "explanation":"Fleming's right-hand rule (dynamo rule) gives the direction of induced current in a generator. Fleming's left-hand rule (motor rule) is used for the force on a conductor in a motor."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Total Internal Reflection",
 "questionText":"Total internal reflection occurs when light travels from:",
 "options":["A: Rarer to denser medium at any angle","B: Denser to rarer medium at an angle greater than the critical angle","C: Air to water","D: Vacuum to glass"],
 "correctAnswer":"B",
 "explanation":"TIR occurs only when light moves from a denser (higher refractive index) to a rarer medium AND the angle of incidence exceeds the critical angle. Used in optical fibres."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Electromagnetic Spectrum",
 "questionText":"Which electromagnetic radiation has the highest frequency?",
 "options":["A: Radio waves","B: Infrared","C: Ultraviolet","D: Gamma rays"],
 "correctAnswer":"D",
 "explanation":"Order of EM spectrum by increasing frequency: Radio < Microwave < Infrared < Visible < Ultraviolet < X-rays < Gamma rays. Gamma rays have the highest frequency and energy."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Magnets — Field Lines",
 "questionText":"Two north poles placed near each other will:",
 "options":["A: Attract each other","B: Repel each other","C: Show no interaction","D: One will become south pole"],
 "correctAnswer":"B",
 "explanation":"Like poles repel; unlike poles attract. Two north poles repel each other. This is the fundamental law of magnetism."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Power and Energy",
 "questionText":"A household uses 5 appliances of 1000W each for 8 hours daily. The daily energy consumption in kWh is:",
 "options":["A: 20 kWh","B: 40 kWh","C: 5 kWh","D: 8 kWh"],
 "correctAnswer":"B",
 "explanation":"Total power = 5 × 1000W = 5000W = 5kW. Energy = 5kW × 8h = 40 kWh per day."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Concave Mirror",
 "questionText":"A concave mirror of focal length 15 cm. An object is placed 30 cm from the mirror. The image is formed at:",
 "options":["A: 30 cm, real and inverted","B: 15 cm, virtual and erect","C: 30 cm, virtual and erect","D: 60 cm, real and inverted"],
 "correctAnswer":"A",
 "explanation":"Mirror formula: 1/v + 1/u = 1/f. Using sign convention: u = −30, f = −15 (concave). 1/v = 1/f − 1/u = −1/15 + 1/30 = −2/30 + 1/30 = −1/30. So v = −30 cm (real, inverted, same size)."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Ohm's Law — Applications",
 "questionText":"A resistor draws a current of 2A when connected to a 10V source. What is the resistance?",
 "options":["A: 20Ω","B: 5Ω","C: 0.2Ω","D: 12Ω"],
 "correctAnswer":"B",
 "explanation":"Ohm's law: R = V/I = 10V / 2A = 5Ω."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Scattering of Light",
 "questionText":"The sky appears blue because:",
 "options":["A: The sea reflects blue light into the sky","B: Blue light is scattered more than red light by air molecules (Rayleigh scattering)","C: The atmosphere absorbs all colours except blue","D: Blue light has a longer wavelength than other colours"],
 "correctAnswer":"B",
 "explanation":"Rayleigh scattering: shorter wavelengths (violet/blue) are scattered ~10× more than longer wavelengths (red). The sky appears blue (not violet) because our eyes are more sensitive to blue and because violet is absorbed in the upper atmosphere."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"AC and DC",
 "questionText":"In India, the standard frequency of alternating current (AC) supplied to homes is:",
 "options":["A: 50 Hz","B: 60 Hz","C: 100 Hz","D: 25 Hz"],
 "correctAnswer":"A",
 "explanation":"India uses 50 Hz AC at 230V for domestic supply. The USA uses 60 Hz. The frequency determines how often the current direction reverses per second (50 times/second in India)."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Renewable Energy",
 "questionText":"A solar cell (photovoltaic cell) converts:",
 "options":["A: Heat energy to electrical energy","B: Chemical energy to electrical energy","C: Light energy to electrical energy","D: Mechanical energy to electrical energy"],
 "correctAnswer":"C",
 "explanation":"Solar (photovoltaic) cells use the photovoltaic effect to convert light energy (photons) directly into electrical energy through the semiconductor p-n junction."},

{"subject":"Science-Physics","grade":10,"difficulty":"Advanced","topic":"Physics",
 "subTopic":"Nuclear Energy",
 "questionText":"Nuclear fission involves:",
 "options":["A: Combining two light nuclei to release energy","B: Splitting a heavy nucleus into smaller fragments with release of energy","C: Radioactive decay only","D: Fusion of protons and neutrons"],
 "correctAnswer":"B",
 "explanation":"Nuclear fission: a heavy nucleus (e.g., U-235) absorbs a neutron and splits into smaller nuclei, releasing 2–3 neutrons and large amounts of energy. Nuclear fusion combines light nuclei (e.g., hydrogen isotopes)."},

# ── Computer Science G12 top-up (5q Foundation + 5q Advanced + 5q Olympiad) ───
{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science",
 "subTopic":"Database Management",
 "questionText":"In a relational database, the attribute used to uniquely identify each record in a table is called:",
 "options":["A: Foreign key","B: Primary key","C: Candidate key","D: Composite key"],
 "correctAnswer":"B",
 "explanation":"A primary key uniquely identifies each row in a relational database table. It must be unique and cannot be NULL. A foreign key references the primary key of another table."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science",
 "subTopic":"Python Programming",
 "questionText":"What is the output of: print(type(3.14))?",
 "options":["A: <class 'int'>","B: <class 'float'>","C: <class 'str'>","D: <class 'double'>"],
 "correctAnswer":"B",
 "explanation":"3.14 is a floating-point literal in Python. type(3.14) returns <class 'float'>. Python does not have a separate 'double' type."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science",
 "subTopic":"Boolean Logic",
 "questionText":"The truth value of (True AND False) OR True is:",
 "options":["A: False","B: True","C: None","D: Error"],
 "correctAnswer":"B",
 "explanation":"Step by step: True AND False = False. Then False OR True = True. The final result is True."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science",
 "subTopic":"Networking",
 "questionText":"HTTP stands for:",
 "options":["A: HyperText Transfer Protocol","B: High Transfer Text Process","C: HyperText Transmission Program","D: High Text Transfer Protocol"],
 "correctAnswer":"A",
 "explanation":"HTTP (HyperText Transfer Protocol) is the foundation protocol of data communication on the World Wide Web. HTTPS adds a layer of encryption (TLS/SSL)."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science",
 "subTopic":"Operating System",
 "questionText":"Which type of operating system allows multiple users to use a computer simultaneously?",
 "options":["A: Single-user OS","B: Real-time OS","C: Multi-user OS","D: Embedded OS"],
 "correctAnswer":"C",
 "explanation":"A multi-user OS (e.g., Unix/Linux) allows multiple users to access the system simultaneously through time-sharing, with the OS managing resources between users."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science",
 "subTopic":"Sorting Algorithms",
 "questionText":"What is the worst-case time complexity of Quick Sort?",
 "options":["A: O(n log n)","B: O(n)","C: O(n²)","D: O(log n)"],
 "correctAnswer":"C",
 "explanation":"Quick Sort has average-case complexity O(n log n) but degrades to O(n²) in the worst case (e.g., when the pivot is always the smallest or largest element — sorted or reverse-sorted input)."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science",
 "subTopic":"SQL",
 "questionText":"Which SQL clause is used to filter groups (after GROUP BY) based on a condition?",
 "options":["A: WHERE","B: HAVING","C: FILTER","D: WHEN"],
 "correctAnswer":"B",
 "explanation":"HAVING filters groups after aggregation (GROUP BY). WHERE filters individual rows before grouping. Example: SELECT dept, AVG(salary) FROM emp GROUP BY dept HAVING AVG(salary) > 50000."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science",
 "subTopic":"Object-Oriented Programming",
 "questionText":"The concept of accessing objects of different classes through the same interface is called:",
 "options":["A: Encapsulation","B: Inheritance","C: Polymorphism","D: Abstraction"],
 "correctAnswer":"C",
 "explanation":"Polymorphism (Greek: 'many forms') allows objects of different classes to be treated through a common interface. Method overloading and overriding are forms of polymorphism."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science",
 "subTopic":"Number Systems",
 "questionText":"Convert hexadecimal 1F to decimal:",
 "options":["A: 30","B: 31","C: 35","D: 27"],
 "correctAnswer":"B",
 "explanation":"1F in hex: 1×16¹ + F×16⁰ = 16 + 15 = 31 in decimal."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science",
 "subTopic":"Stack Data Structure",
 "questionText":"In a Stack, the last element added is the first one removed. This follows the principle:",
 "options":["A: FIFO","B: LIFO","C: FILO only","D: Random access"],
 "correctAnswer":"B",
 "explanation":"A Stack follows LIFO (Last In, First Out). The last element pushed is the first to be popped. Used in function call stacks, undo operations, expression evaluation."},

{"subject":"Computer Science","grade":12,"difficulty":"Olympiad","topic":"Computer Science",
 "subTopic":"Complexity Theory",
 "questionText":"An algorithm with time complexity O(2ⁿ) is called:",
 "options":["A: Polynomial","B: Linear","C: Exponential","D: Logarithmic"],
 "correctAnswer":"C",
 "explanation":"O(2ⁿ) is exponential time complexity — the runtime doubles with each additional input element. NP-hard problems (like brute-force subset sum) often have exponential worst-case complexity."},

{"subject":"Computer Science","grade":12,"difficulty":"Olympiad","topic":"Computer Science",
 "subTopic":"Graph Algorithms",
 "questionText":"Dijkstra's algorithm is used to find:",
 "options":["A: Minimum spanning tree","B: Shortest path from a source to all vertices in a weighted graph","C: Strongly connected components","D: Maximum flow in a network"],
 "correctAnswer":"B",
 "explanation":"Dijkstra's algorithm finds the shortest (minimum weight) path from a single source vertex to all other vertices in a graph with non-negative edge weights. Time complexity: O(V² ) or O((V+E) log V) with a priority queue."},

{"subject":"Computer Science","grade":12,"difficulty":"Olympiad","topic":"Computer Science",
 "subTopic":"Recursion",
 "questionText":"The recursive Fibonacci function fib(n) = fib(n-1) + fib(n-2) without memoisation has time complexity:",
 "options":["A: O(n)","B: O(n log n)","C: O(n²)","D: O(2ⁿ)"],
 "correctAnswer":"D",
 "explanation":"Without memoisation, naive recursive Fibonacci recalculates subproblems exponentially. The recurrence T(n) = T(n-1)+T(n-2) solves to approximately O(φⁿ) ≈ O(2ⁿ) where φ = 1.618 (golden ratio)."},

{"subject":"Computer Science","grade":12,"difficulty":"Olympiad","topic":"Computer Science",
 "subTopic":"Hashing",
 "questionText":"The average-case time complexity for search, insert, and delete in a hash table is:",
 "options":["A: O(n)","B: O(log n)","C: O(1)","D: O(n log n)"],
 "correctAnswer":"C",
 "explanation":"Hash tables provide O(1) average-case time for search, insert, and delete because the hash function directly maps keys to positions. Worst case (many collisions) degrades to O(n)."},

{"subject":"Computer Science","grade":12,"difficulty":"Olympiad","topic":"Computer Science",
 "subTopic":"Dynamic Programming",
 "questionText":"Dynamic programming improves on brute force by:",
 "options":["A: Using randomisation","B: Storing solutions to overlapping subproblems to avoid recomputation","C: Dividing the problem into independent subproblems","D: Using greedy choices at each step"],
 "correctAnswer":"B",
 "explanation":"Dynamic programming (Bellman, 1950s) uses memoisation or tabulation to store previously computed solutions to subproblems, so overlapping subproblems are solved only once — dramatically reducing time complexity."},

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
