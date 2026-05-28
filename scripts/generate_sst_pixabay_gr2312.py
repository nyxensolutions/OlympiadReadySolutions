"""
generate_sst_pixabay_gr2312.py
Real Pixabay photos -> Cloudinary -> Social Studies image questions
Targets: Grade 2, Grade 3, Grade 12 SST (all had 0 images)
"""

import os, io, time, requests
import cloudinary, cloudinary.uploader

PIXABAY_API_KEY       = os.environ.get("PIXABAY_API_KEY", "56031484-1cf6e0a588c13eebd71681fda")
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

def pixabay_fetch(query: str, idx: int = 0) -> str | None:
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
        pub_id = f"{CLOUDINARY_FOLDER}/sst2_{query[:28].replace(' ','-')}_{RUN_ID}_{hit['id']}"
        try:
            time.sleep(1.0)
            res = cloudinary.uploader.upload(io.BytesIO(dl.content), public_id=pub_id,
                                             overwrite=False, resource_type="image")
            return res["secure_url"]
        except Exception as e:
            print(f"    [CDN ERR] '{query}': {e}"); continue
    return None

def post_q(grade, diff, subject, topic, subtopic, qtext, img_url, opts, cidx, expl):
    global posted, skipped, failed
    payload = dict(subject=subject, grade=grade, difficulty=diff,
                   topic=topic, subTopic=subtopic, questionText=qtext,
                   imageUrl=img_url, options=opts, correctAnswer=chr(65+cidx), explanation=expl)
    for attempt in range(2):
        try:
            r = requests.post(f"{ADMIN_API_BASE}/api/admin/add-question",
                              json=payload, headers=HEADERS, timeout=25)
            if r.status_code in (200, 201): posted += 1; return True
            elif r.status_code == 409:      skipped += 1; return False
            else: print(f"    [API {r.status_code}] {r.text[:80]}"); failed += 1; return False
        except Exception as e:
            if attempt == 0: time.sleep(3)
            else: print(f"    [ERR] {e}"); failed += 1; return False

def run_q(label, query, grade, diff, subject, topic, subtopic, qtext, opts, cidx, expl, idx=0):
    global failed
    print(f"  {label}...", end=" ", flush=True)
    url = pixabay_fetch(query, idx)
    if not url:
        print("-> NO IMAGE, skipping"); failed += 1; return
    ok = post_q(grade, diff, subject, topic, subtopic, qtext, url, opts, cidx, expl)
    print(f"-> {'ok' if ok else 'dup/fail'}")
    time.sleep(2.0)

def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")

# =============================================================================
# GRADE 2 SST — Foundation/Advanced (simple, visual, age-appropriate)
# =============================================================================
GR2_SST = [
    ("G2 Indian flag tricolour",
     "Indian flag tricolour saffron white green",
     2, "Foundation", "Social Studies", "Our Country", "National Symbols",
     "Look at the image of the Indian flag. What are the three colours on our national flag, from top to bottom?",
     ["Saffron, White, Green", "Green, White, Saffron", "Blue, White, Orange", "Red, White, Blue"], 0,
     "The Indian national flag (Tiranga) has three horizontal bands: Saffron (top) representing courage, White (middle) with Ashoka Chakra representing peace, and Green (bottom) representing prosperity."),

    ("G2 Indian map outline",
     "India map outline geography country",
     2, "Foundation", "Social Studies", "Our Country", "Maps & Geography",
     "The image shows the map of India. India is shaped somewhat like a:",
     ["Triangle pointing downward (south)", "Circle", "Rectangle", "Square"], 0,
     "India's landmass is roughly triangular, wider in the north and tapering to a point at Cape Comorin (Kanyakumari) in the south."),

    ("G2 Peacock national bird",
     "peacock bird India colourful feathers",
     2, "Foundation", "Social Studies", "Our Country", "National Symbols",
     "The image shows a beautiful bird with colourful feathers. This is India's national bird. What is it called?",
     ["Peacock", "Parrot", "Sparrow", "Eagle"], 0,
     "The Peacock (Pavo cristatus) is India's national bird, declared so in 1963. It is known for its spectacular iridescent tail feathers called a 'train'."),

    ("G2 Indian village house",
     "Indian village rural house mud thatched",
     2, "Foundation", "Social Studies", "Our Community", "Rural Life",
     "The image shows a typical Indian village home. What material is commonly used to make the roof of traditional village houses?",
     ["Thatch (dried grass or straw)", "Concrete", "Glass", "Metal sheets"], 0,
     "Traditional village houses in India often have thatched roofs made from dried grass, straw, or palm leaves — these materials are locally available, cheap, and keep the inside cool."),

    ("G2 School classroom India",
     "Indian school classroom children learning",
     2, "Foundation", "Social Studies", "Our Community", "School & Education",
     "The image shows children in a school classroom. School is important because it helps children:",
     ["Learn to read, write and gain knowledge", "Only play games", "Only make friends", "Watch television"], 0,
     "School provides education — children learn to read, write, do mathematics, and understand the world around them, preparing them for future life."),

    ("G2 Indian market bazaar",
     "Indian market bazaar vegetables fruits colourful",
     2, "Foundation", "Social Studies", "Our Community", "Markets & Trade",
     "The image shows an Indian market (bazaar). People go to a market to:",
     ["Buy and sell goods like vegetables, fruits and clothes", "Only watch others shop", "Play games", "Study books"], 0,
     "A market is a place where buyers and sellers meet to exchange goods and services. People buy food, clothes, and other items they need."),

    ("G2 Water cycle rain cloud",
     "rain clouds water cycle nature India",
     2, "Foundation", "Social Studies", "Our Environment", "Weather & Water",
     "The image shows dark clouds and rain. Rain is important for us because:",
     ["It fills rivers, lakes and helps plants grow", "It only makes puddles", "It causes floods always", "It is not useful for us"], 0,
     "Rain is essential — it fills rivers and lakes (our water sources), recharges groundwater, and provides water for crops and plants to grow."),

    ("G2 Indian family joint family",
     "Indian family together happy home",
     2, "Foundation", "Social Studies", "Our Family", "Family & Relationships",
     "The image shows a family. A family where grandparents, parents, and children all live together is called a:",
     ["Joint family", "Nuclear family", "Single family", "School family"], 0,
     "A joint family has grandparents, parents, children, and sometimes aunts/uncles/cousins all living together. A nuclear family has only parents and their children."),

    ("G2 Traffic signal road safety",
     "traffic signal red green yellow road safety India",
     2, "Foundation", "Social Studies", "Our Community", "Safety & Rules",
     "The image shows a traffic signal. What should you do when the traffic light shows RED?",
     ["STOP and wait", "Walk quickly across", "Speed up", "Ignore it"], 0,
     "Red = STOP. Amber/Yellow = GET READY. Green = GO. Traffic signals keep roads safe by managing the flow of vehicles and pedestrians."),

    ("G2 Indian post office letter",
     "post office letter stamp India",
     2, "Foundation", "Social Studies", "Our Community", "Communication",
     "The image shows a post office. Before mobile phones and email, people used the post office mainly to:",
     ["Send letters and parcels to people far away", "Buy food and groceries", "Watch movies", "Play games"], 0,
     "Post offices handle physical mail — letters, postcards, parcels. They connect people across distances. India Post is one of the world's largest postal networks."),

    ("G2 Farmer paddy field",
     "Indian farmer paddy rice field cultivation",
     2, "Foundation", "Social Studies", "Our Community", "Farmers & Food",
     "The image shows a farmer working in a paddy field. Paddy fields are used to grow:",
     ["Rice", "Wheat", "Maize", "Sugarcane"], 0,
     "Paddy = unhusked rice growing in flooded fields. India is one of the world's largest rice producers. Rice is a staple food for most of India, especially the south and east."),

    ("G2 Hospital doctor patient",
     "hospital doctor patient India healthcare",
     2, "Foundation", "Social Studies", "Our Community", "Community Helpers",
     "The image shows a doctor at a hospital. Doctors help us by:",
     ["Treating illness and helping us stay healthy", "Teaching us in school", "Growing our food", "Building our houses"], 0,
     "Doctors are community helpers who diagnose and treat illness. Hospitals have doctors, nurses, and equipment to help sick people recover."),
]

# =============================================================================
# GRADE 3 SST — Foundation/Advanced
# =============================================================================
GR3_SST = [
    ("G3 Taj Mahal Agra",
     "Taj Mahal Agra India white marble",
     3, "Advanced", "Social Studies", "Our Heritage", "Famous Monuments",
     "The image shows a famous white marble monument in India. Where is the Taj Mahal located?",
     ["Agra, Uttar Pradesh", "Delhi", "Mumbai", "Jaipur"], 0,
     "The Taj Mahal is located in Agra, Uttar Pradesh. Built by Mughal emperor Shah Jahan in memory of his wife Mumtaz Mahal, it is a UNESCO World Heritage Site."),

    ("G3 India river Ganga",
     "Ganga river India holy sacred water",
     3, "Advanced", "Social Studies", "Our Geography", "Rivers of India",
     "The image shows India's most sacred river. Which river is considered the holiest in India and is called 'Ganga Maiya' (Mother Ganga)?",
     ["The Ganga (Ganges)", "The Yamuna", "The Godavari", "The Krishna"], 0,
     "The Ganga originates at Gangotri glacier in the Himalayas and flows about 2,525 km to the Bay of Bengal. It is sacred to Hindus and supports millions of people along its banks."),

    ("G3 Indian village well water pump",
     "Indian village well water hand pump rural",
     3, "Foundation", "Social Studies", "Our Environment", "Water Sources",
     "The image shows people collecting water from a village well. In many Indian villages, people get drinking water from:",
     ["Wells and hand pumps", "Ocean and sea", "Factories", "Only rivers"], 0,
     "In rural India, wells and hand pumps are common water sources. Groundwater is accessed through these. Many government schemes now provide piped water to villages."),

    ("G3 Desert camel Rajasthan",
     "Rajasthan desert camel sand dunes India",
     3, "Advanced", "Social Studies", "Our Geography", "Landforms",
     "The image shows a camel in a sandy desert. The largest desert in India is located in which state?",
     ["Rajasthan (Thar Desert)", "Gujarat", "Madhya Pradesh", "Punjab"], 0,
     "The Thar Desert (Great Indian Desert) covers much of western Rajasthan and some parts of Gujarat. It is the world's 17th largest desert."),

    ("G3 Mountain Himalayas snow",
     "Himalaya mountains snow peaks India",
     3, "Advanced", "Social Studies", "Our Geography", "Landforms",
     "The image shows snow-covered mountain peaks. The Himalayas are important for India because:",
     ["They protect India from cold Arctic winds and are the source of major rivers", "They are only used for tourism", "They have no effect on India's climate", "They cause floods every year"], 0,
     "The Himalayas act as a natural barrier against cold winds from Central Asia, influence monsoon rainfall, and are the source of major rivers like the Ganga, Brahmaputra, and Yamuna."),

    ("G3 Indian Independence Day flag hoisting",
     "India Independence Day flag hoisting celebration",
     3, "Advanced", "Social Studies", "Our History", "National Days",
     "The image shows flag hoisting on a national day. India celebrates Independence Day on August 15 because on this day in 1947:",
     ["India became free from British rule", "India became a Republic", "India won a war", "The Constitution was adopted"], 0,
     "India gained independence from British colonial rule on 15 August 1947. Republic Day (26 January) marks when India's Constitution came into force in 1950."),

    ("G3 Indian spices market",
     "Indian spices colourful market turmeric chilli",
     3, "Foundation", "Social Studies", "Our Community", "Trade & Resources",
     "The image shows colourful Indian spices at a market. India is famous for spices like turmeric, pepper, and cardamom. These spices grow best in which type of climate?",
     ["Warm and humid tropical climate", "Cold and snowy climate", "Very dry desert climate", "Arctic climate"], 0,
     "Most Indian spices (pepper, cardamom, turmeric, ginger) grow in warm, humid tropical regions — particularly Kerala, Karnataka, and Tamil Nadu are major spice-growing states."),

    ("G3 Indian railway train",
     "Indian railway train station passengers",
     3, "Advanced", "Social Studies", "Transport & Communication", "Railways",
     "The image shows an Indian passenger train. Indian Railways is important because it:",
     ["Connects cities and villages, transporting millions of people and goods daily", "Only carries coal", "Operates only in cities", "Was started in 2000"], 0,
     "Indian Railways is one of the world's largest rail networks, carrying over 8 billion passengers annually. It was started by the British in 1853 and connects remote villages to major cities."),

    ("G3 Forest trees wildlife",
     "Indian forest trees wildlife biodiversity",
     3, "Advanced", "Social Studies", "Our Environment", "Forests & Wildlife",
     "The image shows a dense Indian forest. Forests are important because they:",
     ["Provide oxygen, timber, habitat for animals, and prevent soil erosion", "Only provide wood for burning", "Have no use for humans", "Cause floods"], 0,
     "Forests are vital ecosystems — they produce oxygen, absorb CO2, prevent soil erosion, regulate rainfall, provide timber and medicines, and are home to wildlife."),

    ("G3 Indian harvest festival",
     "harvest festival India Pongal Onam celebration",
     3, "Foundation", "Social Studies", "Our Culture", "Festivals",
     "The image shows a harvest festival celebration in India. Harvest festivals are celebrated to:",
     ["Thank nature for good crops and celebrate the farming season's success", "Mourn the end of summer", "Mark the beginning of winter", "Celebrate the New Year only"], 0,
     "Harvest festivals (Pongal in Tamil Nadu, Onam in Kerala, Baisakhi in Punjab, Makar Sankranti) are celebrated with gratitude for a successful harvest, marking the end of the agricultural season."),

    ("G3 Indian coastal fishing",
     "Indian fishermen coastal village fishing boat",
     3, "Foundation", "Social Studies", "Our Community", "Livelihoods",
     "The image shows fishermen near the coast. People who live near the sea often depend on fishing because:",
     ["The sea provides fish which is their main source of food and income", "They have no other option", "Fish is not important", "The sea provides only water"], 0,
     "Coastal communities in India (Kerala, Goa, Tamil Nadu, Andhra Pradesh) rely heavily on fishing. India has a coastline of 7,517 km and millions of people depend on fishing for their livelihood."),

    ("G3 Voting election India",
     "voting election India democracy ballot",
     3, "Advanced", "Social Studies", "Our Government", "Democracy",
     "The image shows people voting in an election. In India, citizens vote to:",
     ["Choose their representatives and the government", "Buy goods from the market", "Pay taxes", "Get a driving licence"], 0,
     "India is a democracy where eligible citizens (18 years and above) vote to elect their representatives to Parliament and State Assemblies. Elections are conducted by the Election Commission of India."),
]

# =============================================================================
# GRADE 12 SST — Olympiad/Advanced
# =============================================================================
GR12_SST = [
    ("G12 SST globalisation world map",
     "globalisation world map trade economy international",
     12, "Olympiad", "Social Studies", "Globalisation", "Global Economy",
     "The image shows global trade connections. Globalisation has led to the international division of labour, where developing countries like India specialise in:",
     ["Labour-intensive manufacturing and services due to cost advantages", "Only agricultural exports", "Military production", "Space technology exclusively"], 0,
     "Globalisation allows countries to specialise based on comparative advantage. India has benefited through IT services, textiles, and manufacturing due to lower labour costs and a large skilled workforce."),

    ("G12 SST Indian Parliament democracy",
     "Indian Parliament building New Delhi democracy",
     12, "Olympiad", "Social Studies", "Indian Democracy", "Parliament & Legislature",
     "The image shows the Indian Parliament. India follows a bicameral legislature. Which statement CORRECTLY describes the difference between Lok Sabha and Rajya Sabha?",
     ["Lok Sabha (House of People) can be dissolved; Rajya Sabha (Council of States) is permanent — one-third retires every 2 years", "Rajya Sabha can be dissolved; Lok Sabha is permanent", "Both houses have equal power in all matters", "Lok Sabha has more members than Rajya Sabha on money bills"], 0,
     "Lok Sabha (545 members, directly elected, 5-year term) can be dissolved by President. Rajya Sabha (245 members, indirectly elected) is a permanent house — 1/3 members retire every 2 years."),

    ("G12 SST urbanisation city skyline India",
     "India city skyline urban development modern",
     12, "Advanced", "Social Studies", "Development", "Urbanisation",
     "The image shows rapid urban growth in India. Which of the following is a NEGATIVE consequence of rapid urbanisation?",
     ["Growth of slums, strain on infrastructure, increased pollution and inequality", "Increased agricultural productivity", "Decrease in population", "Improved rural living standards automatically"], 0,
     "Rapid unplanned urbanisation leads to slum formation, overwhelmed water/sanitation/transport systems, air pollution, urban heat islands, and growing income inequality."),

    ("G12 SST Indian economy GDP growth",
     "India economy business market growth development",
     12, "Olympiad", "Social Studies", "Indian Economy", "Economic Development",
     "The image represents India's economic growth. India follows a 'mixed economy' model. This means:",
     ["Both public (government) and private sectors coexist and contribute to the economy", "Only the government controls all production", "Only private companies control all resources", "India has no economic planning"], 0,
     "A mixed economy combines elements of capitalism (private enterprise) and socialism (state control). India's public sector handles strategic industries while private sector drives growth."),

    ("G12 SST environment deforestation",
     "deforestation forest destruction environmental damage",
     12, "Advanced", "Social Studies", "Environment", "Environmental Issues",
     "The image shows deforestation. From a political science perspective, the destruction of forests is primarily a failure of:",
     ["Environmental governance and policy enforcement", "Agricultural policy alone", "Military policy", "Only local village governance"], 0,
     "Deforestation reflects failures in environmental governance — weak enforcement of forest protection laws, corruption, inadequate penalties, and poor coordination between central and state governments."),

    ("G12 SST social media internet protest",
     "social media internet protest democracy young people",
     12, "Olympiad", "Social Studies", "Democracy & Politics", "Civil Society",
     "The image shows citizens using social media for political activism. The use of social media in democracy has:",
     ["Expanded civic participation but also enabled misinformation and polarisation", "Only positive effects on democracy", "No significant effect on political processes", "Replaced traditional elections"], 0,
     "Social media democratises voice and enables rapid mobilisation, but it also spreads misinformation, creates echo chambers, can be used for political manipulation, and may exclude digitally marginalised populations."),

    ("G12 SST caste discrimination protest",
     "social equality protest India rights march",
     12, "Olympiad", "Social Studies", "Social Justice", "Caste & Inequality",
     "The image shows a social equality march. Despite constitutional provisions for equality, caste-based discrimination persists in India because:",
     ["Social change lags behind legal change — cultural attitudes and structural inequalities take generations to transform", "The Constitution does not address caste discrimination", "Caste has no effect on access to resources", "All discrimination ended in 1950"], 0,
     "Article 17 of the Constitution abolished untouchability, and SC/ST (Prevention of Atrocities) Act provides legal protection. However, entrenched social attitudes, economic dependency, and structural disadvantage mean discrimination persists."),

    ("G12 SST India China border",
     "India China border Himalayas mountain geopolitics",
     12, "Olympiad", "Social Studies", "International Relations", "India's Foreign Policy",
     "The image shows the India-China border region. India follows a policy of 'strategic autonomy' in foreign policy. This means:",
     ["India maintains independent foreign policy positions, not aligning permanently with any power bloc", "India always sides with the USA", "India always sides with China", "India has no independent foreign policy"], 0,
     "India's strategic autonomy (successor to Nehru's Non-Alignment) means India pursues its national interest independently — engaging with USA, Russia, China, and others based on issue-specific interests rather than permanent alliances."),

    ("G12 SST women empowerment",
     "women empowerment education India gender equality",
     12, "Advanced", "Social Studies", "Social Issues", "Gender & Empowerment",
     "The image shows women in education. The 73rd Constitutional Amendment (1992) was significant for women's empowerment because it:",
     ["Reserved one-third of seats for women in Panchayati Raj institutions", "Gave women the right to vote", "Made education compulsory for girls", "Reserved seats for women in Parliament"], 0,
     "The 73rd Amendment (Panchayati Raj Act) mandated at least 1/3 reservation for women in local self-government bodies. In practice, many states have increased this to 50%."),

    ("G12 SST poverty rural India",
     "rural poverty India village livelihood development",
     12, "Advanced", "Social Studies", "Development Economics", "Poverty",
     "The image shows rural poverty in India. The Human Development Index (HDI) measures development using three dimensions. Which combination is CORRECT?",
     ["Life expectancy, Education (mean/expected years of schooling), GNI per capita (PPP)", "GDP, Military strength, Population size", "Literacy rate, GDP growth, Birth rate", "Employment rate, Infant mortality, Exports"], 0,
     "The UNDP's HDI combines: (1) Health — life expectancy at birth, (2) Education — mean years of schooling + expected years, (3) Standard of Living — GNI per capita at PPP."),

    ("G12 SST nuclear power plant energy",
     "nuclear power plant energy electricity India",
     12, "Olympiad", "Social Studies", "Resources & Energy", "Energy Policy",
     "The image shows a nuclear power plant. India's nuclear energy policy is shaped by the fact that India is NOT a signatory to the Nuclear Non-Proliferation Treaty (NPT). This is because:",
     ["India considers the NPT discriminatory — it allows existing nuclear states to keep weapons while preventing others from developing them", "India has no nuclear weapons", "India agreed with all NPT terms", "India signed but later withdrew"], 0,
     "India rejects the NPT as discriminatory (P5 states retain weapons; others cannot acquire them). The 2008 India-US Civil Nuclear Deal was a landmark agreement that gave India access to nuclear technology despite not signing the NPT."),

    ("G12 SST climate change protests",
     "climate change protest youth environment global warming",
     12, "Advanced", "Social Studies", "Environment", "Climate Change",
     "The image shows climate change protests. India faces a unique challenge in climate negotiations because:",
     ["India must balance development needs (reducing poverty, industrialisation) with emission reduction commitments", "India is the largest emitter of CO2", "India has already achieved all development goals", "India is unaffected by climate change"], 0,
     "India argues for 'climate justice' — historically, developed nations caused most emissions while industrialising. India needs development space, so its NDCs focus on renewable energy intensity rather than absolute emission cuts."),
]

# =============================================================================
# RUN
# =============================================================================
def run_batch(name, questions):
    section(name)
    print(f"  Total: {len(questions)}")
    for q in questions:
        run_q(q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10])

if __name__ == "__main__":
    print("=" * 60)
    print("  OlympiadReady - SST Pixabay (Grades 2, 3, 12)")
    total = len(GR2_SST) + len(GR3_SST) + len(GR12_SST)
    print(f"  Total questions: {total}")
    print("=" * 60)

    run_batch("Grade 2 Social Studies", GR2_SST)
    run_batch("Grade 3 Social Studies", GR3_SST)
    run_batch("Grade 12 Social Studies", GR12_SST)

    print(f"\n{'='*60}")
    print(f"DONE - Posted: {posted}  Skipped(dup): {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
    print(f"{'='*60}")
