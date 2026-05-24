import pyodbc

conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=OlympiadReady;Trusted_Connection=yes;")
cursor = conn.cursor()
cursor.execute("SELECT TOP 1 QuestionText FROM QuestionBank WHERE QuestionText LIKE '%109%'")
row = cursor.fetchone()
if row:
    text = row[0]
    print("Text:", text)
    print("Unicode points:")
    for c in text:
        print(f"'{c}' -> U+{ord(c):04X}")
else:
    print("No row found.")
conn.close()
