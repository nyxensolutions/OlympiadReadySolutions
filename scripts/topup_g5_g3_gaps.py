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

# ─── LR G5 Olympiad (15 questions) ───────────────────────────────────────────
{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Number Series",
 "questionText":"Find the next term: 2, 6, 12, 20, 30, 42, __",
 "options":["A: 54","B: 56","C: 52","D: 58"],"correctAnswer":"B",
 "explanation":"Differences are 4,6,8,10,12,14. So 42+14=56."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Alphabet Series",
 "questionText":"In the sequence A, C, F, J, O, __ what letter comes next?",
 "options":["A: T","B: U","C: V","D: W"],"correctAnswer":"B",
 "explanation":"Gaps: +2,+3,+4,+5,+6. O is 15th letter; 15+6=21 = U."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Coding-Decoding",
 "questionText":"If FRIEND is coded as HUMJTK, how is CANDLE coded?",
 "options":["A: ECOFLG","B: ECPFNG","C: DCPFNG","D: ECOFNG"],"correctAnswer":"B",
 "explanation":"Each letter is shifted by +2,+3,+2,+3,... alternating. C+2=E, A+2=C, N+2=P, D+2=F, L+2=N, E+2=G → ECPFNG."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Blood Relations",
 "questionText":"Pointing to a photograph, Riya says, 'He is the only son of my father's father.' How is the man in the photograph related to Riya?",
 "options":["A: Uncle","B: Father","C: Brother","D: Grandfather"],"correctAnswer":"B",
 "explanation":"Father's father = grandfather. Grandfather's only son = Riya's father."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Direction Sense",
 "questionText":"Akash walks 5 km North, turns right and walks 3 km, turns right again and walks 5 km. How far is he from the starting point and in which direction?",
 "options":["A: 3 km West","B: 3 km East","C: 8 km South","D: 5 km North"],"correctAnswer":"B",
 "explanation":"He ends up 3 km East of start (the southward 5 km cancels the northward 5 km; net displacement = 3 km East)."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Mirror Images",
 "questionText":"A clock shows 3:25. What time will its mirror image show?",
 "options":["A: 8:35","B: 9:35","C: 8:25","D: 9:25"],"correctAnswer":"A",
 "explanation":"Mirror image time = 11:60 minus original time (for clocks with no seconds). 11:60 - 3:25 = 8:35."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Analogy",
 "questionText":"Painter : Canvas :: Sculptor : ?",
 "options":["A: Chisel","B: Clay","C: Brush","D: Paint"],"correctAnswer":"B",
 "explanation":"A painter works on a canvas; a sculptor works on clay (the medium/material)."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Classification",
 "questionText":"Find the odd one out: Crow, Parrot, Eagle, Bat, Pigeon",
 "options":["A: Crow","B: Parrot","C: Bat","D: Eagle"],"correctAnswer":"C",
 "explanation":"All others are birds (ave). Bat is a mammal that flies."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Seating Arrangement",
 "questionText":"Five friends A, B, C, D, E sit in a row facing North. B sits to the immediate right of A. D sits to the immediate left of E. C sits between B and D. Who sits at the extreme right end?",
 "options":["A: D","B: E","C: C","D: A"],"correctAnswer":"B",
 "explanation":"Order: A-B-C-D-E. E sits at the extreme right end."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Mathematical Puzzles",
 "questionText":"A number when divided by 3 gives a remainder of 2, and when divided by 5 gives a remainder of 3. What is the smallest such positive number?",
 "options":["A: 8","B: 13","C: 23","D: 17"],"correctAnswer":"A",
 "explanation":"Numbers leaving remainder 2 with 3: 2,5,8,11,14... Numbers leaving remainder 3 with 5: 3,8,13... Smallest common = 8."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Pattern Recognition",
 "questionText":"In a pattern: 1, 1, 2, 3, 5, 8, 13, __ — what comes next?",
 "options":["A: 18","B: 20","C: 21","D: 24"],"correctAnswer":"C",
 "explanation":"Fibonacci sequence: each term = sum of previous two. 8+13=21."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Matrix",
 "questionText":"In a 3×3 matrix each row sums to 15 (magic square). The first row is 2,7,6 and the second row is 9,5,1. What is the middle element of the third row?",
 "options":["A: 8","B: 3","C: 6","D: 7"],"correctAnswer":"B",
 "explanation":"Third row must be 4,3,8 (classic 3×3 magic square). Middle element = 3."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Logical Venn Diagrams",
 "questionText":"All teachers are graduates. Some graduates are doctors. Which conclusion is definitely true?",
 "options":["A: All teachers are doctors","B: Some doctors are teachers","C: All graduates are teachers","D: All teachers are graduates"],"correctAnswer":"D",
 "explanation":"The first statement directly tells us all teachers are graduates — this is a definite conclusion."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Calendar Problems",
 "questionText":"If 1 January 2023 was a Sunday, what day was 1 January 2024?",
 "options":["A: Sunday","B: Monday","C: Tuesday","D: Wednesday"],"correctAnswer":"B",
 "explanation":"2023 is not a leap year (365 days = 52 weeks + 1 day). So 1 Jan 2024 is Sunday + 1 = Monday."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Olympiad","topic":"Logical Reasoning","subTopic":"Cubes and Dice",
 "questionText":"A cube is painted red on all faces and then cut into 27 equal smaller cubes. How many small cubes have exactly 2 faces painted?",
 "options":["A: 12","B: 8","C: 6","D: 1"],"correctAnswer":"A",
 "explanation":"Edge cubes (not corners) have 2 painted faces. A 3×3×3 cube has 12 edge positions."},

# ─── Maths G5 Olympiad (15 questions) ────────────────────────────────────────
{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Number System",
 "questionText":"What is the smallest 6-digit number divisible by both 4 and 9?",
 "options":["A: 100008","B: 100044","C: 100008","D: 100080"],"correctAnswer":"A",
 "explanation":"Smallest 6-digit number = 100000. LCM(4,9)=36. 100000÷36=2777.7… → 2778×36=100008."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Fractions and Decimals",
 "questionText":"What is 3/4 ÷ 1/8 + 1/2 × 4?",
 "options":["A: 8","B: 6","C: 7","D: 8.5"],"correctAnswer":"A",
 "explanation":"3/4 ÷ 1/8 = 3/4 × 8 = 6. 1/2 × 4 = 2. 6+2=8."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Percentages",
 "questionText":"A shirt originally costs Rs 800. After a 20% discount and then a 10% GST on the discounted price, what is the final price?",
 "options":["A: Rs 704","B: Rs 720","C: Rs 696","D: Rs 752"],"correctAnswer":"A",
 "explanation":"800 × 0.8 = Rs 640. 640 × 1.1 = Rs 704."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Average",
 "questionText":"The average of 5 numbers is 24. If one number is removed, the average of remaining 4 numbers becomes 21. What is the removed number?",
 "options":["A: 36","B: 32","C: 28","D: 40"],"correctAnswer":"A",
 "explanation":"Sum of 5 numbers = 5×24=120. Sum of 4 numbers = 4×21=84. Removed number = 120-84=36."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"LCM and HCF",
 "questionText":"The HCF of two numbers is 12 and their LCM is 180. If one number is 36, what is the other number?",
 "options":["A: 60","B: 48","C: 72","D: 54"],"correctAnswer":"A",
 "explanation":"Product of numbers = HCF × LCM = 12×180=2160. Other number = 2160÷36=60."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Ratio and Proportion",
 "questionText":"A and B share money in the ratio 3:5. If B gets Rs 120 more than A, how much does A get?",
 "options":["A: Rs 180","B: Rs 120","C: Rs 240","D: Rs 150"],"correctAnswer":"A",
 "explanation":"Difference in ratio = 5-3=2 parts = Rs 120. One part = Rs 60. A gets 3×60=Rs 180."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Geometry — Triangles",
 "questionText":"In a right-angled triangle, one angle is 35°. What is the third angle?",
 "options":["A: 55°","B: 45°","C: 65°","D: 75°"],"correctAnswer":"A",
 "explanation":"Sum of angles in a triangle = 180°. 90°+35°+x=180°. x=55°."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Area and Perimeter",
 "questionText":"A rectangular garden 24 m long and 16 m wide is surrounded by a path 2 m wide. What is the area of the path?",
 "options":["A: 192 sq m","B: 176 sq m","C: 200 sq m","D: 160 sq m"],"correctAnswer":"B",
 "explanation":"Outer rectangle: (24+4)×(16+4)=28×20=560. Inner rectangle: 24×16=384. Path area=560-384=176 sq m."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Profit and Loss",
 "questionText":"A shopkeeper buys 12 pens for Rs 60 and sells 10 pens for Rs 60. What is his profit or loss percentage?",
 "options":["A: 20% profit","B: 20% loss","C: 25% profit","D: 25% loss"],"correctAnswer":"A",
 "explanation":"CP per pen=5. SP per pen=6. Profit per pen=1. Profit%=(1/5)×100=20%."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Speed, Distance, Time",
 "questionText":"A train 120 m long passes a pole in 6 seconds. How long will it take to pass a 180 m long platform?",
 "options":["A: 15 seconds","B: 12 seconds","C: 9 seconds","D: 18 seconds"],"correctAnswer":"A",
 "explanation":"Speed = 120/6 = 20 m/s. Distance to cross platform = 120+180=300 m. Time = 300/20 = 15 s."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Number Patterns",
 "questionText":"What is the sum of the first 10 odd numbers?",
 "options":["A: 100","B: 90","C: 110","D: 55"],"correctAnswer":"A",
 "explanation":"Sum of first n odd numbers = n². Sum of first 10 odd numbers = 10² = 100."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Volume and Surface Area",
 "questionText":"A cube has a volume of 125 cubic cm. What is its total surface area?",
 "options":["A: 150 sq cm","B: 100 sq cm","C: 125 sq cm","D: 175 sq cm"],"correctAnswer":"A",
 "explanation":"Side = ∛125 = 5 cm. Surface area = 6×5² = 6×25 = 150 sq cm."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Data Handling",
 "questionText":"The median of 5 values 8, 12, 5, 17, 10 is:",
 "options":["A: 10","B: 12","C: 8","D: 11"],"correctAnswer":"A",
 "explanation":"Arrange in order: 5,8,10,12,17. Middle value (3rd) = 10."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Algebra — Basics",
 "questionText":"If 3x + 7 = 28, what is 5x − 3?",
 "options":["A: 32","B: 30","C: 28","D: 35"],"correctAnswer":"A",
 "explanation":"3x=21, x=7. 5×7-3=35-3=32."},

{"subject":"Mathematics","grade":5,"difficulty":"Olympiad","topic":"Mathematics","subTopic":"Unitary Method",
 "questionText":"8 workers can complete a task in 15 days. How many days will 12 workers take to complete the same task?",
 "options":["A: 10 days","B: 12 days","C: 8 days","D: 9 days"],"correctAnswer":"A",
 "explanation":"8×15=120 worker-days. 120÷12=10 days."},

# ─── Hindi G3 Olympiad (15 questions) ────────────────────────────────────────
{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Sangya",
 "questionText":"'मिठास' किस प्रकार की संज्ञा है?",
 "options":["A: व्यक्तिवाचक","B: जातिवाचक","C: भाववाचक","D: द्रव्यवाचक"],"correctAnswer":"C",
 "explanation":"'मिठास' एक गुण/भाव का नाम है, अतः यह भाववाचक संज्ञा है।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Vilom Shabd",
 "questionText":"'आदर' का विलोम शब्द क्या है?",
 "options":["A: सम्मान","B: अनादर","C: निरादर","D: अपमान"],"correctAnswer":"C",
 "explanation":"'आदर' का विलोम 'निरादर' है (उपसर्ग 'नि' जोड़ने से)।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Paryayvachi Shabd",
 "questionText":"'नेत्र' का पर्यायवाची शब्द कौन-सा है?",
 "options":["A: हाथ","B: लोचन","C: कर्ण","D: मुख"],"correctAnswer":"B",
 "explanation":"'नेत्र' यानी आँख — इसके पर्यायवाची हैं: लोचन, नयन, चक्षु।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Muhavare",
 "questionText":"'आँखों का तारा' मुहावरे का सही अर्थ क्या है?",
 "options":["A: आँखों में दर्द","B: बहुत प्रिय होना","C: दूर से देखना","D: सितारे देखना"],"correctAnswer":"B",
 "explanation":"'आँखों का तारा' का अर्थ है — बहुत प्रिय या लाडला होना।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Ling",
 "questionText":"'विद्यार्थी' का स्त्रीलिंग क्या है?",
 "options":["A: विद्यार्थिनी","B: विद्यार्थिन","C: विद्यार्थी","D: विद्यार्थिनि"],"correctAnswer":"A",
 "explanation":"'विद्यार्थी' का स्त्रीलिंग 'विद्यार्थिनी' होता है।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Vachan",
 "questionText":"'कमरा' का बहुवचन क्या है?",
 "options":["A: कमरे","B: कमरों","C: कमराएँ","D: कमरियाँ"],"correctAnswer":"A",
 "explanation":"'कमरा' का बहुवचन 'कमरे' होता है।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Karak",
 "questionText":"'राहुल ने सेब खाया।' इस वाक्य में 'राहुल ने' में कौन-सा कारक है?",
 "options":["A: कर्म कारक","B: कर्ता कारक","C: करण कारक","D: अधिकरण कारक"],"correctAnswer":"B",
 "explanation":"'ने' विभक्ति कर्ता कारक की परसर्ग है।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Kaal",
 "questionText":"'वह कल दिल्ली जाएगा।' यह वाक्य किस काल में है?",
 "options":["A: भूतकाल","B: वर्तमानकाल","C: भविष्यकाल","D: सामान्य काल"],"correctAnswer":"C",
 "explanation":"'जाएगा' क्रिया आने वाले समय की बात करती है, इसलिए यह भविष्यकाल है।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Alankar",
 "questionText":"'चाँदी जैसी चाँदनी चमक रही है।' इस वाक्य में कौन-सा अलंकार है?",
 "options":["A: उपमा","B: रूपक","C: अनुप्रास","D: यमक"],"correctAnswer":"A",
 "explanation":"'चाँदनी' की तुलना 'चाँदी' से की गई है, इसलिए यह उपमा अलंकार है।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Upsarg",
 "questionText":"'अ' उपसर्ग से बना शब्द कौन-सा है?",
 "options":["A: अनार","B: असफल","C: अटल","D: अखबार"],"correctAnswer":"B",
 "explanation":"'असफल' = 'अ' (उपसर्ग) + 'सफल' — जिसका अर्थ है जो सफल न हो।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Swar and Vyanjan",
 "questionText":"'ऐ' और 'औ' किस प्रकार के स्वर हैं?",
 "options":["A: ह्रस्व स्वर","B: दीर्घ स्वर","C: संयुक्त स्वर","D: अनुनासिक स्वर"],"correctAnswer":"B",
 "explanation":"'ऐ' और 'औ' दीर्घ स्वर हैं।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Sandhi",
 "questionText":"'देव + आलय' को जोड़ने पर क्या बनेगा?",
 "options":["A: देवालय","B: देवाआलय","C: देवलय","D: देव-आलय"],"correctAnswer":"A",
 "explanation":"अ + आ = आ (दीर्घ स्वर संधि)। 'देव' के अंत में 'अ' और 'आलय' के आरंभ में 'आ' मिलकर 'आ' बनाते हैं → देवालय।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Kriya",
 "questionText":"'बच्चे खेलते हैं।' इस वाक्य में क्रिया कौन-सी है?",
 "options":["A: बच्चे","B: खेलते","C: हैं","D: खेलते हैं"],"correctAnswer":"D",
 "explanation":"'खेलते हैं' पूरी क्रिया (verb phrase) है — 'खेलते' मुख्य क्रिया और 'हैं' सहायक क्रिया।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Visheshan",
 "questionText":"'थोड़ा पानी पी लो।' वाक्य में विशेषण कौन-सा है?",
 "options":["A: पानी","B: पी","C: थोड़ा","D: लो"],"correctAnswer":"C",
 "explanation":"'थोड़ा' विशेषण है जो 'पानी' की मात्रा बताता है — यह परिमाणवाचक विशेषण है।"},

{"subject":"Hindi","grade":3,"difficulty":"Olympiad","topic":"Hindi","subTopic":"Kavita Bodh",
 "questionText":"किस कवि ने 'झाँसी की रानी' नामक प्रसिद्ध कविता लिखी?",
 "options":["A: मैथिलीशरण गुप्त","B: सुभद्राकुमारी चौहान","C: सूर्यकांत त्रिपाठी 'निराला'","D: जयशंकर प्रसाद"],"correctAnswer":"B",
 "explanation":"'बुंदेले हरबोलों के मुँह हमने सुनी कहानी थी, खूब लड़ी मर्दानी वह तो झाँसी वाली रानी थी।' — सुभद्राकुमारी चौहान।"},

# ─── GK G9 Foundation (15 questions) ─────────────────────────────────────────
{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Science and Technology",
 "questionText":"Which planet in our solar system has the most moons?",
 "options":["A: Jupiter","B: Saturn","C: Uranus","D: Neptune"],"correctAnswer":"B",
 "explanation":"As of recent counts, Saturn has the most confirmed moons (95+), surpassing Jupiter."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Indian History",
 "questionText":"The Quit India Movement was launched in which year?",
 "options":["A: 1942","B: 1930","C: 1947","D: 1920"],"correctAnswer":"A",
 "explanation":"The Quit India Movement (Bharat Chhodo Andolan) was launched by Mahatma Gandhi on 8 August 1942."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Indian Constitution",
 "questionText":"How many Fundamental Rights are guaranteed by the Indian Constitution?",
 "options":["A: 6","B: 7","C: 9","D: 11"],"correctAnswer":"A",
 "explanation":"The Indian Constitution guarantees 6 Fundamental Rights (originally 7; Right to Property was removed in 1978)."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Geography",
 "questionText":"Which is the highest plateau in the world?",
 "options":["A: Deccan Plateau","B: Tibetan Plateau","C: Colorado Plateau","D: Patagonian Plateau"],"correctAnswer":"B",
 "explanation":"The Tibetan Plateau, often called the 'Roof of the World', is the world's highest plateau with an average elevation over 4,500 m."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Current Affairs",
 "questionText":"Which organisation publishes the Human Development Index (HDI) annually?",
 "options":["A: World Bank","B: WHO","C: UNDP","D: IMF"],"correctAnswer":"C",
 "explanation":"The Human Development Index is published annually by the United Nations Development Programme (UNDP)."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Sports",
 "questionText":"The Davis Cup is associated with which sport?",
 "options":["A: Cricket","B: Badminton","C: Tennis","D: Football"],"correctAnswer":"C",
 "explanation":"The Davis Cup is the premier international team event in men's tennis."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Literature",
 "questionText":"Who wrote the novel 'The Guide'?",
 "options":["A: Mulk Raj Anand","B: R.K. Narayan","C: Arundhati Roy","D: Vikram Seth"],"correctAnswer":"B",
 "explanation":"'The Guide' (1958) by R.K. Narayan won the Sahitya Akademi Award and was later adapted into a Bollywood film."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Science and Technology",
 "questionText":"What does the abbreviation 'DNA' stand for?",
 "options":["A: Deoxyribonucleic Acid","B: Di-Nitro Acid","C: Dynamic Nucleic Acid","D: Dual Nitrogen Acid"],"correctAnswer":"A",
 "explanation":"DNA stands for Deoxyribonucleic Acid — the molecule carrying genetic information."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Indian Economy",
 "questionText":"The 'Green Revolution' in India is primarily associated with which crop?",
 "options":["A: Rice only","B: Wheat and Rice","C: Cotton","D: Sugarcane"],"correctAnswer":"B",
 "explanation":"The Green Revolution (1960s-70s) primarily boosted production of wheat (especially) and rice through high-yielding varieties."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"World Geography",
 "questionText":"Which country is known as the 'Land of the Rising Sun'?",
 "options":["A: China","B: South Korea","C: Japan","D: Thailand"],"correctAnswer":"C",
 "explanation":"Japan is known as the 'Land of the Rising Sun' — its name 'Nihon' means 'sun origin'."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Awards and Prizes",
 "questionText":"Who was the first Indian to win the Nobel Prize?",
 "options":["A: C.V. Raman","B: Rabindranath Tagore","C: Mother Teresa","D: Amartya Sen"],"correctAnswer":"B",
 "explanation":"Rabindranath Tagore won the Nobel Prize in Literature in 1913, becoming the first Asian and first Indian Nobel laureate."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Biology",
 "questionText":"Which blood group is known as the 'Universal Donor'?",
 "options":["A: AB+","B: O-","C: A+","D: B-"],"correctAnswer":"B",
 "explanation":"O- (O negative) is the universal donor blood group because it can be given to patients of any blood group in emergencies."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Indian Culture",
 "questionText":"Bharatanatyam is a classical dance form originating from which state?",
 "options":["A: Kerala","B: Andhra Pradesh","C: Tamil Nadu","D: Karnataka"],"correctAnswer":"C",
 "explanation":"Bharatanatyam is one of the oldest classical dance forms of India and originated in Tamil Nadu."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Space Science",
 "questionText":"India's first satellite, Aryabhata, was launched in which year?",
 "options":["A: 1969","B: 1975","C: 1980","D: 1984"],"correctAnswer":"B",
 "explanation":"Aryabhata, India's first satellite, was launched on 19 April 1975 with the help of the Soviet Union."},

{"subject":"General Knowledge","grade":9,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Environment",
 "questionText":"The 'Chipko Movement' was associated with protecting which natural resource?",
 "options":["A: Water bodies","B: Wildlife","C: Forests/Trees","D: Soil"],"correctAnswer":"C",
 "explanation":"The Chipko Movement (1973, Uttarakhand) was a forest conservation movement where villagers hugged trees to prevent felling."},

# ─── English G6 Foundation (15 questions) ────────────────────────────────────
{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Parts of Speech",
 "questionText":"Identify the noun in: 'The clever fox ran across the field.'",
 "options":["A: clever","B: ran","C: fox","D: across"],"correctAnswer":"C",
 "explanation":"'Fox' is a noun (name of an animal). 'Clever' is an adjective, 'ran' is a verb, 'across' is a preposition."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Tenses",
 "questionText":"Choose the correct verb form: 'She __ to school every day.'",
 "options":["A: go","B: goes","C: going","D: went"],"correctAnswer":"B",
 "explanation":"Third person singular (she) uses 'goes' in simple present tense."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Articles",
 "questionText":"Fill in the blank: '__ elephant is the largest land animal.'",
 "options":["A: A","B: An","C: The","D: No article needed"],"correctAnswer":"C",
 "explanation":"'The' is used here because we are talking about elephants as a species in general (generic use of 'the')."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Synonyms and Antonyms",
 "questionText":"What is the antonym of 'ancient'?",
 "options":["A: Old","B: Modern","C: Large","D: Historical"],"correctAnswer":"B",
 "explanation":"'Ancient' means very old. Its antonym (opposite) is 'modern'."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Comprehension",
 "questionText":"Read: 'Neha was excited because her school was going on a trip to the science museum tomorrow.' Why was Neha excited?",
 "options":["A: She got a new book","B: She was going on a school trip","C: She won an award","D: She met a new friend"],"correctAnswer":"B",
 "explanation":"The passage directly states she was excited about the school trip to the science museum."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Prepositions",
 "questionText":"Choose the correct preposition: 'The cat sat __ the mat.'",
 "options":["A: at","B: in","C: on","D: by"],"correctAnswer":"C",
 "explanation":"'On' is the correct preposition for a surface — the cat sat on the mat."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Active and Passive Voice",
 "questionText":"Convert to passive voice: 'The teacher praised the student.'",
 "options":["A: The student is praised by the teacher.","B: The student was praised by the teacher.","C: The teacher was praised by the student.","D: The student praised by the teacher."],"correctAnswer":"B",
 "explanation":"Simple past active → 'was/were + past participle' in passive. Subject becomes object and vice versa."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Punctuation",
 "questionText":"Which sentence uses punctuation correctly?",
 "options":["A: Where are you going","B: Where are you going?","C: where are you going?","D: Where are you going!"],"correctAnswer":"B",
 "explanation":"A question must begin with a capital letter and end with a question mark."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Figures of Speech",
 "questionText":"'The wind whispered through the trees.' This sentence uses which figure of speech?",
 "options":["A: Simile","B: Metaphor","C: Personification","D: Hyperbole"],"correctAnswer":"C",
 "explanation":"Personification gives human qualities (whispering) to non-human things (wind)."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Sentence Types",
 "questionText":"What type of sentence is: 'Please close the door.'",
 "options":["A: Interrogative","B: Declarative","C: Imperative","D: Exclamatory"],"correctAnswer":"C",
 "explanation":"An imperative sentence gives a command or makes a request."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Pronouns",
 "questionText":"Choose the correct pronoun: 'Each of the students must bring __ own pencil.'",
 "options":["A: their","B: his or her","C: its","D: our"],"correctAnswer":"B",
 "explanation":"'Each' is singular, so 'his or her' is grammatically correct in formal usage (though 'their' is increasingly accepted informally)."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Vocabulary",
 "questionText":"What does the word 'immense' mean?",
 "options":["A: Very small","B: Very large","C: Very fast","D: Very dark"],"correctAnswer":"B",
 "explanation":"'Immense' means extremely large or great in size or degree."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Conjunctions",
 "questionText":"Choose the correct conjunction: 'I wanted to play outside __ it was raining.'",
 "options":["A: and","B: so","C: but","D: or"],"correctAnswer":"C",
 "explanation":"'But' shows contrast between two opposing ideas."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Direct and Indirect Speech",
 "questionText":"Convert to indirect speech: She said, 'I am tired.'",
 "options":["A: She said that she is tired.","B: She said that she was tired.","C: She says that she is tired.","D: She said that I was tired."],"correctAnswer":"B",
 "explanation":"In reported speech, present tense 'am' shifts to past tense 'was'."},

{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Adjectives",
 "questionText":"Which sentence uses the superlative degree correctly?",
 "options":["A: Mount Everest is more tall than any other peak.","B: Mount Everest is most tall peak in the world.","C: Mount Everest is the tallest peak in the world.","D: Mount Everest is taller the world's peak."],"correctAnswer":"C",
 "explanation":"Superlative of 'tall' is 'tallest', used with 'the' when comparing with all others."},

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
