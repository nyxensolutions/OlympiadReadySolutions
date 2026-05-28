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

# ─── English G6 Foundation (+1 to reach 15) ───────────────────────────────────
{"subject":"English","grade":6,"difficulty":"Foundation","topic":"English","subTopic":"Spelling",
 "questionText":"Choose the correctly spelled word:",
 "options":["A: beutiful","B: beautiful","C: beautifull","D: butiful"],"correctAnswer":"B",
 "explanation":"The correct spelling is BEAUTIFUL — B-E-A-U-T-I-F-U-L."},

# ─── G12 CS Foundation (15 questions) ────────────────────────────────────────
{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Python — Functions",
 "questionText":"What is the output of: def f(x, y=10): return x + y\nprint(f(5))",
 "options":["A: Error","B: 5","C: 15","D: 10"],"correctAnswer":"C",
 "explanation":"y has a default value of 10. f(5) calls f with x=5, y=10 (default). Returns 5+10=15."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Python — Lists",
 "questionText":"What does the following code print?\nmy_list = [1, 2, 3, 4, 5]\nprint(my_list[1:4])",
 "options":["A: [1, 2, 3]","B: [2, 3, 4]","C: [2, 3, 4, 5]","D: [1, 2, 3, 4]"],"correctAnswer":"B",
 "explanation":"List slicing [1:4] gives elements at indices 1, 2, 3 (stop index is exclusive). Result: [2, 3, 4]."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Databases — SQL",
 "questionText":"Which SQL command is used to remove all rows from a table without deleting the table?",
 "options":["A: DELETE","B: DROP TABLE","C: TRUNCATE","D: REMOVE"],"correctAnswer":"C",
 "explanation":"TRUNCATE removes all rows quickly without logging individual row deletions and keeps the table structure intact."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Networking",
 "questionText":"What does HTTP stand for?",
 "options":["A: HyperText Transfer Protocol","B: High Tech Transfer Process","C: HyperText Transmission Process","D: Host Transfer Protocol"],"correctAnswer":"A",
 "explanation":"HTTP stands for HyperText Transfer Protocol — the foundation of data communication on the World Wide Web."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Object-Oriented Programming",
 "questionText":"In OOP, which feature allows a class to inherit properties and methods from another class?",
 "options":["A: Encapsulation","B: Polymorphism","C: Abstraction","D: Inheritance"],"correctAnswer":"D",
 "explanation":"Inheritance allows a child class to acquire attributes and methods of a parent class, promoting code reuse."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Python — File Handling",
 "questionText":"Which mode opens a file for reading in Python?",
 "options":["A: 'w'","B: 'a'","C: 'r'","D: 'x'"],"correctAnswer":"C",
 "explanation":"'r' opens a file for reading (default). 'w' writes, 'a' appends, 'x' creates new file (fails if exists)."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Data Types",
 "questionText":"In Python, which of the following is an immutable data type?",
 "options":["A: List","B: Dictionary","C: Set","D: Tuple"],"correctAnswer":"D",
 "explanation":"Tuples are immutable — once created, their elements cannot be changed. Lists, dicts, and sets are mutable."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Boolean Algebra",
 "questionText":"What is the result of the Boolean expression: NOT (True AND False)?",
 "options":["A: True","B: False","C: 0","D: None"],"correctAnswer":"A",
 "explanation":"True AND False = False. NOT False = True."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Cybersecurity",
 "questionText":"What type of attack involves sending fraudulent emails that appear to be from reputable companies?",
 "options":["A: Malware","B: Phishing","C: DDoS","D: SQL Injection"],"correctAnswer":"B",
 "explanation":"Phishing attacks use deceptive emails that appear legitimate to trick users into revealing sensitive information."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Operating Systems",
 "questionText":"What is a 'process' in an operating system?",
 "options":["A: A stored file on disk","B: A program currently in execution","C: A hardware device","D: A network connection"],"correctAnswer":"B",
 "explanation":"A process is a program in execution — it includes the program code, current activity, and allocated resources."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Number Systems",
 "questionText":"How many bits are in one byte?",
 "options":["A: 4","B: 16","C: 8","D: 32"],"correctAnswer":"C",
 "explanation":"One byte = 8 bits. This is a fundamental unit of digital information storage."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Python — Loops",
 "questionText":"How many times will the loop execute? \nfor i in range(0, 10, 2): print(i)",
 "options":["A: 10","B: 5","C: 4","D: 6"],"correctAnswer":"B",
 "explanation":"range(0, 10, 2) generates: 0, 2, 4, 6, 8 — five values, so the loop executes 5 times."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Algorithms",
 "questionText":"What does an algorithm's 'time complexity' measure?",
 "options":["A: How long the code is","B: The amount of memory used","C: How the run time grows as input size grows","D: The number of programmers needed"],"correctAnswer":"C",
 "explanation":"Time complexity measures how the running time of an algorithm scales with increasing input size, typically expressed in Big-O notation."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Data Structures",
 "questionText":"Which data structure would you use to implement a 'to-do list' where you always work on the item added earliest?",
 "options":["A: Stack","B: Queue","C: Array","D: Tree"],"correctAnswer":"B",
 "explanation":"A Queue uses FIFO (First In, First Out), so the earliest added item is processed first — perfect for a to-do list."},

{"subject":"Computer Science","grade":12,"difficulty":"Foundation","topic":"Computer Science","subTopic":"Web Technologies",
 "questionText":"What does CSS stand for?",
 "options":["A: Computer Style Sheets","B: Cascading Style Sheets","C: Creative Style System","D: Coded Style Structure"],"correctAnswer":"B",
 "explanation":"CSS stands for Cascading Style Sheets — it is used to style and layout HTML web pages."},

# ─── G12 CS Advanced (15 questions) ──────────────────────────────────────────
{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Python — OOP",
 "questionText":"What is the purpose of the __init__ method in a Python class?",
 "options":["A: To destroy an object","B: To initialize object attributes when an object is created","C: To inherit from a parent class","D: To define class methods only"],"correctAnswer":"B",
 "explanation":"__init__ is the constructor method. It is automatically called when a new object is created, allowing you to set initial attribute values."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Python — OOP",
 "questionText":"Which OOP principle hides internal implementation details and shows only necessary features?",
 "options":["A: Inheritance","B: Polymorphism","C: Encapsulation","D: Abstraction"],"correctAnswer":"D",
 "explanation":"Abstraction hides complex implementation details and shows only the essential features of an object, reducing complexity."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Algorithms — Sorting",
 "questionText":"Which sorting algorithm has O(n log n) average time complexity and works by selecting a pivot?",
 "options":["A: Bubble Sort","B: Insertion Sort","C: Quick Sort","D: Selection Sort"],"correctAnswer":"C",
 "explanation":"Quick Sort partitions the array around a pivot and recursively sorts sub-arrays. Its average time complexity is O(n log n)."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Python — Recursion",
 "questionText":"What is the output of: \ndef power(base, exp):\n  if exp == 0: return 1\n  return base * power(base, exp-1)\nprint(power(2, 4))",
 "options":["A: 8","B: 16","C: 4","D: 256"],"correctAnswer":"B",
 "explanation":"power(2,4) = 2 * power(2,3) = 2 * 2 * power(2,2) = 2*2*2*power(2,1) = 2*2*2*2*1 = 16."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Databases — Normalization",
 "questionText":"A table in 2NF must be in 1NF and have no:",
 "options":["A: Primary key","B: Partial dependencies on the primary key","C: Foreign keys","D: Repeating rows"],"correctAnswer":"B",
 "explanation":"2NF requires 1NF + elimination of partial dependencies — all non-key attributes must depend on the whole primary key, not just part of it."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Networking — TCP/IP",
 "questionText":"At which layer of the OSI model does IP addressing and routing occur?",
 "options":["A: Physical Layer","B: Data Link Layer","C: Network Layer","D: Transport Layer"],"correctAnswer":"C",
 "explanation":"The Network Layer (Layer 3) handles logical addressing (IP addresses) and routing of packets between networks."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Python — Exception Handling",
 "questionText":"What will the following code print?\ntry:\n    x = int('abc')\nexcept ValueError:\n    print('Invalid')\nfinally:\n    print('Done')",
 "options":["A: Invalid","B: Done","C: Invalid\\nDone","D: Error"],"correctAnswer":"C",
 "explanation":"int('abc') raises ValueError, so 'Invalid' is printed. The finally block always executes, printing 'Done'."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Boolean Algebra — Logic Gates",
 "questionText":"A NAND gate is equivalent to which combination?",
 "options":["A: NOT gate followed by AND gate","B: AND gate followed by NOT gate","C: OR gate followed by NOT gate","D: NOT gate followed by OR gate"],"correctAnswer":"B",
 "explanation":"NAND = AND + NOT. The output of an AND gate is inverted. Symbol: A NAND B = NOT(A AND B)."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Python — Comprehensions",
 "questionText":"What is the output of: print([x**2 for x in range(1,6) if x%2==0])",
 "options":["A: [1, 4, 9, 16, 25]","B: [4, 16]","C: [2, 4]","D: [4, 16, 36]"],"correctAnswer":"B",
 "explanation":"Filters even numbers in range(1,6): 2 and 4. Squares them: [4, 16]."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Data Structures — Trees",
 "questionText":"In a Binary Search Tree, where are values smaller than the root stored?",
 "options":["A: Right subtree","B: Left subtree","C: Root level","D: Any position"],"correctAnswer":"B",
 "explanation":"In a BST, for any node, all values in its left subtree are smaller, and all values in its right subtree are larger."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Python — File Handling",
 "questionText":"What is the correct way to read all lines from a file as a list in Python?",
 "options":["A: file.read()","B: file.readline()","C: file.readlines()","D: file.readall()"],"correctAnswer":"C",
 "explanation":"readlines() returns all lines as a list of strings. read() returns the whole file as a string; readline() reads one line."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Networking — Security",
 "questionText":"Which encryption method uses the same key for both encryption and decryption?",
 "options":["A: Asymmetric encryption","B: Symmetric encryption","C: Public key encryption","D: Hashing"],"correctAnswer":"B",
 "explanation":"Symmetric encryption uses a single shared secret key for both encrypting and decrypting data (e.g., AES)."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Algorithms — Complexity",
 "questionText":"If an algorithm takes 8 steps for n=2 and 64 steps for n=4, what is its time complexity?",
 "options":["A: O(n)","B: O(n²)","C: O(n³)","D: O(2ⁿ)"],"correctAnswer":"C",
 "explanation":"n=2: 8=2³. n=4: 64=4³. The pattern is n³, so time complexity is O(n³)."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Databases — Transactions",
 "questionText":"The ACID properties of a database transaction stand for:",
 "options":["A: Accuracy, Consistency, Integrity, Durability","B: Atomicity, Consistency, Isolation, Durability","C: Atomicity, Completeness, Isolation, Data","D: Accuracy, Completeness, Integration, Duration"],"correctAnswer":"B",
 "explanation":"ACID: Atomicity (all or nothing), Consistency (valid state), Isolation (transactions don't interfere), Durability (committed changes persist)."},

{"subject":"Computer Science","grade":12,"difficulty":"Advanced","topic":"Computer Science","subTopic":"Python — Stacks and Queues",
 "questionText":"Which Python method would you use to implement a stack's 'pop' operation on a list?",
 "options":["A: list.remove()","B: list.pop()","C: list.pop(0)","D: list.delete()"],"correctAnswer":"B",
 "explanation":"list.pop() removes and returns the last element (LIFO). list.pop(0) removes the first element (FIFO, for queue behaviour)."},

# ─── GK G10 Foundation (+10, currently 25 → 35) ──────────────────────────────
{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Indian Polity",
 "questionText":"Who is the Constitutional head of the Indian state?",
 "options":["A: Prime Minister","B: Chief Justice","C: President","D: Speaker of Lok Sabha"],"correctAnswer":"C",
 "explanation":"The President of India is the constitutional head of state, though executive powers are exercised by the Prime Minister and Council of Ministers."},

{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Science",
 "questionText":"What is the chemical symbol for gold?",
 "options":["A: Go","B: Gd","C: Ag","D: Au"],"correctAnswer":"D",
 "explanation":"Gold's chemical symbol is Au, from the Latin word 'Aurum'."},

{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"World History",
 "questionText":"The World War II ended in which year?",
 "options":["A: 1943","B: 1944","C: 1945","D: 1946"],"correctAnswer":"C",
 "explanation":"World War II ended in 1945 — in Europe on 8 May (V-E Day) and in the Pacific on 15 August/2 September (V-J Day)."},

{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Indian Economy",
 "questionText":"What does GDP stand for?",
 "options":["A: Gross Domestic Production","B: Gross Domestic Product","C: General Domestic Product","D: Gross Development Programme"],"correctAnswer":"B",
 "explanation":"GDP stands for Gross Domestic Product — the total monetary value of all goods and services produced within a country in a year."},

{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Science and Technology",
 "questionText":"Which scientist is credited with the theory of evolution by natural selection?",
 "options":["A: Gregor Mendel","B: Louis Pasteur","C: Charles Darwin","D: Isaac Newton"],"correctAnswer":"C",
 "explanation":"Charles Darwin proposed the theory of evolution by natural selection in his 1859 book 'On the Origin of Species'."},

{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Sports",
 "questionText":"How many players are there in a football (soccer) team?",
 "options":["A: 9","B: 10","C: 11","D: 12"],"correctAnswer":"C",
 "explanation":"A standard football team has 11 players on the field, including the goalkeeper."},

{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Indian Geography",
 "questionText":"Which Indian state has the longest coastline?",
 "options":["A: Tamil Nadu","B: Kerala","C: Andhra Pradesh","D: Gujarat"],"correctAnswer":"D",
 "explanation":"Gujarat has the longest coastline of any Indian state, spanning approximately 1,600 km."},

{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"World Geography",
 "questionText":"Mount Everest is located on the border of which two countries?",
 "options":["A: India and China","B: Nepal and Tibet (China)","C: Nepal and India","D: Bhutan and Tibet"],"correctAnswer":"B",
 "explanation":"Mount Everest sits on the border between Nepal and Tibet (an autonomous region of China)."},

{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Literature",
 "questionText":"Who wrote the Indian national anthem 'Jana Gana Mana'?",
 "options":["A: Bankim Chandra Chattopadhyay","B: Rabindranath Tagore","C: Sarojini Naidu","D: Subramania Bharati"],"correctAnswer":"B",
 "explanation":"Jana Gana Mana was written by Rabindranath Tagore. It was officially adopted as the national anthem on 24 January 1950."},

{"subject":"General Knowledge","grade":10,"difficulty":"Foundation","topic":"General Knowledge","subTopic":"Environment",
 "questionText":"The Paris Agreement primarily deals with which global issue?",
 "options":["A: Nuclear disarmament","B: Climate change and carbon emissions","C: Biodiversity loss","D: Ocean pollution"],"correctAnswer":"B",
 "explanation":"The Paris Agreement (2015) is an international treaty within the UN Framework Convention on Climate Change, aiming to limit global warming."},

# ─── GK G9 Advanced top-up (+10, currently 15 → 25) ─────────────────────────
{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Indian History",
 "questionText":"The 'Doctrine of Lapse' was introduced by which British Governor-General?",
 "options":["A: Lord Canning","B: Lord Dalhousie","C: Lord Ripon","D: Lord Curzon"],"correctAnswer":"B",
 "explanation":"Lord Dalhousie introduced the Doctrine of Lapse (1848–1856), by which any princely state under British suzerainty would be annexed if the ruler died without a male heir."},

{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Indian Constitution",
 "questionText":"Which Part of the Indian Constitution deals with Fundamental Rights?",
 "options":["A: Part I","B: Part II","C: Part III","D: Part IV"],"correctAnswer":"C",
 "explanation":"Fundamental Rights are enshrined in Part III (Articles 12–35) of the Indian Constitution."},

{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Science",
 "questionText":"What is the SI unit of electric current?",
 "options":["A: Volt","B: Ohm","C: Ampere","D: Watt"],"correctAnswer":"C",
 "explanation":"The Ampere (A) is the SI unit of electric current, named after André-Marie Ampère."},

{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"World Geography",
 "questionText":"Which is the world's largest desert?",
 "options":["A: Sahara","B: Arabian","C: Antarctic","D: Gobi"],"correctAnswer":"C",
 "explanation":"The Antarctic Desert is the world's largest desert at ~14.2 million sq km. The Sahara is the largest hot desert."},

{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Economics",
 "questionText":"What does the term 'inflation' mean?",
 "options":["A: A decrease in the general price level","B: A sustained increase in the general price level","C: Growth in GDP","D: A fall in currency value due to printing more notes"],"correctAnswer":"B",
 "explanation":"Inflation refers to the sustained general increase in prices of goods and services over time, resulting in a decrease in purchasing power."},

{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Science and Technology",
 "questionText":"What is the function of the ozone layer?",
 "options":["A: Traps heat to warm Earth","B: Absorbs ultraviolet radiation from the Sun","C: Provides oxygen for breathing","D: Reflects sunlight back into space"],"correctAnswer":"B",
 "explanation":"The ozone layer in the stratosphere absorbs most of the Sun's harmful ultraviolet (UV-B and UV-C) radiation, protecting life on Earth."},

{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Indian Polity",
 "questionText":"Which Article of the Indian Constitution abolishes untouchability?",
 "options":["A: Article 14","B: Article 15","C: Article 16","D: Article 17"],"correctAnswer":"D",
 "explanation":"Article 17 of the Indian Constitution abolishes 'untouchability' and forbids its practice in any form."},

{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"World History",
 "questionText":"The Russian Revolution of 1917 led to the establishment of which type of government?",
 "options":["A: Constitutional Monarchy","B: Federal Democracy","C: Communist State","D: Military Dictatorship"],"correctAnswer":"C",
 "explanation":"The Bolshevik Revolution of October 1917 led by Lenin established a communist state (Soviet Russia), which later became the Soviet Union in 1922."},

{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Science",
 "questionText":"The speed of light in a vacuum is approximately:",
 "options":["A: 3 × 10⁶ m/s","B: 3 × 10⁸ m/s","C: 3 × 10¹⁰ m/s","D: 3 × 10⁴ m/s"],"correctAnswer":"B",
 "explanation":"The speed of light in vacuum is approximately 3 × 10⁸ m/s (299,792,458 m/s to be precise)."},

{"subject":"General Knowledge","grade":9,"difficulty":"Advanced","topic":"General Knowledge","subTopic":"Environment",
 "questionText":"Which international agreement aimed to phase out ozone-depleting substances?",
 "options":["A: Kyoto Protocol","B: Paris Agreement","C: Montreal Protocol","D: Stockholm Convention"],"correctAnswer":"C",
 "explanation":"The Montreal Protocol (1987) is an international treaty designed to phase out the production of ozone-depleting substances like CFCs. It is considered the most successful environmental treaty."},

# ─── Science G9 Foundation top-up (+10, currently 19 → 29) ──────────────────
{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Matter and Its Nature",
 "questionText":"Which of the following is a physical change?",
 "options":["A: Burning of wood","B: Rusting of iron","C: Melting of ice","D: Cooking food"],"correctAnswer":"C",
 "explanation":"Melting of ice is a physical change — the substance (water) remains the same, only the state changes. The other options involve chemical changes."},

{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Atoms and Molecules",
 "questionText":"What is the atomic number of oxygen?",
 "options":["A: 6","B: 7","C: 8","D: 9"],"correctAnswer":"C",
 "explanation":"Oxygen has atomic number 8, meaning it has 8 protons in its nucleus."},

{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Cell Biology",
 "questionText":"Which organelle is known as the 'powerhouse of the cell'?",
 "options":["A: Nucleus","B: Ribosome","C: Mitochondria","D: Chloroplast"],"correctAnswer":"C",
 "explanation":"Mitochondria produce ATP (energy) through cellular respiration, earning the name 'powerhouse of the cell'."},

{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Motion",
 "questionText":"A car travels 100 km in 2 hours. What is its average speed?",
 "options":["A: 50 km/h","B: 200 km/h","C: 100 km/h","D: 25 km/h"],"correctAnswer":"A",
 "explanation":"Average speed = Distance ÷ Time = 100 km ÷ 2 h = 50 km/h."},

{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Gravitation",
 "questionText":"The value of acceleration due to gravity on Earth's surface is approximately:",
 "options":["A: 6.8 m/s²","B: 9.8 m/s²","C: 11.2 m/s²","D: 8.5 m/s²"],"correctAnswer":"B",
 "explanation":"The standard acceleration due to gravity (g) at Earth's surface is approximately 9.8 m/s²."},

{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Work and Energy",
 "questionText":"What is the SI unit of work and energy?",
 "options":["A: Watt","B: Newton","C: Joule","D: Pascal"],"correctAnswer":"C",
 "explanation":"The SI unit of work and energy is the Joule (J). 1 Joule = 1 Newton × 1 metre."},

{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Sound",
 "questionText":"Sound cannot travel through which medium?",
 "options":["A: Air","B: Water","C: Steel","D: Vacuum"],"correctAnswer":"D",
 "explanation":"Sound requires a medium (matter) to travel. It cannot travel through a vacuum because there are no particles to transmit the vibration."},

{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Natural Resources",
 "questionText":"Which of the following is a renewable source of energy?",
 "options":["A: Coal","B: Petroleum","C: Solar energy","D: Natural gas"],"correctAnswer":"C",
 "explanation":"Solar energy is renewable — it is continuously replenished by the Sun. Coal, petroleum, and natural gas are fossil fuels (non-renewable)."},

{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Improvement in Food Resources",
 "questionText":"Which gas is used by plants for photosynthesis?",
 "options":["A: Oxygen","B: Nitrogen","C: Carbon dioxide","D: Hydrogen"],"correctAnswer":"C",
 "explanation":"Plants absorb carbon dioxide (CO₂) from the atmosphere and use it along with water and sunlight to produce glucose through photosynthesis."},

{"subject":"Science","grade":9,"difficulty":"Foundation","topic":"Science","subTopic":"Diversity in Living Organisms",
 "questionText":"Which classification system of organisms uses two names (genus and species) for each organism?",
 "options":["A: Monomial nomenclature","B: Binomial nomenclature","C: Trinomial nomenclature","D: Polynomial nomenclature"],"correctAnswer":"B",
 "explanation":"Binomial nomenclature, proposed by Carl Linnaeus, assigns each organism a two-part Latin name: genus + species (e.g., Homo sapiens)."},

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
