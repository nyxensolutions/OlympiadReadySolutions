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

# ── Science-Biology G10 Olympiad (15q) ────────────────────────────────────────
{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Calvin Cycle",
 "questionText":"In which cycle is atmospheric CO₂ fixed into organic molecules during photosynthesis?",
 "options":["A: Krebs cycle","B: Calvin cycle","C: Nitrogen cycle","D: Urea cycle"],
 "correctAnswer":"B",
 "explanation":"The Calvin cycle (dark reactions/light-independent reactions) occurs in the stroma of chloroplasts. CO₂ is fixed by RuBisCO enzyme into 3-carbon compounds, ultimately producing G3P for glucose synthesis."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Cell Organelles",
 "questionText":"The 'powerhouse of the cell' is the mitochondrion because it:",
 "options":["A: Stores genetic information","B: Produces ATP through cellular respiration","C: Manufactures proteins","D: Controls cell division"],
 "correctAnswer":"B",
 "explanation":"Mitochondria produce ATP (adenosine triphosphate) through aerobic respiration — glycolysis in cytoplasm, then Krebs cycle and oxidative phosphorylation in mitochondrial matrix and inner membrane."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Protein Synthesis",
 "questionText":"The process of translating mRNA codons into a protein sequence occurs at:",
 "options":["A: The nucleus","B: The Golgi apparatus","C: Ribosomes","D: Lysosomes"],
 "correctAnswer":"C",
 "explanation":"Translation (protein synthesis) occurs at ribosomes. mRNA carries the genetic code from the nucleus; ribosomes read codons and tRNA brings amino acids, assembling the polypeptide chain."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Immune System",
 "questionText":"Antibodies are produced by which type of blood cell?",
 "options":["A: T-lymphocytes","B: B-lymphocytes (plasma cells)","C: Neutrophils","D: Red blood cells"],
 "correctAnswer":"B",
 "explanation":"B-lymphocytes differentiate into plasma cells upon activation and secrete antibodies (immunoglobulins) that specifically bind to and neutralise antigens."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Osmoregulation",
 "questionText":"ADH (antidiuretic hormone) acts on the kidneys to:",
 "options":["A: Decrease water reabsorption, producing dilute urine","B: Increase water reabsorption, producing concentrated urine","C: Increase sodium excretion","D: Stimulate urine production"],
 "correctAnswer":"B",
 "explanation":"ADH (vasopressin) is released when blood is too concentrated. It increases the permeability of the collecting duct and DCT to water, allowing more water reabsorption and producing more concentrated urine."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Hardy-Weinberg Equilibrium",
 "questionText":"The Hardy-Weinberg principle states that allele frequencies in a population remain constant when:",
 "options":["A: Mutation rates are high","B: The population is large and random mating occurs with no selection/mutation/migration","C: Natural selection is strong","D: The population is small and isolated"],
 "correctAnswer":"B",
 "explanation":"Hardy-Weinberg equilibrium requires: large population, random mating, no mutation, no gene flow, no natural selection. These conditions establish that allele/genotype frequencies stay constant generation after generation."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Endocrine System",
 "questionText":"Insulin is produced by which cells of the pancreas?",
 "options":["A: Alpha cells","B: Beta cells","C: Delta cells","D: Acinar cells"],
 "correctAnswer":"B",
 "explanation":"Insulin is secreted by beta cells (β-cells) of the islets of Langerhans in the pancreas. Glucagon is secreted by alpha cells. Insulin lowers blood glucose by promoting glucose uptake."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Genetic Disorders",
 "questionText":"Down syndrome (Trisomy 21) is caused by:",
 "options":["A: A point mutation in chromosome 21","B: Presence of three copies of chromosome 21","C: Deletion of part of chromosome 21","D: Monosomy of chromosome 21"],
 "correctAnswer":"B",
 "explanation":"Down syndrome results from non-disjunction during meiosis, leading to three copies of chromosome 21 (trisomy 21). Affected individuals have 47 chromosomes instead of 46."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Symbiosis",
 "questionText":"Rhizobium bacteria living in root nodules of leguminous plants demonstrate which type of relationship?",
 "options":["A: Parasitism","B: Commensalism","C: Mutualism","D: Predation"],
 "correctAnswer":"C",
 "explanation":"Mutualism: both organisms benefit. Rhizobium fixes atmospheric nitrogen for the plant (which gets amino acids); in return, the plant provides carbohydrates and shelter to the bacteria."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Transpiration",
 "questionText":"The opening and closing of stomata is controlled by:",
 "options":["A: Mesophyll cells","B: Guard cells","C: Xylem vessels","D: Root hair cells"],
 "correctAnswer":"B",
 "explanation":"Guard cells flank each stoma and regulate its aperture. When guard cells become turgid (gain water), the stoma opens; when flaccid (lose water), it closes."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Biotechnology — GM Crops",
 "questionText":"Bt cotton is genetically modified to produce a toxin from:",
 "options":["A: Bacillus thuringiensis","B: Bifidobacterium thermophilum","C: Bartonella taxiensis","D: Brevibacterium toxicum"],
 "correctAnswer":"A",
 "explanation":"Bt crops express the Cry protein gene from Bacillus thuringiensis — a soil bacterium. The protein is toxic to certain insect larvae (bollworm, corn borer) but harmless to humans and most other organisms."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Ecological Pyramids",
 "questionText":"An inverted pyramid of biomass can be seen in which ecosystem?",
 "options":["A: Tropical rainforest","B: Grassland","C: Aquatic/marine ecosystem","D: Desert"],
 "correctAnswer":"C",
 "explanation":"In aquatic ecosystems, phytoplankton (producers) have very short lifespans and rapid turnover, so the biomass of producers at any given time may be less than that of consumers — producing an inverted biomass pyramid."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Neurotransmitters",
 "questionText":"The neurotransmitter acetylcholine is broken down at the synapse by the enzyme:",
 "options":["A: Acetyl CoA","B: Acetylcholinesterase","C: Monoamine oxidase","D: Dopaminase"],
 "correctAnswer":"B",
 "explanation":"Acetylcholinesterase (AChE) rapidly breaks down acetylcholine in the synaptic cleft into acetate and choline, terminating the nerve signal. Organophosphate pesticides inhibit AChE."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Stem Cells",
 "questionText":"Embryonic stem cells are described as 'pluripotent' because they:",
 "options":["A: Can live outside the body indefinitely","B: Can give rise to almost all cell types of the body","C: Can divide without limit causing cancer","D: Can only form blood cells"],
 "correctAnswer":"B",
 "explanation":"Pluripotent stem cells can differentiate into nearly all ~200 cell types found in the human body (but not extraembryonic tissue). Totipotent cells (zygote) can form all cell types including placental cells."},

{"subject":"Science-Biology","grade":10,"difficulty":"Olympiad","topic":"Biology",
 "subTopic":"Biogeochemical Cycles",
 "questionText":"The process by which bacteria convert nitrates in soil back to atmospheric nitrogen is:",
 "options":["A: Nitrification","B: Ammonification","C: Denitrification","D: Nitrogen fixation"],
 "correctAnswer":"C",
 "explanation":"Denitrification is carried out by anaerobic bacteria (e.g., Pseudomonas) in waterlogged soils, converting nitrates (NO₃⁻) → nitrites (NO₂⁻) → N₂ gas, returning nitrogen to the atmosphere."},

# ── Science-Chemistry G10 Olympiad (15q) ──────────────────────────────────────
{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Equilibrium",
 "questionText":"Le Chatelier's principle states that if a stress is applied to a system at equilibrium, the equilibrium will shift to:",
 "options":["A: Increase the stress","B: Oppose and reduce the stress","C: Maintain the same concentrations","D: Stop the reaction"],
 "correctAnswer":"B",
 "explanation":"Le Chatelier's principle: a system at equilibrium shifts to counteract any change (stress) — increase in reactant concentration → shift towards products; increase in pressure for gases → shift towards fewer moles."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Electrochemistry",
 "questionText":"In an electrochemical cell, oxidation occurs at the:",
 "options":["A: Cathode","B: Salt bridge","C: Anode","D: Electrolyte only"],
 "correctAnswer":"C",
 "explanation":"Mnemonic: 'OIL RIG' — Oxidation Is Loss (of electrons), Reduction Is Gain. Oxidation occurs at the anode (AnOde = OxidAtion); reduction occurs at the cathode."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Stoichiometry",
 "questionText":"In the reaction 2H₂ + O₂ → 2H₂O, how many moles of water are produced from 4 moles of H₂?",
 "options":["A: 2","B: 4","C: 8","D: 1"],
 "correctAnswer":"B",
 "explanation":"Molar ratio of H₂ to H₂O is 2:2 = 1:1. So 4 moles of H₂ produces 4 moles of H₂O."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Periodic Table — Periods",
 "questionText":"Which period 3 element is a noble gas?",
 "options":["A: Neon","B: Argon","C: Sodium","D: Chlorine"],
 "correctAnswer":"B",
 "explanation":"Period 3 runs from Na (Z=11) to Ar (Z=18). Argon (Z=18) is the noble gas at the end of period 3. Neon is in period 2."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Isomerism",
 "questionText":"Compounds with the same molecular formula but different structural arrangements are called:",
 "options":["A: Allotropes","B: Isotopes","C: Structural isomers","D: Polymers"],
 "correctAnswer":"C",
 "explanation":"Structural (constitutional) isomers have the same molecular formula but different connectivity of atoms. Example: n-butane and isobutane are both C₄H₁₀ but differ in structure."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Thermochemistry",
 "questionText":"An exothermic reaction is one in which:",
 "options":["A: Heat is absorbed from the surroundings","B: Heat is released to the surroundings","C: No energy change occurs","D: The reactants have less energy than the surroundings"],
 "correctAnswer":"B",
 "explanation":"In exothermic reactions, chemical energy is converted to heat and released (ΔH < 0). Examples: combustion, neutralisation, oxidation of metals. Endothermic reactions absorb heat (ΔH > 0)."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Colligative Properties",
 "questionText":"Adding a solute to a pure solvent causes its boiling point to:",
 "options":["A: Decrease","B: Stay the same","C: Increase","D: Depends only on solvent"],
 "correctAnswer":"C",
 "explanation":"Boiling point elevation is a colligative property — adding solute particles raises the boiling point proportionally to molal concentration. Salt added to water raises its boiling point above 100°C."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Chromatography",
 "questionText":"In paper chromatography, the component that travels the farthest from the origin has the:",
 "options":["A: Least affinity for the mobile phase","B: Most affinity for the stationary phase","C: Highest Rf value","D: Lowest Rf value"],
 "correctAnswer":"C",
 "explanation":"Rf = distance travelled by component / distance travelled by solvent. Higher Rf means the component moves farther — it has greater affinity for the mobile phase relative to the stationary phase."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Alloys",
 "questionText":"Bronze is an alloy of:",
 "options":["A: Iron and carbon","B: Copper and zinc","C: Copper and tin","D: Aluminium and magnesium"],
 "correctAnswer":"C",
 "explanation":"Bronze = copper + tin (typically ~88% Cu, 12% Sn). Brass = copper + zinc. Steel = iron + carbon. Bronze has been used since ~3300 BCE in the Bronze Age."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Chemical Bonding — Polarity",
 "questionText":"Water (H₂O) has a bent molecular structure, making it:",
 "options":["A: Non-polar","B: Polar","C: Ionic","D: Non-bonded"],
 "correctAnswer":"B",
 "explanation":"In H₂O, oxygen is more electronegative than hydrogen, creating polar O-H bonds. The bent geometry means the dipoles don't cancel, resulting in a polar molecule with a net dipole moment."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Concentration",
 "questionText":"Molarity is defined as:",
 "options":["A: Moles of solute per kg of solvent","B: Moles of solute per litre of solution","C: Grams of solute per 100 mL of solution","D: Volume of solute per volume of solution"],
 "correctAnswer":"B",
 "explanation":"Molarity (M) = moles of solute / volume of solution in litres. It is the most commonly used concentration unit in chemistry. Molality uses kg of solvent."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Organic Reactions",
 "questionText":"The reaction of ethanol (C₂H₅OH) with ethanoic acid (CH₃COOH) in the presence of H₂SO₄ is an example of:",
 "options":["A: Saponification","B: Esterification","C: Hydrogenation","D: Halogenation"],
 "correctAnswer":"B",
 "explanation":"Esterification: alcohol + carboxylic acid → ester + water (with acid catalyst). Ethanol + ethanoic acid → ethyl ethanoate (a sweet-smelling ester) + water."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Electroplating",
 "questionText":"During electroplating, the object to be plated is connected to:",
 "options":["A: The positive terminal (anode)","B: The negative terminal (cathode)","C: Either terminal","D: The salt bridge"],
 "correctAnswer":"B",
 "explanation":"In electroplating, the object to be plated is the cathode (connected to –ve). Metal ions from the electrolyte gain electrons at the cathode and deposit as a metal coating."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Radioactivity",
 "questionText":"Which type of radioactive emission has the greatest penetrating power?",
 "options":["A: Alpha (α) particles","B: Beta (β) particles","C: Gamma (γ) rays","D: All have equal penetration"],
 "correctAnswer":"C",
 "explanation":"Penetrating power: γ > β > α. Gamma rays are high-energy photons with no charge or mass — they penetrate several cm of lead. Alpha particles are stopped by a sheet of paper."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Olympiad","topic":"Chemistry",
 "subTopic":"Catalysis",
 "questionText":"A catalyst speeds up a chemical reaction by:",
 "options":["A: Increasing the temperature","B: Providing an alternative reaction pathway with lower activation energy","C: Increasing reactant concentration","D: Being consumed in the reaction"],
 "correctAnswer":"B",
 "explanation":"A catalyst provides an alternative pathway with lower activation energy. It is not consumed (can be recovered unchanged). More reactant molecules have sufficient energy to react — increasing rate."},

# ── Science-Physics G10 Olympiad (15q) ────────────────────────────────────────
{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Wave Optics",
 "questionText":"Young's double-slit experiment demonstrated the wave nature of light by producing:",
 "options":["A: Photoelectric effect","B: Interference fringes","C: Total internal reflection","D: Diffraction only"],
 "correctAnswer":"B",
 "explanation":"Thomas Young (1801) passed light through two closely spaced slits. The overlapping wavefronts produced alternating bright and dark interference fringes, proving light has wave nature."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Photoelectric Effect",
 "questionText":"Einstein's explanation of the photoelectric effect proposed that light consists of:",
 "options":["A: Continuous waves","B: Discrete packets of energy called photons","C: Magnetic fields only","D: Electrons"],
 "correctAnswer":"B",
 "explanation":"Einstein proposed light is made of photons — discrete quanta of energy E = hf (h = Planck's constant, f = frequency). Each photon can eject one electron if E ≥ work function. This earned him the 1921 Nobel Prize."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Transformer",
 "questionText":"A step-up transformer has 100 turns in the primary and 1000 turns in the secondary. If the primary voltage is 220V, the secondary voltage is:",
 "options":["A: 22V","B: 220V","C: 2200V","D: 100V"],
 "correctAnswer":"C",
 "explanation":"Transformer equation: Vs/Vp = Ns/Np. Vs = 220 × (1000/100) = 220 × 10 = 2200V. A step-up transformer increases voltage; step-down decreases it."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Semiconductor Physics",
 "questionText":"In a p-n junction diode, current flows easily when:",
 "options":["A: Reverse-biased (p-side connected to negative, n-side to positive)","B: Forward-biased (p-side connected to positive, n-side to negative)","C: No bias is applied","D: AC current is applied only"],
 "correctAnswer":"B",
 "explanation":"Forward bias reduces the depletion region width, allowing majority carriers to flow — conventional current flows from p to n externally. Reverse bias increases the depletion region and blocks current (except leakage)."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Quantum Theory",
 "questionText":"Planck's constant h has units of:",
 "options":["A: Joules","B: Joule-seconds","C: Watts","D: Metres per second"],
 "correctAnswer":"B",
 "explanation":"Planck's constant h = 6.626×10⁻³⁴ J·s (joule-seconds). It appears in E = hf (energy of a photon) where E is in joules and f is in Hz (s⁻¹), so h must have units of J/Hz = J·s."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Doppler Effect",
 "questionText":"The Doppler effect states that when a sound source moves towards an observer, the observed frequency:",
 "options":["A: Decreases","B: Stays the same","C: Increases","D: Depends only on amplitude"],
 "correctAnswer":"C",
 "explanation":"When source and observer approach each other, wavefronts are compressed — the observed frequency is higher than the emitted frequency. When moving apart, frequency decreases (lower pitch)."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Bernoulli's Principle",
 "questionText":"An aircraft wing generates lift because of Bernoulli's principle — the pressure above the wing is:",
 "options":["A: Higher than below","B: Equal to below","C: Lower than below","D: Dependent only on the wing area"],
 "correctAnswer":"C",
 "explanation":"The curved (cambered) upper surface makes air travel faster over the wing than under it. By Bernoulli's principle, faster airflow = lower pressure. The pressure difference creates upward lift."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Nuclear Reactions",
 "questionText":"In nuclear fusion, large amounts of energy are released because:",
 "options":["A: Heavy nuclei are split","B: The mass of the products is slightly less than the reactants, and this mass is converted to energy (E=mc²)","C: Electrons are removed from atoms","D: Radioactive isotopes decay"],
 "correctAnswer":"B",
 "explanation":"In fusion (and fission), the products have slightly less mass than the reactants. This mass defect (Δm) is converted to energy by Einstein's E = mc² (c = 3×10⁸ m/s), releasing enormous energy."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Capacitors",
 "questionText":"A capacitor stores energy in the form of:",
 "options":["A: Magnetic field","B: Electric field","C: Chemical energy","D: Mechanical energy"],
 "correctAnswer":"B",
 "explanation":"A capacitor stores electrical energy in the electric field between its plates. Energy stored = ½CV². Inductors store energy in magnetic fields."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Special Relativity",
 "questionText":"Einstein's special theory of relativity states that the speed of light in vacuum is:",
 "options":["A: Infinite","B: Variable depending on the observer's velocity","C: Constant for all observers regardless of their motion","D: Dependent on the medium"],
 "correctAnswer":"C",
 "explanation":"Einstein's first postulate of special relativity: the speed of light in vacuum (c ≈ 3×10⁸ m/s) is constant for all inertial observers, regardless of the motion of the light source or observer."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Magnetic Flux",
 "questionText":"Faraday's law of electromagnetic induction states that the induced EMF in a circuit is proportional to:",
 "options":["A: The strength of the magnetic field","B: The rate of change of magnetic flux","C: The resistance of the circuit","D: The current in the circuit"],
 "correctAnswer":"B",
 "explanation":"Faraday's law: EMF = −dΦ/dt (rate of change of magnetic flux Φ). The negative sign (Lenz's law) indicates that the induced EMF opposes the change that caused it."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Black Body Radiation",
 "questionText":"The Stefan-Boltzmann law states that the total energy radiated by a black body is proportional to:",
 "options":["A: T","B: T²","C: T³","D: T⁴"],
 "correctAnswer":"D",
 "explanation":"Stefan-Boltzmann law: P = σAT⁴, where σ = 5.67×10⁻⁸ W/m²/K⁴. The total radiated power is proportional to the fourth power of absolute temperature T."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Quantum Numbers",
 "questionText":"The principal quantum number (n) determines:",
 "options":["A: The shape of the orbital","B: The energy level / shell of the electron","C: The spin of the electron","D: The magnetic orientation of the orbital"],
 "correctAnswer":"B",
 "explanation":"The principal quantum number n = 1, 2, 3... determines the main energy level (shell) of an electron. n=1 is the K shell (lowest energy); higher n = higher energy and greater distance from nucleus."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"X-Rays",
 "questionText":"X-rays are produced when high-energy electrons are rapidly decelerated upon striking a metal target. This is called:",
 "options":["A: Compton scattering","B: Bremsstrahlung radiation","C: Rayleigh scattering","D: Pair production"],
 "correctAnswer":"B",
 "explanation":"Bremsstrahlung (German: 'braking radiation') is the X-ray radiation emitted when electrons are decelerated by the electric field of the nucleus of the target metal (typically tungsten) in an X-ray tube."},

{"subject":"Science-Physics","grade":10,"difficulty":"Olympiad","topic":"Physics",
 "subTopic":"Superconductivity",
 "questionText":"Superconductivity is the phenomenon where a material:",
 "options":["A: Has infinite resistance at very low temperatures","B: Has zero electrical resistance below a critical temperature","C: Conducts electricity only in magnetic fields","D: Becomes magnetic at high temperatures"],
 "correctAnswer":"B",
 "explanation":"Superconductivity was discovered by Kamerlingh Onnes (1911). Below the critical temperature (Tc), certain materials lose all electrical resistance and expel magnetic fields (Meissner effect)."},

# ── G11 Commerce Advanced top-up (10q, currently at 15 → 25) ─────────────────
{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Forms of Business",
 "questionText":"In a partnership firm, which partner has unlimited liability and is actively involved in management?",
 "options":["A: Sleeping partner","B: Nominal partner","C: Active (working) partner","D: Minor partner"],
 "correctAnswer":"C",
 "explanation":"An active (working) partner contributes capital, participates in day-to-day management, and has unlimited liability. A sleeping partner contributes capital but does not participate in management."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Company Law",
 "questionText":"A company is considered a 'legal person' separate from its shareholders. This concept is called:",
 "options":["A: Limited liability","B: Perpetual succession","C: Separate legal entity","D: Common seal"],
 "correctAnswer":"C",
 "explanation":"Separate legal entity (from Salomon v. Salomon, 1897) means a company can own property, sue and be sued, and enter contracts in its own name, separate from its shareholders."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Accounting",
 "subTopic":"Trial Balance",
 "questionText":"A Trial Balance checks the arithmetical accuracy of ledger accounts. It is prepared after:",
 "options":["A: Journal entries only","B: Balancing all ledger accounts","C: Preparing the Balance Sheet","D: Closing the accounts"],
 "correctAnswer":"B",
 "explanation":"The Trial Balance is extracted from the ledger after all accounts have been balanced. Total debits must equal total credits if ledger entries are arithmetically correct."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Accounting",
 "subTopic":"Depreciation",
 "questionText":"Under the Straight-Line Method of depreciation, the annual charge is:",
 "options":["A: A decreasing amount each year","B: An increasing amount each year","C: A fixed equal amount each year","D: Variable based on asset use"],
 "correctAnswer":"C",
 "explanation":"SLM (Straight-Line Method): Depreciation = (Cost − Scrap value) / Useful life. The same fixed amount is charged each year, reducing the asset to its scrap value at end of useful life."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Economics",
 "subTopic":"Demand Elasticity",
 "questionText":"If a 10% rise in price leads to a 20% fall in quantity demanded, the price elasticity of demand is:",
 "options":["A: 0.5 (inelastic)","B: 2 (elastic)","C: 1 (unit elastic)","D: 20 (perfectly elastic)"],
 "correctAnswer":"B",
 "explanation":"PED = % change in Qd / % change in P = 20%/10% = 2. Since |PED| > 1, demand is elastic (quantity is very responsive to price change)."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Economics",
 "subTopic":"Money and Banking",
 "questionText":"The Reserve Bank of India controls money supply partly through the Cash Reserve Ratio (CRR). If RBI increases CRR, the effect is:",
 "options":["A: Banks have more money to lend — credit expands","B: Banks have less money to lend — credit contracts","C: Inflation increases immediately","D: Foreign exchange reserves decrease"],
 "correctAnswer":"B",
 "explanation":"CRR is the fraction of Net Demand and Time Liabilities (NDTL) banks must hold as cash with RBI. Increasing CRR reduces loanable funds with commercial banks, contracting money supply and credit."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Marketing Mix",
 "questionText":"The '4 Ps' of the marketing mix are:",
 "options":["A: Product, Price, Profit, Promotion","B: Product, Price, Place, Promotion","C: Production, Price, Place, People","D: Product, Pricing, Packaging, Promotion"],
 "correctAnswer":"B",
 "explanation":"The traditional marketing mix (E. Jerome McCarthy, 1960) consists of: Product, Price, Place (distribution), and Promotion. The extended 7P model adds People, Process, and Physical evidence."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Accounting",
 "subTopic":"Bank Reconciliation",
 "questionText":"When a cheque issued by the firm has not yet been presented to the bank, in the Bank Reconciliation Statement the balance as per pass book will be:",
 "options":["A: Less than cash book balance","B: More than cash book balance","C: Equal to cash book balance","D: Zero"],
 "correctAnswer":"B",
 "explanation":"An unpresented (outstanding) cheque has been entered as a payment in the cash book (reducing it) but NOT yet presented to the bank (so pass book balance is still higher). Thus pass book balance > cash book balance."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Economics",
 "subTopic":"National Income",
 "questionText":"GDP at market prices minus net indirect taxes equals:",
 "options":["A: GNP","B: NDP at market prices","C: GDP at factor cost","D: NNP"],
 "correctAnswer":"C",
 "explanation":"GDP at factor cost = GDP at market prices − Net indirect taxes (indirect taxes − subsidies). Factor cost reflects actual cost of production factors (wages, rent, interest, profit)."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Management Functions",
 "questionText":"The management function of 'organising' involves:",
 "options":["A: Setting objectives and policies","B: Establishing the structure, allocating responsibilities and authority","C: Measuring actual performance against standards","D: Motivating and directing employees"],
 "correctAnswer":"B",
 "explanation":"Organising is the process of identifying activities, grouping them, assigning them to departments and individuals, delegating authority, and establishing relationships to achieve objectives."},

# ── G11 Science Foundation top-up (10q, currently at 15 → 25) ────────────────
{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Newton's Laws of Motion",
 "questionText":"Newton's first law of motion is also called the law of:",
 "options":["A: Acceleration","B: Inertia","C: Gravitation","D: Conservation of momentum"],
 "correctAnswer":"B",
 "explanation":"Newton's first law states that an object remains at rest or in uniform motion unless acted upon by a net external force. This property of matter is called inertia."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Atomic Structure",
 "questionText":"The number of protons in an atom determines its:",
 "options":["A: Mass number","B: Atomic number (element identity)","C: Number of neutrons","D: Valence electron configuration only"],
 "correctAnswer":"B",
 "explanation":"The atomic number (Z) equals the number of protons. It uniquely identifies the chemical element. Atoms of the same element always have the same number of protons."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Cell Theory",
 "questionText":"The cell theory states that:",
 "options":["A: Only plants are made of cells","B: Cells can arise from non-living matter","C: All living organisms are made of one or more cells, and the cell is the basic unit of life","D: Cells only divide in laboratory conditions"],
 "correctAnswer":"C",
 "explanation":"Cell theory (Schleiden, Schwann, Virchow): (1) All living things are made of cells. (2) The cell is the basic unit of structure and function. (3) All cells arise from pre-existing cells."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Work, Energy, Power",
 "questionText":"The work done on an object is zero if:",
 "options":["A: The object accelerates","B: The force and displacement are perpendicular to each other","C: The object is moving","D: The force is very large"],
 "correctAnswer":"B",
 "explanation":"Work W = F·d·cosθ. When θ = 90° (force and displacement perpendicular), cos90° = 0, so W = 0. Example: a centripetal force does no work on a circular path."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"States of Matter",
 "questionText":"Which state of matter has a definite volume but no definite shape?",
 "options":["A: Solid","B: Liquid","C: Gas","D: Plasma"],
 "correctAnswer":"B",
 "explanation":"Liquids have a definite volume (incompressible) but take the shape of their container. Solids have definite shape and volume; gases have neither. Plasma is ionised gas."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Nutrition",
 "questionText":"Which nutrient is the primary energy source for the human body?",
 "options":["A: Proteins","B: Vitamins","C: Carbohydrates","D: Minerals"],
 "correctAnswer":"C",
 "explanation":"Carbohydrates (sugars and starches) are the body's primary and preferred energy source. They yield ~4 kcal/g. Fats also store energy (9 kcal/g) but are secondary. Proteins are primarily structural."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Sound Waves",
 "questionText":"The speed of sound is greatest in:",
 "options":["A: Vacuum","B: Air","C: Water","D: Steel"],
 "correctAnswer":"D",
 "explanation":"Sound travels fastest in solids > liquids > gases. In steel (~5000 m/s) > water (~1500 m/s) > air (~343 m/s). Sound cannot travel in vacuum (no medium for wave propagation)."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Chemistry",
 "subTopic":"Periodic Classification",
 "questionText":"Elements in the same group of the periodic table have the same number of:",
 "options":["A: Protons","B: Neutrons","C: Valence electrons","D: Total electrons"],
 "correctAnswer":"C",
 "explanation":"Elements in the same group have the same number of valence electrons (outermost shell electrons), which gives them similar chemical properties. Group 1 elements all have 1 valence electron."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Biology",
 "subTopic":"Plant Kingdom",
 "questionText":"Mosses and liverworts belong to which division of the plant kingdom?",
 "options":["A: Pteridophyta","B: Bryophyta","C: Gymnospermae","D: Angiospermae"],
 "correctAnswer":"B",
 "explanation":"Bryophyta includes mosses, liverworts, and hornworts — small, non-vascular land plants that require water for reproduction. They are considered the 'amphibians of the plant kingdom'."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Gravitation",
 "questionText":"The gravitational force between two objects is directly proportional to the product of their masses and inversely proportional to the square of the distance between them. This is:",
 "options":["A: Newton's second law","B: Kepler's first law","C: Newton's law of universal gravitation","D: Coulomb's law"],
 "correctAnswer":"C",
 "explanation":"Newton's law of universal gravitation: F = Gm₁m₂/r². G = 6.674×10⁻¹¹ N·m²/kg² is the universal gravitational constant. This applies to any two masses in the universe."},

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
