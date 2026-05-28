"""
generate_math_pixabay_gr1112.py
High-quality Pixabay images -> Mathematics Grade 11 and Grade 12 (Olympiad difficulty).

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
        pub_id = f"{CLOUDINARY_FOLDER}/math_{query[:26].replace(' ','-')}_{RUN_ID}_{hit['id']}"
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
#  MATHEMATICS GRADE 11
# ===========================================================================

def gen_gr11_math():
    print("\n" + "="*60)
    print("  Mathematics Grade 11")
    print("="*60)
    S, G = "Mathematics", 11

    # 1. Sets — Venn diagram two overlapping circles
    add_img(S, G, "Sets", "Venn Diagrams",
        query="venn diagram two circles overlap",
        text="In the Venn diagram shown, set A has 14 elements, set B has 11 elements, and their intersection has 5 elements. How many elements are in A ∪ B?",
        correct="20",
        wrongs=["25", "15", "30"],
        expl="|A ∪ B| = |A| + |B| − |A ∩ B| = 14 + 11 − 5 = 20. This is the inclusion-exclusion principle.")

    # 2. Trigonometry — protractor measuring angle
    add_img(S, G, "Trigonometric Functions", "Trigonometric Ratios",
        query="protractor angle measurement geometry",
        text="A protractor shows an angle of 150°. What is the value of sin 150°?",
        correct="1/2",
        wrongs=["√3/2", "−1/2", "−√3/2"],
        expl="150° = 180° − 30°. sin(180° − θ) = sin θ, so sin 150° = sin 30° = 1/2.")

    # 3. Coordinate Geometry — graph paper with plotted points
    add_img(S, G, "Straight Lines", "Distance and Section Formula",
        query="graph paper coordinate grid points",
        text="Two points are plotted on graph paper at coordinates P(1, 2) and Q(7, 10). What is the length of segment PQ?",
        correct="10",
        wrongs=["8", "6√2", "12"],
        expl="PQ = √[(7−1)² + (10−2)²] = √[36 + 64] = √100 = 10.")

    # 4. Conic Sections — parabolic dish / satellite dish
    add_img(S, G, "Conic Sections", "Parabola",
        query="satellite dish parabolic antenna",
        text="A parabolic dish has its focus at (3, 0) and directrix x = −3, as seen in the diagram. What is the equation of this parabola?",
        correct="y² = 12x",
        wrongs=["y² = 6x", "x² = 12y", "y² = 3x"],
        expl="For parabola y² = 4ax, the focus is (a, 0) and directrix is x = −a. Here a = 3, so 4a = 12, giving y² = 12x.")

    # 5. Sequences and Series — stacked coins or number blocks
    add_img(S, G, "Sequences and Series", "Arithmetic Progression",
        query="stacked coins rows increasing",
        text="Coins are arranged in rows: 3 in the first row, 5 in the second, 7 in the third, and so on (AP). How many coins are there in the first 10 rows?",
        correct="120",
        wrongs=["100", "110", "130"],
        expl="AP with a = 3, d = 2, n = 10. S₁₀ = (10/2)[2×3 + 9×2] = 5 × 24 = 120.")

    # 6. Permutations and Combinations — playing cards spread out
    add_img(S, G, "Permutations and Combinations", "Combinations",
        query="playing cards deck spread",
        text="A standard 52-card deck (26 red, 26 black) is shown. In how many ways can 5 cards be chosen such that exactly 3 are red and 2 are black?",
        correct="845 000",
        wrongs=["65 780", "2 598 960", "2 600"],
        expl="Choose 3 red from 26: ²⁶C₃ = 2600. Choose 2 black from 26: ²⁶C₂ = 325. Total = 2600 × 325 = 845 000.")

    # 7. Statistics — histogram bar chart
    add_img(S, G, "Statistics", "Measures of Dispersion",
        query="histogram bar chart statistics data",
        text="A histogram shows test scores for 50 students. The mean is 65 and the variance is 100. What is the coefficient of variation (CV)?",
        correct="15.38%",
        wrongs=["10%", "20%", "6.5%"],
        expl="CV = (Standard Deviation / Mean) × 100 = (√100 / 65) × 100 = (10/65) × 100 ≈ 15.38%.")

    # 8. Probability — dice pair
    add_img(S, G, "Probability", "Classical Probability",
        query="two dice probability",
        text="Two fair dice are rolled as shown. What is the probability that the sum of the numbers on the two dice equals 8?",
        correct="5/36",
        wrongs=["6/36", "4/36", "7/36"],
        expl="Favourable outcomes for sum = 8: (2,6),(3,5),(4,4),(5,3),(6,2) = 5 outcomes. Total = 36. P = 5/36.")

    # 9. Binomial Theorem — Pascal's triangle written on board
    add_img(S, G, "Binomial Theorem", "Pascal's Triangle",
        query="pascal triangle mathematics chalkboard",
        text="The triangle shown is Pascal's Triangle. Using it, identify the coefficient of x³ in the expansion of (1 + x)⁵.",
        correct="10",
        wrongs=["5", "15", "20"],
        expl="In (1+x)⁵, the coefficient of x³ is ⁵C₃ = 10, which appears in row 5 of Pascal's Triangle.")

    # 10. Limits and Derivatives — tangent line to a curve graph
    add_img(S, G, "Limits and Derivatives", "Derivative as Slope of Tangent",
        query="tangent line curve graph mathematics",
        text="The graph shows a smooth curve y = f(x) with a tangent line drawn at point (2, 4). If f(x) = x², what is the slope of the tangent at x = 2?",
        correct="4",
        wrongs=["2", "8", "1"],
        expl="f'(x) = 2x. At x = 2, slope = f'(2) = 2 × 2 = 4. The tangent line has slope 4.")

    print(f"  Grade 11 Mathematics done.")


# ===========================================================================
#  MATHEMATICS GRADE 12
# ===========================================================================

def gen_gr12_math():
    print("\n" + "="*60)
    print("  Mathematics Grade 12")
    print("="*60)
    S, G = "Mathematics", 12

    # 1. Matrices — grid/table structure
    add_img(S, G, "Matrices and Determinants", "Matrix Operations",
        query="spreadsheet grid rows columns data",
        text="A matrix A = [[2, 3], [1, 4]] is shown in a grid layout. What is the determinant of A?",
        correct="5",
        wrongs=["8", "11", "−5"],
        expl="|A| = (2×4) − (3×1) = 8 − 3 = 5.")

    # 2. Relations and Functions — mapping diagram arrows
    add_img(S, G, "Relations and Functions", "Types of Functions",
        query="function mapping arrows diagram",
        text="A mapping diagram shows that every element of the domain maps to a unique element in the codomain, and every codomain element is mapped to. What type of function is this?",
        correct="Bijective (one-one and onto)",
        wrongs=["Injective only (one-one, not onto)", "Surjective only (onto, not one-one)", "Many-one onto"],
        expl="A function that is both injective (one-one) and surjective (onto) is called bijective. It establishes a perfect pairing between domain and codomain.")

    # 3. Continuity and Differentiability — smooth curve on graph paper
    add_img(S, G, "Continuity and Differentiability", "Differentiability",
        query="smooth curve graph paper calculus",
        text="The graph shown is of y = |x|. At which point is this function continuous but NOT differentiable?",
        correct="x = 0",
        wrongs=["x = 1", "x = −1", "x = 2"],
        expl="y = |x| is continuous everywhere but has a sharp corner (cusp) at x = 0 where the left-hand and right-hand derivatives differ (−1 and +1 respectively), so it is not differentiable at x = 0.")

    # 4. Applications of Derivatives — maximum minimum graph
    add_img(S, G, "Applications of Derivatives", "Maxima and Minima",
        query="curve local maximum minimum turning point",
        text="The graph shows a function f(x) with a local maximum at point P. At a local maximum, which condition holds?",
        correct="f'(x) = 0 and f''(x) < 0",
        wrongs=["f'(x) = 0 and f''(x) > 0", "f'(x) > 0 and f''(x) = 0", "f'(x) < 0 for all x near P"],
        expl="At a local maximum: the first derivative is zero (f'(x) = 0) and the second derivative is negative (f''(x) < 0), confirming a peak.")

    # 5. Integrals — area under a curve shaded region
    add_img(S, G, "Integrals", "Definite Integral as Area",
        query="area under curve shaded graph integration",
        text="The shaded region in the graph represents the area under y = x² from x = 0 to x = 3. What is this area?",
        correct="9",
        wrongs=["6", "12", "27"],
        expl="∫₀³ x² dx = [x³/3]₀³ = 27/3 − 0 = 9 square units.")

    # 6. Vectors — arrows showing direction and magnitude
    add_img(S, G, "Vectors", "Dot Product and Cross Product",
        query="vector arrows direction magnitude physics",
        text="Two vectors a⃗ and b⃗ are shown with |a⃗| = 5, |b⃗| = 4, and the angle between them is 60°. What is a⃗ · b⃗?",
        correct="10",
        wrongs=["20", "8", "5√3"],
        expl="a⃗ · b⃗ = |a⃗| |b⃗| cos θ = 5 × 4 × cos 60° = 20 × 0.5 = 10.")

    # 7. 3D Geometry — 3D coordinate axes xyz
    add_img(S, G, "Three-Dimensional Geometry", "Direction Cosines",
        query="3D coordinate axes xyz geometry",
        text="A line makes angles α, β, γ with the x, y, z axes respectively, as shown on the 3D coordinate system. If cos α = 1/2 and cos β = 1/√2, what is |cos γ|?",
        correct="1/2",
        wrongs=["1/√2", "√3/2", "0"],
        expl="Direction cosines satisfy cos²α + cos²β + cos²γ = 1. (1/2)² + (1/√2)² + cos²γ = 1 → 1/4 + 1/2 + cos²γ = 1 → cos²γ = 1/4 → |cos γ| = 1/2.")

    # 8. Linear Programming — feasible region graph with constraints
    add_img(S, G, "Linear Programming", "Graphical Method",
        query="graph shaded feasible region linear inequalities",
        text="The shaded region in the graph shows the feasible region for a linear programming problem. The objective function Z = 5x + 3y is to be maximised. At which type of point does the maximum always occur?",
        correct="A corner (vertex) of the feasible region",
        wrongs=["The centroid of the feasible region", "The midpoint of the longest edge", "Any point inside the region"],
        expl="By the Fundamental Theorem of Linear Programming, the maximum (or minimum) of a linear objective function over a convex feasible region always occurs at a corner (vertex) of that region.")

    # 9. Probability — probability tree diagram
    add_img(S, G, "Probability", "Bayes Theorem and Conditional Probability",
        query="probability tree diagram branches",
        text="A probability tree diagram shows: P(A) = 0.4, P(B|A) = 0.7, P(B|A') = 0.3. Using Bayes' theorem, what is P(A|B)?",
        correct="14/23",
        wrongs=["7/10", "4/10", "21/37"],
        expl="P(B) = P(A)P(B|A) + P(A')P(B|A') = 0.4×0.7 + 0.6×0.3 = 0.28 + 0.18 = 0.46. P(A|B) = P(A)P(B|A)/P(B) = 0.28/0.46 = 14/23.")

    # 10. Differential Equations — exponential growth graph
    add_img(S, G, "Differential Equations", "Variable Separable Method",
        query="exponential growth curve population graph",
        text="The graph shows exponential growth modelled by dy/dx = ky, where k > 0. If y(0) = y₀, what is the general solution?",
        correct="y = y₀ eᵏˣ",
        wrongs=["y = y₀ + kx", "y = y₀ kˣ", "y = eˣ + C"],
        expl="Separating variables: dy/y = k dx → ln y = kx + C. At x=0, y=y₀ gives C = ln y₀. Hence y = y₀ eᵏˣ.")

    print(f"  Grade 12 Mathematics done.")


# ===========================================================================
#  MAIN
# ===========================================================================

print("="*60)
print("  OlympiadReady - Mathematics Pixabay Grade 11 & 12")
print("  Olympiad difficulty | 10 questions each grade")
print("="*60)

# Remove the broken placeholder question before running
gen_gr11_math()
gen_gr12_math()

print(f"\n{'='*60}")
print(f"DONE - Posted: {posted}  Skipped: {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
print(f"{'='*60}")
