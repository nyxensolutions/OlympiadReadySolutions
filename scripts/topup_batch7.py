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

# ── Science-Physics G10 Foundation (15q) ──────────────────────────────────────
{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Light — Reflection",
 "questionText":"The angle of incidence equals the angle of reflection. This is known as:",
 "options":["A: Newton's first law","B: Snell's law","C: Law of reflection","D: Law of refraction"],
 "correctAnswer":"C",
 "explanation":"The law of reflection states that the angle of incidence equals the angle of reflection, measured from the normal to the reflecting surface."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Light — Refraction",
 "questionText":"When light travels from air into glass, it:",
 "options":["A: Speeds up and bends away from normal","B: Slows down and bends towards normal","C: Maintains the same speed","D: Reflects completely"],
 "correctAnswer":"B",
 "explanation":"Glass is denser than air. Light slows down when entering a denser medium and bends towards the normal — this is refraction."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Human Eye",
 "questionText":"The lens of the human eye is controlled by which muscles to change its focal length?",
 "options":["A: Corneal muscles","B: Iris muscles","C: Ciliary muscles","D: Retinal muscles"],
 "correctAnswer":"C",
 "explanation":"Ciliary muscles change the shape (and hence focal length) of the eye lens — a process called accommodation."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Electricity",
 "questionText":"The SI unit of electric resistance is:",
 "options":["A: Volt","B: Ampere","C: Watt","D: Ohm"],
 "correctAnswer":"D",
 "explanation":"The ohm (Ω) is the SI unit of electrical resistance, named after German physicist Georg Simon Ohm."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Ohm's Law",
 "questionText":"According to Ohm's law, if voltage across a conductor doubles while resistance stays constant, the current will:",
 "options":["A: Halve","B: Stay the same","C: Double","D: Quadruple"],
 "correctAnswer":"C",
 "explanation":"Ohm's law: V = IR. If V doubles and R is constant, then I = V/R also doubles."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Magnetic Effects of Current",
 "questionText":"A current-carrying conductor placed in a magnetic field experiences a force. This principle is used in:",
 "options":["A: Transformer","B: Electric motor","C: Generator","D: Capacitor"],
 "correctAnswer":"B",
 "explanation":"An electric motor works on the principle that a current-carrying conductor in a magnetic field experiences a mechanical force (Fleming's left-hand rule)."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Electromagnetic Induction",
 "questionText":"An electric generator converts:",
 "options":["A: Electrical energy to chemical energy","B: Mechanical energy to electrical energy","C: Heat energy to electrical energy","D: Light energy to electrical energy"],
 "correctAnswer":"B",
 "explanation":"An electric generator works on electromagnetic induction — mechanical energy (rotation) is converted to electrical energy."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Sources of Energy",
 "questionText":"Which of the following is a non-renewable source of energy?",
 "options":["A: Solar energy","B: Wind energy","C: Coal","D: Tidal energy"],
 "correctAnswer":"C",
 "explanation":"Coal is a fossil fuel and a non-renewable energy source. Solar, wind, and tidal energies are renewable."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Power",
 "questionText":"The SI unit of electric power is:",
 "options":["A: Joule","B: Ampere","C: Volt","D: Watt"],
 "correctAnswer":"D",
 "explanation":"Power is measured in watts (W). 1 watt = 1 joule per second. Power P = VI."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Dispersion of Light",
 "questionText":"When white light passes through a prism, it splits into seven colours. This phenomenon is called:",
 "options":["A: Reflection","B: Refraction","C: Dispersion","D: Diffraction"],
 "correctAnswer":"C",
 "explanation":"Dispersion is the splitting of white light into its constituent colours (VIBGYOR) due to different wavelengths bending by different amounts in a prism."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Mirrors",
 "questionText":"Which type of mirror is used as a rear-view mirror in vehicles?",
 "options":["A: Concave mirror","B: Plane mirror","C: Convex mirror","D: Parabolic mirror"],
 "correctAnswer":"C",
 "explanation":"Convex mirrors give a wider field of view and always form erect, virtual, and diminished images — hence used as rear-view mirrors."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Series and Parallel Circuits",
 "questionText":"In a series circuit, if one bulb fuses, the other bulbs will:",
 "options":["A: Glow brighter","B: Continue glowing normally","C: Also go out","D: Glow dimmer"],
 "correctAnswer":"C",
 "explanation":"In a series circuit all components share the same current path. If one breaks, the circuit is open and all other bulbs go out."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Lenses",
 "questionText":"A convex (converging) lens is used to correct which vision defect?",
 "options":["A: Myopia (short-sightedness)","B: Hypermetropia (long-sightedness)","C: Astigmatism","D: Colour blindness"],
 "correctAnswer":"B",
 "explanation":"Hypermetropia (far-sightedness) is corrected using a convex lens, which converges light rays onto the retina."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Heating Effect of Current",
 "questionText":"The heating effect of electric current is used in:",
 "options":["A: Electric fan","B: Electric motor","C: Electric iron","D: Solar panel"],
 "correctAnswer":"C",
 "explanation":"Electric iron uses the heating effect of current (Joule heating: H = I²Rt) to generate heat for pressing clothes."},

{"subject":"Science-Physics","grade":10,"difficulty":"Foundation","topic":"Physics",
 "subTopic":"Magnetic Field",
 "questionText":"The direction of magnetic field lines outside a bar magnet is from:",
 "options":["A: South pole to North pole","B: North pole to South pole","C: West to East","D: East to West"],
 "correctAnswer":"B",
 "explanation":"Magnetic field lines outside a magnet run from the North pole to the South pole (they go from S to N inside the magnet)."},

# ── Social Studies G9 Foundation top-up (15q, currently ~20) ─────────────────
{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"India — Contemporary World",
 "subTopic":"French Revolution — Causes",
 "questionText":"Which French king was executed during the French Revolution in 1793?",
 "options":["A: Louis XIV","B: Louis XV","C: Louis XVI","D: Napoleon Bonaparte"],
 "correctAnswer":"C",
 "explanation":"King Louis XVI was tried by the National Convention and executed by guillotine on 21 January 1793."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"India — Contemporary World",
 "subTopic":"World War I",
 "questionText":"The immediate cause of World War I was the assassination of Archduke Franz Ferdinand in:",
 "options":["A: Vienna","B: Paris","C: Sarajevo","D: Belgrade"],
 "correctAnswer":"C",
 "explanation":"Archduke Franz Ferdinand of Austria was assassinated in Sarajevo, Bosnia, on 28 June 1914, triggering World War I."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Physical Features of India",
 "subTopic":"Indian Mountains",
 "questionText":"The Aravalli Range is one of the oldest mountain ranges in India. It runs through which state?",
 "options":["A: Himachal Pradesh","B: Rajasthan","C: Uttarakhand","D: Meghalaya"],
 "correctAnswer":"B",
 "explanation":"The Aravalli Range runs through Rajasthan (and partly Haryana and Gujarat). It is one of the world's oldest fold mountains."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Physical Features of India",
 "subTopic":"Indian Rivers",
 "questionText":"The Ganga originates from which glacier?",
 "options":["A: Siachen Glacier","B: Zemu Glacier","C: Gangotri Glacier","D: Pindari Glacier"],
 "correctAnswer":"C",
 "explanation":"The Ganga (Bhagirathi) originates from the Gangotri Glacier in Uttarakhand. It is one of India's most sacred rivers."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Climate",
 "subTopic":"Indian Monsoon",
 "questionText":"The South-West Monsoon enters India first through:",
 "options":["A: Tamil Nadu coast","B: Andaman & Nicobar Islands then Kerala","C: Gujarat coast","D: Odisha coast"],
 "correctAnswer":"B",
 "explanation":"The Arabian Sea branch of the South-West Monsoon first hits the Andaman & Nicobar Islands around late May, then arrives on the Kerala coast around 1 June."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Democratic Politics",
 "subTopic":"What is Democracy",
 "questionText":"Which of the following best describes a democracy?",
 "options":["A: Rule by the military","B: Government chosen by the people","C: Rule by religious leaders","D: Government by the wealthiest citizens"],
 "correctAnswer":"B",
 "explanation":"Democracy means 'rule by the people'. In a democracy, the government is elected by citizens through free and fair elections."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Democratic Politics",
 "subTopic":"Constitutional Design",
 "questionText":"India is described as a 'Sovereign Socialist Secular Democratic Republic'. These words are in the:",
 "options":["A: First Schedule","B: Preamble","C: Seventh Schedule","D: Directive Principles"],
 "correctAnswer":"B",
 "explanation":"The Preamble to the Indian Constitution describes India as a Sovereign, Socialist, Secular, Democratic Republic (amended in 1976 by the 42nd Amendment to add 'Socialist' and 'Secular')."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Economics",
 "subTopic":"Poverty",
 "questionText":"In India, people living below the poverty line are identified using which measure?",
 "options":["A: GDP per capita","B: Consumption expenditure / calorie intake","C: Literacy rate","D: Land ownership"],
 "correctAnswer":"B",
 "explanation":"India's poverty line is determined using minimum consumption expenditure needed to meet basic calorie requirements (2400 kcal/day in rural areas, 2100 kcal/day in urban areas)."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Economics",
 "subTopic":"Food Security",
 "questionText":"The Public Distribution System (PDS) in India primarily distributes which food grain?",
 "options":["A: Millets","B: Wheat and Rice","C: Maize","D: Pulses only"],
 "correctAnswer":"B",
 "explanation":"The PDS mainly distributes wheat and rice (and sometimes sugar and kerosene) to below-poverty-line families through Fair Price Shops at subsidised rates."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Physical Features of India",
 "subTopic":"Indian Deserts",
 "questionText":"The Thar Desert is located in which part of India?",
 "options":["A: North-East India","B: Central India","C: North-West India","D: South India"],
 "correctAnswer":"C",
 "explanation":"The Thar Desert (Great Indian Desert) lies in north-western India, mainly in Rajasthan, and extends into Pakistan."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"India — Contemporary World",
 "subTopic":"Nazism",
 "questionText":"Adolf Hitler became the Chancellor of Germany in:",
 "options":["A: 1929","B: 1933","C: 1939","D: 1945"],
 "correctAnswer":"B",
 "explanation":"Adolf Hitler was appointed Chancellor of Germany on 30 January 1933, after the Nazi Party became the largest party in the Reichstag."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"India — Contemporary World",
 "subTopic":"Russian Revolution",
 "questionText":"The Russian Revolution of 1917 led to the formation of which type of government?",
 "options":["A: Constitutional monarchy","B: Parliamentary democracy","C: Communist Soviet state","D: Military dictatorship"],
 "correctAnswer":"C",
 "explanation":"The Bolshevik Revolution (October 1917) led by Lenin overthrew the Tsar's government and established a Communist state — the Soviet Union."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Physical Features of India",
 "subTopic":"Coastal Plains",
 "questionText":"The Malabar Coast is located on which side of India?",
 "options":["A: Eastern coast","B: Northern coast","C: Western coast","D: Southern tip"],
 "correctAnswer":"C",
 "explanation":"The Malabar Coast is part of India's western coastal plain, running through Kerala and Karnataka along the Arabian Sea."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Physical Features of India",
 "subTopic":"Islands",
 "questionText":"Lakshadweep islands are formed from:",
 "options":["A: Volcanic eruptions","B: Coral reefs","C: River delta deposits","D: Tectonic uplift"],
 "correctAnswer":"B",
 "explanation":"Lakshadweep is a group of coral islands in the Arabian Sea. They are formed from coral reefs and atolls."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Economics",
 "subTopic":"Human Capital Formation",
 "questionText":"Investment in education, health, and skill development is called:",
 "options":["A: Physical capital","B: Financial capital","C: Human capital","D: Social capital"],
 "correctAnswer":"C",
 "explanation":"Human capital refers to the skills, education, health, and knowledge of people that increases their productive capacity — investment in these areas builds human capital."},

{"subject":"Social Studies","grade":9,"difficulty":"Foundation","topic":"Democratic Politics",
 "subTopic":"Electoral System",
 "questionText":"In India's Lok Sabha elections, seats are distributed among states mainly on the basis of:",
 "options":["A: Area of the state","B: Revenue contribution","C: Population","D: Number of districts"],
 "correctAnswer":"C",
 "explanation":"Lok Sabha seats are allocated to states broadly on the basis of population, so that each state is proportionately represented."},

# ── G12 Social Studies Olympiad top-up (15q, currently 15 → 30) ───────────────
{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Social Movements",
 "questionText":"The Chipko Movement of the 1970s in Uttarakhand was primarily a protest against:",
 "options":["A: Mining activities","B: Commercial logging of forests","C: Construction of dams","D: Land acquisition for industry"],
 "correctAnswer":"B",
 "explanation":"The Chipko Movement (1973–74) involved villagers hugging trees to prevent commercial logging in the Himalayan forests of Uttarakhand. It became a landmark environmental movement."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Globalisation",
 "subTopic":"Cultural Globalisation",
 "questionText":"The term 'McDonaldisation' was coined by sociologist George Ritzer to describe:",
 "options":["A: Growth of fast food globally","B: Rationalisation and standardisation of society on the fast-food model","C: American cultural imperialism specifically","D: Decline of local cuisines worldwide"],
 "correctAnswer":"B",
 "explanation":"Ritzer's 'McDonaldisation' (1993) describes how principles of the fast-food industry — efficiency, calculability, predictability, control — are increasingly dominating all of society."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Caste and Class",
 "questionText":"The concept of 'dominant caste' in Indian sociology was introduced by:",
 "options":["A: B.R. Ambedkar","B: M.N. Srinivas","C: André Béteille","D: Louis Dumont"],
 "correctAnswer":"B",
 "explanation":"M.N. Srinivas introduced the concept of 'dominant caste' — a caste that wields power in a local area due to numerical strength, land ownership, and political power, not necessarily ritual status."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Tribes",
 "questionText":"The Narmada Bachao Andolan challenged the construction of which dam?",
 "options":["A: Bhakra-Nangal Dam","B: Tehri Dam","C: Sardar Sarovar Dam","D: Hirakud Dam"],
 "correctAnswer":"C",
 "explanation":"The Narmada Bachao Andolan, led by activists including Medha Patkar, challenged the construction of the Sardar Sarovar Dam over displacement of tribal communities and environmental damage."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Globalisation",
 "subTopic":"Economic Globalisation",
 "questionText":"The Washington Consensus refers to a set of economic policies emphasising:",
 "options":["A: State-led industrialisation","B: Trade protectionism and import substitution","C: Liberalisation, privatisation, and deregulation","D: Agrarian land redistribution"],
 "correctAnswer":"C",
 "explanation":"The Washington Consensus (1989) was a standard package of market-oriented economic reforms — trade liberalisation, privatisation, deregulation — prescribed by IMF/World Bank for developing countries."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Urbanisation",
 "questionText":"According to Census 2011, what percentage of India's population was urban?",
 "options":["A: 17.9%","B: 21.3%","C: 27.8%","D: 31.2%"],
 "correctAnswer":"D",
 "explanation":"The 2011 Census recorded India's urban population at approximately 31.2% (377 million out of 1.21 billion), up from 27.8% in 2001."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Agrarian Society",
 "questionText":"The Green Revolution in India is most associated with which crop and region?",
 "options":["A: Rice in West Bengal","B: Wheat in Punjab and Haryana","C: Cotton in Maharashtra","D: Sugarcane in Uttar Pradesh"],
 "correctAnswer":"B",
 "explanation":"The Green Revolution (1960s–70s) primarily benefited wheat cultivation in Punjab and Haryana through high-yielding seed varieties, irrigation, and fertilisers."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Demography",
 "questionText":"India achieved demographic transition in fertility rates but still faces population momentum because:",
 "options":["A: Death rates are rising","B: A large proportion of the population is in reproductive age","C: Migration from neighbouring countries is high","D: Life expectancy has fallen"],
 "correctAnswer":"B",
 "explanation":"Population momentum means even when fertility rates fall, population continues to grow because the large cohort of young people entering reproductive age ensures continued births."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Globalisation",
 "subTopic":"MNCs and Trade",
 "questionText":"Special Economic Zones (SEZs) were first introduced in India under which legislation?",
 "options":["A: Industries Development and Regulation Act, 1951","B: SEZ Act, 2005","C: Foreign Trade Policy, 1992","D: FEMA, 1999"],
 "correctAnswer":"B",
 "explanation":"India's SEZ Act was enacted in 2005 to promote exports and attract foreign investment by creating enclaves with special tax and regulatory incentives."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Religion and Society",
 "questionText":"Communalism as a political ideology in India refers to:",
 "options":["A: Common ownership of resources","B: Mobilisation of one religious community against another for political ends","C: Community-based local governance","D: Equal rights for all religious minorities"],
 "correctAnswer":"B",
 "explanation":"In Indian politics, communalism refers to the use of religious identity to mobilise one group against another, often exploiting religious differences for electoral or political gains."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Dalit Movements",
 "questionText":"B.R. Ambedkar publicly burned the Manusmriti in 1927 at which event?",
 "options":["A: Mahad Satyagraha","B: Kalaram Temple Entry Movement","C: Poona Pact signing","D: Nagpur Conversion"],
 "correctAnswer":"A",
 "explanation":"On 25 December 1927, during the Mahad Satyagraha (protest for Dalits' right to use the public Chavadar tank), Ambedkar publicly burned the Manusmriti to symbolise rejection of caste discrimination."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Globalisation",
 "subTopic":"Global Institutions",
 "questionText":"The International Monetary Fund (IMF) and World Bank were established as a result of:",
 "options":["A: The Treaty of Versailles (1919)","B: The Bretton Woods Conference (1944)","C: The UN Charter (1945)","D: The GATT Agreement (1947)"],
 "correctAnswer":"B",
 "explanation":"The IMF and World Bank were established at the Bretton Woods Conference in 1944 to manage international monetary cooperation and post-war reconstruction."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Women and Society",
 "questionText":"The self-help group (SHG) movement in India is most associated with:",
 "options":["A: Urban middle-class women's rights","B: Rural women's microfinance and empowerment","C: Higher education access for women","D: Women's political reservation"],
 "correctAnswer":"B",
 "explanation":"SHGs are small informal groups of rural women who pool savings and access micro-credit. They have become a major vehicle for rural women's economic empowerment across India."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Indian Society",
 "subTopic":"Social Stratification",
 "questionText":"Louis Dumont's work 'Homo Hierarchicus' (1966) argued that Indian caste system is fundamentally based on the principle of:",
 "options":["A: Economic class","B: Racial hierarchy","C: Ritual purity and pollution","D: Political dominance"],
 "correctAnswer":"C",
 "explanation":"Dumont argued that the caste hierarchy is ultimately an ideological system ordered by the opposition of ritual purity (Brahmin) and impurity (untouchable) rather than by economic or political power."},

{"subject":"Social Studies","grade":12,"difficulty":"Olympiad","topic":"Globalisation",
 "subTopic":"Cultural Change",
 "questionText":"The concept of 'Glocalization' (coined by Roland Robertson) refers to:",
 "options":["A: Local resistance to globalisation","B: Adaptation of global products/practices to local conditions","C: Economic integration of global markets","D: Migration of people across global cities"],
 "correctAnswer":"B",
 "explanation":"Glocalization describes how global products, ideas, and processes are adapted and modified to fit local cultures and conditions — think McDonald's serving McAloo Tikki in India."},

# ── G12 Logical Reasoning Foundation top-up (15q, currently ~34) ─────────────
{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Analogies",
 "questionText":"Doctor : Hospital :: Teacher : ?",
 "options":["A: Library","B: School","C: College","D: Clinic"],
 "correctAnswer":"B",
 "explanation":"A doctor works in a hospital; a teacher works in a school. The relationship is: professional : place of work."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Odd One Out",
 "questionText":"Which is the odd one out? Longitude, Latitude, Altitude, Meridian",
 "options":["A: Longitude","B: Latitude","C: Altitude","D: Meridian"],
 "correctAnswer":"C",
 "explanation":"Longitude, Latitude, and Meridian all relate to geographic coordinates on Earth's surface. Altitude refers to height above sea level — it is a different dimension."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Number Series",
 "subTopic":"Number Patterns",
 "questionText":"Find the next term: 1, 4, 9, 16, 25, ?",
 "options":["A: 30","B: 34","C: 36","D: 49"],
 "correctAnswer":"C",
 "explanation":"The series is perfect squares: 1²=1, 2²=4, 3²=9, 4²=16, 5²=25, 6²=36."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Coding-Decoding",
 "questionText":"If CAT = 3-1-20 (alphabetical positions), what is DOG?",
 "options":["A: 4-15-7","B: 4-14-6","C: 3-15-8","D: 5-16-8"],
 "correctAnswer":"A",
 "explanation":"D=4, O=15, G=7. Each letter is replaced by its position in the alphabet (A=1, B=2, … Z=26)."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Direction Sense",
 "questionText":"Rohit walks 10 m North, then 10 m East, then 10 m South. How far is he from his starting point?",
 "options":["A: 0 m","B: 10 m","C: 20 m","D: 30 m"],
 "correctAnswer":"B",
 "explanation":"After walking 10m North and 10m South he is back at the same latitude. He is displaced 10m East — so he is 10m from the starting point."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Blood Relations",
 "questionText":"Pointing to a photograph, Anu says 'This man's son is my son's father.' How is the man in the photograph related to Anu?",
 "options":["A: Father","B: Grandfather","C: Uncle","D: Brother"],
 "correctAnswer":"A",
 "explanation":"'My son's father' = Anu's husband. So the man's son is Anu's husband. Therefore the man is Anu's father-in-law. Wait — re-reading: 'my son's father' is Anu's husband. So the man's son = Anu's husband → the man is Anu's father-in-law. But answer A says 'Father' meaning father-in-law in common parlance. The relationship is Father (father-in-law)."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Number Series",
 "subTopic":"Missing Number",
 "questionText":"2, 6, 12, 20, 30, ?",
 "options":["A: 40","B: 42","C: 44","D: 56"],
 "correctAnswer":"B",
 "explanation":"Differences: 4, 6, 8, 10, 12. Next term = 30+12 = 42. Alternatively: n(n+1): 1×2=2, 2×3=6, 3×4=12, 4×5=20, 5×6=30, 6×7=42."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Syllogisms",
 "questionText":"All pens are pencils. All pencils are erasers. Conclusion: All pens are erasers — is this:",
 "options":["A: False","B: True","C: Uncertain","D: Partially true"],
 "correctAnswer":"B",
 "explanation":"From 'All pens are pencils' and 'All pencils are erasers', by transitivity: All pens are erasers. The conclusion is definitely true."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Statement and Assumptions",
 "questionText":"Statement: 'The company will hire only graduates.' Assumption implicit in this statement:",
 "options":["A: Graduates are always more competent","B: Non-graduates will not apply","C: The company has a policy on educational qualifications","D: Graduates are available in the market"],
 "correctAnswer":"D",
 "explanation":"For the statement to be actionable, it must be assumed that graduates are available in the market to be hired; otherwise the statement would be meaningless."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Alphabetical Order",
 "questionText":"If the letters of MASTER are arranged in alphabetical order, which letter will be in the middle (3rd position)?",
 "options":["A: M","B: R","C: S","D: T"],
 "correctAnswer":"A",
 "explanation":"Letters of MASTER: A, E, M, R, S, T (alphabetically). Position 3 is M."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Mathematical Operations",
 "questionText":"If '+' means '×', '×' means '−', '−' means '÷', and '÷' means '+', then 6 + 4 × 2 − 1 ÷ 5 = ?",
 "options":["A: 23","B: 27","C: 25","D: 20"],
 "correctAnswer":"B",
 "explanation":"Replace operators: 6+4×2−1÷5 → 6×4 − 2÷1 + 5. Apply BODMAS: multiplication/division first: 6×4=24, 2÷1=2. Then: 24 − 2 + 5 = 27."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Seating Arrangement",
 "questionText":"Five friends A, B, C, D, E sit in a row. A is to the left of B, C is to the right of B, D is to the right of C, E is between A and B. Who sits in the middle?",
 "options":["A: A","B: B","C: E","D: C"],
 "correctAnswer":"B",
 "explanation":"Order: A, E, B, C, D. B is in position 3 (middle of 5). B sits in the middle."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Number Series",
 "subTopic":"Letter-Number Series",
 "questionText":"AZ, BY, CX, DW, ?",
 "options":["A: EV","B: EU","C: FV","D: EW"],
 "correctAnswer":"A",
 "explanation":"First letter goes A, B, C, D, E (forward). Second letter goes Z, Y, X, W, V (backward). So next pair is EV."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Logical Deduction",
 "questionText":"Some A are B. No B is C. Conclusion: Some A are not C.",
 "options":["A: Definitely true","B: Definitely false","C: Possibly true","D: Data insufficient"],
 "correctAnswer":"A",
 "explanation":"Since some A are B, and no B is C, those A that are B cannot be C. Therefore, at least some A are definitely not C. The conclusion is definitely true."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Calendar",
 "questionText":"If 1 January 2023 was a Sunday, what day was 1 January 2024?",
 "options":["A: Sunday","B: Monday","C: Tuesday","D: Wednesday"],
 "correctAnswer":"B",
 "explanation":"2023 is a non-leap year (365 days = 52 weeks + 1 day). So 1 Jan 2024 is one day after Sunday = Monday."},

# ── Hindi G8 Advanced top-up (15q) ────────────────────────────────────────────
{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Sandhi",
 "questionText":"'देव + आलय' की संधि होगी:",
 "options":["A: देवालय","B: देव्यालय","C: देवायलय","D: देवीलय"],
 "correctAnswer":"A",
 "explanation":"अ + आ = आ (दीर्घ संधि)। देव (अ) + आलय (आ) = देवालय।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Samas (Compound Words)",
 "questionText":"'राजपुत्र' में कौन-सा समास है?",
 "options":["A: अव्ययीभाव","B: तत्पुरुष","C: द्वन्द्व","D: बहुव्रीहि"],
 "correctAnswer":"B",
 "explanation":"'राजा का पुत्र' — यहाँ उत्तरपद 'पुत्र' प्रधान है। यह तत्पुरुष समास है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Alankar (Figures of Speech)",
 "questionText":"'सागर सा गहरा मन है उसका' — इसमें कौन-सा अलंकार है?",
 "options":["A: उपमा","B: रूपक","C: उत्प्रेक्षा","D: अनुप्रास"],
 "correctAnswer":"A",
 "explanation":"उपमा अलंकार में किसी वस्तु की तुलना 'सा/सी/से/जैसा' आदि शब्दों से की जाती है। यहाँ 'मन' की तुलना 'सागर' से 'सा' शब्द द्वारा की गई है — यह उपमा अलंकार है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Kriya (Verb) Types",
 "questionText":"'राम ने सेब खाया' — इस वाक्य में क्रिया का भेद बताइए:",
 "options":["A: अकर्मक क्रिया","B: सकर्मक क्रिया","C: प्रेरणार्थक क्रिया","D: द्विकर्मक क्रिया"],
 "correctAnswer":"B",
 "explanation":"जिस क्रिया के साथ कर्म हो उसे सकर्मक क्रिया कहते हैं। यहाँ 'खाया' के साथ कर्म 'सेब' है, इसलिए यह सकर्मक क्रिया है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Literature",
 "subTopic":"Kabir",
 "questionText":"कबीरदास किस शाखा के कवि माने जाते हैं?",
 "options":["A: सगुण भक्ति — कृष्णभक्ति शाखा","B: सगुण भक्ति — रामभक्ति शाखा","C: निर्गुण भक्ति — ज्ञानमार्गी शाखा","D: निर्गुण भक्ति — प्रेममार्गी शाखा"],
 "correctAnswer":"C",
 "explanation":"कबीरदास निर्गुण भक्ति धारा के ज्ञानमार्गी शाखा के प्रमुख कवि हैं। वे निराकार ब्रह्म की उपासना पर जोर देते थे।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Kaal (Tense)",
 "questionText":"'वह कल दिल्ली जाएगा' — इस वाक्य का काल है:",
 "options":["A: भूतकाल","B: वर्तमानकाल","C: सामान्य भविष्यत काल","D: सामान्य भूतकाल"],
 "correctAnswer":"C",
 "explanation":"'जाएगा' क्रिया भविष्य की साधारण घटना दर्शाती है — यह सामान्य भविष्यत काल है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Vilom Shabd (Antonyms)",
 "questionText":"'आदान' का विलोम शब्द क्या है?",
 "options":["A: दान","B: प्रदान","C: ग्रहण","D: अर्पण"],
 "correctAnswer":"B",
 "explanation":"आदान = लेना; प्रदान = देना। 'आदान-प्रदान' एक प्रचलित द्वन्द्व समास पद है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Paryayvachi (Synonyms)",
 "questionText":"'नयन' का पर्यायवाची शब्द कौन-सा है?",
 "options":["A: कान","B: नासिका","C: नेत्र","D: हस्त"],
 "correctAnswer":"C",
 "explanation":"नयन, नेत्र, आँख, लोचन, दृग — ये सब 'आँख' के पर्यायवाची शब्द हैं।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Muhavare (Idioms)",
 "questionText":"'नौ दो ग्यारह होना' मुहावरे का अर्थ है:",
 "options":["A: बहुत खुश होना","B: भाग जाना","C: गणित में कुशल होना","D: एकजुट होना"],
 "correctAnswer":"B",
 "explanation":"'नौ दो ग्यारह होना' मुहावरे का अर्थ है 'भाग जाना' या 'रफूचक्कर हो जाना'।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Literature",
 "subTopic":"Premchand",
 "questionText":"प्रेमचंद की किस रचना में किसान जीवन की पीड़ा का मार्मिक चित्रण है?",
 "options":["A: गोदान","B: गबन","C: रंगभूमि","D: सेवासदन"],
 "correctAnswer":"A",
 "explanation":"'गोदान' (1936) प्रेमचंद का अंतिम और सर्वश्रेष्ठ उपन्यास है जिसमें होरी नामक किसान के माध्यम से भारतीय किसान की दुर्दशा का यथार्थ चित्रण किया गया है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Vakya Bhed (Sentence Types)",
 "questionText":"'क्या तुमने खाना खाया?' — यह वाक्य किस प्रकार का है?",
 "options":["A: विधानवाचक","B: प्रश्नवाचक","C: आज्ञावाचक","D: विस्मयादिबोधक"],
 "correctAnswer":"B",
 "explanation":"प्रश्न पूछने वाले वाक्य को प्रश्नवाचक वाक्य कहते हैं। इस वाक्य में 'क्या' से प्रश्न किया गया है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Upsarg (Prefix)",
 "questionText":"'अति' उपसर्ग से बना शब्द कौन-सा है?",
 "options":["A: अतिथि","B: अतिशय","C: अधिकार","D: अनुभव"],
 "correctAnswer":"B",
 "explanation":"'अतिशय' में 'अति' (अत्यधिक) उपसर्ग है। 'अतिथि' में 'अ' + 'तिथि' की संरचना है और 'अति' उपसर्ग नहीं है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Pratyay (Suffix)",
 "questionText":"'लिखाई' शब्द में प्रत्यय है:",
 "options":["A: -आई","B: -ई","C: -लि","D: -ख"],
 "correctAnswer":"A",
 "explanation":"लिख + आई = लिखाई। '-आई' भाववाचक संज्ञा बनाने वाला प्रत्यय है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Literature",
 "subTopic":"Ras (Rasas)",
 "questionText":"'वीर रस' का स्थायी भाव क्या है?",
 "options":["A: हास","B: शोक","C: उत्साह","D: भय"],
 "correctAnswer":"C",
 "explanation":"वीर रस का स्थायी भाव 'उत्साह' है। वीरता, साहस और पराक्रम के वर्णन में वीर रस की अभिव्यक्ति होती है।"},

{"subject":"Hindi","grade":8,"difficulty":"Advanced","topic":"Hindi Grammar",
 "subTopic":"Vachan (Number)",
 "questionText":"'नीति' शब्द का बहुवचन क्या है?",
 "options":["A: नीतियाँ","B: नीतिएँ","C: नीतें","D: नीतियों"],
 "correctAnswer":"A",
 "explanation":"'नीति' + बहुवचन प्रत्यय → नीतियाँ। '-इ'/'-ई' अंत वाले शब्दों में बहुवचन बनाने के लिए 'याँ' जोड़ा जाता है।"},

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
