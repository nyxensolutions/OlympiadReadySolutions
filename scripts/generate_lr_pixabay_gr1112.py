"""
generate_lr_pixabay_gr1112.py
High-quality Pixabay images -> Logical Reasoning Grade 11 & 12.
Olympiad difficulty | 15 questions per grade = 30 total.

QUALITY RULES:
  1. Pixabay query matches exactly what is visible in the photo.
  2. Question references the visible element (clock face, chart, compass etc.).
  3. No question asks about invisible details the photo cannot show.
  4. Every question is self-contained; the image provides context not a crutch.
  5. All numerical answers are independently verified before writing.
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
        pub_id = f"{CLOUDINARY_FOLDER}/lr_{query[:26].replace(' ','-')}_{RUN_ID}_{hit['id']}"
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
                          json=payload, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            posted += 1; return True
        elif r.status_code == 409:
            skipped += 1; return False
        else:
            print(f"    [FAIL {r.status_code}] {text[:60]}"); failed += 1; return False
    except Exception as e:
        print(f"    [ERR] {e}"); failed += 1; return False


def add_img(subject, grade, topic, subtopic, query, text, correct, wrongs, expl, pix_idx=0, difficulty="Olympiad"):
    tag = f"G{grade} LR {query[:30]}..."
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
#  LOGICAL REASONING GRADE 11  (15 questions)
# ===========================================================================

def gen_gr11():
    print("\n" + "="*65)
    print("  Logical Reasoning Grade 11  (15 questions)")
    print("="*65)
    S, G = "Logical Reasoning", 11

    # 1. Clock — Angle between hands
    add_img(S, G, "Clock and Calendar", "Angle Between Hands",
        query="analog clock face time",
        text="The clock shown displays 3:20. What is the angle between the hour and minute hands at this time?",
        correct="20°",
        wrongs=["10°", "30°", "40°"],
        expl="At 3:20, minute hand is at 120° (20×6). Hour hand is at 100° (3×30 + 20×0.5 = 90+10). Angle = 120−100 = 20°.")

    # 2. Calendar — Day calculation
    add_img(S, G, "Clock and Calendar", "Day of the Week",
        query="calendar month dates wall",
        text="A calendar shows January 1 falls on a Wednesday. What day of the week is January 31 of the same year?",
        correct="Friday",
        wrongs=["Thursday", "Saturday", "Wednesday"],
        expl="Jan 1 = Wednesday. Jan 31 = Jan 1 + 30 days. 30 = 4 weeks + 2 days. Wednesday + 2 = Friday.")

    # 3. Compass / Direction — Distance and direction
    add_img(S, G, "Direction and Distance", "Final Direction",
        query="compass direction navigation outdoor",
        text="Using the compass shown: Ravi starts facing North, turns 90° clockwise, walks 5 km, then turns 90° anti-clockwise. Which direction is he now facing?",
        correct="North",
        wrongs=["East", "South", "West"],
        expl="Start: North. Turn 90° CW → East. Then turn 90° anti-CW (back) → North. He is facing North again.")

    # 4. Bar chart — Data Interpretation
    add_img(S, G, "Data Interpretation", "Bar Graph",
        query="bar chart statistics comparison data",
        text="A bar chart shows sales: Mon=120, Tue=150, Wed=90, Thu=180, Fri=160. What is the average daily sales for the week?",
        correct="140",
        wrongs=["150", "130", "145"],
        expl="Total = 120+150+90+180+160 = 700. Average = 700÷5 = 140.")

    # 5. Pie chart — Percentage reasoning
    add_img(S, G, "Data Interpretation", "Pie Chart",
        query="pie chart percentage statistics",
        text="A pie chart shows a monthly budget: Rent 30%, Food 25%, Transport 15%, Savings 20%, Misc 10%. If total income is ₹40,000, how much is saved?",
        correct="₹8,000",
        wrongs=["₹10,000", "₹6,000", "₹12,000"],
        expl="Savings = 20% of ₹40,000 = 0.20 × 40,000 = ₹8,000.")

    # 6. Dice — Opposite faces
    add_img(S, G, "Spatial Reasoning", "Dice and Cubes",
        query="dice six faces numbers",
        text="A standard die is shown. On a standard die, opposite faces always sum to 7. If the face showing 2 is visible, which face is directly opposite?",
        correct="5",
        wrongs=["4", "6", "3"],
        expl="On a standard die, opposite faces sum to 7. Opposite of 2 = 7 − 2 = 5.")

    # 7. Mirror image — Reflection reasoning
    add_img(S, G, "Spatial Reasoning", "Mirror Images",
        query="mirror reflection symmetry object",
        text="When the word 'LOGIC' is held in front of a vertical mirror, the mirror image shows the letters in which order?",
        correct="CIGOL (reversed left-to-right)",
        wrongs=["LOGIC (unchanged)", "CIGOL (upside down)", "LOGIC (upside down)"],
        expl="A vertical mirror reverses left and right. Each letter also flips horizontally. The word reads backwards: CIGOL with each letter mirrored.")

    # 8. Puzzle / Jigsaw — Analogy reasoning
    add_img(S, G, "Analogies", "Letter and Word Analogies",
        query="puzzle pieces jigsaw complete",
        text="Just as puzzle pieces fit together to complete a whole image, complete the analogy: BDFH : ACEG :: LNPR : ?",
        correct="KMOQ",
        wrongs=["MNOP", "JLNP", "KMOP"],
        expl="BDFH are even letters (2,4,6,8); ACEG are odd letters one before each (1,3,5,7). Similarly LNPR are even letters (12,14,16,18); the odd letters one before = KMOQ (11,13,15,17).")

    # 9. Number sequence on chalkboard — Number series
    add_img(S, G, "Series and Sequences", "Number Series",
        query="mathematics chalkboard numbers sequence",
        text="A series is written on the board: 3, 6, 11, 18, 27, 38, ?. What is the next term?",
        correct="51",
        wrongs=["47", "49", "53"],
        expl="Differences: 3,5,7,9,11,13 (increasing odd numbers). 38 + 13 = 51.")

    # 10. Blood relation — Family photo
    add_img(S, G, "Blood Relations", "Family Relationships",
        query="family portrait parents children",
        text="In a family photo: Pointing to a man, a woman says 'His mother is the only daughter of my mother.' How is the woman related to the man?",
        correct="Mother",
        wrongs=["Aunt", "Sister", "Grandmother"],
        expl="'Only daughter of my mother' = the woman herself. So the man's mother is the woman herself. Therefore, the woman is the man's Mother.")

    # 11. Flowchart — Input-Output / Sequential reasoning
    add_img(S, G, "Logical Sequences", "Input-Output",
        query="flowchart diagram decision process",
        text="A flowchart processes numbers: Input → Multiply by 3 → Add 5 → Divide by 2 → Output. If the input is 7, what is the output?",
        correct="13",
        wrongs=["11", "15", "12"],
        expl="Step 1: 7 × 3 = 21. Step 2: 21 + 5 = 26. Step 3: 26 ÷ 2 = 13.")

    # 12. Maze — Direction / Path reasoning
    add_img(S, G, "Direction and Distance", "Shortest Path",
        query="maze puzzle path solution",
        text="A person enters a maze and makes these moves: 4 km North, 3 km East, 4 km South, 1 km West. What is the straight-line distance from the start?",
        correct="2 km",
        wrongs=["5 km", "3 km", "4 km"],
        expl="N and S cancel (4 km N − 4 km S = 0). Net East movement = 3 − 1 = 2 km. Straight-line distance = 2 km due East.")

    # 13. Seating arrangement — Ranking
    add_img(S, G, "Arrangements", "Linear Seating Arrangement",
        query="chairs row seats empty auditorium",
        text="In a row of seats, Priya is 8th from the left and 13th from the right. How many seats are there in total?",
        correct="20",
        wrongs=["21", "19", "22"],
        expl="Total = Position from left + Position from right − 1 = 8 + 13 − 1 = 20.")

    # 14. Venn diagram — Syllogism
    add_img(S, G, "Syllogisms", "Venn Diagram Method",
        query="venn diagram three circles overlap",
        text="Using the Venn diagram method for syllogisms: All Roses are Flowers. All Flowers are Plants. Which conclusion is definitely true?",
        correct="All Roses are Plants",
        wrongs=["All Plants are Roses", "Some Plants are not Flowers", "No Rose is a Plant"],
        expl="If Roses ⊆ Flowers and Flowers ⊆ Plants, then by transitivity Roses ⊆ Plants. Therefore 'All Roses are Plants' is definitely true.")

    # 15. Coding — Number/letter keyboard
    add_img(S, G, "Coding and Decoding", "Letter Coding",
        query="keyboard letters alphabet typewriter",
        text="In a coding system, APPLE is coded as DSSOH. Each letter is shifted forward by 3 positions in the alphabet. How would MANGO be coded?",
        correct="PDQJR",
        wrongs=["NBOHP", "OCZIQ", "OCQJR"],
        expl="Shift each letter +3: M→P, A→D, N→Q, G→J, O→R. Coded word = PDQJR.")

    print("  Grade 11 Logical Reasoning done.")


# ===========================================================================
#  LOGICAL REASONING GRADE 12  (15 questions)
# ===========================================================================

def gen_gr12():
    print("\n" + "="*65)
    print("  Logical Reasoning Grade 12  (15 questions)")
    print("="*65)
    S, G = "Logical Reasoning", 12

    # 1. Clock — Time gained/lost
    add_img(S, G, "Clock and Calendar", "Clocks Gaining/Losing Time",
        query="analog clock wall time",
        text="A clock gains 2 minutes every hour. It shows the correct time at 8:00 AM. What time will it show when the actual time is 6:00 PM the same day?",
        correct="6:20 PM",
        wrongs=["6:40 PM", "5:40 PM", "6:10 PM"],
        expl="Elapsed actual time = 10 hours. Clock gains 2 min/hr × 10 hrs = 20 minutes. Clock shows 6:00 PM + 20 min = 6:20 PM.")

    # 2. Line graph — Data interpretation trend
    add_img(S, G, "Data Interpretation", "Line Graph Trend Analysis",
        query="line graph trend statistics business",
        text="A line graph shows revenue (in lakhs): 2019=40, 2020=32, 2021=48, 2022=56, 2023=60. What is the percentage increase from 2020 to 2023?",
        correct="87.5%",
        wrongs=["50%", "75%", "100%"],
        expl="Increase = 60 − 32 = 28. % increase = (28/32) × 100 = 87.5%.")

    # 3. Direction — Shadow reasoning
    add_img(S, G, "Direction and Distance", "Shadow-Based Direction",
        query="shadow sunlight ground direction",
        text="At 6:00 AM, a person's shadow falls directly to the West, as seen in the image. Which direction is the person facing?",
        correct="East",
        wrongs=["West", "North", "South"],
        expl="At sunrise (6 AM), the sun is in the East. Shadows fall opposite to the sun — i.e., to the West. If the shadow is to the West, the person faces East (towards the sun).")

    # 4. Table / matrix — Data sufficiency
    add_img(S, G, "Data Interpretation", "Table Data Analysis",
        query="data table rows columns statistics",
        text="A table shows scores of 5 students (out of 100): A=72, B=88, C=65, D=91, E=79. What is the median score?",
        correct="79",
        wrongs=["72", "88", "80"],
        expl="Arranged in order: 65, 72, 79, 88, 91. The middle (3rd) value of 5 scores = 79. (Note: 79 is the correct answer.)")

    # 5. Sudoku grid — Logical deduction
    add_img(S, G, "Logical Deduction", "Matrix Completion",
        query="sudoku puzzle grid numbers",
        text="In a 3×3 Latin square, each row and column must contain digits 1, 2, 3 exactly once. Row 1: [1, 2, 3], Row 2: [2, 3, 1], Row 3: [3, ?, 2]. What digit fills the '?' position?",
        correct="1",
        wrongs=["2", "3", "4"],
        expl="Row 3 already has 3 and 2, so it needs 1. Column 2 already has 2 (Row 1) and 3 (Row 2), so it also needs 1. Both constraints agree: ? = 1.")

    # 6. Ranking from both ends — Arrangement
    add_img(S, G, "Arrangements", "Ranking from Both Ends",
        query="queue people standing line waiting",
        text="In a queue shown, Ankur is 11th from the front and 19th from the back. Meera is 5 places behind Ankur. What is Meera's position from the front?",
        correct="16th",
        wrongs=["15th", "17th", "14th"],
        expl="Total = 11 + 19 − 1 = 29 people. Ankur is 11th from front. Meera is 5 behind Ankur = 11 + 5 = 16th from front.")

    # 7. Critical reasoning — Newspaper/statement
    add_img(S, G, "Critical Reasoning", "Assumptions and Conclusions",
        query="newspaper headline reading information",
        text="A headline reads: 'Exercise reduces the risk of heart disease.' Which assumption is implicit in this statement?",
        correct="Heart disease risk can be influenced by lifestyle choices",
        wrongs=["All people who exercise will never get heart disease", "Heart disease is always fatal", "Only exercise prevents heart disease"],
        expl="The statement implies that lifestyle factors (exercise) can affect disease risk. The implicit assumption is that heart disease risk is modifiable — not fixed — which allows exercise to make a difference.")

    # 8. Cause and Effect — Traffic image
    add_img(S, G, "Critical Reasoning", "Cause and Effect",
        query="traffic jam congestion road cars",
        text="Statement I: There was heavy rain in the city yesterday. Statement II: Several roads in the city were flooded and traffic was severely disrupted. Which is the most logical relationship?",
        correct="Statement I is the cause; Statement II is the effect",
        wrongs=["Statement II is the cause; Statement I is the effect", "Both are independent events", "Both are effects of a common cause"],
        expl="Heavy rain (I) directly causes road flooding and traffic disruption (II). This is a clear cause-and-effect relationship where the natural phenomenon precedes and produces the consequence.")

    # 9. Binary/coded message — Coding decoding
    add_img(S, G, "Coding and Decoding", "Number-Letter Coding",
        query="binary code numbers screen computer",
        text="In a coding system: 4 = D, 5 = E, 18 = R, 19 = S, 20 = T. The coded message '4-5-19-11' represents DESK. What number codes 'K'?",
        correct="11",
        wrongs=["10", "12", "13"],
        expl="The coding system is positional: A=1, B=2, ..., K=11, ... So K = 11. DESK = 4,5,19,11 confirms: D=4, E=5, S=19, K=11.")

    # 10. Statement and argument — Debate / discussion image
    add_img(S, G, "Critical Reasoning", "Statement and Argument",
        query="debate discussion argument people talking",
        text="Statement: 'Should social media use be restricted for students under 18?' Argument: 'Yes, because excessive social media use is linked to anxiety and reduced academic performance in teenagers.' Is this argument Strong or Weak?",
        correct="Strong — it is relevant, specific, and evidence-based",
        wrongs=["Weak — it does not address all students equally", "Weak — restrictions would violate freedom of expression", "Strong — any restriction on minors is automatically valid"],
        expl="A strong argument is directly relevant to the statement and backed by credible reasoning. This argument links social media to concrete harms (anxiety, academic impact) in the target group (teenagers), making it strong and specific.")

    # 11. Logical sequence — Steps in a process
    add_img(S, G, "Logical Sequences", "Sequence of Events",
        query="steps ladder process stages",
        text="Arrange the steps of the scientific method in the correct logical order: (P) Form hypothesis, (Q) Conduct experiment, (R) Observe phenomenon, (S) Draw conclusion, (T) Analyse data.",
        correct="R → P → Q → T → S",
        wrongs=["P → R → Q → S → T", "R → Q → P → T → S", "Q → R → P → T → S"],
        expl="Scientific method: Observe (R) → Hypothesize (P) → Experiment (Q) → Analyse data (T) → Conclude (S). Observation always precedes hypothesis formation.")

    # 12. Series — Letter and number mixed
    add_img(S, G, "Series and Sequences", "Mixed Series",
        query="alphabet letters sequence pattern board",
        text="Find the next term in the series: Z1, X4, V9, T16, R25, ?",
        correct="P36",
        wrongs=["P25", "Q36", "O36"],
        expl="Letters skip one backwards: Z,X,V,T,R,P. Numbers are perfect squares: 1,4,9,16,25,36. Next term = P36.")

    # 13. Set theory / Venn — Three overlapping sets
    add_img(S, G, "Syllogisms", "Three-Statement Syllogism",
        query="three circles venn diagram overlapping",
        text="In a survey of 100 students: 60 play Cricket, 45 play Football, 30 play both. How many play neither sport?",
        correct="25",
        wrongs=["30", "15", "35"],
        expl="By inclusion-exclusion: Cricket or Football = 60 + 45 − 30 = 75. Neither = 100 − 75 = 25.")

    # 14. Input-output machine — Complex operation
    add_img(S, G, "Logical Sequences", "Input-Output Machine",
        query="machine gear mechanism process industrial",
        text="A machine processes inputs: Input 5 → Output 28; Input 7 → Output 52; Input 9 → Output 84. What is the output for Input 11?",
        correct="124",
        wrongs=["120", "116", "132"],
        expl="The rule is n^2 + 3. Check: 5^2+3=28, 7^2+3=52, 9^2+3=84. For n=11: 121+3=124.")

    # 15. Circular permutations — round table
    add_img(S, G, "Arrangements", "Circular Permutations",
        query="round table meeting circular seats",
        text="8 people are to be seated around the circular table shown. In how many distinct ways can they be arranged if two specific people (P and Q) must always sit next to each other?",
        correct="1 440",
        wrongs=["5 040", "720", "2 880"],
        expl="Treat P and Q as one block -> 7 entities around a circle. Circular arrangements = (7-1)! = 6! = 720. P and Q can swap within the block: x 2. Total = 720 x 2 = 1440.")

    print("  Grade 12 Logical Reasoning done.")


# ===========================================================================
#  MAIN
# ===========================================================================

print("="*65)
print("  OlympiadReady - Logical Reasoning Pixabay Gr 11 & 12")
print("  Olympiad difficulty | 15 questions per grade = 30 total")
print("="*65)

gen_gr11()
gen_gr12()

print(f"\n{'='*65}")
print(f"DONE - Posted: {posted}  Skipped: {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
print(f"{'='*65}")
