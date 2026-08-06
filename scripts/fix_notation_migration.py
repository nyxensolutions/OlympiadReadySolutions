"""
Repair maths notation in the QuestionBank.

Independent fixes, each reported separately so they can be reviewed and applied
in isolation:

  currency  — "$3250" -> "₹3250".  The renderer pairs "$" signs into a KaTeX
              formula and strips every space inside it, so "bought for $3250 and
              sold for $4000" displays as "bought for 3250andsoldfor4000".
              Genuine LaTeX ($x$, $\\frac{7}{20}$) is never touched. Mathematics
              only — elsewhere a dollar figure is usually a real-world fact.
  escape    — LaTeX destroyed by JSON escapes: "\\times" arrived as TAB+"imes".
  degree    — "23.5 degrees" -> "23.5°".
  caret     — "a^3" -> "a³".        Skipped in code questions, where ^ is XOR.
  sqrt      — "sqrt(m/k)" -> "√(m/k)".  Skipped in code questions.
  unit      — "154 m2" -> "154 m²",  "24 cm3" -> "24 cm³".
  multiply  — "12 x 3" / "10 * 4" -> "12 × 3".  Skipped in code questions.
  exponent  — "x2 - 5x + 4" -> "x² - 5x + 4".  Handle with care: a letter before
              a digit is a subscript at least as often as a power, and two
              earlier versions of this rule were ~20% wrong on live data.
              What finally separates the two cases:
                * an indexed variable is always introduced with index 1, so a
                  letter seen anywhere as "n1" carries subscripts, never powers
                  ("n1 sin i = n2 sin r", "S1, S2", "a1 + a2", "r1/r2");
                * variables are lowercase — an uppercase letter before a digit
                  is chemistry ("H2O", "Cl2") or an indexed constant;
                * one preceding letter is a coefficient ("ax2" = a·x²), two
                  means the match is inside a word ("the2").
              Plus outright exclusions for electron configurations, direction
              cosines, sequence terms, pattern lists and chemistry wording.
              Verified on the live bank: 87 changes, all Mathematics, none left
              half converted. Digit-on-digit flattening ("42" meaning 4²) is
              deliberately untouched — that source is genuinely ambiguous.

DRY RUN BY DEFAULT — writes nothing without --apply.

    python fix_notation_migration.py                 # dry run, all categories
    python fix_notation_migration.py --only currency # dry run, one category
    python fix_notation_migration.py --apply         # commit

Connection: set OLYMPIAD_DB_CONN, or edit CONN_STR below.
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

import pyodbc

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CONN_STR = os.environ.get("OLYMPIAD_DB_CONN") or (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=nyxen.database.windows.net;DATABASE=OlympiadReadyProd;"
    "UID=nyxen-admin;PWD=" + os.environ.get("OLYMPIAD_DB_PWD", "") + ";"
    "Encrypt=yes;TrustServerCertificate=no"
)

OUT_CSV = Path(__file__).parent / "notation_migration_review.csv"

# Order is significant, not cosmetic: "escape" must run first. A question whose
# \rightarrow was destroyed reads as prose to the currency detector, which then
# mistakes a genuine "$…$" maths span for money.
# "degree" runs before "exponent" so "3x0" becomes "3x°" rather than "3x⁰".
# "exponent" runs before "multiply" so "6x4" is read as a power, not 6 × 4.
CATEGORY_ORDER = ("escape", "currency", "currency_review", "degree", "caret",
                  "sqrt", "unit", "exponent", "multiply")

DEFAULT_CATEGORIES = ("escape", "currency", "currency_review", "degree", "caret",
                      "sqrt", "unit", "exponent", "multiply")

REVIEW_ONLY = {"currency_review"}

# ── currency detection (mirrors web/lib/notation.ts protectCurrency) ──────────

PROSE_WORD = re.compile(
    r"\b(?:and|the|for|of|in|is|are|was|were|to|from|with|a|an|by|on|at|he|she|it|they"
    r"|his|her|their|bills?|notes?|coins?|costs?|prices?|profit|loss|salary|paid|pays?"
    r"|buy|buys|bought|sold|sells?|spends?|spent|saves?|saved|each|per|total|amount"
    r"|rupees?|dollars?)\b",
    re.I,
)
TWO_WORDS = re.compile(r"[A-Za-z]{2,}\s+[A-Za-z]{2,}")
DEFINITELY_MATH = re.compile(r"[\\^_{}]")


def classify_dollars(text):
    """
    Split every '$' into money markers and genuine maths delimiters.

    Returns (currency_positions, math_positions). Anything paired into a span whose
    contents contain LaTeX syntax is maths and must never be rewritten — the closing
    '$' of "$9 \\rightarrow 0$" sits right after a digit and would otherwise look
    exactly like a trailing price.
    """
    marks = [i for i, c in enumerate(text) if c == "$" and (i == 0 or text[i - 1] != "\\")]
    currency, math = set(), set()

    k = 0
    while k < len(marks) - 1:
        open_i, close_i = marks[k], marks[k + 1]
        content = text[open_i + 1 : close_i]
        after = text[close_i + 1] if close_i + 1 < len(text) else ""
        is_currency = after.isdigit() or bool(
            TWO_WORDS.search(content) and PROSE_WORD.search(content)
        )
        if not DEFINITELY_MATH.search(content) and is_currency:
            currency.update((open_i, close_i))
            k += 1  # the closing '$' may open the next amount
        else:
            math.update((open_i, close_i))
            k += 2

    # Whatever is left is unpaired. It is money only when glued to a number.
    for m in marks:
        if m in currency or m in math:
            continue
        nxt = text[m + 1] if m + 1 < len(text) else ""
        prv = text[m - 1] if m > 0 else ""
        if nxt.isdigit() or prv.isdigit():
            currency.add(m)
    return currency, math


# Only invented word-problem amounts are safe to redenominate. Outside Mathematics a
# dollar figure is usually a real-world fact ("India's GDP: approximately $3.5 trillion",
# "annual salary of $1 a year") and rewriting it as rupees makes the question false.
AUTO_CURRENCY_SUBJECTS = {"Mathematics"}

# "=$A$1+$B$1" is an Excel absolute reference, not money. Converting it would produce
# "=₹A₹1+₹B₹1" and destroy the question.
SPREADSHEET_REF = re.compile(r"=\s*\$|\$[A-Z]{1,3}\$?\d")


def _to_rupees(text):
    currency, _ = classify_dollars(text)
    if not currency:
        return text
    text = "".join("₹" if i in currency else c for i, c in enumerate(text))
    # Symbol trails the amount ("1600₹") — move it to the front.
    return re.sub(r"(?<![\d₹])(\d[\d,]*(?:\.\d+)?)\s*₹(?!\d)", r"₹\1", text)


def fix_currency(text, subject):
    """'$3250' -> '₹3250'  and  '1600$' -> '₹1600'. Mathematics only."""
    if subject not in AUTO_CURRENCY_SUBJECTS or SPREADSHEET_REF.search(text):
        return text
    return _to_rupees(text)


def flag_currency_review(text, subject):
    """Non-Mathematics dollars: report the proposed change, never apply it."""
    if subject in AUTO_CURRENCY_SUBJECTS:
        return text
    return _to_rupees(text)


# ── LaTeX commands eaten by JSON escapes ─────────────────────────────────────

ESCAPE_VICTIMS = [
    ("\r", "r", "ightarrow"), ("\r", "r", "ight"),
    ("\t", "t", "imes"), ("\t", "t", "heta"), ("\t", "t", "riangle"),
    ("\t", "t", "ext"), ("\t", "t", "an"),
    ("\f", "f", "rac"), ("\f", "f", "orall"),
    ("\b", "b", "eta"), ("\b", "b", "inom"), ("\b", "b", "ar"),
    ("\v", "v", "ec"),
    ("\n", "n", "eq"), ("\n", "n", "abla"),
]


def fix_escape(text):
    if not any(c in text for c in "\r\t\f\b\v\n"):
        return text
    for ctrl, letter, tail in ESCAPE_VICTIMS:
        broken = ctrl + tail
        if broken in text:
            text = text.replace(broken, "\\" + letter + tail)
        # the CR variant sometimes arrives as CRLF
        if ctrl == "\r" and ("\r\n" + tail) in text:
            text = text.replace("\r\n" + tail, "\\" + letter + tail)
    return text


# ── unit powers and exponents ────────────────────────────────────────────────

SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
       "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
to_super = lambda d: "".join(SUP.get(c, c) for c in d)

UNIT_RE = re.compile(r"\b(cm|mm|km|m|ft|in|sq|cu)([23])\b")


def fix_unit(text):
    return UNIT_RE.sub(lambda m: m.group(1) + to_super(m.group(2)), text)


# ── code-safety guard ────────────────────────────────────────────────────────
# In a programming question "sqrt(", "*" and "^" are operators, not notation.
# Rewriting them silently breaks the code the question is asking about.
CODE_CONTEXT = re.compile(
    r"print\(|def\s|import\s|range\(|Math\.|#include|console\.|<script|"
    r"\bXOR\b|bitwise|\bpython\b|\bjava\b|\bC\+\+|=\s*\[|\bformula\b.*=",
    re.I,
)


# ── caret exponents:  a^3 -> a³ ──────────────────────────────────────────────
CARET_RE = re.compile(r"\^\{?(\d+)\}?")


def fix_caret(text, subject):
    if CODE_CONTEXT.search(text):
        return text
    return CARET_RE.sub(lambda m: to_super(m.group(1)), text)


# ── sqrt(x) -> √(x) ──────────────────────────────────────────────────────────
SQRT_RE = re.compile(r"\bsqrt\s*(?=\()", re.I)


def fix_sqrt(text, subject):
    if CODE_CONTEXT.search(text):
        return text
    return SQRT_RE.sub("√", text)


# ── "23.5 degrees" -> "23.5°" ────────────────────────────────────────────────
DEGREE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*degrees?(?![A-Za-z])")


def fix_degree(text, subject):
    return DEGREE_RE.sub(r"\1°", text)


# ── "12 x 3" / "10 * 4" -> "12 × 3" ──────────────────────────────────────────
# Whitespace is required on both sides so "6x4" (an exponent) is never caught,
# and so a variable multiplication like "2x" stays untouched.
# "%" is included so "4,000 x 10% x 7.5/12" converts both operators rather than
# stopping half way and leaving the expression inconsistent.
TIMES_RE = re.compile(r"([\d)%])\s+[xX]\s+(?=[\d(])")
STAR_RE = re.compile(r"([\d)%])\s*\*\s*(?=[\d(])")


def fix_multiply(text, subject):
    if CODE_CONTEXT.search(text):
        return text
    return STAR_RE.sub(r"\1 × ", TIMES_RE.sub(r"\1 × ", text))


# ── variable exponents:  x2 -> x²  (the risky one) ───────────────────────────
# A letter followed by a digit is a subscript at least as often as a power, so
# this rule refuses to fire unless the text looks unambiguously algebraic AND
# contains none of the known subscript idioms.
EXP_EXCLUDE = re.compile(
    r"https?://"                                  # image URLs
    r"|\b\d[spdf]\d"                              # electron config: 1s2 2p6
    r"|\bterms?\b|\bsequence|\bprogression|\bnth\b"   # a1, a2 = sequence terms
    r"|\bratio\b|direction\s+cosine|\bA\.?P\.?\b|\bG\.?P\.?\b"
    r"|\b[A-Z]\d\s*,\s*[A-Z]\d"                   # pattern lists: A1, B2, C4
    r"|[a-z]\d[a-z]\d"                            # l1l2, m1m2, n1n2
    r"|\bS\d\b|\ba\d\s*="                         # S2 = …, a2 = …
    r"|\bmole|equilibri|\breaction\b|\bcompound\b|\bmolecul|\bvalency\b",  # chemistry
    re.I,
)

# Something that genuinely reads as algebra, not prose that happens to contain "x2".
EXP_REQUIRE = re.compile(
    r"polynomial|equation|quadratic|\broots?\b|expression|simplif|factoris|factoriz"
    r"|coefficient|\bsolve\b|\bx\s*=|\bdegree of\b",
    re.I,
)

# Lowercase only. Algebraic unknowns are x, y, a, b, k, n and Greek; an uppercase
# letter before a digit is nearly always chemistry (H2O, O2, CO2) or an indexed
# constant (S2), where the digit is a subscript.
GREEK = "αβγδθλμνρσφω"
VAR = f"[a-z{GREEK}]"

# An indexed variable is introduced with the index 1 — "n1 sin i = n2 sin r",
# "S1, S2", "a1 + a2", "r1/r2". Nobody writes a power of one, so a letter seen
# with a trailing 1 is an index, and every digit on that letter is a subscript.
INDEX_RE = re.compile(rf"(?<![A-Za-z]{{2}})({VAR})1(?!\d)")

# Two preceding letters means this is inside a word ("the2"), not a variable.
# One lowercase is fine — "ax2" is the coefficient a times x squared. One
# uppercase is not: "Cl2" is chlorine gas, whose 2 is a subscript.
EXPONENT_RE = re.compile(rf"(?<![A-Za-z]{{2}})(?<![A-Z])({VAR})([2-9])(?!\d)(?!\.\d)")

# A bracketed expression can be raised to a power too: "(2x + 3y)2".
PAREN_POWER_RE = re.compile(r"(\))([2-9])(?!\d)(?!\.\d)")


def fix_exponent(text, subject):
    if EXP_EXCLUDE.search(text) or not EXP_REQUIRE.search(text):
        return text

    indexed = set(INDEX_RE.findall(text))

    def repl(m):
        var, digit = m.group(1), m.group(2)
        if var in indexed:
            return m.group(0)  # subscript, leave alone
        return var + to_super(digit)

    return PAREN_POWER_RE.sub(
        lambda m: m.group(1) + to_super(m.group(2)),
        EXPONENT_RE.sub(repl, text),
    )


# Every fixer takes (text, subject) so subject-specific rules stay in one place.
FIXERS = {
    "escape": lambda t, s: fix_escape(t),
    "currency": fix_currency,
    "currency_review": flag_currency_review,
    "degree": fix_degree,
    "caret": fix_caret,
    "sqrt": fix_sqrt,
    "unit": lambda t, s: fix_unit(t),
    "exponent": fix_exponent,
    "multiply": fix_multiply,
}


def apply_fixes(text, subject, categories):
    """Returns (new_text, [(category, before, after), ...])."""
    if not text:
        return text, []
    changes = []
    for cat in categories:
        new = FIXERS[cat](text, subject)
        if new != text:
            changes.append((cat, text, new))
            # Review-only categories must not leak into the text we would write back.
            if cat not in REVIEW_ONLY:
                text = new
    return text, changes


def snippet(before, after, width=60):
    """Shortest window showing what actually differs."""
    i = 0
    while i < min(len(before), len(after)) and before[i] == after[i]:
        i += 1
    start = max(0, i - width // 2)
    return before[start : i + width].replace("\n", " "), after[start : i + width].replace("\n", " ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--only", default=",".join(DEFAULT_CATEGORIES),
                    help="comma-separated subset of: " + ", ".join(CATEGORY_ORDER))
    ap.add_argument("--out", default=str(OUT_CSV), help="review CSV path")
    args = ap.parse_args()
    out_csv = Path(args.out)

    explicit = args.only != ",".join(DEFAULT_CATEGORIES)
    requested = {c.strip() for c in args.only.split(",") if c.strip()}
    bad = requested - set(FIXERS)
    if bad:
        sys.exit(f"Unknown category: {', '.join(sorted(bad))}")

    unsafe = requested & REVIEW_ONLY
    if unsafe and args.apply and explicit:
        # Asking for a review-only category by name alongside --apply is a mistake
        # worth stopping for. Inheriting it from the defaults is not.
        sys.exit(
            f"Refusing to --apply {', '.join(sorted(unsafe))}: these changes alter mathematical\n"
            "meaning and were measured wrong ~18% of the time. Generate the review CSV without\n"
            "--apply and correct those questions by hand."
        )
    if unsafe and args.apply:
        requested -= REVIEW_ONLY
        unsafe = set()

    # Always run in dependency order, whatever order the user typed them in.
    categories = [c for c in CATEGORY_ORDER if c in requested]

    print(f"{'APPLYING' if args.apply else 'DRY RUN'} — categories: {', '.join(categories)}\n")
    if unsafe:
        print(f"NOTE: {', '.join(sorted(unsafe))} is review-only and cannot be applied.\n")
    if args.apply:
        print("Review-only categories are skipped on --apply; "
              "run without --apply to regenerate their CSVs.\n")

    conn = pyodbc.connect(CONN_STR, timeout=60)
    cur = conn.cursor()
    cur.execute("""SELECT QuestionBankId, Subject, Grade, Difficulty,
                          QuestionText, OptionsJson, Explanation
                   FROM QuestionBank""")
    rows = cur.fetchall()
    print(f"Scanned {len(rows)} questions.\n")

    counts = Counter()
    touched_questions = set()
    review = []
    updates = []

    for qid, subj, grade, diff, qtext, opts, expl in rows:
        new_q, ch_q = apply_fixes(qtext or "", subj, categories)
        new_e, ch_e = apply_fixes(expl or "", subj, categories)

        # Options are a JSON array — fix each element, then re-serialise.
        new_o, ch_o = opts, []
        try:
            parsed = json.loads(opts or "[]")
            if isinstance(parsed, list):
                fixed_opts, per_opt = [], []
                for o in parsed:
                    f, c = apply_fixes(str(o), subj, categories)
                    fixed_opts.append(f)
                    per_opt.extend(c)
                if any(c[0] not in REVIEW_ONLY for c in per_opt):
                    new_o = json.dumps(fixed_opts, ensure_ascii=False)
                    ch_o = per_opt
        except (json.JSONDecodeError, TypeError):
            pass

        all_changes = ch_q + ch_e + ch_o
        if not all_changes:
            continue

        for field, chs in (("stem", ch_q), ("explanation", ch_e), ("options", ch_o)):
            for cat, before, after in chs:
                counts[cat] += 1
                b, a = snippet(before, after)
                review.append({
                    "questionBankId": str(qid), "subject": subj, "grade": grade,
                    "difficulty": diff, "field": field, "category": cat,
                    "action": "review" if cat in REVIEW_ONLY else "apply",
                    "before": b, "after": a,
                })

        # A question whose only findings are review-only must not be rewritten.
        if any(cat not in REVIEW_ONLY for cat, _, _ in all_changes):
            touched_questions.add(qid)
            updates.append((new_q, new_o, new_e, qid))

    with open(out_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["questionBankId", "subject", "grade", "difficulty",
                                           "field", "category", "action", "before", "after"])
        w.writeheader()
        w.writerows(review)

    print("Findings by category (one per field):")
    for cat in categories:
        tag = "REVIEW ONLY — not written" if cat in REVIEW_ONLY else "will be applied"
        print(f"  {cat:<16} {counts[cat]:>6}   {tag}")
    print(f"\nQuestions that would be rewritten: {len(touched_questions)}")
    print(f"Review CSV: {out_csv}")

    print("\n--- sample, 3 per category ---")
    for cat in categories:
        shown = [r for r in review if r["category"] == cat][:3]
        if not shown:
            continue
        print(f"\n[{cat}]")
        for r in shown:
            print(f"  {r['subject']} G{r['grade']} ({r['field']})")
            print(f"    before: {r['before']}")
            print(f"    after : {r['after']}")

    if not args.apply:
        print("\nDry run — nothing written. Re-run with --apply to commit.")
        conn.close()
        return

    # Snapshot the originals first so this run can be reversed.
    backup = out_csv.with_name(out_csv.stem + "_backup.csv")
    originals = {str(r[0]): (r[4], r[5], r[6]) for r in rows}
    with open(backup, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["questionBankId", "questionText", "optionsJson", "explanation"])
        for _, _, _, qid in updates:
            o = originals[str(qid)]
            w.writerow([str(qid), o[0], o[1], o[2]])
    print(f"\nBackup of {len(updates)} original rows: {backup}")

    print(f"Applying {len(updates)} row updates…")
    cur.fast_executemany = False
    for new_q, new_o, new_e, qid in updates:
        cur.execute(
            "UPDATE QuestionBank SET QuestionText = ?, OptionsJson = ?, Explanation = ? "
            "WHERE QuestionBankId = ?",
            new_q, new_o, new_e, qid,
        )
    conn.commit()
    print(f"Committed {len(updates)} updates.")
    conn.close()


if __name__ == "__main__":
    main()
