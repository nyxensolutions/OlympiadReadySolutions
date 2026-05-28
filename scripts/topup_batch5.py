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
# Science G4 Advanced (+12, currently 51 → 63) — CBSE/NCERT Class 4 Science
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Food and Nutrition",
 "questionText":"Scurvy is a disease caused by the deficiency of which vitamin?",
 "options":["A: Vitamin A","B: Vitamin B","C: Vitamin C","D: Vitamin D"],"correctAnswer":"C",
 "explanation":"Scurvy is caused by Vitamin C (ascorbic acid) deficiency. Symptoms include bleeding gums and weak joints. Vitamin C is found in citrus fruits, amla, and guava."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Animals",
 "questionText":"Which of the following animals is a marsupial (carries its young in a pouch)?",
 "options":["A: Elephant","B: Kangaroo","C: Polar bear","D: Dolphin"],"correctAnswer":"B",
 "explanation":"Marsupials are mammals that carry underdeveloped young in a pouch. Kangaroos, koalas, and wombats are famous marsupials, mostly found in Australia."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Plants",
 "questionText":"The process by which plants lose water vapour through their leaves is called:",
 "options":["A: Photosynthesis","B: Transpiration","C: Respiration","D: Pollination"],"correctAnswer":"B",
 "explanation":"Transpiration is the evaporation of water from plant surfaces, mainly through stomata in leaves. This helps pull water up from roots and cools the plant."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Matter",
 "questionText":"When water is heated to 100°C at sea level, it changes from liquid to gas. This process is called:",
 "options":["A: Condensation","B: Evaporation","C: Boiling","D: Sublimation"],"correctAnswer":"C",
 "explanation":"Boiling occurs when liquid reaches its boiling point throughout its volume (100°C for water at sea level). Evaporation happens only at the surface at any temperature below boiling point."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Rocks and Soil",
 "questionText":"Which type of rock is formed from cooled and hardened lava?",
 "options":["A: Sedimentary rock","B: Metamorphic rock","C: Igneous rock","D: Fossil rock"],"correctAnswer":"C",
 "explanation":"Igneous rocks (e.g., basalt, granite) form when magma (underground) or lava (surface) cools and solidifies. 'Igneous' comes from Latin 'ignis' meaning fire."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Light",
 "questionText":"A periscope works using the principle of:",
 "options":["A: Refraction of light","B: Absorption of light","C: Reflection of light","D: Diffraction of light"],"correctAnswer":"C",
 "explanation":"A periscope uses two mirrors (or prisms) at 45° angles to reflect light, allowing you to see over or around obstacles. Used in submarines and for peeking over walls."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Force and Motion",
 "questionText":"Which of the following always OPPOSES motion?",
 "options":["A: Gravity","B: Magnetic force","C: Friction","D: Applied force"],"correctAnswer":"C",
 "explanation":"Friction always acts opposite to the direction of motion (or tendency of motion). It is caused by the roughness between two surfaces in contact."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Human Body",
 "questionText":"The human heart has how many chambers?",
 "options":["A: 2","B: 3","C: 4","D: 6"],"correctAnswer":"C",
 "explanation":"The human heart has 4 chambers: 2 atria (upper) and 2 ventricles (lower). The right side pumps blood to the lungs; the left side pumps oxygenated blood to the body."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Insects",
 "questionText":"Which of the following is an INCOMPLETE metamorphosis (egg → nymph → adult, with NO pupa stage)?",
 "options":["A: Butterfly","B: Moth","C: Grasshopper","D: Housefly"],"correctAnswer":"C",
 "explanation":"Grasshoppers undergo incomplete metamorphosis (hemimetabolism): egg → nymph → adult (no pupa). Butterflies, moths, and houseflies undergo complete metamorphosis (egg → larva → pupa → adult)."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Environment",
 "questionText":"What is the full form of CNG (a cleaner fuel used in vehicles)?",
 "options":["A: Carbon Natural Gas","B: Compressed Natural Gas","C: Clean Nitrogen Gas","D: Cooled Natural Gas"],"correctAnswer":"B",
 "explanation":"CNG stands for Compressed Natural Gas (mainly methane compressed under high pressure). It burns more cleanly than petrol or diesel, producing fewer pollutants."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Water",
 "questionText":"The process by which water vapour in the air cools and turns into liquid water droplets (as seen on a cold glass) is called:",
 "options":["A: Evaporation","B: Precipitation","C: Condensation","D: Infiltration"],"correctAnswer":"C",
 "explanation":"Condensation is the change from gas (vapour) to liquid when water vapour cools below the dew point. This forms dew, clouds, fog, and water droplets on cold surfaces."},

{"subject":"Science","grade":4,"difficulty":"Advanced","topic":"Science","subTopic":"Stars and Space",
 "questionText":"The Sun is a:",
 "options":["A: Planet","B: Satellite","C: Star","D: Asteroid"],"correctAnswer":"C",
 "explanation":"The Sun is a medium-sized star — a huge ball of hot glowing gases (mainly hydrogen and helium) at the centre of our solar system. It is about 150 million km from Earth."},

# ══════════════════════════════════════════════════════════════════════════════
# Hindi G4 Advanced (+12, currently 48 → 60) — NCERT Grade 4 Hindi
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Sangya ke Bhed",
 "questionText":"'बचपन' किस प्रकार की संज्ञा का उदाहरण है?",
 "options":["A: जातिवाचक","B: व्यक्तिवाचक","C: भाववाचक","D: द्रव्यवाचक"],"correctAnswer":"C",
 "explanation":"'बचपन' एक भाव (अवस्था) का नाम है — इसे छू या देख नहीं सकते। इसलिए यह भाववाचक संज्ञा है।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Muhavare",
 "questionText":"'दाँत खट्टे करना' मुहावरे का अर्थ क्या है?",
 "options":["A: खट्टा खाना खाना","B: हराना या परेशान करना","C: मुँह मीठा करना","D: चुप हो जाना"],"correctAnswer":"B",
 "explanation":"'दाँत खट्टे करना' का अर्थ है — किसी को हरा देना या बुरी तरह परेशान कर देना।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Vilom Shabd",
 "questionText":"'सफलता' का विलोम शब्द क्या है?",
 "options":["A: जीत","B: असफलता","C: हार","D: विजय"],"correctAnswer":"B",
 "explanation":"'सफलता' (success) का विलोम 'असफलता' (failure) है। उपसर्ग 'अ' जोड़ने से विलोम बनता है।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Sandhi",
 "questionText":"'महा + उत्सव' = 'महोत्सव' में कौन-सी संधि है?",
 "options":["A: दीर्घ संधि","B: गुण संधि","C: वृद्धि संधि","D: यण संधि"],"correctAnswer":"B",
 "explanation":"आ + उ = ओ (गुण संधि)। 'महा' के आखिर में 'आ' + 'उत्सव' के शुरू में 'उ' = 'ओ' → महोत्सव।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Karak",
 "questionText":"'मेज पर किताब है।' इस वाक्य में 'पर' किस कारक की परसर्ग है?",
 "options":["A: सम्बन्ध कारक","B: करण कारक","C: अधिकरण कारक","D: अपादान कारक"],"correctAnswer":"C",
 "explanation":"'पर' अधिकरण कारक की परसर्ग है, जो स्थान या समय का बोध कराती है। 'मेज पर' = मेज में/ऊपर।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Visheshan",
 "questionText":"'गुणवाचक विशेषण' का उदाहरण कौन-सा है?",
 "options":["A: पाँच लड़के","B: थोड़ा पानी","C: वह किताब","D: लाल गुलाब"],"correctAnswer":"D",
 "explanation":"'लाल' एक गुण (रंग) बताता है, इसलिए यह गुणवाचक विशेषण है। 'पाँच' संख्यावाचक है, 'थोड़ा' परिमाणवाचक है।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Kriya",
 "questionText":"'मैं खाना खाता हूँ।' इस वाक्य में 'खाता हूँ' किस प्रकार की क्रिया है?",
 "options":["A: अकर्मक क्रिया","B: सकर्मक क्रिया","C: संयुक्त क्रिया","D: प्रेरणार्थक क्रिया"],"correctAnswer":"B",
 "explanation":"सकर्मक क्रिया वह है जिसका फल कर्म पर पड़ता है। 'खाना खाता हूँ' — यहाँ 'खाना' कर्म है और क्रिया का फल उस पर पड़ता है।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Upsarg aur Pratyay",
 "questionText":"'सुन्दरता' शब्द में कौन-सा प्रत्यय है?",
 "options":["A: सुन्दर","B: ता","C: सुन","D: अ"],"correctAnswer":"B",
 "explanation":"'सुन्दरता' = 'सुन्दर' (मूल शब्द) + 'ता' (प्रत्यय)। 'ता' प्रत्यय जोड़ने से विशेषण से भाववाचक संज्ञा बनती है।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Vachan",
 "questionText":"'नेता' का बहुवचन क्या है?",
 "options":["A: नेते","B: नेताएँ","C: नेताओं","D: नेतागण"],"correctAnswer":"D",
 "explanation":"'नेता' का बहुवचन 'नेतागण' या 'नेता' (बहुवचन में अपरिवर्तित भी) है। 'गण' प्रत्यय जोड़कर भी बहुवचन बनाया जाता है।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Ling",
 "questionText":"'मोर' का स्त्रीलिंग क्या है?",
 "options":["A: मोरी","B: मोरनी","C: मोरा","D: मोरिया"],"correctAnswer":"B",
 "explanation":"'मोर' (peacock) का स्त्रीलिंग 'मोरनी' (peahen) होता है।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Paryayvachi Shabd",
 "questionText":"'अग्नि' का पर्यायवाची शब्द कौन-सा है?",
 "options":["A: पवन","B: आकाश","C: आग","D: जल"],"correctAnswer":"C",
 "explanation":"'अग्नि' के पर्यायवाची हैं: आग, अनल, ज्वाला, पावक, हुताशन। 'पवन' वायु का, 'आकाश' গগণ का पर्यायवाची है।"},

{"subject":"Hindi","grade":4,"difficulty":"Advanced","topic":"Hindi","subTopic":"Alankar",
 "questionText":"'पत्थर-सा सख्त दिल है उसका' — इस वाक्य में कौन-सा अलंकार है?",
 "options":["A: रूपक","B: उपमा","C: अनुप्रास","D: अतिशयोक्ति"],"correctAnswer":"B",
 "explanation":"'जैसा/सा' से तुलना की गई है — दिल की तुलना पत्थर से की गई है। यह उपमा अलंकार है।"},

# ══════════════════════════════════════════════════════════════════════════════
# CS G4 Advanced (+12, currently 50 → 62) — CBSE/NCERT Computer Science Grade 4
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Binary Numbers",
 "questionText":"What is the decimal value of binary number 1010?",
 "options":["A: 8","B: 9","C: 10","D: 12"],"correctAnswer":"C",
 "explanation":"1010 in binary = 1×8 + 0×4 + 1×2 + 0×1 = 8+0+2+0 = 10."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"MS Word",
 "questionText":"In MS Word, which shortcut key is used to make selected text BOLD?",
 "options":["A: Ctrl+I","B: Ctrl+U","C: Ctrl+B","D: Ctrl+E"],"correctAnswer":"C",
 "explanation":"Ctrl+B applies Bold formatting. Ctrl+I applies Italic, Ctrl+U applies Underline, Ctrl+E centres the paragraph."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Internet Safety",
 "questionText":"Which of the following is a SAFE practice while using the internet?",
 "options":["A: Share your home address with online strangers","B: Click on all pop-up ads","C: Use strong passwords and never share them","D: Download software from any unknown website"],"correctAnswer":"C",
 "explanation":"Using strong, unique passwords and keeping them private is essential internet safety. Never share personal information with strangers, click suspicious ads, or download from untrusted sources."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Hardware",
 "questionText":"The motherboard is:",
 "options":["A: A type of output device","B: The main circuit board that connects all computer components","C: External storage like a pen drive","D: A type of monitor"],"correctAnswer":"B",
 "explanation":"The motherboard is the primary printed circuit board (PCB) inside a computer. It houses the CPU, RAM slots, and connects all hardware components."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Algorithms",
 "questionText":"An algorithm must have which of the following properties?",
 "options":["A: It must be written in Python","B: It must have a definite start and end, with clear unambiguous steps","C: It must use only numbers","D: It must be run on a computer to be valid"],"correctAnswer":"B",
 "explanation":"An algorithm is a finite, ordered set of well-defined instructions that solves a problem. It must have: a clear start/end, unambiguous steps, finite execution, and produce a result."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"File Management",
 "questionText":"In Windows, what is the keyboard shortcut to DELETE a selected file permanently (bypassing Recycle Bin)?",
 "options":["A: Delete","B: Ctrl+Delete","C: Shift+Delete","D: Alt+Delete"],"correctAnswer":"C",
 "explanation":"Shift+Delete permanently deletes a file, bypassing the Recycle Bin. Pressing just Delete moves it to the Recycle Bin where it can be restored."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Memory Units",
 "questionText":"Arrange these storage units from SMALLEST to LARGEST: GB, KB, MB, TB",
 "options":["A: KB < MB < GB < TB","B: MB < KB < GB < TB","C: GB < MB < TB < KB","D: KB < GB < MB < TB"],"correctAnswer":"A",
 "explanation":"KB (Kilobyte) < MB (Megabyte) < GB (Gigabyte) < TB (Terabyte). Each is 1024 times larger than the previous. 1 KB = 1024 bytes, 1 MB = 1024 KB, 1 GB = 1024 MB, 1 TB = 1024 GB."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Spreadsheet",
 "questionText":"In MS Excel, the formula =A1+B1 in cell C1 means:",
 "options":["A: Multiply A1 and B1","B: Compare A1 and B1","C: Add the values in cells A1 and B1","D: Copy A1 to B1"],"correctAnswer":"C",
 "explanation":"The + operator in Excel formulas performs addition. =A1+B1 calculates the sum of whatever numbers are in cells A1 and B1."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Input Devices",
 "questionText":"A 'scanner' is used to:",
 "options":["A: Print documents on paper","B: Convert physical documents/images into digital format","C: Display images on screen","D: Store large amounts of data"],"correctAnswer":"B",
 "explanation":"A scanner converts physical documents, photos, or images into digital files that can be stored, edited, or shared on a computer."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Output Devices",
 "questionText":"Which type of printer uses heat to print on special thermal paper (commonly used in receipt printers)?",
 "options":["A: Inkjet printer","B: Laser printer","C: Thermal printer","D: Dot matrix printer"],"correctAnswer":"C",
 "explanation":"Thermal printers use heat to print on heat-sensitive paper. They are used in cash registers, ATM receipts, and shipping labels. They produce no ink or toner."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Networks",
 "questionText":"The internet is an example of which type of network?",
 "options":["A: LAN (Local Area Network)","B: MAN (Metropolitan Area Network)","C: WAN (Wide Area Network)","D: PAN (Personal Area Network)"],"correctAnswer":"C",
 "explanation":"The internet is a global WAN (Wide Area Network) — it connects millions of computers and networks across the entire world, spanning continents."},

{"subject":"Computer Science","grade":4,"difficulty":"Advanced","topic":"Computer Science","subTopic":"MS Paint",
 "questionText":"In MS Paint, which tool is used to fill a closed area with colour?",
 "options":["A: Pencil tool","B: Fill with colour (Paint Bucket) tool","C: Eraser tool","D: Text tool"],"correctAnswer":"B",
 "explanation":"The 'Fill with colour' tool (Paint Bucket) floods a closed area with the selected colour in one click. The pencil draws free-form lines."},

# ══════════════════════════════════════════════════════════════════════════════
# English G8 Olympiad top-up (+10, currently 31 → 41) — NCERT Honeydew/It So Happened
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Literature — Honeydew",
 "questionText":"In the poem 'The Last Bargain' (NCERT Honeydew, G8), the speaker accepts work from which person at the end?",
 "options":["A: A king with his gold","B: An old man with nothing","C: A young child with flowers","D: A merchant with silver"],"correctAnswer":"C",
 "explanation":"In Tagore's 'The Last Bargain', the speaker rejects the king (who offers power/gold) and the old man. He finally accepts work from a child who pays with flowers and a smile — representing the priceless payment of love and innocence."},

{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Grammar — Passive Voice",
 "questionText":"Change to passive voice: 'They are building a new highway through the forest.'",
 "options":["A: A new highway was built through the forest.","B: A new highway is being built through the forest.","C: A new highway will be built through the forest.","D: A new highway has been built through the forest."],"correctAnswer":"B",
 "explanation":"Present continuous active → passive: 'is/are being + past participle'. They are building → A new highway is being built."},

{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Vocabulary — Word Formation",
 "questionText":"The word 'inevitable' means something that:",
 "options":["A: Can be avoided with effort","B: Cannot be avoided; certain to happen","C: Is unexpected and surprising","D: Is unpleasant but temporary"],"correctAnswer":"B",
 "explanation":"'Inevitable' (in- = not, evitable = avoidable, from Latin 'evitare') means certain to happen and impossible to prevent or avoid."},

{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Grammar — Conditionals",
 "questionText":"Choose the correct sentence using the Second Conditional (hypothetical present/future):",
 "options":["A: If it rains tomorrow, we will cancel the trip.","B: If I were rich, I would travel the world.","C: If she had studied, she would have passed.","D: Unless you hurry, you will miss the train."],"correctAnswer":"B",
 "explanation":"Second conditional = If + past tense, would + infinitive. It expresses hypothetical/imaginary present/future situations. Option A is first conditional (real possibility); Option C is third conditional (past hypothetical)."},

{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Figure of Speech",
 "questionText":"'The classroom was a zoo.' This is an example of:",
 "options":["A: Simile","B: Metaphor","C: Personification","D: Alliteration"],"correctAnswer":"B",
 "explanation":"A metaphor directly states one thing IS another. 'Classroom was a zoo' — direct comparison without 'like' or 'as'. A simile would say 'like a zoo'."},

{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Grammar — Reported Speech",
 "questionText":"Change to reported speech: The teacher said, 'The Earth revolves around the Sun.'",
 "options":["A: The teacher said that the Earth revolved around the Sun.","B: The teacher said that the Earth revolves around the Sun.","C: The teacher told that the Earth revolves around the Sun.","D: The teacher said that the Earth had revolved around the Sun."],"correctAnswer":"B",
 "explanation":"Universal/scientific truths do NOT change tense in reported speech. 'The Earth revolves around the Sun' is a fact, so it stays in present tense: 'the Earth revolves'."},

{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Comprehension — Inference",
 "questionText":"'Despite her calm exterior, Maria's hands trembled slightly as she approached the stage.' What can you infer about Maria?",
 "options":["A: She was very confident and relaxed","B: She was nervous despite appearing calm","C: She was cold and shivering","D: She was excited and happy to perform"],"correctAnswer":"B",
 "explanation":"'Calm exterior' suggests she appeared composed, but 'hands trembled' reveals inner nervousness. This is an inference question — the answer is implied, not stated directly."},

{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Vocabulary — Idioms",
 "questionText":"'She passed the exam with flying colours' means she:",
 "options":["A: Barely passed the exam","B: Failed but was given another chance","C: Passed brilliantly and with distinction","D: Passed because the examiner was lenient"],"correctAnswer":"C",
 "explanation":"'With flying colours' means achieving outstanding success, doing something triumphantly and with distinction. Origin: from ships displaying their flags (colours) flying high after a victorious battle."},

{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Grammar — Clauses",
 "questionText":"Identify the type of subordinate clause in: 'She left before the movie ended.'",
 "options":["A: Noun clause","B: Relative (adjective) clause","C: Adverbial clause of time","D: Adverbial clause of condition"],"correctAnswer":"C",
 "explanation":"'before the movie ended' is an adverbial clause of time — it modifies the verb 'left' by telling us WHEN she left. 'Before' is a subordinating conjunction showing time."},

{"subject":"English","grade":8,"difficulty":"Olympiad","topic":"English","subTopic":"Grammar — Subject-Verb Agreement",
 "questionText":"Choose the correct form: 'A number of students __ absent today.'",
 "options":["A: is","B: are","C: was","D: has been"],"correctAnswer":"B",
 "explanation":"'A number of' means 'many/several' and takes a plural verb (are). Contrast with 'The number of students is increasing' — 'The number' is the subject (singular). Memory tip: 'A number of = are' vs 'The number of = is'."},

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
