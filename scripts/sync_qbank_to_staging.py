"""
Syncs QuestionBank rows (created >= 2026-05-25) from local SQL Server to staging Azure SQL.
Uses MERGE so it's safe to run multiple times — existing rows are skipped.
"""
import pyodbc
import sys

LOCAL_CONN = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=OlympiadReady;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

STAGING_CONN = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=olympiadready-np.database.windows.net;"
    "DATABASE=OlympiadReady;"
    "UID=nyxen-admin;"
    "PWD=Olympiad@2026;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

SINCE = "2026-05-25"
BATCH_SIZE = 50

print(f"Connecting to local DB...", flush=True)
local = pyodbc.connect(LOCAL_CONN)
local_cur = local.cursor()

print(f"Fetching rows created >= {SINCE}...", flush=True)
local_cur.execute("""
    SELECT QuestionBankId, Subject, Grade, Difficulty, Topic, SubTopic,
           QuestionText, OptionsJson, CorrectAnswer, Explanation, CreatedAt, ImageUrl
    FROM QuestionBank
    WHERE CreatedAt >= ?
    ORDER BY CreatedAt
""", SINCE)

rows = local_cur.fetchall()
print(f"Fetched {len(rows)} rows from local DB.", flush=True)

print("Connecting to staging DB...", flush=True)
staging = pyodbc.connect(STAGING_CONN)
staging_cur = staging.cursor()

MERGE_SQL = """
MERGE QuestionBank AS target
USING (VALUES (?,?,?,?,?,?,?,?,?,?,?,?))
  AS source (QuestionBankId, Subject, Grade, Difficulty, Topic, SubTopic,
             QuestionText, OptionsJson, CorrectAnswer, Explanation, CreatedAt, ImageUrl)
ON target.QuestionBankId = source.QuestionBankId
WHEN NOT MATCHED THEN
  INSERT (QuestionBankId, Subject, Grade, Difficulty, Topic, SubTopic,
          QuestionText, OptionsJson, CorrectAnswer, Explanation, CreatedAt, ImageUrl)
  VALUES (source.QuestionBankId, source.Subject, source.Grade, source.Difficulty,
          source.Topic, source.SubTopic, source.QuestionText, source.OptionsJson,
          source.CorrectAnswer, source.Explanation, source.CreatedAt, source.ImageUrl);
"""

inserted = 0
skipped = 0
errors = 0

for i, row in enumerate(rows):
    try:
        staging_cur.execute(MERGE_SQL, (
            str(row.QuestionBankId),
            row.Subject,
            row.Grade,
            row.Difficulty,
            row.Topic,
            row.SubTopic,
            row.QuestionText,
            row.OptionsJson,
            row.CorrectAnswer,
            row.Explanation,
            row.CreatedAt,
            row.ImageUrl,
        ))
        # rowcount 1 = inserted, 0 = already existed
        if staging_cur.rowcount == 1:
            inserted += 1
        else:
            skipped += 1
    except Exception as e:
        errors += 1
        print(f"  ERROR on row {i+1} ({row.QuestionBankId}): {e}", flush=True)

    # Commit in batches
    if (i + 1) % BATCH_SIZE == 0:
        staging.commit()
        print(f"  Progress: {i+1}/{len(rows)} — inserted={inserted}, skipped={skipped}, errors={errors}", flush=True)

staging.commit()
print(f"\nDone! Total={len(rows)}, Inserted={inserted}, Already existed={skipped}, Errors={errors}", flush=True)

local.close()
staging.close()
