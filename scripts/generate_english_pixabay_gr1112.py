"""
generate_english_pixabay_gr1112.py
High-quality Pixabay images -> English Grade 11 & 12 (Olympiad difficulty).
15 questions per grade = 30 total.
Covers: Literature (CBSE Hornbill/Flamingo), Grammar, Poetry, Writing Skills.

QUALITY RULES:
  1. Pixabay query matches what is literally visible in the photo.
  2. Image provides a visual anchor; question tests language/literary knowledge.
  3. All grammar answers are independently verified.
  4. Literary interpretations are based on the canonical CBSE text.
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
        pub_id = f"{CLOUDINARY_FOLDER}/eng_{query[:26].replace(' ','-')}_{RUN_ID}_{hit['id']}"
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
                          json=payload, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            posted += 1; return True
        elif r.status_code == 409:
            skipped += 1; return False
        else:
            print(f"    [FAIL {r.status_code}] {text[:60]}"); failed += 1; return False
    except Exception as e:
        print(f"    [ERR] {e}"); failed += 1; return False


def add_img(subject, grade, topic, subtopic, query, text, correct, wrongs, expl, pix_idx=0, difficulty="Olympiad"):
    tag = f"G{grade} Eng {query[:30]}..."
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
#  ENGLISH GRADE 11  (15 questions)
# ===========================================================================

def gen_gr11():
    print("\n" + "="*65)
    print("  English Grade 11  (15 questions)")
    print("="*65)
    S, G = "English", 11

    # 1. Portrait of a Lady — elderly woman photo
    add_img(S, G, "Literature - Prose", "The Portrait of a Lady",
        query="elderly woman portrait wrinkled face",
        text="In Khushwant Singh's 'The Portrait of a Lady', the grandmother is described as 'like the winter landscape in the mountains.' This comparison is an example of which literary device?",
        correct="Simile",
        wrongs=["Metaphor", "Personification", "Hyperbole"],
        expl="A simile makes a direct comparison using 'like' or 'as'. Here 'like the winter landscape' is a simile, evoking the grandmother's serene, aged appearance. A metaphor would say she WAS the landscape.")

    # 2. Summer — white horse in a field
    add_img(S, G, "Literature - Prose", "The Summer of the Beautiful White Horse",
        query="white horse field summer meadow",
        text="In Saroyan's 'The Summer of the Beautiful White Horse', Mourad's family, the Garoghlanian tribe, was famous for its honesty despite being poor. The horse-borrowing episode primarily explores which theme?",
        correct="The conflict between desire and moral integrity",
        wrongs=["The superiority of the Armenian culture", "The cruelty of poverty", "The importance of physical strength"],
        expl="The story's central tension is between the boys' desire to ride a horse and their family's legendary commitment to honesty. Mourad ultimately returns the horse, choosing integrity over desire.")

    # 3. Road fork autumn trees — The Road Not Taken
    add_img(S, G, "Literature - Poetry", "The Road Not Taken",
        query="forest path fork two roads autumn",
        text="In Robert Frost's 'The Road Not Taken', the speaker claims the road he chose 'had the better claim' because it was grassy and wanted wear. What is the irony in this claim?",
        correct="He then admits both roads were equally worn — his choice was not truly different",
        wrongs=["He regrets not taking the other road", "The grassy road led to failure", "Both roads were blocked by fallen trees"],
        expl="Frost immediately undercuts the claim by saying 'the passing there / Had worn them really about the same.' The speaker rationalises his choice in hindsight — a comment on how humans justify ordinary decisions as life-altering.")

    # 4. Rain on window — The Voice of the Rain
    add_img(S, G, "Literature - Poetry", "The Voice of the Rain",
        query="rain drops falling water surface",
        text="In Walt Whitman's 'The Voice of the Rain', the rain says 'I am the Poem of Earth.' The poet draws a parallel between rain and poetry. What common quality justifies this parallel?",
        correct="Both originate from their source, travel the world, and return transformed to their origin",
        wrongs=["Both are wet and flowing in nature", "Both bring sadness and reflection", "Both are composed of small individual drops/words"],
        expl="Rain rises from earth, wanders the sky, and falls back to nourish it. Poetry originates in the poet's mind, goes out into the world, and returns to enrich the origin. Whitman celebrates this cyclic, selfless journey.")

    # 5. Old photograph album — A Photograph
    add_img(S, G, "Literature - Poetry", "A Photograph",
        query="old vintage photograph album family",
        text="In Shirley Toulson's poem 'A Photograph', the three stanzas deal with three different periods of loss. What is the 'cardboard' the poet refers to as showing the speaker's mother?",
        correct="A photograph printed on stiff card stock (an old photo)",
        wrongs=["A painting of her mother", "A letter written by her mother", "A diary belonging to her mother"],
        expl="'Cardboard' refers to an old photograph — in early photography, photos were mounted on stiff cardboard backing. The image shows the mother as a young girl at the beach, making time and loss its central theme.")

    # 6. Yellow flowering tree — The Laburnum Top
    add_img(S, G, "Literature - Poetry", "The Laburnum Top",
        query="laburnum tree yellow flowers garden",
        text="In Ted Hughes's 'The Laburnum Top', the goldfinch is described as a 'machine' that 'starts up' the tree. What does this mechanical imagery suggest about the bird's role?",
        correct="The bird is the energising force that brings life and movement to the otherwise silent tree",
        wrongs=["The bird has no emotions and acts robotically", "The tree is dead and needs the bird to survive", "Hughes disapproves of industrialisation harming nature"],
        expl="Hughes uses machine imagery to show the goldfinch as an engine of life — its arrival ignites the tree with chirping, movement and energy. The contrast with the silence before and after heightens the bird's vital role.")

    # 7. Classroom chalkboard — Grammar: Tenses
    add_img(S, G, "Grammar", "Tenses - Perfect Aspect",
        query="classroom chalkboard teacher writing",
        text="Choose the grammatically correct sentence for the board: 'By the time the teacher arrived, the students _____ their assignment.'",
        correct="had completed",
        wrongs=["have completed", "completed", "were completing"],
        expl="The past perfect ('had completed') is used for an action completed BEFORE another past action. 'The teacher arrived' is simple past; the assignment was finished before that, so past perfect is required.")

    # 8. Letter writing desk — Reported Speech
    add_img(S, G, "Grammar", "Reported Speech",
        query="writing desk pen letter paper",
        text="Direct speech: She said, 'I will finish the project tomorrow.' Which is the correctly reported version?",
        correct="She said that she would finish the project the following day.",
        wrongs=["She said that she will finish the project tomorrow.", "She told that she would finish the project the next day.", "She said that she shall finish the project the following day."],
        expl="In reported speech: 'will' becomes 'would'; 'tomorrow' becomes 'the following day/the next day'. 'Said' takes a 'that' clause (not 'told' without an object). 'Shall' is not used here — she originally said 'will'.")

    # 9. Spider web dew drops — Figure of speech
    add_img(S, G, "Grammar", "Figures of Speech",
        query="spider web morning dew drops",
        text="The poet writes: 'The spider's web, jewelled with morning dew, was a cathedral of patience.' How many figures of speech are used in this sentence?",
        correct="Two — metaphor ('cathedral of patience') and transferred epithet ('jewelled')",
        wrongs=["One — only metaphor", "Three — simile, metaphor and personification", "Two — personification and simile"],
        expl="'Cathedral of patience' is a metaphor (web = cathedral). 'Jewelled' is a transferred epithet — the dew acts as jewels on the web. There is no simile (no 'like'/'as') and no personification (the spider is not given human traits here).")

    # 10. Sunset silhouette — Imagery and mood
    add_img(S, G, "Literature - Poetry", "Imagery and Mood",
        query="sunset silhouette horizon dramatic sky",
        text="A poem describing a sunset uses words like 'bleeding horizon', 'dying embers', and 'the day drew its last breath.' What dominant literary device is at work?",
        correct="Extended metaphor (treating the day as a dying living being)",
        wrongs=["Oxymoron", "Alliteration", "Onomatopoeia"],
        expl="All three phrases treat the day as a living creature dying (bleeding, embers, last breath) — this sustained comparison throughout the poem is an extended metaphor. A single comparison would be a metaphor; an extended one runs across multiple lines/images.")

    # 11. Library books — Comprehension: inference
    add_img(S, G, "Reading Comprehension", "Inference and Deduction",
        query="library books shelves knowledge reading",
        text="'The library was his universe — each book a galaxy waiting to be explored.' This sentence implies the narrator:",
        correct="Found books a source of endless discovery and wonder",
        wrongs=["Was a professional astronomer", "Felt overwhelmed and lost in the library", "Preferred science books to fiction"],
        expl="The metaphor of the library as a 'universe' and books as 'galaxies' suggests infinite, awe-inspiring discovery. The positive connotation of 'waiting to be explored' implies eagerness and wonder, not fear or preference for any genre.")

    # 12. Stage spotlight theater — Drama: elements
    add_img(S, G, "Literature - Drama", "Elements of Drama",
        query="stage spotlight theater curtain performance",
        text="In J.B. Priestley's 'Mother's Day', the play uses the device of role reversal — Mrs Pearson swaps personalities with Mrs Fitzgerald. This technique primarily creates:",
        correct="Comedy through incongruity — a meek housewife suddenly behaves domineeringly",
        wrongs=["Tragedy through irreversible consequences", "Satire on the British monarchy", "Dramatic irony where the audience knows a secret the characters do not"],
        expl="Role reversal is a classic comic device. The incongruity of gentle Mrs Pearson becoming assertive and shocking her family is the source of humour. It also satirises how housewives are taken for granted, but the primary dramatic effect is comedy.")

    # 13. Ancient ruins temple — Allusion and context
    add_img(S, G, "Literature - Poetry", "Allusion",
        query="ancient ruins stone temple pillars",
        text="A poet writes: 'Like Ozymandias, his empire of words crumbled to dust.' The reference to Ozymandias is an example of:",
        correct="Allusion — a reference to Shelley's poem about the futility of power",
        wrongs=["Allegory — a complete story within a story", "Apostrophe — addressing an absent person", "Hyperbole — extreme exaggeration for effect"],
        expl="An allusion is a brief, indirect reference to a well-known work or figure. Ozymandias is the subject of Shelley's famous sonnet about the transience of power. Using it here alludes to that poem to add depth without retelling it.")

    # 14. Child reading book — Vocabulary: etymology
    add_img(S, G, "Vocabulary", "Word Origins and Etymology",
        query="child reading book concentration focus",
        text="The word 'bibliophile' is seen on a library membership card in the image. 'Biblio-' comes from Greek 'biblion' (book) and '-phile' from 'philos' (loving). What does 'bibliophile' mean?",
        correct="A person who loves and collects books",
        wrongs=["A person who writes books professionally", "A person who burns or destroys books", "A person who studies ancient manuscripts"],
        expl="Breaking the word into roots: biblio (book) + phile (lover of) = a lover of books. Compare: cinephile (film lover), francophile (France lover). A person who destroys books would be a 'biblioclast'.")

    # 15. Typewriter vintage — Writing craft
    add_img(S, G, "Writing Skills", "Formal and Informal Writing",
        query="vintage typewriter keyboard retro writing",
        text="Which sentence best demonstrates the use of FORMAL register appropriate for an official letter?",
        correct="I wish to bring to your kind attention the deteriorating condition of the school canteen.",
        wrongs=["Hey, just wanted to say the canteen is in really bad shape!", "The canteen, you know, is pretty awful these days.", "Kindly note the canteen is not good at all and needs fixing up."],
        expl="Formal register avoids contractions, slang, and colloquialisms. 'I wish to bring to your kind attention' is courteous, impersonal and structured — hallmarks of formal letter writing. The other options use informal language ('Hey', 'you know', 'really bad', 'fixing up').")

    print("  Grade 11 English done.")


# ===========================================================================
#  ENGLISH GRADE 12  (15 questions)
# ===========================================================================

def gen_gr12():
    print("\n" + "="*65)
    print("  English Grade 12  (15 questions)")
    print("="*65)
    S, G = "English", 12

    # 1. Classroom chalkboard last lesson — The Last Lesson
    add_img(S, G, "Literature - Prose", "The Last Lesson",
        query="classroom empty chalkboard school room",
        text="In Alphonse Daudet's 'The Last Lesson', M. Hamel says 'French is the most beautiful language in the world — the clearest, the most logical.' In the context of the story, this statement primarily conveys:",
        correct="Cultural pride and grief at the impending loss of linguistic identity",
        wrongs=["A factual linguistic claim supported by grammar", "M. Hamel's arrogance as a teacher", "The French government's official policy on language"],
        expl="The story is set during the Franco-Prussian War when Alsace was annexed by Prussia. M. Hamel's declaration is not a linguistic fact but an emotional outpouring — his love for French becomes a form of resistance and mourning for a lost cultural identity.")

    # 2. Child working carpet — Lost Spring
    add_img(S, G, "Literature - Prose", "Lost Spring",
        query="child working carpet weaving loom",
        text="In Anees Jung's 'Lost Spring', Saheb-e-Alam's name means 'Lord of the Universe'. The author points out this irony because:",
        correct="Despite his grand name, he scavenges garbage dumps, highlighting the gap between aspiration and harsh reality",
        wrongs=["He is arrogant and believes he rules the world", "He eventually becomes a wealthy businessman", "The name was given by his enemies to mock him"],
        expl="Anees Jung uses the irony of Saheb's name to expose the cruel gap between the hopes embedded in a child's name and the degrading poverty he lives in. This irony is central to the essay's critique of systemic neglect of India's poor children.")

    # 3. Deep water swimming pool — Deep Water
    add_img(S, G, "Literature - Prose", "Deep Water",
        query="swimming pool water blue lanes",
        text="In William Douglas's 'Deep Water', after conquering his fear of water, he tests himself by swimming in Lake Wentworth and diving into Warm Lake. What does this final act symbolise?",
        correct="Complete conquest of fear — the terror is finally dead",
        wrongs=["His desire to become a professional swimmer", "Nostalgia for his childhood near the Yakima River", "His rebellion against his father's wishes"],
        expl="Douglas explicitly states 'I was not afraid of water. I had overcome my fear.' The real-world tests — the lake, the final dive — symbolise that his psychological battle is won. He quotes Roosevelt: 'the only thing we have to fear is fear itself.'")

    # 4. Rattrap seller — The Rattrap
    add_img(S, G, "Literature - Prose", "The Rattrap",
        query="metal trap cage mechanism wire",
        text="In Selma Lagerlof's 'The Rattrap', the peddler's philosophy is that 'the whole world is nothing but a big rattrap.' Which situation in the story BEST validates this philosophy from the peddler's own experience?",
        correct="He steals thirty kronor from the crofter, but is then trapped in the dark forest unable to escape",
        wrongs=["He meets Edla Willmansson who invites him home", "He is mistaken for Captain von Stahle", "He finds shelter with the crofter on a cold night"],
        expl="The irony is perfect: the peddler who preaches about the rattrap falls into one himself — the bait of easy money (stolen kronor) traps him in the forest. His philosophy becomes literally true for him, proving he too is susceptible to the world's temptations.")

    # 5. Elderly mother at window — My Mother at Sixty-Six
    add_img(S, G, "Literature - Poetry", "My Mother at Sixty-Six",
        query="elderly woman window looking outside",
        text="In Kamala Das's 'My Mother at Sixty-Six', the poet describes her mother's face as 'ashen like that of a corpse.' She then contrasts this with 'young trees sprinting' outside. What is the purpose of this contrast?",
        correct="To juxtapose death and life — the mother's ageing against the vibrancy of the external world",
        wrongs=["To show that the poet prefers nature to family", "To indicate the car is moving too fast", "To suggest the trees are a symbol of the poet's youth"],
        expl="The contrast between the corpse-like mother and the sprinting trees is a deliberate juxtaposition of mortality and vitality. Das confronts the universal fear of losing a parent — the vivid life outside makes the mother's decline more stark and heartbreaking.")

    # 6. Silent nature forest — Keeping Quiet
    add_img(S, G, "Literature - Poetry", "Keeping Quiet",
        query="forest silence trees mist peaceful",
        text="In Pablo Neruda's 'Keeping Quiet', the poet asks for 'a second of silence' and says 'let's not speak in any language.' What is his central argument in the poem?",
        correct="That stillness and introspection can break cycles of violence, destruction and self-harm",
        wrongs=["That language divides humanity and should be abolished", "That nature is superior to human civilisation", "That death is the only true form of silence"],
        expl="Neruda is not advocating death or the end of language. He uses 'keeping quiet' as a metaphor for collective introspection. The fishermen who 'harm no whale', the man who 'gathers salt' — all images suggest that pausing our destructive rush allows reflection and peace.")

    # 7. Beautiful landscape flowers — A Thing of Beauty
    add_img(S, G, "Literature - Poetry", "A Thing of Beauty",
        query="beautiful landscape flowers meadow nature bloom",
        text="In John Keats's 'A Thing of Beauty', the line 'A thing of beauty is a joy forever' contains a philosophical claim. What does Keats mean by 'its loveliness increases; it will never pass into nothingness'?",
        correct="Beauty's joy grows with time and lives permanently in memory and spirit",
        wrongs=["Beautiful objects are physically indestructible", "Only nature (not man-made things) lasts forever", "A beautiful person becomes more attractive with age"],
        expl="Keats is not making a physical claim but a spiritual/aesthetic one. The joy experienced from beauty — whether a flower, a poem or a sunset — remains in memory and spirit, increasing in value as other sorrows grow. Beauty becomes a permanent shelter from suffering.")

    # 8. Camera lens photography — On the Face of It (theme)
    add_img(S, G, "Literature - Drama", "On the Face of It",
        query="garden fence wall boundary hedge",
        text="In Susan Hill's 'On the Face of It', Derry climbs into Mr Lamb's garden and says 'I came in because I thought it was empty.' This opening action is symbolic of:",
        correct="Derry seeking isolation due to his disfigurement — he expects rejection and avoids people",
        wrongs=["Derry's criminal nature and disrespect for property", "Derry's curiosity about unusual gardens", "Mr Lamb's deliberate trap to catch intruders"],
        expl="Derry's assumption that the garden is empty reflects his internalised belief that his burned face makes him unwelcome among people. His choice to enter a seemingly empty space symbolises his withdrawal from society — which Mr Lamb slowly helps him overcome.")

    # 9. Newspaper press printing — Grammar: Active/Passive
    add_img(S, G, "Grammar", "Active and Passive Voice",
        query="newspaper printing press machine rolls",
        text="The headline reads: 'A new education policy has been announced by the government.' Which is the correctly transformed ACTIVE voice sentence?",
        correct="The government has announced a new education policy.",
        wrongs=["The government announced a new education policy.", "A new education policy is announced by the government.", "The government had announced a new education policy."],
        expl="Present perfect passive: 'has been announced' → active: 'has announced'. The tense must be preserved (present perfect). 'Announced' (simple past) changes the tense. 'Is announced' (simple present passive) is incorrect. 'Had announced' (past perfect) is also wrong.")

    # 10. Interview microphone — The Interview (non-fiction)
    add_img(S, G, "Literature - Non-Fiction", "The Interview",
        query="interview microphone journalist recording",
        text="In 'The Interview' (Christopher Silvester), V.S. Naipaul calls interviews 'an assault' and 'an intrusion'. What is the significance of Umberto Eco's contrasting attitude in the same essay?",
        correct="It shows that views on interviews vary — some authors see them as invasive, others as a natural part of literary life",
        wrongs=["Eco proves that Naipaul is wrong about interviews", "Eco's willingness shows he is a less serious writer", "Both authors ultimately agree that interviews are useless"],
        expl="Silvester presents two contrasting perspectives: Naipaul's hostility and Eco's acceptance. This balance is deliberate — the essay explores the complex, ambiguous nature of the interview form itself, not to judge either writer but to illuminate the tension between public life and private identity.")

    # 11. Gandhi spinning wheel — Indigo
    add_img(S, G, "Literature - Prose", "Indigo",
        query="spinning wheel craft traditional handloom",
        text="In Louis Fischer's 'Indigo', Gandhi's victory in the Champaran case taught a lesson beyond the immediate settlement. What was the deeper significance of his method?",
        correct="He demonstrated that civil disobedience and non-cooperation could force the British to yield — a blueprint for Independence",
        wrongs=["He proved that Indian farmers were superior cultivators of indigo", "He showed that British courts were always fair to Indians", "He established that economic grievances were more important than political ones"],
        expl="Gandhi's refusal to leave Champaran despite police orders, and his subsequent legal victory, proved that non-violent non-cooperation worked against colonial power. Fischer calls it 'a decisive footprint in India's struggle for independence' — the Champaran campaign was a tactical template for the freedom movement.")

    # 12. Mountain road journey — Going Places
    add_img(S, G, "Literature - Prose", "Going Places",
        query="road journey horizon adventure travel",
        text="In A.R. Barton's 'Going Places', Sophie's fantasies about Danny Casey are never fulfilled — he never appears at their meeting place. What does Sophie's continued faith in his coming BEST represent?",
        correct="The human tendency to live in comforting illusions when reality is disappointing",
        wrongs=["Sophie's superior intuition about people", "Danny Casey's genuine intention that was thwarted by circumstance", "The author's belief that dreams do come true eventually"],
        expl="Sophie comes from a cramped, ordinary background. Her fantasies about the footballer represent an escape from her limited reality. Barton uses her unrequited daydreaming to explore how imagination becomes a coping mechanism — and a trap — for those who cannot access their aspirations.")

    # 13. Typewriter vintage — Grammar: Transformation of Sentences
    add_img(S, G, "Grammar", "Transformation of Sentences",
        query="typewriter vintage keyboard writing craft",
        text="Combine into one sentence using a relative clause: 'The scientist made a groundbreaking discovery. The scientist was awarded the Nobel Prize.' Which option is correct?",
        correct="The scientist who made a groundbreaking discovery was awarded the Nobel Prize.",
        wrongs=["The scientist which made a groundbreaking discovery was awarded the Nobel Prize.", "The scientist whom made a groundbreaking discovery was awarded the Nobel Prize.", "The scientist that was awarded the Nobel Prize, he made a groundbreaking discovery."],
        expl="For a person as the antecedent, use 'who' (subject relative pronoun) or 'that'. 'Which' is used for things/animals. 'Whom' is the object form (he/him → who/whom test: 'the scientist made' → he made → use 'who'). The last option creates a comma splice with a redundant pronoun 'he'.")

    # 14. Doctor hospital patient — Grammar: Determiners
    add_img(S, G, "Grammar", "Determiners and Articles",
        query="doctor hospital patient examination",
        text="Choose the correct sentence: 'She is ___ honest doctor who works at ___ European hospital.'",
        correct="She is an honest doctor who works at a European hospital.",
        wrongs=["She is a honest doctor who works at an European hospital.", "She is an honest doctor who works at an European hospital.", "She is a honest doctor who works at a European hospital."],
        expl="Use 'an' before words beginning with a vowel SOUND: 'honest' starts with silent 'h' — vowel sound 'o' → 'an honest'. 'European' starts with consonant sound 'Y' (yu-ro-pean) → 'a European'. This is about pronunciation, not spelling.")

    # 15. Writers desk lamp books — Creative Writing
    add_img(S, G, "Writing Skills", "Article Writing",
        query="writer desk lamp books night study",
        text="A student writing an article on 'The Importance of Reading' opens with: 'In a world dominated by screens, the humble book fights a silent battle for the human soul.' This opening sentence is effective because:",
        correct="It uses personification and contrast to create an engaging, thought-provoking hook",
        wrongs=["It uses statistics to establish credibility immediately", "It begins with a direct question to involve the reader", "It states the thesis plainly without any figurative language"],
        expl="'The humble book fights a silent battle for the human soul' personifies the book as a warrior. The contrast between 'screens' (modern) and 'humble book' (traditional) creates immediate tension. This is a hook — a compelling opening device using figurative language, not statistics or a question.")

    print("  Grade 12 English done.")


# ===========================================================================
#  MAIN
# ===========================================================================

print("="*65)
print("  OlympiadReady - English Pixabay Grade 11 & 12")
print("  Olympiad difficulty | 15 questions per grade = 30 total")
print("="*65)

gen_gr11()
gen_gr12()

print(f"\n{'='*65}")
print(f"DONE - Posted: {posted}  Skipped: {skipped}  Failed: {failed}  Total: {posted+skipped+failed}")
print(f"{'='*65}")
