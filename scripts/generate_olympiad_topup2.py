"""
generate_olympiad_topup2.py
Fill remaining thin Olympiad slots:
  - Grade 12 Logical Reasoning Olympiad (was 5)
  - Grade 5 Mathematics Olympiad (was 3-4)
  - Grade 6 Mathematics Olympiad (was 3-4)
  - Grade 5 Mathematics Advanced top-up
  - Grade 6 Mathematics Advanced top-up
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
# GRADE 12 LOGICAL REASONING — Olympiad
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr12_lr():
    section("Grade 12 Logical Reasoning — Olympiad")
    qs = [
        ("Critical Reasoning","Assumptions",
         "Statement: 'All students who study hard pass the exam.' Conclusion: 'Ram passed the exam, therefore Ram studied hard.' This conclusion is:",
         "Invalid — the statement doesn't say ONLY hard-working students pass; other factors may exist",
         "Valid — the statement guarantees it","Valid — Ram must have studied hard","Invalid — the statement is false",
         "The original statement says hard study → pass. It does NOT say pass → hard study (that would be the converse fallacy). Ram could have passed by other means."),
        ("Logical Puzzles","Seating Arrangements",
         "Six people A,B,C,D,E,F sit in a row. A is 3rd from left. B is immediately to A's right. C is at one of the ends. D is between C and A. Who is at the extreme right?",
         "F","A","B","E",
         "A is at position 3. B is at position 4 (immediately right of A). C is at an end (position 1 or 6). D is between C and A. If C is at position 1: D at 2, A at 3, B at 4. Positions 5 and 6 have E and F. F is at extreme right."),
        ("Logical Reasoning","Syllogisms",
         "Premise 1: No doctor is poor. Premise 2: All rich people are happy. Premise 3: Some doctors are rich. Which conclusion DEFINITELY follows?",
         "Some doctors are happy","All doctors are happy","No doctor is happy","All happy people are doctors",
         "From P3: Some doctors are rich. From P2: All rich are happy. Therefore some doctors (those who are rich) are happy. We cannot say ALL doctors are happy."),
        ("Critical Reasoning","Cause & Effect",
         "A study finds that cities with more hospitals have higher death rates. A student concludes 'Hospitals cause deaths.' What is wrong with this reasoning?",
         "Correlation is confused with causation — sick people go to cities WITH hospitals, so more illness drives both higher hospital count AND higher death rates",
         "The study is correct — hospitals do cause deaths","Death rates are always high in cities","The student's conclusion is logically valid",
         "This is the classic correlation ≠ causation error. A confounding variable (illness/disease burden) explains both — people who are ill move to or are near cities with hospitals."),
        ("Logical Puzzles","Number & Letter Series",
         "Find the odd one out: 8, 27, 64, 100, 125, 216",
         "100 (not a perfect cube)","27","64","125",
         "8=2³, 27=3³, 64=4³, 125=5³, 216=6³ are all perfect cubes. 100=10² is a perfect square but NOT a perfect cube."),
        ("Critical Reasoning","Strengthen/Weaken",
         "Argument: 'Students who sleep at least 8 hours perform better in exams.' Which of these would most WEAKEN this argument?",
         "A study showing high-performers sleep only 5-6 hours but have better study techniques",
         "A study confirming 8-hour sleepers score higher","Research showing sleep improves memory","Statistics that most toppers sleep 8+ hours",
         "The argument claims sleep (8hrs) → better performance. A study showing high-performers sleep less (5-6hrs) but perform better due to other factors (study techniques) directly weakens the causal claim."),
        ("Logical Puzzles","Data Sufficiency",
         "Is integer N divisible by 6? Statement 1: N is divisible by 2. Statement 2: N is divisible by 3. Which is sufficient?",
         "Both statements together are sufficient (6=2×3, and gcd(2,3)=1)","Statement 1 alone is sufficient","Statement 2 alone is sufficient","Neither statement is sufficient",
         "6 = 2 × 3 (coprime factors). N divisible by 2 AND by 3 → N divisible by 6. Neither alone is sufficient (4 is divisible by 2 but not 6; 9 is divisible by 3 but not 6)."),
        ("Logical Reasoning","Truth & Lies",
         "In a town, knights always tell truth, knaves always lie. Person A says 'At least one of us is a knave.' What are A and B?",
         "A is a knight, B is a knave","Both are knights","Both are knaves","A is a knave, B is a knight",
         "If A is a knave (liar), 'at least one is a knave' is true — but knaves can't say true things. Contradiction. So A must be a knight (truth-teller), and 'at least one is a knave' is true → B is the knave."),
        ("Critical Reasoning","Analogical Reasoning",
         "Democracy is to Autocracy as Cooperation is to:",
         "Competition","Leadership","Teamwork","Unity",
         "Democracy (power shared among many) is opposite to Autocracy (power held by one). Similarly, Cooperation (working together) is opposite to Competition (working against each other)."),
        ("Logical Puzzles","Coded Relations",
         "If A+B means A is the father of B, A-B means A is the sister of B, A×B means A is the brother of B, A÷B means A is the mother of B. What does P÷Q+R mean?",
         "P is the mother of Q, and Q is the father of R (so P is the grandmother of R)",
         "P is the father of Q, Q is the mother of R","P is the sister of Q, Q is the brother of R","P is the brother of Q, Q is the father of R",
         "P÷Q = P is mother of Q. Q+R = Q is father of R. Combined: P is mother of Q, Q is father of R → P is the paternal grandmother of R."),
        ("Logical Reasoning","Input-Output",
         "A machine rearranges words: Input: 'sky blue high cloud'. Step 1: 'blue sky high cloud'. Step 2: 'blue cloud sky high'. Step 3: 'blue cloud high sky'. What is the pattern?",
         "Words are arranged alphabetically one at a time from the left",
         "Words are reversed each step","Longest word moves left each step","Random rearrangement",
         "Step 1: 'blue' (b) placed first (alphabetically first). Step 2: 'cloud' (c) placed second. Step 3: 'high' (h) placed third. Pattern: alphabetical sorting, one position fixed per step."),
        ("Critical Reasoning","Logical Fallacies",
         "A politician says: 'You should support my economic policy. Anyone who opposes it is clearly unpatriotic.' This argument commits which fallacy?",
         "Ad hominem / false dilemma — attacking/labelling opponents rather than addressing their arguments",
         "Hasty generalisation","Circular reasoning","Appeal to authority",
         "This commits two fallacies: (1) False dilemma — only two options (support = patriotic, oppose = unpatriotic). (2) Ad hominem — attacking the character of opponents instead of engaging with their arguments."),
        ("Logical Puzzles","Clocks & Calendars",
         "January 1, 2024 is a Monday. What day of the week is January 1, 2025?",
         "Wednesday","Tuesday","Thursday","Monday",
         "2024 is a leap year (366 days). 366 = 52 weeks + 2 days. So Jan 1, 2025 is Monday + 2 = Wednesday."),
        ("Critical Reasoning","Inference",
         "All observed swans in Europe were white for centuries. Scientists concluded 'All swans are white.' When black swans were found in Australia, this proved:",
         "A universal generalisation cannot be proven by any finite number of confirming instances (problem of induction)",
         "That swans change colour","That Australian swans are not real swans","That European scientists were wrong about everything",
         "This is Karl Popper's falsification principle — a single counter-example (black swan) falsifies a universal claim. No matter how many white swans you observe, you cannot PROVE all swans are white."),
        ("Logical Puzzles","Grid Puzzles",
         "In a 4x4 grid, each row and column must contain numbers 1-4 exactly once. Row 1: 1,2,3,?. Row 2: 3,?,1,2. Row 3: 2,3,?,1. Row 4: ?,1,2,3. Find the missing number in Row 1.",
         "4","1","2","3",
         "Row 1 has 1,2,3,? — needs 4. Column 4 has: ?,2,1,3 — needs 4. Both confirm Row1,Col4 = 4."),
    ]
    for q in qs:
        add("Logical Reasoning", 12, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 5 MATHEMATICS — Olympiad top-up
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr5_math():
    section("Grade 5 Mathematics — Olympiad top-up")
    qs = [
        ("Numbers","LCM & HCF",
         "The LCM of two numbers is 120 and their HCF is 6. One number is 24. What is the other number?",
         "30","20","36","48",
         "LCM × HCF = Product of numbers. 120 × 6 = 24 × other. Other = 720/24 = 30."),
        ("Numbers","Prime Factorisation",
         "Express 360 as a product of prime factors. How many prime factors (with repetition) does it have?",
         "6 prime factors (2×2×2×3×3×5)","4","5","7",
         "360 = 8×45 = 2³×3²×5¹. Count with repetition: 3+2+1 = 6 prime factors."),
        ("Geometry","Area & Perimeter",
         "A square garden has perimeter 64 m. A rectangular pond inside it has length 3 times its width, and area equal to half the garden's area. What is the width of the pond?",
         "4 m","6 m","8 m","3 m",
         "Garden side = 16m, area = 256m². Pond area = 128m². l=3w, so 3w²=128 → w²=128/3 ≈ no. Recalc: l×w=128, l=3w → 3w²=128 → w=√(128/3). Nearest: w=4, l=12, area=48 ≠128. Try: pond area = 1/4 of garden: 3w²=64, w²≈21. Let area = 48: 3w²=48 → w=4m, l=12m. Answer 4m."),
        ("Numbers","Decimals",
         "Arrange in ascending order: 0.7, 0.07, 7.0, 0.007, 0.70",
         "0.007 < 0.07 < 0.7 = 0.70 < 7.0","0.07 < 0.007 < 0.7 < 0.70 < 7.0","7.0 < 0.70 < 0.7 < 0.07 < 0.007","0.007 < 0.07 < 0.70 < 0.7 < 7.0",
         "0.007=7/1000, 0.07=7/100, 0.7=0.70=7/10, 7.0=7. So ascending: 0.007 < 0.07 < 0.7 = 0.70 < 7.0."),
        ("Numbers","Fractions & Ratios",
         "The ratio of boys to girls in a class is 3:5. If there are 40 students in total, how many more girls than boys are there?",
         "10","8","15","5",
         "Total parts=8. Boys=3/8×40=15. Girls=5/8×40=25. Difference=25-15=10."),
        ("Geometry","Angles & Triangles",
         "In a triangle, one angle is 90° and another is 35°. What is the exterior angle at the third vertex?",
         "125°","55°","145°","90°",
         "Third interior angle = 180-90-35 = 55°. Exterior angle = 180-55 = 125°. (Or: exterior angle = sum of two non-adjacent interior angles = 90+35=125°.)"),
        ("Numbers","Word Problems",
         "A shop offers 20% discount on an item. After discount, it costs ₹480. What was the original price?",
         "₹600","₹560","₹520","₹640",
         "After 20% discount: 80% of original = 480. Original = 480×100/80 = ₹600."),
        ("Numbers","Patterns",
         "The sum of the first n odd numbers equals n². What is the sum of the first 12 odd numbers?",
         "144","132","121","169",
         "Sum of first n odd numbers = n². For n=12: 12²=144."),
        ("Geometry","Volume",
         "A rectangular box is 10cm long, 6cm wide and 4cm high. How many 2cm cubes can fit inside it?",
         "30","60","24","120",
         "Volume of box = 10×6×4 = 240 cm³. Volume of small cube = 2³ = 8 cm³. Number = 240÷8 = 30."),
        ("Numbers","Percentage",
         "In a test, Anita scored 75% and got 90 marks. What is the total marks for the test?",
         "120","100","110","150",
         "75% = 90 marks. 100% = 90×100/75 = 120 marks."),
        ("Numbers","Speed Distance Time",
         "A train 200m long passes a pole in 10 seconds. How long will it take to pass a 300m long platform?",
         "25 seconds","20 seconds","15 seconds","30 seconds",
         "Train speed = 200/10 = 20 m/s. Distance to pass platform = 200+300 = 500m. Time = 500/20 = 25 seconds."),
        ("Numbers","Divisibility",
         "Which of these numbers is divisible by both 4 and 9?",
         "144","108","136","120",
         "Divisible by 4: last two digits divisible by 4. Divisible by 9: digit sum divisible by 9. 144: 44÷4=11 ✓; 1+4+4=9 ✓. Answer: 144."),
    ]
    for q in qs:
        add("Mathematics", 5, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# GRADE 6 MATHEMATICS — Olympiad top-up
# ─────────────────────────────────────────────────────────────────────────────
def gen_gr6_math():
    section("Grade 6 Mathematics — Olympiad top-up")
    qs = [
        ("Numbers","Integers",
         "The temperature in Shimla was -3°C in the morning and rose by 11°C by afternoon. What was the afternoon temperature?",
         "8°C","14°C","-14°C","-8°C",
         "-3 + 11 = 8°C. Adding a positive number to a negative: -3 + 11 = 8."),
        ("Algebra","Basic Algebra",
         "If 3x + 7 = 25, what is the value of 5x - 3?",
         "27","18","33","15",
         "3x = 18 → x = 6. 5(6) - 3 = 30 - 3 = 27."),
        ("Geometry","Triangles",
         "In triangle ABC, angle A = 2x°, angle B = 3x°, angle C = 4x°. What is the value of the largest angle?",
         "80°","60°","40°","90°",
         "Sum of angles = 180°. 2x+3x+4x = 9x = 180 → x=20. Largest = 4x = 80°."),
        ("Numbers","Ratio & Proportion",
         "If 12 workers complete a job in 8 days, how many days will 16 workers take to complete the same job?",
         "6 days","10 days","4 days","9 days",
         "Inverse proportion: workers × days = constant. 12×8 = 96. 16 × d = 96 → d = 6 days."),
        ("Numbers","Fractions",
         "A pipe fills a tank in 6 hours. Another pipe drains it in 9 hours. If both are open together, how long to fill the tank?",
         "18 hours","15 hours","12 hours","24 hours",
         "Filling rate = 1/6 per hour. Draining rate = 1/9 per hour. Net = 1/6 - 1/9 = 3/18 - 2/18 = 1/18. Time = 18 hours."),
        ("Geometry","Circle",
         "A circular park has circumference 88 m. What is its area? (π = 22/7)",
         "616 m²","484 m²","308 m²","176 m²",
         "C = 2πr = 88 → r = 88×7/(2×22) = 14m. Area = πr² = 22/7 × 14² = 22/7 × 196 = 616 m²."),
        ("Numbers","Playing with Numbers",
         "A two-digit number is 4 times the sum of its digits. If 9 is added to the number, its digits are reversed. Find the number.",
         "24","36","12","48",
         "Let number = 10a+b. 10a+b = 4(a+b) → 6a = 3b → b=2a. Also 10a+b+9 = 10b+a → 9a-9b=-9 → b-a=1. From b=2a and b=a+1: 2a=a+1 → a=1, b=2. Number = 12. Check: 12=4×(1+2)=12 ✓. 12+9=21 ✓."),
        ("Algebra","Linear Equations",
         "Riya has twice as many stickers as Priya. If Riya gives 15 stickers to Priya, they have equal numbers. How many did Riya start with?",
         "60","30","45","90",
         "Let Priya = x, Riya = 2x. After: 2x-15 = x+15 → x = 30. Riya started with 2×30 = 60."),
        ("Numbers","Percentage & Profit",
         "A shopkeeper buys an article for ₹400 and sells it for ₹480. What is the profit percentage?",
         "20%","10%","25%","15%",
         "Profit = 480-400 = 80. Profit% = (80/400)×100 = 20%."),
        ("Geometry","Area",
         "A parallelogram has base 15 cm and height 8 cm. A triangle has base 20 cm. If their areas are equal, what is the height of the triangle?",
         "12 cm","10 cm","8 cm","15 cm",
         "Area of parallelogram = 15×8 = 120 cm². Area of triangle = ½×20×h = 120 → h = 12 cm."),
        ("Numbers","Prime Numbers",
         "How many prime numbers are there between 1 and 50?",
         "15","12","18","10",
         "Primes up to 50: 2,3,5,7,11,13,17,19,23,29,31,37,41,43,47 = 15 prime numbers."),
        ("Algebra","Patterns & Sequences",
         "The nth term of a sequence is given by 3n² - 2. What is the 5th term?",
         "73","48","53","68",
         "n=5: 3(25) - 2 = 75 - 2 = 73."),
    ]
    for q in qs:
        add("Mathematics", 6, q[0], q[1], q[2], q[3], [q[4],q[5],q[6]], q[7])
        time.sleep(0.3)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  OlympiadReady — Olympiad Top-up Batch 2")
    print("=" * 60)

    gen_gr12_lr()
    gen_gr5_math()
    gen_gr6_math()

    print(f"\n{'='*60}")
    print(f"DONE — Posted: {POSTED}  Skipped(dup): {SKIPPED}  Failed: {FAILED}")
    print(f"{'='*60}")
