import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import pyodbc
import json
import re

AZURE_CONN = (
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=olympiadready-np.database.windows.net;'
    'Database=OlympiadReady;'
    'UID=nyxen-admin;PWD=Olympiad@2026;'
    'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
)

conn = pyodbc.connect(AZURE_CONN)
cur = conn.cursor()

print("Fetching all questions to fix options prefixes...")
cur.execute("SELECT QuestionBankId, OptionsJson FROM QuestionBank WHERE OptionsJson LIKE '%A)%' OR OptionsJson LIKE '%B)%' OR OptionsJson LIKE '%C)%' OR OptionsJson LIKE '%D)%' OR OptionsJson LIKE '%a)%'")
rows = cur.fetchall()

updates = []
prefix_pattern = re.compile(r'^[A-Da-d][\.\)]\s*', re.IGNORECASE)

for r in rows:
    q_id = r[0]
    opts_str = str(r[1] or '')
    
    try:
        opts = json.loads(opts_str)
        if isinstance(opts, list):
            new_opts = []
            changed = False
            for opt in opts:
                if isinstance(opt, str):
                    stripped = prefix_pattern.sub('', opt).strip()
                    if stripped != opt:
                        changed = True
                    new_opts.append(stripped)
                else:
                    new_opts.append(opt)
            
            if changed:
                updates.append((json.dumps(new_opts, ensure_ascii=False), q_id))
    except json.JSONDecodeError:
        pass

print(f"Found {len(updates)} questions that need prefix removal.")

if updates:
    cur.fast_executemany = True
    cur.executemany("UPDATE QuestionBank SET OptionsJson = ? WHERE QuestionBankId = ?", updates)
    conn.commit()
    print("Update complete.")
else:
    print("No updates needed.")

conn.close()
