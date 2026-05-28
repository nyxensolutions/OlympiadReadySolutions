"""
generate_olympiad_zero_slots.py
Fill slots with 0 Olympiad questions (large sets):
  - Computer Science Grade 4
  - English Grade 1
  - English Grade 4
  - General Knowledge Grade 4
  - Hindi Grade 4
  - Mathematics Grade 1
  - Science Grade 1
  - Social Studies Grade 4
  - Science Grade 6 (only 1 Olympiad)
  - Science Grade 7 (only 1 Olympiad)
  - GK Grade 5 (only 7 Olympiad)
  - GK Grade 7 (only 2 Olympiad)
  - GK Grade 10 (only 7 Olympiad)
Target: 15 per slot minimum.
"""

import os, random, time, requests

ADMIN_API_BASE = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY  = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

POSTED = SKIPPED = FAILED = 0

def post_q(subject, grade, difficulty, topic, subtopic, text, opts, cidx, expl):
    global POSTED, SKIPPED, FAILED
    payload = dict(subject=subject, grade=grade, difficulty=difficulty,
                   topic=topic, subTopic=subtopic, questionText=text,
                   options=opts, correctAnswer=chr(65+cidx), explanation=expl)
    for attempt in range(2):
        try:
            r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                              json=payload, headers=HEADERS, timeout=25)
            if r.status_code in (200, 201): POSTED += 1; return True
            elif r.status_code == 409:      SKIPPED += 1; return False
            else: print(f"    FAIL {r.status_code}: {r.text[:80]}"); FAILED += 1; return False
        except Exception as e:
            if attempt == 0: time.sleep(2)
            else: print(f"    ERR: {e}"); FAILED += 1; return False

def add(subject, grade, topic, subtopic, text, correct, wrongs, expl, difficulty="Olympiad"):
    opts = [correct] + wrongs[:3]; random.shuffle(opts); cidx = opts.index(correct)
    return post_q(subject, grade, difficulty, topic, subtopic, text, opts, cidx, expl)

def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")

# ─────────────────────────────────────────────────────────────────────────────
# COMPUTER SCIENCE — Grade 4 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_cs_gr4():
    section("Computer Science Grade 4 — Olympiad")
    qs = [
        ("Hardware","Parts of a Computer",
         "A computer receives instructions through input devices and shows results through output devices. Which of these is ONLY an input device?",
         "Keyboard","Monitor","Printer","Speaker",
         "Keyboard sends data to the computer = input only. Monitor, Printer, Speaker all output information FROM the computer."),
        ("Software","Programs & Apps",
         "An app on a tablet that lets you draw pictures is an example of:",
         "Application software","Operating system","System software","Hardware",
         "Application software is designed for specific end-user tasks like drawing, games, or word processing. The operating system manages the device itself."),
        ("Internet","Online Safety",
         "You receive an email saying you won a prize and asking for your home address. What should you do?",
         "Tell a trusted adult and do NOT reply — it could be a scam","Reply immediately with your address","Forward it to all your friends","Click all the links in the email",
         "Unknown emails asking for personal information are likely phishing scams. Never share your address, phone, or family details with unknown online senders. Always tell a trusted adult."),
        ("Hardware","Storage",
         "Which storage device can you carry in your pocket and plug into different computers to transfer files?",
         "USB pen drive (flash drive)","Hard disk","RAM","Monitor",
         "A USB pen drive is portable, plug-and-play storage. Hard disks are usually inside the computer. RAM is temporary memory. Monitor is an output device."),
        ("Programming","Sequences",
         "A robot follows instructions in order: (1) Move forward 3 steps (2) Turn right (3) Move forward 2 steps (4) Turn left (5) Move forward 1 step. How many total steps forward does the robot take?",
         "6 steps","5 steps","3 steps","9 steps",
         "Steps forward: 3 + 2 + 1 = 6. Turning instructions change direction but don't count as forward movement."),
        ("Programming","Loops & Repetition",
         "Instead of writing 'Jump, Jump, Jump, Jump, Jump' for 5 jumps, a programmer writes REPEAT 5 TIMES: Jump. What is the advantage?",
         "Saves time and space — avoids repetition in code","The robot jumps higher","The program runs slower","The computer needs more memory",
         "Loops (REPEAT/FOR) avoid writing the same instruction multiple times, making code shorter, easier to read, and easier to change (just change the number)."),
        ("Hardware","How Computers Work",
         "When you type a letter on the keyboard, the CPU processes it, and the letter appears on the screen. Which correctly shows the flow?",
         "Input -> Process (CPU) -> Output","Output -> CPU -> Input","CPU -> Input -> Output","Screen -> Keyboard -> CPU",
         "The IPO cycle: Input (keyboard) -> Process (CPU computes) -> Output (monitor displays). All computing follows this fundamental pattern."),
        ("Internet","Networks",
         "When two computers in the same room are connected to share files, they form a:",
         "Local Area Network (LAN)","Wide Area Network (WAN)","The Internet","Wireless hotspot",
         "LAN = Local Area Network, covers a small area like a room, school, or home. The Internet is a global WAN connecting millions of devices worldwide."),
        ("Programming","Algorithms",
         "A student writes steps to make a sandwich: 1. Get bread. 2. Spread butter. 3. Add filling. 4. Close sandwich. 5. Eat. This is an example of a(n):",
         "Algorithm — a step-by-step set of instructions to complete a task","Computer program","Hardware device","Operating system",
         "An algorithm is a finite, ordered set of instructions to solve a problem or complete a task. This sandwich recipe is a real-world algorithm — the same concept computers use."),
        ("Hardware","Binary",
         "Computers store all information using only two digits: 0 and 1. This number system is called:",
         "Binary (Base 2)","Decimal (Base 10)","Hexadecimal (Base 16)","Octal (Base 8)",
         "Binary (base 2) uses only 0 and 1 — corresponding to OFF and ON states of electronic switches (transistors) in a computer. All data (text, images, sound) is ultimately stored as binary."),
        ("Software","Types of Software",
         "Which of these is an example of an OPERATING SYSTEM?",
         "Windows 11","Microsoft Word","Google Chrome","Minecraft",
         "Operating systems manage hardware and run other programs: Windows, macOS, Linux, Android, iOS. Word=application, Chrome=browser application, Minecraft=game application."),
        ("Internet","Email",
         "An email address always contains which special symbol?",
         "@ (the 'at' symbol)","# (hashtag)","* (asterisk)","& (ampersand)",
         "Every email address has the format: username@domain.extension (e.g., student@school.com). The @ separates the username from the domain name."),
        ("Programming","Debugging",
         "A program should print numbers 1 to 5 but prints 1 to 4 instead. The programmer needs to find and fix this error. This process is called:",
         "Debugging","Uploading","Formatting","Compiling",
         "Debugging is the process of finding and fixing errors (bugs) in a computer program. It is a critical skill for every programmer."),
        ("Hardware","Output Devices",
         "A student wants to print her project on paper. Which output device does she need?",
         "Printer","Scanner","Webcam","Microphone",
         "A printer produces hard copy (physical paper) output. Scanner=input device. Webcam and Microphone are both input devices."),
        ("Internet","Safe Searching",
         "When searching online, which website ending (.com, .edu, .gov) is MOST likely to have reliable government information?",
         ".gov (government websites)","  .com (commercial websites)","  .net (network websites)","  .org (any organisation)",
         ".gov domains are reserved for government agencies — they contain official, authoritative information. .com is commercial (can be anyone), .edu is educational institutions, .org can be various organisations."),
    ]
    for q in qs:
        add("Computer Science", 4, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# ENGLISH — Grade 1 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_eng_gr1():
    section("English Grade 1 — Olympiad")
    qs = [
        ("Grammar","Nouns",
         "Which word in this sentence is a noun? 'The cat sat on the mat.'",
         "cat","sat","on","the",
         "A noun is a person, place, or thing. 'Cat' and 'mat' are both nouns. 'Sat' is a verb, 'on' is a preposition, 'the' is an article."),
        ("Grammar","Singular & Plural",
         "What is the plural of 'child'?",
         "children","childs","childes","child",
         "'Child' has an irregular plural: children. It does NOT follow the regular rule of adding -s or -es."),
        ("Vocabulary","Opposites",
         "What is the opposite of 'hot'?",
         "cold","warm","cool","frozen",
         "The direct opposite (antonym) of 'hot' is 'cold'. Warm and cool are between hot and cold, not true opposites."),
        ("Grammar","Verbs",
         "Which word is the action word (verb) in: 'The dog runs fast.'?",
         "runs","dog","fast","the",
         "A verb is an action word. 'Runs' describes what the dog does — it is the verb. 'Dog' is a noun, 'fast' is an adverb, 'the' is an article."),
        ("Vocabulary","Rhyming Words",
         "Which word rhymes with 'cake'?",
         "lake","back","pack","duck",
         "Rhyming words end with the same sound. Cake ends in '-ake'. Lake also ends in '-ake'. Back/pack end in '-ack', duck ends in '-uck'."),
        ("Grammar","Articles",
         "Which is correct: '___ apple a day keeps the doctor away.'?",
         "An","A","The","Some",
         "Use 'an' before words beginning with a vowel sound (a, e, i, o, u). 'Apple' starts with the vowel 'a', so 'an apple' is correct."),
        ("Comprehension","Reading",
         "Read: 'Sam has a red ball. He plays with it every day.' What colour is Sam's ball?",
         "Red","Blue","Green","Yellow",
         "The text says 'Sam has a red ball.' Reading comprehension: the answer is directly stated in the passage."),
        ("Vocabulary","Body Parts",
         "We use this part of the body to smell. It is in the middle of our face. What is it?",
         "Nose","Ear","Eye","Mouth",
         "The nose is the organ of smell, located in the centre of the face. Ears=hearing, Eyes=sight, Mouth=taste/speech."),
        ("Grammar","Capital Letters",
         "Which word MUST start with a capital letter?",
         "india (a country's name)","book","run","big",
         "Proper nouns (names of specific people, places, countries) always start with a capital letter. India is a proper noun. Book, run, big are common/ordinary words."),
        ("Vocabulary","Colours & Shapes",
         "A shape with THREE sides and THREE corners is called a:",
         "Triangle","Square","Circle","Rectangle",
         "Tri = three. A triangle has 3 sides and 3 angles/corners. Square has 4 equal sides. Rectangle has 4 sides. Circle has no corners."),
        ("Grammar","Pronouns",
         "Replace the underlined word with the correct pronoun: 'Priya is my friend. __ is very kind.'",
         "She","He","It","They",
         "Priya is a girl's name, so the pronoun 'She' replaces 'Priya'. He=male, It=object/animal, They=plural."),
        ("Vocabulary","Opposites & Sizes",
         "What is the opposite of 'big'?",
         "small","tall","heavy","long",
         "The antonym (opposite) of 'big' is 'small'. Tall is the opposite of short, heavy is the opposite of light, long is the opposite of short."),
        ("Grammar","Question Words",
         "Which question word asks about a PLACE?",
         "Where","Who","What","When",
         "Where = place/location. Who = person. What = thing/action. When = time. Why = reason. How = manner."),
        ("Vocabulary","Animals & Sounds",
         "What sound does a cow make?",
         "Moo","Baa","Neigh","Quack",
         "Cow = Moo. Sheep = Baa. Horse = Neigh. Duck = Quack. These are animal onomatopoeia words in English."),
        ("Grammar","Sentences",
         "Which of these is a COMPLETE sentence?",
         "The bird sings sweetly.","The bird sings","Sings sweetly","The little",
         "A complete sentence needs a subject (who/what) + predicate (what they do). 'The bird sings sweetly' has subject (The bird) + verb (sings) + adverb (sweetly). Others are incomplete."),
    ]
    for q in qs:
        add("English", 1, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# ENGLISH — Grade 4 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_eng_gr4():
    section("English Grade 4 — Olympiad")
    qs = [
        ("Grammar","Tenses",
         "Choose the correct verb form: 'She ___ to school every day, but yesterday she ___ sick.'",
         "goes / was","go / is","went / were","goes / is",
         "Habitual present action uses simple present: 'goes'. The past event uses simple past: 'was'. Mixed tenses in one sentence are common and important to master."),
        ("Vocabulary","Homophones",
         "Which sentence uses the correct homophone? 'I can ___ the beautiful flowers.'",
         "see","sea","si","cee",
         "Homophones sound the same but have different meanings/spellings. 'See' (to look) vs 'sea' (ocean). Context: you look at flowers, so 'see' is correct."),
        ("Grammar","Adjectives",
         "Identify the adjective in: 'The clever girl solved the difficult puzzle quickly.'",
         "clever and difficult (both are adjectives)","solved","quickly","girl",
         "Adjectives describe nouns. 'Clever' describes the girl; 'difficult' describes the puzzle. 'Quickly' is an adverb (describes the verb). 'Girl' and 'solved' are noun and verb."),
        ("Comprehension","Inference",
         "Read: 'Raju put on his raincoat and picked up his umbrella before leaving home.' What can we infer about the weather?",
         "It was raining or about to rain","It was sunny and hot","It was snowing","It was windy but dry",
         "Inference means reading between the lines. Raincoat + umbrella = preparation for rain. This is not directly stated but strongly implied by the actions described."),
        ("Grammar","Conjunctions",
         "Choose the correct conjunction: 'She wanted to go to the park ___ it was raining heavily.'",
         "but","and","so","because",
         "'But' shows contrast/opposition: she wanted to go (positive), but it was raining (negative/obstacle). 'And' joins similar ideas, 'so' shows result, 'because' shows reason."),
        ("Vocabulary","Synonyms",
         "Which word is a synonym for 'brave'?",
         "courageous","fearful","timid","cowardly",
         "Synonyms have similar meanings. Brave = courageous (both mean willing to face danger). Fearful, timid, cowardly are antonyms (opposites) of brave."),
        ("Grammar","Prepositions",
         "Fill in: 'The book is ___ the table, and the pen is ___ the pencil box.'",
         "on / in","in / on","under / above","beside / below",
         "'On the table' = resting on top of a surface. 'In the pencil box' = inside a container. Prepositions show spatial relationships."),
        ("Comprehension","Main Idea",
         "Read: 'Trees give us fruits, wood, and oxygen. They prevent floods and provide shade. Many animals live in trees. We must protect our forests.' What is the MAIN IDEA?",
         "Trees are very useful and important, so we must protect them","Trees give us fruits only","Animals live in trees","Floods are prevented by dams",
         "The main idea is the central message of the passage. All sentences support the conclusion: trees are valuable and need protection."),
        ("Vocabulary","Compound Words",
         "Which two words combine to make the compound word 'SUNSHINE'?",
         "Sun + Shine","Sun + Fine","Son + Shine","Sun + Shone",
         "A compound word is formed by joining two words: Sun + Shine = Sunshine. Similarly: Rain + Bow = Rainbow, Fire + Works = Fireworks."),
        ("Grammar","Punctuation",
         "Which sentence is punctuated CORRECTLY?",
         "Wow, what a beautiful painting!","wow what a beautiful painting!","Wow what a beautiful painting.","wow, What a beautiful painting?",
         "Exclamatory sentences expressing surprise/admiration end with '!'. 'Wow' as an interjection is followed by a comma. The sentence starts with a capital letter."),
        ("Grammar","Active & Passive Voice",
         "'The cat caught the mouse.' In passive voice, this becomes:",
         "'The mouse was caught by the cat.'","'The mouse caught the cat.'","'The cat was caught by the mouse.'","'The mouse is catching the cat.'",
         "Active: Subject (cat) + verb (caught) + object (mouse). Passive: Object becomes subject + 'was/were' + past participle + 'by' + original subject. 'The mouse was caught by the cat.'"),
        ("Vocabulary","Antonyms",
         "What is the antonym of 'ancient'?",
         "modern","old","historical","traditional",
         "Ancient = very old/from long ago. Antonym = modern (new, current, contemporary). Old, historical, traditional are all similar in meaning to ancient, not opposites."),
        ("Grammar","Subject-Verb Agreement",
         "Choose the correct sentence:",
         "Neither the teacher nor the students were present.","Neither the teacher nor the students was present.","Neither the teacher nor the students is present.","Neither the teacher nor the students are was present.",
         "With 'neither...nor', the verb agrees with the subject CLOSEST to it. 'Students' (plural) is closest, so use 'were'. Rule: RSVP — the verb agrees with the nearest subject."),
        ("Comprehension","Vocabulary in Context",
         "In the sentence 'The miser was so parsimonious that he refused to buy new shoes despite holes in his old ones', 'parsimonious' means:",
         "Extremely unwilling to spend money (miserly)","Extremely generous","Very careless","Incredibly brave",
         "Context clue: 'miser' + 'refused to buy despite holes' — all indicate extreme unwillingness to spend. Parsimonious = excessively unwilling to spend money."),
        ("Grammar","Direct & Indirect Speech",
         "Change to indirect speech: She said, 'I am going to the market.'",
         "She said that she was going to the market.","She said that I am going to the market.","She says that she is going to the market.","She told I was going to the market.",
         "Indirect speech rules: (1) Remove quotes, add 'that'. (2) Change pronoun I->she. (3) Backshift tense: 'am going' -> 'was going' (present continuous -> past continuous)."),
    ]
    for q in qs:
        add("English", 4, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GENERAL KNOWLEDGE — Grade 4 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_gk_gr4():
    section("General Knowledge Grade 4 — Olympiad")
    qs = [
        ("India","National Symbols",
         "What is the national flower of India?",
         "Lotus","Rose","Sunflower","Marigold",
         "The Lotus (Nelumbo nucifera) is India's national flower. It grows in muddy water but blooms beautifully above — symbolising purity and spiritual achievement."),
        ("India","States & Capitals",
         "What is the capital of Rajasthan?",
         "Jaipur","Jodhpur","Udaipur","Ajmer",
         "Jaipur (the Pink City) is the capital of Rajasthan. It was founded in 1727 by Maharaja Jai Singh II and is famous for the Hawa Mahal and Amber Fort."),
        ("World","Planets",
         "Which planet is known as the Red Planet?",
         "Mars","Jupiter","Venus","Saturn",
         "Mars appears red because its surface is covered with iron oxide (rust). It has two small moons (Phobos and Deimos) and is the most likely planet for future human exploration."),
        ("India","Famous Personalities",
         "Who is known as the 'Father of the Indian Constitution'?",
         "Dr. B.R. Ambedkar","Mahatma Gandhi","Jawaharlal Nehru","Sardar Patel",
         "Dr. B.R. Ambedkar was the chairman of the Drafting Committee of the Indian Constitution. He is called the Father of the Indian Constitution for his crucial role in framing it."),
        ("Science","Inventions",
         "Who invented the light bulb?",
         "Thomas Edison","Alexander Graham Bell","Isaac Newton","Albert Einstein",
         "Thomas Edison invented the practical incandescent light bulb in 1879. He also invented the phonograph and made vast improvements to the telegraph."),
        ("India","Geography",
         "Which is the largest state in India by area?",
         "Rajasthan","Madhya Pradesh","Maharashtra","Uttar Pradesh",
         "Rajasthan is the largest state by area (~342,239 km²). The Thar Desert covers a large part of it. UP is the most populous state."),
        ("World","Countries & Capitals",
         "What is the capital of Japan?",
         "Tokyo","Beijing","Seoul","Bangkok",
         "Tokyo is the capital of Japan and one of the world's most populous cities. Beijing=China, Seoul=South Korea, Bangkok=Thailand."),
        ("India","Sports",
         "Who is called the 'Flying Sikh' of India?",
         "Milkha Singh","P.T. Usha","Abhinav Bindra","Saina Nehwal",
         "Milkha Singh (1929-2021) was India's legendary sprinter, nicknamed the 'Flying Sikh'. He won gold at the 1958 Commonwealth Games and came 4th at the 1960 Rome Olympics."),
        ("Science","Animals",
         "Which is the fastest land animal in the world?",
         "Cheetah","Lion","Horse","Greyhound",
         "The cheetah can reach speeds of 112-120 km/h in short bursts. It is built for speed with a flexible spine, semi-retractable claws, and a large heart and lungs."),
        ("India","History",
         "The famous Jallianwala Bagh massacre took place in which year?",
         "1919","1920","1915","1930",
         "The Jallianwala Bagh massacre occurred on 13 April 1919 in Amritsar, Punjab. General Dyer ordered troops to fire on a peaceful gathering, killing hundreds of Indians."),
        ("World","Rivers",
         "Which is the longest river in the world?",
         "Nile","Amazon","Yangtze","Mississippi",
         "The Nile River (6,650 km) in Africa is generally considered the world's longest river. The Amazon (6,400 km) carries the most water by volume."),
        ("India","Monuments",
         "The Gateway of India is located in which city?",
         "Mumbai","Delhi","Kolkata","Chennai",
         "The Gateway of India is a famous arch monument in Mumbai (formerly Bombay), built in 1924. It was built to commemorate King George V's visit to India in 1911."),
        ("Science","Space",
         "The Earth takes approximately how long to complete one revolution around the Sun?",
         "365.25 days (1 year)","24 hours","30 days","7 days",
         "Earth takes ~365.25 days to orbit the Sun. The extra 0.25 day accumulates into a Leap Day every 4 years. Earth's rotation on its axis = 24 hours = 1 day."),
        ("World","World Records",
         "What is the name of the world's largest ocean?",
         "Pacific Ocean","Atlantic Ocean","Indian Ocean","Arctic Ocean",
         "The Pacific Ocean is the world's largest and deepest ocean, covering about 165 million km² — more than all land areas combined. It contains the Mariana Trench."),
        ("India","Culture",
         "Diwali is called the 'Festival of Lights'. It celebrates the return of which Hindu deity after 14 years of exile?",
         "Lord Rama","Lord Krishna","Lord Shiva","Lord Brahma",
         "Diwali celebrates Lord Rama's return to Ayodhya after 14 years of exile and defeating the demon king Ravana. People light diyas (lamps) to guide his way home."),
    ]
    for q in qs:
        add("General Knowledge", 4, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# HINDI — Grade 4 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_hindi_gr4():
    section("Hindi Grade 4 — Olympiad")
    qs = [
        ("Vyakaran","Sangya (Noun)",
         "Hindi mein 'sangya' kise kehte hain?",
         "Kisi vyakti, sthan, vastu ya bhaav ke naam ko","Kaam ko darshane wale shabd ko","Sangya ki jagah istemaal hone wale shabd ko","Visheshata batane wale shabd ko",
         "Sangya (noun) = kisi vyakti (Rama), sthan (Delhi), vastu (kitab) ya bhaav (pyaar) ke naam. Jaise: 'ladki', 'pahaad', 'khushi'."),
        ("Vyakaran","Vachan (Number)",
         "'Ladki' ka bahuvachan kya hoga?",
         "Ladkiyan","Ladkis","Ladkien","Ladki",
         "Akarvant striling sangya mein 'i' ko 'iyan' kar dete hain: Ladki -> Ladkiyan. Jaise: Nadi -> Nadiyan, Roti -> Rotiyan."),
        ("Vyakaran","Ling (Gender)",
         "'Sherni' kis ling ka shabd hai?",
         "Striling (feminine)","Pulling (masculine)","Napunsak ling","Ubhay ling",
         "Sherni = feminine (striling) — yah sher (masculine, pulling) ka striling roop hai. Jaise: Raja-Rani, Mor-Morni, Neta-Netri."),
        ("Vyakaran","Sarvanam (Pronoun)",
         "Rahi ne kaha, '_____ kal school nahi aayi.' Sahi sarvanam chuniye:",
         "Main","Tum","Woh","Hum",
         "Rahi khud apni baat kar rahi hai, isliye 'Main' (I = first person singular) sahi sarvanam hai."),
        ("Sahitya","Kavita (Poetry)",
         "Hindi kavita mein ek hi tarah ki dhwani ka baar baar aana kya kehlata hai?",
         "Tauk (rhyme/tuk)","Sandhi","Samas","Upsarg",
         "Tauk ya tuk = kavita ki panktiyaan jo ek jaisi dhwani par khatam hoti hain. Jaise: 'Aa ja mere paas' aur 'Karo meri baat'. Yahi kavita ko sangeetaatmak banata hai."),
        ("Vyakaran","Visheshan (Adjective)",
         "'Yah sundar phool hai.' Is vakya mein visheshan kaunsa shabd hai?",
         "Sundar","Phool","Yah","Hai",
         "Visheshan = visheshata batane wala shabd. 'Sundar' phool ki visheshata bata raha hai. 'Phool' sangya hai, 'Yah' sarvanam hai, 'Hai' kriya hai."),
        ("Vyakaran","Kriya (Verb)",
         "'Ram ne khana khaya.' Is vakya mein kriya kaunsi hai?",
         "Khaya","Ram","Khana","Ne",
         "Kriya = kaam karne ya hone wala shabd. 'Khaya' (ate) kaam ko darshata hai — yah kriya hai. 'Ram' sangya, 'khana' kriya-visheshak, 'ne' karak hai."),
        ("Vyakaran","Sandhi",
         "'Vidyaalay' shabd kis sandhi se bana hai?",
         "Vidya + Aalay (Deergha Swar Sandhi)","Vidya + Lay","Vidyaa + Aaaly","Vid + Yaalay",
         "Vidyalay = Vidya + Aalay. Jab 'a' + 'aa' milte hain to 'aa' banta hai — yah Deergha Swar Sandhi ka udaharan hai."),
        ("Sahitya","Muhavare (Idioms)",
         "'Haath pair marna' muhavare ka sahi arth kya hai?",
         "Bahut koshish karna","Maar pitai karna","Haath pair hilana","Daudna",
         "Muhavare ka arth seedha nahi hota. 'Haath pair marna' = kasht utha kar bahut prayaas karna (to make a great effort/struggle). Jaise: 'Naukri ke liye bahut haath pair maare.'"),
        ("Vyakaran","Upsarg (Prefix)",
         "'Apman' shabd mein kaunsa upsarg hai?",
         "Ap","Man","Apa","Am",
         "Upsarg 'Ap' + mul shabd 'Man' = Apman (disrespect/insult). 'Ap' upsarg nindaa ya viprit arth deta hai. Jaise: Apshakun, Apyash."),
        ("Vyakaran","Karak (Case)",
         "'Seeta ne seb khaya.' Mein 'Seeta ne' kaunsa karak hai?",
         "Karta karak (nominative)","Karma karak","Karan karak","Sambandh karak",
         "Karta karak = kaam karne wala — 'ne' vibhakti se pahchana jata hai. Seeta kaam kar rahi hai (kha rahi hai), isliye 'Seeta ne' karta karak hai."),
        ("Sahitya","Dohe (Couplets)",
         "Kabir Das ne likha: 'Kaal kare so aaj kar, aaj kare so ab.' Iska sandesh kya hai?",
         "Kaam ko aaj aur abhi karo, kal par mat talo","Aaj aaram karo kal ke liye","Kabhi bhi kaam karo","Kal ka kaam aaj mat karo",
         "Kabir ka doha samay ki kaymat sikhata hai: jo kaam kal karna hai woh aaj karo, jo aaj karna hai woh abhi karo. Procrastination (taal-matol) galat hai."),
        ("Vyakaran","Paryayvachi (Synonyms)",
         "'Jal' ke teen paryayvachi shabd kaunse hain?",
         "Neer, Paani, Ambu","Agni, Paani, Vayu","Neer, Bhoomi, Ambu","Paani, Mitti, Hawa",
         "Jal = Paani = Neer = Ambu = Toye = Salil = Vari — sab 'paani' ke paryayvachi hain. Hindi mein paani ke 10 se zyada paryayvachi hain."),
        ("Vyakaran","Viram Chinh (Punctuation)",
         "Prashn chinh (?) ka prayog kab hota hai?",
         "Prashan vaachak vakyon ke ant mein","Uddharanon ke baad","Vakyon ke beech mein","Sambodhan ke baad",
         "Prashan chinh (?) = question mark — seedhe prashn ke baad lagta hai. Jaise: 'Tumhara naam kya hai?' Uddaharan chinh (:), Viraam (,), Poorn viraam (.) alag kamon ke liye hain."),
        ("Sahitya","Kahani (Story) Comprehension",
         "Ek kahani mein: 'Kauwa pyaasa tha. Usne ghaant ghoot paani khoja par koi ghara mila. Usne kanche daale, paani upar aa gaya.' Kauwe ne kya seekha?",
         "Buddhi aur koshish se mushkil hal hoti hai","Paani peena zaruri nahi","Ghara pakad ke peena chahiye","Kanche khane chahiye",
         "Kauwe ki kahani ek mashhoor Aesop ki niti katha hai jo sikhati hai: samajhdari aur prayaas se badi se badi mushkil hal ki ja sakti hai. Yahi kahani ki seekh (moral) hai."),
    ]
    for q in qs:
        add("Hindi", 4, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# MATHEMATICS — Grade 1 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_math_gr1():
    section("Mathematics Grade 1 — Olympiad")
    qs = [
        ("Numbers","Counting",
         "Count the stars: ★★★★★★★★★. How many stars are there?",
         "9","8","10","7",
         "Count one by one: 1,2,3,4,5,6,7,8,9. There are 9 stars. Careful counting is an important skill!"),
        ("Numbers","Before & After",
         "What number comes just AFTER 19?",
         "20","18","21","9",
         "The number line goes ...17, 18, 19, 20, 21... The number just after 19 is 20. After 19 we move to the next ten (20)."),
        ("Numbers","Addition",
         "Sam has 7 red marbles and 5 blue marbles. How many marbles does he have altogether?",
         "12","10","13","11",
         "7 + 5 = 12. You can count on from 7: 8,9,10,11,12. Sam has 12 marbles in total."),
        ("Numbers","Subtraction",
         "There were 15 birds on a tree. 6 flew away. How many birds are left?",
         "9","8","10","21",
         "15 - 6 = 9. Subtraction: we take away 6 from 15. Count back from 15: 14,13,12,11,10,9. Nine birds remain."),
        ("Shapes","2D Shapes",
         "A shape that has NO corners and NO straight sides, and is perfectly round is called a:",
         "Circle","Square","Triangle","Rectangle",
         "A circle has no corners (vertices) and no straight sides — it is a perfectly round closed curve. Square has 4 corners, Triangle has 3, Rectangle has 4."),
        ("Numbers","Comparing Numbers",
         "Which number is the GREATEST: 17, 9, 23, 15?",
         "23","17","15","9",
         "To compare: 23 has 2 tens, 17 has 1 ten, 15 has 1 ten, 9 has 0 tens. 2 tens is the most, so 23 is the greatest."),
        ("Numbers","Odd & Even",
         "Which of these numbers is ODD?",
         "7","4","8","10",
         "Odd numbers cannot be divided evenly by 2. They end in 1,3,5,7,9. 7 is odd. 4, 8, 10 are even (end in 4, 8, 0)."),
        ("Numbers","Patterns",
         "What comes next in this pattern? 2, 4, 6, 8, __",
         "10","9","11","12",
         "This is the pattern of even numbers, increasing by 2 each time. 8 + 2 = 10. These are the multiples of 2."),
        ("Numbers","Place Value",
         "In the number 34, the digit 3 represents:",
         "3 tens (30)","3 ones","3 hundreds","30 ones",
         "In the number 34: 3 is in the TENS place = 30. 4 is in the ONES place = 4. 34 = 30 + 4."),
        ("Measurement","Length",
         "Which is the LONGEST: a pencil (15 cm), an eraser (5 cm), a ruler (30 cm), a crayon (10 cm)?",
         "Ruler (30 cm)","Pencil (15 cm)","Crayon (10 cm)","Eraser (5 cm)",
         "Compare the numbers: 30 > 15 > 10 > 5. The ruler at 30 cm is the longest."),
        ("Numbers","Number Names",
         "What is the number name for 16?",
         "Sixteen","Sixty","Seventeen","Fifteen",
         "16 = Sixteen. 60 = Sixty. 17 = Seventeen. 15 = Fifteen. The 'teen' numbers (13-19) can be tricky!"),
        ("Numbers","Addition with Carrying",
         "What is 8 + 7?",
         "15","13","14","16",
         "8 + 7 = 15. You can break it: 8 + 2 = 10, then 10 + 5 = 15. Or count on from 8: 9,10,11,12,13,14,15."),
        ("Shapes","3D Shapes",
         "A ball is an example of which 3D shape?",
         "Sphere","Cube","Cylinder","Cone",
         "A sphere is a perfectly round 3D shape — like a ball or globe. Cube = dice. Cylinder = tin can. Cone = ice cream cone."),
        ("Numbers","Subtraction",
         "Meena has 20 toffees. She gives 8 to her friend. How many does she have left?",
         "12","8","10","14",
         "20 - 8 = 12. Meena keeps 12 toffees. You can count back from 20: 19,18,17,16,15,14,13,12."),
        ("Measurement","Time",
         "How many days are there in one week?",
         "7","5","6","8",
         "One week = 7 days: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday. 4 weeks = approximately 1 month."),
    ]
    for q in qs:
        add("Mathematics", 1, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# SCIENCE — Grade 1 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_science_gr1():
    section("Science Grade 1 — Olympiad")
    qs = [
        ("Living World","Plants & Animals",
         "Which of these is a LIVING thing?",
         "A mango tree","A rock","A glass of water","A toy car",
         "Living things grow, breathe, reproduce, and need food. A mango tree is alive. Rocks, water, and toy cars are non-living — they don't grow or reproduce."),
        ("Our Body","Senses",
         "We use our EYES to:",
         "See objects and colours","Hear sounds","Smell flowers","Taste food",
         "The five senses: Eyes=see, Ears=hear, Nose=smell, Tongue=taste, Skin=touch. Eyes detect light and help us see shapes, colours, and movement."),
        ("Plants","Parts of a Plant",
         "Which part of a plant is usually underground and absorbs water?",
         "Root","Leaf","Flower","Stem",
         "Roots anchor the plant in the soil and absorb water and minerals. Leaves make food. Flowers help in reproduction. Stems support the plant and transport water."),
        ("Animals","Types of Animals",
         "Which animal gives us milk?",
         "Cow","Hen","Fish","Dog",
         "Cows are dairy animals that produce milk for their calves. Humans collect this milk for drinking, making curd, butter, and cheese. Hens give eggs, fish give fish."),
        ("Our Environment","Weather",
         "When the sky is full of dark clouds and it starts to pour, the weather is:",
         "Rainy","Sunny","Windy","Foggy",
         "Dark clouds carry water droplets. When they get heavy, water falls as rain. This is rainy weather. Sunny=clear sky, Windy=strong breeze, Foggy=thick mist."),
        ("Living World","Needs of Living Things",
         "What do ALL living things need to survive?",
         "Food, water, and air","Only water","Only sunlight","Only food",
         "All living things need: food (energy), water (for cell functions), and air (oxygen for respiration). Plants also need sunlight, but not all animals need direct sunlight."),
        ("Animals","Animal Homes",
         "A bird lives in a:",
         "Nest","Den","Burrow","Web",
         "Birds build nests from twigs, grass, and mud to lay eggs and raise chicks. Den=lion/bear. Burrow=rabbit/fox. Web=spider (not really a home but where they catch prey)."),
        ("Our Body","Body Parts",
         "How many fingers do we have on BOTH hands together?",
         "10","8","5","12",
         "Each hand has 5 fingers (including thumb). Both hands: 5 + 5 = 10 fingers total."),
        ("Plants","What Plants Need",
         "A plant kept in a dark cupboard for many days will:",
         "Turn yellow and die because it cannot make food without sunlight","Grow faster in the dark","Stay green always","Produce more flowers",
         "Plants need sunlight for photosynthesis (food-making). Without light, chlorophyll breaks down, leaves turn yellow (chlorosis), and eventually the plant dies."),
        ("Our Environment","Day & Night",
         "We have day when the Sun is shining. We have night when:",
         "Our part of Earth has turned away from the Sun","The Sun goes to sleep","The Moon covers the Sun","The stars turn off the Sun",
         "Day and night are caused by Earth's rotation. When your side faces the Sun = day. When your side faces away from the Sun = night. The Sun doesn't move; Earth spins."),
        ("Animals","Wild & Pet Animals",
         "Which of these is a PET animal (kept at home)?",
         "Dog","Lion","Elephant","Tiger",
         "Pet animals live with humans: dogs, cats, rabbits, fish, birds. Wild animals (lions, elephants, tigers) live in forests and cannot be safely kept as pets."),
        ("Our Body","Hygiene",
         "Why should we wash our hands before eating?",
         "To remove germs (bacteria) that could make us sick","To make food taste better","Because our hands are always dirty","To make our nails clean only",
         "Our hands touch many surfaces and carry invisible germs (bacteria, viruses). Washing with soap removes germs before they enter our body through food and make us ill."),
        ("Plants","Fruits & Seeds",
         "Seeds are found inside:",
         "Fruits","Roots","Stems","Leaves",
         "Fruits develop from flowers and contain seeds. The fruit protects the seed and often helps in seed dispersal (animals eat fruits and spread seeds). Examples: mango seed inside mango fruit."),
        ("Our Environment","Air & Water",
         "Air is important for us because we:",
         "Breathe it to stay alive","Drink it","Eat it","Sleep in it",
         "We breathe air to get oxygen, which our body needs for releasing energy from food (cellular respiration). Without air, we cannot survive for more than a few minutes."),
        ("Animals","Animal Sounds",
         "A lion makes a loud sound called a:",
         "Roar","Bark","Moo","Chirp",
         "Lion=Roar. Dog=Bark. Cow=Moo. Bird=Chirp/Tweet. These are characteristic sounds of different animals — important vocabulary in early science."),
    ]
    for q in qs:
        add("Science", 1, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# SOCIAL STUDIES — Grade 4 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_sst_gr4():
    section("Social Studies Grade 4 — Olympiad")
    qs = [
        ("Our Country","Regions of India",
         "India is divided into how many major geographical regions? (Northern Mountains, Northern Plains, Peninsular Plateau, Coastal Plains, Islands)",
         "5 major regions","3 major regions","4 major regions","7 major regions",
         "India's 5 major physical divisions: (1) Himalayan Mountains (2) Northern Plains (3) Peninsular Plateau (4) Coastal Plains (5) Islands (Andaman & Nicobar + Lakshadweep)."),
        ("Our History","Ancient India",
         "The Indus Valley Civilisation had cities with excellent drainage and water supply. The two most famous cities were:",
         "Harappa and Mohenjo-daro","Delhi and Agra","Pataliputra and Vaishali","Taxila and Nalanda",
         "Harappa (Punjab) and Mohenjo-daro (Sindh, now Pakistan) are the largest known Indus Valley Civilisation cities, famous for grid-planned streets and covered drains (~2600-1900 BCE)."),
        ("Our Government","Local Government",
         "In rural areas, local self-government is handled by:",
         "Gram Panchayat","Municipal Corporation","State Assembly","Lok Sabha",
         "Gram Panchayat = village-level self-government body. Municipal Corporation = cities. State Assembly = state legislature. Lok Sabha = national parliament."),
        ("Our Environment","Natural Disasters",
         "An earthquake is measured using which scale?",
         "Richter Scale","Beaufort Scale","Celsius Scale","Decibel Scale",
         "The Richter Scale measures earthquake magnitude (energy released). Beaufort Scale = wind speed. Celsius = temperature. Decibel = sound intensity."),
        ("Our Country","Rivers",
         "The Ganga originates from which glacier?",
         "Gangotri Glacier, Uttarakhand","Siachen Glacier","Zemu Glacier","Baltoro Glacier",
         "The Ganga originates at Gangotri Glacier in the Garhwal Himalayas, Uttarakhand. The actual source is called Gaumukh ('cow's mouth'). The Ganga then flows ~2,525 km to the Bay of Bengal."),
        ("Our History","Freedom Struggle",
         "Mahatma Gandhi gave the call 'Do or Die' during which movement?",
         "Quit India Movement (1942)","Non-Cooperation Movement (1920)","Civil Disobedience Movement (1930)","Swadeshi Movement (1905)",
         "'Do or Die' (Karo Ya Maro) was Gandhi's rallying cry at the launch of the Quit India Movement on 8 August 1942, demanding immediate British withdrawal from India."),
        ("Our Country","Seasons",
         "India has mainly three seasons. Which option correctly names them?",
         "Summer, Monsoon (Rainy), Winter","Spring, Autumn, Winter","Hot, Cold, Wet","Dry, Wet, Mild",
         "India's three main seasons: Summer (March-June), Monsoon/Rainy (July-September), Winter (October-February). Some regions also experience a brief autumn/spring transition."),
        ("Our Government","Fundamental Duties",
         "According to the Indian Constitution, who has the duty to protect the environment?",
         "Every citizen of India","Only the government","Only factories","Only farmers",
         "Article 51A (g) of the Indian Constitution lists Fundamental Duties: every citizen must protect and improve the natural environment including forests, lakes, rivers, and wildlife."),
        ("Our Country","Minerals & Resources",
         "Coal is an important mineral used to generate electricity. Coal-rich states in India include:",
         "Jharkhand and Odisha","Kerala and Goa","Rajasthan and Gujarat","Punjab and Haryana",
         "Jharkhand (~40% of India's reserves), Odisha, Chhattisgarh, West Bengal, and Madhya Pradesh are major coal-producing states. Jharkhand alone has the largest coal deposits."),
        ("Our Society","Diversity",
         "India is known for its diversity. 'Unity in Diversity' means:",
         "People of different religions, languages, and cultures live together harmoniously","Everyone in India speaks the same language","All Indians follow the same religion","India has only one culture",
         "'Unity in Diversity' is India's strength — 1.4 billion people speaking 1,600+ languages, following many religions, yet living as one nation with a shared constitutional identity."),
        ("Our History","Mughal Empire",
         "Which Mughal emperor built the Taj Mahal?",
         "Shah Jahan","Akbar","Aurangzeb","Babur",
         "Shah Jahan (reign 1628-1658) built the Taj Mahal in Agra in memory of his beloved wife Mumtaz Mahal who died in 1631. Construction took ~22 years (1632-1653)."),
        ("Our Country","Transport",
         "The Golden Quadrilateral is a famous highway network connecting which four cities?",
         "Delhi, Mumbai, Chennai, Kolkata","Delhi, Agra, Jaipur, Chandigarh","Mumbai, Pune, Nashik, Aurangabad","Chennai, Bangalore, Hyderabad, Kochi",
         "The Golden Quadrilateral connects India's four major metros: Delhi (north), Mumbai (west), Chennai (south), and Kolkata (east) — forming a quadrilateral shape across India."),
        ("Our Environment","Conservation",
         "Project Tiger was launched in India to protect:",
         "The Bengal Tiger from extinction","All Indian wildlife","Only tigers in Rajasthan","International tigers",
         "Project Tiger was launched in 1973 by PM Indira Gandhi to save the critically endangered Bengal Tiger. Tiger numbers have grown from ~1,800 in 1973 to over 3,600 today."),
        ("Our Government","Elections",
         "The minimum age to VOTE in Indian elections is:",
         "18 years","21 years","25 years","16 years",
         "The 61st Constitutional Amendment (1988) lowered the voting age from 21 to 18 years. Citizens aged 18+ can register as voters and participate in elections."),
        ("Our Country","Climate",
         "Which winds bring the most rainfall to India between June and September?",
         "South-West Monsoon winds","North-East Trade Winds","Western Disturbances","Polar Winds",
         "The South-West Monsoon (June-September) brings about 80% of India's annual rainfall. Moisture-laden winds from the Arabian Sea and Bay of Bengal deposit rain as they hit land."),
    ]
    for q in qs:
        add("Social Studies", 4, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# SCIENCE — Grades 6 & 7 (top-up to 15+)
# ─────────────────────────────────────────────────────────────────────────────
def gen_science_gr6_topup():
    section("Science Grade 6 — Olympiad top-up")
    qs = [
        ("Chemistry","Substances & Mixtures",
         "Salt dissolved in water forms a solution. Which property of a solution makes it DIFFERENT from a pure substance?",
         "A solution has variable composition; a pure substance has fixed composition","Solutions are always liquid","Pure substances cannot be separated","Solutions are always coloured",
         "A solution (mixture) can have any proportion of solute:solvent. Pure substances (like water, salt) have fixed, definite composition. This is the key distinction between mixtures and pure compounds."),
        ("Physics","Forces & Simple Machines",
         "A wheelbarrow is used to carry heavy loads easily. It is an example of which class of lever?",
         "Class 2 lever (load between fulcrum and effort)","Class 1 lever","Class 3 lever","Not a lever at all",
         "Wheelbarrow: Fulcrum=wheel (front), Load=in the tray (middle), Effort=handles (back). Load between fulcrum and effort = Class 2 lever. Nutcracker, bottle opener are also Class 2."),
        ("Biology","Reproduction in Plants",
         "In vegetative reproduction, a new plant grows from part of the parent plant (not a seed). Which example is CORRECT?",
         "A new potato plant from a potato tuber (eye bud)","A new plant from a seed","A new plant from pollen","A plant growing from another plant's root only",
         "Vegetative propagation: potato (tuber), ginger (rhizome), onion (bulb), strawberry (runner/stolon), money plant (stem cutting). These reproduce without seeds."),
        ("Physics","Light & Reflection",
         "You stand 1 metre in front of a plane mirror. Your image appears to be:",
         "1 metre BEHIND the mirror (total distance 2m between you and image)","1 metre in front of the mirror","At the surface of the mirror","At an infinite distance",
         "In a plane mirror, the image is formed as far BEHIND the mirror as the object is IN FRONT. Object 1m in front -> image 1m behind. Total distance = 1+1 = 2m."),
        ("Chemistry","Changes Around Us",
         "Curd forming from milk and iron rusting are both examples of:",
         "Chemical changes (new substances formed, irreversible)","Physical changes (reversible)","Natural disasters","Biological digestion only",
         "Chemical changes: new substances form, usually irreversible. Curd (lactic acid bacteria change milk proteins). Rust (iron + oxygen -> iron oxide). Both cannot be reversed to get original materials back."),
        ("Biology","Adaptations",
         "Fish have streamlined bodies and gills. What is the PURPOSE of gills?",
         "Extract dissolved oxygen from water for respiration","Filter food from water","Help in swimming movement","Store food underwater",
         "Gills are highly vascularised organs that extract dissolved O2 from water as water flows over them. This allows fish to breathe underwater without coming to the surface."),
        ("Physics","Electricity",
         "In an electric circuit, what is the function of a SWITCH?",
         "To open or close the circuit (control current flow)","To generate electricity","To store electricity","To measure voltage",
         "A switch breaks or completes a circuit. Open switch = circuit broken = no current. Closed switch = circuit complete = current flows. Essential for controlling devices safely."),
        ("Chemistry","Air & Its Components",
         "About 78% of air is nitrogen. Why is nitrogen important for living things despite being inert (not directly breathable)?",
         "Nitrogen is essential for making proteins and DNA — plants absorb it through soil bacteria and fertilisers","Nitrogen is breathed directly by animals","Nitrogen provides energy like oxygen","Nitrogen is not important at all",
         "Though we cannot breathe N2 directly, nitrogen is a building block of amino acids (proteins) and nucleic acids (DNA/RNA). Nitrogen-fixing bacteria convert atmospheric N2 into usable forms for plants."),
        ("Biology","Food & Nutrition",
         "A person who eats no fruits or vegetables and only rice and bread develops bleeding gums and fatigue. This deficiency disease is called:",
         "Scurvy (Vitamin C deficiency)","Rickets (Vitamin D deficiency)","Anaemia (Iron deficiency)","Goitre (Iodine deficiency)",
         "Scurvy is caused by Vitamin C (ascorbic acid) deficiency. Symptoms: bleeding gums, fatigue, joint pain. Vitamin C is essential for collagen synthesis and immune function. Source: citrus fruits, amla."),
        ("Physics","Motion & Measurement",
         "A car travels 120 km in 2 hours. What is its average speed?",
         "60 km/h","240 km/h","30 km/h","120 km/h",
         "Average speed = Total distance / Total time = 120 km / 2 hours = 60 km/h."),
    ]
    for q in qs:
        add("Science", 6, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

def gen_science_gr7_topup():
    section("Science Grade 7 — Olympiad top-up")
    qs = [
        ("Chemistry","Acids, Bases & Salts",
         "When an acid reacts with a base, the products are always:",
         "Salt and water (neutralisation reaction)","Acid and gas","New acid only","Metal and hydrogen",
         "Neutralisation: Acid + Base -> Salt + Water. HCl + NaOH -> NaCl + H2O. This is always the pattern. The pH moves towards 7."),
        ("Biology","Nutrition in Plants",
         "Insectivorous plants (like Venus flytrap) grow in nitrogen-poor soil and eat insects. This is because they need nitrogen for:",
         "Making proteins and chlorophyll","Making glucose via photosynthesis","Absorbing water","Producing oxygen",
         "All living things need nitrogen for proteins and nucleic acids. Where soil is deficient in nitrogen (like bogs), insectivorous plants evolved to digest insects as a nitrogen source."),
        ("Physics","Heat & Temperature",
         "A metal spoon left in hot soup gets hot, while a wooden spoon stays cool. This is because:",
         "Metals are good thermal conductors; wood is a poor conductor (insulator)","Metal spoons are longer","Wood is cooler than metal naturally","Soup only heats metal",
         "Thermal conductivity: metals have free electrons that transfer heat energy rapidly. Wood has no free electrons — it is an insulator. This is why metal utensils are hot but wooden handles stay cool."),
        ("Chemistry","Fibre to Fabric",
         "Silk is a natural fibre obtained from the cocoon of which insect?",
         "Silkworm (Bombyx mori)","Honeybee","Spider","Beetle",
         "Silk is produced by silkworms (Bombyx mori larvae) as they spin their cocoons. One cocoon can yield up to 1 km of silk thread. This process is called sericulture."),
        ("Biology","Respiration",
         "During vigorous exercise, muscles produce lactic acid because:",
         "Oxygen supply is insufficient, so anaerobic respiration occurs — glucose -> lactic acid + energy","Muscles make extra glucose","Lactic acid gives more energy than oxygen","The heart pumps less blood during exercise",
         "During intense exercise, muscles need more O2 than the blood can supply. Anaerobic respiration kicks in: glucose -> lactic acid + ATP (less energy). Lactic acid build-up causes the burning sensation in muscles."),
        ("Physics","Electric Current",
         "Three bulbs connected in SERIES to a battery. If one bulb breaks, what happens?",
         "All bulbs go out — the circuit is broken","Only the broken bulb goes out","The other two glow brighter","Nothing changes",
         "In series circuits, components share one path. If any component breaks = open circuit = no current anywhere = all bulbs go out. Old Christmas lights were series — one bulb failing caused all to go out."),
        ("Chemistry","Water",
         "Hard water doesn't lather well with soap. Hard water contains dissolved salts of:",
         "Calcium and magnesium","Sodium and potassium","Iron and copper","Gold and silver",
         "Hard water contains dissolved Ca2+ and Mg2+ ions (from limestone/chalk). These react with soap to form scum (insoluble calcium stearate) instead of lather. Soft water lathers easily."),
        ("Biology","Forest & Wildlife",
         "Decomposers (fungi and bacteria) are essential in a forest ecosystem because they:",
         "Break down dead organisms and return nutrients to the soil, completing the nutrient cycle","Produce food via photosynthesis","Are the top predators in the food chain","Only harm other organisms",
         "Decomposers are nature's recyclers. Without them, dead matter would pile up and nutrients (nitrogen, carbon) would not be returned to soil for plants to use. They are essential for ecosystem sustainability."),
        ("Physics","Sound & Light",
         "We see lightning before we hear thunder because:",
         "Light travels much faster than sound (3×10^8 m/s vs 340 m/s in air)","Thunder is produced after lightning","Our eyes are more sensitive than ears","Thunder travels underground",
         "Speed of light ≈ 300,000,000 m/s. Speed of sound ≈ 340 m/s. Light reaches us almost instantly; sound takes ~3 seconds per km. The delay between flash and thunder tells us the storm's distance."),
        ("Chemistry","Physical & Chemical Changes",
         "Which of these is a PHYSICAL change (no new substance formed)?",
         "Melting of ice into water","Burning of wood","Milk turning sour","Iron rusting",
         "Melting ice: H2O(solid) -> H2O(liquid). Same substance (water), just change of state — reversible physical change. Burning, souring, rusting all produce NEW substances = chemical changes."),
    ]
    for q in qs:
        add("Science", 7, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GK — Grades 5, 7, 10 top-up
# ─────────────────────────────────────────────────────────────────────────────
def gen_gk_gr5_topup():
    section("General Knowledge Grade 5 — Olympiad top-up")
    qs = [
        ("India","Geography",
         "Cape Comorin (Kanyakumari) is the southernmost tip of mainland India. It is where three large water bodies meet. Which three?",
         "Bay of Bengal, Arabian Sea, Indian Ocean","Pacific Ocean, Atlantic Ocean, Indian Ocean","Bay of Bengal, Arabian Sea, Red Sea","Indian Ocean, Pacific Ocean, Arabian Sea",
         "Kanyakumari is the unique meeting point of three large water bodies: Bay of Bengal (east), Arabian Sea (west), and Indian Ocean (south). It is a famous pilgrimage and tourist site."),
        ("World","Famous Scientists",
         "Who developed the Theory of General Relativity, which changed our understanding of gravity and space-time?",
         "Albert Einstein","Isaac Newton","Stephen Hawking","Nikola Tesla",
         "Albert Einstein published the Theory of General Relativity in 1915. It describes gravity as the curvature of space-time caused by mass, replacing Newton's classical gravity for extreme conditions."),
        ("India","Awards",
         "The Nobel Prize for Physics in 1930 was awarded to an Indian scientist for the 'Raman Effect'. Who was he?",
         "C.V. Raman","Homi Bhabha","Vikram Sarabhai","S.N. Bose",
         "Sir C.V. Raman won the 1930 Nobel Prize in Physics for discovering the Raman Effect — the scattering of light by molecules that shifts its wavelength. He was the first Asian Nobel laureate in science."),
        ("World","Records & Facts",
         "Which is the smallest country in the world by area?",
         "Vatican City","Monaco","San Marino","Liechtenstein",
         "Vatican City (0.44 km²) in Rome is the world's smallest country by area. It is the headquarters of the Roman Catholic Church and home to the Pope."),
        ("India","Environment",
         "Project Snow Leopard was launched to protect the snow leopard in which region of India?",
         "Himalayan and Trans-Himalayan regions","Western Ghats","Sundarbans","Andaman Islands",
         "Project Snow Leopard (2009) focuses on conserving the elusive snow leopard in India's Himalayan states: Jammu & Kashmir, Himachal Pradesh, Uttarakhand, Sikkim, and Arunachal Pradesh."),
        ("World","History",
         "The first man to walk on the Moon was Neil Armstrong during which mission?",
         "Apollo 11 (1969)","Apollo 13 (1970)","Gemini 7 (1965)","Sputnik 1 (1957)",
         "Neil Armstrong and Buzz Aldrin landed on the Moon on 20 July 1969 during NASA's Apollo 11 mission. Armstrong's famous words: 'That's one small step for man, one giant leap for mankind.'"),
        ("India","Culture & Heritage",
         "The UNESCO Intangible Cultural Heritage list includes Indian classical dance. Which dance form from Odisha is on this list?",
         "Odissi","Bharatanatyam","Kathak","Manipuri",
         "Odissi is one of the oldest classical dance forms, originating from temple rituals in Odisha. It has been recognised by UNESCO. Other Indian art forms on UNESCO lists include Vedic chanting and Yoga."),
        ("World","Science & Technology",
         "The first artificial satellite launched into space was Sputnik 1. Which country launched it and in what year?",
         "Soviet Union (USSR) in 1957","USA in 1957","France in 1958","India in 1975",
         "The USSR launched Sputnik 1 on 4 October 1957, marking the start of the Space Age. It orbited Earth every 98 minutes for 3 weeks before its battery died. This triggered the Space Race."),
    ]
    for q in qs:
        add("General Knowledge", 5, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

def gen_gk_gr7_topup():
    section("General Knowledge Grade 7 — Olympiad top-up")
    qs = [
        ("India","History",
         "The Battle of Panipat in 1526 was fought between Babur and Ibrahim Lodi. Its significance is that it:",
         "Established the Mughal Empire in India","Ended British rule in India","Started the Maratha Empire","Was the first Indian independence war",
         "The First Battle of Panipat (1526) saw Babur defeat Ibrahim Lodi (Delhi Sultanate), marking the end of the Delhi Sultanate and the beginning of Mughal rule in India."),
        ("World","Geography",
         "The Great Barrier Reef, the world's largest coral reef system, is located off the coast of which country?",
         "Australia","Brazil","Indonesia","Philippines",
         "The Great Barrier Reef stretches ~2,300 km along Queensland, Australia's northeast coast. It is the world's largest coral reef system and a UNESCO World Heritage Site, visible from space."),
        ("Science","Inventions",
         "The World Wide Web was invented by Tim Berners-Lee in 1989. He worked at which international organisation?",
         "CERN (European Organisation for Nuclear Research)","NASA","MIT","IBM",
         "Tim Berners-Lee invented the Web in 1989 while working at CERN in Geneva, Switzerland. He proposed it as a way to share information between physicists across the world."),
        ("India","Politics & Current Affairs",
         "India's Uniform Civil Code (UCC) would mean:",
         "One set of civil laws (marriage, divorce, inheritance) for all citizens regardless of religion","Uniform dress code for all citizens","Same income tax for all","Uniform school curriculum",
         "UCC would replace religion-specific personal laws (Hindu Marriage Act, Muslim Personal Law, etc.) with a common civil code for all citizens. It is mentioned in Article 44 of the Directive Principles."),
        ("World","Economics",
         "GDP stands for Gross Domestic Product. A country's GDP measures:",
         "The total monetary value of all goods and services produced within a country in a year","Only industrial output","Only agricultural production","The wealth of the richest citizens",
         "GDP is the broadest measure of a country's economic activity — total value of everything produced (goods + services) within national borders in one year. India is currently the 5th largest economy by GDP."),
        ("World","Science",
         "Black holes were first theorised by Einstein's General Relativity. The first real image of a black hole was captured in 2019. It was a black hole in which galaxy?",
         "Messier 87 (M87)","Milky Way","Andromeda","Triangulum",
         "The Event Horizon Telescope (EHT) captured the first image of a black hole in April 2019 — the supermassive black hole at the centre of Messier 87 galaxy, 55 million light-years away."),
        ("India","Environment",
         "The Chipko Movement (1973) in Uttarakhand was significant because:",
         "Villagers hugged trees to prevent them from being cut — it became a landmark environmental movement","It was a movement to plant new trees","Chipko means 'to build' in Hindi","It was an anti-dam protest",
         "Chipko (meaning 'to hug/stick') saw Garhwali women embrace trees to prevent logging. Led by Sundarlal Bahuguna and Chandi Prasad Bhatt, it inspired global environmental movements and led to forest protection policies."),
        ("World","Sports",
         "The FIFA World Cup is held every how many years, and how many teams participate in the final tournament?",
         "Every 4 years; 32 teams (48 from 2026)","Every 2 years; 16 teams","Every 4 years; 16 teams","Every 2 years; 32 teams",
         "FIFA World Cup: held every 4 years. The 2022 Qatar World Cup had 32 teams. From 2026 (USA/Canada/Mexico), it expands to 48 teams. Brazil has the most wins (5 titles)."),
        ("India","Science & Space",
         "India's Mars Orbiter Mission (Mangalyaan) made India the first country to successfully reach Mars orbit on its FIRST attempt in:",
         "2014","2012","2016","2019",
         "Mangalyaan (Mars Orbiter Mission) was launched on 5 November 2013 and entered Mars orbit on 24 September 2014. India became the first country to succeed on its maiden Mars mission and at the lowest cost ($74 million)."),
        ("World","Famous People",
         "Nelson Mandela spent 27 years in prison before becoming South Africa's first Black president. He fought against:",
         "Apartheid (racial segregation and discrimination in South Africa)","British colonial rule","Nuclear weapons","Military dictatorship",
         "Apartheid was South Africa's official policy of racial segregation (1948-1994). Nelson Mandela led the ANC against it, was imprisoned 1964-1990, and became South Africa's first Black president in 1994."),
    ]
    for q in qs:
        add("General Knowledge", 7, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

def gen_gk_gr10_topup():
    section("General Knowledge Grade 10 — Olympiad top-up")
    qs = [
        ("India","Economy",
         "The Nifty 50 and Sensex are stock market indices. Sensex is based on which stock exchange?",
         "Bombay Stock Exchange (BSE)","National Stock Exchange (NSE)","Delhi Stock Exchange","Calcutta Stock Exchange",
         "Sensex (Sensitive Index) tracks 30 large-cap companies on the Bombay Stock Exchange (BSE), Asia's oldest exchange (est. 1875). Nifty 50 tracks 50 companies on the NSE."),
        ("World","Science & Technology",
         "The Large Hadron Collider (LHC) at CERN discovered the Higgs Boson in 2012. The Higgs Boson is significant because:",
         "It confirms the mechanism that gives particles their mass (the Higgs field) — completing the Standard Model of physics","It is the fastest particle known","It enables faster-than-light travel","It is identical to an electron",
         "The Higgs Boson (nicknamed 'God Particle') was the last missing piece of the Standard Model. Its discovery confirmed the Higgs field, which gives particles mass. Discoverers Peter Higgs and Francois Englert won the 2013 Nobel Prize."),
        ("India","Defence & Security",
         "Operation Shakti (1998) refers to:",
         "India's nuclear tests at Pokhran, Rajasthan","India's military operation in Kargil","A naval exercise in the Indian Ocean","India's missile defence system launch",
         "Operation Shakti (Pokhran-II) was India's series of five nuclear tests on 11-13 May 1998 at Pokhran, Rajasthan. It made India a declared nuclear weapons state and led to international sanctions."),
        ("World","Environment",
         "The Montreal Protocol (1987) is an international treaty that successfully reduced:",
         "Ozone-depleting substances (CFCs, HCFCs) to protect the ozone layer","Carbon dioxide emissions","Plastic pollution in oceans","Nuclear weapons testing",
         "The Montreal Protocol (1987, in force 1989) is considered the most successful environmental treaty — it phased out CFCs and other ozone-depleting substances. The ozone layer is recovering as a result."),
        ("India","Judiciary",
         "The Supreme Court of India has the power of 'Judicial Review'. This means it can:",
         "Strike down any law passed by Parliament if it violates the Constitution","Only advise Parliament on laws","Override the President's decisions","Create new laws directly",
         "Judicial review allows courts to examine the constitutional validity of legislation. If a law violates Fundamental Rights or constitutional provisions, the Supreme Court can declare it void. This is a key check on legislative power."),
        ("World","Technology",
         "Artificial Intelligence (AI) systems like ChatGPT use Large Language Models (LLMs). These models are trained using:",
         "Vast amounts of text data from the internet, processed using deep learning neural networks","Simple if-then rule systems","Human experts typing responses manually","Pre-written encyclopaedias only",
         "LLMs (GPT, LLaMA, Gemini) use deep learning (transformer architecture) trained on trillions of words of text. They learn statistical patterns in language rather than being explicitly programmed with rules."),
        ("India","Current Affairs",
         "The G20 Summit was hosted by India in 2023 in which city, under what theme?",
         "New Delhi; 'Vasudhaiva Kutumbakam — One Earth, One Family, One Future'","Mumbai; 'Digital India'","Bengaluru; 'Innovation for All'","Chennai; 'Inclusive Growth'",
         "India hosted the G20 Summit in New Delhi (9-10 September 2023) under PM Modi's presidency. The theme was 'Vasudhaiva Kutumbakam' (the world is one family), from the Maha Upanishad. India achieved the African Union's inclusion in G20."),
        ("World","Sports",
         "In cricket, which record does Sachin Tendulkar hold that remains unbroken?",
         "Most international centuries (100) and most runs in international cricket","Most Test wickets","Most ODI wickets","Most Test matches as captain",
         "Sachin Tendulkar holds the records for: most international centuries (100 — 51 in Tests, 49 in ODIs) and most international runs (34,357). These records were achieved across a 24-year career (1989-2013)."),
    ]
    for q in qs:
        add("General Knowledge", 10, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  OlympiadReady — Zero Olympiad Slot Fill")
    print("=" * 60)

    gen_cs_gr4()
    gen_eng_gr1()
    gen_eng_gr4()
    gen_gk_gr4()
    gen_hindi_gr4()
    gen_math_gr1()
    gen_science_gr1()
    gen_sst_gr4()
    gen_science_gr6_topup()
    gen_science_gr7_topup()
    gen_gk_gr5_topup()
    gen_gk_gr7_topup()
    gen_gk_gr10_topup()

    print(f"\n{'='*60}")
    print(f"DONE -- Posted: {POSTED}  Skipped(dup): {SKIPPED}  Failed: {FAILED}")
    print(f"{'='*60}")
