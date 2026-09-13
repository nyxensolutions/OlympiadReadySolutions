"""
August 2026 Olympiad Season Promo Email
Usage:
  python send_promo_email.py --test           # send to akhil.mittal20@gmail.com only
  python send_promo_email.py --all            # send to all free users (run --test first!)

Set BREVO_API_KEY env variable before running.
"""
import sys
import os
import json
import urllib.request
import urllib.error
import argparse

sys.stdout.reconfigure(encoding="utf-8")

BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
SENDER_EMAIL  = "no-reply@olympiadready.com"
SENDER_NAME   = "OlympiadReady"
TEST_EMAIL    = "akhil.mittal20@gmail.com"
TEST_NAME     = "Akhil"

DB_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "Server=tcp:nyxen.database.windows.net,1433;"
    "Database=OlympiadReadyProd;"
    "Uid=nyxen-admin;"
    "Pwd=Tnab5@AFxKhL3DA;"
    "TrustServerCertificate=yes;"
)


def build_html(first_name: str) -> str:
    return f"""
<div style="font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;max-width:600px;margin:0 auto;color:#333;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;background:#ffffff;">

  <!-- Header -->
  <div style="background:#1e3a8a;padding:40px 20px 30px;text-align:center;">
    <img src="https://pub-10c8d4fc83f3441291d56f22a87f0da6.r2.dev/olympiadready/Logo_white.png"
         alt="OlympiadReady" style="height:52px;max-width:100%;display:block;margin:0 auto;" />
    <h1 style="color:#ffffff;margin:20px 0 0;font-size:24px;font-weight:700;">🎉 August Olympiad Season Offer</h1>
  </div>

  <!-- Body -->
  <div style="padding:36px 32px;">
    <p style="font-size:16px;margin-top:0;">Hi <strong>{first_name}</strong>,</p>

    <p style="font-size:15px;color:#475569;line-height:1.6;">
      Olympiad exams are coming up in October — and this August we&rsquo;re giving you <strong>40% off</strong>
      on all subscriptions and PDF downloads so you can prepare without breaking the bank.
    </p>

    <!-- Offer highlight box -->
    <div style="background:#fff7ed;border:2px solid #fb923c;border-radius:12px;padding:24px;margin:28px 0;text-align:center;">
      <p style="margin:0 0 4px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#c2410c;">
        August 2026 Limited Offer
      </p>
      <p style="margin:0 0 16px;font-size:28px;font-weight:800;color:#1e3a8a;">
        <span style="text-decoration:line-through;color:#94a3b8;font-size:18px;">&#x20B9;129</span>
        &nbsp;&#x20B9;77
        <span style="font-size:16px;font-weight:500;color:#64748b;"> / subject / month</span>
      </p>
      <p style="margin:0;font-size:13px;color:#92400e;">
        PDF downloads from <span style="text-decoration:line-through;">&#x20B9;29</span> <strong>&#x20B9;19</strong> &nbsp;|&nbsp;
        Champion plan from <span style="text-decoration:line-through;">&#x20B9;649</span> <strong>&#x20B9;389</strong>/month
      </p>
    </div>

    <!-- Features -->
    <p style="font-size:15px;color:#475569;line-height:1.6;margin-bottom:8px;">
      Here&rsquo;s what you unlock when you upgrade:
    </p>
    <div style="margin:0 0 24px;">
      <div style="display:flex;align-items:flex-start;margin-bottom:14px;">
        <span style="font-size:20px;margin-right:12px;">📄</span>
        <div>
          <strong style="color:#1e293b;">Unlimited AI Practice Papers</strong>
          <p style="margin:3px 0 0;font-size:14px;color:#64748b;">SOF-aligned questions for IMO, NSO, IEO, IGKO &amp; Spell Bee — any grade.</p>
        </div>
      </div>
      <div style="display:flex;align-items:flex-start;margin-bottom:14px;">
        <span style="font-size:20px;margin-right:12px;">🤖</span>
        <div>
          <strong style="color:#1e293b;">AI Explains Every Answer</strong>
          <p style="margin:3px 0 0;font-size:14px;color:#64748b;">Instant step-by-step explanations after every question.</p>
        </div>
      </div>
      <div style="display:flex;align-items:flex-start;margin-bottom:14px;">
        <span style="font-size:20px;margin-right:12px;">📈</span>
        <div>
          <strong style="color:#1e293b;">Progress Tracking</strong>
          <p style="margin:3px 0 0;font-size:14px;color:#64748b;">See weak topics at a glance and focus your prep where it matters.</p>
        </div>
      </div>
      <div style="display:flex;align-items:flex-start;">
        <span style="font-size:20px;margin-right:12px;">🏅</span>
        <div>
          <strong style="color:#1e293b;">Level 1 &amp; Level 2 Ready</strong>
          <p style="margin:3px 0 0;font-size:14px;color:#64748b;">Practice papers calibrated to both SOF exam rounds.</p>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div style="text-align:center;margin:32px 0;">
      <a href="https://olympiadready.com/dashboard"
         style="background:#1e3a8a;color:#fff;padding:16px 36px;text-decoration:none;border-radius:10px;font-weight:700;font-size:16px;display:inline-block;">
        Unlock August Offer &rarr;
      </a>
      <p style="margin:12px 0 0;font-size:12px;color:#94a3b8;">Offer valid through 31 August 2026 only.</p>
    </div>

    <!-- Urgency note -->
    <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:16px 20px;">
      <p style="margin:0;font-size:14px;color:#1e40af;">
        ⏰ <strong>Hurry</strong> — prices go back up on 1 September. Olympiad exams start in October,
        so the next 4–6 weeks of focused practice can make all the difference.
      </p>
    </div>
  </div>

  <!-- Footer -->
  <div style="background:#f1f5f9;padding:20px;text-align:center;border-top:1px solid #e2e8f0;">
    <p style="margin:0;font-size:12px;color:#64748b;">© 2026 OlympiadReady. All rights reserved.</p>
    <p style="margin:6px 0 0;font-size:12px;color:#94a3b8;">
      Questions? Reply to this email — we read every one.
    </p>
    <p style="margin:6px 0 0;font-size:11px;color:#cbd5e1;">
      You&rsquo;re receiving this because you signed up at olympiadready.com.
      <a href="https://olympiadready.com" style="color:#94a3b8;">Unsubscribe</a>
    </p>
  </div>
</div>
"""


def send_email(to_email: str, to_name: str) -> bool:
    if not BREVO_API_KEY:
        print("ERROR: BREVO_API_KEY env variable not set.")
        return False

    first_name = to_name.split()[0] if to_name else "there"
    payload = {
        "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
        "to": [{"email": to_email, "name": to_name}],
        "subject": "🎉 August Offer: 40% off OlympiadReady — Olympiad season starts soon!",
        "htmlContent": build_html(first_name),
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=data,
        headers={
            "Content-Type": "application/json",
            "api-key": BREVO_API_KEY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  ✓  {to_email}  →  {resp.status}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ✗  {to_email}  →  HTTP {e.code}: {body}")
        return False


def get_free_users():
    try:
        import pyodbc
    except ImportError:
        print("pyodbc not installed. Run: pip install pyodbc")
        sys.exit(1)

    conn = pyodbc.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT u.Email, u.FullName
        FROM   Users u
        WHERE  u.SubscriptionTier = 'Free'
          AND  u.Email IS NOT NULL
          AND  u.Email <> ''
          AND  (u.EmailOptOut IS NULL OR u.EmailOptOut = 0)
        ORDER  BY u.CreatedAt DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [(r.Email, r.FullName or "there") for r in rows]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Send to test email only")
    parser.add_argument("--all",  action="store_true", help="Send to all free users")
    args = parser.parse_args()

    if not args.test and not args.all:
        parser.print_help()
        sys.exit(1)

    if args.test:
        print(f"Sending test email to {TEST_EMAIL} ...")
        send_email(TEST_EMAIL, TEST_NAME)
        return

    print("Fetching free users from database ...")
    users = get_free_users()
    print(f"Found {len(users)} free users. Sending emails ...")
    ok = fail = 0
    for email, name in users:
        if send_email(email, name):
            ok += 1
        else:
            fail += 1
    print(f"\nDone. {ok} sent, {fail} failed.")


if __name__ == "__main__":
    main()
