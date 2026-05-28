import sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
import pyodbc
import json
import sqlite3
import re
import time
from google import genai
from google.genai import types

# Configuration
AZURE_CONN = (
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=olympiadready-np.database.windows.net;'
    'Database=OlympiadReady;'
    'UID=nyxen-admin;PWD=Olympiad@2026;'
    'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
)

GEMINI_API_KEY = "AIzaSyDya3SWV1WS13NxILkNJnYRJ3aaxXe-VMA"
client = genai.Client(api_key=GEMINI_API_KEY)

def get_db():
    for attempt in range(5):
        try:
            conn = pyodbc.connect(AZURE_CONN)
            return conn
        except Exception as e:
            print(f"DB Connection error: {e}. Retrying in 5s...")
            time.sleep(5)
    raise Exception("Failed to connect to Azure SQL after 5 attempts.")

def get_checkpoint_db():
    conn = sqlite3.connect("validation_log.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS processed (
            QuestionBankId TEXT PRIMARY KEY,
            verdict TEXT,
            model_used TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Clear out any previous 'error' runs so we can retry them
    cur.execute("DELETE FROM processed WHERE verdict = 'error'")
    conn.commit()
    return conn

def is_processed(chk_conn, q_id):
    cur = chk_conn.cursor()
    cur.execute("SELECT 1 FROM processed WHERE QuestionBankId = ?", (q_id,))
    return cur.fetchone() is not None

def mark_processed(chk_conn, q_id, verdict, model):
    cur = chk_conn.cursor()
    cur.execute("INSERT OR REPLACE INTO processed (QuestionBankId, verdict, model_used) VALUES (?, ?, ?)", (q_id, verdict, model))
    chk_conn.commit()

def generate_prompt(q):
    q_text = q['QuestionText']
    opts = q['OptionsJson']
    ans = q['CorrectAnswer']
    expl = q['Explanation']
    grade = q['Grade']
    subj = q['Subject']

    prompt = f"""You are an expert teacher strictly validating a Grade {grade} {subj} multiple-choice question.

Question: {q_text}
Current Options: {opts}
Marked Correct Answer: {ans}
Explanation: {expl}

Tasks:
1. Solve the question independently.
2. Check if the Marked Correct Answer is exactly one of the options and is factually correct.
3. Check if the Explanation is correct and actually belongs to this question.
4. If there is ANY error (wrong answer, correct answer missing from options, duplicate options, wrong explanation), you MUST fix it. Ensure there are exactly 4 distinct options (A, B, C, D). Ensure the correct answer is accurately indicated and matches the explanation.

Output valid JSON ONLY with no markdown formatting (do not wrap in ```json).
Schema:
{{
  "verdict": "ok" | "fix_required",
  "correct_answer_letter": "A/B/C/D",
  "corrected_options": ["...", "...", "...", "..."] (only if fix_required, DO NOT include A) B) C) D) prefixes in the option text itself),
  "corrected_explanation": "..." (only if fix_required)
}}
"""
    return prompt

def call_ai(prompt, subj):
    for attempt in range(10): # retry up to 10 times to handle 1-minute rate limits
        try:
            res = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=500,
                )
            )
            return res.text, "gemini-3.5-flash"
        except Exception as e:
            err_str = str(e)
            print(f"Gemini error: {err_str}")
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                print("Rate limit hit. Waiting 60 seconds...")
                time.sleep(60)
            else:
                time.sleep(2)
    return None, None

def process_question(db_conn, chk_conn, q):
    q_id = str(q['QuestionBankId'])
    if is_processed(chk_conn, q_id):
        return "skipped"

    prompt = generate_prompt(q)
    resp_text, model = call_ai(prompt, q['Subject'])
    
    if not resp_text:
        return "error"
        
    match = re.search(r'\{.*\}', resp_text, re.DOTALL)
    if not match:
        mark_processed(chk_conn, q_id, "parse_error", model)
        return "parse_error"
        
    try:
        res = json.loads(match.group(0))
        verdict = res.get('verdict', 'ok')
        
        if verdict == 'fix_required':
            new_ans = res.get('correct_answer_letter', q['CorrectAnswer'])
            if new_ans and isinstance(new_ans, str) and len(new_ans) > 0:
                new_ans = new_ans[0].upper()
            else:
                new_ans = 'A'

            new_opts = res.get('corrected_options', None)
            new_expl = res.get('corrected_explanation', None)
            
            updates = []
            params = []
            
            if new_ans in ['A','B','C','D']:
                updates.append("CorrectAnswer = ?")
                params.append(new_ans)
                
            if new_opts and isinstance(new_opts, list) and len(new_opts) == 4:
                updates.append("OptionsJson = ?")
                params.append(json.dumps(new_opts, ensure_ascii=False))
                
            if new_expl:
                updates.append("Explanation = ?")
                params.append(new_expl)
                
            if updates:
                params.append(q_id)
                sql = f"UPDATE QuestionBank SET {', '.join(updates)} WHERE QuestionBankId = ?"
                cur = db_conn.cursor()
                cur.execute(sql, params)
                db_conn.commit()
                
        mark_processed(chk_conn, q_id, verdict, model)
        return verdict
        
    except json.JSONDecodeError:
        mark_processed(chk_conn, q_id, "parse_error", model)
        return "parse_error"
    except Exception as e:
        print(f"Update error: {e}")
        return "error"

def main():
    print("Starting AI Validation Pipeline using Gemini...")
    db_conn = get_db()
    chk_conn = get_checkpoint_db()
    
    subjects = ['Mathematics','Science','Science-Biology','Science-Chemistry','Science-Physics','Logical Reasoning']
    placeholders = ','.join(['?' for _ in subjects])
    
    cur = db_conn.cursor()
    # Prioritize Mathematics, then others
    cur.execute(f'''
        SELECT QuestionBankId, Subject, Grade, QuestionText, OptionsJson, CorrectAnswer, Explanation 
        FROM QuestionBank 
        WHERE Subject IN ({placeholders})
        ORDER BY CASE WHEN Subject = 'Mathematics' THEN 0 ELSE 1 END, Grade DESC
    ''', subjects)
    
    rows = cur.fetchall()
    total = len(rows)
    print(f"Found {total} questions to process.")
    
    stats = {'ok': 0, 'fix_required': 0, 'skipped': 0, 'error': 0, 'parse_error': 0}
    
    for i, r in enumerate(rows):
        q = {
            'QuestionBankId': r[0],
            'Subject': r[1],
            'Grade': r[2],
            'QuestionText': str(r[3] or ''),
            'OptionsJson': str(r[4] or ''),
            'CorrectAnswer': str(r[5] or ''),
            'Explanation': str(r[6] or '')
        }
        
        status = process_question(db_conn, chk_conn, q)
        stats[status] = stats.get(status, 0) + 1
        
        if (i + 1) % 10 == 0 or (i + 1) == total:
            print(f"[{i+1}/{total}] Stats: {stats}")

if __name__ == '__main__':
    main()
