"""
fix_hex_colors_in_db.py
Finds all questions in the DB whose options contain hex color codes
(#E74C3C, #2980B9, etc.) and replaces them with readable color names.

Usage:
    python fix_hex_colors_in_db.py
Requires ADMIN_API_KEY env var and API running at localhost:5080.
"""
import os, sys, json, time
import requests

ADMIN_API_BASE = os.environ.get("ADMIN_API_BASE", "http://localhost:5080")
ADMIN_API_KEY  = os.environ.get("ADMIN_API_KEY", "")

HEX_TO_NAME = {
    "#E74C3C": "Red",
    "#2980B9": "Blue",
    "#27AE60": "Green",
    "#8E44AD": "Purple",
    "#E67E22": "Orange",
    "#F1C40F": "Yellow",
    "#F39C12": "Amber",
    "#1ABC9C": "Teal",
}

if not ADMIN_API_KEY:
    print("[!] Set ADMIN_API_KEY env var first.")
    sys.exit(1)

def replace_hex(text):
    for hex_code, name in HEX_TO_NAME.items():
        text = text.replace(hex_code, name)
    return text

def needs_fix(options):
    return any(any(h in opt for h in HEX_TO_NAME) for opt in options)

# ── 1. Fetch all questions (paginate) ────────────────────────────────────────
print("Fetching questions from DB...")
all_questions = []
page = 1
page_size = 200
while True:
    r = requests.get(
        f"{ADMIN_API_BASE}/api/admin/questions",
        params={"page": page, "pageSize": page_size},
        headers={"X-Admin-Key": ADMIN_API_KEY},
        timeout=15
    )
    if r.status_code != 200:
        print(f"[FAIL] GET /api/admin/questions: {r.status_code} {r.text[:200]}")
        sys.exit(1)
    data = r.json()
    # Handle both array response and paged response
    items = data if isinstance(data, list) else data.get("items", data.get("questions", data.get("data", [])))
    if not items:
        break
    all_questions.extend(items)
    if len(items) < page_size:
        break
    page += 1

print(f"Fetched {len(all_questions)} questions total.")

# ── 2. Find questions with hex codes in options ───────────────────────────────
to_fix = []
for q in all_questions:
    # API returns options as a parsed list under "Options" key
    opts_raw = q.get("Options") or q.get("options") or q.get("optionsJson") or "[]"
    if isinstance(opts_raw, str):
        try:
            opts = json.loads(opts_raw)
        except Exception:
            opts = []
    else:
        opts = opts_raw
    if needs_fix(opts):
        to_fix.append((q, opts))

print(f"Found {len(to_fix)} questions with hex color codes in options.\n")

if not to_fix:
    print("Nothing to fix!")
    sys.exit(0)

# ── 3. Patch each via PUT ─────────────────────────────────────────────────────
fixed = 0
failed = 0

for q, old_opts in to_fix:
    new_opts = [replace_hex(opt) for opt in old_opts]
    new_expl = replace_hex(q.get("Explanation") or q.get("explanation") or "")
    q_id = q.get("QuestionBankId") or q.get("id") or q.get("questionId")
    q_text = q.get("QuestionText") or q.get("questionText") or ""

    print(f"  Fixing: {q_text[:60]}")
    print(f"    Before: {old_opts}")
    print(f"    After:  {new_opts}")

    payload = {
        "subject":       q.get("Subject")       or q.get("subject"),
        "grade":         q.get("Grade")         or q.get("grade"),
        "difficulty":    q.get("Difficulty")    or q.get("difficulty"),
        "topic":         q.get("Topic")         or q.get("topic"),
        "subTopic":      q.get("SubTopic")      or q.get("subTopic"),
        "questionText":  q_text,
        "imageUrl":      q.get("ImageUrl")      or q.get("imageUrl"),
        "options":       new_opts,
        "correctAnswer": q.get("CorrectAnswer") or q.get("correctAnswer"),
        "explanation":   new_expl,
    }

    try:
        r = requests.put(
            f"{ADMIN_API_BASE}/api/admin/questions/{q_id}",
            json=payload,
            headers={"X-Admin-Key": ADMIN_API_KEY},
            timeout=15
        )
        if r.status_code in (200, 204):
            print(f"    -> [OK] updated")
            fixed += 1
        else:
            print(f"    -> [FAIL {r.status_code}] {r.text[:120]}")
            failed += 1
    except Exception as e:
        print(f"    -> [ERROR] {e}")
        failed += 1

    time.sleep(0.05)

print(f"\nDONE: {fixed} fixed, {failed} failed out of {len(to_fix)} questions.")
