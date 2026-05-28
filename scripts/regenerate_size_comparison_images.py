"""
regenerate_size_comparison_images.py
Fetches Size Comparison questions, re-draws images with the correct shape
(square, circle, triangle, etc.) at the right sizes, uploads to Cloudinary,
and PUTs the updated imageUrl + cleaned questionText back.

Usage:
    python scripts/regenerate_size_comparison_images.py
"""

import os, io, math, time, re, random, requests
import cloudinary, cloudinary.uploader
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── CONFIG ────────────────────────────────────────────────────────────────────
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")
# ─────────────────────────────────────────────────────────────────────────────

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

# The original generator always sampled from these four sizes
ORIGINAL_SIZES = [30, 55, 80, 100]

# Shape name aliases (lowercase)
SHAPE_ALIASES = {
    "square":   "square",
    "circle":   "circle",
    "triangle": "triangle",
    "star":     "star",
    "diamond":  "diamond",
    "pentagon": "pentagon",
}

# Nice fill / outline colours per shape
SHAPE_COLORS = {
    "square":   ((99,  179, 237), (49,  130, 206)),   # blue
    "circle":   ((154, 205, 50),  (85,  150, 20)),    # green
    "triangle": ((246, 173, 85),  (196, 118, 20)),    # orange
    "star":     ((236, 100, 100), (185, 50,  50)),    # red
    "diamond":  ((167, 139, 250), (109, 77,  201)),   # purple
    "pentagon": ((72,  209, 204), (32,  160, 155)),   # teal
}

LABEL_FONT_SIZE = 28


def load_font(size: int, bold: bool = False):
    paths = (
        ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"]
        if bold else
        ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for fp in paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def star_points(cx, cy, r, points=5):
    """Return polygon points for a star."""
    pts = []
    inner_r = r * 0.42
    for i in range(points * 2):
        angle = math.radians(i * 180 / points - 90)
        rr = r if i % 2 == 0 else inner_r
        pts.append((cx + rr * math.cos(angle), cy + rr * math.sin(angle)))
    return pts


def pentagon_points(cx, cy, r):
    pts = []
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def draw_shape(draw: ImageDraw.ImageDraw, shape: str, cx: int, cy: int,
               s: int, fill, outline, scale: int = 1):
    """
    Draw `shape` centred at (cx, cy) fitting within a square of side `s`.
    All coords are in the 2x upscaled space (scale=2 passed from caller).
    """
    r = s // 2

    if shape == "circle":
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline,
                     width=max(2, s // 18))

    elif shape == "square":
        # Rounded rectangle feel — use plain rect with thick outline
        draw.rectangle([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline,
                       width=max(2, s // 18))

    elif shape == "triangle":
        pts = [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)]
        draw.polygon(pts, fill=fill, outline=outline)
        draw.line(pts + [pts[0]], fill=outline, width=max(2, s // 18))

    elif shape == "diamond":
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        draw.polygon(pts, fill=fill, outline=outline)
        draw.line(pts + [pts[0]], fill=outline, width=max(2, s // 18))

    elif shape == "star":
        pts = star_points(cx, cy, r)
        draw.polygon(pts, fill=fill, outline=outline)

    elif shape == "pentagon":
        pts = pentagon_points(cx, cy, r)
        draw.polygon(pts, fill=fill, outline=outline)
        draw.line(pts + [pts[0]], fill=outline, width=max(2, s // 18))

    else:
        # fallback: circle
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline,
                     width=max(2, s // 18))


def make_size_comparison_image(shape: str, sizes: list[int]) -> Image.Image:
    """
    Draw 4 shapes (A B C D) with the given pixel sizes, well-spaced, no overlap.
    Render at 2x then downscale for quality.
    """
    scale   = 2
    n       = len(sizes)
    max_s   = max(sizes)            # largest shape size in pixels
    cell_w  = max_s + 40            # cell width gives comfortable padding
    img_w   = n * cell_w + 40
    img_h   = max_s + 100           # room for shape + label below

    S_w, S_h = img_w * scale, img_h * scale
    img  = Image.new("RGB", (S_w, S_h), (250, 250, 250))
    draw = ImageDraw.Draw(img)

    # Subtle grid background
    for y in range(0, S_h, 16):
        draw.line([(0, y), (S_w, y)], fill=(240, 240, 240), width=1)
    for x in range(0, S_w, 16):
        draw.line([(x, 0), (x, S_h)], fill=(240, 240, 240), width=1)

    fill_col, outline_col = SHAPE_COLORS.get(shape, ((150, 150, 200), (80, 80, 150)))
    label_font = load_font(LABEL_FONT_SIZE * scale, bold=True)

    for j, s in enumerate(sizes):
        s_scaled = s * scale
        cx = (20 + j * cell_w + cell_w // 2) * scale
        cy = (20 + max_s // 2 + (max_s - s) // 2 + s // 2) * scale   # bottom-align

        # Drop shadow
        shadow_off = max(3, s_scaled // 20)
        draw_shape(draw, shape, cx + shadow_off, cy + shadow_off,
                   s_scaled, (180, 180, 180), (160, 160, 160), scale)

        # Actual shape
        draw_shape(draw, shape, cx, cy, s_scaled, fill_col, outline_col, scale)

        # Label (A / B / C / D)
        label = chr(65 + j)
        lx = cx
        ly = (20 + max_s + 14) * scale
        try:
            bb = draw.textbbox((0, 0), label, font=label_font)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
        except AttributeError:
            tw, th = draw.textsize(label, font=label_font)
        draw.text((lx - tw // 2, ly), label, font=label_font, fill=(50, 50, 50))

    # Downscale 2x → 1x
    img = img.resize((img_w, img_h), Image.LANCZOS)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    return img


# ── HELPERS ───────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    text = re.sub(r'\s*\(\s*Set\s+\d+\s*\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*\(\s*Clock\s+\d+\s*\)', '', text, flags=re.IGNORECASE)
    return text.strip()


def parse_shape_from_options(options: list[str]) -> str:
    """Extract shape name from options like ['Square A', 'Square B', ...]"""
    for opt in options:
        word = opt.strip().split()[0].lower() if opt.strip() else ""
        if word in SHAPE_ALIASES:
            return SHAPE_ALIASES[word]
    return "square"   # safe default


def parse_shape_from_text(text: str) -> str:
    text_lower = text.lower()
    for name in SHAPE_ALIASES:
        if name in text_lower:
            return SHAPE_ALIASES[name]
    return "square"


def build_sizes_for_correct(correct_letter: str) -> list[int]:
    """
    Return a permutation of ORIGINAL_SIZES where the largest (100) is at
    the index corresponding to correct_letter (A=0, B=1, C=2, D=3).
    """
    correct_idx = ord(correct_letter.upper()) - ord('A')
    others = [s for s in ORIGINAL_SIZES if s != 100]
    random.shuffle(others)
    sizes = others[:]
    sizes.insert(correct_idx, 100)
    return sizes


def fetch_size_comparison_questions() -> list[dict]:
    # Fetch by topic+subject (fast indexed query), then filter subTopic in Python
    all_items = []
    page = 1
    while True:
        r = requests.get(f"{ADMIN_API_BASE}/api/admin/questions",
            params={"topic": "Patterns and Shapes", "subject": "Logical Reasoning",
                    "pageSize": 100, "page": page},
            headers={"X-Admin-Key": ADMIN_API_KEY}, timeout=60)
        if r.status_code != 200:
            print(f"  [FAIL] GET page {page}: {r.status_code} {r.text[:150]}")
            break
        data = r.json()
        items = data.get("items", data.get("results", []))
        if not items:
            break
        # Filter to Size Comparison only
        for item in items:
            st = (item.get("subTopic") or "").strip().lower()
            if "size" in st and "comparison" in st:
                all_items.append(item)
        fetched = (page - 1) * 100 + len(items)
        if fetched >= data.get("total", 0):
            break
        page += 1
    return all_items


def upload_image(img: Image.Image) -> str | None:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    public_id = f"{CLOUDINARY_FOLDER}/size-regen-{int(time.time())}-{random.randint(1000,9999)}"
    try:
        result = cloudinary.uploader.upload(
            buf.getvalue(), public_id=public_id, overwrite=False, resource_type="image"
        )
        return result["secure_url"]
    except Exception as e:
        print(f"  [FAIL] Cloudinary: {e}")
        return None


def update_question(q_id: str, q: dict, new_image_url: str, new_text: str) -> bool:
    payload = {
        "subject":       q["subject"],
        "grade":         q["grade"],
        "topic":         q["topic"],
        "subTopic":      q.get("subTopic", "Size Comparison"),
        "difficulty":    q.get("difficulty", "Foundation"),
        "questionText":  new_text,
        "imageUrl":      new_image_url,
        "options":       q["options"],
        "correctAnswer": q["correctAnswer"],
        "explanation":   q.get("explanation", ""),
    }
    try:
        r = requests.put(
            f"{ADMIN_API_BASE}/api/admin/questions/{q_id}",
            json=payload,
            headers={"X-Admin-Key": ADMIN_API_KEY},
            timeout=15,
        )
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"  [FAIL] PUT: {e}")
        return False


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("Fetching Size Comparison questions...")
    questions = fetch_size_comparison_questions()
    print(f"  Total: {len(questions)}")

    ok = fail = skip = 0

    for q in questions:
        q_id         = q.get("questionBankId") or q.get("QuestionBankId")
        raw_text     = q.get("questionText", "")
        clean        = clean_text(raw_text)
        options      = q.get("options", [])
        correct_ltr  = q.get("correctAnswer", "A")

        # Determine the intended shape
        shape = parse_shape_from_options(options)
        if shape == "square":   # double-check via question text
            shape = parse_shape_from_text(raw_text) or shape

        # Build sizes so correct answer maps to the largest shape
        sizes = build_sizes_for_correct(correct_ltr)

        safe_shape = shape.encode('ascii', 'replace').decode()
        safe_text  = clean.encode('ascii', 'replace').decode()
        print(f"  {q_id}  shape={safe_shape}  correct={correct_ltr}  "
              f"sizes={sizes}  \"{safe_text[:45]}\"...", end=" ", flush=True)

        img = make_size_comparison_image(shape, sizes)
        url = upload_image(img)
        if not url:
            print("[FAIL] upload")
            fail += 1
            continue

        success = update_question(q_id, q, url, clean)
        if success:
            print("[OK]")
            ok += 1
        else:
            print("[FAIL] PUT")
            fail += 1

        time.sleep(0.3)

    print(f"\n[DONE] {ok} updated, {fail} failed, {skip} skipped.")


if __name__ == "__main__":
    main()
