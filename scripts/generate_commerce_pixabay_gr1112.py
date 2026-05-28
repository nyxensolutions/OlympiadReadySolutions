"""
generate_commerce_pixabay_gr1112.py
High-quality Pixabay images -> Commerce Grade 11 and Grade 12 (Olympiad difficulty).
Covers: Accountancy, Business Studies, Economics topics.

QUALITY RULES:
  1. Pixabay query is EXACTLY what must be visible in the photo.
  2. Question references a specific visible feature of the image.
  3. No question asks about something the image cannot show.
  4. Each question is self-contained even without the image.
"""

import os, io, time, random, requests
import cloudinary, cloudinary.uploader

PIXABAY_API_KEY       = os.environ.get("PIXABAY_API_KEY",       "56031484-1cf6e0a588c13eebd71681fda")
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE",
    "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY", "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME, api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET, secure=True)
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}
RUN_ID  = int(time.time())

posted = skipped = failed = 0

_dl = requests.Session()
_dl.headers.update({"User-Agent": "Mozilla/5.0 (compatible; OlympiadReady/1.0)"})


def pixabay_fetch(query, idx=0):
    params = {"key": PIXABAY_API_KEY, "q": query, "image_type": "photo",
              "orientation": "horizontal", "safesearch": "true",
              "per_page": 10, "order": "popular"}
    try:
        r = requests.get("https://pixabay.com/api/", params=params, timeout=12)
        r.raise_for_status()
        hits = r.json().get("hits", [])
    except Exception as e:
        print(f"    [PIXABAY ERR] '{query}': {e}"); return None
    if not hits:
        print(f"    [NO HITS] '{query}'"); return None
    for hi in range(min(len(hits), 5)):
        hit = hits[(idx + hi) % len(hits)]
        img_url = hit.get("previewURL") or hit.get("webformatURL")
        if not img_url: continue
        try:
            time.sleep(1.5)
            dl = _dl.get(img_url, timeout=20); dl.raise_for_status()
        except Exception as e:
            print(f"    [DL ERR] '{query}' hit {hi}: {e}"); continue
        pub_id = f"{CLOUDINARY_FOLDER}/com_{query[:26].replace(' ','-')}_{RUN_ID}_{hit['id']}"
        try:
            time.sleep(1.0)
            res = cloudinary.uploader.upload(io.BytesIO(dl.content), public_id=pub_id,
                                             overwrite=False, resource_type="image")
            return res["secure_url"]
        except Exception as e:
            print(f"    [CDN ERR] '{query}' hit {hi}: {e}"); continue
    return None


def post_q(subject, grade, difficulty, topic, subtopic, text, opts, correct_idx, expl, img_url):
    global posted, skipped, failed
    payload = {
        "subject": subject, "grade": grade, "difficulty": difficulty,
        "topic": topic, "subTopic": subtopic,
        "questionText": text, "imageUrl": img_url,
        "options": opts, "correctAnswer": ["A","B","C","D"][correct_idx],
        "explanation": expl
    }
    try:
        r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                          json=payload, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            posted += 1; return True
        elif r.status_code == 409:
            skipped += 1; return False
        else:
            print(f"    [FAIL {r.status_code}] {text[:60]}"); failed += 1; return False
    except Exception as e:
        print(f"    [ERR] {e}"); failed += 1; return False


def add_img(subject, grade, topic, subtopic, query, text, correct, wrongs, expl, pix_idx=0, difficulty="Olympiad"):
    tag = f"G{grade} {subject[:4]} {query[:28]}..."
    img_url = pixabay_fetch(query, pix_idx)
    if not img_url:
        print(f"    [SKIP no img] {tag}"); return
    opts = [correct] + wrongs[:3]
    random.shuffle(opts)
    cidx = opts.index(correct)
    ok = post_q(subject, grade, difficulty, topic, subtopic, text, opts, cidx, expl, img_url)
    status = "ok" if ok else "dup/fail"
    print(f"  {tag} -> {status}")


# ===========================================================================
#  COMMERCE GRADE 11
# ===========================================================================

def gen_gr11_commerce():
    print("\n" + "="*60)
    print("  Commerce Grade 11")
    print("="*60)
    S, G = "Commerce", 11

    # 1. Accountancy — Accounting equation (Balance Sheet layout)
    add_img(S, G, "Financial Accounting", "Accounting Equation",
        query="balance sheet financial statement accounting",
        text="A balance sheet shows: Total Assets = ₹5,00,000; Total Liabilities = ₹1,80,000. Using the accounting equation (Assets = Liabilities + Capital), what is the owner's capital?",
        correct="₹3,20,000",
        wrongs=["₹6,80,000", "₹1,80,000", "₹5,00,000"],
        expl="Accounting equation: Capital = Assets − Liabilities = 5,00,000 − 1,80,000 = ₹3,20,000.")

    # 2. Business Studies — Factory / manufacturing (Forms of Business)
    add_img(S, G, "Forms of Business Organisation", "Joint Stock Company",
        query="factory manufacturing production plant",
        text="A large factory shown employs thousands of workers and is owned by a Joint Stock Company. Which feature of a Joint Stock Company BEST explains how it can raise such large-scale capital?",
        correct="Issue of shares to the public",
        wrongs=["Unlimited liability of owners", "Ownership restricted to 20 members", "Managed exclusively by government"],
        expl="A Joint Stock Company can raise vast capital by issuing shares to the public. Shareholders' liability is limited to the face value of shares held.")

    # 3. Economics — Market / supermarket (Demand and Supply)
    add_img(S, G, "Theory of Demand", "Law of Demand",
        query="supermarket shelves products shopping",
        text="Prices of goods in a supermarket rise sharply. According to the Law of Demand, what happens to quantity demanded, assuming all other factors remain constant?",
        correct="Quantity demanded falls",
        wrongs=["Quantity demanded rises", "Quantity demanded remains unchanged", "Demand curve shifts rightward"],
        expl="The Law of Demand states an inverse relationship between price and quantity demanded (ceteris paribus). A rise in price causes a fall in quantity demanded — a movement along the demand curve, not a shift.")

    # 4. Accountancy — Journal entry / ledger book
    add_img(S, G, "Financial Accounting", "Journal and Ledger",
        query="accounting journal ledger book entries",
        text="A journal entry reads: Purchases A/c Dr. ₹40,000 / To Cash A/c ₹40,000. This records which type of transaction?",
        correct="Cash purchase of goods",
        wrongs=["Credit purchase of goods", "Cash sale of goods", "Return of goods to supplier"],
        expl="Debit Purchases and Credit Cash indicates goods were bought and paid for immediately in cash. A credit purchase would credit 'Creditors/Accounts Payable' instead.")

    # 5. Business Studies — Bank building (Banking and Finance)
    add_img(S, G, "Sources of Business Finance", "Commercial Banks",
        query="bank building entrance facade",
        text="The bank shown offers a working capital loan at 12% p.a. to a firm for 6 months on ₹2,00,000. What is the interest payable?",
        correct="₹12,000",
        wrongs=["₹24,000", "₹6,000", "₹14,400"],
        expl="Simple Interest = P × R × T / 100 = 2,00,000 × 12 × (6/12) / 100 = 2,00,000 × 0.06 = ₹12,000.")

    # 6. Economics — Stock market graph / trading screen
    add_img(S, G, "Theory of Supply", "Price Elasticity of Supply",
        query="stock market trading screen graph",
        text="A supply graph shows that when price rises from ₹50 to ₹60 (20% rise), quantity supplied increases from 200 to 260 units (30% rise). What is the price elasticity of supply?",
        correct="1.5 (elastic supply)",
        wrongs=["0.67 (inelastic supply)", "1.0 (unit elastic)", "0 (perfectly inelastic)"],
        expl="PES = % change in Qs / % change in P = 30% / 20% = 1.5. Since PES > 1, supply is price-elastic.")

    # 7. Business Studies — Business meeting / boardroom
    add_img(S, G, "Business Organisation", "Partnership",
        query="business meeting boardroom discussion",
        text="A partnership firm has 4 partners. The firm incurs a loss of ₹80,000 and all partners share profits and losses equally. What is each partner's share of loss?",
        correct="₹20,000",
        wrongs=["₹40,000", "₹80,000", "₹16,000"],
        expl="Equal sharing among 4 partners: ₹80,000 ÷ 4 = ₹20,000 each.")

    # 8. Accountancy — Trial Balance (spreadsheet/table format)
    add_img(S, G, "Financial Accounting", "Trial Balance",
        query="spreadsheet financial data columns rows",
        text="A trial balance shows Debit total = ₹7,50,000 and Credit total = ₹7,20,000. The difference of ₹30,000 is transferred to which account?",
        correct="Suspense Account",
        wrongs=["Capital Account", "Profit & Loss Account", "Drawings Account"],
        expl="When the trial balance does not agree (debit ≠ credit), the difference is temporarily placed in a Suspense Account until the error is located and corrected.")

    # 9. Economics — Inflation / currency and prices
    add_img(S, G, "Money and Banking", "Inflation",
        query="currency money inflation economy",
        text="Inflation erodes the purchasing power of money. If inflation is 8% per year, how many years will it take for the purchasing power to halve (using the Rule of 70)?",
        correct="Approximately 8.75 years",
        wrongs=["Approximately 14 years", "Approximately 5 years", "Approximately 20 years"],
        expl="Rule of 70: Years to halve = 70 / inflation rate = 70 / 8 ≈ 8.75 years.")

    # 10. Business Studies — Warehouse / inventory storage
    add_img(S, G, "Internal Trade", "Warehousing",
        query="warehouse storage shelves inventory",
        text="The warehouse shown stores seasonal goods year-round. Which function of warehousing does this PRIMARILY represent?",
        correct="Time utility — making goods available when needed",
        wrongs=["Form utility — changing the physical form of goods", "Place utility — moving goods to point of sale", "Possession utility — transferring ownership"],
        expl="Warehousing creates TIME utility by storing goods produced in one season and releasing them when demand arises, bridging the gap between production and consumption.")

    print("  Grade 11 Commerce done.")


# ===========================================================================
#  COMMERCE GRADE 12
# ===========================================================================

def gen_gr12_commerce():
    print("\n" + "="*60)
    print("  Commerce Grade 12")
    print("="*60)
    S, G = "Commerce", 12

    # 1. Accountancy — Partnership dissolution / auction
    add_img(S, G, "Accounting for Partnership", "Dissolution of Partnership",
        query="auction gavel business sale",
        text="At dissolution, a partnership firm's assets realise ₹3,00,000 against a book value of ₹2,60,000. The profit of ₹40,000 is credited to which account?",
        correct="Realisation Account",
        wrongs=["Capital Account", "Profit & Loss Account", "Cash Account"],
        expl="All assets and liabilities at dissolution are transferred to the Realisation Account. Any profit (assets realised > book value) is also recorded in the Realisation Account before being distributed to partners.")

    # 2. Business Studies — Organisational chart / hierarchy
    add_img(S, G, "Principles of Management", "Span of Management",
        query="organisational chart hierarchy corporate",
        text="An org chart shows a manager directly supervising 8 subordinates. This relates to which management principle?",
        correct="Span of Management (Span of Control)",
        wrongs=["Unity of Command", "Division of Labour", "Scalar Chain"],
        expl="Span of Management refers to the number of subordinates directly reporting to a manager. Here the span is 8. A narrow span means more hierarchy; a wide span means flatter structure.")

    # 3. Economics — GDP / economic growth bar chart
    add_img(S, G, "National Income", "GDP and Economic Growth",
        query="GDP economic growth bar chart statistics",
        text="A bar chart shows a country's GDP rising from ₹150 lakh crore to ₹165 lakh crore in one year. What is the GDP growth rate?",
        correct="10%",
        wrongs=["15%", "5%", "8%"],
        expl="Growth rate = [(New GDP − Old GDP) / Old GDP] × 100 = [(165 − 150) / 150] × 100 = (15/150) × 100 = 10%.")

    # 4. Accountancy — Share certificate / stock
    add_img(S, G, "Company Accounts", "Issue of Shares",
        query="share certificate stock investment document",
        text="A company issues 10,000 shares of ₹10 face value at a premium of ₹5 each. What is the total amount credited to the Securities Premium Reserve?",
        correct="₹50,000",
        wrongs=["₹1,50,000", "₹1,00,000", "₹5,000"],
        expl="Securities Premium = Number of shares × premium per share = 10,000 × ₹5 = ₹50,000. Face value amount goes to Share Capital, premium goes to Securities Premium Reserve.")

    # 5. Business Studies — Advertisement / marketing billboard
    add_img(S, G, "Marketing Management", "Promotion Mix",
        query="advertisement billboard marketing outdoor",
        text="A company spends ₹20 lakh on a billboard campaign shown above. This is an example of which element of the promotion mix?",
        correct="Advertising",
        wrongs=["Personal Selling", "Sales Promotion", "Public Relations"],
        expl="Advertising is a paid, non-personal form of communication through mass media (TV, hoardings, newspapers). Outdoor billboards are a classic advertising medium.")

    # 6. Economics — Foreign exchange / currency exchange rates
    add_img(S, G, "Foreign Exchange", "Determination of Exchange Rate",
        query="foreign exchange currency rates board",
        text="A currency exchange board shows USD 1 = INR 83. If the rate changes to USD 1 = INR 86, what has happened to the Indian Rupee?",
        correct="The Rupee has depreciated against the Dollar",
        wrongs=["The Rupee has appreciated against the Dollar", "The Dollar has depreciated", "The exchange rate is fixed by the government"],
        expl="Depreciation means more units of domestic currency (INR) are needed per unit of foreign currency (USD). Going from 83 to 86 INR per USD means the Rupee has lost value — it has depreciated.")

    # 7. Accountancy — Cash flow statement (water flow analogy)
    add_img(S, G, "Cash Flow Statement", "Operating Investing Financing Activities",
        query="cash flow business finance money transfer",
        text="A cash flow statement shows: Operating Activities +₹4,00,000; Investing Activities −₹2,50,000; Financing Activities −₹80,000. What is the net change in cash?",
        correct="₹70,000 increase",
        wrongs=["₹70,000 decrease", "₹1,50,000 increase", "₹3,30,000 increase"],
        expl="Net cash change = 4,00,000 − 2,50,000 − 80,000 = ₹70,000 (positive = increase in cash balance).")

    # 8. Business Studies — Leadership / CEO at podium
    add_img(S, G, "Directing", "Leadership Styles",
        query="CEO speaker podium business leadership",
        text="A leader makes all decisions alone without consulting team members and expects complete obedience, as shown in the image. Which leadership style does this represent?",
        correct="Autocratic (Authoritarian) leadership",
        wrongs=["Democratic (Participative) leadership", "Laissez-faire (Free-rein) leadership", "Transformational leadership"],
        expl="Autocratic leaders centralise decision-making, give direct orders, and expect compliance without input from subordinates. This contrasts with democratic leaders who involve the team.")

    # 9. Economics — Unemployment / job seekers
    add_img(S, G, "Employment and Unemployment", "Types of Unemployment",
        query="unemployment job seekers queue",
        text="During an economic recession, thousands of factory workers shown lose jobs because demand for goods falls drastically. This type of unemployment is called:",
        correct="Cyclical (Demand-deficient) unemployment",
        wrongs=["Structural unemployment", "Frictional unemployment", "Seasonal unemployment"],
        expl="Cyclical unemployment occurs during economic downturns when aggregate demand falls, reducing output and leading to layoffs. It follows the business cycle — hence 'cyclical'.")

    # 10. Accountancy — Ratio analysis (financial report)
    add_img(S, G, "Analysis of Financial Statements", "Ratio Analysis",
        query="financial report analysis business document",
        text="A company's financial report shows: Current Assets = ₹8,00,000; Current Liabilities = ₹5,00,000; Inventory = ₹2,00,000. What is the Quick Ratio?",
        correct="1.2 : 1",
        wrongs=["1.6 : 1", "0.8 : 1", "2.0 : 1"],
        expl="Quick Ratio = (Current Assets − Inventory) / Current Liabilities = (8,00,000 − 2,00,000) / 5,00,000 = 6,00,000 / 5,00,000 = 1.2 : 1. Quick ratio excludes inventory as it is less liquid.")

    print("  Grade 12 Commerce done.")


# ===========================================================================
#  MAIN
# ===========================================================================

print("="*60)
print("  OlympiadReady - Commerce Pixabay Grade 11 & 12")
print("  Olympiad difficulty | 10 questions each grade")
print("="*60)

gen_gr11_commerce()
gen_gr12_commerce()

print(f"\n{'='*60}")
print(f"DONE - Posted: {posted}  Skipped: {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
print(f"{'='*60}")
