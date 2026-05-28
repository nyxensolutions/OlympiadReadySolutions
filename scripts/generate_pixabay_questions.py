"""
generate_pixabay_questions.py
Search Pixabay for real photos, download them, re-host on Cloudinary,
and create image-options questions for Science / GK grades 1–5.

Flow:
  Pixabay search -> download image bytes -> upload to Cloudinary -> store Cloudinary URL

Requirements:
    pip install requests cloudinary

Config (edit below OR set environment variables):
    PIXABAY_API_KEY        from https://pixabay.com/api/docs/
    CLOUDINARY_CLOUD_NAME
    CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET
    ADMIN_API_BASE         e.g. http://localhost:5062
    ADMIN_API_KEY
"""

import os, io, json, time, random, sys
import requests
import cloudinary
import cloudinary.uploader

# ── CONFIG ────────────────────────────────────────────────────────────────────
PIXABAY_API_KEY       = os.environ.get("PIXABAY_API_KEY", "")          # required
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "dyommthef")
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "414698218814162")
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "fIHmpWwiIllKPs2qbEeHVNzMMP4")
CLOUDINARY_FOLDER     = "olympiadready/questions"

ADMIN_API_BASE = os.environ.get("ADMIN_API_BASE", "https://olympiad-api-test-arghhvfxdpc5etem.centralindia-01.azurewebsites.net")
ADMIN_API_KEY  = os.environ.get("ADMIN_API_KEY",  "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt")   # required to post

DELAY_BETWEEN_UPLOADS  = 1.5  # seconds between Cloudinary uploads
DELAY_BETWEEN_DOWNLOADS = 2.0 # seconds between Pixabay image downloads
# ─────────────────────────────────────────────────────────────────────────────

if not PIXABAY_API_KEY:
    print("ERROR: PIXABAY_API_KEY is not set.")
    print("Get a free key at https://pixabay.com/api/docs/")
    print("Then run:  set PIXABAY_API_KEY=your_key_here")
    sys.exit(1)

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

RUN_ID = int(time.time())
posted_count = 0
failed_count = 0
local_queue = []


# ── HELPERS ───────────────────────────────────────────────────────────────────

def pixabay_search(query: str, count: int = 8) -> list[str]:
    """Return up to `count` Cloudinary URLs after downloading and re-hosting from Pixabay."""
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "safesearch": "true",
        "per_page": max(3, min(count * 2, 20)),   # minimum 3 (Pixabay requirement)
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        hits = r.json().get("hits", [])
    except Exception as e:
        print(f"  [FAIL] Pixabay search failed for '{query}': {e}")
        return []

    results = []
    for hit in hits:
        if len(results) >= count:
            break
        # Use previewURL (cdn.pixabay.com) — more permissive than webformatURL
        img_url = hit.get("previewURL") or hit.get("webformatURL")
        if not img_url:
            continue
        # Let Cloudinary fetch the image directly — avoids our download rate limit
        public_id = f"{CLOUDINARY_FOLDER}/{query.replace(' ','-')}-{RUN_ID}-{hit['id']}"
        try:
            time.sleep(DELAY_BETWEEN_UPLOADS)
            res = cloudinary.uploader.upload(
                img_url,          # pass URL string — Cloudinary fetches it
                public_id=public_id,
                overwrite=False,
                resource_type="image",
            )
            results.append(res["secure_url"])
        except Exception as e:
            print(f"  [FAIL] Cloudinary upload failed for '{query}': {e}")
    return results


def post_question(q: dict) -> bool:
    if not ADMIN_API_KEY:
        return False
    try:
        r = requests.post(
            f"{ADMIN_API_BASE}/api/admin/add-question",
            json=q,
            headers={"X-Admin-Key": ADMIN_API_KEY},
            timeout=15,
        )
        return r.status_code in (200, 201)
    except Exception as e:
        print(f"  [FAIL] Post failed: {e}")
        return False


def make_image_options_question(
    query_correct: str,
    query_wrongs: list[str],   # 3 items
    question_text: str,
    subject: str,
    grade: int,
    topic: str,
    subtopic: str,
    difficulty: str,
    explanation: str,
):
    global posted_count, failed_count
    print(f"\n  Building: '{question_text}'")

    # Fetch images — 1 correct + 3 wrong
    correct_urls = pixabay_search(query_correct, count=1)
    if not correct_urls:
        print(f"  [FAIL] No image found for correct answer '{query_correct}', skipping.")
        failed_count += 1
        return

    wrong_urls = []
    for wq in query_wrongs:
        urls = pixabay_search(wq, count=1)
        if urls:
            wrong_urls.extend(urls[:1])
        if len(wrong_urls) >= 3:
            break

    if len(wrong_urls) < 3:
        print(f"  [FAIL] Could not get enough wrong images ({len(wrong_urls)}/3), skipping.")
        failed_count += 1
        return

    options = [correct_urls[0]] + wrong_urls[:3]
    random.shuffle(options)
    correct_idx = options.index(correct_urls[0])

    q = {
        "subject": subject,
        "grade": grade,
        "topic": topic,
        "subTopic": subtopic,
        "difficulty": difficulty,
        "questionText": question_text,
        "imageUrl": None,
        "options": options,
        "correctAnswer": chr(65 + correct_idx),
        "explanation": explanation,
    }

    ok = post_question(q)
    if ok:
        print(f"  [OK] Posted ({chr(65+correct_idx)} = {query_correct})")
        posted_count += 1
    else:
        print(f"  -> Saved locally ({chr(65+correct_idx)} = {query_correct})")
        local_queue.append(q)
    time.sleep(3)  # pause between questions to reset Pixabay rate limit window


# ── QUESTION DEFINITIONS ──────────────────────────────────────────────────────
# Each entry: (correct_query, [wrong1, wrong2, wrong3], question_text, subject, grade, topic, subtopic, difficulty, explanation)

# fmt: (correct_query, [wrong1,wrong2,wrong3], question_text, subject, grade, topic, subtopic, difficulty, explanation)

SCIENCE_GRADE1 = [
    ("apple fruit",["banana fruit","mango fruit","grapes fruit"],"Which of these is an apple?","Science",1,"Plants Around Us","Fruits","Foundation","An apple is a round red or green fruit that grows on apple trees."),
    ("banana fruit",["orange fruit","strawberry","watermelon fruit"],"Which picture shows a banana?","Science",1,"Plants Around Us","Fruits","Foundation","A banana is a long yellow curved fruit."),
    ("carrot vegetable",["potato vegetable","tomato","broccoli"],"Which is a carrot?","Science",1,"Plants Around Us","Vegetables","Foundation","A carrot is an orange root vegetable."),
    ("lion wild animal",["elephant","tiger","bear"],"Which animal is a lion?","Science",1,"Animals Around Us","Wild Animals","Foundation","A lion is a large wild cat known as the king of the jungle."),
    ("elephant animal",["giraffe","zebra","rhinoceros"],"Which picture shows an elephant?","Science",1,"Animals Around Us","Wild Animals","Foundation","An elephant is the largest land animal with a long trunk."),
    ("butterfly insect",["bee insect","ant insect","dragonfly insect"],"Which of these is a butterfly?","Science",1,"Animals Around Us","Insects","Foundation","A butterfly has colourful wings and is a type of insect."),
    ("dog pet animal",["cat pet","rabbit pet","hamster pet"],"Which of these is a dog?","Science",1,"Animals Around Us","Domestic Animals","Foundation","Dogs are loyal domestic animals kept as pets."),
    ("rose flower",["tulip flower","daisy flower","lily flower"],"Which flower is a rose?","Science",1,"Plants Around Us","Flowers","Foundation","A rose is a beautiful flower with thorns on its stem."),
]

SCIENCE_GRADE2 = [
    ("sunflower",["rose flower","tulip flower","daisy flower"],"Which flower is a sunflower?","Science",2,"Plants Around Us","Flowers","Foundation","A sunflower is tall with large yellow petals and a dark centre."),
    ("cow domestic animal",["buffalo animal","goat animal","sheep animal"],"Which animal is a cow?","Science",2,"Animals Around Us","Domestic Animals","Foundation","A cow is a large domestic animal kept for milk."),
    ("mango fruit",["papaya fruit","pineapple fruit","guava fruit"],"Which picture shows a mango?","Science",2,"Plants Around Us","Fruits","Foundation","A mango is a sweet yellow or orange tropical fruit."),
    ("fish aquatic",["frog","crocodile","dolphin"],"Which of these is a fish?","Science",2,"Animals Around Us","Aquatic Animals","Foundation","Fish live in water and breathe through gills."),
    ("parrot bird",["eagle bird","penguin bird","sparrow bird"],"Which bird is a parrot?","Science",2,"Animals Around Us","Birds","Foundation","A parrot is a colourful bird that can mimic human speech."),
    ("neem tree",["oak tree","pine tree","palm tree"],"Which is a neem tree?","Science",2,"Plants Around Us","Trees","Foundation","The neem tree is a tall tree with compound leaves, known for medicinal properties."),
    ("onion vegetable",["garlic","ginger root","potato vegetable"],"Which vegetable is an onion?","Science",2,"Plants Around Us","Vegetables","Foundation","An onion is a round vegetable with layers, known for its strong smell."),
    ("frog amphibian",["lizard reptile","turtle reptile","crocodile reptile"],"Which of these is a frog?","Science",2,"Animals Around Us","Amphibians","Foundation","Frogs are amphibians that live both on land and in water."),
]

SCIENCE_GRADE3 = [
    ("eagle bird",["hawk bird","vulture bird","kite bird"],"Which bird is an eagle?","Science",3,"Animals Around Us","Birds","Foundation","Eagles are large birds of prey with sharp talons and hooked beaks."),
    ("cactus plant",["fern plant","bamboo plant","lotus plant"],"Which plant is a cactus?","Science",3,"Plants Around Us","Adaptation","Foundation","Cacti are desert plants that store water in their thick stems."),
    ("magnet",["battery","bulb","wire"],"Which object is a magnet?","Science",3,"Magnetism","Magnets","Foundation","A magnet attracts iron and steel objects."),
    ("rainbow",["lightning","thunder clouds","sunrise"],"Which natural phenomenon shows a rainbow?","Science",3,"Our Environment","Weather Phenomena","Foundation","A rainbow forms when sunlight passes through water droplets in the air."),
    ("penguin bird",["ostrich bird","flamingo bird","peacock bird"],"Which bird is a penguin?","Science",3,"Animals Around Us","Birds","Foundation","Penguins are flightless birds that live in cold Antarctic regions."),
    ("lotus flower",["water lily","pond weed","seaweed"],"Which is a lotus flower?","Science",3,"Plants Around Us","Aquatic Plants","Foundation","The lotus is the national flower of India and grows in ponds."),
]

SCIENCE_GRADE4 = [
    ("microscope lab equipment",["telescope","binoculars","magnifying glass"],"Which instrument is a microscope?","Science",4,"Scientific Tools","Lab Equipment","Advanced","A microscope magnifies very tiny objects that cannot be seen with the naked eye."),
    ("solar system planets",["milky way galaxy","constellation","comet"],"Which image shows the solar system?","Science",4,"Space","Solar System","Foundation","The solar system consists of the Sun and 8 planets orbiting around it."),
    ("caterpillar larva",["beetle insect","moth insect","ant insect"],"Which is a caterpillar?","Science",4,"Animals Around Us","Insects","Foundation","A caterpillar is the larva stage of a butterfly or moth."),
    ("skeleton human bones",["muscles diagram","nervous system","digestive system"],"Which diagram shows the human skeleton?","Science",4,"Human Body","Skeletal System","Foundation","The human skeleton has 206 bones and provides support and structure to the body."),
    ("thermometer",["barometer","compass","ruler"],"Which instrument measures temperature?","Science",4,"Scientific Tools","Measurement","Foundation","A thermometer measures temperature in degrees Celsius or Fahrenheit."),
]

SCIENCE_GRADE5 = [
    ("beaker lab glassware",["test tube","flask","petri dish"],"Which lab equipment is a beaker?","Science",5,"Scientific Tools","Lab Equipment","Foundation","A beaker is a cylindrical glass container used to hold and heat liquids."),
    ("heart human organ",["lungs organ","kidney organ","liver organ"],"Which human organ is the heart?","Science",5,"Human Body","Organs","Foundation","The heart pumps blood throughout the body."),
    ("moon phases",["solar eclipse","lunar eclipse","comet"],"Which image shows the phases of the moon?","Science",5,"Space","Moon","Advanced","The moon goes through phases — new moon, crescent, quarter, gibbous, and full moon."),
    ("wind turbine renewable energy",["solar panel","hydroelectric dam","nuclear plant"],"Which generates wind energy?","Science",5,"Energy","Renewable Energy","Advanced","Wind turbines convert wind energy into electricity."),
    ("pyramid food",["food plate","vitamin chart","calorie chart"],"Which diagram shows the food pyramid?","Science",5,"Health and Nutrition","Food Groups","Foundation","The food pyramid shows the recommended proportions of different food groups."),
]

SCIENCE_GRADE6_8 = [
    ("test tube chemistry",["beaker","flask conical","bunsen burner"],"Which lab equipment is a test tube?","Science",6,"Lab Equipment","Chemistry Tools","Foundation","Test tubes are small cylindrical tubes used in chemistry experiments."),
    ("bunsen burner",["alcohol lamp","gas stove","oven"],"Which is a Bunsen burner used in labs?","Science",6,"Lab Equipment","Heating Devices","Foundation","A Bunsen burner provides a hot flame for heating in chemistry labs."),
    ("human eye diagram",["human ear","human nose","human tongue"],"Which diagram shows the structure of the human eye?","Science",7,"Human Body","Sense Organs","Advanced","The human eye consists of the cornea, lens, retina, and optic nerve."),
    ("telescope astronomy",["microscope","binoculars","periscope"],"Which instrument is used to observe stars?","Science",7,"Space","Astronomical Tools","Foundation","A telescope magnifies distant objects in space like stars and planets."),
    ("earthquake seismograph",["barometer","anemometer","rain gauge"],"Which instrument measures earthquake intensity?","Science",8,"Earth and Universe","Natural Disasters","Advanced","A seismograph records the intensity and magnitude of earthquakes."),
    ("convex lens",["concave lens","concave mirror","plane mirror"],"Which is a convex lens?","Science",8,"Light","Optics","Advanced","A convex lens is thicker in the middle and converges light rays to a focal point."),
]

GK_GRADES = [
    ("Indian flag",["French flag","Italian flag","Irish flag"],"Which is the flag of India?","General Knowledge",1,"Our Country","National Symbols","Foundation","The Indian flag has saffron, white, and green with a blue Ashoka Chakra in the centre."),
    ("traffic light red",["traffic light green","traffic light yellow","road sign"],"Which traffic light colour means STOP?","General Knowledge",2,"Safety Rules","Traffic Rules","Foundation","Red light means stop. Never cross on a red light."),
    ("school building",["hospital building","post office","library building"],"Which building is a school?","General Knowledge",1,"Community","Places","Foundation","A school is where children study and learn."),
    ("ambulance vehicle",["police car","fire truck","bus"],"Which vehicle is an ambulance?","General Knowledge",2,"Community Helpers","Vehicles","Foundation","An ambulance rushes sick or injured people to the hospital."),
    ("fire truck",["police car","ambulance","tow truck"],"Which vehicle is a fire truck?","General Knowledge",2,"Community Helpers","Vehicles","Foundation","Fire trucks carry firefighters and water to put out fires."),
    ("Taj Mahal monument",["Red Fort","Qutub Minar","India Gate"],"Which monument is the Taj Mahal?","General Knowledge",3,"Our Country","Monuments","Foundation","The Taj Mahal in Agra is a white marble mausoleum and a UNESCO World Heritage Site."),
    ("Red Fort Delhi",["Qutub Minar","Gateway of India","Charminar"],"Which is the Red Fort?","General Knowledge",3,"Our Country","Monuments","Foundation","The Red Fort in Delhi was built by Mughal emperor Shah Jahan."),
    ("India Gate Delhi",["Gateway of India","Qutub Minar","Charminar Hyderabad"],"Which monument is India Gate?","General Knowledge",4,"Our Country","Monuments","Foundation","India Gate in New Delhi is a war memorial dedicated to Indian soldiers."),
    ("Golden Temple Amritsar",["Lotus Temple","Akshardham Temple","Sun Temple"],"Which is the Golden Temple?","General Knowledge",4,"Our Country","Monuments","Foundation","The Golden Temple in Amritsar is the holiest shrine of Sikhism."),
    ("astronaut space",["pilot airplane","diver underwater","mountaineer"],"Which picture shows an astronaut?","General Knowledge",3,"Space","Space Exploration","Foundation","An astronaut is a person trained to travel and work in space."),
    ("cricket bat",["hockey stick","badminton racket","tennis racket"],"Which sports equipment is a cricket bat?","General Knowledge",2,"Sports","Cricket","Foundation","A cricket bat is used to hit the ball in the sport of cricket."),
    ("football soccer",["rugby ball","basketball","volleyball"],"Which ball is used in football (soccer)?","General Knowledge",2,"Sports","Football","Foundation","A football is a round ball used in the sport of soccer/football."),
    ("chess board game",["carrom board","ludo board","snakes and ladders"],"Which is a chess board?","General Knowledge",4,"Sports","Indoor Games","Foundation","Chess is a strategy board game played between two players with 16 pieces each."),
    ("map India outline",["map China","map Australia","map Africa"],"Which map shows the outline of India?","General Knowledge",5,"Our Country","Geography","Advanced","India is a peninsula surrounded by the Arabian Sea, Bay of Bengal, and Indian Ocean."),
    ("Mahatma Gandhi photo",["Jawaharlal Nehru","Subhas Chandra Bose","Bhagat Singh"],"Which picture shows Mahatma Gandhi?","General Knowledge",4,"Our Country","Freedom Fighters","Foundation","Mahatma Gandhi led India's non-violent independence movement against British rule."),
    ("planet Earth from space",["planet Mars","planet Jupiter","planet Saturn"],"Which planet is shown — the one with blue oceans and green land?","General Knowledge",4,"Space","Planets","Foundation","Earth is the third planet from the Sun and the only known planet with life."),
    ("planet Saturn rings",["planet Jupiter","planet Neptune","planet Uranus"],"Which planet has prominent rings visible in the image?","General Knowledge",5,"Space","Planets","Foundation","Saturn is famous for its beautiful ring system made of ice and rock."),
    ("solar panel energy",["wind turbine","hydroelectric dam","coal plant"],"Which image shows a solar panel?","General Knowledge",5,"Environment","Renewable Energy","Foundation","Solar panels convert sunlight directly into electricity."),
]

SPELL_BEE_GRADES = [
    ("umbrella rain",["raincoat","rain boots","hat"],"Which picture shows an UMBRELLA?","Spell Bee",2,"Objects","Weather Items","Foundation","Umbrella: U-M-B-R-E-L-L-A. Used for protection from rain."),
    ("butterfly insect",["dragonfly","grasshopper","moth insect"],"Which picture shows a BUTTERFLY?","Spell Bee",2,"Animals","Insects","Foundation","Butterfly: B-U-T-T-E-R-F-L-Y."),
    ("bicycle",["motorcycle","scooter","tricycle"],"Which vehicle is a BICYCLE?","Spell Bee",2,"Vehicles","Two-wheelers","Foundation","Bicycle: B-I-C-Y-C-L-E. A two-wheeled vehicle powered by pedalling."),
    ("elephant animal",["rhinoceros","hippopotamus","giraffe"],"Which animal is an ELEPHANT?","Spell Bee",3,"Animals","Wild Animals","Foundation","Elephant: E-L-E-P-H-A-N-T. The largest land animal."),
    ("giraffe animal",["camel animal","zebra animal","cheetah animal"],"Which animal is a GIRAFFE?","Spell Bee",3,"Animals","Wild Animals","Foundation","Giraffe: G-I-R-A-F-F-E. The tallest living animal."),
    ("pineapple fruit",["coconut fruit","jackfruit","watermelon fruit"],"Which fruit is a PINEAPPLE?","Spell Bee",3,"Plants","Fruits","Foundation","Pineapple: P-I-N-E-A-P-P-L-E. A tropical fruit with a spiky crown."),
    ("telescope instrument",["microscope","binoculars","periscope"],"Which instrument is a TELESCOPE?","Spell Bee",4,"Science","Instruments","Advanced","Telescope: T-E-L-E-S-C-O-P-E. Used to see distant objects in space."),
    ("helicopter aircraft",["airplane","hot air balloon","glider"],"Which aircraft is a HELICOPTER?","Spell Bee",3,"Vehicles","Aircraft","Foundation","Helicopter: H-E-L-I-C-O-P-T-E-R. It can hover and fly vertically."),
    ("thermometer temperature",["barometer","compass","magnifying glass"],"Which instrument is a THERMOMETER?","Spell Bee",4,"Science","Instruments","Foundation","Thermometer: T-H-E-R-M-O-M-E-T-E-R. Measures temperature."),
    ("octopus sea animal",["jellyfish","squid","crab"],"Which sea animal is an OCTOPUS?","Spell Bee",4,"Animals","Sea Animals","Foundation","Octopus: O-C-T-O-P-U-S. It has eight arms and lives in the ocean."),
    ("crocodile reptile",["alligator reptile","lizard reptile","iguana reptile"],"Which reptile is a CROCODILE?","Spell Bee",4,"Animals","Reptiles","Foundation","Crocodile: C-R-O-C-O-D-I-L-E. A large reptile living near rivers."),
    ("ambulance vehicle",["police car","fire truck","taxi"],"Which vehicle is an AMBULANCE?","Spell Bee",3,"Vehicles","Emergency","Foundation","Ambulance: A-M-B-U-L-A-N-C-E. Carries patients to hospital."),
]

SOCIAL_STUDIES = [
    ("world map globe",["India map","Asia map","Europe map"],"Which image shows a globe (world map)?","Social Studies",4,"Geography","Maps and Globes","Foundation","A globe is a spherical model of Earth showing all continents and oceans."),
    ("compass direction",["thermometer","barometer","magnifying glass"],"Which instrument is used to find direction?","Social Studies",5,"Geography","Navigation","Foundation","A compass has a magnetic needle that always points North."),
    ("river Ganges India",["river Nile","river Amazon","river Mississippi"],"Which river is shown in India — the sacred river flowing through Varanasi?","Social Studies",5,"Geography","Rivers","Advanced","The Ganges (Ganga) is India's most sacred river and the longest river flowing entirely within India."),
    ("Himalaya mountains snow",["Western Ghats","Aravalli Hills","Nilgiri Hills"],"Which mountain range has snow-capped peaks — the highest in India?","Social Studies",5,"Geography","Mountains","Foundation","The Himalayas are the highest mountain range in the world, forming India's northern border."),
    ("Parliament House India",["Rashtrapati Bhavan","Supreme Court India","Vidhan Sabha"],"Which building is the Parliament House of India?","Social Studies",6,"Civics","Government Buildings","Advanced","The Parliament House (Sansad Bhavan) in New Delhi is where India's Parliament meets."),
]

CYBER_GRADES = [
    ("computer desktop",["laptop computer","tablet computer","smartphone"],"Which is a desktop computer?","Cyber",3,"Computers","Types of Computers","Foundation","A desktop computer has a separate monitor, keyboard, and CPU unit."),
    ("keyboard computer",["mouse computer","monitor screen","printer"],"Which computer peripheral is a keyboard?","Cyber",3,"Computers","Input Devices","Foundation","A keyboard is an input device used to type text and commands."),
    ("computer mouse",["trackpad","joystick","touchscreen"],"Which is a computer mouse?","Cyber",3,"Computers","Input Devices","Foundation","A mouse is a pointing device that controls the cursor on the screen."),
    ("printer output device",["scanner","keyboard","hard disk"],"Which device is a printer?","Cyber",4,"Computers","Output Devices","Foundation","A printer is an output device that produces hard copies of digital documents."),
    ("robot technology",["computer","drone","3d printer"],"Which image shows a robot?","Cyber",5,"Technology","Robotics","Advanced","Robots are machines programmed to perform tasks automatically."),
    ("satellite dish communication",["radio antenna","cell tower","television"],"Which device is a satellite dish?","Cyber",5,"Technology","Communication","Advanced","Satellite dishes receive and send signals to/from satellites in space for communication."),
]


# ── NEW BATCHES ───────────────────────────────────────────────────────────────

GK_INDIA_SPECIFIC = [
    ("Indian school building",["Indian hospital","Indian post office","Indian library"],"Which building is an Indian school?","General Knowledge",1,"Community","Places in India","Foundation","Schools in India are where children receive their education."),
    ("Indian ambulance red cross",["Indian police car","Indian fire truck","Indian bus"],"Which vehicle is an Indian AMBULANCE?","General Knowledge",2,"Community Helpers","Emergency Vehicles","Foundation","An ambulance carries patients to hospital quickly."),
    ("Indian police car",["ambulance vehicle","fire truck","taxi car"],"Which is an Indian police vehicle?","General Knowledge",2,"Community Helpers","Safety","Foundation","Police vehicles help maintain law and order."),
    ("Qutub Minar Delhi",["Charminar Hyderabad","Lotus Temple Delhi","Hawa Mahal Jaipur"],"Which is the Qutub Minar?","General Knowledge",4,"Our Country","Monuments","Foundation","Qutub Minar in Delhi is the tallest brick minaret in the world."),
    ("Hawa Mahal Jaipur",["Amer Fort","City Palace Jaipur","Jantar Mantar"],"Which is the Hawa Mahal?","General Knowledge",4,"Our Country","Monuments","Foundation","Hawa Mahal is a palace in Jaipur known as the Palace of Winds."),
    ("Gateway of India Mumbai",["Victoria Memorial Kolkata","Charminar","India Gate"],"Which is the Gateway of India?","General Knowledge",4,"Our Country","Monuments","Foundation","The Gateway of India is an arch monument in Mumbai built in 1924."),
    ("Jawaharlal Nehru photo",["Sardar Vallabhbhai Patel","Rabindranath Tagore","Dr BR Ambedkar"],"Which picture shows Jawaharlal Nehru?","General Knowledge",5,"Our Country","Freedom Fighters","Foundation","Jawaharlal Nehru was India's first Prime Minister."),
    ("Dr APJ Abdul Kalam",["Dr Vikram Sarabhai","CV Raman scientist","Homi Bhabha scientist"],"Which picture shows Dr APJ Abdul Kalam?","General Knowledge",5,"Our Country","Great Indians","Foundation","Dr APJ Abdul Kalam was India's Missile Man and 11th President."),
    ("Indian rupee currency",["US dollar","British pound","Euro currency"],"Which is the Indian currency (Rupee)?","General Knowledge",3,"Our Country","Economy","Foundation","The Indian Rupee (INR) is the official currency of India."),
    ("peacock bird India",["crane bird","flamingo bird","hornbill bird"],"Which bird is India's National Bird?","General Knowledge",3,"Our Country","National Symbols","Foundation","The peacock is India's national bird, known for its beautiful feathers."),
    ("tiger wild animal",["leopard animal","cheetah animal","jaguar animal"],"Which animal is India's National Animal?","General Knowledge",3,"Our Country","National Symbols","Foundation","The Bengal Tiger is India's national animal."),
    ("lotus flower national",["rose flower","sunflower","marigold flower"],"Which is India's National Flower?","General Knowledge",3,"Our Country","National Symbols","Foundation","The Lotus is India's national flower and grows in ponds."),
    ("Indian railway train",["metro train","bullet train Japan","tram car"],"Which image shows an Indian Railway train?","General Knowledge",4,"Transport","Railways","Foundation","Indian Railways is one of the largest railway networks in the world."),
    ("auto rickshaw India",["tuk tuk Thailand","rickshaw cycle","taxi cab"],"Which is an auto-rickshaw common in India?","General Knowledge",2,"Transport","Vehicles","Foundation","Auto-rickshaws are three-wheeled vehicles used for short-distance travel in India."),
]

SCIENCE_GRADE7_8_OLYMPIAD = [
    ("cell microscope biology",["tissue diagram","organ heart","organism animal"],"Which image shows a cell as seen under a microscope?","Science",7,"Living World","Cell Biology","Advanced","The cell is the basic unit of life. A typical animal cell has a nucleus, cytoplasm and cell membrane."),
    ("mitochondria cell organelle",["nucleus cell","chloroplast","ribosome"],"Which organelle is called the powerhouse of the cell?","Science",8,"Living World","Cell Biology","Olympiad","Mitochondria produce ATP through cellular respiration, providing energy to the cell."),
    ("chloroplast green plant cell",["mitochondria","vacuole","nucleus"],"Which organelle in a plant cell is responsible for photosynthesis?","Science",7,"Plants Around Us","Photosynthesis","Advanced","Chloroplasts contain chlorophyll which absorbs sunlight for photosynthesis."),
    ("DNA double helix structure",["RNA structure","protein structure","chromosome"],"Which image shows the double helix structure of DNA?","Science",9,"Living World","Genetics","Olympiad","DNA (Deoxyribonucleic acid) carries genetic information in a double helix structure."),
    ("periodic table chemistry",["chemical formula","molecular structure","atom diagram"],"Which image shows the Periodic Table of Elements?","Science",8,"Matter and Materials","Chemistry","Olympiad","The Periodic Table arranges all known elements by atomic number and properties."),
    ("prism light dispersion",["lens refraction","mirror reflection","optical fibre"],"Which shows dispersion of white light through a prism?","Science",8,"Light","Optics","Advanced","A prism splits white light into its constituent colours: VIBGYOR (rainbow colours)."),
    ("electromagnet coil",["permanent magnet","bar magnet","horseshoe magnet"],"Which image shows an electromagnet?","Science",7,"Electricity and Magnetism","Electromagnetism","Advanced","An electromagnet is made by passing electric current through a coil wound around an iron core."),
    ("acid base indicator litmus",["pH meter","thermometer","voltmeter"],"Which shows a litmus test used to identify acids and bases?","Science",8,"Matter and Materials","Acids and Bases","Advanced","Litmus paper turns red in acids and blue in bases."),
    ("human digestive system diagram",["circulatory system","nervous system","respiratory system"],"Which diagram shows the human digestive system?","Science",7,"Human Body","Digestion","Foundation","The digestive system breaks down food into nutrients for the body."),
    ("human circulatory system heart",["digestive system","nervous system","skeletal system"],"Which diagram shows the human circulatory system?","Science",8,"Human Body","Circulation","Advanced","The circulatory system consists of the heart, blood, and blood vessels."),
    ("nuclear power plant",["solar plant","wind farm","hydroelectric dam"],"Which image shows a nuclear power plant?","Science",9,"Energy","Nuclear Energy","Olympiad","Nuclear power plants generate electricity using nuclear fission reactions."),
    ("volcanic eruption lava",["earthquake damage","tsunami wave","tornado storm"],"Which natural disaster shows a volcanic eruption?","Science",7,"Earth and Universe","Natural Disasters","Foundation","Volcanic eruptions release hot lava, ash, and gases from beneath the Earth's surface."),
]

SCIENCE_GRADE9_10_OLYMPIAD = [
    ("electromagnetic spectrum chart",["sound spectrum","colour spectrum","atomic spectrum"],"Which diagram shows the electromagnetic spectrum?","Science",9,"Light","Electromagnetic Waves","Olympiad","The EM spectrum ranges from radio waves to gamma rays, with visible light in between."),
    ("Newton laws of motion diagram",["Kepler laws","Ohm law graph","Boyle law graph"],"Which diagram illustrates Newton's Laws of Motion?","Science",9,"Force and Motion","Newton's Laws","Olympiad","Newton's three laws describe how objects behave under forces and inertia."),
    ("electric circuit parallel series",["magnetic field diagram","wave diagram","power grid"],"Which diagram shows both series and parallel circuits?","Science",9,"Electricity and Magnetism","Electric Circuits","Olympiad","Series circuits have one path for current; parallel circuits have multiple paths."),
    ("chemical bonding ionic covalent",["molecular formula","structural formula","periodic table"],"Which diagram shows ionic and covalent bonding?","Science",10,"Matter and Materials","Chemical Bonding","Olympiad","Ionic bonds involve electron transfer; covalent bonds involve electron sharing."),
    ("genetics Punnett square",["karyotype chromosomes","DNA replication","cell division mitosis"],"Which diagram shows a Punnett square for genetics?","Science",10,"Living World","Genetics","Olympiad","A Punnett square predicts the probability of offspring inheriting certain traits."),
    ("photosynthesis equation diagram",["respiration equation","digestion diagram","excretion diagram"],"Which diagram shows the process of photosynthesis?","Science",9,"Plants Around Us","Photosynthesis","Advanced","Photosynthesis: 6CO2 + 6H2O + light -> C6H12O6 + 6O2."),
    ("human brain diagram parts",["spinal cord","nervous system","sense organs diagram"],"Which diagram shows the parts of the human brain?","Science",9,"Human Body","Nervous System","Olympiad","The brain has three main parts: cerebrum (thinking), cerebellum (balance), brainstem (basic functions)."),
    ("reflection refraction light diagram",["diffraction light","dispersion prism","polarisation light"],"Which diagram shows both reflection and refraction of light?","Science",9,"Light","Optics","Advanced","Reflection is bouncing of light; refraction is bending of light as it passes between media."),
]

MATH_VISUAL = [
    ("number line integers",["number chart","multiplication table","abacus"],"Which shows a number line with integers?","Mathematics",5,"Number System","Number Line","Foundation","A number line shows integers arranged in order from negative to positive."),
    ("pie chart statistics",["bar graph","line graph","histogram"],"Which is a pie chart used in statistics?","Mathematics",6,"Data Handling","Pie Charts","Foundation","A pie chart shows data as slices of a circle proportional to each value."),
    ("coordinate plane graph",["number line","bar graph","Venn diagram"],"Which shows a coordinate plane (x-y axes)?","Mathematics",6,"Geometry","Coordinate Geometry","Advanced","A coordinate plane has two axes — x (horizontal) and y (vertical) — meeting at the origin."),
    ("triangle types acute obtuse",["quadrilateral shapes","circle diagram","polygon shapes"],"Which diagram shows types of triangles?","Mathematics",5,"Geometry","Triangles","Foundation","Triangles are classified by angles: acute (all <90°), right (one =90°), obtuse (one >90°)."),
    ("fraction equivalent diagram",["decimal chart","percentage chart","ratio diagram"],"Which diagram shows equivalent fractions?","Mathematics",4,"Fractions","Equivalent Fractions","Foundation","Equivalent fractions represent the same value, e.g. 1/2 = 2/4 = 4/8."),
    ("3D shapes cube sphere cylinder",["2D shapes circle","flat shapes","polygon chart"],"Which image shows 3D geometric shapes?","Mathematics",4,"Geometry","3D Shapes","Foundation","Common 3D shapes include cube, sphere, cylinder, cone, and cuboid."),
    ("symmetry butterfly mirror line",["rotation diagram","translation diagram","reflection axis"],"Which image shows a line of symmetry?","Mathematics",5,"Geometry","Symmetry","Foundation","A line of symmetry divides a shape into two identical mirror-image halves."),
    ("probability tree diagram",["Venn diagram","bar graph","frequency table"],"Which diagram is a probability tree?","Mathematics",8,"Probability","Tree Diagrams","Olympiad","A probability tree diagram shows all possible outcomes of sequential events."),
]

CYBER_ADVANCED = [
    ("binary code 01",["hexadecimal code","ASCII chart","morse code"],"Which image shows binary code (0s and 1s)?","Cyber",5,"Programming","Number Systems","Foundation","Computers use binary code — only 0s and 1s — to process all information."),
    ("Python programming code",["C++ code","Java code","HTML code"],"Which image shows Python programming code?","Cyber",6,"Programming","Coding","Advanced","Python is a popular, beginner-friendly programming language."),
    ("internet network diagram",["local area network","server rack","router modem"],"Which diagram shows an internet network?","Cyber",6,"Networks","Internet","Advanced","The internet is a global network connecting millions of computers worldwide."),
    ("artificial intelligence robot brain",["computer chip","circuit board","hard disk"],"Which image represents Artificial Intelligence (AI)?","Cyber",7,"Technology","AI and ML","Olympiad","Artificial Intelligence enables machines to learn and perform human-like tasks."),
    ("cloud computing diagram",["server room","data centre","mainframe computer"],"Which diagram shows cloud computing?","Cyber",7,"Technology","Cloud Computing","Advanced","Cloud computing stores and processes data on remote servers accessed via the internet."),
    ("cybersecurity lock shield",["antivirus software","firewall diagram","password manager"],"Which image represents cybersecurity?","Cyber",6,"Safety","Cyber Safety","Foundation","Cybersecurity protects computers and data from hackers and cyber attacks."),
    ("QR code scanner",["barcode scanner","NFC chip","RFID tag"],"Which image shows a QR code?","Cyber",4,"Technology","Digital Tools","Foundation","QR codes store information that can be read by a camera or scanner."),
    ("3D printer object",["laser printer","inkjet printer","photocopier"],"Which machine is a 3D printer?","Cyber",7,"Technology","3D Printing","Advanced","A 3D printer creates three-dimensional objects by layering material based on a digital design."),
]

LR_VISUAL = [
    ("mirror image reflection",["rotation 90 degree","symmetry axis","shadow outline"],"Which image shows a mirror reflection?","Logical Reasoning",4,"Visual Reasoning","Mirror Images","Foundation","A mirror image is the reflection of an object, flipped horizontally."),
    ("cube net flat pattern",["pyramid net","cylinder net","cone net"],"Which is the net (unfolded pattern) of a cube?","Logical Reasoning",5,"Visual Reasoning","3D to 2D","Advanced","A net is a 2D shape that can be folded to make a 3D shape. A cube net has 6 equal squares."),
    ("shadow matching object",["reflection mirror","rotation shape","silhouette art"],"Which image shows shadow matching?","Logical Reasoning",4,"Visual Reasoning","Shadows","Foundation","The shadow of an object shows its silhouette from a particular direction of light."),
    ("figure counting shapes",["pattern sequence","odd one out","analogy diagram"],"Which image shows counting shapes in a figure?","Logical Reasoning",3,"Visual Counting","Shape Counting","Foundation","Count the number of triangles, squares or other shapes hidden in a complex figure."),
    ("paper folding punch hole",["paper cutting","origami fold","paper symmetry"],"Which shows a paper folding and hole-punch problem?","Logical Reasoning",6,"Visual Reasoning","Paper Folding","Advanced","Paper folding problems test spatial reasoning — predict where holes appear when unfolded."),
]

ALL_QUESTION_SETS = (SCIENCE_GRADE1 + SCIENCE_GRADE2 + SCIENCE_GRADE3 +
                     SCIENCE_GRADE4 + SCIENCE_GRADE5 + SCIENCE_GRADE6_8 +
                     GK_GRADES + SPELL_BEE_GRADES + SOCIAL_STUDIES + CYBER_GRADES +
                     GK_INDIA_SPECIFIC + SCIENCE_GRADE7_8_OLYMPIAD +
                     SCIENCE_GRADE9_10_OLYMPIAD + MATH_VISUAL +
                     CYBER_ADVANCED + LR_VISUAL)


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not ADMIN_API_KEY:
        print("[!]  ADMIN_API_KEY not set — questions will be saved to pixabay_questions.json")

    total = len(ALL_QUESTION_SETS)
    print(f"Processing {total} image-options questions via Pixabay -> Cloudinary pipeline...\n")

    for entry in ALL_QUESTION_SETS:
        make_image_options_question(*entry)

    # Save local queue for manual import
    out_path = os.path.join(os.path.dirname(__file__), "pixabay_questions.json")
    if local_queue:
        with open(out_path, "w") as f:
            json.dump(local_queue, f, indent=2)
        print(f"\n[FILE] {len(local_queue)} questions saved to {out_path}")

    print(f"\n[DONE] Done — {posted_count} posted, {len(local_queue)} saved locally, {failed_count} failed")
    if not PIXABAY_API_KEY:
        print("\n[!]  REMINDER: Set PIXABAY_API_KEY to actually fetch real images.")
