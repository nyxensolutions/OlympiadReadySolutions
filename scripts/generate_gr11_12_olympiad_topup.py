"""
generate_gr11_12_olympiad_topup.py
High-quality Olympiad top-up:
  - Computer Science Grade 11 (was 11, need 15+)
  - English Grade 12 (was 12, need 15+)
Questions are NCERT-plus competitive level with precise, unambiguous wording.
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
    print(f"\n{'='*65}\n  {title}\n{'='*65}")

# ─────────────────────────────────────────────────────────────────────────────
# COMPUTER SCIENCE — Grade 11 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_cs_gr11():
    section("Computer Science Grade 11 — Olympiad")
    qs = [
        ("Programming","Python — Data Types",
         "In Python 3, what is the output of: print(type(5 / 2))?",
         "<class 'float'>","<class 'int'>","<class 'double'>","<class 'number'>",
         "In Python 3, the / operator ALWAYS returns a float, even when dividing two integers: 5/2 = 2.5 (float). Use // for integer (floor) division: 5//2 = 2 (int)."),

        ("Programming","Python — String Operations",
         "What does the following Python code print?\n  s = 'OlympiadReady'\n  print(s[3:8])",
         "mpiad","lymp","Olymp","mpiadR",
         "Python slicing s[start:end] extracts characters from index start up to (but not including) end. s[3]='m', s[4]='p', s[5]='i', s[6]='a', s[7]='d'. Result: 'mpiad'."),

        ("Programming","Python — Lists",
         "What is the output of:\n  lst = [10, 20, 30, 40, 50]\n  lst.pop(2)\n  print(lst)",
         "[10, 20, 40, 50]","[10, 20, 30, 50]","[10, 30, 40, 50]","[20, 30, 40, 50]",
         "list.pop(index) removes and returns the element at that index. pop(2) removes index 2 = value 30. Remaining: [10, 20, 40, 50]."),

        ("Programming","Python — Dictionary",
         "What does this code print?\n  d = {'a': 1, 'b': 2, 'c': 3}\n  d['b'] = 10\n  del d['a']\n  print(sum(d.values()))",
         "13","6","12","16",
         "After d['b']=10: {'a':1, 'b':10, 'c':3}. After del d['a']: {'b':10, 'c':3}. sum of values = 10+3 = 13."),

        ("Programming","Python — Functions",
         "What is the output of:\n  def func(x, y=5):\n      return x * y\n  print(func(3), func(3, 2))",
         "15 6","10 6","15 15","6 15",
         "func(3) uses default y=5: 3*5=15. func(3,2) overrides default: 3*2=6. Output: '15 6'."),

        ("Data Structures","Arrays & Complexity",
         "Binary search on a sorted array of n elements has a time complexity of:",
         "O(log n)","O(n)","O(n log n)","O(1)",
         "Binary search halves the search space each step: n -> n/2 -> n/4 -> ... -> 1. This takes log2(n) steps. Time complexity = O(log n). Linear search = O(n)."),

        ("Networking","OSI Model",
         "In the OSI model, which layer is responsible for end-to-end data delivery, error recovery, and flow control between two applications?",
         "Transport Layer (Layer 4)","Network Layer (Layer 3)","Session Layer (Layer 5)","Data Link Layer (Layer 2)",
         "Transport Layer (TCP/UDP): provides end-to-end communication, segmentation, flow control, error recovery. TCP ensures reliable delivery; UDP is faster but unreliable. Network Layer handles routing (IP)."),

        ("Database","SQL",
         "Which SQL clause is used to filter groups AFTER a GROUP BY operation (not individual rows)?",
         "HAVING","WHERE","FILTER","GROUP FILTER",
         "WHERE filters individual rows BEFORE grouping. HAVING filters groups AFTER GROUP BY. Example: SELECT dept, COUNT(*) FROM employees GROUP BY dept HAVING COUNT(*) > 5;"),

        ("Programming","Recursion",
         "What does this Python function return for fact(5)?\n  def fact(n):\n      if n == 0: return 1\n      return n * fact(n-1)",
         "120","60","24","100",
         "Recursive factorial: fact(5)=5*fact(4)=5*4*fact(3)=5*4*3*fact(2)=5*4*3*2*fact(1)=5*4*3*2*1*fact(0)=5*4*3*2*1*1=120."),

        ("Programming","Python — File Handling",
         "Which mode opens a file for BOTH reading and writing WITHOUT truncating it (preserving existing content)?",
         "r+ (read and write, file must exist)","w+ (write and read, truncates)","a (append only)","rb (read binary)",
         "'r+' opens existing file for both reading and writing without truncating. 'w+' truncates to zero length first. 'a' only appends. For new+read/write use 'w+'; for existing+read/write use 'r+'."),

        ("Cybersecurity","Encryption",
         "In asymmetric encryption (e.g., RSA), a message encrypted with a user's PUBLIC key can ONLY be decrypted by:",
         "The user's PRIVATE key","The same public key","Any public key","A shared secret key",
         "Asymmetric cryptography uses key pairs. Data encrypted with the public key can ONLY be decrypted with the matching private key (which the owner keeps secret). This enables secure communication without sharing secret keys."),

        ("Data Structures","Stacks & Queues",
         "A stack follows LIFO (Last In, First Out). If you push 1, 2, 3, 4 onto a stack and then pop twice, what is the top of the stack?",
         "2","1","3","4",
         "Push order: 1,2,3,4. Stack (top to bottom): 4,3,2,1. Pop removes 4 (1st pop), then 3 (2nd pop). Top of stack is now 2."),

        ("Networking","IP & Protocols",
         "What is the purpose of the DNS (Domain Name System)?",
         "Translates human-readable domain names (e.g., google.com) into IP addresses (e.g., 142.250.80.46)","Assigns dynamic IP addresses to devices","Encrypts internet traffic","Manages email routing",
         "DNS is the internet's 'phone book' — it maps domain names to IP addresses so browsers can load websites. Without DNS, users would need to type IP addresses directly. DHCP assigns IPs; TLS/SSL encrypts traffic."),

        ("Programming","Python — OOP",
         "In Python, what is the purpose of the __init__ method in a class?",
         "It is the constructor — automatically called when a new object is created, to initialise its attributes","It destroys the object when done","It defines class-level (static) variables","It is called only when the class is defined, not when objects are made",
         "__init__ is Python's constructor/initialiser. Called automatically when you do obj = ClassName(). It sets up the object's initial state (instance variables). __del__ is the destructor. @staticmethod defines static methods."),

        ("Programming","Python — Exception Handling",
         "What will this code print?\n  try:\n      x = int('abc')\n  except ValueError:\n      print('caught')\n  finally:\n      print('done')",
         "caught\ndone","caught only","done only","Error — program crashes",
         "int('abc') raises ValueError (can't convert non-numeric string). The except ValueError block catches it -> prints 'caught'. The finally block ALWAYS executes regardless -> prints 'done'. Output: caught then done."),
    ]
    for q in qs:
        add("Computer Science", 11, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)
    print(f"  CS Gr11 done.")

# ─────────────────────────────────────────────────────────────────────────────
# ENGLISH — Grade 12 Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_eng_gr12():
    section("English Grade 12 — Olympiad")
    qs = [
        ("Literature","Poetry Analysis",
         "In Robert Frost's 'The Road Not Taken', the speaker takes the road 'less travelled by'. Literary scholars often argue the poem is actually about:",
         "Self-justification — both roads were equally worn; the speaker is fabricating uniqueness in hindsight to justify a choice","Regret for not taking the better path","The joy of being an explorer","The importance of following others",
         "Frost himself called this poem 'a tricky poem'. Both roads are described as 'equally worn' in stanzas 2-3. The speaker's claim of taking the 'less travelled' road in stanza 4 is a later rationalisation — the poem mocks our tendency to rewrite our own histories."),

        ("Grammar","Advanced Syntax",
         "Identify the type of clause underlined: 'She left early [so that she could catch the last train].'",
         "Adverbial clause of purpose","Adverbial clause of result","Noun clause","Relative clause",
         "'So that she could catch the last train' tells us WHY she left early — it modifies the verb 'left' and expresses purpose. Adverbial clauses of purpose use: so that, in order that, lest. Result clauses use: so...that, such...that."),

        ("Literature","Novel Analysis",
         "In George Orwell's '1984', the concept of 'doublethink' means:",
         "Holding two contradictory beliefs simultaneously and accepting both as true","Thinking twice before acting","A form of telepathy","Thinking in two languages at once",
         "Doublethink is the Party's psychological tool: e.g., 'War is Peace, Freedom is Slavery, Ignorance is Strength.' Citizens accept contradictions without perceiving them as contradictions — the ultimate form of thought control."),

        ("Writing","Argumentative Writing",
         "In a formal argumentative essay, the REFUTATION paragraph serves to:",
         "Acknowledge and then counter the opposing viewpoint, strengthening the writer's own argument","Introduce the main thesis","Summarise the essay","Provide statistics only",
         "Effective argumentation acknowledges counterarguments (shows intellectual honesty) then refutes them (shows logical strength). Ignoring opposing views weakens an argument; addressing and dismantling them strengthens it."),

        ("Grammar","Figures of Speech",
         "Identify the figure of speech: 'The pen is mightier than the sword.'",
         "Metaphor (abstract comparison without 'like' or 'as')","Simile","Personification","Hyperbole",
         "A metaphor makes a direct comparison between two unlike things without using 'like' or 'as'. The pen (writing/ideas) IS the sword (military power) — not like it. This famous Bulwer-Lytton phrase contrasts intellectual versus physical power."),

        ("Literature","Comprehension & Inference",
         "Read: 'Mr. Sharma arrived at the interview in a crumpled shirt, shoes unpolished, glancing repeatedly at his watch.' What can be MOST accurately inferred?",
         "He was unprepared and possibly anxious about the interview","He was confident and relaxed","He was late and indifferent","He did not want the job",
         "Inference: crumpled shirt and unpolished shoes = rushed/unprepared presentation. Glancing at watch = anxiety about time. Together these suggest unpreparedness and nervousness — not indifference (he showed up) or confidence."),

        ("Grammar","Reported Speech — Complex",
         "Report this question: She asked me, 'Have you ever been to Paris?'",
         "She asked me if I had ever been to Paris.","She asked me have I ever been to Paris.","She asked me that had I ever been to Paris.","She asked me whether have you been to Paris.",
         "Reporting a Yes/No question: use 'if' or 'whether' (not 'that'). Tense backshift: 'Have you' (present perfect) -> 'had I' (past perfect). Pronoun change: 'you' -> 'I' (relative to the reporter). No question mark in reported speech."),

        ("Vocabulary","Etymology & Word Formation",
         "The word 'philanthropy' comes from Greek 'philos' (loving) + 'anthropos' (human being). Based on this, what does 'misanthrope' mean?",
         "A person who dislikes or distrusts humanity in general","A generous charitable person","A lover of animals","A person who studies humans",
         "'Misos' (Greek) = hatred. Misanthrope = one who hates/distrusts humans. Philanthropist = one who loves humans (gives to help them). Etymology knowledge helps decode unfamiliar words from roots."),

        ("Literature","Prose — The Rattrap",
         "In Selma Lagerlof's 'The Rattrap', the peddler compares the world to a rattrap. The central irony is that:",
         "The ironmaster and his daughter, who represent 'bait' in the rat trap of wealth/kindness, ultimately redeem the peddler rather than trap him","The peddler himself is the rattrap","The rattrap metaphor only applies to poor people","There is no irony — the metaphor is straightforward",
         "The irony: the peddler expects the world (with its bait of wealth/kindness) to trap him. But Edla's genuine compassion and non-judgmental generosity breaks the cycle — the intended trap becomes a path to redemption."),

        ("Grammar","Clauses & Conditionals",
         "Which sentence expresses an UNREAL present condition (second conditional)?",
         "'If I were the Prime Minister, I would abolish poverty.' (unreal/hypothetical present)","'If it rains, I will stay home.' (real future)","'If he had studied, he would have passed.' (unreal past)","'If water boils, it turns to steam.' (universal truth)",
         "Second conditional: If + past simple/subjunctive, would + infinitive. Used for unreal/hypothetical present situations. 'Were' (not 'was') is correct in formal second conditional. Third conditional = unreal past (had + past participle)."),

        ("Literature","Poetry — Keeping Quiet",
         "In Pablo Neruda's 'Keeping Quiet', the poet asks everyone to keep still. The philosophical message is about:",
         "Collective introspection and non-violence — a moment of stillness to reflect on the self-destruction caused by human activity and wars","The importance of silence in daily life","Never speaking at all","Environmental pollution only",
         "Neruda's poem advocates for a universal pause from 'threatening ourselves with death' — wars, rushing, exploitation of nature. The stillness he advocates is not inaction but reflection that leads to understanding and coexistence."),

        ("Writing","Précis Writing",
         "In précis writing, the length of the précis should be approximately:",
         "One-third of the original passage","One-half","Two-thirds","One-quarter",
         "The standard rule for précis writing: reduce to 1/3rd of the original length. A 300-word passage becomes a ~100-word précis. The précis must retain all main ideas in continuous, coherent prose — no examples, no repetition."),

        ("Grammar","Voice — Complex Sentences",
         "Change to passive: 'The committee will announce the results tomorrow.'",
         "'The results will be announced by the committee tomorrow.'","'The results are announced by the committee tomorrow.'","'The results would have been announced tomorrow.'","'Tomorrow the committee announces the results.'",
         "Future active (will + base verb) -> Future passive (will + be + past participle). Subject 'committee' becomes agent (by the committee). Object 'results' becomes passive subject."),

        ("Literature","Lost Spring — Themes",
         "In Anees Jung's 'Lost Spring', the recurring motif of 'garbage' and 'gold' symbolises:",
         "The cruel paradox where children scavenge through waste (garbage) in search of something valuable (gold) — their stolen childhoods, lost in poverty","That poor children prefer garbage to gold","That gold is found in garbage dumps","The author's literal observation of recycling",
         "Jung uses this as an extended metaphor: children rummage through garbage literally (for scraps) but metaphorically search for the 'gold' of a dignified life, education, and childhood — all stolen by systemic poverty and social indifference."),

        ("Vocabulary","Idioms & Phrases in Context",
         "Choose the correct meaning of the idiom in: 'After years of struggle, the startup finally turned the corner last quarter.'",
         "Passed the most difficult phase and began to improve/succeed","Literally turned around a corner on a road","Changed its business direction suddenly","Went bankrupt",
         "'Turn the corner' = to pass the hardest part of a difficult situation and begin to improve. Idioms cannot be interpreted literally. Context: 'after years of struggle' + 'finally' = beginning of success after difficulty."),
    ]
    for q in qs:
        add("English", 12, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)
    print(f"  English Gr12 done.")

if __name__ == "__main__":
    print("=" * 65)
    print("  OlympiadReady -- Gr11/12 Olympiad Top-up")
    print("=" * 65)
    gen_cs_gr11()
    gen_eng_gr12()
    print(f"\n{'='*65}")
    print(f"DONE -- Posted: {POSTED}  Skipped(dup): {SKIPPED}  Failed: {FAILED}")
    print(f"{'='*65}")
