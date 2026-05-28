"""
generate_sst_pixabay.py
Real Pixabay photos → Cloudinary → Social Studies questions.

Format: Real photo in questionImage, text A/B/C/D options.
Targets:
  • Grade 10 SST  — monuments, historical events, geography, civics
  • Grades 5–9    — monuments, famous Indians, geography, history
  • Grades 2–4    — national symbols, basic geography

Pixabay key is embedded for convenience; override via PIXABAY_API_KEY env var.
"""

import os, io, json, time, random, sys
import requests
import cloudinary
import cloudinary.uploader

# ── CONFIG ────────────────────────────────────────────────────────────────────
PIXABAY_API_KEY       = os.environ.get("PIXABAY_API_KEY", "56031484-1cf6e0a588c13eebd71681fda")
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"
ADMIN_API_BASE        = os.environ.get("ADMIN_API_BASE",
    "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY         = os.environ.get("ADMIN_API_KEY", "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")

cloudinary.config(cloud_name=CLOUDINARY_CLOUD_NAME,
                  api_key=CLOUDINARY_API_KEY,
                  api_secret=CLOUDINARY_API_SECRET, secure=True)
HEADERS = {"X-Admin-Key": ADMIN_API_KEY}
RUN_ID  = int(time.time())

posted = skipped = failed = 0
local_queue = []

# ── HELPERS ───────────────────────────────────────────────────────────────────

_dl_session = requests.Session()
_dl_session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; OlympiadReady/1.0)"})

def pixabay_fetch(query: str, preferred_idx: int = 0) -> str | None:
    """Search Pixabay, download image bytes locally, upload to Cloudinary, return URL."""
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": 10,
        "order": "popular",
    }
    try:
        r = requests.get("https://pixabay.com/api/", params=params, timeout=12)
        r.raise_for_status()
        hits = r.json().get("hits", [])
    except Exception as e:
        print(f"    [PIXABAY ERR] '{query}': {e}")
        return None

    if not hits:
        print(f"    [NO HITS] '{query}'")
        return None

    # Try hits in order until one downloads successfully
    for hi in range(min(len(hits), 5)):
        hit = hits[(preferred_idx + hi) % len(hits)]
        img_url = hit.get("previewURL") or hit.get("webformatURL")
        if not img_url:
            continue
        try:
            time.sleep(1.5)
            dl = _dl_session.get(img_url, timeout=20)
            dl.raise_for_status()
            img_bytes = dl.content
        except Exception as e:
            print(f"    [DL ERR] hit {hi} '{query}': {e}")
            continue

        pub_id = f"{CLOUDINARY_FOLDER}/sst_{query[:28].replace(' ','-')}_{RUN_ID}_{hit['id']}"
        try:
            time.sleep(1.0)
            res = cloudinary.uploader.upload(
                io.BytesIO(img_bytes), public_id=pub_id,
                overwrite=False, resource_type="image")
            return res["secure_url"]
        except Exception as e:
            print(f"    [CDN ERR] '{query}': {e}")
            continue

    return None


def post_q(grade, diff, subject, topic, subtopic, qtext, img_url, opts, cidx, expl):
    global posted, skipped, failed
    payload = dict(subject=subject, grade=grade, difficulty=diff,
                   topic=topic, subTopic=subtopic,
                   questionText=qtext, imageUrl=img_url,
                   options=opts, correctAnswer=chr(65+cidx), explanation=expl)
    for attempt in range(2):
        try:
            r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                              json=payload, headers=HEADERS, timeout=25)
            if r.status_code in (200, 201): posted += 1; return True
            elif r.status_code == 409:      skipped += 1; return False
            else:
                print(f"    [API {r.status_code}] {r.text[:80]}")
                failed += 1; return False
        except Exception as e:
            if attempt == 0: time.sleep(3)
            else: print(f"    [ERR] {e}"); failed += 1; return False


def run_q(label, query, grade, diff, subject, topic, subtopic, qtext, opts, cidx, expl,
          pixabay_idx=0):
    """Fetch photo from Pixabay then post question."""
    print(f"  {label}...", end=" ", flush=True)
    url = pixabay_fetch(query, pixabay_idx)
    if not url:
        print("-> NO IMAGE, skipping")
        global failed; failed += 1
        return
    ok = post_q(grade, diff, subject, topic, subtopic, qtext, url, opts, cidx, expl)
    print(f"-> {'ok' if ok else 'dup/fail'}")
    time.sleep(2.0)


# ═════════════════════════════════════════════════════════════════════════════
# QUESTION BANK
# Each tuple:
#  (label, pixabay_query, grade, difficulty, subject, topic, subtopic,
#   question_text, [opt_A, opt_B, opt_C, opt_D], correct_idx_0based, explanation)
# ═════════════════════════════════════════════════════════════════════════════

# ── GRADE 10 — HISTORY ────────────────────────────────────────────────────────
GR10_HISTORY = [
    ("G10 Dandi March", "Gandhi salt march Dandi India 1930",
     10, "Olympiad", "Social Studies", "Modern Indian History", "Civil Disobedience",
     "The photograph shows Mahatma Gandhi leading a famous march in 1930. What was the primary significance of this event?",
     ["It broke British salt monopoly and launched Civil Disobedience Movement",
      "It was the first meeting of the Indian National Congress",
      "It led directly to the Quit India Movement of 1942",
      "It was a protest against the Rowlatt Act"],
     0, "The Dandi March (March–April 1930) covered 385 km to the sea where Gandhi made salt, defying British salt laws. It triggered mass Civil Disobedience across India and drew global attention."),

    ("G10 Jallianwala Bagh", "Jallianwala Bagh memorial Amritsar",
     10, "Advanced", "Social Studies", "Modern Indian History", "Freedom Struggle",
     "This memorial in Amritsar marks the site of a 1919 massacre. Which British officer ordered troops to fire on a peaceful gathering here?",
     ["General Reginald Dyer",
      "Lord Curzon",
      "Lord Mountbatten",
      "Winston Churchill"],
     0, "On 13 April 1919, General Dyer ordered troops to fire at an unarmed crowd at Jallianwala Bagh during Baisakhi. ~400 people died. This event turned moderate nationalists into radical independence supporters."),

    ("G10 Quit India", "Quit India movement 1942 India protest",
     10, "Advanced", "Social Studies", "Modern Indian History", "August Movement",
     "The photograph depicts mass protests during the 1942 movement. What was the central slogan of this movement launched by Gandhi?",
     ["Do or Die / Quit India",
      "Jai Hind",
      "Swaraj is my birthright",
      "Inquilab Zindabad"],
     0, "'Do or Die' and 'Quit India' were Gandhi's slogans for the August 1942 movement demanding immediate British withdrawal. The British arrested all Congress leaders within hours, but protests spread across India."),

    ("G10 INC founding", "Indian National Congress Bombay 1885 history",
     10, "Foundation", "Social Studies", "Modern Indian History", "Nationalist Movement",
     "The Indian National Congress was founded in 1885 in Bombay. Who is credited as its founder?",
     ["A.O. Hume (with Dadabhai Naoroji and Dinshaw Wacha)",
      "Bal Gangadhar Tilak",
      "Mahatma Gandhi",
      "Jawaharlal Nehru"],
     0, "A.O. Hume, a retired British civil servant, founded the INC in 1885 along with Dadabhai Naoroji and Dinshaw Wacha. Initially it was a moderate body petitioning for reforms, later transforming into a mass movement."),

    ("G10 Partition 1947", "India Pakistan partition 1947 independence",
     10, "Olympiad", "Social Studies", "Modern Indian History", "Independence and Partition",
     "The Partition of 1947 divided British India into two nations. What was the PRIMARY cause of large-scale violence during Partition?",
     ["Communal riots as 15 million people were displaced across new borders",
      "War between India and Pakistan over Kashmir",
      "British troops attacking civilians as they withdrew",
      "Disagreement over the Constitution between Congress and Muslim League"],
     0, "Partition triggered one of history's largest mass migrations — ~15 million people crossed new borders. Communal violence killed an estimated 200,000–2 million. The violence was driven by communal tensions, not a formal war."),

    ("G10 Non Cooperation", "Gandhi non-cooperation movement India spinning wheel charkha",
     10, "Advanced", "Social Studies", "Modern Indian History", "Non-Cooperation",
     "Gandhi promoted the spinning wheel (charkha) as a symbol of this movement. What was the movement's strategy against British rule?",
     ["Boycott British goods, courts, schools, and return honours — use Indian alternatives",
      "Violent uprising against British military",
      "Petition the British Parliament for dominion status",
      "General strike by industrial workers only"],
     0, "The Non-Cooperation Movement (1920–22) asked Indians to return titles, boycott councils/courts/schools, and use swadeshi goods. The charkha symbolised economic self-reliance. Gandhi suspended it after the Chauri Chaura violence in 1922."),
]

# ── GRADE 10 — GEOGRAPHY ──────────────────────────────────────────────────────
GR10_GEOGRAPHY = [
    ("G10 Western Ghats", "Western Ghats mountain range India Kerala",
     10, "Foundation", "Social Studies", "Indian Geography", "Physical Features",
     "The photograph shows a mountain range covered in dense forests running parallel to India's west coast. This is the:",
     ["Western Ghats — a UNESCO World Heritage biodiversity hotspot",
      "Eastern Ghats — lower, discontinuous range on east coast",
      "Aravalli Range — oldest mountains in northwest India",
      "Nilgiri Hills — part of the Deccan Plateau"],
     0, "Western Ghats (Sahyadri) run ~1,600 km along India's west coast through Maharashtra, Goa, Karnataka, and Kerala. They are a UNESCO World Heritage Site and one of the world's 8 biodiversity hotspots."),

    ("G10 Ganga river Varanasi", "Ganga river Varanasi ghats India",
     10, "Advanced", "Social Studies", "Indian Geography", "Rivers",
     "The photo shows the ghats of a sacred city on the banks of the Ganga. This river is significant because it:",
     ["Drains the most fertile Indo-Gangetic Plain and supports ~40% of India's population",
      "Is the longest river in India, flowing into the Arabian Sea",
      "Originates in the Eastern Ghats and flows westward",
      "Forms India's eastern boundary with Bangladesh"],
     0, "The Ganga drains the vast Indo-Gangetic Plain — home to ~43% of India's population. It originates at Gangotri glacier and flows 2,525 km to the Bay of Bengal forming the Sundarbans delta."),

    ("G10 Thar Desert", "Thar desert Rajasthan sand dunes India",
     10, "Foundation", "Social Studies", "Indian Geography", "Natural Regions",
     "The photograph shows a vast sandy desert in northwestern India. This is:",
     ["The Thar Desert — India's largest hot desert in Rajasthan",
      "The Deccan Plateau — flat-topped tableland in peninsular India",
      "The Rann of Kutch — seasonal salt marsh in Gujarat",
      "The Ladakh Desert — cold desert in northern India"],
     0, "The Thar (Great Indian Desert) covers ~200,000 sq km in Rajasthan. It receives <150 mm rainfall annually and has extreme temperatures. The Aravalli Range to its east blocks moisture from reaching it."),

    ("G10 Sundarbans delta", "Sundarbans mangrove forest Bengal tiger India",
     10, "Olympiad", "Social Studies", "Indian Geography", "Natural Vegetation",
     "This mangrove forest in the Ganga-Brahmaputra delta is home to the Bengal Tiger. Which of the following BEST explains why mangroves grow specifically in delta regions?",
     ["They are salt-tolerant and adapted to tidal, waterlogged, brackish coastal zones",
      "They need very low rainfall and dry soil",
      "They grow only in freshwater lakes and river banks",
      "They are planted by the government as windbreaks"],
     0, "Mangroves are uniquely adapted to tidal saltwater/brackish conditions — they have aerial roots (pneumatophores) for oxygen and salt-filtering mechanisms. Deltas provide exactly these waterlogged, brackish tidal conditions."),

    ("G10 coal mine India", "coal mine Jharkhand India mining",
     10, "Advanced", "Social Studies", "Indian Geography", "Minerals and Energy",
     "The photograph shows a coal mine in Jharkhand. India's coal reserves are concentrated in the:",
     ["Damodar Valley (Jharkhand-WB) and Mahanadi Valley (Chhattisgarh-Odisha)",
      "Indo-Gangetic Plains of UP and Bihar",
      "Deccan Plateau of Maharashtra and Karnataka",
      "Himalayan foothills of Uttarakhand"],
     0, "About 80% of India's coal comes from the Gondwana coalfields in the Damodar Valley (Jharkhand, WB) and Mahanadi/Son/Wardha valleys (Chhattisgarh, Odisha, MP). Jharkhand alone has ~26% of India's reserves."),

    ("G10 India map agriculture", "wheat fields Punjab India agriculture",
     10, "Foundation", "Social Studies", "Indian Geography", "Agriculture",
     "The photograph shows vast wheat fields. Punjab and Haryana are called the 'wheat bowl' of India because:",
     ["They have flat fertile alluvial soil, canal irrigation, and suitable cool winters for wheat",
      "They receive the highest rainfall in India from the Bay of Bengal",
      "They are located near the Equator, giving year-round warmth",
      "The government bans rice cultivation there to promote wheat"],
     0, "Punjab/Haryana's flat alluvial plains, extensive canal irrigation (Bhakra Nangal), cool winters (wheat needs vernalisation), and Green Revolution technology make them produce ~50% of India's wheat procurement."),
]

# ── GRADE 10 — CIVICS & ECONOMICS ─────────────────────────────────────────────
GR10_CIVICS = [
    ("G10 Parliament India", "Indian Parliament building New Delhi Sansad Bhavan",
     10, "Foundation", "Social Studies", "Indian Civics", "Government Structure",
     "This is the Parliament House of India in New Delhi. India's Parliament consists of:",
     ["Lok Sabha (lower house) + Rajya Sabha (upper house) + President",
      "Only Lok Sabha — the elected house",
      "Lok Sabha + Rajya Sabha + Supreme Court",
      "Prime Minister's Office + Cabinet + President"],
     0, "India's Parliament = President + Lok Sabha (545 seats, directly elected, 5-year term) + Rajya Sabha (245 seats, indirectly elected, 6-year staggered terms). The President is a formal part but does not sit in Parliament."),

    ("G10 Supreme Court India", "Supreme Court India New Delhi building",
     10, "Advanced", "Social Studies", "Indian Civics", "Judiciary",
     "The photograph shows India's Supreme Court. Which of the following powers does the Supreme Court have that makes it unique?",
     ["Original, appellate, and advisory jurisdiction — plus power to issue writs for fundamental rights",
      "Power to dissolve Parliament if laws are unjust",
      "Power to remove the Prime Minister from office",
      "Power to declare war on behalf of India"],
     0, "The Supreme Court has: (1) Original jurisdiction in disputes between states/Union, (2) Appellate jurisdiction, (3) Advisory jurisdiction (President can seek opinion), (4) Writ jurisdiction under Art. 32 to protect Fundamental Rights. This makes it the guardian of the Constitution."),

    ("G10 Rashtrapati Bhavan", "Rashtrapati Bhavan Presidential palace New Delhi India",
     10, "Foundation", "Social Studies", "Indian Civics", "Government",
     "This is Rashtrapati Bhavan, the official residence of India's President. The President of India is:",
     ["The constitutional head — elected by an electoral college of elected MPs and MLAs",
      "Directly elected by all citizens of India",
      "Appointed by the Prime Minister",
      "The real head of government who makes policy decisions"],
     0, "The President is the constitutional (nominal) head elected by elected MPs + MLAs. The Prime Minister is the real executive. The President acts on the advice of the Council of Ministers (Art. 74)."),

    ("G10 Indian currency Rupee", "Indian rupee notes currency money",
     10, "Advanced", "Social Studies", "Economics Basics", "Money and Credit",
     "The photograph shows Indian Rupee notes. In India's formal banking system, which institution has the sole right to issue currency?",
     ["Reserve Bank of India (RBI)",
      "State Bank of India (SBI)",
      "Ministry of Finance",
      "SEBI (Securities and Exchange Board)"],
     0, "The RBI (Reserve Bank of India), established 1935, is India's central bank. Only the RBI can issue currency notes. It regulates money supply, credit, and the banking sector."),

    ("G10 factory workers India", "Indian factory workers manufacturing industry",
     10, "Olympiad", "Social Studies", "Economics Basics", "Sectors of Economy",
     "The photograph shows workers in a manufacturing factory — part of which sector of the economy?",
     ["Secondary sector — transforms raw materials into finished goods",
      "Primary sector — directly extracts from nature",
      "Tertiary sector — provides services",
      "Quaternary sector — knowledge and information"],
     0, "The three-sector model: Primary (agriculture, mining — extract from nature), Secondary (manufacturing, construction — transform materials), Tertiary (banking, transport, trade — provide services). A factory = secondary sector."),
]

# ── GRADE 9 ───────────────────────────────────────────────────────────────────
GR9_SST = [
    ("G9 French Revolution Bastille", "Bastille storming French Revolution 1789",
     9, "Advanced", "Social Studies", "Modern Indian History", "French Revolution",
     "This painting depicts the storming of the Bastille in 1789 — the start of the French Revolution. What did the fall of Bastille symbolise?",
     ["The end of royal tyranny and rise of popular sovereignty",
      "The beginning of Napoleon's military campaigns",
      "The signing of the French Constitution",
      "The formation of the Third Estate parliament"],
     0, "The Bastille was a royal prison symbolising despotic royal power. Its fall on 14 July 1789 marked the people's victory over the monarchy. Today 14 July is France's national day (Bastille Day)."),

    ("G9 Himalayas mountains", "Himalayas snow peaks India Nepal mountain range",
     9, "Foundation", "Social Studies", "Indian Geography", "Physical Features",
     "The photograph shows snow-capped Himalayan peaks. The Himalayas are important for India because they:",
     ["Block cold winds from Central Asia, force monsoon rains, and are the source of perennial rivers",
      "Are the oldest mountain range in India",
      "Form India's eastern border with Myanmar",
      "Were formed by volcanic activity"],
     0, "The Himalayas: (1) Act as a climatic barrier — block freezing Central Asian winds (keeping winters milder), (2) Force SW Monsoon to rise and rain heavily, (3) Feed perennial rivers like Ganga, Indus, Brahmaputra from glaciers."),

    ("G9 Drought India farmer", "Indian farmer drought dry land cracked soil",
     9, "Olympiad", "Social Studies", "Economics Basics", "Poverty",
     "The photograph shows cracked, drought-hit farmland. Rural poverty in India is closely linked to agriculture because:",
     ["70% of rural households depend on farming; crop failure means income collapse with no social safety net",
      "Only rich farmers own land; poor farmers work in cities",
      "The government has banned small farmers from selling crops",
      "Rural areas have more factories than farms"],
     0, "India's rural poor are mostly marginal/small farmers or landless labourers. A drought means zero income, debt trap (moneylender loans at 30-40% interest), and hunger. MGNREGA and crop insurance schemes try to address this vulnerability."),

    ("G9 Nazi Germany", "Berlin Wall Nazi Germany World War 2 history",
     9, "Advanced", "Social Studies", "Modern Indian History", "World Wars",
     "The photograph relates to Nazi Germany. Hitler rose to power by exploiting Germany's post-WWI conditions. Which treaty imposed harsh penalties on Germany, creating resentment that Hitler exploited?",
     ["Treaty of Versailles (1919) — imposed war guilt, reparations, and territorial losses",
      "Treaty of Westphalia (1648)",
      "Congress of Vienna (1815)",
      "Treaty of Versailles (1918) — ended the war immediately"],
     0, "The Treaty of Versailles blamed Germany for WWI ('war guilt clause'), demanded ₹6 billion in reparations, stripped territories, and banned a large German army. This humiliation and economic misery created fertile ground for Hitler's nationalist extremism."),

    ("G9 coastal erosion India", "Arabian Sea coastline India beach waves",
     9, "Advanced", "Social Studies", "Indian Geography", "Coastal Plains",
     "The photograph shows India's western coastline. The Western Coastal Plain differs from the Eastern Coastal Plain because:",
     ["Western coast is narrow and has natural harbours; Eastern coast is broader with large river deltas",
      "Western coast has deltas; Eastern coast has estuaries",
      "Eastern coast borders the Arabian Sea; Western coast borders the Bay of Bengal",
      "Western coast receives no monsoon rainfall"],
     0, "Western Coastal Plain: narrow (10-25 km), rocky with natural harbours (Mumbai, Kochi), sea-drowned river mouths = estuaries. Eastern Coastal Plain: wider (100-120 km), rivers form large fertile deltas (Mahanadi, Krishna, Godavari, Kaveri)."),
]

# ── GRADE 8 ───────────────────────────────────────────────────────────────────
GR8_SST = [
    ("G8 crop field India", "rice paddy field India green harvest",
     8, "Foundation", "Social Studies", "Indian Geography", "Agriculture",
     "The photograph shows a rice paddy field. Rice is grown mainly in India's coastal and eastern regions because:",
     ["It needs heavy rainfall (>150 cm) or irrigation, and high temperatures year-round",
      "It grows only in cold mountainous regions",
      "It needs very dry, sandy soil",
      "It is grown only in Punjab and Haryana"],
     0, "Rice requires standing water during growth (hence paddy fields), high temperatures (25°C+), and heavy rain or canal irrigation. West Bengal, Odisha, Andhra Pradesh, and Tamil Nadu are top producers."),

    ("G8 Andaman Islands India", "Andaman Nicobar Islands India tropical forest beach",
     8, "Advanced", "Social Studies", "Indian Geography", "Islands",
     "The photo shows the lush tropical islands of the Andaman & Nicobar group. These islands are significant because they:",
     ["Mark India's easternmost point and have strategic location in the Indian Ocean",
      "Are part of the Western Ghats",
      "Form India's southernmost mainland boundary",
      "Are located in the Arabian Sea"],
     0, "A&N Islands (Bay of Bengal) contain India's easternmost point — Indira Point (Car Nicobar). They are strategically important, controlling Indian Ocean sea lanes. The indigenous Sentinelese tribe here is one of the world's most isolated peoples."),

    ("G8 Mughal architecture", "Mughal architecture Agra Fort red sandstone India",
     8, "Foundation", "Social Studies", "Medieval Indian History", "Mughal Empire",
     "The photograph shows magnificent Mughal architecture in red sandstone. The Mughals were known for blending which two architectural styles?",
     ["Persian-Islamic and Indian (Hindu) architectural traditions",
      "Greek and Roman classical styles",
      "British colonial and Rajput styles",
      "Buddhist and Jain temple styles"],
     0, "Mughal architecture blended Persian domes and arches with Indian elements like chhatris, jaalis (lattice screens), and temple-style brackets. Akbar's Fatehpur Sikri shows this Indo-Islamic fusion most clearly."),

    ("G8 British India Railway", "British era railway station India colonial heritage",
     8, "Olympiad", "Social Studies", "Modern Indian History", "British Colonial Period",
     "The British built railways in India primarily to:",
     ["Transport raw materials from interior to ports for export, and troops for control — not for Indian welfare",
      "Help Indian farmers reach markets quickly",
      "Promote tourism between Indian cities",
      "Connect pilgrimage sites for Hindu and Muslim travellers"],
     0, "Railway construction served British economic and military interests: move raw materials (cotton, jute, coal) to ports for export to Britain, deploy troops rapidly to suppress uprisings. Dadabhai Naoroji's 'Drain of Wealth' highlighted how this infrastructure exploited India."),
]

# ── GRADE 7 ───────────────────────────────────────────────────────────────────
GR7_SST = [
    ("G7 Taj Mahal", "Taj Mahal Agra India white marble",
     7, "Foundation", "Social Studies", "Medieval Indian History", "Mughal Empire",
     "The photograph shows one of the world's most famous monuments in Agra, India. Who built the Taj Mahal and why?",
     ["Shah Jahan built it as a mausoleum for his wife Mumtaz Mahal who died in 1631",
      "Akbar built it to celebrate victory over Rajputs",
      "Aurangzeb built it as a mosque",
      "Babur built it after the First Battle of Panipat"],
     0, "Shah Jahan (5th Mughal emperor) built the Taj Mahal (1632–1653) in memory of his favourite wife Mumtaz Mahal. It took 22 years and 20,000 workers. It is a UNESCO World Heritage Site and a symbol of love."),

    ("G7 Amazon rainforest", "Amazon rainforest tropical Brazil river",
     7, "Foundation", "Social Studies", "World Geography", "Natural Vegetation",
     "The photograph shows the Amazon rainforest in South America. What makes tropical rainforests so biologically diverse?",
     ["Year-round high temperature and heavy rainfall create ideal conditions for millions of species",
      "Cold temperatures preserve species like a freezer",
      "Absence of sunlight allows unique nocturnal species",
      "Rainforests are artificially maintained by governments"],
     0, "Tropical rainforests near the equator have consistent warmth (25–30°C) and 200–400 cm of rainfall annually. This stable, resource-rich environment has driven evolution of extraordinary biodiversity — the Amazon holds ~10% of all Earth's species."),

    ("G7 Sahara desert", "Sahara desert sand dunes Africa camel",
     7, "Foundation", "Social Studies", "World Geography", "Deserts",
     "The photograph shows the Sahara Desert in Africa — the world's largest hot desert. Desert regions receive very little rainfall because:",
     ["They lie in subtropical high-pressure zones where air sinks, warms, and absorbs moisture rather than releasing it",
      "They are too far from the equator to receive sunlight",
      "Deserts are always at high altitude where clouds cannot form",
      "Desert soil absorbs all rainfall instantly"],
     0, "Deserts (20-30° N/S latitude) lie in subtropical high-pressure belts. Here, air descends from high altitude, compresses, and warms — creating dry conditions where evaporation exceeds precipitation. This explains why the Sahara, Thar, and Arabian deserts are all around 20-30° latitude."),

    ("G7 Hampi ruins Karnataka", "Hampi ruins stone chariot Karnataka India UNESCO",
     7, "Advanced", "Social Studies", "Ancient Indian History", "Vijayanagara Empire",
     "The photograph shows the famous stone chariot at Hampi, Karnataka — the capital of which empire?",
     ["Vijayanagara Empire (1336–1646 CE)",
      "Maurya Empire",
      "Mughal Empire",
      "Chola Empire"],
     0, "Hampi was the capital of the Vijayanagara Empire, founded by Harihara and Bukka in 1336. At its peak under Krishna Deva Raya, it was one of the world's largest and wealthiest cities. It was destroyed in 1565 after the Battle of Talikota."),
]

# ── GRADES 5–6 ────────────────────────────────────────────────────────────────
GR56_SST = [
    ("G5 Ganga river", "Ganga river India sacred river Haridwar Rishikesh",
     5, "Foundation", "Social Studies", "Indian Geography", "Rivers",
     "The photograph shows the Ganga river at Haridwar. The Ganga is important for India because:",
     ["It is the most sacred river and supports agriculture for millions along its banks",
      "It forms India's western border",
      "It originates in South India and flows northward",
      "It is the longest river in the world"],
     0, "The Ganga (2,525 km) originates at Gangotri glacier in Uttarakhand. It is India's holiest river and flows through UP, Bihar, WB to the Bay of Bengal. The Ganga basin supports ~430 million people."),

    ("G5 Indian village farming", "Indian village farmer bullock cart agriculture",
     5, "Foundation", "Social Studies", "Indian Geography", "Occupation",
     "The photograph shows Indian village life. About what percentage of India's population lives in rural areas (villages)?",
     ["About 65% (nearly 2 out of 3 Indians live in villages)",
      "About 20%",
      "About 90%",
      "About 45%"],
     0, "According to Census 2011, about 69% of India's population is rural. Most rural people depend on farming, animal husbandry, or small-scale crafts for their livelihood."),

    ("G5 Himalaya trek snow", "Himalaya mountains trekking snow India",
     5, "Advanced", "Social Studies", "Indian Geography", "Mountains",
     "The photograph shows the snow-covered Himalayas. Which is the TALLEST peak in the Himalayas?",
     ["Mount Everest (8,848 m) — on the Nepal-China border",
      "K2 (8,611 m) — in Ladakh, India",
      "Kangchenjunga (8,586 m) — on India-Nepal border",
      "Nanda Devi (7,816 m) — in Uttarakhand, India"],
     0, "Mount Everest (8,848 m) is the world's highest peak, on the Nepal-China border. The highest peak in India is Kangchenjunga (8,586 m) on the India-Nepal border. K2 is in Pakistan-controlled territory."),

    ("G6 Red Fort Delhi", "Red Fort Lal Qila Delhi India",
     6, "Foundation", "Social Studies", "Medieval Indian History", "Mughal Monuments",
     "The photograph shows the Red Fort (Lal Qila) in Delhi. Which Mughal emperor built it and what is its significance today?",
     ["Shah Jahan built it in 1639; PM hoists the national flag here on Independence Day",
      "Akbar built it in 1556 as his main palace",
      "Humayun built it after returning from exile",
      "Aurangzeb built it after defeating his brothers"],
     0, "Shah Jahan built the Red Fort (1638–48) as the main palace of Shahjahanabad (Delhi). Every year on 15 August, India's Prime Minister hoists the national flag and addresses the nation from its ramparts."),

    ("G6 Konark Sun Temple", "Konark Sun Temple Odisha chariot India UNESCO",
     6, "Advanced", "Social Studies", "Ancient Indian History", "Temple Architecture",
     "The photograph shows the Konark Sun Temple in Odisha, shaped like a massive chariot. It was built by which dynasty?",
     ["Eastern Ganga dynasty — King Narasimhadeva I (13th century CE)",
      "Maurya dynasty under Ashoka",
      "Chola dynasty of Tamil Nadu",
      "Mughal emperor Akbar"],
     0, "The Konark Sun Temple was built c.1250 CE by King Narasimhadeva I of the Eastern Ganga dynasty. It is designed as a 24-wheeled chariot for the Sun God Surya. It is a UNESCO World Heritage Site."),

    ("G6 Parliament India", "Parliament House India New Delhi dome circular",
     6, "Foundation", "Social Studies", "Indian Civics", "Government",
     "The photograph shows the Parliament of India. Who has the power to make laws for the entire country?",
     ["Parliament (Lok Sabha + Rajya Sabha) — the national legislature",
      "The President alone",
      "The Prime Minister alone",
      "Each State Government independently"],
     0, "India's Parliament (Article 79) consists of the President and two houses — Lok Sabha and Rajya Sabha. Parliament alone can make laws on subjects in the Union List and Concurrent List for the whole country."),
]

# ── GRADES 2–4 — National Symbols & Geography basics ─────────────────────────
GR234_SST = [
    ("G4 Taj Mahal basic", "Taj Mahal India white building beautiful",
     4, "Foundation", "Social Studies", "Culture and Heritage", "Monuments",
     "The photograph shows a famous white monument in India. What is this called?",
     ["Taj Mahal — in Agra, Uttar Pradesh",
      "Red Fort — in Delhi",
      "Qutub Minar — in Delhi",
      "Charminar — in Hyderabad"],
     0, "The Taj Mahal is in Agra (UP). It was built by Mughal Emperor Shah Jahan in memory of his wife Mumtaz Mahal. It is one of the Seven Wonders of the World."),

    ("G4 Indian flag", "Indian flag tricolour flying independence",
     4, "Foundation", "Social Studies", "Indian Civics", "National Symbols",
     "The photograph shows India's national flag. The three colours of the Indian flag stand for:",
     ["Saffron = courage/sacrifice, White = peace/truth, Green = prosperity/faith",
      "Saffron = Hinduism, White = Christianity, Green = Islam",
      "Saffron = the sun, White = snow, Green = forests",
      "All three colours represent different states of India"],
     0, "The Indian national flag: Saffron (top) = courage and sacrifice; White (middle) = peace and truth, with the blue Ashoka Chakra (24 spokes = 24 hours, progress); Green (bottom) = faith and fertility of the land."),

    ("G3 peacock bird India", "Indian peacock bird national bird colorful feathers",
     3, "Foundation", "Social Studies", "Indian Civics", "National Symbols",
     "The photograph shows a beautiful bird with colourful feathers. This is India's national bird. What is it called?",
     ["Peacock (Mayur)",
      "Eagle (Garuda)",
      "Parrot (Tota)",
      "Crane (Saras)"],
     0, "The Indian Peacock (Pavo cristatus) is India's national bird. The male peacock has spectacular colourful feathers. It is found throughout India and is protected under the Wildlife Protection Act."),

    ("G3 Bengal tiger", "Bengal tiger India wildlife national animal",
     3, "Foundation", "Social Studies", "Indian Civics", "National Symbols",
     "The photograph shows a large striped wild cat — India's national animal. What is it?",
     ["Bengal Tiger — protected under Project Tiger since 1973",
      "Asiatic Lion — found in Gir Forest, Gujarat",
      "Indian Leopard — found across India",
      "Snow Leopard — found in Himalayan regions"],
     0, "The Bengal Tiger is India's national animal. Project Tiger (1973) was launched to protect it from extinction. Today India has ~3,000 tigers — about 70% of the world's wild tiger population."),

    ("G2 Indian school children", "Indian school children uniform classroom happy",
     2, "Foundation", "Social Studies", "Indian Civics", "Rights",
     "The photograph shows Indian school children. Every child in India has the right to free education up to age:",
     ["14 years (Article 21A — Right to Education)",
      "10 years",
      "18 years",
      "6 years only"],
     0, "Article 21A (added by 86th Amendment, 2002) makes education a Fundamental Right for all children aged 6–14. The Right to Education Act (2009) makes it compulsory and free in government schools."),

    ("G2 Indian village well water", "Indian village water well rural pump hand pump",
     2, "Foundation", "Social Studies", "Indian Geography", "Water",
     "The photograph shows people getting water from a well in a village. Why is water important for life?",
     ["All living things need water to survive — for drinking, farming, cooking, and cleaning",
      "Water is only used for farming, not for drinking",
      "Only plants need water; animals can survive without it",
      "Water is important only in deserts"],
     0, "Water is essential for all life — humans need it for drinking (we are 70% water), plants need it for photosynthesis, and farmers need it for crops. Access to clean water is a basic human need and right."),
]

# ─────────────────────────────────────────────────────────────────────────────
ALL_QUESTIONS = (
    GR10_HISTORY + GR10_GEOGRAPHY + GR10_CIVICS +
    GR9_SST + GR8_SST + GR7_SST + GR56_SST + GR234_SST
)

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("OlympiadReady — Social Studies Pixabay (Real Photos)")
    print(f"Total questions to process: {len(ALL_QUESTIONS)}")
    print("=" * 65)

    sections = {
        "Grade 10 — History":   GR10_HISTORY,
        "Grade 10 — Geography": GR10_GEOGRAPHY,
        "Grade 10 — Civics":    GR10_CIVICS,
        "Grade 9":              GR9_SST,
        "Grade 8":              GR8_SST,
        "Grade 7":              GR7_SST,
        "Grades 5–6":           GR56_SST,
        "Grades 2–4":           GR234_SST,
    }

    for section, qs in sections.items():
        print(f"\n[{section}]")
        for row in qs:
            label, query, grade, diff, subj, topic, subtopic, qtext, opts, cidx, expl = row
            run_q(label, query, grade, diff, subj, topic, subtopic, qtext, opts, cidx, expl)

    total = posted + skipped + failed
    print(f"\n{'='*65}")
    print(f"DONE — Posted: {posted}  Skipped(dup): {skipped}  Failed: {failed}  Total: {total}")
    print(f"{'='*65}")
