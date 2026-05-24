"""ICO question bank generator - uses Groq API (free). No Claude API key used."""
import json, os, re, time, unicodedata, requests

GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
COUNT        = 50
OUT_DIR      = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seeded")

# Unicode -> ASCII map (all keys as unicode escapes so source stays pure ASCII)
UMAP = [
    (u"₹","Rs."),(u"£","GBP"),(u"€","EUR"),
    (u"‘","'"),(u"’","'"),(u"“",'"'),(u"”",'"'),
    (u"′","'"),(u"″",'"'),
    (u"–","-"),(u"—","-"),(u"‒","-"),(u"―","-"),(u"−","-"),
    (u"…","..."),(u"×","x"),(u"÷","/"),
    (u"≥",">="),(u"≤","<="),(u"≠","!="),
    (u"√","sqrt"),(u"α","alpha"),(u"β","beta"),(u"π","pi"),
    (u"δ","delta"),(u"θ","theta"),
    (u"²","^2"),(u"³","^3"),(u"¹","^1"),
    (u"⁰","^0"),(u"⁴","^4"),(u"⁵","^5"),
    (u"₀","_0"),(u"₁","_1"),(u"₂","_2"),
    (u"½","1/2"),(u"¼","1/4"),(u"¾","3/4"),
    (u"°"," degrees"),(u"·","."),(u"•","-"),
    (u" "," "),(u"«",'"'),(u"»",'"'),
]

def clean(text):
    text = str(text)
    for ch, r in UMAP:
        text = text.replace(ch, r)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", errors="ignore").decode("ascii")
    return re.sub(r"  +", " ", text).strip()

def assert_ascii(qs, fname):
    for i, q in enumerate(qs):
        for f, v in q.items():
            items = v if isinstance(v, list) else [v]
            for item in items:
                bad = [c for c in str(item) if ord(c) > 127]
                if bad:
                    raise ValueError("%s Q%d '%s' has non-ASCII: %r" % (fname, i+1, f, bad[:3]))

TOPICS = [
    # ---------- Grade 11 ----------
    {"file":"sample-commerce-grade11-microeconomics.json","grade":11,"diff":"Foundation",
     "topic":"Commerce - Microeconomics",
     "syllabus":"Introductory Microeconomics Class 11 CBSE: central problems of economy, consumer equilibrium (utility analysis, indifference curves, budget line), law of demand, determinants of demand, price/income/cross elasticity of demand, production function, law of variable proportions, returns to scale, cost concepts (fixed, variable, total, average, marginal), revenue concepts (TR, MR, AR), forms of market (perfect competition, monopoly, monopolistic competition, oligopoly), price determination under perfect competition, price ceiling and floor."},

    {"file":"sample-commerce-grade11-statistics-for-economics.json","grade":11,"diff":"Foundation",
     "topic":"Commerce - Statistics for Economics",
     "syllabus":"Statistics for Economics Class 11 CBSE: primary vs secondary data, methods of collecting primary data, organisation of data, frequency distribution, tally marks, bar diagrams, pie charts, histograms, frequency polygons, ogives, arithmetic mean (direct, assumed mean, step deviation methods), median, mode, range, quartile deviation, mean deviation, standard deviation, coefficient of variation, Karl Pearson correlation coefficient, Spearman rank correlation, price index numbers, consumer price index, uses and limitations of statistics."},

    {"file":"sample-commerce-grade11-nature-purpose-forms-of-business.json","grade":11,"diff":"Foundation",
     "topic":"Commerce - Nature and Forms of Business",
     "syllabus":"Business Studies Class 11 CBSE: nature and purpose of business, business objectives, sole proprietorship (features, merits, limitations), partnership (types: active/sleeping/nominal partner, partnership deed, registration, dissolution), Joint Hindu Family Business (HUF, karta, coparcener, unlimited/limited liability), cooperative societies (types: consumer, producer, credit, housing, marketing), joint stock company (characteristics, types: public/private, formation stages, MOA, AOA, prospectus), public private and global enterprises, MNCs, disinvestment."},

    {"file":"sample-commerce-grade11-business-services-emerging-modes.json","grade":11,"diff":"Foundation",
     "topic":"Commerce - Business Services and Emerging Modes",
     "syllabus":"Business Studies Class 11 CBSE: banking services (types of banks, functions of commercial banks, e-banking, RBI role), insurance principles (indemnity, insurable interest, subrogation, utmost good faith, contribution, proximate cause), types of insurance (life, fire, marine), warehousing (types, functions), e-commerce (B2B, B2C, C2C, G2C), m-commerce, outsourcing, BPO, KPO, benefits and limitations of e-commerce, online payment methods, cybersecurity threats, intellectual property rights (copyright, trademark, patent)."},

    {"file":"sample-commerce-grade11-social-responsibility-finance-small-business.json","grade":11,"diff":"Foundation",
     "topic":"Commerce - Social Responsibility and Sources of Finance",
     "syllabus":"Business Studies Class 11 CBSE: social responsibility of business (concept, Carroll's pyramid, arguments for and against), business ethics, environment protection, sources of business finance: owners funds (equity shares, preference shares, retained earnings), borrowed funds (debentures, bank loans, public deposits, trade credit, factoring), angel investors, venture capital, MSME definition, role of small business in Indian economy, problems faced by MSMEs, government schemes (MUDRA, Stand-Up India)."},

    {"file":"sample-commerce-grade11-internal-international-trade.json","grade":11,"diff":"Foundation",
     "topic":"Commerce - Internal and International Trade",
     "syllabus":"Business Studies Class 11 CBSE: wholesale trade, retail trade types (itinerant traders, fixed shop retailers: general stores, single line stores, specialty stores), large scale retail (departmental stores, chain stores, supermarkets, consumer cooperative stores, mail order houses, teleshopping, vending machines), GST (concept, CGST, SGST, IGST), international business (concept, benefits, modes: exporting, importing, joint ventures, FDI, licensing, franchising), balance of trade vs balance of payments, WTO functions, export documentation (bill of lading, letter of credit, certificate of origin, shipping bill)."},

    {"file":"sample-commerce-grade11-accounting-theoretical-framework.json","grade":11,"diff":"Foundation",
     "topic":"Commerce - Accounting Theoretical Framework and Process",
     "syllabus":"Accountancy Class 11 CBSE: meaning and objectives of accounting, advantages and limitations, users of accounting information, accounting concepts (entity, money measurement, going concern, accounting period, cost, dual aspect, revenue recognition, matching, full disclosure), accounting conventions (consistency, conservatism, materiality, objectivity), accounting standards, GAAP, double entry system, accounting equation, source documents (invoice, receipt, debit/credit note), journal entries, ledger posting, trial balance, rectification of errors (types, suspense account), bank reconciliation statement, depreciation (SLM, WDV methods, asset disposal account), bills of exchange and promissory notes."},

    {"file":"sample-commerce-grade11-financial-statements-sole-proprietorship.json","grade":11,"diff":"Foundation",
     "topic":"Commerce - Financial Statements of Sole Proprietorship",
     "syllabus":"Accountancy Class 11 CBSE: trading account (purpose, format, gross profit calculation), profit and loss account, balance sheet from complete records, adjustments in final accounts (outstanding expenses, prepaid expenses, accrued income, income received in advance, depreciation, provision for bad debts, provision for discount on debtors, goods taken for personal use, interest on capital), incomplete records / single entry system (statement of affairs method to calculate opening capital, calculating profit or loss, comparison of capital method), converting single entry to double entry."},

    {"file":"sample-commerce-grade11-ico-achievers.json","grade":11,"diff":"Olympiad",
     "topic":"Commerce - ICO Achievers Section Grade 11",
     "syllabus":"Higher order thinking questions for ICO Class 11 covering all sections. Include: (1) Economics: elasticity calculations, indifference curve analysis, market equilibrium numerical, index number computation, correlation coefficient from given data. (2) Business Studies: insurance claim scenario identifying which principle applies, identifying correct form of business from a detailed case, e-commerce scenario analysis. (3) Accountancy: WDV depreciation multi-year calculation, preparing adjusted final accounts with multiple adjustments, finding profit from incomplete records. Questions must be case-study based, passage-based, or multi-step numerical. Each question should be significantly more challenging than Foundation level."},

    # ---------- Grade 12 ----------
    {"file":"sample-commerce-grade12-macroeconomics.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Macroeconomics",
     "syllabus":"Introductory Macroeconomics Class 12 CBSE: national income concepts (GDP, GNP, NNP, NDP at market price and factor cost, personal income, disposable income), methods of calculating national income (income method, expenditure method, value added method), circular flow of income, money and banking (functions of money, credit creation by commercial banks, RBI functions, monetary policy tools: CRR, SLR, bank rate, open market operations, repo rate, reverse repo rate), aggregate demand components (C+I+G+NX), Keynesian theory of income determination, investment multiplier, government budget (revenue receipts/expenditure, capital receipts/expenditure, fiscal deficit, revenue deficit, primary deficit, types of budget), balance of payments (current account, capital account, BOP deficit/surplus), foreign exchange market, exchange rate determination, managed floating."},

    {"file":"sample-commerce-grade12-indian-economic-development.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Indian Economic Development",
     "syllabus":"Indian Economic Development Class 12 CBSE: Indian economy on eve of independence (colonial impact, occupational structure, GDP share), five year plans (objectives, achievements), mixed economy model, Green Revolution (causes, effects, limitations), land reforms, industrial policy 1956, public sector role, LPG reforms 1991 (background, components: industrial delicensing, financial sector reform, trade liberalisation, disinvestment), effects of globalisation on Indian economy, poverty (absolute and relative, HCR, poverty line, causes, anti-poverty programmes: PDS, MGNREGA, PMGSY, Antyodaya), unemployment (types, NSSO data, MGNREGA), human capital formation (education, health expenditure), rural development (credit, land reforms, diversification), sustainable development and environmental issues, comparison of development indicators with China and Pakistan."},

    {"file":"sample-commerce-grade12-management-principles.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Nature and Principles of Management",
     "syllabus":"Business Studies Class 12 CBSE: nature and significance of management (definition, objectives, importance), characteristics of management (goal-oriented, pervasive, multi-dimensional, continuous, group activity, dynamic, intangible), management as science/art/profession, levels of management (top: policy making; middle: implementing; lower: supervisory), Fayol's 14 principles (division of work, authority and responsibility, discipline, unity of command, unity of direction, subordination of individual interest, remuneration, centralisation, scalar chain, order, equity, stability of tenure, initiative, esprit de corps), Taylor's scientific management (principles: science not rule of thumb, harmony, cooperation, maximum output, development of each person; techniques: functional foremanship, standardisation, simplification, time study, motion study, fatigue study, differential piece wage), differences between Fayol and Taylor, business environment dimensions (economic, social, technological, political, legal), impact of LPG on business."},

    {"file":"sample-commerce-grade12-planning-organising-staffing.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Planning, Organising and Staffing",
     "syllabus":"Business Studies Class 12 CBSE: planning (meaning, importance, limitations: rigidity, time-consuming, does not work in dynamic environment; types: strategic, tactical, operational; steps in planning process; MBO - objectives, process, benefits), organising (meaning, importance, steps, span of management factors, departmentalisation by function/product/territory/customer, formal vs informal organisation, delegation - elements: authority, responsibility, accountability; barriers to delegation; decentralisation vs centralisation, differences), staffing (meaning, importance, HRM process: estimating manpower requirements, recruitment - internal sources: promotion/transfer, external sources: direct recruitment/campus/employment exchange/advertisement; selection process steps; training and development methods: on-the-job: apprenticeship, job rotation; off-the-job: vestibule, lecture; performance appraisal, promotion, compensation)."},

    {"file":"sample-commerce-grade12-directing-controlling.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Directing and Controlling",
     "syllabus":"Business Studies Class 12 CBSE: directing (meaning, importance, principles), supervision (role of supervisor), motivation (meaning, importance, Maslow's hierarchy of needs: physiological/safety/social/esteem/self-actualisation; Herzberg's two-factor theory: hygiene factors vs motivators; financial incentives: pay, bonus, profit sharing; non-financial incentives: recognition, job enrichment, ESOPs), leadership (meaning, styles: authoritarian/autocratic, democratic/participative, laissez-faire/free-rein; qualities of a good leader), communication (process, formal: downward/upward/horizontal; informal: grapevine; barriers: semantic, psychological, organisational, personal; improving communication), controlling (meaning, importance, steps: setting standards, measuring actual performance, comparing, taking corrective action; relationship with planning; techniques: budgetary control, ratio analysis, ROI, EVA, PERT, CPM, MIS)."},

    {"file":"sample-commerce-grade12-financial-management-markets.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Financial Management and Financial Markets",
     "syllabus":"Business Studies Class 12 CBSE: financial management (meaning, objectives: profit maximisation vs wealth maximisation; financial decisions: investment decision/capital budgeting, financing decision/capital structure, dividend decision; factors affecting capital structure: cash flow, interest coverage, debt service coverage, ROI, cost of debt, tax rate, flexibility, control; trading on equity; working capital: meaning, types, factors affecting; fixed capital: meaning, factors affecting), financial markets (meaning, functions; money market instruments: call money, treasury bills, commercial paper, certificate of deposit, commercial bill; capital market: primary market methods: public issue through prospectus, offer for sale, private placement, rights issue, e-IPO; secondary market: stock exchange functions, listing, trading procedure, BSE Sensex, NSE Nifty, SEBI: objectives, functions, powers, SEBI as regulator)."},

    {"file":"sample-commerce-grade12-marketing-consumer-protection.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Marketing Management and Consumer Protection",
     "syllabus":"Business Studies Class 12 CBSE: marketing (meaning, functions, marketing management philosophies: production/product/selling/marketing/societal concept), marketing mix 4Ps: product (levels, product life cycle, branding - types of brand names, brand equity, packaging functions, labelling), price (factors affecting pricing, pricing methods: cost-plus, competition-based, value-based), place/distribution (types of channels: zero/one/two/three level; factors determining channel; wholesaler vs retailer functions), promotion (advertising - features, objectives, merits, demerits; personal selling - qualities of salesman; sales promotion tools; public relations), consumer protection (importance, Consumer Protection Act 2019, rights of consumers: right to safety/information/choice/heard/redressal/education; consumer responsibilities; District/State/National Consumer Disputes Redressal Commission; consumer organisations and NGOs role)."},

    {"file":"sample-commerce-grade12-partnership-accounts.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Accounting for Partnership Firms",
     "syllabus":"Accountancy Class 12 CBSE: features of partnership, partnership deed, fixed vs fluctuating capital method, profit and loss appropriation account (interest on capital, interest on drawings, partner salary, partner commission, transfer to reserves), goodwill (nature, need for valuation, factors affecting, methods: average profit method, super profit method, capitalisation method), admission of partner (new profit sharing ratio, sacrificing ratio, treatment of goodwill: raised and written off, adjusted through capital accounts, hidden goodwill, revaluation of assets and liabilities, treatment of accumulated profits and losses, journal entries for admission), retirement/death of partner (gaining ratio, treatment of goodwill on retirement, revaluation, settlement of accounts of retiring partner), dissolution of partnership firm (settlement of accounts, realisation account, Garner vs Murray rule for insolvency of a partner)."},

    {"file":"sample-commerce-grade12-company-accounts.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Accounting for Companies",
     "syllabus":"Accountancy Class 12 CBSE: types of share capital (authorised, issued, subscribed, called-up, paid-up), issue of shares at par/premium/discount, pro-rata allotment, calls in arrears and advance, forfeiture of shares (journal entries), reissue of forfeited shares (at discount, at par, at premium), buy-back of shares, types of debentures (secured/unsecured, redeemable/irredeemable, convertible/non-convertible), issue of debentures at par/premium/discount, issue as collateral security, interest on debentures (journal entries), redemption of debentures (methods: lump sum, instalments, sinking fund method, open market purchase, conversion into shares or new debentures), financial statements of companies: balance sheet as per Schedule III format, statement of profit and loss, notes to accounts."},

    {"file":"sample-commerce-grade12-financial-statement-analysis-cashflow.json","grade":12,"diff":"Foundation",
     "topic":"Commerce - Analysis of Financial Statements and Cash Flow",
     "syllabus":"Accountancy Class 12 CBSE: tools of financial analysis (comparative statements: inter-firm and inter-period; common size statements: balance sheet and income statement), ratio analysis: liquidity ratios (current ratio: ideal 2:1, quick ratio: ideal 1:1), solvency ratios (debt-equity ratio, total assets to debt ratio, proprietary ratio, interest coverage ratio), activity/turnover ratios (inventory turnover ratio, debtors turnover ratio, creditors turnover ratio, working capital turnover ratio), profitability ratios (gross profit ratio, net profit ratio, operating ratio, operating profit ratio, return on investment, return on equity), limitations of ratio analysis, cash flow statement (meaning, objectives, operating activities: direct and indirect method, investing activities, financing activities; preparation using indirect method as per AS-3 / Ind AS-7; adjustments for non-cash items and working capital changes)."},

    {"file":"sample-commerce-grade12-ico-achievers.json","grade":12,"diff":"Olympiad",
     "topic":"Commerce - ICO Achievers Section Grade 12",
     "syllabus":"Higher order thinking questions for ICO Class 12 covering all sections. Include: (1) Economics: national income calculation using given data (expenditure or income method), multiplier effect numerical, fiscal deficit calculation from budget data, BOP problem identification. (2) Business Studies: identifying Fayol or Taylor principle from a detailed workplace scenario, identifying leadership style from a case, SEBI function identification, marketing mix decision from business case. (3) Accountancy: goodwill valuation using super profit method with given data, admission of partner with hidden goodwill and revaluation, ratio analysis with multiple ratios from given balance sheet data, cash flow statement classification. Questions must be case-study, passage-based, or multi-step numerical. Each should require higher-order thinking beyond simple recall."},
]

PROMPT = """You are an expert question setter for the SOF International Commerce Olympiad (ICO), following the CBSE/NCERT Class {grade} syllabus.

Generate exactly {count} multiple-choice questions on: {topic}
Syllabus: {syllabus}

STRICT RULES:
1. Exactly 4 options per question, labeled: A) ... B) ... C) ... D) ...
2. CorrectAnswer: single uppercase letter A, B, C, or D.
3. Difficulty: {diff}  (Foundation = direct conceptual; Olympiad = case-study/multi-step/analytical)
4. CRITICAL - plain ASCII only:
   - Rupee: write Rs. (never use rupee symbol)
   - Straight apostrophes and quotes only
   - Hyphens only, no em-dash or en-dash
   - Simple fractions: 1/2 not Unicode fractions
   - No superscript/subscript Unicode characters
5. Each question must cover a DIFFERENT sub-concept from the syllabus.
6. Explanation: 1-2 concise sentences.
7. SubTopic: specific concept name (e.g. "Law of Demand", "Fayol Equity Principle").

Return ONLY a raw JSON array - no markdown, no wrapper object:
[
  {{
    "QuestionText": "...",
    "Options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "CorrectAnswer": "A",
    "Topic": "{topic}",
    "SubTopic": "...",
    "Difficulty": "{diff}",
    "Explanation": "..."
  }}
]"""


def call_groq(prompt):
    resp = requests.post(
        GROQ_API_URL,
        headers={"Authorization": "Bearer " + GROQ_API_KEY, "Content-Type": "application/json"},
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        },
        timeout=120,
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    parsed = json.loads(raw)
    if isinstance(parsed, list):
        return parsed
    for v in parsed.values():
        if isinstance(v, list):
            return v
    raise ValueError("Unexpected response shape")


def validate(questions, topic, diff):
    valid = []
    for i, q in enumerate(questions):
        try:
            qt   = clean(q.get("QuestionText", ""))
            opts = [clean(o) for o in q.get("Options", [])]
            ans  = str(q.get("CorrectAnswer", "")).strip().upper()
            if len(opts) != 4 or ans not in ("A","B","C","D") or not qt:
                continue
            valid.append({
                "QuestionText": qt,
                "Options":      opts,
                "CorrectAnswer":ans,
                "Topic":        clean(topic),
                "SubTopic":     clean(q.get("SubTopic","")),
                "Difficulty":   str(q.get("Difficulty", diff)),
                "Explanation":  clean(q.get("Explanation","")),
            })
        except Exception:
            pass
    return valid


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    total, failed = 0, []

    for i, cfg in enumerate(TOPICS):
        out = os.path.join(OUT_DIR, cfg["file"])
        if os.path.exists(out):
            n = len(json.load(open(out, encoding="ascii")))
            print("[%d/%d] SKIP (exists, %d Qs): %s" % (i+1, len(TOPICS), n, cfg["file"]))
            continue

        print("\n[%d/%d] %s  grade=%d  diff=%s" % (i+1, len(TOPICS), cfg["topic"], cfg["grade"], cfg["diff"]))

        prompt = PROMPT.format(
            grade=cfg["grade"], count=COUNT,
            topic=cfg["topic"], syllabus=cfg["syllabus"], diff=cfg["diff"]
        )

        try:
            qs = validate(call_groq(prompt), cfg["topic"], cfg["diff"])
            print("  Got %d valid questions" % len(qs))

            if len(qs) < 40:
                print("  Low count, retrying...")
                time.sleep(3)
                extra = validate(call_groq(prompt), cfg["topic"], cfg["diff"])
                seen = {q["QuestionText"] for q in qs}
                qs += [q for q in extra if q["QuestionText"] not in seen]
                print("  After retry: %d questions" % len(qs))

            assert_ascii(qs, cfg["file"])

            with open(out, "w", encoding="ascii") as f:
                json.dump(qs, f, indent=2, ensure_ascii=True)

            print("  Saved: %s" % cfg["file"])
            total += len(qs)

        except Exception as e:
            print("  [ERROR] %s" % e)
            failed.append(cfg["file"])

        if i < len(TOPICS) - 1:
            time.sleep(2)

    print("\n=== DONE: %d total questions ===" % total)
    if failed:
        print("Failed topics:", failed)
    print("Next: run  pwsh api/import-ico.ps1")


if __name__ == "__main__":
    main()
