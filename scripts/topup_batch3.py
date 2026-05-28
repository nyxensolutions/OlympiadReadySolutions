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
# CS G6 Foundation (+10) — basic hardware/software/internet concepts
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Input Devices",
 "questionText":"Which of the following is an INPUT device?",
 "options":["A: Monitor","B: Speaker","C: Keyboard","D: Printer"],"correctAnswer":"C",
 "explanation":"A keyboard is an input device — it sends data into the computer. Monitor, speaker, and printer are output devices."},

{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"CPU",
 "questionText":"The 'brain' of the computer that processes all instructions is called the:",
 "options":["A: Hard Disk","B: RAM","C: Monitor","D: CPU"],"correctAnswer":"D",
 "explanation":"The CPU (Central Processing Unit) is called the brain of the computer. It processes all instructions and data."},

{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"RAM",
 "questionText":"RAM stands for:",
 "options":["A: Read Access Memory","B: Random Access Memory","C: Real-time Application Memory","D: Remote Access Memory"],"correctAnswer":"B",
 "explanation":"RAM stands for Random Access Memory. It is the computer's temporary working memory — data in RAM is lost when the computer is switched off."},

{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Software Types",
 "questionText":"Which of the following is an APPLICATION software?",
 "options":["A: Windows Operating System","B: BIOS","C: MS Paint","D: Device Driver"],"correctAnswer":"C",
 "explanation":"MS Paint is an application software used for drawing. Windows OS, BIOS, and device drivers are system software."},

{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Internet Basics",
 "questionText":"WWW stands for:",
 "options":["A: World Wide Web","B: Wide World Web","C: World Web Window","D: Worldwide Wire Web"],"correctAnswer":"A",
 "explanation":"WWW stands for World Wide Web — a system of interlinked web pages accessible via the internet."},

{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Keyboard Shortcuts",
 "questionText":"Which keyboard shortcut is used to UNDO the last action in MS Word?",
 "options":["A: Ctrl+Y","B: Ctrl+Z","C: Ctrl+X","D: Ctrl+W"],"correctAnswer":"B",
 "explanation":"Ctrl+Z undoes the last action. Ctrl+Y redoes (opposite of undo). Ctrl+X cuts. Ctrl+W closes the document."},

{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Output Devices",
 "questionText":"A printer is an example of which type of device?",
 "options":["A: Input","B: Processing","C: Storage","D: Output"],"correctAnswer":"D",
 "explanation":"A printer produces physical output (a printed page), making it an output device."},

{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Storage",
 "questionText":"Which storage device retains data permanently even when the computer is switched off?",
 "options":["A: RAM","B: CPU Cache","C: Hard Disk","D: CPU Register"],"correctAnswer":"C",
 "explanation":"A hard disk (or SSD) stores data permanently even without power. RAM, cache, and registers lose data when power is off."},

{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Email",
 "questionText":"What does the abbreviation 'CC' stand for in an email?",
 "options":["A: Copied Contact","B: Carbon Copy","C: Certified Content","D: Common Copy"],"correctAnswer":"B",
 "explanation":"CC stands for Carbon Copy. Addresses in CC receive the email and all recipients can see them. BCC (Blind Carbon Copy) hides the recipient from others."},

{"subject":"Computer Science","grade":6,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Number Systems",
 "questionText":"How many digits are used in the binary number system?",
 "options":["A: 8","B: 10","C: 16","D: 2"],"correctAnswer":"D",
 "explanation":"The binary (base-2) number system uses only 2 digits: 0 and 1. Decimal uses 10 (0–9); hexadecimal uses 16 (0–9, A–F)."},

# ══════════════════════════════════════════════════════════════════════════════
# CS G6 Advanced (+10) — binary, networks, logic, shortcuts
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Binary Numbers",
 "questionText":"The binary number 1101 is equal to which decimal number?",
 "options":["A: 11","B: 12","C: 13","D: 14"],"correctAnswer":"C",
 "explanation":"1101 in binary = 1×8 + 1×4 + 0×2 + 1×1 = 8+4+0+1 = 13."},

{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Number Systems",
 "questionText":"Which number system uses base 16 and includes digits 0–9 and letters A–F?",
 "options":["A: Binary","B: Octal","C: Decimal","D: Hexadecimal"],"correctAnswer":"D",
 "explanation":"Hexadecimal (base-16) uses 16 symbols: 0–9 for values 0–9, and A–F for values 10–15."},

{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Spreadsheets",
 "questionText":"In MS Excel, the cell reference B3 refers to:",
 "options":["A: Row B, Column 3","B: Column B, Row 3","C: Column 3, Row 2","D: Row 2, Column B"],"correctAnswer":"B",
 "explanation":"In Excel, columns are labelled with letters (A, B, C…) and rows with numbers. B3 means Column B, Row 3."},

{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Networking",
 "questionText":"LAN stands for:",
 "options":["A: Large Area Network","B: Local Area Network","C: Long Access Network","D: Linked Area Network"],"correctAnswer":"B",
 "explanation":"LAN stands for Local Area Network — a network covering a small area like a school, home, or office building."},

{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Software",
 "questionText":"Which of the following is NOT an operating system?",
 "options":["A: Windows 11","B: Ubuntu","C: macOS","D: MS Word"],"correctAnswer":"D",
 "explanation":"MS Word is an application (word processing) software. Windows 11, Ubuntu, and macOS are all operating systems."},

{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Cybersecurity",
 "questionText":"What is the main function of a firewall?",
 "options":["A: Speed up internet browsing","B: Store data permanently","C: Block unauthorized network access","D: Convert binary to decimal numbers"],"correctAnswer":"C",
 "explanation":"A firewall monitors and controls incoming and outgoing network traffic, blocking unauthorized access while allowing legitimate communication."},

{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Flowcharts",
 "questionText":"In a flowchart, which shape is used to represent a DECISION (Yes/No question)?",
 "options":["A: Rectangle","B: Oval","C: Parallelogram","D: Diamond"],"correctAnswer":"D",
 "explanation":"Diamonds represent decision points (yes/no or true/false). Rectangles are for processes, ovals for start/end, parallelograms for input/output."},

{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Keyboard Shortcuts",
 "questionText":"Which keyboard shortcut selects ALL content in a document?",
 "options":["A: Ctrl+C","B: Ctrl+A","C: Ctrl+V","D: Ctrl+X"],"correctAnswer":"B",
 "explanation":"Ctrl+A selects all content. Ctrl+C copies, Ctrl+V pastes, Ctrl+X cuts."},

{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Memory",
 "questionText":"How many bits are in 2 bytes?",
 "options":["A: 8","B: 12","C: 16","D: 4"],"correctAnswer":"C",
 "explanation":"1 byte = 8 bits. Therefore 2 bytes = 2 × 8 = 16 bits."},

{"subject":"Computer Science","grade":6,"difficulty":"Advanced","topic":"Computer Science","subTopic":"User Interface",
 "questionText":"GUI stands for:",
 "options":["A: General User Input","B: Graphical User Interface","C: Global Unified Interface","D: Generic Utility Interface"],"correctAnswer":"B",
 "explanation":"GUI stands for Graphical User Interface — a visual interface using icons, windows, and menus (like Windows desktop), as opposed to a text-based command-line interface."},

# ══════════════════════════════════════════════════════════════════════════════
# CS G6 Olympiad (+10) — advanced binary, logic gates, networks, programming
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"Binary Numbers",
 "questionText":"What is the decimal value of binary 11111111?",
 "options":["A: 254","B: 255","C: 256","D: 128"],"correctAnswer":"B",
 "explanation":"11111111 = 128+64+32+16+8+4+2+1 = 255. This is the maximum value of an 8-bit (1-byte) unsigned integer."},

{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"Python Keywords",
 "questionText":"Which of the following is a reserved KEYWORD in Python 3?",
 "options":["A: name","B: value","C: while","D: number"],"correctAnswer":"C",
 "explanation":"'while' is a reserved keyword used for loops in Python. 'name', 'value', and 'number' are valid variable names, not reserved keywords."},

{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"Internet Protocols",
 "questionText":"What does HTTP stand for?",
 "options":["A: HyperText Transfer Protocol","B: High Transfer Text Protocol","C: Hyperlink Text Transmission Process","D: HyperText Transmission Procedure"],"correctAnswer":"A",
 "explanation":"HTTP stands for HyperText Transfer Protocol — the protocol used to transfer web pages over the internet. HTTPS adds 'Secure' (encrypted)."},

{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"Logic Gates",
 "questionText":"For an AND gate, when is the output 1?",
 "options":["A: When both inputs are 0","B: When at least one input is 1","C: When both inputs are 1","D: When exactly one input is 1"],"correctAnswer":"C",
 "explanation":"AND gate output is 1 ONLY when ALL inputs are 1. Truth table: 0·0=0, 0·1=0, 1·0=0, 1·1=1."},

{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"Cybersecurity",
 "questionText":"What is 'phishing'?",
 "options":["A: A type of computer virus that deletes files","B: Tricking users into revealing sensitive info via fake emails or websites","C: Directly breaking into a server's database","D: Sending millions of spam emails to slow a server"],"correctAnswer":"B",
 "explanation":"Phishing uses deceptive emails or websites that impersonate trusted organisations to steal passwords, credit card numbers, or other sensitive data."},

{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"ASCII",
 "questionText":"ASCII stands for:",
 "options":["A: American Standard Code for Information Interchange","B: American System Code for Internet Interchange","C: Automated Standard Code for Information Input","D: Advanced Standard Code for Internet Interface"],"correctAnswer":"A",
 "explanation":"ASCII (American Standard Code for Information Interchange) is a character encoding standard that assigns numbers 0–127 to letters, digits, and symbols."},

{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"Pseudocode",
 "questionText":"What is the output of this pseudocode?\nX ← 5\nY ← 3\nX ← X + Y\nPRINT X",
 "options":["A: 5","B: 3","C: 8","D: 15"],"correctAnswer":"C",
 "explanation":"X starts as 5. X ← X + Y = 5 + 3 = 8. PRINT X outputs 8."},

{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"Network Topology",
 "questionText":"Which network topology connects all devices to a single central hub or switch?",
 "options":["A: Ring topology","B: Mesh topology","C: Bus topology","D: Star topology"],"correctAnswer":"D",
 "explanation":"In star topology, every device connects to a central hub/switch. If the hub fails, all devices lose connectivity — but individual device failures don't affect others."},

{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"Display",
 "questionText":"The sharpness (resolution) of a monitor image is measured in:",
 "options":["A: Megabytes","B: Hertz","C: Pixels","D: Watts"],"correctAnswer":"C",
 "explanation":"Screen resolution is expressed in pixels (e.g., 1920×1080). More pixels = sharper image. Hertz measures refresh rate; megabytes measures data size; watts measures power."},

{"subject":"Computer Science","grade":6,"difficulty":"Olympiad","topic":"Computer Science","subTopic":"Programming Concepts",
 "questionText":"What does 'debugging' mean in programming?",
 "options":["A: Writing new features in code","B: Testing software for speed","C: Finding and fixing errors (bugs) in code","D: Compressing the program file"],"correctAnswer":"C",
 "explanation":"Debugging is the process of identifying, locating, and fixing errors (bugs) in a program. The term originated when Grace Hopper found an actual moth causing a computer malfunction in 1947."},

# ══════════════════════════════════════════════════════════════════════════════
# SS G6 Advanced (+10) — NCERT Our Pasts I, Earth Habitat, Social & Political Life I
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Harappan Civilisation",
 "questionText":"Which of the following was a distinctive feature of Harappan cities?",
 "options":["A: Large pyramid-shaped temples","B: Well-planned drainage and sewage systems","C: Underground fortresses","D: Nomadic tent settlements"],"correctAnswer":"B",
 "explanation":"Harappan cities like Mohenjo-daro and Harappa had sophisticated, covered drainage systems running through streets — more advanced than most ancient civilisations."},

{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Ashoka",
 "questionText":"Ashoka's edicts (inscriptions) were written in which script?",
 "options":["A: Devanagari","B: Sanskrit","C: Brahmi","D: Persian"],"correctAnswer":"C",
 "explanation":"Most of Ashoka's rock and pillar edicts were inscribed in Prakrit language using the Brahmi script. Some edicts in the northwest used Kharoshthi script."},

{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Vedic Period",
 "questionText":"The Vedas, the oldest scriptures of Hinduism, are written in which language?",
 "options":["A: Pali","B: Prakrit","C: Sanskrit","D: Tamil"],"correctAnswer":"C",
 "explanation":"The Vedas (Rigveda, Samaveda, Yajurveda, Atharvaveda) are composed in Vedic Sanskrit, the oldest form of the Sanskrit language."},

{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Mahajanapadas",
 "questionText":"The Mahajanapadas were large territorial kingdoms that emerged around which period?",
 "options":["A: Around 3000 BCE","B: Around 600 BCE","C: Around 300 BCE","D: Around 100 CE"],"correctAnswer":"B",
 "explanation":"The sixteen Mahajanapadas (great kingdoms) emerged around 600 BCE in the subcontinent, coinciding with the rise of Buddhism and Jainism. Magadha became the most powerful among them."},

{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Panchayati Raj",
 "questionText":"Panchayati Raj is a system of:",
 "options":["A: Urban local government","B: Central government administration of states","C: Rural local self-government","D: State legislature"],"correctAnswer":"C",
 "explanation":"Panchayati Raj is India's three-tier system of rural local self-government (Gram Panchayat → Panchayat Samiti → Zila Parishad), constitutionally mandated by the 73rd Amendment (1992)."},

{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Latitudes",
 "questionText":"Which Indian state does the Tropic of Cancer pass through?",
 "options":["A: Kerala","B: Rajasthan","C: Tamil Nadu","D: Andhra Pradesh"],"correctAnswer":"B",
 "explanation":"The Tropic of Cancer (23.5°N) passes through Gujarat, Rajasthan, Madhya Pradesh, Chhattisgarh, Jharkhand, West Bengal, Tripura, and Mizoram. Kerala and Tamil Nadu are too far south."},

{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Earth's Domains",
 "questionText":"The term 'lithosphere' refers to:",
 "options":["A: The layer of gases surrounding the Earth","B: All water bodies on Earth","C: The solid rocky outer layer of the Earth","D: All living organisms on Earth"],"correctAnswer":"C",
 "explanation":"Lithosphere = solid outer crust and upper mantle. Atmosphere = gases. Hydrosphere = water bodies. Biosphere = all living organisms."},

{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Early Agriculture",
 "questionText":"Which crops were among the FIRST to be cultivated by early humans?",
 "options":["A: Rice and sugarcane","B: Barley and wheat","C: Cotton and jute","D: Tea and coffee"],"correctAnswer":"B",
 "explanation":"Barley and wheat were among the earliest crops cultivated (~10,000 BCE) in the Fertile Crescent (modern-day Middle East). This was a key step in the Neolithic Revolution."},

{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Urban Administration",
 "questionText":"A 'Municipality' is responsible for governing:",
 "options":["A: Villages and rural areas","B: Small and medium towns","C: The entire state","D: Union Territories only"],"correctAnswer":"B",
 "explanation":"A Municipality (Nagar Panchayat or Municipal Council) governs small/medium towns. A Municipal Corporation governs large cities. Gram Panchayats govern villages."},

{"subject":"Social Studies","grade":6,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Rural Livelihoods",
 "questionText":"The main occupation of the majority of people in rural India is:",
 "options":["A: Manufacturing in factories","B: Trade and commerce","C: Agriculture and related activities","D: Information technology"],"correctAnswer":"C",
 "explanation":"Agriculture is the primary occupation in rural India, employing the majority of the rural workforce either directly (farming) or indirectly (dairy, fishing, forestry)."},

# ══════════════════════════════════════════════════════════════════════════════
# SS G7 Advanced (+10) — NCERT Our Pasts II, Our Environment, Social & Political Life II
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Mughal Empire",
 "questionText":"Which Mughal emperor built the Taj Mahal?",
 "options":["A: Akbar","B: Humayun","C: Shah Jahan","D: Aurangzeb"],"correctAnswer":"C",
 "explanation":"Shah Jahan built the Taj Mahal (1631–1648) at Agra as a mausoleum for his wife Mumtaz Mahal. It is now a UNESCO World Heritage Site."},

{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Mughal Administration",
 "questionText":"The official language of the Mughal court was:",
 "options":["A: Hindi","B: Urdu","C: Persian","D: Arabic"],"correctAnswer":"C",
 "explanation":"Persian was the official language of the Mughal Empire — used for administration, diplomacy, and literature. Urdu emerged later as a blend of Persian with local languages."},

{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Delhi Sultanate",
 "questionText":"The Delhi Sultanate was established in which year?",
 "options":["A: 1000 CE","B: 1100 CE","C: 1206 CE","D: 1526 CE"],"correctAnswer":"C",
 "explanation":"Qutb-ud-din Aibak founded the Delhi Sultanate in 1206 CE after the death of Muhammad of Ghor. It ruled until 1526 CE when Babur defeated Ibrahim Lodi at the First Battle of Panipat."},

{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Bhakti Movement",
 "questionText":"The Bhakti movement originated in which part of India?",
 "options":["A: Northern India (Punjab)","B: Eastern India (Bengal)","C: Southern India (Tamil Nadu)","D: Western India (Gujarat)"],"correctAnswer":"C",
 "explanation":"The Bhakti movement originated in South India (Tamil Nadu) around the 6th–7th centuries CE with Tamil poet-saints called the Alvars (Vishnu devotees) and Nayanars (Shiva devotees)."},

{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Akbar's Policies",
 "questionText":"Akbar abolished the 'jizya' tax in 1564. This tax was:",
 "options":["A: A tax on imported goods","B: A tax levied on non-Muslims in a Muslim-ruled state","C: A tax on agricultural produce","D: A trade tax for crossing rivers"],"correctAnswer":"B",
 "explanation":"Jizya was a poll tax imposed on non-Muslim subjects in Islamic states. Akbar abolished it to promote religious tolerance and harmony, reflecting his policy of sulh-i-kul (universal peace)."},

{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Medieval Scholars",
 "questionText":"Al-Biruni, who wrote the famous 'Kitab-ul-Hind' (a detailed account of India), came to India with:",
 "options":["A: Babur","B: Mahmud of Ghazni","C: Muhammad of Ghor","D: Timur"],"correctAnswer":"B",
 "explanation":"Al-Biruni (973–1048 CE) accompanied Mahmud of Ghazni on his campaigns and spent years studying India. His book Kitab-ul-Hind is a landmark in cross-cultural scholarship."},

{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Water Cycle",
 "questionText":"The water cycle is also scientifically known as the:",
 "options":["A: Carbon cycle","B: Nitrogen cycle","C: Hydrological cycle","D: Oxygen cycle"],"correctAnswer":"C",
 "explanation":"The water cycle describes the continuous movement of water through evaporation, condensation, and precipitation. Its scientific name is the Hydrological cycle (from Greek 'hydro' = water)."},

{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Forests",
 "questionText":"Which type of forest is found near the equator and receives heavy rainfall throughout the year?",
 "options":["A: Temperate evergreen forest","B: Tropical rainforest","C: Boreal (Taiga) forest","D: Mediterranean shrubland"],"correctAnswer":"B",
 "explanation":"Tropical rainforests (like the Amazon) grow near the equator. They receive 250+ cm of rainfall annually and have extraordinary biodiversity."},

{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"Indian Secularism",
 "questionText":"The word 'secular' in the Indian Constitution means that India:",
 "options":["A: Has Hinduism as the state religion","B: Does not have an official state religion — the government treats all religions equally","C: Recognises only Hinduism and Islam","D: Prohibits citizens from practising religion"],"correctAnswer":"B",
 "explanation":"India is a secular state: the government does not officially favour or fund any religion. All citizens are free to practise their own faith, and the state is neutral on religious matters."},

{"subject":"Social Studies","grade":7,"difficulty":"Advanced","topic":"Social Studies","subTopic":"State Government",
 "questionText":"The head of the government in an Indian state is the:",
 "options":["A: Governor","B: Chief Minister","C: President","D: Prime Minister"],"correctAnswer":"B",
 "explanation":"The Chief Minister is the head of the state government (elected, executive head). The Governor is the constitutional head of the state (appointed by the President, like a state-level President)."},

# ══════════════════════════════════════════════════════════════════════════════
# GK G9 Olympiad (+10, currently 15 → 25) — tough, broad GK for Grade 9
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Nobel Prize — Science",
 "questionText":"Albert Einstein received the Nobel Prize in Physics in 1921. It was awarded for:",
 "options":["A: Theory of Special Relativity","B: Theory of General Relativity","C: Discovery of nuclear fission","D: Discovery of the photoelectric effect"],"correctAnswer":"D",
 "explanation":"Surprisingly, Einstein's Nobel was NOT for relativity. It was awarded for his explanation of the photoelectric effect (light quanta), which laid foundations for quantum mechanics."},

{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Chemistry — Elements",
 "questionText":"Which element is a liquid at room temperature (other than mercury)?",
 "options":["A: Phosphorus","B: Bromine","C: Iodine","D: Gallium"],"correctAnswer":"B",
 "explanation":"Bromine (Br, atomic number 35) is the only non-metal liquid at room temperature. Mercury (Hg) is the only liquid metal. Gallium melts just above room temperature at 29.76°C."},

{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Space Exploration",
 "questionText":"The world's first artificial satellite, Sputnik 1, was launched in 1957 by:",
 "options":["A: USA","B: China","C: Soviet Union","D: United Kingdom"],"correctAnswer":"C",
 "explanation":"The Soviet Union launched Sputnik 1 on 4 October 1957, beginning the Space Age. It was the first human-made object to orbit Earth."},

{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Genetics",
 "questionText":"The Human Genome Project, which mapped all human genes, was declared complete in:",
 "options":["A: 1990","B: 2000","C: 2003","D: 2010"],"correctAnswer":"C",
 "explanation":"The Human Genome Project was completed in April 2003 (draft sequence in 2001). It identified ~20,000–25,000 human genes and sequenced the ~3 billion base pairs of human DNA."},

{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Geology",
 "questionText":"'Pangaea' was:",
 "options":["A: The first permanent human settlement on Earth","B: An ancient supercontinent that existed ~300 million years ago before breaking apart","C: The name of the prehistoric ocean surrounding all land","D: Alfred Wegener's theory of plate tectonics"],"correctAnswer":"B",
 "explanation":"Pangaea (Greek for 'all land') was the supercontinent that existed ~335–175 million years ago. It broke into Laurasia (northern) and Gondwana (southern) and eventually the current continents."},

{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Indian History",
 "questionText":"The Battle of Plassey (1757) was fought between the British East India Company and:",
 "options":["A: Hyder Ali of Mysore","B: The Maratha Confederacy","C: Siraj ud-Daulah, Nawab of Bengal","D: Tipu Sultan of Mysore"],"correctAnswer":"C",
 "explanation":"The Battle of Plassey (23 June 1757) was fought between the British EIC (Robert Clive) and Siraj ud-Daulah, the last independent Nawab of Bengal. British victory established their dominance in India."},

{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Astronomy",
 "questionText":"On which planet is a DAY longer than a YEAR?",
 "options":["A: Mercury","B: Mars","C: Venus","D: Jupiter"],"correctAnswer":"C",
 "explanation":"Venus rotates so slowly (243 Earth days per rotation) that its day is longer than its year (225 Earth days per orbit of the Sun). It also rotates backwards (retrograde) compared to most planets."},

{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Human Body",
 "questionText":"The smallest bone in the human body is the:",
 "options":["A: Patella (kneecap)","B: Stapes (in the ear)","C: Coccyx (tailbone)","D: Phalanx (finger bone)"],"correctAnswer":"B",
 "explanation":"The stapes is one of three ossicles (tiny bones) in the middle ear, measuring about 3 mm. It transmits sound vibrations to the inner ear."},

{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Technology",
 "questionText":"Silicon Valley, the global hub for technology companies, is located in which US state?",
 "options":["A: New York","B: Texas","C: California","D: Washington"],"correctAnswer":"C",
 "explanation":"Silicon Valley is in the San Francisco Bay Area, California. It is home to tech giants like Apple, Google, Meta, Intel, and hundreds of startups. Named after silicon used in semiconductors."},

{"subject":"General Knowledge","grade":9,"difficulty":"Olympiad","topic":"General Knowledge","subTopic":"Chemistry",
 "questionText":"Fluorine is the most electronegative element in the periodic table. Its atomic number is:",
 "options":["A: 7","B: 8","C: 9","D: 17"],"correctAnswer":"C",
 "explanation":"Fluorine (F) has atomic number 9 (9 protons). It is in Group 17 (halogens) and Period 2. Its high electronegativity (3.98 on Pauling scale) makes it the most reactive non-metal."},

# ══════════════════════════════════════════════════════════════════════════════
# G12 LR Advanced (+10, currently 21 → 31)
# ══════════════════════════════════════════════════════════════════════════════
{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Syllogisms",
 "questionText":"Statements: All managers are leaders. No politician is a manager. Some politicians are leaders.\nWhich conclusion definitely follows?",
 "options":["A: Some leaders are not managers","B: All leaders are politicians","C: Some managers are politicians","D: All politicians are leaders"],"correctAnswer":"A",
 "explanation":"Since some politicians are leaders (Stmt 3) AND no politician is a manager (Stmt 2), those politicians who are leaders must be leaders who are NOT managers. Hence 'Some leaders are not managers' is definitely true."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Direction Sense",
 "questionText":"A man walks 4 km North, then 3 km East, then 4 km South, then 3 km West. How far is he from his starting point?",
 "options":["A: 4 km","B: 10 km","C: 0 km (back at start)","D: 6 km"],"correctAnswer":"C",
 "explanation":"North 4 km and South 4 km cancel out. East 3 km and West 3 km cancel out. Net displacement = 0 km — he is back at the starting point."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Number Series — Wrong Term",
 "questionText":"Find the WRONG number in the series: 1, 8, 27, 64, 124, 216",
 "options":["A: 64","B: 124","C: 216","D: 27"],"correctAnswer":"B",
 "explanation":"The series is cubes: 1³=1, 2³=8, 3³=27, 4³=64, 5³=125, 6³=216. The 5th term should be 125, not 124. So 124 is the wrong number."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Coding-Decoding",
 "questionText":"In a code, MILK is written as NHMJ (alternate +1, −1 shift). Using the same rule, how is BOOK coded?",
 "options":["A: CPNJ","B: CNPJ","C: CPOJ","D: CNNJ"],"correctAnswer":"B",
 "explanation":"Pattern: letter 1 +1, letter 2 −1, letter 3 +1, letter 4 −1. Check: M+1=N, I−1=H, L+1=M, K−1=J = NHMJ ✓. BOOK: B+1=C, O−1=N, O+1=P, K−1=J = CNPJ."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Blood Relations",
 "questionText":"Pointing to a boy, Priya says, 'His mother is the only daughter of my father.' How is Priya related to the boy?",
 "options":["A: Aunt","B: Mother","C: Sister","D: Grandmother"],"correctAnswer":"B",
 "explanation":"'Only daughter of my father' = Priya herself. So the boy's mother = Priya. Therefore Priya is the boy's Mother."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Cubes",
 "questionText":"A cube of side 4 cm is painted red on all faces and cut into 1 cm³ cubes. How many small cubes have EXACTLY 3 faces painted red?",
 "options":["A: 4","B: 6","C: 8","D: 12"],"correctAnswer":"C",
 "explanation":"Only corner cubes have 3 painted faces. A cube always has exactly 8 corners, regardless of size. So 8 small cubes have exactly 3 faces painted."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Linear Arrangement",
 "questionText":"In a row of 10 students, Anita is 4th from the left and Beena is 7th from the left. How many students are between Anita and Beena?",
 "options":["A: 1","B: 2","C: 3","D: 4"],"correctAnswer":"B",
 "explanation":"Anita is at position 4, Beena at position 7. Students between them = positions 5 and 6 = 2 students. Formula: (7−4−1) = 2."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Analogy",
 "questionText":"Microscope : Microbiology :: Telescope : ?",
 "options":["A: Astronomy","B: Geography","C: Geology","D: Meteorology"],"correctAnswer":"A",
 "explanation":"A microscope is the primary instrument used in microbiology (study of microorganisms). A telescope is the primary instrument used in astronomy (study of celestial objects)."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Calendar",
 "questionText":"1 January 2024 was a Monday. 2024 is a leap year. What day of the week was 29 February 2024?",
 "options":["A: Wednesday","B: Thursday","C: Friday","D: Saturday"],"correctAnswer":"B",
 "explanation":"29 February is the 60th day of 2024. Day 1 = Monday. Day 60 = Monday + 59 days. 59 = 8×7 + 3, so 3 days ahead. Monday + 3 = Thursday."},

{"subject":"Logical Reasoning","grade":12,"difficulty":"Advanced","topic":"Logical Reasoning","subTopic":"Data Sufficiency",
 "questionText":"Is X > Y?\nStatement 1: X² > Y²\nStatement 2: X > 0",
 "options":["A: Statement 1 alone is sufficient","B: Statement 2 alone is sufficient","C: Both statements together are sufficient","D: Neither statement is sufficient even together"],"correctAnswer":"C",
 "explanation":"S1 alone: X²>Y² means |X|>|Y| but X could be negative (e.g., X=−3, Y=2 gives X²=9>4=Y² but X<Y). S2 alone gives nothing. Together: X>0 and X²>Y² → X>|Y| → X>Y (since X is positive, X>|Y|≥Y). Sufficient."},

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
