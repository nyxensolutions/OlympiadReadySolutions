"""
regenerate_coin_images.py
Fetches existing coin/money questions from the admin API, re-draws their
images with realistic-looking Indian coins (metallic gradient, rim, proper
denomination), uploads to Cloudinary, and PUTs the updated imageUrl back.

Usage:
    python scripts/regenerate_coin_images.py

Requirements: pip install pillow cloudinary requests numpy
"""

import os, io, math, time, random, uuid
import requests
import cloudinary, cloudinary.uploader
from PIL import Image, ImageDraw, ImageFilter

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

# ── COIN VISUAL DEFINITIONS ───────────────────────────────────────────────────
# (value_float, display_label, outer_color, inner_color, text_color, edge_color)
COIN_STYLES = {
    "50p":  (0.50,  "50P",  (180,180,180), (210,210,210), (60,60,60),   (140,140,140)),
    "₹1":   (1.00,  "₹1",   (192,192,192), (220,220,220), (50,50,50),   (150,150,150)),
    "₹2":   (2.00,  "₹2",   (192,192,200), (215,215,225), (40,40,80),   (145,145,155)),
    "₹5":   (5.00,  "₹5",   (180,150,60),  (220,195,100), (80,50,10),   (140,110,30)),
    "₹10":  (10.0,  "₹10",  (180,150,60),  (210,190,90),  (70,45,5),    (135,105,25)),
}


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_realistic_coin(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int,
                        outer_col, inner_col, text_col, edge_col, label: str):
    """
    Draw a realistic metallic coin centred at (cx, cy) with radius r.
    Layers (back to front):
      1. Dark edge shadow
      2. Outer rim with radial gradient
      3. Inner field with highlight gradient
      4. Decorative inner ring
      5. Denomination text
    """
    # 1. Drop shadow (soft offset circle)
    shadow_offset = max(2, r // 12)
    for sh in range(4, 0, -1):
        alpha = 40 + sh * 10
        shc = (60, 60, 60)
        draw.ellipse(
            [cx - r + shadow_offset + sh, cy - r + shadow_offset + sh,
             cx + r + shadow_offset + sh, cy + r + shadow_offset + sh],
            fill=shc,
        )

    # 2. Edge / rim
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=edge_col)

    # 3. Outer face (slightly smaller)
    rim = max(3, r // 8)
    draw.ellipse([cx-r+rim, cy-r+rim, cx+r-rim, cy+r-rim], fill=outer_col)

    # 4. Highlight gradient simulation — paint concentric rings from dark→light
    inner_r = r - rim
    steps = max(10, inner_r)
    for i in range(steps, 0, -1):
        t = 1.0 - (i / steps)           # 0 at edge, 1 at centre
        # top-left highlight: blend toward a brighter shade
        highlight = lerp_color(outer_col, (255, 255, 255), 0.35 * t)
        draw.ellipse(
            [cx - i, cy - i, cx + i, cy + i],
            fill=highlight,
        )

    # 5. Inner decorative ring (thin groove)
    groove_r = int(r * 0.62)
    draw.ellipse(
        [cx - groove_r, cy - groove_r, cx + groove_r, cy + groove_r],
        outline=edge_col, width=max(1, r // 20),
    )

    # 6. Second inner highlight ring
    inner_field_r = int(r * 0.58)
    draw.ellipse(
        [cx - inner_field_r, cy - inner_field_r,
         cx + inner_field_r, cy + inner_field_r],
        fill=inner_col,
    )

    # 7. Small Ashoka-chakra-style dot ring
    num_dots = 12
    dot_ring_r = int(r * 0.42)
    dot_r = max(1, r // 18)
    for k in range(num_dots):
        angle = math.radians(k * 360 / num_dots)
        dx = int(cx + dot_ring_r * math.cos(angle))
        dy = int(cy + dot_ring_r * math.sin(angle))
        draw.ellipse([dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r], fill=edge_col)

    # 8. Denomination text centred
    # Estimate font size proportional to radius
    # Scale down font for longer labels (e.g. ₹10)
    font_size = max(10, int(r * 0.45 * (1.0 if len(label) <= 2 else 0.72)))
    # Try to load a font; fall back to default
    font = None
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                from PIL import ImageFont
                font = ImageFont.truetype(fp, font_size)
                break
            except Exception:
                pass

    if font is None:
        from PIL import ImageFont
        font = ImageFont.load_default()

    # Get text bounding box
    try:
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except AttributeError:
        tw, th = draw.textsize(label, font=font)

    tx = cx - tw // 2
    ty = cy - th // 2

    # Slight emboss: dark outline then lighter fill
    for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        draw.text((tx + ox, ty + oy), label, font=font, fill=edge_col)
    draw.text((tx, ty), label, font=font, fill=text_col)


def make_coin_image(coin_labels: list[str]) -> Image.Image:
    """
    Build a wide image with the given coins laid out horizontally.
    coin_labels: list of strings like ["₹1", "₹2", "₹5"]
    """
    n = len(coin_labels)
    coin_r = 70          # radius of each coin in pixels
    padding = 30
    img_w = n * (coin_r * 2 + padding) + padding
    img_h = coin_r * 2 + padding * 2 + 40  # extra for bottom label

    img = Image.new("RGB", (img_w, img_h), (245, 245, 245))
    draw = ImageDraw.Draw(img)

    # Subtle grid/linen background
    for y in range(0, img_h, 8):
        draw.line([(0, y), (img_w, y)], fill=(235, 235, 235), width=1)

    for i, lbl in enumerate(coin_labels):
        if lbl not in COIN_STYLES:
            continue
        _, display, outer, inner, text_c, edge = COIN_STYLES[lbl]
        cx = padding + coin_r + i * (coin_r * 2 + padding)
        cy = padding + coin_r
        draw_realistic_coin(draw, cx, cy, coin_r, outer, inner, text_c, edge, display)

    # Soft blur for anti-aliasing effect
    img = img.filter(ImageFilter.SMOOTH_MORE)
    return img


# ── API HELPERS ───────────────────────────────────────────────────────────────

def fetch_coin_questions() -> list[dict]:
    """Fetch all money/coin questions via admin search API."""
    all_items = []
    page = 1
    while True:
        url = f"{ADMIN_API_BASE}/api/admin/questions"
        params = {"topic": "Money", "subject": "Mathematics", "pageSize": 50, "page": page}
        r = requests.get(url, params=params, headers={"X-Admin-Key": ADMIN_API_KEY}, timeout=15)
        if r.status_code != 200:
            print(f"  [FAIL] GET questions page {page}: {r.status_code} {r.text[:200]}")
            break
        data = r.json()
        items = data.get("items", data.get("results", []))
        if not items:
            break
        all_items.extend(items)
        total = data.get("total", 0)
        if len(all_items) >= total:
            break
        page += 1
    return all_items


def upload_image(img: Image.Image) -> str | None:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    public_id = f"{CLOUDINARY_FOLDER}/coin-regen-{int(time.time())}-{random.randint(1000,9999)}"
    try:
        result = cloudinary.uploader.upload(
            buf.getvalue(), public_id=public_id, overwrite=False, resource_type="image"
        )
        return result["secure_url"]
    except Exception as e:
        print(f"  [FAIL] Cloudinary upload: {e}")
        return None


def update_question_image(q_id: str, q: dict, new_image_url: str) -> bool:
    url = f"{ADMIN_API_BASE}/api/admin/questions/{q_id}"
    payload = {
        "subject":       q["subject"],
        "grade":         q["grade"],
        "topic":         q["topic"],
        "subTopic":      q.get("subTopic", "Indian Currency"),
        "difficulty":    q.get("difficulty", "Foundation"),
        "questionText":  q["questionText"],
        "imageUrl":      new_image_url,
        "options":       q["options"],
        "correctAnswer": q["correctAnswer"],
        "explanation":   q.get("explanation", ""),
    }
    try:
        r = requests.put(url, json=payload, headers={"X-Admin-Key": ADMIN_API_KEY}, timeout=15)
        return r.status_code in (200, 204)
    except Exception as e:
        print(f"  [FAIL] PUT {q_id}: {e}")
        return False


# ── COIN LABEL EXTRACTION ─────────────────────────────────────────────────────

def extract_coins_from_explanation(explanation: str) -> list[str] | None:
    """
    Explanation format: "Sum of coins: ₹1 + ₹2 + ₹5 = Rs. 8"
    Extract the coins list.
    """
    if not explanation:
        return None
    import re
    m = re.search(r"Sum of coins:\s*(.+?)\s*=", explanation)
    if not m:
        return None
    raw = m.group(1)
    tokens = [t.strip() for t in raw.split("+")]
    valid = [t for t in tokens if t in COIN_STYLES]
    return valid if valid else None


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("Fetching coin questions from admin API...")
    questions = fetch_coin_questions()
    print(f"Found {len(questions)} money questions.")

    # Filter only the coin-image questions (those with imageUrl set)
    coin_qs = [q for q in questions if q.get("imageUrl")]
    print(f"  {len(coin_qs)} have existing images (will regenerate).")
    if not coin_qs:
        print("No coin image questions found. Run generate_lr_math_science.py first.")
        return

    ok = 0
    fail = 0
    for q in coin_qs:
        q_id = q.get("questionBankId") or q.get("QuestionBankId")
        explanation = q.get("explanation", "")
        coins = extract_coins_from_explanation(explanation)

        if not coins:
            print(f"  [SKIP] {q_id} — can't parse coins from explanation: {explanation[:80]}")
            fail += 1
            continue

        coins_safe = [c.replace("₹", "Rs.") for c in coins]
        print(f"  Regenerating {q_id}  coins={coins_safe}...", end=" ", flush=True)
        img = make_coin_image(coins)
        url = upload_image(img)
        if not url:
            fail += 1
            continue

        success = update_question_image(q_id, q, url)
        if success:
            print(f"[OK] -> {url}")
            ok += 1
        else:
            print("[FAIL] update returned error")
            fail += 1

        time.sleep(0.3)   # gentle rate limiting

    print(f"\n[DONE] {ok} updated, {fail} failed.")


if __name__ == "__main__":
    main()
