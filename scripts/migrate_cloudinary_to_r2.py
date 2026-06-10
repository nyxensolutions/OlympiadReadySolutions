"""
One-time migration: download images from Cloudinary, upload to Cloudflare R2,
update ALL columns in QuestionBank that may contain Cloudinary URLs:

  - ImageUrl          (dedicated image column)
  - OptionsJson       (JSON array — image-options mode stores 4 image URLs here)
  - QuestionText      (may have embedded bare or markdown Cloudinary URLs)
  - Explanation       (may have embedded bare or markdown Cloudinary URLs)

Prerequisites:
    pip install boto3 requests pyodbc python-dotenv
"""

import os, re, uuid, json, mimetypes, time

import boto3
import pyodbc
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
DB_CONN        = os.environ["DB_CONN"]
R2_ACCOUNT_ID  = os.environ["R2_ACCOUNT_ID"]
R2_ACCESS_KEY  = os.environ["R2_ACCESS_KEY"]
R2_SECRET_KEY  = os.environ["R2_SECRET_KEY"]
R2_BUCKET      = os.environ.get("R2_BUCKET", "olympiadready-questions")
R2_PUBLIC_BASE = os.environ["R2_PUBLIC_BASE"].rstrip("/")
DRY_RUN        = os.environ.get("DRY_RUN", "false").lower() == "true"
# ───────────────────────────────────────────────────────────────────────────────

CLOUDINARY_RE = re.compile(r'https?://res\.cloudinary\.com/[^\s\)\]"\']+')

s3 = boto3.client(
    "s3",
    endpoint_url          = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id     = R2_ACCESS_KEY,
    aws_secret_access_key = R2_SECRET_KEY,
    region_name           = "auto",
)

# Cache: cloudinary_url -> r2_url  (avoids re-uploading the same image twice)
_url_cache: dict[str, str] = {}


def upload_to_r2(image_bytes: bytes, ext: str, content_type: str) -> str:
    key = f"questions/{uuid.uuid4()}{ext}"
    s3.put_object(
        Bucket       = R2_BUCKET,
        Key          = key,
        Body         = image_bytes,
        ContentType  = content_type,
        CacheControl = "public, max-age=31536000, immutable",
    )
    return f"{R2_PUBLIC_BASE}/{key}"


def migrate_url(old_url: str) -> str:
    """Download from Cloudinary, upload to R2, return new URL. Uses cache."""
    if old_url in _url_cache:
        return _url_cache[old_url]

    resp = requests.get(old_url, timeout=30)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
    ext = mimetypes.guess_extension(content_type) or ".jpg"
    if ext == ".jpe":
        ext = ".jpg"

    if DRY_RUN:
        fake = f"{R2_PUBLIC_BASE}/questions/DRY-RUN{ext}"
        _url_cache[old_url] = fake
        return fake

    new_url = upload_to_r2(resp.content, ext, content_type)
    _url_cache[old_url] = new_url
    return new_url


def replace_urls_in_text(text: str) -> tuple[str, list[str]]:
    """Replace all Cloudinary URLs inside a text string. Returns (new_text, [replaced urls])."""
    replaced = []
    def replacer(m):
        old = m.group(0)
        new = migrate_url(old)
        if new != old:
            replaced.append(old)
        return new
    new_text = CLOUDINARY_RE.sub(replacer, text)
    return new_text, replaced


def fetch_all_rows(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT QuestionBankId, ImageUrl, OptionsJson, QuestionText, Explanation
        FROM QuestionBank
        WHERE
            (ImageUrl      IS NOT NULL AND ImageUrl      LIKE '%cloudinary.com%')
         OR (OptionsJson   IS NOT NULL AND OptionsJson   LIKE '%cloudinary.com%')
         OR (QuestionText  IS NOT NULL AND QuestionText  LIKE '%cloudinary.com%')
         OR (Explanation   IS NOT NULL AND Explanation   LIKE '%cloudinary.com%')
    """)
    return cur.fetchall()


def update_row(conn, row_id, image_url, options_json, question_text, explanation):
    cur = conn.cursor()
    cur.execute("""
        UPDATE QuestionBank
        SET ImageUrl     = ?,
            OptionsJson  = ?,
            QuestionText = ?,
            Explanation  = ?
        WHERE QuestionBankId = ?
    """, (image_url, options_json, question_text, explanation, row_id))
    conn.commit()


def migrate():
    conn = pyodbc.connect(DB_CONN)
    rows = fetch_all_rows(conn)
    print(f"Found {len(rows)} rows with Cloudinary URLs across all columns.\n")

    total_urls = 0
    success_rows, failed_rows = 0, []

    for i, row in enumerate(rows, 1):
        row_id, image_url, options_json, question_text, explanation = row
        print(f"[{i}/{len(rows)}] Row {row_id}")

        try:
            changed = False

            # ── 1. ImageUrl ───────────────────────────────────────────────────
            new_image_url = image_url
            if image_url and "cloudinary.com" in image_url:
                new_image_url = migrate_url(image_url)
                print(f"  ImageUrl      → {new_image_url}")
                total_urls += 1
                changed = True

            # ── 2. OptionsJson (JSON array of strings) ────────────────────────
            new_options_json = options_json
            if options_json and "cloudinary.com" in options_json:
                options = json.loads(options_json)
                new_options = []
                for opt in options:
                    if opt and "cloudinary.com" in opt:
                        new_opt = migrate_url(opt)
                        print(f"  Option        → {new_opt}")
                        total_urls += 1
                        new_options.append(new_opt)
                    else:
                        new_options.append(opt)
                new_options_json = json.dumps(new_options, ensure_ascii=False)
                changed = True

            # ── 3. QuestionText ───────────────────────────────────────────────
            new_question_text = question_text
            if question_text and "cloudinary.com" in question_text:
                new_question_text, replaced = replace_urls_in_text(question_text)
                for u in replaced:
                    print(f"  QuestionText  → replaced {u[:60]}...")
                total_urls += len(replaced)
                changed = True

            # ── 4. Explanation ────────────────────────────────────────────────
            new_explanation = explanation
            if explanation and "cloudinary.com" in explanation:
                new_explanation, replaced = replace_urls_in_text(explanation)
                for u in replaced:
                    print(f"  Explanation   → replaced {u[:60]}...")
                total_urls += len(replaced)
                changed = True

            if changed and not DRY_RUN:
                update_row(conn, row_id, new_image_url, new_options_json, new_question_text, new_explanation)
                print(f"  ✓ DB updated")
            elif changed and DRY_RUN:
                print(f"  DRY RUN — would update DB row")

            success_rows += 1

        except Exception as e:
            print(f"  FAILED: {e}")
            failed_rows.append((str(row_id), str(e)))

        time.sleep(0.1)

    conn.close()
    print(f"\n{'='*60}")
    print(f"Rows processed : {success_rows}")
    print(f"URLs migrated  : {total_urls}")
    print(f"Rows failed    : {len(failed_rows)}")
    if failed_rows:
        print("\nFailed rows:")
        for rid, err in failed_rows:
            print(f"  {rid} → {err}")


if __name__ == "__main__":
    mode = "DRY RUN" if DRY_RUN else "LIVE"
    print(f"{'='*60}")
    print(f"  Cloudinary → R2 Migration  [{mode}]")
    print(f"  R2 Bucket : {R2_BUCKET}")
    print(f"  Public URL: {R2_PUBLIC_BASE}")
    print(f"{'='*60}\n")
    migrate()
