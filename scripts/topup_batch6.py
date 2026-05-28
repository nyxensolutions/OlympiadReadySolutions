import pyodbc, json, uuid, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

CONN_STR = (
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

# ══════════════════════════════════════════════════════════════════════════════
# GK G5 Olympiad (+15, currently 15 → 30)
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"World Geography",
 "questionText":"The deepest point on Earth is the Challenger Deep, located in the:",
 "options":["A: Atlantic Ocean","B: Indian Ocean","C: Mariana Trench (Pacific Ocean)","D: Arctic Ocean"],"correctAnswer":"C",
 "explanation":"The Challenger Deep in the Mariana Trench (Pacific Ocean) is about 10,935 m deep — the deepest known point on Earth. It is off the coast of the Mariana Islands."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Science and Technology",
 "questionText":"Who invented the World Wide Web (WWW)?",
 "options":["A: Bill Gates","B: Tim Berners-Lee","C: Steve Jobs","D: Mark Zuckerberg"],"correctAnswer":"B",
 "explanation":"Tim Berners-Lee invented the World Wide Web in 1989 while working at CERN in Switzerland. He also created the first web browser and web server."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Space Science",
 "questionText":"Jupiter's 'Great Red Spot' is:",
 "options":["A: A large red volcano","B: A giant crater formed by an asteroid","C: A massive storm that has lasted for hundreds of years","D: A large sea of red liquid iron"],"correctAnswer":"C",
 "explanation":"The Great Red Spot is a massive, persistent anticyclonic storm on Jupiter, wider than Earth, that has been observed for at least 350 years."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Sports",
 "questionText":"In which year did Sachin Tendulkar play his 200th and final Test match?",
 "options":["A: 2011","B: 2012","C: 2013","D: 2014"],"correctAnswer":"C",
 "explanation":"Sachin Tendulkar played his 200th and final Test match against the West Indies at Wankhede Stadium, Mumbai, in November 2013. He finished with 15,921 Test runs."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Indian Geography",
 "questionText":"The Sundarbans mangrove forest is shared between India and:",
 "options":["A: Nepal","B: Myanmar","C: Bangladesh","D: Sri Lanka"],"correctAnswer":"C",
 "explanation":"The Sundarbans, the world's largest mangrove delta, spans the Bengal delta across India (West Bengal) and Bangladesh. It is home to the Royal Bengal Tiger."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Chemistry",
 "questionText":"The chemical formula of common salt is:",
 "options":["A: KCl","B: NaCl","C: CaCl₂","D: NaOH"],"correctAnswer":"B",
 "explanation":"Common salt is sodium chloride, with the chemical formula NaCl (one sodium atom and one chlorine atom)."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Indian Culture",
 "questionText":"The Kumbh Mela, the world's largest human gathering, is held at how many locations in India?",
 "options":["A: 2","B: 3","C: 4","D: 6"],"correctAnswer":"C",
 "explanation":"The Kumbh Mela rotates among 4 sacred river cities: Prayagraj (Ganga-Yamuna-Saraswati), Haridwar (Ganga), Nashik/Trimbak (Godavari), and Ujjain (Shipra). The Maha Kumbh at Prayagraj is the largest."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Literature",
 "questionText":"'Vande Mataram', India's national song, was written by:",
 "options":["A: Rabindranath Tagore","B: Subramanya Bharati","C: Bankim Chandra Chattopadhyay","D: Maithilisharan Gupt"],"correctAnswer":"C",
 "explanation":"Bankim Chandra Chattopadhyay wrote 'Vande Mataram' in 1876, published in his novel Anandamath (1882). The first two stanzas are India's National Song."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"World Geography",
 "questionText":"Which country is known as the 'Land of the Midnight Sun' because the Sun does not set there during summer?",
 "options":["A: Iceland","B: Denmark","C: Norway","D: Switzerland"],"correctAnswer":"C",
 "explanation":"Norway (and other Arctic/Nordic countries like Sweden, Finland) experience the 'Midnight Sun' in summer because they lie above the Arctic Circle. The Sun stays above the horizon for 24 hours."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Nobel Prize",
 "questionText":"Marie Curie received the Nobel Prize in Physics (1903) for her research on:",
 "options":["A: X-rays","B: Radioactivity","C: The photoelectric effect","D: Nuclear fission"],"correctAnswer":"B",
 "explanation":"Marie Curie (shared with Pierre Curie and Henri Becquerel) received the 1903 Physics Nobel for research on radioactivity. She also won the 1911 Chemistry Nobel — the only person to win Nobel Prizes in two different sciences."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Board Games",
 "questionText":"The game of Chess originated in which ancient civilisation?",
 "options":["A: Greek","B: Chinese","C: Egyptian","D: Indian"],"correctAnswer":"D",
 "explanation":"Chess originated in India as 'Chaturanga' (meaning four divisions of the military) around the 6th century CE. It spread to Persia (as Chatrang/Shatranj) and then to Europe."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Indian Geography",
 "questionText":"After the reorganisation of Jammu & Kashmir in 2019, which is now the largest Indian STATE by area?",
 "options":["A: Maharashtra","B: Madhya Pradesh","C: Rajasthan","D: Uttar Pradesh"],"correctAnswer":"C",
 "explanation":"Rajasthan (342,239 sq km) became the largest state after J&K became a Union Territory in October 2019. Before that, J&K was counted separately."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Astronomy",
 "questionText":"The Tropic of Capricorn is an imaginary line located at:",
 "options":["A: 0° latitude","B: 23.5°N latitude","C: 66.5°S latitude","D: 23.5°S latitude"],"correctAnswer":"D",
 "explanation":"The Tropic of Capricorn is at 23.5°S — the southernmost latitude where the Sun can appear directly overhead (at noon on the December solstice)."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Indian Heritage",
 "questionText":"The Khajuraho temples, famous for their intricate sculptures, are located in which state?",
 "options":["A: Rajasthan","B: Uttar Pradesh","C: Madhya Pradesh","D: Odisha"],"correctAnswer":"C",
 "explanation":"The Khajuraho temples (built by the Chandela dynasty, 950–1050 CE) are in Chhatarpur district, Madhya Pradesh. They are a UNESCO World Heritage Site."},

{"subject":"General Knowledge","grade":5,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"World Records",
 "questionText":"Which is the longest mountain range in the world?",
 "options":["A: The Himalayas","B: The Rockies","C: The Alps","D: The Andes"],"correctAnswer":"D",
 "explanation":"The Andes in South America (7,000 km long) is the world's longest mountain range. The Himalayas are the world's highest mountain range (containing the world's highest peaks)."},

# ══════════════════════════════════════════════════════════════════════════════
# SS G5 Olympiad (+15, currently 16 → 31)
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Indian States",
 "questionText":"Which is the SMALLEST state in India by area?",
 "options":["A: Sikkim","B: Tripura","C: Goa","D: Nagaland"],"correctAnswer":"C",
 "explanation":"Goa (3,702 sq km) is the smallest state in India by area. It was liberated from Portuguese rule in 1961. Sikkim is the second smallest."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Indian Leaders",
 "questionText":"Who was the first Prime Minister of independent India?",
 "options":["A: Mahatma Gandhi","B: Sardar Vallabhbhai Patel","C: Jawaharlal Nehru","D: B.R. Ambedkar"],"correctAnswer":"C",
 "explanation":"Jawaharlal Nehru became India's first Prime Minister on 15 August 1947 and served until his death on 27 May 1964 — the longest-serving Indian PM."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Rivers",
 "questionText":"The Brahmaputra river originates from:",
 "options":["A: The Karakoram Range","B: The Aravalli Hills","C: The Chemayungdung glacier in Tibet (near Mansarovar)","D: The Zoji La pass"],"correctAnswer":"C",
 "explanation":"The Brahmaputra (called Tsangpo in Tibet) originates near Lake Mansarovar in the Chemayungdung glacier, Tibet. It enters India through Arunachal Pradesh after cutting through the Himalayas."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Agriculture",
 "questionText":"Which crop is known as the 'Golden Fibre' of India?",
 "options":["A: Cotton","B: Jute","C: Silk","D: Wheat"],"correctAnswer":"B",
 "explanation":"Jute is called the 'Golden Fibre' because of its golden colour and its high economic value. India (mainly West Bengal) is the world's largest producer of raw jute."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Mountains",
 "questionText":"The Western Ghats are also known by which name?",
 "options":["A: Vindhya Range","B: Sahyadri","C: Aravalli","D: Eastern Ghats"],"correctAnswer":"B",
 "explanation":"The Western Ghats are also called the Sahyadri range. They run parallel to the western coast of India (~1,600 km), are a UNESCO World Biodiversity Hotspot, and influence the monsoon significantly."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Civics",
 "questionText":"India follows which type of democracy?",
 "options":["A: Direct Democracy","B: Military Democracy","C: Monarchy","D: Parliamentary Representative Democracy"],"correctAnswer":"D",
 "explanation":"India is a Parliamentary Representative Democracy — citizens elect representatives to Parliament (Lok Sabha) who then form the government. Direct democracy means citizens vote on every law (not practical for 1.4 billion people)."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Environment Movements",
 "questionText":"The Chipko Movement (1973) was a non-violent protest against:",
 "options":["A: Water pollution","B: Deforestation of Himalayan forests","C: Building of dams on the Ganga","D: Air pollution in cities"],"correctAnswer":"B",
 "explanation":"In 1973, villagers in Uttarakhand (led by Sunderlal Bahuguna) hugged trees to prevent felling by commercial loggers — 'Chipko' means 'to hug'. It became a landmark environmental conservation movement."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Indian Leaders",
 "questionText":"Who was the first woman Prime Minister of India?",
 "options":["A: Sarojini Naidu","B: Pratibha Patil","C: Sonia Gandhi","D: Indira Gandhi"],"correctAnswer":"D",
 "explanation":"Indira Gandhi was India's first (and only) woman Prime Minister, serving 1966–1977 and 1980–1984. She was the daughter of Jawaharlal Nehru. Pratibha Patil was India's first woman President (2007–2012)."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Parliament",
 "questionText":"The Lok Sabha is also known as the:",
 "options":["A: Council of States","B: Upper House","C: House of the People","D: Rajya Sabha"],"correctAnswer":"C",
 "explanation":"Lok Sabha means 'House of the People' — it is the lower house of India's Parliament, directly elected by citizens. Rajya Sabha is the 'Council of States' (upper house)."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Soil",
 "questionText":"Which type of soil is best suited for growing cotton?",
 "options":["A: Sandy soil","B: Red soil","C: Laterite soil","D: Black (Regur) soil"],"correctAnswer":"D",
 "explanation":"Black soil (also called Regur or Deccan trap soil) is ideal for cotton because it retains moisture for long periods, is rich in lime and potash, and has high clay content. It covers large parts of Maharashtra, MP, and Gujarat."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Rivers",
 "questionText":"The name 'Punjab' (meaning 'Land of Five Rivers') refers to the five rivers:",
 "options":["A: Ganga, Yamuna, Sutlej, Beas, Ravi","B: Sutlej, Ravi, Beas, Chenab, Jhelum","C: Indus, Jhelum, Chenab, Ravi, Sutlej","D: Beas, Sutlej, Ravi, Yamuna, Ganga"],"correctAnswer":"B",
 "explanation":"Punjab means 'Panj' (five) + 'Ab' (water/rivers). The five rivers are Sutlej, Ravi, Beas, Chenab, and Jhelum — all tributaries of the Indus River system."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Space",
 "questionText":"India's first satellite, launched in 1975, was named:",
 "options":["A: Chandrayaan","B: Mangalyaan","C: Aryabhata","D: Bhaskara"],"correctAnswer":"C",
 "explanation":"Aryabhata was India's first satellite, launched on 19 April 1975 with the help of the Soviet Union. It was named after the ancient Indian mathematician and astronomer."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Constitution",
 "questionText":"The Tropic of Cancer passes through how many Indian states?",
 "options":["A: 5","B: 6","C: 8","D: 10"],"correctAnswer":"C",
 "explanation":"The Tropic of Cancer (23.5°N) passes through 8 Indian states: Gujarat, Rajasthan, Madhya Pradesh, Chhattisgarh, Jharkhand, West Bengal, Tripura, and Mizoram."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Fundamental Duties",
 "questionText":"Which of the following is a Fundamental DUTY of Indian citizens?",
 "options":["A: Right to vote","B: Right to education","C: To protect and improve the natural environment","D: Right to get a government job"],"correctAnswer":"C",
 "explanation":"Article 51A(g) of the Indian Constitution lists protecting and improving the natural environment (forests, lakes, rivers, wildlife) as a Fundamental Duty. Rights to vote, education, and employment are Rights, not Duties."},

{"subject":"Social Studies","grade":5,"difficulty":"Olympiad","topic":"Social Studies","subTopic":"Indian Culture",
 "questionText":"Bihu (Assam), Pongal (Tamil Nadu), Lohri (Punjab), and Makar Sankranti (many states) are all harvest festivals celebrated around the same time. What month do they typically fall in?",
 "options":["A: March–April","B: October–November","C: July–August","D: January"],"correctAnswer":"D",
 "explanation":"All these harvest festivals celebrate the winter harvest and the northward movement of the Sun (Makar Sankranti). They all fall in mid-January (Pongal: Jan 14–17, Lohri: Jan 13, Makar Sankranti: Jan 14, Magh Bihu: Jan 14)."},

# ══════════════════════════════════════════════════════════════════════════════
# Science-Biology G10 Foundation (15 questions — tier was missing entirely)
# CBSE Class 10 Biology: Life Processes, Control & Coordination,
# Reproduction, Heredity, Environment
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Photosynthesis",
 "questionText":"Photosynthesis takes place in which organelle of a plant cell?",
 "options":["A: Mitochondria","B: Ribosome","C: Chloroplast","D: Nucleus"],"correctAnswer":"C",
 "explanation":"Chloroplasts contain chlorophyll and are the sites of photosynthesis. They capture light energy and convert CO₂ + H₂O into glucose and O₂."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Digestion",
 "questionText":"Which part of the digestive system is mainly responsible for the absorption of digested nutrients?",
 "options":["A: Stomach","B: Large intestine","C: Oesophagus","D: Small intestine"],"correctAnswer":"D",
 "explanation":"The small intestine (with villi and microvilli) has a massive surface area for absorbing digested food — glucose, amino acids, fatty acids — into the bloodstream."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Circulation",
 "questionText":"Which type of blood vessel carries blood AWAY from the heart?",
 "options":["A: Vein","B: Artery","C: Capillary","D: Venule"],"correctAnswer":"B",
 "explanation":"Arteries carry oxygenated blood away from the heart to the body (except the pulmonary artery, which carries deoxygenated blood to lungs). Veins carry blood back TO the heart."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Excretion",
 "questionText":"The functional unit of the kidney is called:",
 "options":["A: Neuron","B: Alveolus","C: Nephron","D: Villus"],"correctAnswer":"C",
 "explanation":"Each human kidney contains about 1 million nephrons. Each nephron filters blood, reabsorbs useful substances, and produces urine."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Hormones",
 "questionText":"Which hormone is responsible for the 'fight or flight' response in stressful situations?",
 "options":["A: Insulin","B: Thyroxin","C: Adrenaline","D: Oestrogen"],"correctAnswer":"C",
 "explanation":"Adrenaline (epinephrine) is released by the adrenal glands in response to stress. It increases heart rate, dilates airways, and redirects blood to muscles — preparing the body to fight or flee."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Nervous System",
 "questionText":"A reflex action (like withdrawing your hand from a hot object) is primarily controlled by the:",
 "options":["A: Cerebellum","B: Spinal cord","C: Cerebrum","D: Hypothalamus"],"correctAnswer":"B",
 "explanation":"Reflex arcs pass through the spinal cord (bypassing the brain for speed). This is why you pull your hand away before you consciously feel the pain — the reflex is faster than brain-mediated response."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Reproduction",
 "questionText":"Which of the following is an example of ASEXUAL reproduction?",
 "options":["A: Seed germination in plants","B: Budding in Hydra","C: Pollination in flowers","D: Fertilisation in frogs"],"correctAnswer":"B",
 "explanation":"Budding in Hydra is asexual — a small bud grows on the parent, develops into a new organism, and detaches. Seed germination, pollination, and fertilisation involve sexual reproduction."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Heredity",
 "questionText":"Where is genetic information (DNA) primarily stored in a cell?",
 "options":["A: Cell membrane","B: Cytoplasm","C: Nucleus","D: Ribosome"],"correctAnswer":"C",
 "explanation":"DNA is primarily stored in the nucleus of a cell, wound around histone proteins to form chromosomes. (Small amounts of DNA also exist in mitochondria and chloroplasts.)"},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Evolution",
 "questionText":"The theory of evolution by natural selection was proposed by:",
 "options":["A: Gregor Mendel","B: Louis Pasteur","C: Charles Darwin","D: Jean-Baptiste Lamarck"],"correctAnswer":"C",
 "explanation":"Charles Darwin proposed the theory of evolution by natural selection in 'On the Origin of Species' (1859). Mendel worked on genetics; Pasteur on germ theory; Lamarck proposed an earlier (incorrect) theory of evolution."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Human Chromosomes",
 "questionText":"The total number of chromosomes in a normal human body (somatic) cell is:",
 "options":["A: 23","B: 46","C: 48","D: 24"],"correctAnswer":"B",
 "explanation":"Human body cells have 46 chromosomes (23 pairs — 22 autosome pairs + 1 sex chromosome pair XX or XY). Sex cells (gametes) have 23 chromosomes (haploid)."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Ecosystem",
 "questionText":"In a food chain, organisms that make their own food using sunlight are called:",
 "options":["A: Consumers","B: Decomposers","C: Producers","D: Carnivores"],"correctAnswer":"C",
 "explanation":"Producers (plants, algae, phytoplankton) make their own food via photosynthesis and form the base of every food chain. Consumers eat other organisms; decomposers break down dead matter."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Respiration",
 "questionText":"In aerobic respiration, glucose is broken down in the presence of oxygen to produce:",
 "options":["A: Carbon dioxide, water, and energy (ATP)","B: Lactic acid only","C: Oxygen and glucose","D: Carbon monoxide and water"],"correctAnswer":"A",
 "explanation":"Aerobic respiration: C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + Energy (ATP). It produces CO₂, water, and releases ~38 ATP molecules per glucose molecule."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Plant Structure",
 "questionText":"The waxy layer on the surface of leaves that reduces water loss is called the:",
 "options":["A: Epidermis","B: Cuticle","C: Stomata","D: Mesophyll"],"correctAnswer":"B",
 "explanation":"The cuticle is a waxy, waterproof coating secreted by the epidermal cells of leaves. It prevents excessive water loss through transpiration and protects against pathogens."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Ozone Layer",
 "questionText":"The ozone layer protects life on Earth by absorbing:",
 "options":["A: Infrared radiation","B: Visible light","C: Ultraviolet radiation","D: X-rays"],"correctAnswer":"C",
 "explanation":"The ozone layer (in the stratosphere, 15–35 km altitude) absorbs most of the Sun's harmful UV-B and UV-C radiation, preventing skin cancer, cataracts, and ecosystem damage."},

{"subject":"Science-Biology","grade":10,"difficulty":"Foundation","topic":"Science-Biology","subTopic":"Asexual Reproduction — Plants",
 "questionText":"Which of these is an example of vegetative propagation (a form of asexual reproduction in plants)?",
 "options":["A: Pollination by wind","B: Growing a new plant from a potato tuber","C: Germination of seeds","D: Dispersal of seeds by animals"],"correctAnswer":"B",
 "explanation":"Growing a new plant from a potato tuber (modified stem) is vegetative propagation — a new plant grows from a part of the parent plant. Pollination, germination, and seed dispersal are all part of sexual reproduction."},

# ══════════════════════════════════════════════════════════════════════════════
# Science-Chemistry G10 Foundation (15 questions — tier was missing entirely)
# CBSE Class 10 Chemistry: Chemical Reactions, Acids/Bases/Salts,
# Metals & Non-metals, Carbon Compounds, Periodic Classification
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Chemical Reactions",
 "questionText":"When baking soda (NaHCO₃) is added to vinegar (acetic acid), which gas is released?",
 "options":["A: Oxygen","B: Hydrogen","C: Carbon dioxide","D: Nitrogen"],"correctAnswer":"C",
 "explanation":"NaHCO₃ + CH₃COOH → CH₃COONa + H₂O + CO₂↑. Carbon dioxide is released, causing effervescence (fizzing). This is an acid–carbonate reaction."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"pH Scale",
 "questionText":"A solution with a pH of 4 is:",
 "options":["A: Neutral","B: Weakly basic","C: Strongly basic","D: Acidic"],"correctAnswer":"D",
 "explanation":"The pH scale runs from 0 to 14. pH < 7 = acidic; pH = 7 = neutral; pH > 7 = basic. pH 4 is acidic. (Example: tomato juice has pH ~4.)"},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Displacement Reactions",
 "questionText":"When an iron nail is placed in copper sulphate (CuSO₄) solution, which of the following is observed?",
 "options":["A: No change","B: The solution turns colourless and copper is deposited on the nail","C: The iron nail dissolves completely","D: The solution turns red and iron dissolves"],"correctAnswer":"B",
 "explanation":"Fe + CuSO₄ → FeSO₄ + Cu. Iron (more reactive) displaces copper from solution. The blue CuSO₄ solution turns light green (FeSO₄) and copper deposits on the nail. This is a displacement reaction."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Metals",
 "questionText":"The process of coating iron with a layer of zinc to prevent rusting is called:",
 "options":["A: Electroplating","B: Galvanisation","C: Alloying","D: Annealing"],"correctAnswer":"B",
 "explanation":"Galvanisation coats iron/steel with zinc to prevent rusting. Zinc forms a protective oxide layer and also acts as a sacrificial anode (it corrodes instead of iron). Used in roofing sheets and buckets."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Carbon Compounds",
 "questionText":"Which acid is present in vinegar?",
 "options":["A: Hydrochloric acid","B: Citric acid","C: Acetic acid (ethanoic acid)","D: Tartaric acid"],"correctAnswer":"C",
 "explanation":"Vinegar is a 5–8% solution of acetic acid (ethanoic acid, CH₃COOH) in water. It is produced by fermentation of ethanol."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Rusting",
 "questionText":"Rusting of iron requires which two substances?",
 "options":["A: Oxygen and nitrogen","B: Water (moisture) and oxygen","C: Nitrogen and carbon dioxide","D: Light and water"],"correctAnswer":"B",
 "explanation":"Rusting (Fe₂O₃·xH₂O) requires both water/moisture and oxygen. In a dry environment, iron does not rust. Rust is a hydrated iron(III) oxide, formed by electrochemical oxidation."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Periodic Table",
 "questionText":"The Periodic Table was developed by:",
 "options":["A: John Dalton","B: Antoine Lavoisier","C: Dmitri Mendeleev","D: Henry Moseley"],"correctAnswer":"C",
 "explanation":"Dmitri Mendeleev (1869) arranged elements by increasing atomic mass and noticed periodic patterns. He even predicted properties of undiscovered elements. Henry Moseley later revised it by atomic number."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Alloys",
 "questionText":"Steel is an alloy of:",
 "options":["A: Iron and copper","B: Iron and carbon","C: Iron and zinc","D: Iron and tin"],"correctAnswer":"B",
 "explanation":"Steel is an alloy of iron and carbon (0.2–2.1% carbon). Carbon improves hardness and strength. Stainless steel also contains chromium and nickel for corrosion resistance."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Acid-Base Indicators",
 "questionText":"Which gas turns lime water (Ca(OH)₂ solution) milky when bubbled through it?",
 "options":["A: Oxygen","B: Hydrogen","C: Carbon dioxide","D: Nitrogen"],"correctAnswer":"C",
 "explanation":"CO₂ + Ca(OH)₂ → CaCO₃↓ + H₂O. Calcium carbonate (CaCO₃) is an insoluble white precipitate that makes the lime water appear milky. This is a standard test for CO₂."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Soaps and Detergents",
 "questionText":"Soap is made by the reaction of oils/fats with a strong alkali (NaOH or KOH). This process is called:",
 "options":["A: Esterification","B: Saponification","C: Fermentation","D: Hydrogenation"],"correctAnswer":"B",
 "explanation":"Saponification is the alkaline hydrolysis of fats/oils with NaOH (for hard soap) or KOH (for soft soap), producing glycerol and soap (sodium/potassium fatty acid salt)."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Carbon — Catenation",
 "questionText":"Carbon can form millions of organic compounds primarily because of:",
 "options":["A: Its small atomic size","B: Its ability to form bonds with other carbon atoms (catenation) and tetravalency","C: Its high melting point","D: Its abundance in nature"],"correctAnswer":"B",
 "explanation":"Carbon's two unique properties — catenation (C–C bonding to form chains, branches, rings) and tetravalency (4 bonds with other elements) — allow it to form an enormous variety of compounds."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Reactivity Series",
 "questionText":"In the reactivity series of metals, which metal is the MOST reactive?",
 "options":["A: Gold","B: Iron","C: Potassium","D: Copper"],"correctAnswer":"C",
 "explanation":"Potassium (K) is at the top of the reactivity series — it reacts explosively even with cold water. The order (most to least reactive): K > Na > Ca > Mg > Al > Zn > Fe > Pb > H > Cu > Ag > Au."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Types of Chemical Reactions",
 "questionText":"2Mg + O₂ → 2MgO is an example of which type of reaction?",
 "options":["A: Decomposition reaction","B: Displacement reaction","C: Combination (synthesis) reaction","D: Double displacement reaction"],"correctAnswer":"C",
 "explanation":"Two or more reactants combine to form a single product → Combination (synthesis) reaction. Mg burns in oxygen to form magnesium oxide (a white powder)."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Non-metals",
 "questionText":"Which of the following is a property of non-metals (in general)?",
 "options":["A: Good conductors of heat and electricity","B: Malleable and ductile","C: Lustrous (shiny) surface","D: Poor conductors of heat and electricity"],"correctAnswer":"D",
 "explanation":"Non-metals are generally poor conductors (insulators) of heat and electricity (except graphite). They are also brittle (not malleable/ductile) and lack lustre. Metals have opposite properties."},

{"subject":"Science-Chemistry","grade":10,"difficulty":"Foundation","topic":"Science-Chemistry","subTopic":"Acids and Bases",
 "questionText":"Which of the following is a strong acid?",
 "options":["A: Acetic acid","B: Carbonic acid","C: Hydrochloric acid","D: Citric acid"],"correctAnswer":"C",
 "explanation":"Hydrochloric acid (HCl) is a strong acid — it completely dissociates in water. Acetic, carbonic, and citric acids are weak acids that only partially dissociate."},

# ══════════════════════════════════════════════════════════════════════════════
# Social Studies G9 Advanced (+15, currently 22 → 37)
# NCERT History: French Revolution, Russian, Nazism, Pastoralists, Forest Society
# Geography: India Physical, Drainage, Climate, Vegetation, Population
# Civics: Democracy, Elections, Working of Institutions
# Economics: Poverty, Food Security, People as Resource
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"French Revolution",
 "questionText":"The French Revolution began in which year?",
 "options":["A: 1776","B: 1789","C: 1799","D: 1815"],"correctAnswer":"B",
 "explanation":"The French Revolution began in 1789 with the Storming of the Bastille on 14 July 1789, a date now celebrated as Bastille Day in France. It ended the absolute monarchy and transformed European politics."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"French Revolution",
 "questionText":"In pre-revolutionary France, the 'Third Estate' comprised:",
 "options":["A: The clergy (Church)","B: The nobility (aristocrats)","C: The king and his court","D: Common people — peasants, workers, and the middle class (bourgeoisie)"],"correctAnswer":"D",
 "explanation":"French society was divided into three estates. First Estate = clergy, Second Estate = nobility. The Third Estate = ~97% of the population (commoners), who bore the tax burden despite having the least power."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Indian Rivers",
 "questionText":"The Himalayan rivers are called 'perennial rivers' because:",
 "options":["A: They flow only during the monsoon season","B: They are fed by glaciers and monsoon rainfall, so they flow throughout the year","C: They are entirely within Indian territory","D: They flow very slowly due to flat terrain"],"correctAnswer":"B",
 "explanation":"Himalayan rivers like the Ganga, Brahmaputra, and Indus are perennial (never dry) because they are fed by both monsoon rainfall and melting glaciers, ensuring year-round flow."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Indian Climate",
 "questionText":"'Western Disturbances' bring winter rainfall mainly to which part of India?",
 "options":["A: Southern India (Tamil Nadu)","B: Eastern India (West Bengal)","C: Northwestern India (Punjab, Haryana, J&K)","D: Northeastern India (Assam)"],"correctAnswer":"C",
 "explanation":"Western Disturbances are extratropical cyclones originating in the Mediterranean Sea. They travel eastward and bring winter rainfall/snowfall to J&K, Himachal Pradesh, Punjab, and Haryana — vital for the Rabi crop."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Indian Water Bodies",
 "questionText":"Which is the largest freshwater lake in India?",
 "options":["A: Dal Lake","B: Chilika Lake","C: Wular Lake","D: Sambhar Lake"],"correctAnswer":"C",
 "explanation":"Wular Lake in Jammu & Kashmir is the largest freshwater lake in India (130–260 sq km, varying seasonally). Chilika Lake (Odisha) is the largest coastal lagoon/brackish water lake."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Indian Climate",
 "questionText":"The retreating northeast monsoon brings heavy rainfall to which coastal region?",
 "options":["A: Konkan Coast (Maharashtra)","B: Malabar Coast (Kerala)","C: Coromandel Coast (Tamil Nadu, Andhra Pradesh)","D: Gujarat Coast"],"correctAnswer":"C",
 "explanation":"When the southwest monsoon retreats (October–December), the northeast monsoon picks up moisture from the Bay of Bengal and deposits it on the Coromandel Coast. Chennai receives most of its rain during this period."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Democracy",
 "questionText":"'Universal Adult Franchise' means:",
 "options":["A: Only educated adults can vote","B: Only taxpayers can vote","C: Every citizen above 18 years has the right to vote regardless of class, gender, or religion","D: Only adults who own property can vote"],"correctAnswer":"C",
 "explanation":"Universal Adult Franchise gives every adult citizen (18+ in India since 1989; earlier 21+) the equal right to vote regardless of education, income, caste, religion, or gender."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Indian Elections",
 "questionText":"Lok Sabha elections in India are held every:",
 "options":["A: 3 years","B: 4 years","C: 5 years","D: 6 years"],"correctAnswer":"C",
 "explanation":"The Lok Sabha (House of the People) has a maximum term of 5 years. Elections can be held earlier if the house is dissolved. The Election Commission of India oversees these elections."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Indian Constitution",
 "questionText":"The Constituent Assembly adopted the Indian Constitution on:",
 "options":["A: 15 August 1947","B: 26 November 1949","C: 26 January 1950","D: 26 January 1949"],"correctAnswer":"B",
 "explanation":"The Constitution was adopted on 26 November 1949 (now celebrated as Constitution Day). It came into force on 26 January 1950 (Republic Day). Dr. B.R. Ambedkar chaired the Drafting Committee."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Poverty",
 "questionText":"The Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA) guarantees how many days of employment per year to rural households?",
 "options":["A: 50 days","B: 75 days","C: 100 days","D: 150 days"],"correctAnswer":"C",
 "explanation":"MGNREGA (enacted 2005) guarantees 100 days of unskilled wage employment per financial year to every rural household whose adult members volunteer to do unskilled manual work."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Gandhi and Non-violence",
 "questionText":"'Satyagraha' as a political tool introduced by Mahatma Gandhi primarily means:",
 "options":["A: Violent revolution against oppression","B: A hunger strike until demands are met","C: Passive non-violent resistance based on the force of truth","D: Armed civil disobedience"],"correctAnswer":"C",
 "explanation":"Satyagraha (Sat = truth, Agraha = insistence/force) means 'truth-force' or 'soul-force'. Gandhi's method involved non-violent resistance, civil disobedience, and non-cooperation to fight injustice."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Nazism",
 "questionText":"The Holocaust during World War II refers to the:",
 "options":["A: German bombing of London","B: Systematic genocide of 6 million Jews (and millions of others) by the Nazi regime","C: Allied invasion of Normandy","D: Nuclear bombing of Japan"],"correctAnswer":"B",
 "explanation":"The Holocaust was the systematic, state-sponsored persecution and murder of 6 million Jews (and ~5 million others — Roma, disabled, Poles, Soviet citizens, etc.) by Nazi Germany under Hitler (1933–1945)."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Food Security",
 "questionText":"The 'Green Revolution' in India was associated primarily with the high-yielding varieties (HYV) of which crops?",
 "options":["A: Rice and sugarcane","B: Wheat and rice","C: Jute and cotton","D: Maize and barley"],"correctAnswer":"B",
 "explanation":"The Green Revolution (1960s–70s), championed by M.S. Swaminathan in India, introduced HYV seeds for wheat (Punjab, Haryana) and rice, along with irrigation, fertilisers, and pesticides, dramatically boosting food production."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"People as Resource",
 "questionText":"India's Right to Education (RTE) Act 2009 makes free and compulsory education a right for children aged:",
 "options":["A: 5–14 years","B: 6–14 years","C: 6–18 years","D: 3–14 years"],"correctAnswer":"B",
 "explanation":"The RTE Act 2009 (under Article 21A added by the 86th Constitutional Amendment, 2002) guarantees free and compulsory education to all children aged 6–14 years as a Fundamental Right."},

{"subject":"Social Studies","grade":9,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Indian Drainage",
 "questionText":"The Luni river drains into the:",
 "options":["A: Arabian Sea","B: Bay of Bengal","C: Rann of Kutch","D: River Indus"],"correctAnswer":"C",
 "explanation":"The Luni is a western Rajasthan river that originates in the Aravallis and drains into the Rann of Kutch (Great Rann) in Gujarat. It is saline in its lower course."},

]

conn = pyodbc.connect(CONN_STR)
ok = dup = err = 0
for i, q in enumerate(questions, 1):
    label = f"[{q['subject']:<22} G{q['grade']} {q['difficulty'][:3].upper()}]"
    try:
        r = insert(conn, q)
        if r == "OK":
            ok += 1
        else:
            dup += 1
        print(f"  {r:<3} Q{i:03d} {label} {q['subTopic']}")
    except Exception as e:
        err += 1
        print(f"  ERR Q{i:03d} {label} {q['subTopic']} — {e}")
conn.close()
print(f"\n  Done: {ok} posted, {dup} duplicates, {err} errors  (total={len(questions)})")
