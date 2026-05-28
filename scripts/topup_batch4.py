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
# G11 Commerce Advanced (15 questions) — missing tier entirely
# Covers Accountancy, Business Studies, Economics
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Accountancy — Journal Entries",
 "questionText":"Which accounting principle states that revenue should be recorded when earned, not when cash is received?",
 "options":["A: Going Concern","B: Revenue Recognition (Accrual) Principle","C: Matching Principle","D: Conservatism Principle"],"correctAnswer":"B",
 "explanation":"The Revenue Recognition (Accrual) principle states revenue is recognised when earned and realisable, regardless of when cash is actually received or paid."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Accountancy — Balance Sheet",
 "questionText":"In accounting, 'goodwill' is classified as:",
 "options":["A: Current Asset","B: Current Liability","C: Tangible Fixed Asset","D: Intangible Fixed Asset"],"correctAnswer":"D",
 "explanation":"Goodwill is an intangible fixed asset representing the value of a business's reputation, customer relations, brand, etc. It has no physical existence."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Accountancy — Depreciation",
 "questionText":"Under the Straight Line Method (SLM) of depreciation, annual depreciation is calculated as:",
 "options":["A: (Cost − Residual Value) ÷ Useful Life","B: Cost × Depreciation Rate","C: (Book Value − Residual Value) × Rate","D: Cost ÷ Useful Life only"],"correctAnswer":"A",
 "explanation":"SLM formula: Annual Depreciation = (Original Cost − Residual/Scrap Value) ÷ Useful Life in years. The same amount is charged every year, creating a straight-line graph."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Accountancy — Bank Reconciliation",
 "questionText":"A Bank Reconciliation Statement is prepared to:",
 "options":["A: Calculate the bank's profit","B: Reconcile the difference between the Cash Book balance and the Bank Statement balance","C: Determine the interest on overdraft","D: Prepare the final accounts of the business"],"correctAnswer":"B",
 "explanation":"A BRS reconciles why the cash book balance differs from the bank pass book balance, identifying timing differences (e.g., unpresented cheques, uncredited deposits) and errors."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Business Studies — Organisation",
 "questionText":"Which form of business organisation has 'unlimited liability' for its owners?",
 "options":["A: Private Limited Company","B: Public Limited Company","C: Sole Proprietorship","D: Government Company"],"correctAnswer":"C",
 "explanation":"In a sole proprietorship, the owner has unlimited personal liability — personal assets can be used to pay business debts. In limited companies, liability is limited to share capital invested."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Business Studies — Management",
 "questionText":"'Division of work' and 'Unity of Command' are principles of management proposed by:",
 "options":["A: F.W. Taylor","B: Elton Mayo","C: Henri Fayol","D: Peter Drucker"],"correctAnswer":"C",
 "explanation":"Henri Fayol proposed 14 Principles of General Management, including Division of Work, Unity of Command, Unity of Direction, and Scalar Chain, among others."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Business Studies — Finance",
 "questionText":"Which of the following is a long-term source of finance for a company?",
 "options":["A: Trade credit","B: Bank overdraft","C: Debentures","D: Factoring"],"correctAnswer":"C",
 "explanation":"Debentures are long-term debt instruments (typically 5–20 years). Trade credit, bank overdrafts, and factoring are short-term sources of finance."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Economics — Demand",
 "questionText":"When the price of a good falls and consumers buy less of it (because it is an inferior good), this is called the:",
 "options":["A: Substitution effect","B: Giffen good phenomenon","C: Income effect","D: Price effect"],"correctAnswer":"B",
 "explanation":"A Giffen good violates the law of demand — as price rises, quantity demanded also rises (and vice versa). It is a severely inferior good where the negative income effect outweighs the substitution effect (e.g., bread for the very poor)."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Economics — Supply",
 "questionText":"A rightward shift of the supply curve indicates:",
 "options":["A: Decrease in supply at the same price","B: Increase in supply — more is supplied at every price","C: A rise in the market price","D: A fall in demand"],"correctAnswer":"B",
 "explanation":"A rightward (downward) shift of the supply curve means producers offer more quantity at every price level. This can be caused by lower input costs, improved technology, or favourable government policies."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Economics — Market Structures",
 "questionText":"In a perfectly competitive market, firms are 'price takers' because:",
 "options":["A: They have patent protection","B: They have no market power — the market price is set by supply and demand","C: The government sets a fixed price","D: Only one buyer exists"],"correctAnswer":"B",
 "explanation":"In perfect competition, many identical firms sell a homogeneous product. No single firm can influence the market price; each firm must accept ('take') the market-determined price."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Accountancy — Cash Flow",
 "questionText":"Purchase of machinery is classified under which activity in a Cash Flow Statement?",
 "options":["A: Operating Activity","B: Investing Activity","C: Financing Activity","D: Non-cash Activity"],"correctAnswer":"B",
 "explanation":"Buying/selling fixed assets (like machinery, land, buildings) = Investing Activity. Operating = core business cash flows. Financing = loans, share capital, dividends."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Business Studies — Marketing",
 "questionText":"The '4 Ps' of the marketing mix are:",
 "options":["A: Product, Price, Place, Promotion","B: People, Process, Physical Evidence, Promotion","C: Planning, Pricing, Packaging, Publicity","D: Product, Profit, Place, People"],"correctAnswer":"A",
 "explanation":"The classic 4 Ps of the marketing mix are: Product (what you sell), Price (how much), Place (distribution), and Promotion (communication). Services marketing adds 3 more Ps: People, Process, Physical Evidence."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Economics — National Income",
 "questionText":"Which of the following is EXCLUDED from GDP calculation?",
 "options":["A: Government expenditure on roads","B: Export of software services","C: Sale of second-hand goods","D: Investment in new machinery"],"correctAnswer":"C",
 "explanation":"GDP measures only the value of NEW goods and services produced in a year. Sale of second-hand goods (e.g., a used car) does not represent new production, so it is excluded to avoid double counting."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Accountancy — Ratios",
 "questionText":"Current Ratio = Current Assets ÷ Current Liabilities. A current ratio of 2:1 means:",
 "options":["A: For every Rs 1 of liability, there is Rs 2 of current assets to cover it","B: The company has twice as many liabilities as assets","C: Current assets equal twice the fixed assets","D: The company is making 2% profit"],"correctAnswer":"A",
 "explanation":"Current ratio of 2:1 is considered healthy — it means for every Re 1 of short-term debt, the company has Rs 2 of liquid assets to pay it, indicating good short-term solvency."},

{"subject":"Commerce","grade":11,"difficulty":"Advanced","topic":"Commerce","subTopic":"Business Studies — Consumer Protection",
 "questionText":"The Consumer Protection Act 2019 provides for how many rights of consumers in India?",
 "options":["A: 4","B: 5","C: 6","D: 8"],"correctAnswer":"C",
 "explanation":"The Consumer Protection Act 2019 (and UN Guidelines) recognises 6 consumer rights: Right to Safety, Right to be Informed, Right to Choose, Right to be Heard, Right to Seek Redressal, and Right to Consumer Education."},

# ══════════════════════════════════════════════════════════════════════════════
# G11 Science Foundation (15 questions) — missing tier; covers CBSE Gr11 core topics
# Physics, Chemistry, Biology basics at Foundation level
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Physical World",
 "questionText":"Which branch of physics deals with the study of motion and its causes?",
 "options":["A: Thermodynamics","B: Electromagnetism","C: Mechanics","D: Optics"],"correctAnswer":"C",
 "explanation":"Mechanics is the branch of physics dealing with motion (kinematics) and its causes — forces and energy (dynamics). Classical mechanics was formulated by Newton."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Units and Measurement",
 "questionText":"The SI unit of electric charge is:",
 "options":["A: Ampere","B: Volt","C: Coulomb","D: Ohm"],"correctAnswer":"C",
 "explanation":"The Coulomb (C) is the SI unit of electric charge. 1 Coulomb = charge transported by 1 Ampere of current flowing for 1 second. Named after Charles-Augustin de Coulomb."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Motion in a Straight Line",
 "questionText":"A car accelerates uniformly from rest to 72 km/h in 10 seconds. Its acceleration is:",
 "options":["A: 1 m/s²","B: 2 m/s²","C: 7.2 m/s²","D: 4 m/s²"],"correctAnswer":"B",
 "explanation":"Convert 72 km/h to m/s: 72 × (1000/3600) = 20 m/s. Acceleration = (v−u)/t = (20−0)/10 = 2 m/s²."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Laws of Motion",
 "questionText":"Newton's Third Law of Motion states:",
 "options":["A: F = ma","B: A body at rest remains at rest unless acted upon by an external force","C: For every action there is an equal and opposite reaction","D: Acceleration is directly proportional to net force"],"correctAnswer":"C",
 "explanation":"Newton's Third Law: every action force has an equal and opposite reaction force. Example: a rocket expels gas backward (action) and moves forward (reaction)."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Structure of Atom",
 "questionText":"The number of protons in an atom determines its:",
 "options":["A: Atomic mass","B: Atomic number","C: Mass number","D: Neutron count"],"correctAnswer":"B",
 "explanation":"The atomic number (Z) = number of protons in the nucleus. It uniquely identifies each element. Atomic mass ≈ protons + neutrons."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Chemical Bonding",
 "questionText":"A covalent bond is formed by:",
 "options":["A: Transfer of electrons from one atom to another","B: Sharing of electron pairs between atoms","C: Attraction between opposite ions","D: Exchange of protons between nuclei"],"correctAnswer":"B",
 "explanation":"Covalent bonds form when atoms share one or more pairs of electrons, achieving stable electron configurations. Example: H₂O — oxygen shares electrons with two hydrogen atoms."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"States of Matter",
 "questionText":"At what temperature (°C) and pressure (atm) is the 'Standard Temperature and Pressure' (STP) defined?",
 "options":["A: 0°C and 1 atm","B: 25°C and 1 atm","C: 100°C and 1 atm","D: 0°C and 0 atm"],"correctAnswer":"A",
 "explanation":"STP is defined as 0°C (273.15 K) and 1 atm (101.325 kPa). At STP, 1 mole of an ideal gas occupies 22.4 litres."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Thermodynamics",
 "questionText":"The First Law of Thermodynamics is essentially a statement of:",
 "options":["A: Conservation of Mass","B: Conservation of Energy","C: Conservation of Momentum","D: Conservation of Charge"],"correctAnswer":"B",
 "explanation":"The First Law of Thermodynamics states that energy cannot be created or destroyed — only converted from one form to another. ΔU = Q − W (change in internal energy = heat absorbed − work done)."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Cell Biology",
 "questionText":"The cell membrane is described as 'selectively permeable' because it:",
 "options":["A: Allows all substances to pass freely","B: Blocks all substances from passing","C: Allows only certain substances to pass through","D: Is made of a single layer of protein"],"correctAnswer":"C",
 "explanation":"The cell membrane is selectively permeable (semi-permeable) — it allows water and small non-polar molecules to pass freely while regulating entry of ions, glucose, and large molecules."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Biological Classification",
 "questionText":"The five-kingdom classification system was proposed by:",
 "options":["A: Carl Linnaeus","B: Charles Darwin","C: R.H. Whittaker","D: Ernst Haeckel"],"correctAnswer":"C",
 "explanation":"R.H. Whittaker (1969) proposed the Five Kingdom classification: Monera, Protista, Fungi, Plantae, and Animalia, based on cell structure, nutrition, and body organisation."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Plant Physiology",
 "questionText":"Transpiration in plants primarily occurs through tiny pores called:",
 "options":["A: Lenticels","B: Stomata","C: Hydathodes","D: Guard cells"],"correctAnswer":"B",
 "explanation":"Stomata are tiny pores on leaf surfaces (guarded by guard cells) through which ~90% of transpiration occurs. Lenticels are on bark; hydathodes release water droplets (guttation)."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Human Physiology",
 "questionText":"The largest gland in the human body is the:",
 "options":["A: Pancreas","B: Thyroid","C: Liver","D: Adrenal gland"],"correctAnswer":"C",
 "explanation":"The liver is the largest internal gland/organ in the human body (~1.5 kg). It performs over 500 functions including detoxification, protein synthesis, and bile production for fat digestion."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Periodic Table",
 "questionText":"Elements in the same GROUP (vertical column) of the periodic table have similar chemical properties because they have:",
 "options":["A: The same atomic mass","B: The same number of protons","C: The same number of valence electrons","D: The same number of neutrons"],"correctAnswer":"C",
 "explanation":"Elements in the same group have identical valence electron configurations (e.g., all alkali metals have 1 valence electron). Valence electrons determine chemical bonding behaviour."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Waves and Sound",
 "questionText":"The speed of sound is greatest in which medium?",
 "options":["A: Vacuum","B: Air at room temperature","C: Water","D: Steel"],"correctAnswer":"D",
 "explanation":"Sound travels faster in denser/stiffer media: Steel (~5100 m/s) > Water (~1500 m/s) > Air (~343 m/s). Sound cannot travel through vacuum at all."},

{"subject":"Science","grade":11,"difficulty":"Foundation","topic":"Science","subTopic":"Environmental Chemistry",
 "questionText":"The 'greenhouse effect' is caused primarily by which gases trapping heat in Earth's atmosphere?",
 "options":["A: Oxygen and Nitrogen","B: CO₂, methane, water vapour, and nitrous oxide","C: Ozone and argon","D: Hydrogen and helium"],"correctAnswer":"B",
 "explanation":"Greenhouse gases (CO₂, CH₄, H₂O vapour, N₂O, and fluorinated gases) absorb and re-emit infrared radiation, trapping heat. N₂ and O₂ (78%+21% of atmosphere) are NOT greenhouse gases."},

# ══════════════════════════════════════════════════════════════════════════════
# GK G10 Advanced top-up (+10, currently 23 → 33) — rich GK for Grade 10
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Indian Polity",
 "questionText":"How many schedules does the Indian Constitution contain (as amended)?",
 "options":["A: 8","B: 10","C: 12","D: 14"],"correctAnswer":"C",
 "explanation":"The Indian Constitution currently has 12 Schedules. It originally had 8; the 9th was added in 1951, the 10th (Anti-Defection) in 1985, the 11th (Panchayati Raj) and 12th (Municipalities) in 1992."},

{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Science",
 "questionText":"Which organ produces insulin in the human body?",
 "options":["A: Liver","B: Kidney","C: Pancreas","D: Thyroid gland"],"correctAnswer":"C",
 "explanation":"Insulin is produced by the beta cells of the Islets of Langerhans in the pancreas. It regulates blood glucose levels. Absence or insufficiency of insulin causes diabetes mellitus."},

{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Indian History",
 "questionText":"The Indian National Congress was founded in which year?",
 "options":["A: 1857","B: 1885","C: 1905","D: 1919"],"correctAnswer":"B",
 "explanation":"The Indian National Congress (INC) was founded on 28 December 1885 in Bombay by A.O. Hume, Dadabhai Naoroji, and Dinshaw Wacha. Womesh Chandra Bonnerjee was its first president."},

{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"World Geography",
 "questionText":"The Amazon River flows into which ocean?",
 "options":["A: Pacific Ocean","B: Atlantic Ocean","C: Indian Ocean","D: Caribbean Sea"],"correctAnswer":"B",
 "explanation":"The Amazon River, the world's largest river by discharge, flows through Brazil and empties into the Atlantic Ocean near Marajó Island."},

{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Science and Technology",
 "questionText":"Wi-Fi technology uses which type of electromagnetic waves?",
 "options":["A: Infrared waves","B: X-rays","C: Radio waves (microwave frequency)","D: Ultraviolet waves"],"correctAnswer":"C",
 "explanation":"Wi-Fi operates on radio waves at 2.4 GHz and 5 GHz frequencies (microwave range). These frequencies pass through walls and are non-ionising and safe for everyday use."},

{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Economy",
 "questionText":"The Reserve Bank of India (RBI) was established in which year?",
 "options":["A: 1935","B: 1947","C: 1950","D: 1969"],"correctAnswer":"A",
 "explanation":"The RBI was established on 1 April 1935 under the Reserve Bank of India Act, 1934. It was nationalised in 1949. It is India's central bank and monetary authority."},

{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Space Science",
 "questionText":"ISRO's Chandrayaan-3 successfully landed on the Moon's south pole in:",
 "options":["A: 2019","B: 2021","C: 2023","D: 2022"],"correctAnswer":"C",
 "explanation":"Chandrayaan-3's Vikram lander touched down near the Moon's south pole on 23 August 2023, making India the first country to land near the lunar south pole and the 4th to land on the Moon."},

{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Sports",
 "questionText":"Saina Nehwal won India's first individual Olympic medal in badminton at the:",
 "options":["A: 2004 Athens Olympics","B: 2008 Beijing Olympics","C: 2012 London Olympics","D: 2016 Rio Olympics"],"correctAnswer":"C",
 "explanation":"Saina Nehwal won the Bronze Medal at the 2012 London Olympics — India's first individual Olympic medal in badminton."},

{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Literature",
 "questionText":"Arundhati Roy won the Booker Prize in 1997 for which novel?",
 "options":["A: The Inheritance of Loss","B: The God of Small Things","C: A Fine Balance","D: The White Tiger"],"correctAnswer":"B",
 "explanation":"Arundhati Roy won the Booker Prize (Man Booker Prize) in 1997 for her debut novel 'The God of Small Things', a story set in Kerala. 'The Inheritance of Loss' is by Kiran Desai (2006)."},

{"subject":"General Knowledge","grade":10,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Environment",
 "questionText":"Project Tiger was launched in India in which year to protect the Bengal tiger?",
 "options":["A: 1965","B: 1969","C: 1973","D: 1980"],"correctAnswer":"C",
 "explanation":"Project Tiger was launched on 1 April 1973 by Prime Minister Indira Gandhi. It started with 9 tiger reserves and now covers 53+ reserves across India."},

# ══════════════════════════════════════════════════════════════════════════════
# Hindi G5 Foundation top-up (+10, currently 152 → 162) — targeting thin sub-topics
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Muhavare",
 "questionText":"'आँखें खुलना' मुहावरे का सही अर्थ क्या है?",
 "options":["A: नींद से जागना","B: सच्चाई का पता चलना","C: आँखों में दर्द होना","D: आँखों का व्यायाम करना"],"correctAnswer":"B",
 "explanation":"'आँखें खुलना' का अर्थ है — होश में आना या सच्चाई का बोध होना।"},

{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Vilom Shabd",
 "questionText":"'उपस्थित' का विलोम शब्द क्या है?",
 "options":["A: हाजिर","B: मौजूद","C: अनुपस्थित","D: उपलब्ध"],"correctAnswer":"C",
 "explanation":"'उपस्थित' (present) का विलोम 'अनुपस्थित' (absent) है।"},

{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Paryayvachi Shabd",
 "questionText":"'वायु' का पर्यायवाची शब्द कौन-सा है?",
 "options":["A: जल","B: समीर","C: अग्नि","D: भूमि"],"correctAnswer":"B",
 "explanation":"'वायु' (हवा/wind) के पर्यायवाची हैं — समीर, पवन, अनिल, मारुत।"},

{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Sandhi",
 "questionText":"'सूर्य + उदय' = 'सूर्योदय' में कौन-सी संधि है?",
 "options":["A: व्यंजन संधि","B: विसर्ग संधि","C: गुण स्वर संधि","D: यण संधि"],"correctAnswer":"C",
 "explanation":"अ/आ + उ/ऊ = ओ (गुण संधि)। 'सूर्य' के अंत में 'अ' + 'उदय' के आरंभ में 'उ' = 'ओ' → सूर्योदय।"},

{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Ling",
 "questionText":"'शेर' का स्त्रीलिंग क्या है?",
 "options":["A: शेरी","B: शेरनी","C: शेरिन","D: शेरा"],"correctAnswer":"B",
 "explanation":"'शेर' का स्त्रीलिंग 'शेरनी' होता है।"},

{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Vachan",
 "questionText":"'पत्ता' का बहुवचन क्या है?",
 "options":["A: पत्ते","B: पत्तियाँ","C: पत्ताएँ","D: पत्तों"],"correctAnswer":"A",
 "explanation":"'पत्ता' का बहुवचन 'पत्ते' होता है।"},

{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Kaal",
 "questionText":"'राहुल खाना खा रहा है।' इस वाक्य में कौन-सा काल है?",
 "options":["A: भूतकाल","B: वर्तमान काल (अपूर्ण)","C: भविष्यकाल","D: सामान्य वर्तमान"],"correctAnswer":"B",
 "explanation":"'खा रहा है' क्रिया से पता चलता है कि काम अभी हो रहा है — यह अपूर्ण वर्तमानकाल (Present Continuous Tense) है।"},

{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Swar Vyanjan",
 "questionText":"हिंदी वर्णमाला में कुल कितने स्वर हैं?",
 "options":["A: 10","B: 11","C: 13","D: 16"],"correctAnswer":"B",
 "explanation":"हिंदी वर्णमाला में 11 स्वर हैं: अ, आ, इ, ई, उ, ऊ, ऋ, ए, ऐ, ओ, औ।"},

{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Alankar",
 "questionText":"'पीपर पात सरिस मन डोला' — इस पंक्ति में कौन-सा अलंकार है?",
 "options":["A: रूपक","B: उपमा","C: अनुप्रास","D: यमक"],"correctAnswer":"B",
 "explanation":"'पीपल के पत्ते की तरह मन हिल गया' — यहाँ 'सरिस' (जैसा) से तुलना की गई है, इसलिए यह उपमा अलंकार है।"},

{"subject":"Hindi","grade":5,"difficulty":"Foundation","topic":"Hindi","subTopic":"Nibandh",
 "questionText":"एक अच्छे निबंध में मुख्यतः कितने भाग होते हैं?",
 "options":["A: 2","B: 3","C: 4","D: 5"],"correctAnswer":"B",
 "explanation":"एक अच्छे निबंध में 3 मुख्य भाग होते हैं: 1. प्रस्तावना (भूमिका), 2. विषय-विस्तार (मुख्य भाग), 3. उपसंहार (निष्कर्ष)।"},

# ══════════════════════════════════════════════════════════════════════════════
# Mathematics G4 Advanced top-up (+10, currently 69 → 79)
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Fractions",
 "questionText":"Which of the following fractions is the LARGEST?",
 "options":["A: 3/4","B: 5/6","C: 7/10","D: 2/3"],"correctAnswer":"B",
 "explanation":"Convert to same denominator (60): 3/4=45/60, 5/6=50/60, 7/10=42/60, 2/3=40/60. Largest numerator is 50, so 5/6 is the largest."},

{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Decimals",
 "questionText":"What is 2.75 + 1.6?",
 "options":["A: 3.81","B: 4.25","C: 4.35","D: 3.35"],"correctAnswer":"C",
 "explanation":"2.75 + 1.6 = 2.75 + 1.60 = 4.35. Align decimal points: 2.75 + 1.60 = 4.35."},

{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Divisibility",
 "questionText":"Which of the following numbers is divisible by both 6 and 9?",
 "options":["A: 36","B: 30","C: 24","D: 21"],"correctAnswer":"A",
 "explanation":"Divisible by 6: must be divisible by both 2 and 3. Divisible by 9: digit sum must be divisible by 9. 36: digit sum=9 (÷9 ✓), 36÷6=6 ✓. 30: 30÷9 not whole. 24: 24÷9 not whole. 21: odd, not ÷6."},

{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Area",
 "questionText":"A square garden has a side of 12 m. What is its area?",
 "options":["A: 48 sq m","B: 120 sq m","C: 144 sq m","D: 96 sq m"],"correctAnswer":"C",
 "explanation":"Area of a square = side × side = 12 × 12 = 144 sq m."},

{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Word Problem — Division",
 "questionText":"576 books are to be packed equally into 24 boxes. How many books will be in each box?",
 "options":["A: 20","B: 22","C: 24","D: 28"],"correctAnswer":"C",
 "explanation":"576 ÷ 24 = 24. Each box will contain 24 books. Verify: 24 × 24 = 576 ✓"},

{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Roman Numerals",
 "questionText":"What is XC + XIV in Roman numerals written as an Arabic number?",
 "options":["A: 94","B: 100","C: 104","D: 114"],"correctAnswer":"C",
 "explanation":"XC = 90 (100−10). XIV = 14 (10+4). 90 + 14 = 104."},

{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Perimeter",
 "questionText":"A rectangle has a length of 18 cm and a perimeter of 52 cm. What is its width?",
 "options":["A: 6 cm","B: 7 cm","C: 8 cm","D: 9 cm"],"correctAnswer":"C",
 "explanation":"Perimeter = 2(length + width). 52 = 2(18 + w). 26 = 18 + w. w = 8 cm."},

{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Patterns",
 "questionText":"What is the next number in the pattern: 3, 6, 12, 24, 48, __?",
 "options":["A: 72","B: 84","C: 96","D: 60"],"correctAnswer":"C",
 "explanation":"Each number doubles. 48 × 2 = 96."},

{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Time",
 "questionText":"A film starts at 7:45 PM and lasts 2 hours 30 minutes. At what time does it end?",
 "options":["A: 9:45 PM","B: 10:00 PM","C: 10:15 PM","D: 9:30 PM"],"correctAnswer":"C",
 "explanation":"7:45 PM + 2 hours = 9:45 PM. 9:45 PM + 30 minutes = 10:15 PM."},

{"subject":"Mathematics","grade":4,"difficulty":"Advanced","topic":"Mathematics","subTopic":"Multi-step Word Problem",
 "questionText":"Rahim has 3 times as many marbles as Suresh. Suresh has 45 marbles. If Rahim gives 30 marbles to Suresh, how many more marbles does Rahim have than Suresh?",
 "options":["A: 30","B: 45","C: 15","D: 60"],"correctAnswer":"A",
 "explanation":"Rahim starts: 3×45=135. After giving 30: Rahim has 135−30=105, Suresh has 45+30=75. Difference = 105−75=30."},

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
