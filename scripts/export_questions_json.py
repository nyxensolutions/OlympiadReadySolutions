import pyodbc, json, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=olympiadready-np.database.windows.net;"
    "DATABASE=OlympiadReady;"
    "UID=nyxen-admin;PWD=Olympiad@2026"
)

# Image-related keywords to detect image-based questions/answers
IMAGE_KEYWORDS = re.compile(
    r'\b(image|figure|diagram|picture|photo|graph|chart|illustration|shown|below|above|refer|see|look at)\b',
    re.IGNORECASE
)

c = conn.cursor()
c.execute("""
    SELECT
        QuestionBankId,
        Subject,
        Grade,
        Difficulty,
        Topic,
        SubTopic,
        QuestionText,
        OptionsJson,
        CorrectAnswer,
        Explanation
    FROM QuestionBank
    WHERE (ImageUrl IS NULL OR ImageUrl = '')
    ORDER BY Grade, Subject, Difficulty
""")

columns = [desc[0] for desc in c.description]
rows = c.fetchall()

questions = []
skipped_image_refs = 0

for row in rows:
    record = dict(zip(columns, row))

    # Parse OptionsJson
    try:
        options = json.loads(record["OptionsJson"]) if record["OptionsJson"] else []
    except Exception:
        options = []

    qt = record["QuestionText"] or ""
    exp = record["Explanation"] or ""
    opts_text = " ".join(options)

    # Skip questions that reference images in text
    if IMAGE_KEYWORDS.search(qt) or IMAGE_KEYWORDS.search(opts_text):
        skipped_image_refs += 1
        continue

    questions.append({
        "id": record["QuestionBankId"],
        "subject": record["Subject"],
        "grade": record["Grade"],
        "difficulty": record["Difficulty"],
        "topic": record["Topic"],
        "subTopic": record["SubTopic"],
        "questionText": qt,
        "options": options,
        "correctAnswer": record["CorrectAnswer"],
        "explanation": exp
    })

print(f"Total fetched (no ImageUrl): {len(rows)}")
print(f"Skipped (image-reference text): {skipped_image_refs}")
print(f"Questions in JSON: {len(questions)}")

output_path = r"D:\Nyxen\OlympiadReady\questions_json.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"Saved to: {output_path}")
print(f"File size: {__import__('os').path.getsize(output_path) / 1024 / 1024:.2f} MB")
