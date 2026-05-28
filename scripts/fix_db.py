"""
fix_db.py  — targeted cleanup:
  1. Delete old Venn questions (generic images, always answer=3)
  2. Delete old Water Cycle questions (same image for all processes)
  3. Fix hex color codes in Matrix Pattern question options
"""
import os, sys, json, time, requests

ADMIN_API_BASE = "http://localhost:5080"
ADMIN_API_KEY  = os.environ.get("ADMIN_API_KEY", "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}

HEX_TO_NAME = {
    "#E74C3C": "Red", "#2980B9": "Blue", "#27AE60": "Green",
    "#8E44AD": "Purple", "#E67E22": "Orange", "#F1C40F": "Yellow",
}

def fetch(search=None, topic=None):
    all_q, page = [], 1
    while True:
        params = {"page": page, "pageSize": 100}
        if search: params["search"] = search
        if topic:  params["topic"]  = topic
        r = requests.get(f"{ADMIN_API_BASE}/api/admin/questions",
                         params=params, headers=HEADERS, timeout=60)
        if r.status_code != 200:
            print(f"  fetch error {r.status_code}")
            break
        items = r.json().get("items", [])
        all_q.extend(items)
        if len(items) < 100:
            break
        page += 1
    return all_q

def replace_hex(t):
    if not t: return t
    for h, n in HEX_TO_NAME.items():
        t = t.replace(h, n)
    return t

def dedup(qs):
    seen, out = set(), []
    for q in qs:
        qid = q.get("questionBankId")
        if qid and qid not in seen:
            seen.add(qid); out.append(q)
    return out

# ── 1. Delete old Venn questions ─────────────────────────────────────────────
print("="*55)
print("STEP 1: Delete old Venn Diagram questions")
print("="*55)
venn = dedup(fetch(search="Venn diagram") + fetch(topic="Sets"))
print(f"  Found {len(venn)} Venn questions total")
deleted = 0
for q in venn:
    qid  = q.get("questionBankId")
    expl = q.get("explanation", "")
    # Old questions: explanation doesn't contain "count ="  (new ones do)
    if "count =" not in expl:
        r = requests.delete(f"{ADMIN_API_BASE}/api/admin/questions/{qid}",
                            headers=HEADERS, timeout=10)
        status = "OK" if r.status_code in (200, 204) else f"FAIL {r.status_code}"
        txt = q.get("questionText", "")[:65].encode("ascii","replace").decode()
        print(f"  [{status}] {txt}")
        if r.status_code in (200, 204):
            deleted += 1
        time.sleep(0.05)
print(f"  Deleted {deleted}\n")

# ── 2. Delete old Water Cycle questions ───────────────────────────────────────
print("="*55)
print("STEP 2: Delete old Water Cycle questions")
print("="*55)
water = dedup(fetch(topic="Water Cycle") + fetch(search="water cycle"))
print(f"  Found {len(water)} Water Cycle questions total")
PROCESS_NAMES = ["evaporation","condensation","precipitation","transpiration","collection","infiltration"]
wdeleted = 0
for q in water:
    qid = q.get("questionBankId")
    img = q.get("imageUrl") or ""
    # Old = image URL does NOT contain a process name; new ones do
    is_old = not any(p in img.lower() for p in PROCESS_NAMES)
    if is_old:
        r = requests.delete(f"{ADMIN_API_BASE}/api/admin/questions/{qid}",
                            headers=HEADERS, timeout=10)
        status = "OK" if r.status_code in (200, 204) else f"FAIL {r.status_code}"
        txt = q.get("questionText", "")[:65].encode("ascii","replace").decode()
        print(f"  [{status}] {txt}")
        if r.status_code in (200, 204):
            wdeleted += 1
        time.sleep(0.05)
print(f"  Deleted {wdeleted}\n")

# ── 3. Fix hex codes in Matrix questions ─────────────────────────────────────
print("="*55)
print("STEP 3: Fix hex color codes in Matrix options")
print("="*55)
matrix = dedup(fetch(topic="Matrix Patterns") + fetch(search="matrix"))
matrix_hex = [q for q in matrix
              if any(h in str(q.get("options", [])) for h in HEX_TO_NAME)]
print(f"  Found {len(matrix_hex)} Matrix questions with hex codes")
mfixed = 0
for q in matrix_hex:
    qid  = q.get("questionBankId")
    opts = q.get("options", [])
    new_opts = [replace_hex(o) for o in opts]
    payload = {
        "subject":       q.get("subject"),
        "grade":         q.get("grade"),
        "difficulty":    q.get("difficulty"),
        "topic":         q.get("topic"),
        "subTopic":      q.get("subTopic"),
        "questionText":  q.get("questionText"),
        "imageUrl":      q.get("imageUrl"),
        "options":       new_opts,
        "correctAnswer": replace_hex(q.get("correctAnswer", "A")),
        "explanation":   replace_hex(q.get("explanation", "")),
    }
    r = requests.put(f"{ADMIN_API_BASE}/api/admin/questions/{qid}",
                     json=payload, headers=HEADERS, timeout=15)
    if r.status_code in (200, 204):
        mfixed += 1
        safe_txt = q.get("questionText","")[:55].encode("ascii","replace").decode()
        print(f"  [OK] {safe_txt}")
        print(f"       {opts}")
        print(f"    -> {new_opts}")
    else:
        print(f"  [FAIL {r.status_code}] {r.text[:100]}")
    time.sleep(0.05)
print(f"  Fixed {mfixed}\n")

print("="*55)
print(f"DONE: {deleted} Venn deleted, {wdeleted} Water Cycle deleted, {mfixed} Matrix hex fixed")
print("="*55)
