"""
generate_science_pixabay_gr678.py
Real Pixabay photos -> Cloudinary -> Science image questions
Targets: Grades 6, 7, 8 Science (all had 0 images)
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
        pub_id = f"{CLOUDINARY_FOLDER}/sci678_{query[:26].replace(' ','-')}_{RUN_ID}_{hit['id']}"
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
# GRADE 6 SCIENCE
# =============================================================================
GR6_SCIENCE = [
    ("G6 Sci plant parts",
     "plant parts roots stem leaves flower",
     6, "Advanced", "Science", "Living World", "Parts of a Plant",
     "The image shows the different parts of a plant. Which part of the plant absorbs water and minerals from the soil?",
     ["Roots", "Leaves", "Stem", "Flowers"], 0,
     "Roots anchor the plant and absorb water and dissolved minerals from the soil through tiny root hair cells. These are then transported upward through the stem."),

    ("G6 Sci magnet iron filings",
     "magnet iron filings magnetic field science",
     6, "Advanced", "Science", "Magnetism", "Magnets & Magnetic Fields",
     "The image shows a magnet attracting iron filings. Which materials are attracted to a magnet?",
     ["Iron, nickel, and cobalt (magnetic materials)", "All metals including copper and gold", "Wood and plastic", "Water and glass"], 0,
     "Only ferromagnetic materials (iron, nickel, cobalt, and their alloys like steel) are attracted to magnets. Non-magnetic metals like copper, gold, aluminium are NOT attracted."),

    ("G6 Sci water cycle diagram",
     "water cycle evaporation rain cloud nature",
     6, "Advanced", "Science", "Our Environment", "Water Cycle",
     "The image shows the water cycle. Water evaporates from oceans and rises as vapour. As it cools at higher altitudes, it forms clouds through the process of:",
     ["Condensation", "Evaporation", "Transpiration", "Precipitation"], 0,
     "Condensation: water vapour cools and converts to tiny water droplets that form clouds. When droplets combine and become heavy, they fall as precipitation (rain/snow)."),

    ("G6 Sci food groups nutrition",
     "food groups nutrition healthy diet vegetables",
     6, "Foundation", "Science", "Health & Nutrition", "Balanced Diet",
     "The image shows various food groups. Which nutrient is the PRIMARY source of energy for the body?",
     ["Carbohydrates", "Proteins", "Vitamins", "Minerals"], 0,
     "Carbohydrates (found in rice, wheat, bread, potatoes) are the body's primary and most readily available energy source. Proteins build and repair tissue; vitamins and minerals regulate body functions."),

    ("G6 Sci microscope biology",
     "microscope laboratory science biology school",
     6, "Olympiad", "Science", "Living World", "Cell Biology",
     "The image shows a microscope. Who invented the first simple microscope and first observed cells?",
     ["Robert Hooke (1665) observed cells; Antonie van Leeuwenhoek improved microscopes", "Charles Darwin", "Louis Pasteur", "Gregor Mendel"], 0,
     "Robert Hooke (1665) first observed and named 'cells' in cork under a microscope. Antonie van Leeuwenhoek made the first powerful single-lens microscopes and observed bacteria and protozoa."),

    ("G6 Sci simple machines lever",
     "simple machines lever fulcrum physics",
     6, "Advanced", "Science", "Force & Motion", "Simple Machines",
     "The image shows a lever (like a seesaw). A lever makes work easier by:",
     ["Multiplying the applied force or changing its direction using a fulcrum", "Reducing the amount of work done", "Increasing the distance the load moves always", "Creating energy from nothing"], 0,
     "A lever is a simple machine with a rigid bar pivoting at a fulcrum. It can multiply force (Class 1&2 levers) or multiply speed/distance (Class 3 levers). It does NOT reduce total work — it changes force and distance."),

    ("G6 Sci solar system planets",
     "solar system planets space astronomy",
     6, "Advanced", "Science", "Space Science", "Solar System",
     "The image shows our solar system. Which is the largest planet in the solar system?",
     ["Jupiter", "Saturn", "Neptune", "Uranus"], 0,
     "Jupiter is the largest planet — its mass is greater than all other planets combined. It has at least 95 known moons, including the four large Galilean moons."),

    ("G6 Sci shadow light torch",
     "shadow light torch experiment science",
     6, "Foundation", "Science", "Light", "Shadows & Light",
     "The image shows a torch casting a shadow of an object. A shadow is formed because light:",
     ["Travels in straight lines and cannot bend around opaque objects", "Bounces off all surfaces", "Bends around every object", "Is absorbed by the ground"], 0,
     "Light travels in straight lines (rectilinear propagation). When an opaque object blocks light, a shadow forms behind it where light cannot reach."),

    ("G6 Sci rainfall India monsoon",
     "monsoon rain India rainfall season",
     6, "Advanced", "Science", "Weather & Climate", "Monsoon",
     "The image shows heavy monsoon rain in India. The Indian monsoon brings rainfall mainly from which direction?",
     ["South-West (Arabian Sea and Bay of Bengal)", "North-East", "North-West", "South-East only"], 0,
     "The South-West Monsoon (June–September) brings over 70% of India's annual rainfall. Moisture-laden winds from the Arabian Sea and Bay of Bengal are deflected northward by the Himalayas."),

    ("G6 Sci recycling waste management",
     "recycling waste management environment green",
     6, "Foundation", "Science", "Environment", "Waste & Conservation",
     "The image shows recycling bins. The 3R principle for waste management stands for:",
     ["Reduce, Reuse, Recycle", "Remove, Replace, Rebuild", "Reclaim, Restore, Renew", "Reduce, Remove, Reclaim"], 0,
     "The 3Rs: Reduce (use less), Reuse (use again), Recycle (process into new materials). This hierarchy reduces environmental impact — reducing is better than reusing, which is better than recycling."),
]

# =============================================================================
# GRADE 7 SCIENCE
# =============================================================================
GR7_SCIENCE = [
    ("G7 Sci acid litmus indicator",
     "acid base indicator chemistry litmus test",
     7, "Advanced", "Science", "Chemistry", "Acids & Bases",
     "The image shows litmus paper tests. Blue litmus paper turned RED when dipped in a liquid. This indicates the liquid is:",
     ["Acidic (pH below 7)", "Basic (alkaline)", "Neutral (pH = 7)", "Pure water"], 0,
     "Blue litmus turns red in acidic solutions (pH < 7). Red litmus turns blue in basic/alkaline solutions (pH > 7). Neutral solutions do not change either litmus colour."),

    ("G7 Sci human skeleton bones",
     "human skeleton bones anatomy body",
     7, "Advanced", "Science", "Human Body", "Skeletal System",
     "The image shows the human skeleton. The human skeleton has approximately how many bones in an adult?",
     ["206", "300", "150", "350"], 0,
     "An adult human has 206 bones. Babies are born with ~270 bones that fuse during growth. The femur (thigh bone) is the longest and strongest bone."),

    ("G7 Sci electric current bulb",
     "electric circuit bulb current battery simple",
     7, "Advanced", "Science", "Electricity", "Electric Current",
     "The image shows a simple electric circuit with a bulb. The bulb glows only when the circuit is:",
     ["Complete (closed) — allowing current to flow continuously", "Open (broken) — no current flows", "Connected to only one wire", "Placed in water"], 0,
     "Electric current flows only in a closed (complete) circuit. If there is a break anywhere (open circuit), current stops and the bulb goes out."),

    ("G7 Sci weather instruments thermometer",
     "weather instruments thermometer barometer meteorology",
     7, "Foundation", "Science", "Weather & Climate", "Weather Instruments",
     "The image shows weather measuring instruments. Which instrument measures atmospheric pressure?",
     ["Barometer", "Thermometer", "Rain gauge", "Anemometer"], 0,
     "Barometer measures atmospheric pressure. Thermometer measures temperature. Rain gauge measures rainfall. Anemometer measures wind speed."),

    ("G7 Sci habitat forest animals",
     "forest habitat animals biodiversity wildlife India",
     7, "Advanced", "Science", "Living World", "Habitats",
     "The image shows a forest habitat. Animals are adapted to their habitat. Which adaptation helps a fish survive in water?",
     ["Streamlined body and gills to extract dissolved oxygen from water", "Thick fur to retain heat", "Long legs to run fast", "Wings to fly above water"], 0,
     "Fish are adapted to aquatic life: streamlined body reduces water resistance; gills extract dissolved O2 from water; fins provide movement and balance; scales protect and reduce friction."),

    ("G7 Sci nutrition plants chlorophyll",
     "chlorophyll green plants leaves sunlight",
     7, "Olympiad", "Science", "Living World", "Plant Nutrition",
     "The image shows green leaves in sunlight. Leaves appear green because chlorophyll:",
     ["Absorbs red and blue light, reflecting green light back to our eyes", "Produces green-coloured water", "Contains green-coloured minerals", "Absorbs green light and reflects red and blue"], 0,
     "Chlorophyll absorbs mainly red (650-700nm) and blue (430-450nm) wavelengths of light for photosynthesis. It reflects green wavelengths, which is why leaves appear green."),

    ("G7 Sci wind energy windmill",
     "wind energy windmill turbine renewable India",
     7, "Advanced", "Science", "Energy", "Renewable Energy",
     "The image shows wind turbines. Wind energy is considered a renewable source of energy because:",
     ["Wind is a natural resource that replenishes continuously and will not run out", "Wind turbines create energy from nothing", "Wind energy produces no electricity", "It is stored in batteries permanently"], 0,
     "Renewable energy comes from sources that naturally replenish — wind, solar, hydroelectric, geothermal. Fossil fuels (coal, oil, gas) are non-renewable as they take millions of years to form."),

    ("G7 Sci digestive system stomach",
     "digestive system stomach intestine human body",
     7, "Advanced", "Science", "Human Body", "Digestive System",
     "The image shows the human digestive system. Which digestive juice is produced by the stomach that begins protein digestion?",
     ["Gastric juice (containing pepsin and HCl)", "Bile (from liver)", "Saliva (from mouth)", "Pancreatic juice"], 0,
     "The stomach produces gastric juice containing: pepsin (enzyme that digests proteins) and hydrochloric acid (HCl, pH~2 that kills bacteria and activates pepsin)."),

    ("G7 Sci friction force surface",
     "friction force surface rough smooth physics",
     7, "Advanced", "Science", "Force & Motion", "Friction",
     "The image shows surfaces with different textures. Friction between two surfaces depends on:",
     ["The roughness of surfaces AND the force pressing them together (normal force)", "Only the weight of the object", "Only the speed of movement", "The colour of the surfaces"], 0,
     "Friction force = coefficient of friction x normal force. It depends on: (1) surface roughness/texture, (2) normal force pressing surfaces together. Speed and colour do not directly determine friction."),

    ("G7 Sci reproduction animals eggs",
     "animals reproduction eggs nature wildlife",
     7, "Foundation", "Science", "Living World", "Reproduction",
     "The image shows animals reproducing by laying eggs. Animals that lay eggs are called:",
     ["Oviparous (egg-laying)", "Viviparous (give birth to live young)", "Ovoviviparous", "Asexual reproducers"], 0,
     "Oviparous = egg-laying (birds, reptiles, fish, insects, amphibians). Viviparous = give birth to live young (most mammals). Ovoviviparous = eggs hatch inside the mother (some sharks)."),
]

# =============================================================================
# GRADE 8 SCIENCE
# =============================================================================
GR8_SCIENCE = [
    ("G8 Sci chemical reaction combustion",
     "combustion fire chemical reaction burning",
     8, "Advanced", "Science", "Chemistry", "Chemical Reactions",
     "The image shows combustion (burning). Combustion is a chemical reaction where a substance reacts with oxygen and produces:",
     ["Heat, light, and usually carbon dioxide and water", "Only smoke", "Cold temperatures", "New metals"], 0,
     "Combustion: fuel + O2 -> CO2 + H2O + heat + light (for complete combustion). Incomplete combustion produces CO (carbon monoxide) and soot. This is an exothermic oxidation reaction."),

    ("G8 Sci cell plant animal",
     "plant animal cell biology microscope comparison",
     8, "Olympiad", "Science", "Biology", "Cell Biology",
     "The image shows plant and animal cells under a microscope. Which structure is present in plant cells but ABSENT in animal cells?",
     ["Cell wall and large central vacuole", "Cell membrane", "Nucleus", "Mitochondria"], 0,
     "Plant cells have: cell wall (rigid, cellulose), large central vacuole, chloroplasts. Animal cells lack all three. Both have cell membrane, nucleus, mitochondria, ribosomes, ER."),

    ("G8 Sci force motion Newton",
     "force motion ball rolling physics Newton",
     8, "Olympiad", "Science", "Physics", "Forces & Motion",
     "The image shows a ball in motion. According to Newton's First Law, a moving ball will continue moving in a straight line UNLESS:",
     ["An external force acts on it (e.g., friction, gravity, collision)", "It decides to stop on its own", "The air temperature changes", "It reaches a certain speed"], 0,
     "Newton's First Law (Inertia): an object in motion stays in motion at constant velocity unless acted upon by a net external force. The ball slows due to friction and gravity, not on its own."),

    ("G8 Sci pollution factory smoke",
     "pollution factory chimney smoke air quality",
     8, "Advanced", "Science", "Environment", "Pollution",
     "The image shows factory smoke causing air pollution. Which gas produced by burning fossil fuels is a major contributor to acid rain?",
     ["Sulphur dioxide (SO2)", "Nitrogen (N2)", "Oxygen (O2)", "Argon (Ar)"], 0,
     "SO2 (from burning coal/oil containing sulphur) + water vapour -> sulphurous/sulphuric acid -> acid rain. NOx (from vehicles) also contributes. Acid rain damages forests, soil, and buildings."),

    ("G8 Sci lens eye optics",
     "human eye lens optics retina anatomy",
     8, "Advanced", "Science", "Physics", "Light & Optics",
     "The image shows the human eye. The image of an object is formed on which part of the eye?",
     ["Retina", "Cornea", "Lens", "Iris"], 0,
     "The retina (back of the eye) contains photoreceptors (rods and cones). The cornea and lens focus light onto the retina. The image is inverted on the retina but the brain corrects it."),

    ("G8 Sci rock types geology",
     "rock types geology igneous sedimentary metamorphic",
     8, "Advanced", "Science", "Earth Science", "Rocks & Minerals",
     "The image shows different types of rocks. Rocks formed from cooled and solidified magma (molten rock) are called:",
     ["Igneous rocks", "Sedimentary rocks", "Metamorphic rocks", "Fossil rocks"], 0,
     "Igneous rocks form from solidified magma/lava (e.g., granite, basalt). Sedimentary form from compressed sediments (sandstone, limestone). Metamorphic form when existing rocks are transformed by heat and pressure (marble, slate)."),

    ("G8 Sci solar eclipse moon",
     "solar eclipse moon shadow sun astronomy",
     8, "Advanced", "Science", "Space Science", "Eclipses",
     "The image shows a solar eclipse. A solar eclipse occurs when:",
     ["The Moon comes between the Earth and Sun, blocking sunlight", "The Earth comes between the Moon and Sun", "The Sun moves behind the Moon", "Clouds block the Sun completely"], 0,
     "Solar eclipse: Moon (new moon phase) aligns between Earth and Sun, casting a shadow on Earth. Total solar eclipse visible only in a narrow path. Lunar eclipse: Earth comes between Sun and Moon."),

    ("G8 Sci sound vibration music",
     "sound vibration music instrument string waves",
     8, "Advanced", "Science", "Physics", "Sound",
     "The image shows a vibrating string producing sound. Sound is a form of energy that travels as:",
     ["Longitudinal (compression) waves through a medium", "Transverse waves like light", "Electromagnetic waves in vacuum", "Heat waves through air"], 0,
     "Sound is a mechanical longitudinal wave — particles vibrate parallel to the direction of wave travel, creating compressions and rarefactions. Sound needs a medium (cannot travel through vacuum)."),

    ("G8 Sci microorganisms bacteria",
     "microorganisms bacteria fungi microscope biology",
     8, "Advanced", "Science", "Biology", "Microorganisms",
     "The image shows microorganisms under a microscope. Which of the following is a BENEFICIAL use of microorganisms?",
     ["Making curd, bread, antibiotics, and decomposing waste", "Causing all diseases", "Only producing toxins", "Breaking down ozone layer"], 0,
     "Microorganisms are essential: Lactobacillus makes curd; yeast makes bread/alcohol; Penicillium mould produces penicillin antibiotics; decomposers recycle nutrients. Only some microorganisms are harmful pathogens."),

    ("G8 Sci reproduction flower fertilisation",
     "flower reproduction fertilisation pollen stamen pistil",
     8, "Olympiad", "Science", "Biology", "Reproduction in Plants",
     "The image shows a flower's reproductive parts. After pollination, fertilisation in a flower occurs when:",
     ["A pollen grain's male nucleus fuses with the egg cell in the ovule", "The petal falls off", "The fruit ripens and falls", "The bee carries pollen away"], 0,
     "After a pollen grain lands on the stigma (pollination), it grows a pollen tube down to the ovule. The male nucleus travels down the tube and fuses with the egg cell (fertilisation) → zygote → seed."),
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
    print("  OlympiadReady - Science Pixabay (Grades 6, 7, 8)")
    total = len(GR6_SCIENCE) + len(GR7_SCIENCE) + len(GR8_SCIENCE)
    print(f"  Total questions: {total}")
    print("=" * 60)

    run_batch("Grade 6 Science", GR6_SCIENCE)
    run_batch("Grade 7 Science", GR7_SCIENCE)
    run_batch("Grade 8 Science", GR8_SCIENCE)

    print(f"\n{'='*60}")
    print(f"DONE - Posted: {posted}  Skipped(dup): {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
    print(f"{'='*60}")
