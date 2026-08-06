/**
 * Shared maths-notation helpers.
 *
 * Three jobs, one source of truth:
 *   protectCurrency()      — render-time guard so a money "$" can never open a KaTeX span
 *   repastePdfNotation()   — repair the artefacts you get pasting from a PDF (x2 -> x², 20 0 -> 20°)
 *   detectNotationIssues() — warn an admin about suspicious text before it reaches the database
 *
 * Used by components/MarkdownMath.tsx (guard) and app/admin (repair + warnings).
 */

// ── 1. Currency guard ───────────────────────────────────────────────────────

/** Words that mark a "$…$" span as prose, not maths. */
const PROSE_WORD = /\b(?:and|the|for|of|in|is|are|was|were|to|from|with|a|an|by|on|at|he|she|it|they|his|her|their|bills?|notes?|coins?|cost[s]?|price[s]?|profit|loss|salary|paid|pays?|buy|buys|bought|sold|sells?|spend[s]?|spent|save[s]?|saved|each|per|total|amount|rupees?|dollars?)\b/i;

/** Two adjacent alphabetic words — a strong prose signal. */
const TWO_WORDS = /[A-Za-z]{2,}\s+[A-Za-z]{2,}/;

/**
 * A "$…$" span is currency (not maths) when either:
 *   (a) its contents read like prose  — "$1400, $1600, and $2200 respectively in a…"
 *   (b) the closing "$" is itself glued to a digit — "$20.00 - $15.50", where that
 *       "closing" delimiter is really the next amount's opening one.
 */
function spanIsCurrency(content: string, charAfterClose: string): boolean {
  if (/\d/.test(charAfterClose)) return true;
  if (TWO_WORDS.test(content) && PROSE_WORD.test(content)) return true;
  return false;
}

/** Contents that are unambiguously maths, regardless of anything else. */
const DEFINITELY_MATH = /[\\^_{}]/;

/**
 * Escape "$" characters that denote money so remark-math never pairs them.
 *
 * Genuine LaTeX ($x$, $2x$, $\frac{7}{20}$, $11011011_2$) is left untouched.
 * Idempotent: an already-escaped "\$" is skipped.
 */
export function protectCurrency(input: string): string {
  if (!input.includes("$")) return input;

  // Collect the offsets of every unescaped "$".
  const marks: number[] = [];
  for (let i = 0; i < input.length; i++) {
    if (input[i] === "$" && input[i - 1] !== "\\") marks.push(i);
  }
  if (marks.length === 0) return input;

  const escapeAt = new Set<number>();

  // Walk delimiters in pairs, mirroring how remark-math consumes them.
  let k = 0;
  while (k < marks.length - 1) {
    const open = marks[k];
    const close = marks[k + 1];
    const content = input.slice(open + 1, close);
    const after = input[close + 1] ?? "";

    if (!DEFINITELY_MATH.test(content) && spanIsCurrency(content, after)) {
      escapeAt.add(open);
      escapeAt.add(close);
      k += 1; // the closing "$" may open the next amount — reconsider it
    } else {
      k += 2; // consumed as a genuine maths span
    }
  }

  // Any delimiter left unpaired that is glued to a digit is money too.
  const lastUnpaired = marks.length % 2 === 1 ? marks[marks.length - 1] : -1;
  for (const m of marks) {
    if (escapeAt.has(m)) continue;
    const isOdd = m === lastUnpaired;
    if (isOdd && /\d/.test(input[m + 1] ?? "")) escapeAt.add(m);
  }

  if (escapeAt.size === 0) return input;

  let out = "";
  for (let i = 0; i < input.length; i++) {
    if (escapeAt.has(i)) out += "\\$";
    else out += input[i];
  }
  return out;
}

// ── 2. PDF-paste repair ─────────────────────────────────────────────────────

const SUP: Record<string, string> = {
  "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
  "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
};

const toSuper = (digits: string) =>
  digits.split("").map((d) => SUP[d] ?? d).join("");

/** Units that are commonly written squared or cubed. */
const UNIT = "(?:cm|mm|km|m|ft|in|sq|cu)";

export interface RepairResult {
  text: string;
  changes: { rule: string; before: string; after: string }[];
}

/**
 * Repair the notation damage that copy-paste from a PDF introduces.
 *
 * Superscripts and degree signs get flattened into ordinary digits, which turns a
 * valid expression into a different, usually meaningless one:
 *   "x2 - 5x + 4"   should be  "x² - 5x + 4"
 *   "7x + 200"      should be  "7x + 20°"
 *   "154 m2"        should be  "154 m²"
 *
 * Conservative by design: only fires on shapes that are unambiguous in context, and
 * reports every change so the caller can show them for confirmation.
 */
export function repastePdfNotation(input: string): RepairResult {
  const changes: RepairResult["changes"] = [];
  let text = input;

  const apply = (rule: string, re: RegExp, fn: (m: RegExpMatchArray) => string) => {
    text = text.replace(re, (...args) => {
      const m = args.slice(0, -2) as unknown as RegExpMatchArray;
      const before = m[0];
      const after = fn(m);
      if (before !== after) changes.push({ rule, before, after });
      return after;
    });
  };

  // ∠ABC = 7x + 200  ->  7x + 20°   (degree sign flattened to a trailing zero)
  // Only inside text that already talks about angles, so plain numbers are safe.
  // Must run before the exponent rule, which would otherwise read "3x0" as "3x⁰".
  if (/∠|angle/i.test(text)) {
    apply("degree", /(\d+)0(?=\s*(?:and|,|\.|$|\)))/g, (m) => `${m[1]}°`);
    apply("degree-var", /(?<![A-Za-z])([a-z])0\b/g, (m) => `${m[1]}°`);
  }

  // 6x4 + 8x3 + 17x2  ->  6x⁴ + 8x³ + 17x²   (variable immediately followed by a digit)
  // No \b before the letter: in "6x4" the digit and the letter are both word
  // characters, so there is no boundary to match. Guard with a lookbehind instead,
  // which also keeps the rule to single-letter variables ("Grade 5" is untouched).
  apply("exponent-var", /(?<![A-Za-z])([a-zA-Z])(\d+)(?![\d.])/g, (m) =>
    m[2] === "1" ? m[0] : `${m[1]}${toSuper(m[2])}`
  );

  // 154 m2 / 24 cm3 / 16 sq cm2  ->  m², cm³
  apply("unit-power", new RegExp(`\\b(${UNIT})([23])\\b`, "g"), (m) => `${m[1]}${toSuper(m[2])}`);

  // a^3, x^12  ->  a³, x¹²
  apply("caret", /\^(\d+)/g, (m) => toSuper(m[1]));

  // sqrt(7)/4  ->  √(7)/4
  apply("sqrt", /\bsqrt\s*/gi, () => "√");

  // 12 x 3, (1/2) x 3  ->  12 × 3   (multiplication written as the letter x)
  // Requires whitespace around the x so "6x4" (an exponent) is never caught here.
  apply("times", /([\d)])\s+[xX]\s+(?=[\d(])/g, (m) => `${m[1]} × `);

  // 10 * 4  ->  10 × 4
  apply("asterisk", /([\d)])\s*\*\s*(?=[\d(])/g, (m) => `${m[1]} × `);

  // 23.5 degrees  ->  23.5°
  apply("degree-word", /(\d+(?:\.\d+)?)\s*degrees?\b/g, (m) => `${m[1]}°`);

  // <= >= != -> ≤ ≥ ≠
  apply("inequality", /<=|>=|!=|<>/g, (m) =>
    m[0] === "<=" ? "≤" : m[0] === ">=" ? "≥" : "≠"
  );

  return { text, changes };
}

// ── 3. Pre-save warnings ────────────────────────────────────────────────────

export interface NotationIssue {
  severity: "error" | "warning";
  message: string;
  sample?: string;
}

/**
 * Signatures of a LaTeX command destroyed by string-escape processing:
 * "\times" -> TAB + "imes", "\rightarrow" -> CR + "ightarrow", "\frac" -> FF + "rac".
 * Tab, CR and LF are legitimate whitespace on their own, so match them only when
 * followed by the tail of the command they ate.
 */
const CORRUPT_ESCAPE =
  /\t(?=imes|heta|an\b|o\b)|\r\n?(?=ightarrow|ight)|\f(?=rac)|[\x08](?=ar\b)|\n(?=eq\b)|[\x00-\x07\x0b\x0e-\x1f]/;

/**
 * Inspect text destined for the question bank and report anything that will
 * store or render incorrectly. Runs in the admin form before save.
 */
export function detectNotationIssues(input: string): NotationIssue[] {
  const issues: NotationIssue[] = [];
  if (!input) return issues;

  if (CORRUPT_ESCAPE.test(input)) {
    issues.push({
      severity: "error",
      message:
        "Contains an invisible control character — a LaTeX command was corrupted (e.g. \\times became a tab). Retype it.",
    });
  }

  // A "$" that will be swallowed by the maths renderer.
  if (input !== protectCurrency(input)) {
    issues.push({
      severity: "error",
      message:
        'Currency "$" detected. It will be rendered as a formula and the spaces will disappear. Use ₹ instead.',
    });
  }

  const flatExp = input.match(/\b[a-zA-Z][2-9]\b/);
  if (flatExp) {
    issues.push({
      severity: "warning",
      message:
        "Looks like a flattened exponent from a PDF paste — this changes the meaning of the expression.",
      sample: flatExp[0],
    });
  }

  const flatUnit = input.match(new RegExp(`\\b${UNIT}[23]\\b`));
  if (flatUnit) {
    issues.push({
      severity: "warning",
      message: "Unit written without a superscript.",
      sample: flatUnit[0],
    });
  }

  const unmatchedBrace = (input.match(/\{/g)?.length ?? 0) !== (input.match(/\}/g)?.length ?? 0);
  if (unmatchedBrace) {
    issues.push({ severity: "error", message: "Unbalanced { } braces — KaTeX will fail to render." });
  }

  // KaTeX has no glyph for these; they render as blank boxes inside $…$.
  const badGlyph = input.match(/\$[^$]*([★☆◆◇∥—])[^$]*\$/);
  if (badGlyph) {
    issues.push({
      severity: "warning",
      message: `The symbol "${badGlyph[1]}" has no maths glyph and will render as an empty box. Move it outside the $…$.`,
      sample: badGlyph[1],
    });
  }

  return issues;
}
