import pyodbc, uuid, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=olympiadready-np.database.windows.net;"
    "DATABASE=OlympiadReady;"
    "UID=nyxen-admin;PWD=Olympiad@2026"
)

def insert(conn, q):
    c = conn.cursor()
    c.execute("SELECT 1 FROM QuestionBank WHERE Subject=? AND Grade=? AND SubTopic=? AND QuestionText=?",
              q["subject"], q["grade"], q["subTopic"], q["questionText"])
    if c.fetchone():
        return "DUP"
    c.execute("""INSERT INTO QuestionBank
                 (QuestionBankId,Subject,Grade,Difficulty,Topic,SubTopic,
                  QuestionText,OptionsJson,CorrectAnswer,Explanation,CreatedAt)
                 VALUES (?,?,?,?,?,?,?,?,?,?,GETUTCDATE())""",
              str(uuid.uuid4()).upper(), q["subject"], q["grade"], q["difficulty"],
              q["topic"], q["subTopic"], q["questionText"],
              json.dumps(q["options"]), q["correctAnswer"], q["explanation"])
    conn.commit()
    return "OK"

questions = [

# ── Commerce G12 Advanced (20q) — tier was MISSING entirely ──────────────────
{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Partnership Accounts — Goodwill",
 "questionText":"Under the Average Profit Method, goodwill is calculated as:",
 "options":["A: Super profit × Number of years' purchase","B: Average profit × Number of years' purchase","C: Normal profit × Capitalisation rate","D: Future profit × Discount factor"],
 "correctAnswer":"B",
 "explanation":"Average Profit Method: Goodwill = Average (maintainable) profit × Number of years' purchase. The number of years' purchase reflects how many years a buyer is willing to pay for the existing goodwill."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Partnership — Admission of Partner",
 "questionText":"When a new partner is admitted, the existing partners' Capital Accounts are credited with their share of:",
 "options":["A: General reserve only","B: Goodwill brought in by new partner (in their gaining ratio)","C: New partner's capital contribution","D: Revaluation loss"],
 "correctAnswer":"B",
 "explanation":"On admission, the new partner pays for goodwill (premium for goodwill). This is credited to existing partners' Capital Accounts in their sacrificing ratio — compensating them for the share of future profits they give up."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Company Accounts — Issue of Shares",
 "questionText":"When shares are issued at a price above their face (nominal) value, the excess is credited to:",
 "options":["A: Share Capital Account","B: General Reserve","C: Securities Premium Reserve","D: Capital Reserve"],
 "correctAnswer":"C",
 "explanation":"Under Section 52 of Companies Act 2013, the premium received on issue of shares is credited to Securities Premium Reserve, which can be used for specific purposes (issuing bonus shares, writing off preliminary expenses, etc.)."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Company Accounts — Debentures",
 "questionText":"Debentures issued at a discount and redeemable at par result in:",
 "options":["A: Capital loss to the company","B: Loss on issue — written off over the life of the debenture","C: Profit for the debenture holder","D: No impact on accounts"],
 "correctAnswer":"B",
 "explanation":"Discount on issue of debentures is a capital loss. It is shown as a fictitious asset and written off (amortised) over the life of the debenture against Securities Premium or Statement of P&L."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Cash Flow Statement",
 "questionText":"In a Cash Flow Statement, repayment of bank loan is classified as:",
 "options":["A: Operating activity","B: Investing activity","C: Financing activity","D: Non-cash activity"],
 "correctAnswer":"C",
 "explanation":"Financing activities include transactions with lenders and shareholders — borrowing and repaying loans, issuing/buying back shares, paying dividends. Repayment of bank loan is a cash outflow under financing activities."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Ratio Analysis — Liquidity",
 "questionText":"The Quick Ratio (Acid-Test Ratio) excludes which current asset from the numerator?",
 "options":["A: Cash and bank balances","B: Debtors","C: Inventory (Stock)","D: Short-term investments"],
 "correctAnswer":"C",
 "explanation":"Quick Ratio = (Current Assets − Inventory − Prepaid Expenses) / Current Liabilities. Inventory is excluded because it may not be quickly convertible to cash. A ratio ≥ 1 is generally considered satisfactory."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Ratio Analysis — Profitability",
 "questionText":"Return on Investment (ROI) is calculated as:",
 "options":["A: Net Profit / Sales × 100","B: Net Profit / Total Assets × 100","C: Gross Profit / Sales × 100","D: EBIT / Capital Employed × 100"],
 "correctAnswer":"D",
 "explanation":"ROI (or Return on Capital Employed) = EBIT / Capital Employed × 100. Capital Employed = Shareholders' Funds + Long-term Borrowings. It measures how efficiently capital is being used."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Financial Management",
 "questionText":"The optimal capital structure is the debt-equity mix that:",
 "options":["A: Uses 100% equity","B: Minimises the cost of capital and maximises firm value","C: Uses 100% debt","D: Keeps the D/E ratio at exactly 1:1"],
 "correctAnswer":"B",
 "explanation":"Optimal capital structure minimises the Weighted Average Cost of Capital (WACC) and thereby maximises the market value of the firm. The right balance of debt (tax shield) and equity is firm-specific."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Financial Markets — Stock Exchange",
 "questionText":"SEBI (Securities and Exchange Board of India) was established in:",
 "options":["A: 1980","B: 1988 (statutory body 1992)","C: 1994","D: 2000"],
 "correctAnswer":"B",
 "explanation":"SEBI was established as a non-statutory body in 1988 and given statutory powers under the SEBI Act, 1992. It regulates and develops the securities market and protects investor interests."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Consumer Protection",
 "questionText":"Under the Consumer Protection Act 2019, a consumer complaint can be filed in District Commission for claims up to:",
 "options":["A: ₹10 lakh","B: ₹1 crore","C: ₹50 lakh","D: ₹5 crore"],
 "correctAnswer":"B",
 "explanation":"Consumer Protection Act 2019 revised pecuniary limits: District Commission → up to ₹1 crore; State Commission → ₹1 crore to ₹10 crore; National Commission → above ₹10 crore."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Partnership — Retirement",
 "questionText":"On retirement of a partner, the gaining ratio is the ratio in which the remaining partners:",
 "options":["A: Share the retiring partner's capital","B: Gain the retiring partner's share of profits","C: Pay goodwill to the retiring partner","D: Revalue assets"],
 "correctAnswer":"B",
 "explanation":"Gaining Ratio = New Profit Sharing Ratio − Old Profit Sharing Ratio (for remaining partners). It determines how much extra share of profit each remaining partner gains from the retiring partner's surrender."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Dissolution of Partnership",
 "questionText":"In case of dissolution of a firm, after paying all liabilities, the residual assets are distributed to partners in their:",
 "options":["A: Equal shares","B: Profit-sharing ratio","C: Capital ratio","D: Gaining ratio"],
 "correctAnswer":"B",
 "explanation":"After paying creditors, loans, and partners' loans, the remaining assets (or deficiency) are shared among partners in their profit-sharing ratio, as the profits and losses are borne in that ratio."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Organising — Delegation",
 "questionText":"The process of assigning tasks and authority downward in the organisation hierarchy is called:",
 "options":["A: Coordination","B: Decentralisation","C: Delegation","D: Centralisation"],
 "correctAnswer":"C",
 "explanation":"Delegation is the transfer of authority from superior to subordinate for a specific task. Decentralisation is the systematic delegation of authority throughout the organisation — it is an extension of delegation."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Controlling",
 "questionText":"Management by Exception (MBE) is a principle of controlling that states managers should focus on:",
 "options":["A: Every small deviation from the plan","B: Only significant deviations, not minor variations","C: External environmental changes","D: Competitor benchmarking only"],
 "correctAnswer":"B",
 "explanation":"MBE: managers should concentrate their time and attention only on significant deviations from plans, leaving routine matters to subordinates. This saves managerial time for critical issues."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Company Accounts — Forfeiture of Shares",
 "questionText":"The Share Forfeiture Account balance (after forfeiture) is ultimately transferred to:",
 "options":["A: General Reserve","B: Capital Reserve (after reissue)","C: Profit and Loss Account","D: Securities Premium"],
 "correctAnswer":"B",
 "explanation":"On reissue of forfeited shares, any excess in the Forfeited Shares Account (after adjusting any discount on reissue) is transferred to Capital Reserve, as it is a capital profit not available for distribution."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Staffing",
 "questionText":"The difference between training and development in human resource management is that development is:",
 "options":["A: Job-specific and short-term","B: Broader, long-term, and focuses on future roles and overall growth","C: Only for technical skills","D: Limited to new employees"],
 "correctAnswer":"B",
 "explanation":"Training is job-specific and skill-focused (immediate task performance). Development is broader — it aims at overall personal and professional growth, preparing employees for future responsibilities and leadership."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Directing — Motivation",
 "questionText":"Maslow's Hierarchy of Needs arranges human needs in how many levels?",
 "options":["A: 3","B: 4","C: 5","D: 7"],
 "correctAnswer":"C",
 "explanation":"Maslow (1943) proposed 5 levels: (1) Physiological, (2) Safety, (3) Social/Love and Belonging, (4) Esteem, (5) Self-Actualisation. People are motivated to fulfil lower-order needs before higher ones."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Marketing — Advertising",
 "questionText":"Which of the following is NOT a function of advertising?",
 "options":["A: Inform consumers about new products","B: Persuade consumers to buy","C: Directly deliver the product to consumers","D: Remind consumers about existing products"],
 "correctAnswer":"C",
 "explanation":"Advertising informs, persuades, and reminds — it is a paid, non-personal form of communication. Physical delivery of products is the function of the distribution channel (place in marketing mix), not advertising."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Accountancy",
 "subTopic":"Analysis of Financial Statements — Comparative",
 "questionText":"Comparative Financial Statements show figures of two or more years side by side primarily to help in:",
 "options":["A: Intra-firm comparison over time (trend analysis)","B: Inter-firm comparison only","C: Ratio calculation only","D: Tax filing"],
 "correctAnswer":"A",
 "explanation":"Comparative statements place figures of two or more periods side by side, showing absolute change and percentage change, enabling intra-firm trend analysis to assess growth or decline over time."},

{"subject":"Commerce","grade":12,"difficulty":"Advanced","topic":"Business Studies",
 "subTopic":"Business Environment",
 "questionText":"The liberalisation, privatisation, and globalisation (LPG) reforms in India were introduced in:",
 "options":["A: 1985","B: 1991","C: 1995","D: 2001"],
 "correctAnswer":"B",
 "explanation":"India's LPG reforms were announced in July 1991 by Finance Minister Dr. Manmohan Singh under PM P.V. Narasimha Rao, in response to a severe balance-of-payments crisis. They transformed the Indian economy."},

# ── Spell Bee G1 Foundation (+15q, currently 15 → 30) ─────────────────────────
{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"3-Letter Words",
 "questionText":"Which spelling is correct for the animal that says 'moo'?",
 "options":["A: kow","B: cow","C: cuw","D: kau"],
 "correctAnswer":"B",
 "explanation":"'Cow' is a 3-letter word (C-O-W). A cow is a farm animal known for giving milk."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"3-Letter Words",
 "questionText":"Which is the correct spelling for something you sit on?",
 "options":["A: chare","B: chiar","C: chair","D: cheer"],
 "correctAnswer":"C",
 "explanation":"'Chair' is the correct spelling. A chair is a piece of furniture you sit on."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"4-Letter Words",
 "questionText":"Choose the correct spelling of the colour of grass:",
 "options":["A: grean","B: gren","C: grene","D: green"],
 "correctAnswer":"D",
 "explanation":"'Green' is the correct spelling (G-R-E-E-N). Grass, leaves, and frogs are often green."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"4-Letter Words",
 "questionText":"Which spelling is correct for what you read?",
 "options":["A: buk","B: book","C: bock","D: bouk"],
 "correctAnswer":"B",
 "explanation":"'Book' is the correct spelling (B-O-O-K). Books have pages and words to read."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Animal Names",
 "questionText":"Which is the correct spelling of a striped jungle animal?",
 "options":["A: tyger","B: tiegr","C: tiger","D: tigur"],
 "correctAnswer":"C",
 "explanation":"'Tiger' is the correct spelling (T-I-G-E-R). Tigers are big cats with orange and black stripes."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Common Words",
 "questionText":"Choose the correct spelling of the opposite of night:",
 "options":["A: dai","B: dey","C: day","D: daye"],
 "correctAnswer":"C",
 "explanation":"'Day' is the correct spelling (D-A-Y). Daytime is when the sun shines."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Body Parts",
 "questionText":"Which is the correct spelling of what you use to smell?",
 "options":["A: noze","B: noes","C: nose","D: nowse"],
 "correctAnswer":"C",
 "explanation":"'Nose' is the correct spelling (N-O-S-E). You use your nose to smell flowers and food."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Common Words",
 "questionText":"Which spelling is correct for the round shape?",
 "options":["A: sircle","B: cercle","C: circle","D: sircul"],
 "correctAnswer":"C",
 "explanation":"'Circle' is the correct spelling (C-I-R-C-L-E). A circle is a perfectly round shape."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Food Words",
 "questionText":"Choose the correct spelling of the yellow fruit:",
 "options":["A: bananah","B: banana","C: banaena","D: bannana"],
 "correctAnswer":"B",
 "explanation":"'Banana' is the correct spelling (B-A-N-A-N-A). Bananas are yellow and sweet."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Common Words",
 "questionText":"Which is the correct spelling of what shines in the sky at night?",
 "options":["A: stare","B: ster","C: star","D: starr"],
 "correctAnswer":"C",
 "explanation":"'Star' is the correct spelling (S-T-A-R). Stars twinkle in the night sky."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Colours",
 "questionText":"Which spelling is correct for the colour of the sky?",
 "options":["A: blew","B: bloo","C: bloe","D: blue"],
 "correctAnswer":"D",
 "explanation":"'Blue' is the correct spelling (B-L-U-E). The sky and the ocean appear blue."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Transport Words",
 "questionText":"Choose the correct spelling of a vehicle that flies:",
 "options":["A: plene","B: plain","C: plane","D: plaen"],
 "correctAnswer":"C",
 "explanation":"'Plane' (short for airplane) is the correct spelling (P-L-A-N-E). Planes fly through the sky."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Nature Words",
 "questionText":"Which is the correct spelling for water that falls from clouds?",
 "options":["A: rane","B: rain","C: rayn","D: rein"],
 "correctAnswer":"B",
 "explanation":"'Rain' is the correct spelling (R-A-I-N). Rain is water that falls from clouds."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Number Words",
 "questionText":"Which spelling is correct for the number after nine?",
 "options":["A: ten","B: tenn","C: tean","D: ten"],
 "correctAnswer":"A",
 "explanation":"'Ten' is the correct spelling (T-E-N). Ten comes after nine in counting."},

{"subject":"Spell Bee","grade":1,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Common Words",
 "questionText":"Choose the correct spelling of the building where you learn:",
 "options":["A: skool","B: scool","C: school","D: schule"],
 "correctAnswer":"C",
 "explanation":"'School' is the correct spelling (S-C-H-O-O-L). We go to school to learn and study."},

# ── Spell Bee G2 Foundation (+15q, currently 15 → 30) ─────────────────────────
{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"5-Letter Words",
 "questionText":"Which is the correct spelling of a large grey animal with a trunk?",
 "options":["A: elefant","B: elephant","C: elephent","D: eliphant"],
 "correctAnswer":"B",
 "explanation":"'Elephant' is the correct spelling (E-L-E-P-H-A-N-T). Elephants are the largest land animals."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Double Letters",
 "questionText":"Which spelling is correct for a sweet treat made from cocoa?",
 "options":["A: chocolat","B: choclate","C: chocolate","D: choculate"],
 "correctAnswer":"C",
 "explanation":"'Chocolate' is the correct spelling (C-H-O-C-O-L-A-T-E). Chocolate is made from cacao beans."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Silent Letters",
 "questionText":"Choose the correct spelling of a sharp tool used for cutting:",
 "options":["A: nife","B: knive","C: knife","D: kniff"],
 "correctAnswer":"C",
 "explanation":"'Knife' has a silent 'K' (K-N-I-F-E). The 'kn' combination always has a silent K in English."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Common Words",
 "questionText":"Which is the correct spelling of the season with falling leaves?",
 "options":["A: autum","B: autumn","C: autunm","D: autumne"],
 "correctAnswer":"B",
 "explanation":"'Autumn' is the correct spelling (A-U-T-U-M-N). In autumn, leaves turn red, orange, and yellow."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Science Words",
 "questionText":"Choose the correct spelling of the planet we live on:",
 "options":["A: Erth","B: Eath","C: Earht","D: Earth"],
 "correctAnswer":"D",
 "explanation":"'Earth' is the correct spelling (E-A-R-T-H). Earth is our home planet in the solar system."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Action Words",
 "questionText":"Which spelling is correct for moving through water using your arms?",
 "options":["A: swimm","B: sweem","C: swim","D: swime"],
 "correctAnswer":"C",
 "explanation":"'Swim' is the correct spelling (S-W-I-M). When you swim, you move through water."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Compound Concepts",
 "questionText":"Choose the correct spelling of a bow of colours in the sky after rain:",
 "options":["A: rainboe","B: rainbbow","C: rainbow","D: raynbow"],
 "correctAnswer":"C",
 "explanation":"'Rainbow' is the correct spelling (R-A-I-N-B-O-W). A rainbow forms when sunlight passes through raindrops."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Family Words",
 "questionText":"Which is the correct spelling for your mother's mother?",
 "options":["A: granmother","B: grandmother","C: grandmuther","D: grandmothar"],
 "correctAnswer":"B",
 "explanation":"'Grandmother' is the correct spelling (G-R-A-N-D-M-O-T-H-E-R). Your grandmother is your parent's mother."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Time Words",
 "questionText":"Choose the correct spelling of the day before today:",
 "options":["A: yesturday","B: yesterday","C: yeterday","D: yestrday"],
 "correctAnswer":"B",
 "explanation":"'Yesterday' is the correct spelling (Y-E-S-T-E-R-D-A-Y). Yesterday is the day that has just passed."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Nature Words",
 "questionText":"Which spelling is correct for the large body of salt water?",
 "options":["A: oceen","B: osean","C: ocean","D: oceon"],
 "correctAnswer":"C",
 "explanation":"'Ocean' is the correct spelling (O-C-E-A-N). The five oceans cover about 71% of Earth's surface."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Adjectives",
 "questionText":"Choose the correct spelling of the opposite of dirty:",
 "options":["A: clene","B: claen","C: clean","D: cleane"],
 "correctAnswer":"C",
 "explanation":"'Clean' is the correct spelling (C-L-E-A-N). When something is clean, it has no dirt or mess."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Science Words",
 "questionText":"Which is the correct spelling of the natural satellite of Earth?",
 "options":["A: mun","B: moone","C: moon","D: moom"],
 "correctAnswer":"C",
 "explanation":"'Moon' is the correct spelling (M-O-O-N). The Moon orbits Earth and reflects sunlight."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Common Nouns",
 "questionText":"Choose the correct spelling of the person who teaches you:",
 "options":["A: teacer","B: teacher","C: teachur","D: teecher"],
 "correctAnswer":"B",
 "explanation":"'Teacher' is the correct spelling (T-E-A-C-H-E-R). A teacher helps students learn new things."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Vegetables",
 "questionText":"Which spelling is correct for the orange vegetable rabbits love?",
 "options":["A: carot","B: carrot","C: carrut","D: carott"],
 "correctAnswer":"B",
 "explanation":"'Carrot' is the correct spelling (C-A-R-R-O-T) — note the double R. Carrots are orange root vegetables."},

{"subject":"Spell Bee","grade":2,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Transport",
 "questionText":"Choose the correct spelling of the two-wheeled vehicle you pedal:",
 "options":["A: bicicle","B: bicyle","C: bicycle","D: bycicle"],
 "correctAnswer":"C",
 "explanation":"'Bicycle' is the correct spelling (B-I-C-Y-C-L-E). 'Bi' means two, and 'cycle' refers to the wheels."},

# ── Spell Bee G3 Foundation (+15q, currently 15 → 30) ─────────────────────────
{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Tricky Spellings",
 "questionText":"Which is the correct spelling of a word meaning to move quietly and secretly?",
 "options":["A: sneek","B: sneak","C: sneac","D: sneake"],
 "correctAnswer":"B",
 "explanation":"'Sneak' is the correct spelling (S-N-E-A-K). To sneak means to move quietly without being noticed."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Silent Letters",
 "questionText":"Choose the correct spelling of the hour when the sun goes down:",
 "options":["A: twighlight","B: twilight","C: twillite","D: twilite"],
 "correctAnswer":"B",
 "explanation":"'Twilight' is the correct spelling (T-W-I-L-I-G-H-T). Twilight is the soft glowing light from the sky after sunset."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Double Letters",
 "questionText":"Which spelling is correct for the subject that uses numbers?",
 "options":["A: mathamatics","B: mathemattics","C: mathematics","D: mathimatics"],
 "correctAnswer":"C",
 "explanation":"'Mathematics' is the correct spelling (M-A-T-H-E-M-A-T-I-C-S). Mathematics is the study of numbers, shapes and patterns."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"ie/ei Words",
 "questionText":"Choose the correct spelling of what you do when you get something from someone:",
 "options":["A: recieve","B: receive","C: receve","D: receeve"],
 "correctAnswer":"B",
 "explanation":"'Receive' is the correct spelling (R-E-C-E-I-V-E). Remember: 'i before e, except after c' — so it's 'cei' not 'cie'."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Geography Words",
 "questionText":"Which is the correct spelling of a large area of sand with little rain?",
 "options":["A: deseart","B: dessert","C: desert","D: dezert"],
 "correctAnswer":"C",
 "explanation":"'Desert' (one S) is a dry, sandy area. 'Dessert' (two S's) is the sweet course after a meal. Remember: desert has one S like 'sand'."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Action Words",
 "questionText":"Choose the correct spelling of moving through air using wings:",
 "options":["A: fliying","B: flyying","C: flying","D: fleing"],
 "correctAnswer":"C",
 "explanation":"'Flying' is the correct spelling (F-L-Y-I-N-G). When we add '-ing' to 'fly', the Y stays: fly → flying."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Science Words",
 "questionText":"Which spelling is correct for the process by which plants make food using sunlight?",
 "options":["A: photosinthesis","B: photosynthesis","C: fotosynthesis","D: photosinthsis"],
 "correctAnswer":"B",
 "explanation":"'Photosynthesis' is the correct spelling (P-H-O-T-O-S-Y-N-T-H-E-S-I-S). Photo means light; synthesis means making."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Confusing Words",
 "questionText":"Choose the correct spelling of complete control or power over something:",
 "options":["A: autharity","B: authority","C: authourity","D: athority"],
 "correctAnswer":"B",
 "explanation":"'Authority' is the correct spelling (A-U-T-H-O-R-I-T-Y). Authority means the power or right to make decisions."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Homophones",
 "questionText":"Which spelling correctly means 'permitted to'?",
 "options":["A: aloud","B: allowed","C: aload","D: alloued"],
 "correctAnswer":"B",
 "explanation":"'Allowed' means permitted (I am allowed to go). 'Aloud' means out loud (spoken). These are homophones — same sound, different meaning."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Compound Words",
 "questionText":"Choose the correct spelling of a place where books are kept and lent:",
 "options":["A: libary","B: liberry","C: library","D: librery"],
 "correctAnswer":"C",
 "explanation":"'Library' is the correct spelling (L-I-B-R-A-R-Y). A library stores and lends books."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Tricky Spellings",
 "questionText":"Which is the correct spelling for something very funny?",
 "options":["A: hilarious","B: hilarious","C: hilarius","D: hillarious"],
 "correctAnswer":"A",
 "explanation":"'Hilarious' is the correct spelling (H-I-L-A-R-I-O-U-S). Something hilarious is extremely funny."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Science Words",
 "questionText":"Choose the correct spelling of the study of the stars and universe:",
 "options":["A: astronomie","B: asstronomy","C: astronomy","D: astornomy"],
 "correctAnswer":"C",
 "explanation":"'Astronomy' is the correct spelling (A-S-T-R-O-N-O-M-Y). Astronomers study stars, planets, and galaxies."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Tricky Endings",
 "questionText":"Which spelling is correct for a person who wins a competition?",
 "options":["A: champiun","B: champion","C: champeon","D: champoin"],
 "correctAnswer":"B",
 "explanation":"'Champion' is the correct spelling (C-H-A-M-P-I-O-N). A champion is the winner of a competition or contest."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Adjectives",
 "questionText":"Choose the correct spelling of the word meaning very important or essential:",
 "options":["A: necesary","B: necessary","C: neccesary","D: neccessary"],
 "correctAnswer":"B",
 "explanation":"'Necessary' is the correct spelling (N-E-C-E-S-S-A-R-Y). One C, double S. Tip: one Collar, two Socks."},

{"subject":"Spell Bee","grade":3,"difficulty":"Foundation","topic":"Spelling",
 "subTopic":"Countries",
 "questionText":"Which is the correct spelling of the country known as the land of the rising sun?",
 "options":["A: Japen","B: Japon","C: Japan","D: Jappan"],
 "correctAnswer":"C",
 "explanation":"'Japan' is the correct spelling (J-A-P-A-N). Japan is an island nation in East Asia known as the Land of the Rising Sun."},

]

ok = dup = err = 0
for i, q in enumerate(questions, 1):
    try:
        r = insert(conn, q)
        if r == "DUP": dup += 1
        else: ok += 1
        label = q['subject'][:22].ljust(22)
        diff = q['difficulty'][:3].upper()
        print(f"  {r}  Q{i:03d} [{label} G{q['grade']} {diff}] {q['subTopic']}")
    except Exception as e:
        err += 1
        print(f"  ERR Q{i:03d}: {e}")

print(f"\n  Done: {ok} posted, {dup} duplicates, {err} errors  (total={ok+dup+err})")
conn.close()
