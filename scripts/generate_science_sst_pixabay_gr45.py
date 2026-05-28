"""
generate_science_sst_pixabay_gr45.py
Real Pixabay photos -> Cloudinary -> image questions
Targets: Grade 4 Science, Grade 5 Science, Grade 4 SST, Grade 5 SST
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
        pub_id = f"{CLOUDINARY_FOLDER}/g45_{query[:26].replace(' ','-')}_{RUN_ID}_{hit['id']}"
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
# GRADE 4 SCIENCE
# =============================================================================
GR4_SCIENCE = [
    ("G4 Sci butterfly life cycle",
     "butterfly life cycle caterpillar metamorphosis",
     4, "Advanced", "Science", "Living World", "Life Cycles",
     "The image shows the life cycle of a butterfly. The process where a caterpillar transforms into a butterfly is called:",
     ["Metamorphosis", "Germination", "Pollination", "Migration"], 0,
     "Metamorphosis is the biological process of transformation. Complete metamorphosis (holometabolism) has 4 stages: egg → larva (caterpillar) → pupa (chrysalis) → adult (butterfly)."),

    ("G4 Sci food web animals",
     "food web animals nature predator prey ecosystem",
     4, "Advanced", "Science", "Living World", "Food Chains & Webs",
     "The image shows animals in a food web. An animal that eats BOTH plants and other animals is called:",
     ["Omnivore", "Herbivore", "Carnivore", "Decomposer"], 0,
     "Omnivores eat both plants and animals (e.g., bears, humans, crows). Herbivores eat only plants. Carnivores eat only animals. Decomposers break down dead matter."),

    ("G4 Sci water states liquid solid gas",
     "water states ice liquid steam evaporation",
     4, "Foundation", "Science", "Matter", "States of Water",
     "The image shows water in three states. When water vapour (gas) cools and turns back into liquid water, this process is called:",
     ["Condensation", "Evaporation", "Melting", "Freezing"], 0,
     "Condensation: gas → liquid (cooling). Evaporation: liquid → gas (heating). Melting: solid → liquid. Freezing: liquid → solid."),

    ("G4 Sci plants growing sunlight",
     "plants growing sunlight garden nature",
     4, "Foundation", "Science", "Living World", "Plants Need",
     "The image shows plants growing in sunlight. Plants need sunlight, water, and carbon dioxide to make their own food. This food-making process is called:",
     ["Photosynthesis", "Respiration", "Digestion", "Transpiration"], 0,
     "Photosynthesis: 6CO2 + 6H2O + sunlight → C6H12O6 (glucose) + 6O2. Plants are autotrophs (self-feeders) — they make food using sunlight energy."),

    ("G4 Sci human eye vision",
     "human eye close up vision sight",
     4, "Advanced", "Science", "Our Body", "Sense Organs",
     "The image shows a human eye. The coloured part of the eye that controls how much light enters is called the:",
     ["Iris", "Pupil", "Cornea", "Retina"], 0,
     "The iris is the coloured ring that expands/contracts to control pupil size — letting in more or less light depending on brightness. The pupil is the dark opening (hole) in the centre of the iris."),

    ("G4 Sci rock soil types",
     "soil types layers earth ground different",
     4, "Advanced", "Science", "Earth & Space", "Soil",
     "The image shows different types of soil. Which type of soil is BEST for growing most crops due to its ability to hold water while still draining well?",
     ["Loamy soil", "Sandy soil", "Clayey soil", "Rocky soil"], 0,
     "Loamy soil is ideal for crops — it is a mixture of sand, silt, and clay that holds moisture (unlike sandy soil which drains too fast) but doesn't waterlog (unlike heavy clay)."),

    ("G4 Sci teeth types food",
     "teeth types human dental health",
     4, "Foundation", "Science", "Our Body", "Teeth & Digestion",
     "The image shows human teeth. The sharp pointed teeth used for tearing food are called:",
     ["Canines", "Incisors", "Molars", "Premolars"], 0,
     "Canines (4 in adults) are pointed/conical — used for tearing meat and food. Incisors are chisel-shaped for cutting. Molars and premolars are flat for grinding."),

    ("G4 Sci rainbow sky colors",
     "rainbow sky colours spectrum light nature",
     4, "Foundation", "Science", "Light", "Colours of Light",
     "The image shows a rainbow in the sky. A rainbow forms when sunlight passes through raindrops. How many colours are visible in a rainbow?",
     ["7 (VIBGYOR)", "5", "6", "8"], 0,
     "A rainbow has 7 colours: Violet, Indigo, Blue, Green, Yellow, Orange, Red (VIBGYOR / ROY G BIV). Raindrops act as prisms, dispersing white sunlight into its spectrum."),

    ("G4 Sci animal shelter habitat",
     "bird nest animals shelter habitat nature",
     4, "Foundation", "Science", "Living World", "Animal Habitats",
     "The image shows a bird's nest. Animals build or find shelters to protect themselves from:",
     ["Predators, weather, and for raising young", "Only sunlight", "Making noise", "Finding water only"], 0,
     "Animal shelters (nests, burrows, dens, shells) serve multiple purposes: protection from predators, shelter from harsh weather (rain, cold, heat), and safe spaces to raise offspring."),

    ("G4 Sci magnet attraction",
     "magnet attract metal iron experiment",
     4, "Foundation", "Science", "Magnets", "Magnetic Attraction",
     "The image shows a magnet attracting objects. A student tests various objects with a magnet. Which object will the magnet NOT attract?",
     ["A copper coin", "An iron nail", "A steel pin", "A paper clip"], 0,
     "Magnets attract ferromagnetic materials: iron, steel, nickel, cobalt. Copper, aluminium, plastic, wood, and gold are non-magnetic and are NOT attracted to magnets."),
]

# =============================================================================
# GRADE 5 SCIENCE
# =============================================================================
GR5_SCIENCE = [
    ("G5 Sci microorganism yeast bread",
     "yeast bread baking microorganism fermentation",
     5, "Advanced", "Science", "Microorganisms", "Useful Microorganisms",
     "The image shows bread rising during baking. Yeast is used in bread-making because it produces carbon dioxide gas through fermentation, which makes the bread:",
     ["Rise and become light and fluffy (porous)", "Turn golden-brown", "Become hard", "Taste sweet"], 0,
     "Yeast ferments sugar: C6H12O6 → 2C2H5OH + 2CO2. The CO2 gas bubbles get trapped in the dough, making it rise and creating the soft, porous texture of bread."),

    ("G5 Sci water purification filter",
     "water purification filter clean drinking water",
     5, "Foundation", "Science", "Water", "Water Treatment",
     "The image shows water being purified. The process of making water safe to drink by killing germs using chlorine or UV light is called:",
     ["Disinfection / Chlorination", "Filtration", "Sedimentation", "Distillation"], 0,
     "Disinfection kills microorganisms — chlorine (most common), UV light, or ozonation are used. Filtration removes suspended particles but not all microbes. Both steps are used together in water treatment."),

    ("G5 Sci seed germination plant",
     "seed germination sprouting plant growth soil",
     5, "Foundation", "Science", "Plants", "Germination",
     "The image shows a seed germinating. For a seed to germinate successfully, it mainly needs:",
     ["Water, warmth, and air (oxygen)", "Sunlight directly on the seed", "Fertiliser and chemicals", "Only water"], 0,
     "Seeds need: (1) Water — activates enzymes, softens seed coat. (2) Warmth — speeds up metabolic reactions. (3) Air (O2) — for aerobic respiration to power growth. Sunlight is NOT needed for germination (seeds germinate underground)."),

    ("G5 Sci human lungs breathing",
     "human lungs breathing respiratory system anatomy",
     5, "Advanced", "Science", "Human Body", "Respiratory System",
     "The image shows human lungs. The exchange of oxygen and carbon dioxide between the blood and lungs takes place in tiny air sacs called:",
     ["Alveoli", "Bronchi", "Trachea", "Diaphragm"], 0,
     "Alveoli are tiny balloon-like air sacs in the lungs with very thin walls and rich blood supply — perfect for gas exchange. Their large total surface area (tennis court-sized) maximises O2/CO2 exchange."),

    ("G5 Sci simple machine pulley",
     "pulley simple machine rope weight lift",
     5, "Advanced", "Science", "Forces", "Simple Machines",
     "The image shows a pulley being used to lift a heavy object. A single fixed pulley makes work easier by:",
     ["Changing the direction of force (you pull down instead of lifting up)", "Reducing the amount of force needed to half","Increasing the speed of lifting","Multiplying the weight lifted"], 0,
     "A single fixed pulley does NOT reduce the force needed — it only changes the direction of force. You pull down (using your weight) instead of pulling up. Movable pulleys actually reduce the force needed."),

    ("G5 Sci food nutrients vitamins",
     "vitamins nutrition health food fresh vegetables",
     5, "Advanced", "Science", "Health", "Nutrients",
     "The image shows fresh fruits and vegetables. Vitamins are important nutrients because they:",
     ["Protect the body from diseases and regulate body processes", "Provide the main source of energy", "Build and repair muscles", "Form bones and teeth"], 0,
     "Vitamins are micronutrients needed in small amounts to regulate body processes and protect against deficiency diseases (Vitamin C prevents scurvy, D prevents rickets, A prevents night blindness)."),

    ("G5 Sci water cycle evaporation cloud",
     "water cycle cloud formation evaporation river",
     5, "Advanced", "Science", "Water Cycle", "Evaporation & Condensation",
     "The image shows the water cycle. Water from oceans, rivers and lakes evaporates into water vapour. This water vapour rises, cools, and forms clouds through a process called:",
     ["Condensation", "Precipitation", "Transpiration", "Infiltration"], 0,
     "Condensation: water vapour cools at higher altitudes → tiny droplets form around dust particles → clouds. When droplets combine and get heavy, they fall as precipitation (rain, snow, hail)."),

    ("G5 Sci electric safety lightning",
     "lightning storm electricity thunder safety",
     5, "Foundation", "Science", "Electricity", "Safety",
     "The image shows lightning during a storm. Lightning is dangerous because it is a:",
     ["Giant electric discharge between clouds and the ground","Type of rainfall","Sound wave","Magnetic field"], 0,
     "Lightning is a massive electrostatic discharge — built-up static electricity in clouds discharges to the ground (or between clouds), releasing enormous energy as heat and light."),

    ("G5 Sci animal adaptations desert",
     "camel desert adaptation animal survival",
     5, "Advanced", "Science", "Living World", "Adaptations",
     "The image shows a camel in the desert. Camels are adapted to hot, dry deserts. Which adaptation helps camels survive WITHOUT water for long periods?",
     ["Storing fat (not water) in their humps for energy; conserving water through concentrated urine","Humps store water directly for drinking","Sweating more than other animals to cool down","Having no kidneys to remove water from the body"], 0,
     "Camel humps store FAT (not water) — when metabolised, fat releases energy AND metabolic water. Camels also have very efficient kidneys (concentrated urine), can tolerate body temperature swings, and their oval RBCs work even when dehydrated."),

    ("G5 Sci rock erosion river",
     "river erosion rocks water nature geology",
     5, "Advanced", "Science", "Earth Science", "Erosion",
     "The image shows river erosion of rocks. The process by which rocks and soil are worn away and carried away by water, wind, or ice is called:",
     ["Erosion", "Weathering", "Sedimentation", "Deposition"], 0,
     "Erosion is the carrying away of rock/soil particles by an agent (water, wind, ice, gravity). Weathering is the breaking down of rock in place. Sedimentation/deposition is when eroded material settles."),
]

# =============================================================================
# GRADE 4 SST
# =============================================================================
GR4_SST = [
    ("G4 SST globe world map",
     "globe world map continents oceans geography",
     4, "Foundation", "Social Studies", "Our World", "Globe & Maps",
     "The image shows a globe. A globe is a model of the Earth. The large blue areas on the globe represent:",
     ["Oceans and seas (water bodies)", "Forests and jungles", "Deserts", "Mountains"], 0,
     "Oceans and seas cover about 71% of Earth's surface, shown in blue on maps and globes. The seven continents (land masses) are shown in different colours."),

    ("G4 SST Indian currency rupee",
     "Indian currency rupee notes coins money",
     4, "Foundation", "Social Studies", "Our Economy", "Money & Trade",
     "The image shows Indian currency. The symbol ₹ represents the Indian Rupee. This symbol was designed by:",
     ["D. Udaya Kumar (adopted 2010)", "Mahatma Gandhi", "The British government", "Reserve Bank of India in 1950"], 0,
     "The ₹ symbol was designed by D. Udaya Kumar and officially adopted on 15 July 2010. It combines the Devanagari 'Ra' and the Roman 'R' with two horizontal lines."),

    ("G4 SST government services police",
     "police officer India law safety government",
     4, "Foundation", "Social Studies", "Our Government", "Government Services",
     "The image shows a police officer. The police are a government service. Their main job is to:",
     ["Maintain law and order, prevent crime, and protect citizens", "Collect taxes from people", "Build roads and bridges", "Run schools and hospitals"], 0,
     "The police are responsible for maintaining public order, preventing and investigating crime, arresting lawbreakers, and protecting citizens — funded by the government as a public service."),

    ("G4 SST newspaper media communication",
     "newspaper media press journalism India",
     4, "Advanced", "Social Studies", "Communication", "Media",
     "The image shows a newspaper. Newspapers are important in a democracy because they:",
     ["Inform citizens about current events and hold the government accountable", "Only publish advertisements", "Replace schools and education", "Only entertain people"], 0,
     "A free press is essential to democracy — newspapers inform citizens, expose corruption, provide a platform for debate, and hold elected officials accountable. Freedom of the press is protected in India's Constitution."),

    ("G4 SST ancient monuments India",
     "ancient monuments ruins heritage India history",
     4, "Advanced", "Social Studies", "Our Heritage", "Ancient India",
     "The image shows ancient ruins in India. Studying old monuments and artefacts tells us about the past. The people who study ancient history through physical remains are called:",
     ["Archaeologists", "Geographers", "Meteorologists", "Biologists"], 0,
     "Archaeologists study human history by excavating and analysing physical remains — buildings, tools, pottery, coins, and bones. Famous Indian archaeological sites include Mohenjo-daro and Harappa."),

    ("G4 SST district map local area",
     "India state district map local area",
     4, "Foundation", "Social Studies", "Our Geography", "Administrative Divisions",
     "The image shows a map of India showing states. India is divided into states for administrative purposes. Currently, India has how many states?",
     ["28 states and 8 Union Territories", "29 states and 7 Union Territories", "25 states", "30 states"], 0,
     "As of 2024, India has 28 states and 8 Union Territories (Jammu & Kashmir became a UT in 2019; Ladakh became a separate UT). Total = 36 administrative divisions."),

    ("G4 SST tribal life India",
     "tribal community India village traditional culture",
     4, "Advanced", "Social Studies", "Our Society", "Tribes & Communities",
     "The image shows a tribal community in India. Tribal communities are important because they:",
     ["Preserve ancient traditions, languages, and knowledge about forests and nature", "Only live in cities", "Have no connection to mainstream culture", "Always oppose development"], 0,
     "India has over 700 tribal (Adivasi) communities. They preserve unique languages, art forms, traditional ecological knowledge, and cultural practices. Many live in forest areas and depend on forests for their livelihood."),

    ("G4 SST harvest crops India",
     "wheat harvest crop India agriculture farmer",
     4, "Foundation", "Social Studies", "Agriculture", "Crops & Seasons",
     "The image shows a wheat harvest. Wheat is a rabi crop in India. Rabi crops are sown in:",
     ["Winter (October-November) and harvested in spring (March-April)", "Summer (April-May)", "Monsoon (June-July)", "Any time of year"], 0,
     "Rabi = winter crops (sown Oct-Nov, harvested Mar-Apr): wheat, mustard, barley, peas. Kharif = monsoon crops (sown Jun-Jul, harvested Sep-Oct): rice, cotton, maize, jowar."),
]

# =============================================================================
# GRADE 5 SST
# =============================================================================
GR5_SST = [
    ("G5 SST Indus Valley civilisation",
     "Indus Valley Harappa Mohenjo-daro ancient India",
     5, "Advanced", "Social Studies", "Ancient India", "Indus Valley Civilisation",
     "The image shows artefacts from the Indus Valley Civilisation. This civilisation is remarkable for having:",
     ["Well-planned cities with drainage systems, standardised weights, and writing script", "Built the Taj Mahal", "Invented the decimal system only", "Existed only 200 years ago"], 0,
     "The Indus Valley Civilisation (3300-1300 BCE) had advanced urban planning: grid-pattern streets, covered brick drains, standardised weights and measures, multi-storey buildings, and their own undeciphered script."),

    ("G5 SST Ashoka pillar Buddhist",
     "Ashoka pillar Buddhist India ancient heritage",
     5, "Advanced", "Social Studies", "Ancient India", "Mauryan Empire",
     "The image shows an Ashoka Pillar. Emperor Ashoka erected these pillars across his empire. The Ashoka Chakra (wheel) on India's national flag is taken from the Ashoka Pillar at:",
     ["Sarnath (Uttar Pradesh)", "Delhi", "Patna", "Sanchi"], 0,
     "The Ashoka Pillar at Sarnath (where Buddha gave his first sermon) has the Lion Capital with the Dharmachakra. India's national emblem and the flag's Ashoka Chakra are both derived from this Sarnath pillar."),

    ("G5 SST India physical map mountains",
     "India physical map mountains plains rivers geography",
     5, "Advanced", "Social Studies", "Geography", "Physical Features of India",
     "The image shows India's physical map. The Great Indian Plains (Indo-Gangetic Plains) are formed by the rivers Indus, Ganga, and Brahmaputra. These plains are India's most important agricultural region because:",
     ["Fertile alluvial soil deposited by rivers makes them extremely productive for farming", "They have the most rainfall", "They are the highest land in India", "They border the sea directly"], 0,
     "The Indo-Gangetic Plains have deep, fertile alluvial soil carried down from the Himalayas over millions of years. Flat terrain and river irrigation make this India's breadbasket, growing wheat, rice, and sugarcane."),

    ("G5 SST medieval fort India",
     "medieval fort India Mughal Rajput history architecture",
     5, "Advanced", "Social Studies", "Medieval India", "Forts & Architecture",
     "The image shows a medieval Indian fort. Medieval forts were built on hills or with thick walls because:",
     ["They served as military defence — high ground gave advantage and thick walls resisted attacks", "They were more beautiful on hills", "They were easier to build on hills", "Hills had more water supply"], 0,
     "Medieval forts were military structures — elevated positions gave defenders strategic advantage (could see approaching enemies, harder to attack uphill). Thick walls withstood artillery. Famous: Chittorgarh, Gwalior, Red Fort."),

    ("G5 SST water conservation dam",
     "dam water reservoir conservation India irrigation",
     5, "Advanced", "Social Studies", "Resources", "Water Conservation",
     "The image shows a dam and reservoir. Dams are built to:",
     ["Store water for irrigation, generate hydroelectricity, and control floods", "Only generate electricity", "Only prevent floods", "Only provide drinking water to cities"], 0,
     "Multi-purpose dams serve several functions: irrigation water for crops, hydroelectric power generation, flood control by regulating river flow, and drinking water supply. Bhakra Nangal, Tehri, and Hirakud are major Indian dams."),

    ("G5 SST trade silk route ancient",
     "ancient trade route silk spices India merchants",
     5, "Olympiad", "Social Studies", "Ancient India", "Trade Routes",
     "The image shows ancient trade routes. India was famous for exporting spices, cotton, and silk to the world. The ancient trade route connecting Asia and Europe was called:",
     ["The Silk Route (Silk Road)", "The Spice Highway", "The Golden Road", "The Eastern Passage"], 0,
     "The Silk Road/Route was an ancient network of trade routes (overland and maritime) connecting China, India, Central Asia, the Middle East, and Europe. India exported spices, cotton, silk, and gems; imported gold, silver, and horses."),

    ("G5 SST national parks wildlife India",
     "national park tiger wildlife sanctuary India",
     5, "Advanced", "Social Studies", "Environment", "Wildlife Conservation",
     "The image shows a national park in India. Project Tiger was launched in 1973 to protect the Bengal tiger. How many tiger reserves does India currently have (approximately)?",
     ["Over 50 tiger reserves", "10 tiger reserves", "25 tiger reserves", "5 tiger reserves"], 0,
     "India launched Project Tiger in 1973 with 9 reserves. As of 2024, India has over 54 tiger reserves. India hosts about 70% of the world's wild tiger population, having grown from ~1800 (1970s) to over 3600 (2023)."),

    ("G5 SST constitution fundamental rights",
     "Indian Constitution fundamental rights democracy",
     5, "Advanced", "Social Studies", "Civics", "Our Constitution",
     "The image shows the Indian Constitution. The Fundamental Rights guaranteed to every Indian citizen include the Right to Equality. This means:",
     ["Every citizen is equal before the law regardless of religion, caste, gender, or birthplace", "Everyone earns the same salary", "Everyone has the same job", "Only adults have equal rights"], 0,
     "Article 14 guarantees equality before law. Article 15 prohibits discrimination on grounds of religion, race, caste, sex, or place of birth. These rights apply to ALL citizens regardless of background."),
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
    print("  OlympiadReady - Science & SST Pixabay (Grades 4, 5)")
    total = len(GR4_SCIENCE)+len(GR5_SCIENCE)+len(GR4_SST)+len(GR5_SST)
    print(f"  Total questions: {total}")
    print("=" * 60)

    run_batch("Grade 4 Science", GR4_SCIENCE)
    run_batch("Grade 5 Science", GR5_SCIENCE)
    run_batch("Grade 4 Social Studies", GR4_SST)
    run_batch("Grade 5 Social Studies", GR5_SST)

    print(f"\n{'='*60}")
    print(f"DONE - Posted: {posted}  Skipped(dup): {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
    print(f"{'='*60}")
