"""
generate_cs_pixabay_gr1112.py
High-quality Pixabay images -> Computer Science Grade 11 & 12 (Olympiad difficulty).
15 questions per grade = 30 total.
Covers: Python, Data Structures, Algorithms, Networking, Databases, OOP, OS concepts.

QUALITY RULES:
  1. Pixabay query matches what is literally visible in the photo.
  2. Image provides visual context; question tests CS knowledge.
  3. All code outputs and algorithm answers are independently verified.
  4. Concepts are Olympiad-level (beyond basic textbook).
"""

import os, io, time, random, requests
import cloudinary, cloudinary.uploader

PIXABAY_API_KEY       = os.environ.get("PIXABAY_API_KEY",       "56031484-1cf6e0a588c13eebd71681fda")
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE",
    "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY", "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME, api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET, secure=True)
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}
RUN_ID  = int(time.time())

posted = skipped = failed = 0

_dl = requests.Session()
_dl.headers.update({"User-Agent": "Mozilla/5.0 (compatible; OlympiadReady/1.0)"})


def pixabay_fetch(query, idx=0):
    params = {"key": PIXABAY_API_KEY, "q": query, "image_type": "photo",
              "orientation": "horizontal", "safesearch": "true",
              "per_page": 10, "order": "popular"}
    try:
        r = requests.get("https://pixabay.com/api/", params=params, timeout=12)
        r.raise_for_status()
        hits = r.json().get("hits", [])
    except Exception as e:
        print(f"    [PIXABAY ERR] '{query}': {e}"); return None
    if not hits:
        print(f"    [NO HITS] '{query}'"); return None
    for hi in range(min(len(hits), 5)):
        hit = hits[(idx + hi) % len(hits)]
        img_url = hit.get("previewURL") or hit.get("webformatURL")
        if not img_url: continue
        try:
            time.sleep(1.5)
            dl = _dl.get(img_url, timeout=20); dl.raise_for_status()
        except Exception as e:
            print(f"    [DL ERR] '{query}' hit {hi}: {e}"); continue
        pub_id = f"{CLOUDINARY_FOLDER}/cs_{query[:26].replace(' ','-')}_{RUN_ID}_{hit['id']}"
        try:
            time.sleep(1.0)
            res = cloudinary.uploader.upload(io.BytesIO(dl.content), public_id=pub_id,
                                             overwrite=False, resource_type="image")
            return res["secure_url"]
        except Exception as e:
            print(f"    [CDN ERR] '{query}' hit {hi}: {e}"); continue
    return None


def post_q(subject, grade, difficulty, topic, subtopic, text, opts, correct_idx, expl, img_url):
    global posted, skipped, failed
    payload = {
        "subject": subject, "grade": grade, "difficulty": difficulty,
        "topic": topic, "subTopic": subtopic,
        "questionText": text, "imageUrl": img_url,
        "options": opts, "correctAnswer": ["A","B","C","D"][correct_idx],
        "explanation": expl
    }
    try:
        r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                          json=payload, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            posted += 1; return True
        elif r.status_code == 409:
            skipped += 1; return False
        else:
            print(f"    [FAIL {r.status_code}] {text[:60]}"); failed += 1; return False
    except Exception as e:
        print(f"    [ERR] {e}"); failed += 1; return False


def add_img(subject, grade, topic, subtopic, query, text, correct, wrongs, expl, pix_idx=0, difficulty="Olympiad"):
    tag = f"G{grade} CS {query[:30]}..."
    img_url = pixabay_fetch(query, pix_idx)
    if not img_url:
        print(f"    [SKIP no img] {tag}"); return
    opts = [correct] + wrongs[:3]
    random.shuffle(opts)
    cidx = opts.index(correct)
    ok = post_q(subject, grade, difficulty, topic, subtopic, text, opts, cidx, expl, img_url)
    status = "ok" if ok else "dup/fail"
    print(f"  {tag} -> {status}")


# ===========================================================================
#  COMPUTER SCIENCE GRADE 11  (15 questions)
# ===========================================================================

def gen_gr11():
    print("\n" + "="*65)
    print("  Computer Science Grade 11  (15 questions)")
    print("="*65)
    S, G = "Computer Science", 11

    # 1. Python code on screen — List slicing
    add_img(S, G, "Python Programming", "List Slicing",
        query="python programming code screen laptop",
        text="Consider the Python code:\nmy_list = [10, 20, 30, 40, 50, 60]\nprint(my_list[1:4])\nWhat is the output?",
        correct="[20, 30, 40]",
        wrongs=["[10, 20, 30]", "[20, 30, 40, 50]", "[30, 40, 50]"],
        expl="Slicing my_list[1:4] returns elements at indices 1, 2, 3 (stop index 4 is exclusive). Index 1=20, 2=30, 3=40. Output: [20, 30, 40].")

    # 2. Binary numbers screen — Number systems
    add_img(S, G, "Number Systems", "Binary to Decimal Conversion",
        query="binary code numbers screen digital",
        text="The binary number 10110101 is displayed on a screen. What is its decimal equivalent?",
        correct="181",
        wrongs=["173", "185", "169"],
        expl="10110101 = 128+0+32+16+0+4+0+1 = 128+32+16+4+1 = 181. (Positional: 1x128 + 0x64 + 1x32 + 1x16 + 0x8 + 1x4 + 0x2 + 1x1 = 181)")

    # 3. Flowchart algorithm diagram — Algorithm design
    add_img(S, G, "Computational Thinking", "Flowchart and Algorithms",
        query="flowchart algorithm diagram decision boxes",
        text="A flowchart has: Start -> Input N -> Is N%2==0? -> Yes: Print 'Even', No: Print 'Odd' -> Stop. What is printed if N = 0?",
        correct="Even",
        wrongs=["Odd", "0", "Error — division by zero"],
        expl="0 % 2 = 0 (zero divided by 2 has remainder 0). The condition N%2==0 is True for N=0, so 'Even' is printed. Zero is mathematically an even number.")

    # 4. Computer motherboard circuit — Boolean logic
    add_img(S, G, "Boolean Logic", "Logic Gates",
        query="computer motherboard circuit board chip",
        text="A circuit on the motherboard implements the Boolean expression: F = A AND (NOT B) OR C. Evaluate F when A=1, B=1, C=0.",
        correct="0",
        wrongs=["1", "Undefined", "depends on gate order"],
        expl="Following operator precedence (NOT first, then AND, then OR): NOT B = NOT 1 = 0. A AND 0 = 1 AND 0 = 0. 0 OR C = 0 OR 0 = 0. So F = 0.")

    # 5. Stack of books/plates — Stack data structure
    add_img(S, G, "Data Structures", "Stack",
        query="stack plates pile kitchen dishes",
        text="A stack (like a pile of plates shown) has elements pushed in order: 5, 10, 15, 20. The operation sequence is: PUSH 5, PUSH 10, POP, PUSH 15, POP. What is the top of the stack after all operations?",
        correct="5",
        wrongs=["15", "10", "20"],
        expl="PUSH 5: Stack=[5]. PUSH 10: Stack=[5,10]. POP removes 10: Stack=[5]. PUSH 15: Stack=[5,15]. POP removes 15: Stack=[5]. Top = 5.")

    # 6. Queue waiting line — Queue data structure
    add_img(S, G, "Data Structures", "Queue",
        query="queue people waiting line airport",
        text="A queue (like the queue shown) initially has: FRONT -> [A, B, C, D] <- REAR. Operations: ENQUEUE('E'), DEQUEUE(), ENQUEUE('F'), DEQUEUE(). What is the queue state after all operations?",
        correct="FRONT -> [C, D, E, F] <- REAR",
        wrongs=["FRONT -> [B, C, D, E] <- REAR", "FRONT -> [D, E, F] <- REAR", "FRONT -> [A, C, E, F] <- REAR"],
        expl="Start: [A,B,C,D]. ENQUEUE E: [A,B,C,D,E]. DEQUEUE removes A: [B,C,D,E]. ENQUEUE F: [B,C,D,E,F]. DEQUEUE removes B: [C,D,E,F]. Final: [C,D,E,F].")

    # 7. Network cables router — Networking
    add_img(S, G, "Computer Networks", "Network Topologies",
        query="network cables router ethernet switch",
        text="In the network shown, all devices connect to a central hub/switch. What network topology is this, and what is its key disadvantage?",
        correct="Star topology — if the central switch fails, all devices lose connectivity",
        wrongs=["Bus topology — a break anywhere disrupts the whole network", "Ring topology — data travels in one direction causing delays", "Mesh topology — expensive due to excessive cabling"],
        expl="A central hub/switch with all devices connected to it is a Star topology. Its main weakness is the single point of failure: the hub/switch. If it fails, all devices are disconnected, unlike mesh where multiple paths exist.")

    # 8. Database server — SQL basics
    add_img(S, G, "Database Management", "SQL Queries",
        query="database server rack storage hardware",
        text="A database has a table 'Students(RollNo, Name, Marks, Grade)'. Which SQL query correctly retrieves names of students who scored above 90?",
        correct="SELECT Name FROM Students WHERE Marks > 90;",
        wrongs=["SELECT Name WHERE Marks > 90 FROM Students;", "SELECT * FROM Students WHERE Marks = 90;", "GET Name FROM Students IF Marks > 90;"],
        expl="SQL SELECT syntax: SELECT column(s) FROM table WHERE condition. Clause order is fixed: SELECT -> FROM -> WHERE. 'GET' and 'IF' are not SQL keywords. 'Marks = 90' retrieves only exactly 90, not above 90.")

    # 9. Cybersecurity padlock — Encryption
    add_img(S, G, "Cybersecurity", "Encryption and Security",
        query="cybersecurity padlock digital security lock",
        text="The padlock icon shown represents HTTPS encryption. HTTPS uses TLS which employs asymmetric encryption for the handshake and symmetric encryption for data transfer. Why is symmetric encryption used for data transfer (not asymmetric)?",
        correct="Symmetric encryption is much faster and less computationally expensive for bulk data",
        wrongs=["Symmetric encryption is more secure than asymmetric", "Asymmetric encryption cannot encrypt large amounts of data", "Symmetric keys are longer and harder to crack"],
        expl="Asymmetric encryption (RSA) is computationally expensive — it uses large key pairs and mathematical operations. Symmetric encryption (AES) is orders of magnitude faster. TLS uses asymmetric keys to securely exchange a session key, then switches to fast symmetric encryption for all actual data.")

    # 10. Python dictionary — Dictionary operations
    add_img(S, G, "Python Programming", "Dictionaries",
        query="dictionary book words definitions open",
        text="Consider this Python code:\nd = {'a': 1, 'b': 2, 'c': 3}\nd['b'] = 10\nd['d'] = 4\ndel d['a']\nprint(len(d))\nWhat is the output?",
        correct="3",
        wrongs=["4", "2", "5"],
        expl="Start: d={'a':1,'b':2,'c':3} (3 items). Update b=10: still 3 items. Add 'd':4: now 4 items. Delete 'a': now 3 items. len(d) = 3.")

    # 11. CPU processor — OS and memory management
    add_img(S, G, "Computer Organisation", "CPU and Memory",
        query="CPU processor chip Intel AMD computer",
        text="A CPU shown has multiple cores. In context of the OS, what is the key difference between a PROCESS and a THREAD?",
        correct="A process has its own separate memory space; threads within the same process share memory space",
        wrongs=["A thread is a complete program; a process is a part of a thread", "Processes are faster than threads because they run independently", "Threads can only run on single-core CPUs"],
        expl="A process is an independent program in execution with its own address space. Threads are lightweight units within a process that share the same memory. Threads are faster to create and communicate (shared memory) but have risks like race conditions.")

    # 12. File folder storage — File handling in Python
    add_img(S, G, "Python Programming", "File Handling",
        query="file folder documents storage organised",
        text="What is the output of this Python code assuming 'test.txt' does not exist?\ntry:\n    f = open('test.txt', 'r')\nexcept FileNotFoundError:\n    print('File missing')\nfinally:\n    print('Done')",
        correct="File missing\nDone",
        wrongs=["File missing", "Done", "Error — program crashes"],
        expl="Since 'test.txt' doesn't exist, opening with 'r' raises FileNotFoundError. The except block prints 'File missing'. The finally block ALWAYS executes regardless of exception, so 'Done' is also printed.")

    # 13. Cloud computing data center — Cloud and Internet
    add_img(S, G, "Computer Networks", "Internet Services",
        query="data center cloud computing servers rows",
        text="A data center like the one shown hosts cloud services. What is the difference between IaaS, PaaS, and SaaS in cloud computing?",
        correct="IaaS = infrastructure (VMs, storage); PaaS = platform (OS+runtime); SaaS = ready-to-use software",
        wrongs=["IaaS = software; PaaS = storage; SaaS = networking", "All three are identical — they just differ in pricing", "IaaS is for businesses; PaaS and SaaS are for individuals only"],
        expl="Cloud service models: IaaS (Infrastructure as a Service) gives raw compute/storage (e.g., AWS EC2). PaaS (Platform) provides a development environment (e.g., Heroku). SaaS (Software) delivers finished applications over the internet (e.g., Gmail, Office 365).")

    # 14. Sorting colored balls/objects — Sorting algorithms
    add_img(S, G, "Algorithms", "Sorting Algorithms",
        query="sorted organized colored objects arrangement",
        text="Bubble Sort is applied to the list [5, 3, 8, 1, 2]. How many swaps occur in the FIRST complete pass (left to right)?",
        correct="3",
        wrongs=["4", "2", "5"],
        expl="First pass comparisons: (5,3)→swap [3,5,8,1,2]; (5,8)→no swap; (8,1)→swap [3,5,1,8,2]; (8,2)→swap [3,5,1,2,8]. Total swaps = 3.")

    # 15. Linked chain — Linked list concept
    add_img(S, G, "Data Structures", "Linked List",
        query="chain links metal connected sequence",
        text="In a singly linked list (like chain links shown), deleting a node from the MIDDLE requires:",
        correct="Updating the previous node's 'next' pointer to point to the node after the deleted one — O(n) to find it",
        wrongs=["Simply removing the node — no pointer update needed — O(1)", "Rebuilding the entire list from scratch — O(n^2)", "Updating the deleted node's own pointer — O(1)"],
        expl="In a singly linked list, to delete node X: traverse from head to find node Y before X (O(n)), then set Y.next = X.next. X becomes unreachable. The key insight is that you must update the PREVIOUS node's pointer, and finding it takes O(n) time.")

    print("  Grade 11 Computer Science done.")


# ===========================================================================
#  COMPUTER SCIENCE GRADE 12  (15 questions)
# ===========================================================================

def gen_gr12():
    print("\n" + "="*65)
    print("  Computer Science Grade 12  (15 questions)")
    print("="*65)
    S, G = "Computer Science", 12

    # 1. Python OOP — class hierarchy
    add_img(S, G, "Python OOP", "Inheritance and Polymorphism",
        query="hierarchy pyramid levels organisation",
        text="In Python OOP, a class 'Dog' inherits from class 'Animal'. Both have a method speak(). Dog.speak() prints 'Woof', Animal.speak() prints 'Generic sound'. What concept does this demonstrate?",
        correct="Method overriding (runtime polymorphism)",
        wrongs=["Method overloading", "Multiple inheritance", "Encapsulation"],
        expl="When a subclass redefines a method from its parent class, it is method overriding. Calling speak() on a Dog object will use Dog's version — this runtime decision on which method to call is polymorphism. Python does not support method overloading (multiple methods with same name).")

    # 2. Binary tree diagram — Tree data structure
    add_img(S, G, "Data Structures", "Binary Search Tree",
        query="tree branches structure organic natural",
        text="A Binary Search Tree (BST) has these insertions in order: 50, 30, 70, 20, 40, 60, 80. What is the result of an IN-ORDER traversal?",
        correct="20, 30, 40, 50, 60, 70, 80",
        wrongs=["50, 30, 70, 20, 40, 60, 80", "20, 40, 30, 60, 80, 70, 50", "50, 20, 40, 30, 80, 60, 70"],
        expl="In-order traversal (Left -> Root -> Right) of a BST always produces sorted ascending output. The BST with root 50, left subtree {30,20,40}, right subtree {70,60,80} gives in-order: 20,30,40,50,60,70,80.")

    # 3. Recursion spiral — Recursion
    add_img(S, G, "Python Programming", "Recursion",
        query="spiral staircase recursive pattern architecture",
        text="What is the output of this recursive Python function?\ndef f(n):\n    if n <= 0: return 0\n    return n + f(n-2)\nprint(f(6))",
        correct="12",
        wrongs=["21", "6", "18"],
        expl="f(6) = 6 + f(4) = 6 + 4 + f(2) = 6+4+2+f(0) = 6+4+2+0 = 12. The function sums every other integer from n down to 0 (for even n: sum of 6,4,2 = 12).")

    # 4. Network OSI model — Networking layers
    add_img(S, G, "Computer Networks", "OSI and TCP/IP Model",
        query="network cables ethernet data center connections",
        text="Data is transmitted over the network shown. At which OSI layer does a ROUTER primarily operate, and what does it use to forward packets?",
        correct="Layer 3 (Network Layer) — uses IP addresses to route packets",
        wrongs=["Layer 2 (Data Link Layer) — uses MAC addresses", "Layer 4 (Transport Layer) — uses port numbers", "Layer 7 (Application Layer) — uses domain names"],
        expl="Routers operate at OSI Layer 3 (Network Layer) and use IP addresses to determine the best path for packet forwarding between different networks. Switches operate at Layer 2 using MAC addresses. Layer 4 devices (like firewalls/load balancers) use port numbers.")

    # 5. Database table spreadsheet — Advanced SQL
    add_img(S, G, "Database Management", "Advanced SQL",
        query="database spreadsheet table data records",
        text="A 'Sales' table has columns: SaleID, Product, Amount, Region. Which query finds regions where total sales exceed 1,00,000?",
        correct="SELECT Region, SUM(Amount) FROM Sales GROUP BY Region HAVING SUM(Amount) > 100000;",
        wrongs=["SELECT Region, SUM(Amount) FROM Sales WHERE SUM(Amount) > 100000 GROUP BY Region;", "SELECT Region FROM Sales WHERE Amount > 100000 GROUP BY Region;", "SELECT Region, SUM(Amount) FROM Sales HAVING SUM(Amount) > 100000;"],
        expl="GROUP BY groups rows by Region; SUM(Amount) aggregates. HAVING filters on aggregated results (WHERE cannot be used with aggregate functions). GROUP BY must come before HAVING. Without GROUP BY, HAVING cannot reference Region groups.")

    # 6. Python list comprehension — Advanced Python
    add_img(S, G, "Python Programming", "List Comprehension",
        query="python programming code dark screen terminal",
        text="What is the output of:\nresult = [x**2 for x in range(1, 6) if x % 2 != 0]\nprint(result)",
        correct="[1, 9, 25]",
        wrongs=["[1, 4, 9, 16, 25]", "[4, 16]", "[1, 3, 5]"],
        expl="range(1,6) = [1,2,3,4,5]. Filter odd numbers (x%2!=0): [1,3,5]. Square each: [1,9,25]. List comprehension applies the expression x**2 only to elements passing the condition.")

    # 7. Hashing / fingerprint — Hashing concept
    add_img(S, G, "Algorithms", "Hashing",
        query="fingerprint biometric scan security unique",
        text="Like a fingerprint, a hash function maps data to a unique fixed-size output. If a hash table has 7 slots and uses h(key) = key % 7, where does key=50 map?",
        correct="Slot 1",
        wrongs=["Slot 0", "Slot 3", "Slot 5"],
        expl="h(50) = 50 % 7 = 1 (since 7x7=49, 50-49=1). Key 50 maps to slot 1.")

    # 8. Stack of papers — Python exception handling
    add_img(S, G, "Python Programming", "Exception Handling",
        query="stack papers documents overflow pile desk",
        text="What is printed by this code?\ntry:\n    x = int('abc')\n    print('A')\nexcept ValueError:\n    print('B')\nexcept Exception:\n    print('C')\nelse:\n    print('D')\nfinally:\n    print('E')",
        correct="B\nE",
        wrongs=["B\nD\nE", "C\nE", "A\nD\nE"],
        expl="int('abc') raises ValueError. The except ValueError block catches it and prints 'B'. The else block only runs if NO exception occurs — so 'D' is skipped. Finally always runs → 'E'. Output: B then E.")

    # 9. Wireless signal router — WiFi and protocols
    add_img(S, G, "Computer Networks", "Wireless Networking",
        query="wifi router wireless signal home network",
        text="A WiFi router shown broadcasts on the 5 GHz band. Compared to 2.4 GHz, 5 GHz WiFi offers:",
        correct="Higher speed and less interference but shorter range",
        wrongs=["Longer range and higher speed", "Lower speed but longer range and less interference", "Identical performance but different frequency allocation"],
        expl="5 GHz provides faster data rates and less congestion (fewer devices use it), but higher frequency signals attenuate more quickly and penetrate walls less effectively — resulting in shorter range. 2.4 GHz is slower but travels farther and penetrates obstacles better.")

    # 10. Pandas/data analysis — Python libraries
    add_img(S, G, "Python Programming", "Python Libraries",
        query="data analysis graph statistics laptop screen",
        text="A data analyst uses Python. Which library is BEST suited for loading a CSV file into a tabular structure, filtering rows, and computing column statistics?",
        correct="pandas",
        wrongs=["numpy", "matplotlib", "os"],
        expl="pandas provides DataFrame — a 2D tabular data structure. It excels at reading CSV (read_csv()), filtering rows (df[df['col']>5]), and computing statistics (df.describe(), df.mean()). numpy handles numerical arrays. matplotlib handles plotting. os handles file system operations.")

    # 11. Binary search — Sorted array
    add_img(S, G, "Algorithms", "Binary Search",
        query="sorted books shelf library organised alphabetical",
        text="Binary search is applied to the sorted list [2, 5, 8, 12, 16, 23, 38, 56, 72, 91] to find 23. How many comparisons are needed?",
        correct="3",
        wrongs=["4", "5", "2"],
        expl="List has 10 elements (indices 0-9). Compare 1: mid=4, value=16 < 23 -> search right half. Compare 2: mid=7, value=56 > 23 -> search left. Compare 3: mid=5, value=23 == 23 -> found. Total: 3 comparisons.")

    # 12. Python error fix — Debugging
    add_img(S, G, "Python Programming", "Debugging",
        query="magnifying glass code bug error screen",
        text="Find the error: def calculate_avg(lst):\n    total = 0\n    for i in range(len(lst)+1):\n        total += lst[i]\n    return total / len(lst)\nWhat type of error will this cause?",
        correct="IndexError — range(len(lst)+1) goes one index beyond the list",
        wrongs=["ZeroDivisionError — total is 0", "NameError — variable 'total' is not defined", "SyntaxError — the for loop is incorrectly written"],
        expl="range(len(lst)+1) produces indices 0 to len(lst), but valid list indices are only 0 to len(lst)-1. When i = len(lst), lst[i] raises IndexError: list index out of range. Fix: use range(len(lst)) instead.")

    # 13. Encryption keys — Cryptography
    add_img(S, G, "Cybersecurity", "Cryptography",
        query="encryption keys digital security golden lock",
        text="RSA encryption shown uses a public key to encrypt and private key to decrypt. If a message M is encrypted as C = M^e mod n, and decrypted as M = C^d mod n, what property ensures d works as the decryption key?",
        correct="e and d are modular multiplicative inverses: e*d ≡ 1 (mod phi(n))",
        wrongs=["e and d are always equal in RSA", "d is derived by simply subtracting e from n", "d = n / e always produces the correct decryption key"],
        expl="In RSA, phi(n) = (p-1)(q-1). The keys e and d satisfy e*d mod phi(n) = 1 — they are modular inverses. This ensures (M^e)^d mod n = M^(ed mod phi(n)) mod n = M^1 mod n = M, recovering the original message.")

    # 14. Graph nodes network map — Graph algorithms
    add_img(S, G, "Algorithms", "Graph Traversal",
        query="network map nodes connections graph web",
        text="In the graph shown (like a network map), BFS starts from node A and explores level by level. For an unweighted graph, what property does BFS guarantee when finding a path from A to any node?",
        correct="The path found is the shortest path (minimum number of edges)",
        wrongs=["The path found visits the fewest total nodes in the graph", "BFS guarantees the path with the minimum total weight", "BFS only works on directed graphs"],
        expl="BFS explores nodes in order of their distance (number of edges) from the source. When it first reaches a node, it has taken the fewest possible edges to get there — guaranteeing shortest path in unweighted graphs. For weighted graphs, Dijkstra's algorithm is needed.")

    # 15. Machine learning neural network — AI concepts
    add_img(S, G, "Emerging Technologies", "Artificial Intelligence",
        query="artificial intelligence neural network brain digital",
        text="A neural network is being trained for image classification. After 50 epochs, training accuracy is 99% but test accuracy is 65%. This gap indicates:",
        correct="Overfitting — the model memorised training data and fails to generalise to new data",
        wrongs=["Underfitting — the model is too simple to learn patterns", "The test dataset is corrupted or too small", "99% is the maximum possible accuracy — 65% test is normal"],
        expl="Overfitting occurs when a model learns the training data too well (including noise), resulting in high training accuracy but low test accuracy. The cure includes: adding regularisation (dropout, L2), using more diverse training data, reducing model complexity, or early stopping.")

    print("  Grade 12 Computer Science done.")


# ===========================================================================
#  MAIN
# ===========================================================================

print("="*65)
print("  OlympiadReady - Computer Science Pixabay Grade 11 & 12")
print("  Olympiad difficulty | 15 questions per grade = 30 total")
print("="*65)

gen_gr11()
gen_gr12()

print(f"\n{'='*65}")
print(f"DONE - Posted: {posted}  Skipped: {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
print(f"{'='*65}")
