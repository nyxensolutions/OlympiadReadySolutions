#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grade 5 Question Bank Importer
-------------------------------
- Reads all JSON files from Grade5 directory
- Repairs corrupted JSON (BOM, trailing commas, bad items, truncated files)
- Normalizes difficulty levels (Foundation / Advanced / Olympiad only)
- Fixes questions with <4 options using OpenAI GPT-4o-mini
- Sanitizes Unicode characters to prevent DB corruption (preserves Devanagari for Hindi)
- Inserts into Azure SQL Database (staging) only
"""

import os
import sys
import json
import re
import time
import textwrap

# Force UTF-8 output on Windows consoles
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ─── CONFIG ───────────────────────────────────────────────────────────────────
GRADE5_DIR  = r"D:\Nyxen\OlympiadReady\OlympiadReadySolutions\Grade5"
GRADE       = 5

AZURE_CONN  = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=olympiadready-np.database.windows.net;"
    "Database=OlympiadReady;"
    "UID=nyxen-admin;"
    "PWD=Olympiad@2026;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

OPENAI_API_KEY  = "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"
OPENAI_MODEL    = "gpt-4o-mini"

DRY_RUN = "--dry-run" in sys.argv

# ─── SUBJECT MAP ──────────────────────────────────────────────────────────────
SUBJECT_MAP = {
    "computer":         "Computer Science",
    "english":          "English",
    "generalknowledge": "General Knowledge",
    "hindi":            "Hindi",
    "hindi-olympiad":   "Hindi",
    "mathematics":      "Mathematics",
    "science":          "Science",
    "socialstudies":    "Social Studies",
}

# ─── DIFFICULTY NORMALIZER ────────────────────────────────────────────────────
VALID_DIFFICULTIES = {"Foundation", "Advanced", "Olympiad"}

def normalize_difficulty(raw, filename=""):
    if raw in VALID_DIFFICULTIES:
        return raw
    is_olympiad_file = "olympiad" in filename.lower()
    d = str(raw or "").strip().lower()
    if d in ("", "none", "null", "n/a"):
        return "Foundation"
    if d in ("intermediate", "moderate", "medium", "inter"):
        return "Olympiad" if is_olympiad_file else "Advanced"
    if d in ("advance",):
        return "Advanced"
    if d in ("beginner", "easy", "basic"):
        return "Foundation"
    if d in ("hard", "difficult", "expert", "olympiad"):
        return "Olympiad"
    return "Olympiad" if is_olympiad_file else "Advanced"

# ─── UNICODE SANITIZER ────────────────────────────────────────────────────────
UNICODE_MAP = {
    "\u20B9": "Rs.",    "\u00A3": "GBP",   "\u20AC": "EUR",
    "\u2018": "'",      "\u2019": "'",      "\u201C": '"',
    "\u201D": '"',      "\u2032": "'",      "\u2033": '"',
    "\u2013": "-",      "\u2014": "-",      "\u2012": "-",
    "\u2015": "-",      "\u2212": "-",      "\u2026": "...",
    "\u00D7": "x",      "\u00F7": "/",      "\u2265": ">=",
    "\u2264": "<=",     "\u2260": "!=",     "\u221A": "sqrt",
    "\u00B2": "^2",     "\u00B3": "^3",     "\u00B9": "^1",
    "\u00BD": "1/2",    "\u00BC": "1/4",    "\u00BE": "3/4",
    "\u00B0": " degrees", "\u00B7": ".",    "\u2022": "-",
    "\u00A0": " ",      "\u00AB": '"',      "\u00BB": '"',
    "\u03B1": "alpha",  "\u03B2": "beta",   "\u03C0": "pi",
    "\u03B4": "delta",  "\u03B8": "theta",
}

DEVANAGARI_RANGE = (0x0900, 0x097F)
DEVANAGARI_EXTRAS = {0x200C, 0x200D, 0x0964, 0x0965}

def sanitize_text(text, allow_devanagari=True):
    if not text:
        return ""
    for ch, rep in UNICODE_MAP.items():
        text = text.replace(ch, rep)
    result = []
    for ch in text:
        code = ord(ch)
        if code in (9, 10, 13):
            result.append(ch)
        elif 32 <= code <= 126:
            result.append(ch)
        elif allow_devanagari and DEVANAGARI_RANGE[0] <= code <= DEVANAGARI_RANGE[1]:
            result.append(ch)
        elif allow_devanagari and code in DEVANAGARI_EXTRAS:
            result.append(ch)
        # else: silently drop
    clean = "".join(result)
    clean = re.sub(r"  +", " ", clean).strip()
    return clean

# ─── JSON REPAIR ──────────────────────────────────────────────────────────────
def repair_json(content, filename):
    # Strip BOM
    content = content.lstrip("\ufeff")
    # Remove trailing commas before ] or }
    content = re.sub(r",(\s*[\]}])", r"\1", content)
    # Remove "Note" keys injected into question objects inside the array
    content = re.sub(r',\s*"Note"\s*:\s*"[^"]*"', "", content)
    # If file looks truncated (no closing bracket), close it
    stripped = content.rstrip()
    if stripped and not stripped.endswith("]"):
        last_brace = stripped.rfind("}")
        if last_brace != -1:
            content = stripped[:last_brace + 1] + "\n]"
    return content

def load_json_file(filepath, filename):
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            raw = f.read().strip()
        if not raw:
            print(f"  [SKIP] Empty file: {filename}")
            return []
        repaired = repair_json(raw, filename)
        data = json.loads(repaired)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as e:
        print(f"  [WARN] JSON repair failed ({filename}): {e}")
        # Last-resort: extract individual objects
        try:
            raw_repaired = repair_json(raw, filename)
            objects = []
            # Find all top-level { ... } blocks
            depth = 0
            start = None
            for i, ch in enumerate(raw_repaired):
                if ch == '{':
                    if depth == 0:
                        start = i
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0 and start is not None:
                        block = raw_repaired[start:i+1]
                        try:
                            obj = json.loads(block)
                            if isinstance(obj, dict) and "QuestionText" in obj:
                                objects.append(obj)
                        except:
                            pass
                        start = None
            if objects:
                print(f"  [RECOVER] Salvaged {len(objects)} questions from {filename}")
                return objects
        except Exception as ex2:
            print(f"  [ERROR] Could not recover {filename}: {ex2}")
        return []

# ─── OPENAI OPTION FIXER ──────────────────────────────────────────────────────
_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client

def fix_options_with_openai(item, subject, grade, max_retries=2):
    q_text    = item.get("QuestionText", "")
    options   = item.get("Options", [])
    correct   = item.get("CorrectAnswer", "A")
    expl      = item.get("Explanation", "")
    topic     = item.get("Topic", subject)
    subtopic  = item.get("SubTopic", "")
    difficulty = item.get("Difficulty", "Foundation")

    prompt = textwrap.dedent(f"""
You are writing multiple-choice questions for a Grade {grade} school Olympiad exam.
The question below has only {len(options)} option(s). Add plausible distractors so it has exactly 4 options (A, B, C, D).
Keep the original question text, correct answer, and explanation. Keep the difficulty level.

Question: {q_text}
Current options: {json.dumps(options)}
Correct answer letter: {correct}
Explanation: {expl}
Topic: {topic} / {subtopic}
Difficulty: {difficulty}

Return ONLY valid JSON, no markdown fences, no extra text:
{{
  "QuestionText": "...",
  "Options": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "CorrectAnswer": "{correct}",
  "Explanation": "...",
  "Topic": "{topic}",
  "SubTopic": "{subtopic}",
  "Difficulty": "{difficulty}"
}}
""").strip()

    client = get_openai_client()
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=600,
            )
            text = resp.choices[0].message.content.strip()
            # Extract JSON block
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                fixed = json.loads(json_match.group())
                if isinstance(fixed.get("Options"), list) and len(fixed["Options"]) == 4:
                    return fixed
            print(f"  [AI] Unexpected response shape, retrying...")
        except Exception as e:
            print(f"  [AI] OpenAI error (attempt {attempt+1}): {e}")
            time.sleep(3 * (attempt + 1))
    return None

# ─── DATABASE INSERT ───────────────────────────────────────────────────────────
def insert_batch(conn, questions_with_meta, dry_run=False):
    """
    questions_with_meta: list of (item_dict, canonical_subject, filename)
    Returns (inserted_count, skipped_count)
    """
    cursor = conn.cursor()
    inserted = 0
    skipped  = 0

    for item, subject, filename in questions_with_meta:
        is_hindi = "hindi" in subject.lower()

        q_text = sanitize_text(item.get("QuestionText", ""), allow_devanagari=is_hindi)
        if not q_text:
            skipped += 1
            continue

        options = item.get("Options", [])
        clean_opts = [sanitize_text(str(o), allow_devanagari=is_hindi) for o in options]
        options_json = json.dumps(clean_opts, ensure_ascii=False)

        difficulty  = normalize_difficulty(item.get("Difficulty"), filename)
        topic       = sanitize_text(item.get("Topic", subject),  allow_devanagari=is_hindi) or subject
        subtopic    = sanitize_text(item.get("SubTopic", ""),     allow_devanagari=is_hindi)
        explanation = sanitize_text(item.get("Explanation", ""),  allow_devanagari=is_hindi)

        correct = str(item.get("CorrectAnswer", "A")).strip().upper()
        if len(correct) > 1:
            correct = correct[0]
        if correct not in ("A", "B", "C", "D"):
            correct = "A"

        if dry_run:
            inserted += 1
            continue

        try:
            cursor.execute(
                """
                INSERT INTO QuestionBank
                    (QuestionBankId, Subject, Grade, Difficulty, Topic, SubTopic,
                     QuestionText, OptionsJson, CorrectAnswer, Explanation, CreatedAt)
                VALUES (NEWID(), ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE())
                """,
                subject, GRADE, difficulty, topic, subtopic,
                q_text, options_json, correct, explanation
            )
            inserted += 1
        except Exception as e:
            print(f"  [DB ERR] {e} | Q: {q_text[:60]}")
            skipped += 1

    if not dry_run:
        conn.commit()

    return inserted, skipped

# -- MAIN ----------------------------------------------------------------------
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    files = sorted([f for f in os.listdir(GRADE5_DIR) if f.endswith(".json")])

    print(f"\n{'='*65}")
    print(f"Grade 5 Importer -> Azure SQL (Staging Only)")
    print(f"DRY RUN: {DRY_RUN}")
    print(f"{'='*65}\n")

    # -- Phase 1: Load & repair all files -------------------------------------
    all_ready    = []   # (item, canonical_subject, filename)
    ai_fixed     = 0
    ai_failed    = 0
    total_loaded = 0

    for filename in files:
        filepath = os.path.join(GRADE5_DIR, filename)

        # Determine subject alias
        m = re.match(r"^sample-(.*?)-grade", filename)
        alias = m.group(1) if m else ("mathematics" if "mathematics" in filename else filename)

        # Resolve to canonical subject
        canonical = SUBJECT_MAP.get(alias)
        if not canonical:
            for k, v in SUBJECT_MAP.items():
                if k in alias or alias in k:
                    canonical = v
                    break
        if not canonical:
            print(f"[SKIP] Unknown subject: {alias} ({filename})")
            continue

        print(f"[LOAD] {filename}  ->  {canonical}")
        items = load_json_file(filepath, filename)
        if not items:
            continue

        for item in items:
            total_loaded += 1
            options = item.get("Options") or []
            if not isinstance(options, list):
                options = []

            if len(options) < 4:
                print(f"  [FIX]  {len(options)} opts: {item.get('QuestionText','')[:55]}...")
                fixed = fix_options_with_openai(item, canonical, GRADE)
                if fixed:
                    ai_fixed += 1
                    item = fixed
                else:
                    ai_failed += 1
                    print(f"  [SKIP] Could not fix — dropping question")
                    continue

            all_ready.append((item, canonical, filename))

    print(f"\n{'─'*65}")
    print(f"Loaded:    {total_loaded}")
    print(f"AI-fixed:  {ai_fixed}   |   AI-failed (dropped): {ai_failed}")
    print(f"Ready:     {len(all_ready)}")
    print(f"{'─'*65}\n")

    # ── Phase 2: Connect to Azure SQL ─────────────────────────────────────────
    if DRY_RUN:
        print("[DRY RUN] Skipping database operations.")
        counts = {}
        for _, subj, _ in all_ready:
            counts[subj] = counts.get(subj, 0) + 1
        for s in sorted(counts):
            print(f"  {s}: {counts[s]} questions would be inserted")
        return

    import pyodbc
    print("[DB] Connecting to Azure SQL (staging)...")
    try:
        conn = pyodbc.connect(AZURE_CONN)
    except Exception as e:
        print(f"[FATAL] Azure SQL connection failed: {e}")
        sys.exit(1)
    print("[DB] Connected.\n")

    # Clear existing Grade 5 rows
    cur = conn.cursor()
    cur.execute("DELETE FROM QuestionBank WHERE Grade = 5")
    conn.commit()
    print(f"[DB] Cleared {cur.rowcount} existing Grade 5 rows from Azure SQL.\n")

    # ── Phase 3: Insert ───────────────────────────────────────────────────────
    # Group by file for readable progress
    from collections import defaultdict
    by_file = defaultdict(list)
    for triplet in all_ready:
        by_file[triplet[2]].append(triplet)   # key = filename

    total_ins = 0
    total_skp = 0
    for fname, triplets in sorted(by_file.items()):
        ins, skp = insert_batch(conn, triplets)
        total_ins += ins
        total_skp += skp
        print(f"  [{fname}] inserted={ins}  skipped={skp}")

    print(f"\n{'='*65}")
    print(f"IMPORT COMPLETE")
    print(f"  Total Inserted : {total_ins}")
    print(f"  Total Skipped  : {total_skp}")
    print(f"{'='*65}\n")

    conn.close()

if __name__ == "__main__":
    main()
