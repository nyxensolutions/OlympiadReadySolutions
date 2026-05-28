"""
post_saved_questions.py
1. Deletes old Venn Diagram and Water Cycle questions from DB
   (they have incorrect images — wrong overlap / same image for all processes)
2. Patches existing Matrix Pattern questions to replace hex color codes with names
3. Posts all questions from diagram_questions.json (new corrected versions)

Usage:
    python post_saved_questions.py [path_to_json]
Default path: diagram_questions.json (same folder as this script)

Requires:
    ADMIN_API_KEY env var set
    API running at http://localhost:5080
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

HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

# ─────────────────────────────────────────────────────────────────────────────
def fetch_questions(search=None, topic=None, page_size=100):
    """Fetch questions with optional filters. Returns all matching pages."""
    all_q = []
    page = 1
    while True:
        params = {"page": page, "pageSize": page_size}
        if search:
            params["search"] = search
        if topic:
            params["topic"] = topic
        r = requests.get(f"{ADMIN_API_BASE}/api/admin/questions",
                         params=params, headers=HEADERS, timeout=60)
        if r.status_code != 200:
            print(f"[FAIL] fetch: {r.status_code} {r.text[:120]}")
            break
        data = r.json()
        items = data.get("items", data.get("questions", data if isinstance(data, list) else []))
        if not items:
            break
        all_q.extend(items)
        if len(items) < page_size:
            break
        page += 1
    return all_q

def get_field(q, *keys):
    # Try exact keys, then lowercase versions
    for k in keys:
        if k in q and q[k] is not None:
            return q[k]
        lk = k[0].lower() + k[1:]   # PascalCase -> camelCase
        if lk in q and q[lk] is not None:
            return q[lk]
    return None

def get_options(q):
    opts = q.get("options") or q.get("Options") or q.get("optionsJson") or "[]"
    if isinstance(opts, str):
        try:
            return json.loads(opts)
        except Exception:
            return []
    return opts or []

def replace_hex(text):
    if not text:
        return text
    for hex_code, name in HEX_TO_NAME.items():
        text = text.replace(hex_code, name)
    return text

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Delete old Venn Diagram questions
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Deleting old Venn Diagram questions...")
print("=" * 60)

venn_qs = fetch_questions(search="Venn diagram", topic="Sets")
print(f"  Found {len(venn_qs)} from Sets topic search.")
# Also search by question text
venn_qs2 = fetch_questions(search="intersection")
venn_qs += [q for q in venn_qs2 if q not in venn_qs]
# Deduplicate by id
seen = set()
deduped = []
for q in venn_qs:
    qid = get_field(q, "QuestionBankId", "id")
    if qid not in seen:
        seen.add(qid); deduped.append(q)
venn_qs = deduped

print(f"  Found {len(venn_qs)} Venn Diagram questions to delete.")
venn_deleted = 0
for q in venn_qs:
    qid = get_field(q, "QuestionBankId", "id", "questionId")
    try:
        r = requests.delete(f"{ADMIN_API_BASE}/api/admin/questions/{qid}",
                            headers=HEADERS, timeout=10)
        if r.status_code in (200, 204):
            venn_deleted += 1
        else:
            print(f"  [FAIL {r.status_code}] delete venn {qid}")
    except Exception as e:
        print(f"  [ERROR] {e}")
    time.sleep(0.05)
print(f"  Deleted {venn_deleted} Venn questions.\n")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Delete old Water Cycle questions
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 2: Deleting old Water Cycle questions...")
print("=" * 60)

water_qs = fetch_questions(topic="Water Cycle")
water_qs2 = fetch_questions(search="water cycle")
all_water_ids = {get_field(q, "QuestionBankId", "id") for q in water_qs}
water_qs += [q for q in water_qs2 if get_field(q, "QuestionBankId", "id") not in all_water_ids]

print(f"  Found {len(water_qs)} Water Cycle questions to delete.")
water_deleted = 0
for q in water_qs:
    qid = get_field(q, "QuestionBankId", "id", "questionId")
    try:
        r = requests.delete(f"{ADMIN_API_BASE}/api/admin/questions/{qid}",
                            headers=HEADERS, timeout=10)
        if r.status_code in (200, 204):
            water_deleted += 1
        else:
            print(f"  [FAIL {r.status_code}] delete water {qid}")
    except Exception as e:
        print(f"  [ERROR] {e}")
    time.sleep(0.05)
print(f"  Deleted {water_deleted} Water Cycle questions.\n")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Fix hex color codes in existing Matrix Pattern questions
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 3: Fixing hex color codes in Matrix Pattern questions...")
print("=" * 60)

matrix_qs = fetch_questions(topic="Matrix Patterns")
matrix_qs2 = fetch_questions(search="matrix")
all_matrix_ids = {get_field(q, "QuestionBankId", "id") for q in matrix_qs}
matrix_qs += [q for q in matrix_qs2 if get_field(q, "QuestionBankId", "id") not in all_matrix_ids]
# Filter to only those actually containing hex codes
matrix_qs = [q for q in matrix_qs if any(h in str(get_options(q)) for h in HEX_TO_NAME)]

print(f"  Found {len(matrix_qs)} questions with hex codes in options.")
hex_fixed = 0
for q in matrix_qs:
    old_opts = get_options(q)
    new_opts = [replace_hex(opt) for opt in old_opts]
    qid = get_field(q, "QuestionBankId", "id", "questionId")
    payload = {
        "subject":       get_field(q, "Subject", "subject"),
        "grade":         get_field(q, "Grade", "grade"),
        "difficulty":    get_field(q, "Difficulty", "difficulty"),
        "topic":         get_field(q, "Topic", "topic"),
        "subTopic":      get_field(q, "SubTopic", "subTopic"),
        "questionText":  get_field(q, "QuestionText", "questionText"),
        "imageUrl":      get_field(q, "ImageUrl", "imageUrl"),
        "options":       new_opts,
        "correctAnswer": replace_hex(get_field(q, "CorrectAnswer", "correctAnswer") or "A"),
        "explanation":   replace_hex(get_field(q, "Explanation", "explanation") or ""),
    }
    try:
        r = requests.put(f"{ADMIN_API_BASE}/api/admin/questions/{qid}",
                         json=payload, headers=HEADERS, timeout=15)
        if r.status_code in (200, 204):
            hex_fixed += 1
            print(f"  [OK] {get_field(q,'QuestionText','questionText')[:60]}")
        else:
            print(f"  [FAIL {r.status_code}] {r.text[:80]}")
    except Exception as e:
        print(f"  [ERROR] {e}")
    time.sleep(0.05)
print(f"  Fixed {hex_fixed} questions.\n")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Post new questions from diagram_questions.json
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 4: Posting new questions from diagram_questions.json...")
print("=" * 60)

json_path = sys.argv[1] if len(sys.argv) > 1 else \
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagram_questions.json")

with open(json_path, encoding="utf-8") as f:
    new_questions = json.load(f)

print(f"  {len(new_questions)} questions to post.")
posted = skipped = failed = 0

for i, q in enumerate(new_questions, 1):
    try:
        r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                          json=q, headers=HEADERS, timeout=15)
        if r.status_code in (200, 201):
            posted += 1
            if i % 20 == 0 or i == len(new_questions):
                print(f"  [{i}/{len(new_questions)}] {posted} posted so far...")
        elif r.status_code == 409:
            skipped += 1
        else:
            print(f"  [{i}] [FAIL {r.status_code}] {r.text[:80]}")
            failed += 1
    except Exception as e:
        print(f"  [{i}] [ERROR] {e}")
        failed += 1
    time.sleep(0.05)

print(f"\n{'='*60}")
print(f"ALL DONE")
print(f"  Venn deleted:      {venn_deleted}")
print(f"  Water Cycle deleted: {water_deleted}")
print(f"  Hex codes fixed:   {hex_fixed}")
print(f"  New questions posted: {posted}")
print(f"  Duplicates skipped:   {skipped}")
print(f"  Failed:               {failed}")
print(f"{'='*60}")
