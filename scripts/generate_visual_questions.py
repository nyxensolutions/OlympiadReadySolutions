"""
generate_visual_questions.py
Generates programmatic image-based questions (Logical Reasoning / Math),
uploads each image to Cloudinary, and POSTs the questions to the Admin API.

Requirements:
    pip install pillow cloudinary requests

Config (edit the section below OR set environment variables):
    CLOUDINARY_CLOUD_NAME
    CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET
    ADMIN_API_BASE   e.g. http://localhost:5062
    ADMIN_API_KEY    value of X-Admin-Key header
"""

import os, io, json, random, time, sys
import requests
import cloudinary
import cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont

# ── CONFIG ────────────────────────────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"

ADMIN_API_BASE = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY  = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")   # set this!

# How many questions to generate per generator
QUESTIONS_PER_TYPE = 20
# ─────────────────────────────────────────────────────────────────────────────

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

RUN_ID = int(time.time())
questions_generated = []
questions_failed = []


# ── HELPERS ───────────────────────────────────────────────────────────────────

def img_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def upload_to_cloudinary(img: Image.Image, label: str) -> str | None:
    """Upload a PIL image to Cloudinary and return the secure URL."""
    data = img_to_bytes(img)
    public_id = f"{CLOUDINARY_FOLDER}/{label}-{RUN_ID}-{random.randint(1000,9999)}"
    try:
        result = cloudinary.uploader.upload(
            data,
            public_id=public_id,
            overwrite=False,
            resource_type="image",
        )
        return result["secure_url"]
    except Exception as e:
        print(f"  [FAIL] Cloudinary upload failed for {label}: {e}")
        return None


def post_question(q: dict):
    """POST a single question to the admin add-question endpoint."""
    if not ADMIN_API_KEY:
        print("  [!] ADMIN_API_KEY not set — saving to local JSON only")
        return False
    url = f"{ADMIN_API_BASE}/api/admin/add-question"
    try:
        r = requests.post(
            url,
            json=q,
            headers={"X-Admin-Key": ADMIN_API_KEY},
            timeout=15,
        )
        if r.status_code in (200, 201):
            return True
        else:
            print(f"  [FAIL] API error {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")
        return False


def make_question(
    img: Image.Image,
    label: str,
    question_text: str,
    options: list[str],   # exactly 4 strings
    correct_idx: int,     # 0-based index into options
    subject: str,
    grade: int,
    topic: str,
    subtopic: str,
    difficulty: str,
    explanation: str,
):
    print(f"  Uploading: {label}...", end=" ", flush=True)
    url = upload_to_cloudinary(img, label)
    if url is None:
        questions_failed.append(question_text)
        return

    correct_letter = chr(65 + correct_idx)
    q = {
        "subject": subject,
        "grade": grade,
        "topic": topic,
        "subTopic": subtopic,
        "difficulty": difficulty,
        "questionText": question_text,
        "imageUrl": url,
        "options": options,
        "correctAnswer": correct_letter,
        "explanation": explanation,
    }
    print("[OK]", end=" ", flush=True)

    ok = post_question(q)
    if ok:
        print("-> posted")
    else:
        print("-> saved locally")
        questions_generated.append(q)


# ── GENERATORS ────────────────────────────────────────────────────────────────

# --- 1. Count Shapes (Grade 1–3 Logical Reasoning) ---
SHAPE_COLORS = {
    "circle":   [("#AED6F1","#2E86C1","blue"),   ("#F9A8D4","#BE185D","pink"),  ("#BBF7D0","#15803D","green"), ("#FDE68A","#92400E","yellow")],
    "square":   [("#A9DFBF","#1E8449","green"),   ("#FCA5A5","#DC2626","red"),   ("#C4B5FD","#7C3AED","purple"),("#FED7AA","#C2410C","orange")],
    "triangle": [("#F9E79F","#B7950B","yellow"),  ("#A5F3FC","#0E7490","cyan"),  ("#FCA5A5","#DC2626","red"),   ("#D9F99D","#4D7C0F","lime")],
}
COUNT_QUESTIONS = [
    "How many {color} {shape}s can you count in the image?",
    "Count the {color} {shape}s. How many are there?",
    "Look carefully — how many {color} {shape}s do you see?",
    "How many {shape}s are drawn in {color} colour?",
    "What is the total number of {color} {shape}s shown?",
]

def gen_count_shapes(n: int):
    print(f"\n[Count Shapes] generating {n} questions...")
    used_texts = set()
    for i in range(n):
        img = Image.new("RGB", (320, 220), "white")
        draw = ImageDraw.Draw(img)
        shape = random.choice(["circle", "square", "triangle"])
        fill_col, outline_col, color_name = random.choice(SHAPE_COLORS[shape])
        count = random.randint(3, 8)
        placed = []
        for _ in range(count * 5):
            if len(placed) >= count:
                break
            x = random.randint(15, 255)
            y = random.randint(15, 165)
            s = random.randint(25, 45)
            if any(abs(x - px) < s + ps and abs(y - py) < s + ps for px, py, ps in placed):
                continue
            placed.append((x, y, s))
            if shape == "circle":
                draw.ellipse([x, y, x+s, y+s], fill=fill_col, outline=outline_col, width=2)
            elif shape == "square":
                draw.rectangle([x, y, x+s, y+s], fill=fill_col, outline=outline_col, width=2)
            else:
                draw.polygon([(x+s//2, y), (x, y+s), (x+s, y+s)], fill=fill_col, outline=outline_col, width=2)
        actual = len(placed)
        opts = list({actual, actual+1, actual-1, actual+2})
        opts = [o for o in opts if o > 0]
        while len(opts) < 4:
            opts.append(actual + random.randint(3, 5))
            opts = list(set(opts))
        random.shuffle(opts)
        opts = opts[:4]
        cidx = opts.index(actual) if actual in opts else 0
        if actual not in opts:
            opts[0] = actual
            cidx = 0

        # Generate unique question text
        template = random.choice(COUNT_QUESTIONS)
        q_text = template.format(color=color_name, shape=shape)
        # If text collides, append the count as a hint variant
        if q_text in used_texts:
            q_text = f"There are some {color_name} {shape}s in the image. How many are there?"
        # Still collides? add index
        if q_text in used_texts:
            q_text = f"Count the {color_name} {shape}s in picture #{i+1}. How many are there?"
        used_texts.add(q_text)

        grade = random.choice([1, 2, 3])
        make_question(
            img, "shapes-count",
            q_text,
            [str(o) for o in opts], cidx,
            "Logical Reasoning", grade,
            "Patterns and Shapes", "Counting Shapes",
            "Foundation",
            f"There are exactly {actual} {color_name} {shape}s in the picture.",
        )


# --- 2. Odd One Out — Shape (Grade 1–4) ---
ODD_QUESTIONS = [
    "Three figures are alike and one is different. Which is the odd one out?",
    "Which figure does NOT belong with the others?",
    "One shape is different from the rest. Which one?",
    "Find the shape that is different from the other three.",
    "Which of the four figures does not match the group?",
]

def gen_odd_shape(n: int):
    import math
    print(f"\n[Odd Shape Out] generating {n} questions...")
    shape_names = ["circle", "square", "triangle", "pentagon"]
    used_texts = set()
    for i in range(n):
        base = random.choice(shape_names)
        odd  = random.choice([s for s in shape_names if s != base])
        items = [base, base, base, odd]
        random.shuffle(items)
        odd_pos = items.index(odd)
        img = Image.new("RGB", (420, 160), "white")
        draw = ImageDraw.Draw(img)
        color = random.choice(["#E74C3C","#2980B9","#27AE60","#8E44AD"])
        for j, sh in enumerate(items):
            x, y, s = 20 + j*95, 25, 65
            label = chr(65+j)
            try:
                draw.text((x+s//2-6, y+s+8), label, fill="#333333")
            except Exception:
                pass
            if sh == "circle":
                draw.ellipse([x,y,x+s,y+s], outline=color, width=3)
            elif sh == "square":
                draw.rectangle([x,y,x+s,y+s], outline=color, width=3)
            elif sh == "triangle":
                draw.polygon([(x+s//2,y),(x,y+s),(x+s,y+s)], outline=color, width=3)
            elif sh == "pentagon":
                pts = [(x+s//2 + int(s//2*math.cos(math.radians(90+72*k))),
                        y+s//2 + int(s//2*math.sin(math.radians(90+72*k)))) for k in range(5)]
                draw.polygon(pts, outline=color, width=3)

        # Unique question text combining template + base shape name
        q_text = f"Three figures are {base}s and one is different — which figure is the odd one out?"
        if q_text in used_texts:
            q_text = random.choice(ODD_QUESTIONS) + f" (All are {base}s except one.)"
        if q_text in used_texts:
            q_text = f"Which of A, B, C, D is NOT a {base}? (Set {i+1})"
        used_texts.add(q_text)

        grade = random.choice([1, 2, 3, 4])
        make_question(
            img, "odd-shape",
            q_text,
            ["Figure A","Figure B","Figure C","Figure D"], odd_pos,
            "Logical Reasoning", grade,
            "Patterns and Shapes", "Odd One Out",
            "Foundation",
            f"Figure {chr(65+odd_pos)} is a {odd}, while the others are {base}s.",
        )


# --- 3. Colour Pattern (Grade 1–3) ---
PATTERN_QUESTIONS = [
    "What colour comes next in the pattern?",
    "Which colour should fill the empty box to continue the pattern?",
    "The circles follow a pattern. What colour comes next?",
    "Complete the colour sequence — what comes after the last circle?",
    "What is the next colour in this repeating pattern?",
]

def gen_colour_pattern(n: int):
    print(f"\n[Colour Pattern] generating {n} questions...")
    all_colors = {
        "Red": "#E74C3C", "Blue": "#2980B9", "Green": "#27AE60",
        "Yellow": "#F1C40F", "Purple": "#8E44AD", "Orange": "#E67E22",
    }
    used_texts = set()
    for i in range(n):
        names = random.sample(list(all_colors.keys()), 2)
        c1, c2 = names
        seq = [c1, c2, c1, c2]   # pattern: next = c1
        ans = c1
        img = Image.new("RGB", (420, 120), "white")
        draw = ImageDraw.Draw(img)
        for j, col in enumerate(seq):
            x = 15 + j*80
            draw.ellipse([x, 20, x+60, 80], fill=all_colors[col])
        # question mark box
        draw.rectangle([335, 20, 395, 80], outline="#333333", width=2)
        draw.text((355, 40), "?", fill="#333333")

        wrong_names = [c for c in all_colors if c != ans]
        random.shuffle(wrong_names)
        opts = [ans] + wrong_names[:3]
        random.shuffle(opts)
        cidx = opts.index(ans)

        # Unique question text using the actual colour pair
        q_text = f"The pattern alternates {c1} and {c2}. What colour comes next?"
        if q_text in used_texts:
            q_text = f"In the {c1}-{c2} repeating pattern, what colour fills the box marked '?'?"
        if q_text in used_texts:
            q_text = f"Pattern: {c1}, {c2}, {c1}, {c2}, ? — what colour is next? (Set {i+1})"
        used_texts.add(q_text)

        grade = random.choice([1, 2, 3])
        make_question(
            img, "colour-pattern",
            q_text,
            opts, cidx,
            "Logical Reasoning", grade,
            "Patterns and Shapes", "Colour Patterns",
            "Foundation",
            f"The pattern is {c1}, {c2}, {c1}, {c2}, ... so the next colour is {ans}.",
        )


MIRROR_QUESTIONS = [
    "What is the mirror image of the shape shown on the left?",
    "If you place a mirror on the dotted line, which option shows the reflection?",
    "Which figure is the mirror image of the arrow on the left side?",
    "The shape on the left is reflected. What does its mirror image look like?",
    "Which option correctly shows the mirror reflection of the left figure?",
]

# --- 4. Mirror Image (Grade 3–5) ---
def gen_mirror(n: int):
    print(f"\n[Mirror Image] generating {n} questions...")
    used_texts = set()
    for i in range(n):
        img = Image.new("RGB", (300, 200), "white")
        draw = ImageDraw.Draw(img)
        # Draw a simple asymmetric arrow pointing right -> correct mirror is ←
        # Arrow pointing right
        draw.polygon([(50,80),(130,80),(130,60),(180,100),(130,140),(130,120),(50,120)],
                     fill="#AED6F1", outline="#2471A3", width=2)
        draw.line([(150,10),(150,190)], fill="#AAAAAA", width=1)
        draw.text((10,10), "Original", fill="#555555")
        draw.text((155,10), "Mirror?", fill="#555555")
        # We'll label the options as text descriptions since PIL can't render nicely
        opts = ["Arrow pointing Left", "Arrow pointing Right", "Arrow pointing Up", "Arrow pointing Down"]
        cidx = 0
        grade = random.choice([3, 4, 5])
        q_text = MIRROR_QUESTIONS[i % len(MIRROR_QUESTIONS)]
        if q_text in used_texts:
            q_text = f"Mirror image question #{i+1}: which option shows the correct reflection?"
        used_texts.add(q_text)
        make_question(
            img, "mirror",
            q_text,
            opts, cidx,
            "Logical Reasoning", grade,
            "Spatial Reasoning", "Mirror Images",
            "Advanced",
            "A mirror image flips the shape horizontally, so a right-pointing arrow becomes a left-pointing arrow.",
        )


SIZE_SHAPES  = ["circle", "square", "triangle", "star", "diamond"]
SIZE_COLORS  = ["#E74C3C","#27AE60","#2980B9","#E67E22","#8E44AD"]
SIZE_Q_TEMPLATES = [
    "Which {shape} is the biggest?",
    "Which {shape} has the largest size?",
    "Point to the largest {shape} among A, B, C, D.",
    "Which of these {shape}s is the greatest in size?",
    "Identify the biggest {shape} in the image.",
]

# --- 5. Size Comparison (Grade 1–2) ---
def gen_size_comparison(n: int):
    print(f"\n[Size Comparison] generating {n} questions...")
    used_texts = set()
    for i in range(n):
        img = Image.new("RGB", (320, 180), "white")
        draw = ImageDraw.Draw(img)
        sizes = random.sample([30, 55, 80, 100], 4)
        labels = ["A","B","C","D"]
        shape_name = random.choice(SIZE_SHAPES)
        color = random.choice(SIZE_COLORS)
        max_s = max(sizes)
        max_idx = sizes.index(max_s)
        for j, s in enumerate(sizes):
            x = 15 + j*75 + (75-s)//2
            y = 90 - s//2
            draw.ellipse([x, y, x+s, y+s], fill=color)
            try:
                draw.text((15 + j*75 + 30, 145), labels[j], fill="#333333")
            except Exception:
                pass

        template = SIZE_Q_TEMPLATES[i % len(SIZE_Q_TEMPLATES)]
        q_text = template.format(shape=shape_name)
        if q_text in used_texts:
            q_text = f"Which {shape_name} is bigger than all the rest? (Set {i+1})"
        used_texts.add(q_text)

        grade = random.choice([1, 2])
        make_question(
            img, "size-compare",
            q_text,
            [f"{shape_name.capitalize()} {l}" for l in labels], max_idx,
            "Logical Reasoning", grade,
            "Patterns and Shapes", "Size Comparison",
            "Foundation",
            f"{shape_name.capitalize()} {labels[max_idx]} is the largest.",
        )


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not ADMIN_API_KEY:
        print("[!]  ADMIN_API_KEY is not set. Questions will be saved to generated_questions.json only.")
        print("   Set it with: set ADMIN_API_KEY=your_key_here\n")

    gen_count_shapes(QUESTIONS_PER_TYPE)
    gen_odd_shape(QUESTIONS_PER_TYPE)
    gen_colour_pattern(QUESTIONS_PER_TYPE)
    gen_mirror(QUESTIONS_PER_TYPE)
    gen_size_comparison(QUESTIONS_PER_TYPE)

    # Save any that failed to post (for manual import)
    out_path = os.path.join(os.path.dirname(__file__), "generated_questions.json")
    if questions_generated:
        with open(out_path, "w") as f:
            json.dump(questions_generated, f, indent=2)
        print(f"\n[FILE] {len(questions_generated)} questions saved to {out_path} (import via admin API)")

    total = QUESTIONS_PER_TYPE * 5
    failed = len(questions_failed)
    print(f"\n[DONE] Done — {total - failed}/{total} succeeded, {failed} failed")
    if questions_failed:
        print("Failed questions:")
        for q in questions_failed:
            print(f"  - {q}")
