"""
regenerate_clock_images.py
For every analog-clock question that has an image:
  1. Parse the correct time from the question's correctAnswer + options
  2. Draw a high-quality realistic clock image
  3. Upload to Cloudinary
  4. PUT the updated imageUrl (and cleaned questionText) back via admin API

Also strips "(Clock N)" / "(Set N)" suffixes from questionText.

Usage:
    python scripts/regenerate_clock_images.py
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


# ── QUESTION TEXT CLEANER ─────────────────────────────────────────────────────

def clean_question_text(text: str) -> str:
    """Remove trailing (Clock N), (Set N), (Set N) style suffixes."""
    text = re.sub(r'\s*\(\s*Clock\s+\d+\s*\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*\(\s*Set\s+\d+\s*\)',   '', text, flags=re.IGNORECASE)
    return text.strip()


# ── REALISTIC CLOCK RENDERER ──────────────────────────────────────────────────

def load_font(size: int, bold: bool = False):
    paths_bold = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    paths_reg = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in (paths_bold if bold else paths_reg):
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def lerp(a, b, t):
    return a + (b - a) * t


def draw_realistic_clock(hour: int, minute: int, size: int = 400) -> Image.Image:
    """
    Draw a photo-realistic analog clock face.
    Layers:
      1. Bezel (dark metallic ring)
      2. Cream/white dial with subtle radial gradient
      3. Hour tick marks (long, wide) + minute tick marks (short, thin)
      4. Hour numerals (bold)
      5. Hour hand (thick tapered polygon)
      6. Minute hand (thinner tapered polygon)
      7. Second hand stub (thin red line — decorative, at 12)
      8. Centre cap (layered circles)
    """
    # Work at 2x for anti-aliasing, then downscale
    scale = 2
    S = size * scale
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx = cy = S // 2

    # ── 1. Outer bezel ────────────────────────────────────────────────────────
    bezel_r = S // 2 - 4
    # Shadow ring
    draw.ellipse([cx-bezel_r-4, cy-bezel_r-4, cx+bezel_r+4, cy+bezel_r+4],
                 fill=(40, 40, 40, 180))
    # Dark metallic bezel
    draw.ellipse([cx-bezel_r, cy-bezel_r, cx+bezel_r, cy+bezel_r],
                 fill=(55, 55, 60))
    # Inner bezel highlight ring
    bezel_inner = bezel_r - 14
    draw.ellipse([cx-bezel_inner, cy-bezel_inner, cx+bezel_inner, cy+bezel_inner],
                 fill=(230, 220, 200))   # cream dial colour

    # ── 2. Dial radial gradient (cream centre, slightly darker edge) ──────────
    dial_r = bezel_inner - 2
    steps = dial_r
    for i in range(steps, 0, -1):
        t = i / steps   # 1 at edge, 0 at centre
        r_c = int(lerp(252, 240, t))
        g_c = int(lerp(250, 235, t))
        b_c = int(lerp(240, 215, t))
        draw.ellipse([cx-i, cy-i, cx+i, cy+i], fill=(r_c, g_c, b_c))

    # ── 3. Tick marks ─────────────────────────────────────────────────────────
    tick_outer = dial_r - 4
    for i in range(60):
        ang = math.radians(i * 6 - 90)
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        if i % 5 == 0:
            # Hour tick — long and thick
            t_in  = tick_outer - 26
            t_out = tick_outer
            width = 6
            color = (30, 30, 30)
        else:
            # Minute tick — short and thin
            t_in  = tick_outer - 12
            t_out = tick_outer
            width = 3
            color = (120, 120, 120)
        x1 = cx + int(t_in  * cos_a)
        y1 = cy + int(t_in  * sin_a)
        x2 = cx + int(t_out * cos_a)
        y2 = cy + int(t_out * sin_a)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=width)

    # ── 4. Hour numerals ──────────────────────────────────────────────────────
    num_r   = tick_outer - 46
    num_fnt = load_font(int(S * 0.095), bold=True)
    for i in range(1, 13):
        ang = math.radians(i * 30 - 90)
        nx = cx + int(num_r * math.cos(ang))
        ny = cy + int(num_r * math.sin(ang))
        label = str(i)
        try:
            bb = draw.textbbox((0, 0), label, font=num_fnt)
            tw, th = bb[2]-bb[0], bb[3]-bb[1]
        except AttributeError:
            tw, th = draw.textsize(label, font=num_fnt)
        draw.text((nx - tw//2, ny - th//2), label, font=num_fnt, fill=(20, 20, 20))

    # ── 5. Helper: tapered hand polygon ───────────────────────────────────────
    def hand_polygon(cx, cy, angle_deg, length, base_w, tip_w=2):
        """Return polygon points for a tapered clock hand."""
        ang  = math.radians(angle_deg - 90)
        perp = math.radians(angle_deg - 90 + 90)
        # Tip point
        tx = cx + length * math.cos(ang)
        ty = cy + length * math.sin(ang)
        # Base points (wide end)
        bx1 = cx + base_w * math.cos(perp)
        by1 = cy + base_w * math.sin(perp)
        bx2 = cx - base_w * math.cos(perp)
        by2 = cy - base_w * math.sin(perp)
        # Near-tip points
        mx  = cx + (length - tip_w*4) * math.cos(ang)
        my  = cy + (length - tip_w*4) * math.sin(ang)
        tx1 = mx + tip_w * math.cos(perp)
        ty1 = my + tip_w * math.sin(perp)
        tx2 = mx - tip_w * math.cos(perp)
        ty2 = my - tip_w * math.sin(perp)
        return [(bx1,by1),(tx1,ty1),(tx,ty),(tx2,ty2),(bx2,by2)]

    # ── 6. Hour hand ──────────────────────────────────────────────────────────
    h_angle = (hour % 12 + minute / 60) * 30
    h_len   = dial_r * 0.52
    h_pts   = hand_polygon(cx, cy, h_angle, h_len, base_w=14, tip_w=4)
    # Shadow
    shadow_pts = [(x+5, y+5) for x, y in h_pts]
    draw.polygon(shadow_pts, fill=(0, 0, 0, 80))
    draw.polygon(h_pts, fill=(25, 25, 25))
    draw.polygon(h_pts, outline=(60, 60, 60), width=2)

    # ── 7. Minute hand ────────────────────────────────────────────────────────
    m_angle = minute * 6
    m_len   = dial_r * 0.74
    m_pts   = hand_polygon(cx, cy, m_angle, m_len, base_w=9, tip_w=2)
    shadow_m = [(x+4, y+4) for x, y in m_pts]
    draw.polygon(shadow_m, fill=(0, 0, 0, 60))
    draw.polygon(m_pts, fill=(30, 30, 30))
    draw.polygon(m_pts, outline=(80, 80, 80), width=2)

    # ── 8. Decorative seconds stub (red, always at 12 position) ──────────────
    sec_ang = math.radians(-90)
    sx = cx + int(dial_r * 0.35 * math.cos(sec_ang))
    sy = cy + int(dial_r * 0.35 * math.sin(sec_ang))
    draw.line([(cx, cy), (sx, sy)], fill=(200, 30, 30), width=4)

    # ── 9. Centre cap ─────────────────────────────────────────────────────────
    for cap_r, cap_col in [(22, (40,40,40)), (16, (80,80,80)), (10, (200,200,200)), (5, (255,255,255))]:
        draw.ellipse([cx-cap_r, cy-cap_r, cx+cap_r, cy+cap_r], fill=cap_col)

    # ── Downscale 2x → 1x for smooth anti-aliasing ───────────────────────────
    img = img.resize((size, size), Image.LANCZOS)

    # Convert RGBA → RGB on white background
    bg = Image.new("RGB", (size, size), (255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    return bg


# ── TIME PARSING ──────────────────────────────────────────────────────────────

def parse_time(time_str: str):
    """Parse 'H:MM' or 'HH:MM' into (hour, minute)."""
    m = re.match(r'^(\d{1,2}):(\d{2})$', time_str.strip())
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def get_correct_time(q: dict):
    """Extract (hour, minute) from the question's correct answer option."""
    correct_letter = q.get("correctAnswer", "A")
    options = q.get("options", [])
    idx = ord(correct_letter.upper()) - ord('A')
    if 0 <= idx < len(options):
        return parse_time(options[idx])
    return None


# ── API HELPERS ───────────────────────────────────────────────────────────────

def fetch_all_time_questions() -> list[dict]:
    all_items = []
    page = 1
    while True:
        r = requests.get(f"{ADMIN_API_BASE}/api/admin/questions",
            params={"topic": "Time", "pageSize": 100, "page": page},
            headers={"X-Admin-Key": ADMIN_API_KEY}, timeout=15)
        if r.status_code != 200:
            print(f"  [FAIL] GET page {page}: {r.status_code}")
            break
        data = r.json()
        items = data.get("items", data.get("results", []))
        if not items:
            break
        all_items.extend(items)
        if len(all_items) >= data.get("total", 0):
            break
        page += 1
    return all_items


def upload_image(img: Image.Image) -> str | None:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    public_id = f"{CLOUDINARY_FOLDER}/clock-regen-{int(time.time())}-{random.randint(1000,9999)}"
    try:
        result = cloudinary.uploader.upload(
            buf.getvalue(), public_id=public_id, overwrite=False, resource_type="image"
        )
        return result["secure_url"]
    except Exception as e:
        print(f"  [FAIL] Cloudinary: {e}")
        return None


def update_question(q_id: str, q: dict, new_image_url: str, new_text: str) -> bool:
    url = f"{ADMIN_API_BASE}/api/admin/questions/{q_id}"
    payload = {
        "subject":       q["subject"],
        "grade":         q["grade"],
        "topic":         q["topic"],
        "subTopic":      q.get("subTopic", "Analog Clock Reading"),
        "difficulty":    q.get("difficulty", "Foundation"),
        "questionText":  new_text,
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


def update_question_text_only(q_id: str, q: dict, new_text: str) -> bool:
    """Update only questionText (keep existing imageUrl)."""
    return update_question(q_id, q, q.get("imageUrl", ""), new_text)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("Fetching all Time questions...")
    questions = fetch_all_time_questions()
    print(f"  Total: {len(questions)}")

    # Split into two jobs:
    # A) Analog clock image questions (have imageUrl + parseable correct time)
    # B) Questions with (Clock N)/(Set N) text but maybe no image to redo

    clock_img_qs   = []   # need new image + text fix
    text_only_qs   = []   # only need text fix (no image or not a clock-image question)

    for q in questions:
        raw_text    = q.get("questionText", "")
        clean_text  = clean_question_text(raw_text)
        needs_clean = (clean_text != raw_text)
        has_image   = bool(q.get("imageUrl"))
        time_val    = get_correct_time(q) if has_image else None
        is_clock_img = has_image and time_val is not None and (
            "clock" in raw_text.lower() or "analog" in raw_text.lower()
            or "hands" in raw_text.lower() or "time" in raw_text.lower()
        )

        if is_clock_img:
            clock_img_qs.append((q, clean_text, time_val))
        elif needs_clean:
            text_only_qs.append((q, clean_text))

    print(f"  Analog clock image questions to regenerate: {len(clock_img_qs)}")
    print(f"  Text-only cleanup (no image redo): {len(text_only_qs)}")

    ok = fail = 0

    # Job A: regenerate image + fix text
    print("\n--- Regenerating clock images ---")
    for q, clean_text, (hour, minute) in clock_img_qs:
        q_id = q.get("questionBankId") or q.get("QuestionBankId")
        print(f"  {q_id}  {hour}:{minute:02d}  \"{clean_text[:55]}\"...", end=" ", flush=True)
        img  = draw_realistic_clock(hour, minute, size=400)
        url  = upload_image(img)
        if not url:
            print("[FAIL] upload")
            fail += 1
            continue
        success = update_question(q_id, q, url, clean_text)
        if success:
            print("[OK]")
            ok += 1
        else:
            print("[FAIL] PUT")
            fail += 1
        time.sleep(0.3)

    # Job B: text-only fixes
    print("\n--- Text-only cleanup ---")
    for q, clean_text in text_only_qs:
        q_id = q.get("questionBankId") or q.get("QuestionBankId")
        print(f"  {q_id}  \"{clean_text[:55]}\"...", end=" ", flush=True)
        success = update_question_text_only(q_id, q, clean_text)
        if success:
            print("[OK]")
            ok += 1
        else:
            print("[FAIL]")
            fail += 1
        time.sleep(0.2)

    print(f"\n[DONE] {ok} updated, {fail} failed.")


if __name__ == "__main__":
    main()
