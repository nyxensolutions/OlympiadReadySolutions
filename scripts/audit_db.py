import pyodbc, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=olympiadready-np.database.windows.net;"
    "DATABASE=OlympiadReady;"
    "UID=nyxen-admin;PWD=Olympiad@2026"
)
c = conn.cursor()
c.execute("""SELECT Subject, Grade, Difficulty, COUNT(*) as cnt
FROM QuestionBank
GROUP BY Subject, Grade, Difficulty
ORDER BY Grade, Subject, Difficulty""")
rows = c.fetchall()
print(f"{'Subject':<28} {'Gr':<4} {'Difficulty':<12} {'Count':<6}")
print('-'*55)
cur_grade = None
for r in rows:
    if r[1] != cur_grade:
        cur_grade = r[1]
        print()
    flag = ' ***' if r[3] < 15 else ''
    print(f"{r[0]:<28} G{r[1]:<3} {r[2]:<12} {r[3]:<6}{flag}")
conn.close()
print(f"\nTotal rows: {sum(r[3] for r in rows)}")
