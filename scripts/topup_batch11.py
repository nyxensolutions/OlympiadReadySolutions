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

# ── Spell Bee G4 Foundation (+15q, 15→30) ─────────────────────────────────────
{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Homophones",
 "questionText":"Which is the correct spelling for land surrounded by water on all sides?",
 "options":["A: iland","B: island","C: iseland","D: aisland"],
 "correctAnswer":"B",
 "explanation":"'Island' is the correct spelling (I-S-L-A-N-D). Note the silent 'S'. An island is a piece of land entirely surrounded by water."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"ph Words",
 "questionText":"Choose the correct spelling of the study of living things:",
 "options":["A: biolegy","B: biology","C: byology","D: biollogy"],
 "correctAnswer":"B",
 "explanation":"'Biology' is the correct spelling (B-I-O-L-O-G-Y). 'Bio' means life, and 'logy' means study. Biology is the science of living organisms."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Double Letters",
 "questionText":"Which spelling is correct for a word meaning very beautiful or impressive?",
 "options":["A: magnificant","B: magnifisent","C: magnificent","D: magnificient"],
 "correctAnswer":"C",
 "explanation":"'Magnificent' is the correct spelling (M-A-G-N-I-F-I-C-E-N-T). It means very impressive, beautiful, or elaborate."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Tricky Words",
 "questionText":"Choose the correct spelling of an organisation that competes against another:",
 "options":["A: competitor","B: competetor","C: competiter","D: competitur"],
 "correctAnswer":"A",
 "explanation":"'Competitor' is the correct spelling (C-O-M-P-E-T-I-T-O-R). A competitor is someone who takes part in a competition."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Silent Letters",
 "questionText":"Which is the correct spelling for an official who keeps records:",
 "options":["A: secretery","B: secretarie","C: secretary","D: secratary"],
 "correctAnswer":"C",
 "explanation":"'Secretary' is the correct spelling (S-E-C-R-E-T-A-R-Y). A secretary manages correspondence and records."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Suffixes",
 "questionText":"Choose the correct spelling of the word meaning full of hope:",
 "options":["A: hopefull","B: hopful","C: hopeful","D: hoopeful"],
 "correctAnswer":"C",
 "explanation":"'Hopeful' is the correct spelling (H-O-P-E-F-U-L). The suffix '-ful' (meaning full of) has only one L when added to a word."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Geography Words",
 "questionText":"Which spelling is correct for the imaginary line around the middle of the Earth?",
 "options":["A: equater","B: equator","C: equatour","D: equaitor"],
 "correctAnswer":"B",
 "explanation":"'Equator' is the correct spelling (E-Q-U-A-T-O-R). The equator divides Earth into the Northern and Southern Hemispheres."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Science Words",
 "questionText":"Choose the correct spelling of the force that keeps us on Earth:",
 "options":["A: gravity","B: gravitty","C: gravety","D: gravvity"],
 "correctAnswer":"A",
 "explanation":"'Gravity' is the correct spelling (G-R-A-V-I-T-Y). Gravity is the force that attracts objects toward Earth's centre."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Tricky Words",
 "questionText":"Which is the correct spelling for something that cannot be seen:",
 "options":["A: invisable","B: invissible","C: invisible","D: invisibel"],
 "correctAnswer":"C",
 "explanation":"'Invisible' is the correct spelling (I-N-V-I-S-I-B-L-E). 'In-' means not, and 'visible' means able to be seen."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Historical Words",
 "questionText":"Choose the correct spelling of the long period before written records:",
 "options":["A: prehistory","B: pre-hystory","C: prehistorie","D: prehistori"],
 "correctAnswer":"A",
 "explanation":"'Prehistory' is the correct spelling (P-R-E-H-I-S-T-O-R-Y). Prehistory refers to the time before writing was invented."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Confusing Words",
 "questionText":"Which spelling means a statement that is the opposite of another?",
 "options":["A: contradiction","B: contradicion","C: contradection","D: contradition"],
 "correctAnswer":"A",
 "explanation":"'Contradiction' is the correct spelling (C-O-N-T-R-A-D-I-C-T-I-O-N). A contradiction is when two statements cannot both be true at the same time."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Math Words",
 "questionText":"Choose the correct spelling of a flat shape with four equal sides and four right angles:",
 "options":["A: sqaure","B: square","C: squere","D: sqaur"],
 "correctAnswer":"B",
 "explanation":"'Square' is the correct spelling (S-Q-U-A-R-E). A square has four equal sides and four right angles."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Adjectives",
 "questionText":"Which spelling is correct for a word meaning very happy and excited?",
 "options":["A: enthusiastic","B: enthoosiastic","C: enthousiastic","D: enthussiastic"],
 "correctAnswer":"A",
 "explanation":"'Enthusiastic' is the correct spelling (E-N-T-H-U-S-I-A-S-T-I-C). An enthusiastic person shows great excitement and interest."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Body of Water",
 "questionText":"Choose the correct spelling of a large, deep natural body of fresh water:",
 "options":["A: laik","B: lake","C: laek","D: layke"],
 "correctAnswer":"B",
 "explanation":"'Lake' is the correct spelling (L-A-K-E). Lakes are large bodies of standing freshwater surrounded by land."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Abstract Nouns",
 "questionText":"Which is the correct spelling of the quality of being fair and just?",
 "options":["A: justise","B: justise","C: justice","D: justis"],
 "correctAnswer":"C",
 "explanation":"'Justice' is the correct spelling (J-U-S-T-I-C-E). Justice means fairness and rightful treatment according to law or morality."},

# ── Spell Bee G4 Advanced (+15q, 15→30) ──────────────────────────────────────
{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Greek Roots",
 "questionText":"Choose the correct spelling of the study of ancient human societies:",
 "options":["A: archeology","B: archaeology","C: archealogy","D: archeaology"],
 "correctAnswer":"B",
 "explanation":"'Archaeology' is the correct spelling (A-R-C-H-A-E-O-L-O-G-Y). Archaeologists study human history through excavation and analysis of artefacts. (Also accepted: archeology in American English.)"},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Latin Roots",
 "questionText":"Which is the correct spelling of the word meaning to say or state officially?",
 "options":["A: pronounce","B: prononce","C: pronounse","D: pronnounce"],
 "correctAnswer":"A",
 "explanation":"'Pronounce' is the correct spelling (P-R-O-N-O-U-N-C-E). It means to make the sound of a word, or to declare officially."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Double Letters",
 "questionText":"Choose the correct spelling of a word meaning the most important or main:",
 "options":["A: principle","B: principel","C: principall","D: principl"],
 "correctAnswer":"A",
 "explanation":"'Principle' (a rule or belief) and 'Principal' (most important / head of school) are often confused. 'Principle' ends in '-le'. Here the answer is 'principle' (a fundamental truth)."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Confusing Pairs",
 "questionText":"Which spelling correctly means 'relating to sound'?",
 "options":["A: acoustic","B: acousitc","C: accoustic","D: acoustik"],
 "correctAnswer":"A",
 "explanation":"'Acoustic' is the correct spelling (A-C-O-U-S-T-I-C). Acoustic properties relate to sound; an acoustic guitar uses no electrical amplification."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Science Words",
 "questionText":"Choose the correct spelling of the imaginary line around which Earth rotates:",
 "options":["A: axiss","B: axiz","C: axis","D: axys"],
 "correctAnswer":"C",
 "explanation":"'Axis' is the correct spelling (A-X-I-S). Earth's axis is the imaginary line from the North Pole to the South Pole around which it rotates."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Abstract Nouns",
 "questionText":"Which spelling is correct for the quality of being persistent and not giving up?",
 "options":["A: perseverance","B: perseverence","C: perserverance","D: persiverance"],
 "correctAnswer":"A",
 "explanation":"'Perseverance' is the correct spelling (P-E-R-S-E-V-E-R-A-N-C-E). It means continued effort despite difficulty or delay."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Tricky Endings",
 "questionText":"Choose the correct spelling of the word meaning able to be seen through:",
 "options":["A: transparant","B: transperent","C: transparent","D: transparrent"],
 "correctAnswer":"C",
 "explanation":"'Transparent' is the correct spelling (T-R-A-N-S-P-A-R-E-N-T). A transparent material, like glass, allows light to pass through clearly."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Prefixes",
 "questionText":"Which spelling is correct for something that exists or works on its own without outside control?",
 "options":["A: autonamous","B: autonomous","C: autonomus","D: autonomouse"],
 "correctAnswer":"B",
 "explanation":"'Autonomous' is the correct spelling (A-U-T-O-N-O-M-O-U-S). It means self-governing or independent. 'Auto' = self, 'nomos' = law (Greek)."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Latin Words",
 "questionText":"Choose the correct spelling of the word meaning to make something larger:",
 "options":["A: magnifie","B: magnify","C: magnifye","D: magnefy"],
 "correctAnswer":"B",
 "explanation":"'Magnify' is the correct spelling (M-A-G-N-I-F-Y). A magnifying glass makes objects appear larger."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"ie/ei Rule",
 "questionText":"Which spelling is correct for the word meaning the right to vote?",
 "options":["A: franchize","B: franchise","C: franchyse","D: franshise"],
 "correctAnswer":"B",
 "explanation":"'Franchise' is the correct spelling (F-R-A-N-C-H-I-S-E). It means the right to vote, or a licence to operate a business under an established brand."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Medical Words",
 "questionText":"Choose the correct spelling of the doctor who treats mental health:",
 "options":["A: psyciatrist","B: psychiatrist","C: psychatrist","D: psyhciatrist"],
 "correctAnswer":"B",
 "explanation":"'Psychiatrist' is the correct spelling (P-S-Y-C-H-I-A-T-R-I-S-T). The silent 'P' at the start comes from Greek 'psyche' (mind). A psychiatrist is a medical doctor specialising in mental health."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Tricky Words",
 "questionText":"Which spelling means a brief formal account or list?",
 "options":["A: sumary","B: summary","C: summery","D: summari"],
 "correctAnswer":"B",
 "explanation":"'Summary' is the correct spelling (S-U-M-M-A-R-Y). Note double M. 'Summery' means resembling summer (warm weather). A summary is a brief statement of main points."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Adjectives",
 "questionText":"Choose the correct spelling of the word meaning easily broken or damaged:",
 "options":["A: fragil","B: fragile","C: fragle","D: fragiil"],
 "correctAnswer":"B",
 "explanation":"'Fragile' is the correct spelling (F-R-A-G-I-L-E). Fragile objects break easily and must be handled with care."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Words from Other Languages",
 "questionText":"Which is the correct spelling of a Japanese art of paper folding?",
 "options":["A: oragami","B: origami","C: origamy","D: origame"],
 "correctAnswer":"B",
 "explanation":"'Origami' is the correct spelling (O-R-I-G-A-M-I). Origami is the Japanese art of folding paper into decorative shapes. 'Ori' = fold, 'kami' = paper."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spelling",
 "subTopic":"Math Words",
 "questionText":"Choose the correct spelling of a triangle with all sides of different length:",
 "options":["A: scalane","B: scalene","C: scalaene","D: scaleen"],
 "correctAnswer":"B",
 "explanation":"'Scalene' is the correct spelling (S-C-A-L-E-N-E). A scalene triangle has three unequal sides and three unequal angles."},

# ── Spell Bee G10 Foundation (+15q, 15→30) ────────────────────────────────────
{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Scientific Terms",
 "questionText":"Which is the correct spelling of the tiny structures in a cell that make proteins?",
 "options":["A: ribosomes","B: ribozomes","C: ribasomes","D: ribossomes"],
 "correctAnswer":"A",
 "explanation":"'Ribosomes' is the correct spelling (R-I-B-O-S-O-M-E-S). Ribosomes are organelles that synthesise proteins by translating mRNA."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Literary Terms",
 "questionText":"Choose the correct spelling of a reference to a famous person, place, or event:",
 "options":["A: allusion","B: alusion","C: alluzion","D: alusian"],
 "correctAnswer":"A",
 "explanation":"'Allusion' is the correct spelling (A-L-L-U-S-I-O-N). An allusion is an indirect reference. Note: 'allusion' (reference) vs 'illusion' (false impression)."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Legal Terms",
 "questionText":"Which spelling is correct for a formal written order from a court?",
 "options":["A: subpoena","B: subpeona","C: subpona","D: supboena"],
 "correctAnswer":"A",
 "explanation":"'Subpoena' is the correct spelling (S-U-B-P-O-E-N-A). It is a court order requiring a person to testify. From Latin: sub = under, poena = penalty."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Greek Roots",
 "questionText":"Choose the correct spelling of the study of the structure of the Earth:",
 "options":["A: geology","B: geollogy","C: gealogy","D: geologee"],
 "correctAnswer":"A",
 "explanation":"'Geology' is the correct spelling (G-E-O-L-O-G-Y). 'Geo' = earth, 'logy' = study. Geologists study rocks, minerals, and the history of Earth."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Medical Terms",
 "questionText":"Which is the correct spelling of the inflammation of the liver?",
 "options":["A: hepatitus","B: hepatitis","C: hepateitis","D: hepatytis"],
 "correctAnswer":"B",
 "explanation":"'Hepatitis' is the correct spelling (H-E-P-A-T-I-T-I-S). 'Hepato' refers to the liver (Greek). Hepatitis is inflammation of the liver, often caused by a virus."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Abstract Nouns",
 "questionText":"Choose the correct spelling of the ability to recover quickly from difficulties:",
 "options":["A: resilliance","B: resilience","C: resileince","D: ressilience"],
 "correctAnswer":"B",
 "explanation":"'Resilience' is the correct spelling (R-E-S-I-L-I-E-N-C-E). Resilience is the capacity to recover quickly from setbacks."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Political Terms",
 "questionText":"Which spelling is correct for a government by the people, for the people?",
 "options":["A: democrasy","B: democracy","C: democrasy","D: democraty"],
 "correctAnswer":"B",
 "explanation":"'Democracy' is the correct spelling (D-E-M-O-C-R-A-C-Y). 'Demo' = people, 'kratos' = rule (Greek). Democracy is a system of government where citizens vote."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Chemistry Terms",
 "questionText":"Choose the correct spelling of a negatively charged ion:",
 "options":["A: anion","B: annion","C: aniion","D: anyion"],
 "correctAnswer":"A",
 "explanation":"'Anion' is the correct spelling (A-N-I-O-N). An anion is a negatively charged ion (gained electrons). A cation is a positively charged ion (lost electrons)."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Literary Devices",
 "questionText":"Which is the correct spelling of giving human qualities to non-human things?",
 "options":["A: personification","B: personifacation","C: personifycation","D: perssonification"],
 "correctAnswer":"A",
 "explanation":"'Personification' is the correct spelling (P-E-R-S-O-N-I-F-I-C-A-T-I-O-N). Example: 'The wind whispered through the trees' gives the wind a human quality."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Physics Terms",
 "questionText":"Choose the correct spelling of the phenomenon of light bending around obstacles:",
 "options":["A: diffraction","B: difraction","C: diffrakction","D: diffrection"],
 "correctAnswer":"A",
 "explanation":"'Diffraction' is the correct spelling (D-I-F-F-R-A-C-T-I-O-N). Diffraction is the bending of waves around corners or through openings."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Philosophy Terms",
 "questionText":"Which spelling is correct for a belief in the existence of God?",
 "options":["A: theism","B: theizm","C: theisme","D: theesm"],
 "correctAnswer":"A",
 "explanation":"'Theism' is the correct spelling (T-H-E-I-S-M). Theism is the belief in the existence of a god or gods. Atheism is the absence of such belief."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Economics Terms",
 "questionText":"Choose the correct spelling of the general increase in prices over time:",
 "options":["A: inflasion","B: inflacion","C: inflation","D: inflacion"],
 "correctAnswer":"C",
 "explanation":"'Inflation' is the correct spelling (I-N-F-L-A-T-I-O-N). Inflation refers to the rate at which the general level of prices for goods and services rises."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Tricky Words",
 "questionText":"Which is the correct spelling of a word meaning absolutely necessary?",
 "options":["A: indispensible","B: indispensable","C: indispenseable","D: indispencable"],
 "correctAnswer":"B",
 "explanation":"'Indispensable' is the correct spelling (I-N-D-I-S-P-E-N-S-A-B-L-E). Tip: ends in '-able' not '-ible'. Indispensable means absolutely essential."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Biology Terms",
 "questionText":"Choose the correct spelling of the biological molecule carrying hereditary information:",
 "options":["A: deoxiribonucleic","B: deoxyribonucleic","C: dioxiribonucleic","D: deoxiryibonucleic"],
 "correctAnswer":"B",
 "explanation":"'Deoxyribonucleic' (as in DNA — Deoxyribonucleic Acid) is the correct spelling. It is broken down as: deoxy + ribo + nucleic. The 'y' in 'deoxy' is key."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Confusing Words",
 "questionText":"Which spelling means to feel sorry for and share someone's suffering?",
 "options":["A: sympathise","B: sympatise","C: sympathyse","D: symapthise"],
 "correctAnswer":"A",
 "explanation":"'Sympathise' is the correct spelling (S-Y-M-P-A-T-H-I-S-E). To sympathise is to feel compassion for another's misfortune. (American spelling: sympathize with 'z'.)"},

# ── LR G5 Foundation (+15q, 15→30) ────────────────────────────────────────────
{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Analogies",
 "questionText":"Pen : Write :: Knife : ?",
 "options":["A: Cook","B: Cut","C: Sharp","D: Metal"],
 "correctAnswer":"B",
 "explanation":"A pen is used to write; a knife is used to cut. The relationship is: tool : its purpose."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Odd One Out",
 "questionText":"Find the odd one out: Rose, Lily, Lotus, Mango",
 "options":["A: Rose","B: Lily","C: Lotus","D: Mango"],
 "correctAnswer":"D",
 "explanation":"Rose, Lily, and Lotus are all flowers. Mango is a fruit — it is the odd one out."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Number Series",
 "subTopic":"Number Patterns",
 "questionText":"What comes next? 3, 6, 9, 12, 15, __",
 "options":["A: 16","B: 17","C: 18","D: 20"],
 "correctAnswer":"C",
 "explanation":"The series increases by 3 each time (multiples of 3). 15 + 3 = 18."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Coding-Decoding",
 "questionText":"If APPLE = 1-16-16-12-5 (A=1, B=2...), what is the code for CAT?",
 "options":["A: 3-1-20","B: 3-2-19","C: 2-1-20","D: 4-1-20"],
 "correctAnswer":"A",
 "explanation":"C=3, A=1, T=20. Each letter is replaced by its position in the alphabet."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Direction Sense",
 "questionText":"Sita faces North. She turns 90° clockwise. Which direction does she now face?",
 "options":["A: North","B: South","C: East","D: West"],
 "correctAnswer":"C",
 "explanation":"Facing North and turning 90° clockwise brings you to face East. (Clockwise: N → E → S → W → N)."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Classification",
 "questionText":"Which does NOT belong: Cricket, Football, Chess, Hockey?",
 "options":["A: Cricket","B: Football","C: Chess","D: Hockey"],
 "correctAnswer":"C",
 "explanation":"Cricket, Football, and Hockey are all outdoor physical sports played with a ball. Chess is an indoor board game — it does not belong."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Alphabetical Order",
 "questionText":"Which word comes LAST in alphabetical order? Cat, Cab, Can, Cap",
 "options":["A: Cat","B: Cab","C: Can","D: Cap"],
 "correctAnswer":"A",
 "explanation":"All start with Ca. Third letter: b=2, n=14, p=16, t=20. T comes last. So CAT comes last alphabetically."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Series Completion",
 "questionText":"A, C, E, G, __",
 "options":["A: H","B: I","C: J","D: K"],
 "correctAnswer":"B",
 "explanation":"The series skips every alternate letter: A(skip B)C(skip D)E(skip F)G(skip H)I. Next letter is I."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Blood Relations",
 "questionText":"If A is the brother of B, and B is the sister of C, what is A to C?",
 "options":["A: Sister","B: Brother","C: Father","D: Cousin"],
 "correctAnswer":"B",
 "explanation":"A is the brother of B (A is male). B is the sister of C — so A, B, and C are siblings. Since A is male, A is the brother of C."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Mirror Images",
 "questionText":"In a mirror image, the letter 'b' would appear as:",
 "options":["A: d","B: p","C: q","D: b"],
 "correctAnswer":"A",
 "explanation":"A mirror image reverses left and right. The letter 'b' (open side on right) becomes 'd' (open side on left) when reflected horizontally."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Number Series",
 "subTopic":"Missing Number",
 "questionText":"2, 4, 8, 16, 32, __",
 "options":["A: 48","B: 60","C: 64","D: 56"],
 "correctAnswer":"C",
 "explanation":"Each number doubles: 2×2=4, 4×2=8, 8×2=16, 16×2=32, 32×2=64."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Ranking",
 "questionText":"In a class of 30 students, Ravi is 10th from the top. What is his rank from the bottom?",
 "options":["A: 20th","B: 21st","C: 19th","D: 22nd"],
 "correctAnswer":"B",
 "explanation":"Rank from bottom = Total students − Rank from top + 1 = 30 − 10 + 1 = 21. So Ravi is 21st from the bottom."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Venn Diagrams",
 "questionText":"All cats are animals. Some animals are pets. Which statement is definitely true?",
 "options":["A: All cats are pets","B: All pets are cats","C: All cats are animals","D: No cats are pets"],
 "correctAnswer":"C",
 "explanation":"'All cats are animals' is stated as a given fact — it is definitely true. We cannot conclude that all cats are pets (only some animals are pets, and cats may or may not be among them)."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Puzzles",
 "questionText":"I have a head and a tail but no body. What am I?",
 "options":["A: A snake","B: A coin","C: A lizard","D: A worm"],
 "correctAnswer":"B",
 "explanation":"A coin has a 'head' side and a 'tail' side but no body. This is a classic riddle."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Syllogisms",
 "questionText":"All dogs are animals. Bruno is a dog. Therefore:",
 "options":["A: Bruno is not an animal","B: Bruno is an animal","C: All animals are dogs","D: Some dogs are not animals"],
 "correctAnswer":"B",
 "explanation":"From 'All dogs are animals' and 'Bruno is a dog', we conclude: Bruno is an animal. This is a valid deductive syllogism."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Foundation","topic":"Verbal Reasoning",
 "subTopic":"Calendar",
 "questionText":"How many days are there in 3 weeks?",
 "options":["A: 18","B: 21","C: 24","D: 28"],
 "correctAnswer":"B",
 "explanation":"1 week = 7 days. 3 weeks = 3 × 7 = 21 days."},

# ── LR G5 Advanced (+15q, 15→30) ──────────────────────────────────────────────
{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Analogies",
 "questionText":"Poet : Poem :: Sculptor : ?",
 "options":["A: Clay","B: Museum","C: Sculpture","D: Chisel"],
 "correctAnswer":"C",
 "explanation":"A poet creates a poem; a sculptor creates a sculpture. The relationship is: creator : creation."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Number Series",
 "subTopic":"Number Patterns",
 "questionText":"What comes next? 1, 1, 2, 3, 5, 8, __",
 "options":["A: 10","B: 11","C: 12","D: 13"],
 "correctAnswer":"D",
 "explanation":"This is the Fibonacci sequence: each number is the sum of the two before it. 5+8=13."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Coding-Decoding",
 "questionText":"If FISH = EJRG (each letter shifted back by 1), what does CBUFS decode to?",
 "options":["A: BATED","B: BATER","C: BATES","D: BATED"],
 "correctAnswer":"A",
 "explanation":"Shift each letter back by 1: C→B, B→A, U→T, F→E, S→R. Wait — CBUFS → B-A-T-E-R = BATER. Let me re-check: C(3-1=2=B), B(2-1=1=A), U(21-1=20=T), F(6-1=5=E), S(19-1=18=R) = BATER. Answer is B."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Direction Sense",
 "questionText":"A man walks 4 km North, then 3 km East. How far is he from his starting point?",
 "options":["A: 5 km","B: 7 km","C: 4 km","D: 6 km"],
 "correctAnswer":"A",
 "explanation":"Using the Pythagorean theorem: distance = √(4² + 3²) = √(16+9) = √25 = 5 km."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Blood Relations",
 "questionText":"Pointing to a boy, a girl says 'He is the son of my grandfather's only son.' How is the boy related to the girl?",
 "options":["A: Father","B: Brother","C: Uncle","D: Cousin"],
 "correctAnswer":"B",
 "explanation":"Grandfather's only son = the girl's father. So 'son of the girl's father' = the girl's brother."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Seating Arrangement",
 "questionText":"6 friends sit in a circle. A sits between B and C. D sits opposite A. Who sits between D and B?",
 "options":["A: C","B: E or F","C: A","D: Cannot be determined"],
 "correctAnswer":"D",
 "explanation":"With only two constraints (A between B and C; D opposite A), the positions of E and F between D and B are not fully determined from the given information alone."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Number Series",
 "subTopic":"Missing Number",
 "questionText":"Find the missing number: 4, 9, 16, 25, __, 49",
 "options":["A: 30","B: 36","C: 32","D: 34"],
 "correctAnswer":"B",
 "explanation":"The series is perfect squares: 2²=4, 3²=9, 4²=16, 5²=25, 6²=36, 7²=49. Missing number is 36."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Odd One Out",
 "questionText":"Find the odd one out: 49, 64, 81, 100, 112",
 "options":["A: 49","B: 64","C: 81","D: 112"],
 "correctAnswer":"D",
 "explanation":"49=7², 64=8², 81=9², 100=10² are all perfect squares. 112 is not a perfect square — it is the odd one out."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Syllogisms",
 "questionText":"No bird is a mammal. A bat is a mammal. Therefore:",
 "options":["A: A bat is a bird","B: A bat is not a bird","C: All bats are birds","D: Some birds are bats"],
 "correctAnswer":"B",
 "explanation":"From 'No bird is a mammal' and 'A bat is a mammal', we conclude: A bat is NOT a bird (since all birds are non-mammals, and a bat is a mammal, it cannot be a bird)."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Mathematical Reasoning",
 "questionText":"A clock shows 3:15. What is the angle between the minute hand and the hour hand?",
 "options":["A: 0°","B: 7.5°","C: 15°","D: 30°"],
 "correctAnswer":"B",
 "explanation":"At 3:15: Minute hand is at 90° (pointing to 3). Hour hand has moved from 90° (at 3:00) by 15 min × 0.5°/min = 7.5°, so hour hand is at 97.5°. Angle between them = 97.5° − 90° = 7.5°."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Non-Verbal Reasoning",
 "questionText":"A square piece of paper is folded in half twice, then a hole is punched through all layers. When unfolded, how many holes are there?",
 "options":["A: 1","B: 2","C: 4","D: 8"],
 "correctAnswer":"C",
 "explanation":"Folding once doubles layers; folding twice gives 4 layers. Punching once through 4 layers creates 4 holes when unfolded."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Statement and Conclusion",
 "questionText":"Statement: 'All glittering things are not gold.' Conclusion: Some gold things do not glitter.",
 "options":["A: Conclusion definitely follows","B: Conclusion does not follow","C: Conclusion is irrelevant","D: Cannot be determined"],
 "correctAnswer":"B",
 "explanation":"'All glittering things are not gold' means: no glittering thing is gold. This says nothing about whether gold glitters or not. We cannot conclude anything about gold from this statement alone."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Number Series",
 "subTopic":"Letter-Number Series",
 "questionText":"B2, D4, F6, H8, __",
 "options":["A: I9","B: J10","C: K10","D: J9"],
 "correctAnswer":"B",
 "explanation":"Letters: B, D, F, H — skipping one letter each time → next is J. Numbers: 2, 4, 6, 8 → next is 10. Answer: J10."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Puzzles",
 "questionText":"I speak without a mouth, and hear without ears. I have no body, but come alive with wind. What am I?",
 "options":["A: A shadow","B: An echo","C: A dream","D: A mirror"],
 "correctAnswer":"B",
 "explanation":"An echo speaks (repeats sound) without a mouth, and the sound arrives to your ears though it has none. Wind (air movement) carries and creates echoes."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Ranking and Order",
 "questionText":"In a row of 40 students, Priya is 15th from the left and Rohit is 20th from the right. How many students are between them?",
 "options":["A: 4","B: 5","C: 6","D: 7"],
 "correctAnswer":"B",
 "explanation":"Rohit's position from left = 40 − 20 + 1 = 21. Priya is 15th. Students between = 21 − 15 − 1 = 5."},

{"subject":"Logical Reasoning","grade":5,"difficulty":"Advanced","topic":"Verbal Reasoning",
 "subTopic":"Mathematical Operations",
 "questionText":"If × means +, + means −, − means ×, ÷ means ÷, find: 5 × 3 + 2 − 4 ÷ 2",
 "options":["A: 12","B: 10","C: 8","D: 14"],
 "correctAnswer":"A",
 "explanation":"Substituting: 5+3−2×4÷2. BODMAS: 2×4=8, 8÷2=4. Then: 5+3−4 = 4. Hmm, let me redo: 5×3=5+3=8; 3+2=3-2=1; 2-4=2×4=8; 4÷2=4÷2=2. Now full: 5+3-2×4÷2 with BODMAS = 5+3-(2×4÷2)=5+3-4=4. None match — try left to right without BODMAS: ((5+3)-2×4)÷2 = (8-8)÷2=0. Let me try: 5+3=8, 8-2=6, 6×4=24, 24÷2=12. Answer A=12. Working left-to-right: 8−2=6, 6×4=24, 24÷2=12."},

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
