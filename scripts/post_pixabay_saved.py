"""
post_pixabay_saved.py
Posts all questions saved in pixabay_questions.json that haven't been posted yet.
Images are already on Cloudinary — just posts the question payload.
"""
import json, time, requests, os

BASE = os.environ.get("ADMIN_API_BASE", "http://localhost:5080")
KEY  = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")
HDR  = {"X-Admin-Key": KEY}

with open("pixabay_questions.json") as f:
    qs = json.load(f)

print(f"Loaded {len(qs)} saved questions from pixabay_questions.json")
posted = skipped = failed = 0

for q in qs:
    # Validate required fields — imageUrl can be null for image-options questions
    opts = q.get("options", [])
    if not opts or len(opts) < 2:
        print(f"  [SKIP-invalid] {str(q.get('questionText',''))[:50]}")
        skipped += 1
        continue

    # Ensure 4 options — pad with placeholders if needed (shouldn't happen for image-opts)
    opts = q.get("options", [])

    payload = {
        "subject":       q.get("subject", "Science"),
        "grade":         q.get("grade", 3),
        "difficulty":    q.get("difficulty", "Foundation"),
        "topic":         q.get("topic", "General Knowledge"),
        "subTopic":      q.get("subTopic", ""),
        "questionText":  q.get("questionText", ""),
        "imageUrl":      q.get("imageUrl", ""),
        "options":       opts,
        "correctAnswer": q.get("correctAnswer", "A"),
        "explanation":   q.get("explanation", ""),
    }

    try:
        r = requests.post(f"{BASE}/api/admin/add-question", json=payload, headers=HDR, timeout=20)
        txt = q.get("questionText", "")[:55]
        if r.status_code in (200, 201):
            posted += 1
            print(f"  [OK] {txt}")
        elif r.status_code == 409:
            skipped += 1
            print(f"  [DUP] {txt}")
        else:
            failed += 1
            print(f"  [FAIL {r.status_code}] {txt}")
    except Exception as e:
        failed += 1
        print(f"  [ERR] {e}")

    time.sleep(0.15)

print(f"\nDone — Posted: {posted}  Skipped/Dup: {skipped}  Failed: {failed}")
