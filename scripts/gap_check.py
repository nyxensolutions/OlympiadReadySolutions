"""
gap_check.py
Query the staging DB and print a gap analysis report:
- Total questions per grade/subject/difficulty
- Image coverage per grade/subject
- Thin slots (< 10 Olympiad, < 20 total)
"""

import pyodbc, os
from collections import defaultdict

SERVER   = "olympiadready-np.database.windows.net"
DATABASE = "OlympiadReady"
USERNAME = "nyxen-admin"
PASSWORD = "Olympiad@2026"
DRIVER   = "{ODBC Driver 18 for SQL Server}"

conn_str = (
    f"DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};"
    f"UID={USERNAME};PWD={PASSWORD};Encrypt=yes;TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

print("Connecting to staging DB...")
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# ── 1. Total questions per subject / grade / difficulty ──────────────────────
cursor.execute("""
    SELECT Subject, Grade, Difficulty, COUNT(*) as cnt
    FROM QuestionBank
    GROUP BY Subject, Grade, Difficulty
    ORDER BY Subject, Grade, Difficulty
""")
rows = cursor.fetchall()

# Build nested dict: data[subject][grade][difficulty] = count
data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for subject, grade, difficulty, cnt in rows:
    data[subject][grade][difficulty] = cnt

# ── 2. Image coverage per subject / grade ────────────────────────────────────
cursor.execute("""
    SELECT Subject, Grade,
           COUNT(*) as total,
           SUM(CASE WHEN ImageUrl IS NOT NULL AND ImageUrl != '' THEN 1 ELSE 0 END) as with_image
    FROM QuestionBank
    GROUP BY Subject, Grade
    ORDER BY Subject, Grade
""")
img_rows = cursor.fetchall()

img_data = {}  # (subject, grade) -> (total, with_image)
for subject, grade, total, with_image in img_rows:
    img_data[(subject, grade)] = (total, with_image or 0)

conn.close()

DIFFICULTIES = ["Foundation", "Advanced", "Olympiad"]

# ── PRINT FULL TABLE ──────────────────────────────────────────────────────────
print("\n" + "="*90)
print(f"  {'Subject':<28} {'Gr':>3}  {'Found':>6} {'Adv':>6} {'Olym':>6} {'TOTAL':>6}  {'Images':>8}  {'Img%':>5}")
print("="*90)

thin_olympiad = []
thin_total    = []
zero_images   = []

all_subjects = sorted(data.keys())
for subject in all_subjects:
    grades = sorted(data[subject].keys())
    for grade in grades:
        diff_counts = data[subject][grade]
        found = diff_counts.get("Foundation", 0)
        adv   = diff_counts.get("Advanced", 0)
        olym  = diff_counts.get("Olympiad", 0)
        total = found + adv + olym

        ti = img_data.get((subject, grade), (total, 0))
        img_total, img_count = ti
        img_pct = f"{img_count/img_total*100:.0f}%" if img_total else "0%"

        flag = ""
        if olym < 10: flag += " !OLY"
        if total < 20: flag += " !THIN"

        print(f"  {subject:<28} {grade:>3}  {found:>6} {adv:>6} {olym:>6} {total:>6}  {img_count:>4}/{img_total:<4}  {img_pct:>5}{flag}")

        if olym < 10:
            thin_olympiad.append((subject, grade, olym))
        if total < 20:
            thin_total.append((subject, grade, total))
        if img_count == 0 and total >= 50:
            zero_images.append((subject, grade, total))

# ── SUMMARY ALERTS ────────────────────────────────────────────────────────────
print("\n" + "="*90)
print("  !!  THIN OLYMPIAD (< 10 questions)")
print("="*90)
if thin_olympiad:
    for s, g, c in sorted(thin_olympiad, key=lambda x: x[2]):
        print(f"    Grade {g:>2} {s:<30} -> {c} Olympiad questions")
else:
    print("    None! All slots have 10+ Olympiad questions.")

print("\n" + "="*90)
print("  !!  VERY THIN OVERALL (< 20 total questions)")
print("="*90)
if thin_total:
    for s, g, c in sorted(thin_total, key=lambda x: x[2]):
        print(f"    Grade {g:>2} {s:<30} -> {c} total questions")
else:
    print("    None! All grade/subject combos have 20+ questions.")

print("\n" + "="*90)
print("  !!  ZERO IMAGES (subjects with 50+ questions and 0% image coverage)")
print("="*90)
if zero_images:
    for s, g, c in sorted(zero_images, key=lambda x: -x[2]):
        print(f"    Grade {g:>2} {s:<30} -> {c} questions, 0 images")
else:
    print("    None! All large question sets have some image coverage.")

print("\n" + "="*90)
print("  DONE")
print("="*90)
