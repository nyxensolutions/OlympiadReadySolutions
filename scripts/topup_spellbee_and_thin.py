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

# ─── Spell Bee G1 Foundation (top-up to 15, currently 5 so +10) ───────────────
{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"3-Letter Words",
 "questionText":"Which spelling is correct for the animal that says 'moo'?",
 "options":["A: kow","B: caw","C: cow","D: kau"],"correctAnswer":"C",
 "explanation":"The animal that says 'moo' is a COW. Spelled C-O-W."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"3-Letter Words",
 "questionText":"Choose the correct spelling for the opposite of 'cold':",
 "options":["A: hott","B: hot","C: hote","D: hoat"],"correctAnswer":"B",
 "explanation":"The opposite of cold is HOT. Spelled H-O-T."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"4-Letter Words",
 "questionText":"Which is the correct spelling of what you do when you are tired?",
 "options":["A: sleap","B: slep","C: sleep","D: sleepe"],"correctAnswer":"C",
 "explanation":"When you are tired, you SLEEP. Spelled S-L-E-E-P."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"4-Letter Words",
 "questionText":"Choose the correct spelling for a fruit that is yellow and curved:",
 "options":["A: banan","B: banana","C: banena","D: bananna"],"correctAnswer":"B",
 "explanation":"The yellow curved fruit is a BANANA. Spelled B-A-N-A-N-A."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Colour Words",
 "questionText":"Which is the correct spelling of the colour of the sky?",
 "options":["A: bloo","B: blew","C: blue","D: blui"],"correctAnswer":"C",
 "explanation":"The colour of the sky is BLUE. Spelled B-L-U-E."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Colour Words",
 "questionText":"Choose the correct spelling of the colour of grass:",
 "options":["A: gren","B: grean","C: grien","D: green"],"correctAnswer":"D",
 "explanation":"The colour of grass is GREEN. Spelled G-R-E-E-N."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Action Words",
 "questionText":"Which is the correct spelling of what birds do with their wings?",
 "options":["A: flie","B: fly","C: flay","D: fli"],"correctAnswer":"B",
 "explanation":"Birds FLY with their wings. Spelled F-L-Y."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Number Words",
 "questionText":"Choose the correct spelling of the number after nine:",
 "options":["A: tenn","B: ten","C: tean","D: tin"],"correctAnswer":"B",
 "explanation":"The number after nine is TEN. Spelled T-E-N."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Body Parts",
 "questionText":"Which is the correct spelling of the part of the body you see with?",
 "options":["A: iye","B: eye","C: aie","D: ei"],"correctAnswer":"B",
 "explanation":"You see with your EYE. Spelled E-Y-E."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Common Words",
 "questionText":"Choose the correct spelling of the place where you live:",
 "options":["A: hom","B: hoam","C: home","D: hoome"],"correctAnswer":"C",
 "explanation":"The place where you live is called HOME. Spelled H-O-M-E."},

# ─── Spell Bee G2 Foundation (top-up to 15, currently 3 so +12) ───────────────
{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Double Letters",
 "questionText":"Which is the correct spelling of a round toy that bounces?",
 "options":["A: bal","B: ball","C: balle","D: bawl"],"correctAnswer":"B",
 "explanation":"A round toy that bounces is a BALL. Spelled B-A-L-L."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"5-Letter Words",
 "questionText":"Choose the correct spelling of where you buy things:",
 "options":["A: store","B: stoer","C: stour","D: sture"],"correctAnswer":"A",
 "explanation":"A place where you buy things is a STORE. Spelled S-T-O-R-E."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Silent Letters",
 "questionText":"Which is the correct spelling of the past tense of 'know'?",
 "options":["A: noed","B: knowed","C: knew","D: knoo"],"correctAnswer":"C",
 "explanation":"The past tense of know is KNEW. Spelled K-N-E-W. The 'k' is silent."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Animals",
 "questionText":"Choose the correct spelling of a large animal with a long neck:",
 "options":["A: giraff","B: jiraf","C: giraffe","D: giraf"],"correctAnswer":"C",
 "explanation":"The tall animal with a long neck is a GIRAFFE. Spelled G-I-R-A-F-F-E."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Nature Words",
 "questionText":"Which is the correct spelling of what falls from the sky when it is cold?",
 "options":["A: snoe","B: snow","C: snowe","D: sno"],"correctAnswer":"B",
 "explanation":"Frozen precipitation is SNOW. Spelled S-N-O-W."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Food Words",
 "questionText":"Choose the correct spelling of a vegetable that makes you cry when you cut it:",
 "options":["A: onnion","B: onion","C: oinion","D: oneon"],"correctAnswer":"B",
 "explanation":"The vegetable that makes you cry is ONION. Spelled O-N-I-O-N."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Action Words",
 "questionText":"Which is the correct spelling of moving quickly on your legs?",
 "options":["A: runing","B: running","C: runn","D: runing"],"correctAnswer":"B",
 "explanation":"Moving quickly on legs is RUNNING. Note the double 'n' — R-U-N-N-I-N-G."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Opposite Words",
 "questionText":"Choose the correct spelling of the opposite of 'light' (weight):",
 "options":["A: hevy","B: heavey","C: heavy","D: heawy"],"correctAnswer":"C",
 "explanation":"The opposite of light (weight) is HEAVY. Spelled H-E-A-V-Y."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Days and Months",
 "questionText":"Which is the correct spelling of the first month of the year?",
 "options":["A: Januery","B: Janury","C: January","D: Januray"],"correctAnswer":"C",
 "explanation":"The first month is JANUARY. Spelled J-A-N-U-A-R-Y."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"School Words",
 "questionText":"Choose the correct spelling of a person who teaches in school:",
 "options":["A: techer","B: teacher","C: teachar","D: teatchr"],"correctAnswer":"B",
 "explanation":"A person who teaches is a TEACHER. Spelled T-E-A-C-H-E-R."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Tricky Spellings",
 "questionText":"Which is the correct spelling of a large sea creature with fins?",
 "options":["A: dolfin","B: dolpin","C: dolphin","D: daulphin"],"correctAnswer":"C",
 "explanation":"The sea creature is a DOLPHIN. Spelled D-O-L-P-H-I-N. Note the silent 'ph' making an 'f' sound."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Common Words",
 "questionText":"Choose the correct spelling of the day before today:",
 "options":["A: yesturday","B: yesterday","C: yesterdy","D: yestrday"],"correctAnswer":"B",
 "explanation":"The day before today is YESTERDAY. Spelled Y-E-S-T-E-R-D-A-Y."},

# ─── Spell Bee G3 Foundation (top-up to 15, currently 5 so +10) ───────────────
{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Science Words",
 "questionText":"Which is the correct spelling of the process plants use to make food?",
 "options":["A: fotosinthesis","B: photosynthesis","C: photosinthasis","D: photosynthisis"],"correctAnswer":"B",
 "explanation":"Plants make food through PHOTOSYNTHESIS. Spelled P-H-O-T-O-S-Y-N-T-H-E-S-I-S."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Tricky Spellings",
 "questionText":"Choose the correct spelling of something you do not have to pay for:",
 "options":["A: free","B: frea","C: frie","D: fre"],"correctAnswer":"A",
 "explanation":"Something you don't pay for is FREE. Spelled F-R-E-E."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Homophones",
 "questionText":"Which spelling means 'to belong to someone' (possessive, not they are)?",
 "options":["A: they're","B: there","C: their","D: ther"],"correctAnswer":"C",
 "explanation":"THEIR is the possessive form (their books). 'They're' = they are, 'there' = a place."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Words with Silent Letters",
 "questionText":"Which is the correct spelling of a person who writes books?",
 "options":["A: auther","B: author","C: authar","D: authur"],"correctAnswer":"B",
 "explanation":"A person who writes books is an AUTHOR. Spelled A-U-T-H-O-R."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Geography Words",
 "questionText":"Choose the correct spelling of the imaginary line around the middle of the Earth:",
 "options":["A: equater","B: equitor","C: equator","D: equatre"],"correctAnswer":"C",
 "explanation":"The imaginary line around the Earth's middle is the EQUATOR. Spelled E-Q-U-A-T-O-R."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Body and Health",
 "questionText":"Which is the correct spelling of the body part that pumps blood?",
 "options":["A: hart","B: haert","C: heart","D: heartt"],"correctAnswer":"C",
 "explanation":"The organ that pumps blood is the HEART. Spelled H-E-A-R-T."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Abstract Nouns",
 "questionText":"Choose the correct spelling of the feeling of great happiness:",
 "options":["A: hapiness","B: happiness","C: happyness","D: happines"],"correctAnswer":"B",
 "explanation":"The feeling of great joy is HAPPINESS. Spelled H-A-P-P-I-N-E-S-S. Note double 'p' and double 's'."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Compound Words",
 "questionText":"Which is the correct spelling of a place where you board a plane?",
 "options":["A: airpott","B: airport","C: airpoort","D: aireport"],"correctAnswer":"B",
 "explanation":"A place to board planes is an AIRPORT. Spelled A-I-R-P-O-R-T."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Action Words",
 "questionText":"Choose the correct spelling of 'to get rid of something you no longer need':",
 "options":["A: discard","B: discared","C: disccrd","D: deskard"],"correctAnswer":"A",
 "explanation":"To throw away something unneeded is to DISCARD. Spelled D-I-S-C-A-R-D."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Words with Double Letters",
 "questionText":"Which is the correct spelling of 'a room for cooking food'?",
 "options":["A: kitchin","B: kichen","C: kitchen","D: kittchen"],"correctAnswer":"C",
 "explanation":"The room for cooking is a KITCHEN. Spelled K-I-T-C-H-E-N."},

# ─── Spell Bee G4 Foundation (top-up to 15, currently 3 so +12) ───────────────
{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Commonly Misspelled",
 "questionText":"Which is the correct spelling of 'something you do regularly to stay fit'?",
 "options":["A: exersice","B: excercise","C: exercise","D: exercize"],"correctAnswer":"C",
 "explanation":"Regular physical activity is EXERCISE. Spelled E-X-E-R-C-I-S-E."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Commonly Misspelled",
 "questionText":"Choose the correct spelling of the word meaning 'very important or necessary':",
 "options":["A: necesary","B: neccesary","C: neccessary","D: necessary"],"correctAnswer":"D",
 "explanation":"NECESSARY. Remember: one Collar (1 c) and two Socks (2 s's) — N-E-C-E-S-S-A-R-Y."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Words with Silent Letters",
 "questionText":"Which is the correct spelling of the adjective meaning 'relating to knowledge gained through the senses'?",
 "options":["A: knowlege","B: knowladge","C: knowledge","D: knolege"],"correctAnswer":"C",
 "explanation":"Information/facts are called KNOWLEDGE. K-N-O-W-L-E-D-G-E. The 'k' is silent and 'd' before 'ge' is tricky."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Homophones",
 "questionText":"Choose the correct spelling meaning 'to give advice or suggestions':",
 "options":["A: advice","B: advise","C: advicse","D: advize"],"correctAnswer":"B",
 "explanation":"To give recommendations is to ADVISE (verb). ADVICE is the noun. Spelled A-D-V-I-S-E."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Long Words",
 "questionText":"Which is the correct spelling of a major natural catastrophe?",
 "options":["A: desaster","B: dissaster","C: disaster","D: dysaster"],"correctAnswer":"C",
 "explanation":"A major natural catastrophe is a DISASTER. Spelled D-I-S-A-S-T-E-R."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"ie/ei Words",
 "questionText":"Choose the correct spelling of 'to get something back that was taken':",
 "options":["A: recieve","B: receve","C: receive","D: recive"],"correctAnswer":"C",
 "explanation":"To get something back is to RECEIVE. Remember: i before e, except after c. So 'cei' not 'cie'. R-E-C-E-I-V-E."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Words with -ough",
 "questionText":"Which is the correct spelling of 'the rough outer layer of a tree'?",
 "options":["A: bork","B: bork","C: bark","D: barc"],"correctAnswer":"C",
 "explanation":"The outer layer of a tree is called BARK. Spelled B-A-R-K."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Commonly Misspelled",
 "questionText":"Choose the correct spelling meaning 'to happen at the same time':",
 "options":["A: simultanious","B: simultaneous","C: simultanous","D: simaltaneous"],"correctAnswer":"B",
 "explanation":"Happening at the same time is SIMULTANEOUS. Spelled S-I-M-U-L-T-A-N-E-O-U-S."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"School Subjects",
 "questionText":"Which is the correct spelling of the study of living organisms?",
 "options":["A: biologie","B: biolegy","C: biologee","D: biology"],"correctAnswer":"D",
 "explanation":"The study of living organisms is BIOLOGY. Spelled B-I-O-L-O-G-Y."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Descriptive Words",
 "questionText":"Choose the correct spelling meaning 'extremely large in size':",
 "options":["A: enormous","B: enourmous","C: enormus","D: enormeous"],"correctAnswer":"A",
 "explanation":"Extremely large is ENORMOUS. Spelled E-N-O-R-M-O-U-S."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Abstract Nouns",
 "questionText":"Which is the correct spelling of the state of being thankful?",
 "options":["A: gratitude","B: grattitude","C: gratitued","D: grattitood"],"correctAnswer":"A",
 "explanation":"Being thankful is GRATITUDE. Spelled G-R-A-T-I-T-U-D-E."},

{"subject":"Spell Bee","grade":4,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Tricky Spellings",
 "questionText":"Choose the correct spelling meaning 'to make something look exactly like the original':",
 "options":["A: immitate","B: imitatte","C: imitate","D: immitatte"],"correctAnswer":"C",
 "explanation":"To copy or mimic is to IMITATE. Spelled I-M-I-T-A-T-E. One 'm', not two."},

# ─── Spell Bee G4 Advanced (top-up, currently 1 so +14) ──────────────────────
{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Advanced Vocabulary",
 "questionText":"Which is the correct spelling of the quality of being honest and having strong moral principles?",
 "options":["A: integrity","B: integirity","C: intregity","D: integrety"],"correctAnswer":"A",
 "explanation":"Moral uprightness is INTEGRITY. Spelled I-N-T-E-G-R-I-T-Y."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Advanced Vocabulary",
 "questionText":"Choose the correct spelling meaning 'lasting only a short time':",
 "options":["A: temporery","B: temporary","C: temporay","D: tempory"],"correctAnswer":"B",
 "explanation":"Lasting for a short time is TEMPORARY. Spelled T-E-M-P-O-R-A-R-Y."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Science Words",
 "questionText":"Which is the correct spelling of the study of the Earth's physical structure and history?",
 "options":["A: geology","B: geologie","C: geolagy","D: geolegy"],"correctAnswer":"A",
 "explanation":"The study of Earth's structure is GEOLOGY. Spelled G-E-O-L-O-G-Y."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Commonly Confused Words",
 "questionText":"Choose the correct spelling of 'to set apart for a specific purpose':",
 "options":["A: allocate","B: alocate","C: alloccate","D: alokate"],"correctAnswer":"A",
 "explanation":"To set aside for a purpose is to ALLOCATE. Spelled A-L-L-O-C-A-T-E. Double 'l'."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Advanced Vocabulary",
 "questionText":"Which is the correct spelling of the ability to understand and share others' feelings?",
 "options":["A: empethy","B: empathy","C: empthy","D: emppathy"],"correctAnswer":"B",
 "explanation":"Understanding others' feelings is EMPATHY. Spelled E-M-P-A-T-H-Y."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Tricky Long Words",
 "questionText":"Choose the correct spelling of 'the ability to recover quickly from difficulties':",
 "options":["A: resiliance","B: resillience","C: resilience","D: resileince"],"correctAnswer":"C",
 "explanation":"The ability to recover is RESILIENCE. Spelled R-E-S-I-L-I-E-N-C-E."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Science Words",
 "questionText":"Which is the correct spelling of a substance that speeds up a chemical reaction?",
 "options":["A: catelist","B: catalyst","C: catalest","D: catallyst"],"correctAnswer":"B",
 "explanation":"A substance that speeds reactions is a CATALYST. Spelled C-A-T-A-L-Y-S-T."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Words with Silent Letters",
 "questionText":"Choose the correct spelling of 'a person who speaks on behalf of another':",
 "options":["A: spoksperson","B: spokeperson","C: spokesperson","D: spokspersen"],"correctAnswer":"C",
 "explanation":"A representative speaker is a SPOKESPERSON. Spelled S-P-O-K-E-S-P-E-R-S-O-N."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Advanced Vocabulary",
 "questionText":"Which is the correct spelling of 'to gradually destroy or undermine'?",
 "options":["A: errode","B: erode","C: eroed","D: eroad"],"correctAnswer":"B",
 "explanation":"To gradually wear away is to ERODE. Spelled E-R-O-D-E."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Words with -ance/-ence",
 "questionText":"Choose the correct spelling of 'the state of being different or distinct':",
 "options":["A: diferance","B: difference","C: diffirence","D: differance"],"correctAnswer":"B",
 "explanation":"Being distinct is DIFFERENCE. Spelled D-I-F-F-E-R-E-N-C-E. Double 'f' and '-ence' not '-ance'."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Commonly Misspelled",
 "questionText":"Which is the correct spelling of 'to take part in an activity'?",
 "options":["A: particapate","B: participait","C: participate","D: participet"],"correctAnswer":"C",
 "explanation":"To take part is to PARTICIPATE. Spelled P-A-R-T-I-C-I-P-A-T-E."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Abstract Nouns",
 "questionText":"Choose the correct spelling of 'the quality of showing good taste and correctness':",
 "options":["A: elegance","B: eleganse","C: ellagance","D: elegense"],"correctAnswer":"A",
 "explanation":"Tasteful refinement is ELEGANCE. Spelled E-L-E-G-A-N-C-E."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Advanced Vocabulary",
 "questionText":"Which is the correct spelling of 'a period of ten years'?",
 "options":["A: decaid","B: decade","C: decate","D: decaid"],"correctAnswer":"B",
 "explanation":"A period of ten years is a DECADE. Spelled D-E-C-A-D-E."},

{"subject":"Spell Bee","grade":4,"difficulty":"Advanced","topic":"Spell Bee","subTopic":"Words with -ous",
 "questionText":"Choose the correct spelling of 'extremely skilled or talented'?",
 "options":["A: virtuos","B: virtuouss","C: virtueous","D: virtuous"],"correctAnswer":"D",
 "explanation":"Extremely skilled is VIRTUOUS. Spelled V-I-R-T-U-O-U-S."},

# ─── Spell Bee G10 Foundation (top-up to 15, currently 5 so +10) ─────────────
{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Advanced Vocabulary",
 "questionText":"Which is the correct spelling of 'a formal expression of praise'?",
 "options":["A: accolade","B: acolade","C: accollade","D: akollade"],"correctAnswer":"A",
 "explanation":"A formal expression of praise is an ACCOLADE. Spelled A-C-C-O-L-A-D-E."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Latin/Greek Roots",
 "questionText":"Choose the correct spelling of 'the belief that there is no God'?",
 "options":["A: atheizm","B: atheism","C: aetheism","D: athiism"],"correctAnswer":"B",
 "explanation":"The belief in no God is ATHEISM. Spelled A-T-H-E-I-S-M."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Commonly Confused Words",
 "questionText":"Which is the correct spelling of 'the right or condition of self-government'?",
 "options":["A: autonomy","B: autonemy","C: autonomy","D: autanomy"],"correctAnswer":"A",
 "explanation":"Self-governance is AUTONOMY. Spelled A-U-T-O-N-O-M-Y."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Scientific Terms",
 "questionText":"Choose the correct spelling of 'the branch of biology dealing with heredity'?",
 "options":["A: genatics","B: genetics","C: genettis","D: gennetics"],"correctAnswer":"B",
 "explanation":"The study of heredity is GENETICS. Spelled G-E-N-E-T-I-C-S."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Abstract Nouns",
 "questionText":"Which is the correct spelling of 'the quality of being open to more than one interpretation'?",
 "options":["A: ambiguity","B: ambiguety","C: ambigiuty","D: ambiguitty"],"correctAnswer":"A",
 "explanation":"Having more than one meaning is AMBIGUITY. Spelled A-M-B-I-G-U-I-T-Y."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Commonly Misspelled",
 "questionText":"Choose the correct spelling of 'a formal meeting for consultation'?",
 "options":["A: conference","B: conferance","C: confernce","D: conferrence"],"correctAnswer":"A",
 "explanation":"A formal meeting is a CONFERENCE. Spelled C-O-N-F-E-R-E-N-C-E."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Words from Other Languages",
 "questionText":"Which is the correct spelling of the Italian word meaning 'musical tempo from the beginning'?",
 "options":["A: renaisance","B: renaissance","C: rennaisance","D: renaissence"],"correctAnswer":"B",
 "explanation":"The European cultural revival period is the RENAISSANCE. Spelled R-E-N-A-I-S-S-A-N-C-E."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Advanced Vocabulary",
 "questionText":"Choose the correct spelling of 'the practice of claiming to have higher standards than is the case'?",
 "options":["A: hipocrisy","B: hypocrisy","C: hipocracy","D: hypocracy"],"correctAnswer":"B",
 "explanation":"Claiming to have better values than one does is HYPOCRISY. Spelled H-Y-P-O-C-R-I-S-Y."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Scientific Terms",
 "questionText":"Which is the correct spelling of 'the process of converting organic material into energy'?",
 "options":["A: metabolizm","B: metabalism","C: metabolism","D: metabalism"],"correctAnswer":"C",
 "explanation":"The chemical processes sustaining life is METABOLISM. Spelled M-E-T-A-B-O-L-I-S-M."},

{"subject":"Spell Bee","grade":10,"difficulty":"Foundation","topic":"Spell Bee","subTopic":"Advanced Vocabulary",
 "questionText":"Choose the correct spelling of 'the science of efficient and comfortable work environments'?",
 "options":["A: ergonomics","B: ergonomicks","C: ergonommics","D: ergonimics"],"correctAnswer":"A",
 "explanation":"The science of workplace design is ERGONOMICS. Spelled E-R-G-O-N-O-M-I-C-S."},

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
