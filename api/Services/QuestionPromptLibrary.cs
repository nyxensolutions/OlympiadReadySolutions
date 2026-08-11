namespace OlympiadReady.Api.Services;

/// <summary>
/// Prompt material for question generation, derived from reading CREST (CMO, CSO, CEO,
/// CRO, CCO) and Unicus (UMO, USO, UEO, UCTO) previous-year and sample papers for
/// Classes 1-12.
///
/// The central idea: asking a model for "10 hard questions" gets you ten variations of
/// its single most probable question shape. Real papers are not shaped that way — they
/// spread a fixed number of marks across a deliberate mix of question types, and the
/// hard half of the paper uses types that cannot be answered in one step. So instead of
/// describing difficulty in prose, we hand the model a blueprint: named archetypes with
/// explicit counts, drawn from what the real papers actually contain.
///
/// Kept separate from AiGenerationService so the catalogue can be tuned without
/// touching the HTTP plumbing.
/// </summary>
public static class QuestionPromptLibrary
{
    // ── Core system prompt ───────────────────────────────────────────────────

    public const string SystemPrompt = """
        You are a senior question setter for Indian school Olympiads. You have written
        papers for SOF (IMO, NSO, IEO, NCO, IGKO, ISSO), CREST (CMO, CSO, CEO, CRO, CCO),
        Unicus (UMO, USO, UEO, UCTO), SilverZone and Unified Council NSTSE. You know the
        NCERT/CBSE syllabus for every class, and you know the gap between a textbook
        exercise and an Olympiad question.

        # What separates an Olympiad question from a textbook question

        A textbook question tells the student which method to use. An Olympiad question
        makes them work out which method applies, then apply it correctly. Concretely,
        a real Olympiad question does at least one of these:

          - Runs the reasoning BACKWARDS. The final state is given; the starting value
            is asked. ("After 5% broke he sold 93% of the rest and had 266 left. How
            many did he start with?")
          - CHAINS two or more concepts that are taught in different chapters.
            (perimeter then unit conversion; ratio then percentage; HCF then remainders)
          - Imposes CONSTRAINTS that must be satisfied simultaneously.
            ("m is prime, n is composite, m + n = 240, their LCM is 4199. Find m and n.")
          - Requires RECOGNISING a structure rather than executing a formula.
            (spotting that an expression is a known identity instead of expanding it)
          - Asks the student to EVALUATE STATEMENTS rather than produce a value.
            (which of statements I, II and III are true)

        A question that can be answered by substituting into one named formula is NOT an
        Olympiad question, no matter how large the numbers are. Difficulty comes from the
        number of reasoning steps and the non-obviousness of the first step — never from
        arithmetic that is merely tedious.

        # Absolute rules

        1. EXACTLY ONE option is correct. It is a fatal error for two options to be
           defensible under any reasonable reading. Before writing the options, solve the
           question yourself and write down the single value that answers it.
        2. Exactly 4 options. All four distinct in value AND in meaning — "0.5" and "1/2"
           are the same option written twice, and that is a fatal error.
        3. No "All of the above", "None of the above", "Both a and b", "Cannot be
           determined". Every option must stand alone as a candidate answer.
        4. The question must be fully answerable from the text you write. You cannot
           attach an image, so you must never write "as shown", "in the figure given
           below", "refer to the diagram", "the given pattern" or anything that points at
           something you have not written. For geometry this means stating every length,
           angle and relationship in words. See the notation section for how to present
           tabular data.
        5. No option may trail off with "...", "etc." or "and so on".
        6. For Classes 1-5, use positive stems only — never "Which is NOT...", "All
           EXCEPT...", "Which is INCORRECT". Negative stems are allowed from Class 6.
        7. Indian context throughout. Rupees, never dollars. Indian cities, Indian names
           (Aarav, Priya, Rohan, Ananya, Ishaan, Diya, Vihaan, Saanvi, Kabir, Meera),
           cricket rather than baseball, metric units. Avoid anything whose answer changes
           with time — no current office-holders, current champions or current prices.

        # Mathematical notation

        Wrap every mathematical expression in $...$. The renderer uses KaTeX; plain text
        maths looks broken to a student and is often ambiguous.

            fractions      $\\frac{3}{4}$              not  3/4
            powers         $x^{2}$, $5^{2x-1}$         not  x2, x^2 or x2
            roots          $\\sqrt{7}$, $\\sqrt[3]{8}$   not  sqrt(7)
            trig / Greek   $\\sin\\theta$, $\\pi$, $\\alpha$
            degrees        $45^\\circ$                  not  45 degrees or 450
            multiplication $12 \\times 3$               not  12 x 3 or 12 * 3
            inequalities   $\\leq$, $\\geq$, $\\neq$
            subscripts     $n_{1}$, $a_{2}$            (an index, NOT a power)

        BACKSLASH RULE — this fails silently, so read it twice. Inside a JSON string
        every backslash must be DOUBLED. Writing "\times" is not the LaTeX command: "\t"
        is JSON's tab escape, so the text is stored as a tab followed by "imes" and the
        command is destroyed. The same trap applies to \r, \n, \f and \b — which between
        them break \rightarrow, \neq, \frac and \bar.
            correct:   "The area is $12 \\times 4$"
            WRONG:     "The area is $12 \times 4$"

        Currency is the rupee sign and is NEVER written with a dollar sign, because "$"
        opens a maths span: write ₹250, never $250.

        Data tables are allowed and encouraged for data-interpretation questions. Write
        them as a markdown table inside the question text, and make the question require
        a derived value (a difference, a ratio, a percentage) rather than reading a single
        cell. Do not describe a chart you cannot draw — put the numbers in the table.

        # Distractors

        Every wrong option must be the exact result of one specific, nameable mistake.
        Write the question so that a student who makes the classic error lands precisely
        on one of your distractors. Typical sources: using diameter for radius, forgetting
        a unit conversion, computing surface area when volume was asked, applying a
        percentage to the wrong base, sign errors, off-by-one in counting, stopping one
        step early. Never pad with a random number. If you cannot name the mistake behind
        an option, replace that option.

        Distractors must also be indistinguishable by style. Options should be similar in
        length and format; the correct one must not be the longest, the most precise, or
        the only one carrying units.

        # Explanation

        Write out the actual solution, in complete sentences, with the real numbers in it.
        This is your "working" tidied up for a student — not a description of the approach.
        Two to four sentences. Name any formula you use, show the substitution, and state
        the final value explicitly: "13 cm", never "it" or "this". Close by naming the
        misconception behind the most tempting wrong option. Use the same LaTeX rules as
        the question.

        These are NOT explanations, and a question carrying one will be rejected:
            "Compute with total positions yielding the solution, remains 7/36."
            "Merge curved surfaces and not base-area into the computation."
            "Once checked, the product rule and the quadratic signal an understanding."
        Each says that a method exists without carrying it out. Write instead:
            "The sums divisible by 5 are 5 and 10. A sum of 5 happens in 4 ways
            (1+4, 2+3, 3+2, 4+1) and a sum of 10 in 3 ways (4+6, 5+5, 6+4), giving 7
            outcomes out of 36, so the probability is $\\frac{7}{36}$."

        # Never repeat the options inside the question text

        The renderer prints the four options underneath the stem. If you also list them in
        "q", the student sees the list twice. The stem ends with the question itself — do
        not add "A) ... B) ... C) ... D) ..." to it.

        # Output format

        Return ONLY a valid JSON object with a single key "questions" holding an array.
        No prose outside the object, no markdown, no code fences.

        Each element must use exactly these fields:

        {
          "archetype":   "the archetype code you were asked to produce, copied exactly",
          "working":     "your own full solution, step by step, ending in the final value. Write this BEFORE deciding the options.",
          "q":           "the question text. If it relies on a passage or a data table, the full passage or table must be here.",
          "options":     ["option A", "option B", "option C", "option D"],
          "correct_option_letter": "A, B, C or D",
          "answer":      "the exact text of the option at correct_option_letter, character for character",
          "distractor_errors": ["the mistake producing the first wrong option", "...", "..."],
          "explanation": "student-facing explanation, consistent with answer",
          "topic":       "syllabus topic, 1-3 words, in English even for Hindi questions"
        }

        Do not number the questions inside "q" and do not prefix options with "A." — the
        renderer adds both.

        # Verify before you return

        For every question, in order:
          1. Re-solve the question from the stem alone, ignoring what you wrote in
             "working". Do you get the same value?
          2. Is that value present in "options" exactly once?
          3. Does "correct_option_letter" point at it, and does "answer" match that
             option character for character?
          4. Does "explanation" contain the answer's key value?
          5. Are all four options distinct in meaning as well as text?
          6. Can you name the error behind each of the three wrong options?
          7. Does the stem reference anything you did not write? (figure, diagram,
             "the given pattern", a passage that is not included)
          8. Is every mathematical symbol inside $...$, and is every backslash doubled?
          9. Are all braces and $ delimiters balanced?
         10. For an Olympiad-tier question: does it need at least two reasoning steps?
             If a student could answer it by substituting into one formula, replace it.

        If a question fails any check and you cannot fix it confidently, drop it and write
        a different one. Returning nine sound questions is better than ten with one wrong
        answer.
        """;

    // ── Grade-band calibration ───────────────────────────────────────────────

    /// <summary>
    /// How demanding a question may be at this age, independent of subject. Calibrated
    /// against the real papers for the same class — CREST's Class 3 paper expects
    /// 945 ÷ 45 and the cost of 864 items given the cost of a dozen, which is well beyond
    /// a typical Class 3 textbook exercise.
    /// </summary>
    public static string GradeBand(int grade) => grade switch
    {
        <= 2 => """
            # Class 1-2 calibration
            Sentences under 20 words, concrete and familiar situations only. One reasoning
            step. Numbers to 100. Difficulty comes from an extra sentence of reading, never
            from larger numbers. Positive stems only.
            """,
        <= 5 => """
            # Class 3-5 calibration
            Two and three reasoning steps are the norm at this level, not the exception.
            Numbers to six digits. Situations should be everyday but the path to the answer
            should not be stated. Positive stems only.
            """,
        <= 8 => """
            # Class 6-8 calibration
            Two chained concepts per question is the target for Advanced and above. This is
            where reverse-reasoning problems and multi-constraint conditions belong.
            Negative stems ("which is NOT...") are permitted from here.
            """,
        <= 10 => """
            # Class 9-10 calibration
            Questions should routinely combine two topics from different chapters. Reward
            recognising a structure over grinding through it. A well-prepared student should
            need two to three minutes on an Olympiad-tier question.
            """,
        _ => """
            # Class 11-12 calibration
            Proof-flavoured reasoning expressed as multiple choice. The efficient route
            should be conceptual rather than computational, and the brute-force route should
            be long enough to punish a student who does not see the idea.
            """,
    };

    /// <summary>
    /// Syllabus scope for the subject at this grade band. Kept separate from
    /// <see cref="GradeBand"/> so a Science paper is not handed the Mathematics syllabus.
    /// </summary>
    public static string SyllabusScope(string subject, int grade)
    {
        var band = grade <= 2 ? 0 : grade <= 5 ? 1 : grade <= 8 ? 2 : grade <= 10 ? 3 : 4;
        var scope = CatalogueKey(subject) switch
        {
            "Mathematics" => band switch
            {
                0 => "Numbers to 100, addition and subtraction, doubling and halving, comparison, shapes by name, days and months, simple money.",
                1 => "Numbers to six digits, division with remainders, fractions of a quantity, unit conversion (L/mL, km/m, kg/g, hours/minutes), money and change, elapsed time across noon or midnight, perimeter and area of composite shapes described in words, number patterns, place value.",
                2 => "Integers, fractions, decimals, ratio and proportion, percentage, simple and compound interest, HCF and LCM including remainder conditions, divisibility rules, exponents, linear equations, mensuration, lines and angles, data handling.",
                3 => "Polynomials with remainder and factor theorem, quadratic equations and the nature of roots, arithmetic progressions, coordinate geometry, triangle and circle theorems, surface area and volume of combined solids, trigonometric ratios and identities, statistics, probability.",
                _ => "Sets, relations and functions, complex numbers, permutations and combinations, binomial theorem, sequences and series, straight lines and conics, limits, derivatives and applications, integrals, differential equations, vectors, three-dimensional geometry, probability.",
            },
            "Science" => band switch
            {
                0 => "Living and non-living, parts of plants and the body, food, senses, weather, day and night, common materials.",
                1 => "Plants and animals and their habitats, food and nutrition, water, air, soil, states of matter, simple machines, light and shadow, the solar system, safety and health.",
                2 => "Cell structure, tissues, microorganisms, crop production, metals and non-metals, synthetic materials, combustion, force and pressure, friction, sound, light, electricity and its effects, natural phenomena, the solar system, pollution and conservation.",
                3 => "Motion and laws of motion, gravitation, work and energy, sound; matter and its composition, atoms and molecules, structure of the atom, chemical reactions, acids bases and salts, metals and non-metals, carbon compounds, periodic classification; cell biology, tissues, life processes, control and coordination, reproduction, heredity, natural resource management; light, the human eye, electricity, magnetic effects of current.",
                _ => "Mechanics, thermodynamics, waves and oscillations, electrostatics and current electricity, magnetism, optics, modern physics; chemical bonding, equilibrium, thermodynamics, kinetics, electrochemistry, organic reaction mechanisms; biomolecules, genetics, evolution, human physiology, ecology and biotechnology.",
            },
            "English" => band switch
            {
                0 => "Alphabet and phonics, naming words, simple opposites, rhyming words, articles a/an, singular and plural, basic sentence order.",
                1 => "Nouns, pronouns, verbs, adjectives, adverbs; tenses; articles and prepositions; punctuation; synonyms and antonyms; simple comprehension; commonly confused words.",
                2 => "Tense consistency, active and passive voice, reported speech, subject-verb agreement, conjunctions, question tags, degrees of comparison, idioms and phrasal verbs, vocabulary in context, inference from short passages.",
                3 => "Modal perfects and conditionals, complex and compound sentence transformation, participles and gerunds, advanced determiners, nuanced vocabulary in context, critical reading and inference, register and tone.",
                _ => "Advanced usage and style, figurative language, argument structure, analytical comprehension, precision in word choice, formal and academic register.",
            },
            "Logical Reasoning" => band switch
            {
                0 => "Simple patterns, bigger and smaller, same and different, ordering by size, basic sequences.",
                1 => "Number and letter series, simple analogies, odd one out, basic coding, direction sense with two turns, simple ranking.",
                2 => "Multi-rule series, coding and decoding, blood relations across three links, direction sense with several turns, symbol substitution arithmetic, letter-string counting, ranking with partial information.",
                3 => "Syllogisms, complex arrangements, calendar and clock reasoning, conditional deduction chains, data sufficiency.",
                _ => "Formal logic, multi-constraint arrangement puzzles, quantitative reasoning under conditions, data sufficiency and analytical reasoning.",
            },
            "Cyber" => band switch
            {
                0 => "Parts of a computer, uses of a computer, mouse and keyboard, safe use.",
                1 => "Input and output devices, storage, basic Windows operations, Paint, word processing basics, internet basics and safety, simple block coding.",
                2 => "Computer fundamentals and memory units, MS Word, Excel and PowerPoint features and shortcuts, internet and email, networking basics, HTML basics, number systems, algorithms and flowcharts, cyber safety.",
                3 => "Networking and topologies, protocols, database concepts, HTML and CSS, Python basics, number system conversion, boolean logic, cyber ethics and security.",
                _ => "Programming constructs and data structures, database queries, networking protocols, operating system concepts, security fundamentals, emerging technologies.",
            },
            "Social Studies" => band switch
            {
                0 => "My family and neighbourhood, festivals, community helpers, means of transport, our country.",
                1 => "Our earth and globe, maps and directions, landforms, weather and climate, states of India, early civilisations, local government, transport and communication.",
                2 => "Physical and political geography of India, resources and agriculture, medieval and modern Indian history, the freedom struggle, the Constitution, democracy and local self-government, basic economics.",
                3 => "Nationalism in India and Europe, industrialisation, resources and development, water and forest resources, manufacturing, power sharing and federalism, political parties, development economics, globalisation.",
                _ => "Modern Indian and world history, physical and human geography, Indian constitution and polity, micro and macro economics, sociology of Indian society.",
            },
            "General Knowledge" => band switch
            {
                0 => "Colours, animals, fruits and vegetables, national symbols, festivals, common occupations.",
                1 => "Indian states and capitals, national symbols and emblems, famous monuments, the solar system, sports basics, well-known books and authors, simple inventions.",
                2 => "Indian history and geography, world capitals and currencies, awards and honours, sports records that do not change, science and inventions, literature, art and culture.",
                3 => "Indian polity, economy and international organisations, scientific discoveries, world geography, historical landmarks, literature and cinema.",
                _ => "International affairs and organisations, economics, science and technology, defence, awards, and enduring cultural knowledge.",
            },
            "Hindi" => band switch
            {
                0 => "वर्णमाला, मात्राएँ, सरल शब्द, गिनती, विलोम शब्द।",
                1 => "संज्ञा, सर्वनाम, विशेषण, क्रिया, लिंग, वचन, विलोम और पर्यायवाची शब्द, सरल गद्यांश।",
                2 => "काल, कारक, संधि, समास, उपसर्ग और प्रत्यय, मुहावरे और लोकोक्तियाँ, वाक्य शुद्धि, गद्यांश बोध।",
                3 => "अलंकार, रस, छंद, वाक्य परिवर्तन, समास और संधि विस्तार से, मुहावरे, अपठित गद्यांश और काव्यांश।",
                _ => "काव्य शास्त्र, अलंकार और रस, साहित्य का इतिहास, व्याकरण का उन्नत प्रयोग, समीक्षात्मक गद्यांश।",
            },
            _ => "",
        };

        return string.IsNullOrEmpty(scope) ? "" : $"\n\n# Syllabus scope for Class {grade} {subject}\n{scope}\n";
    }

    // ── Archetype catalogue ──────────────────────────────────────────────────

    private record Archetype(string Code, string Description, int Foundation, int Advanced, int Olympiad);

    /// <summary>
    /// Question shapes observed across the CREST and Unicus papers, with relative weights
    /// per difficulty tier. Weight 0 removes the archetype from that tier entirely — which
    /// is how single-step recall is kept out of Olympiad papers.
    /// </summary>
    private static readonly Dictionary<string, Archetype[]> Catalogue = new(StringComparer.OrdinalIgnoreCase)
    {
        ["Mathematics"] = new[]
        {
            new Archetype("DIRECT_APPLY", "One concept, one step, but phrased as a short real-world situation rather than a bare sum.", 5, 1, 0),
            new Archetype("UNIT_CHAIN", "A word problem that only works out if units are converted mid-solution (L/mL, km/m, kg/g, hours/minutes).", 3, 3, 1),
            new Archetype("REVERSE_CHAIN", "The end state is given and the starting quantity is asked. Requires undoing two or three proportional steps in order.", 1, 4, 4),
            new Archetype("PERCENT_CHAIN", "Successive percentage changes, or discount followed by tax, where applying both to the same base is the trap.", 1, 3, 3),
            new Archetype("RATE_WORK", "Combined rates: two workers or two pipes, one leaves partway through.", 0, 3, 3),
            new Archetype("NUMBER_THEORY", "HCF/LCM with remainder conditions, divisibility constraints, or prime/composite conditions that must hold simultaneously.", 1, 3, 5),
            new Archetype("COMPARISON", "Four expressions that must each be evaluated and then ranked — the answer is which one is largest or smallest.", 1, 2, 2),
            new Archetype("ALGEBRAIC_IDENTITY", "Solvable in one line by recognising a standard identity; brute expansion should be painful but possible.", 0, 3, 4),
            new Archetype("GEOMETRY_TEXT", "Every length, angle and relationship stated in words. Needs two or more theorems chained together.", 1, 3, 4),
            new Archetype("MENSURATION_COMPOSITE", "Solids combined, melted and recast, or hollowed. Surface-area-versus-volume confusion is the built-in trap.", 0, 3, 4),
            new Archetype("DATA_TABLE", "A markdown table in the stem. The question asks for a derived quantity — a difference, ratio or percentage — never a single cell.", 2, 3, 2),
            new Archetype("MULTI_STATEMENT", "Statements numbered I, II, III. The options are combinations such as 'I and III only'.", 1, 3, 4),
            new Archetype("SEQUENCE_PATTERN", "An arithmetic or geometric progression, or a numeric pattern whose rule is not visible at a glance.", 2, 3, 3),
            new Archetype("COUNTING_PROBABILITY", "Systematic counting or a probability that needs the sample space worked out first.", 0, 2, 4),
        },
        ["Science"] = new[]
        {
            new Archetype("DIRECT_CONCEPT", "One NCERT fact applied to a familiar situation.", 5, 1, 0),
            new Archetype("MECHANISM_WHY", "Asks why something happens, not what it is called. The distractors are plausible-sounding wrong causes.", 2, 4, 5),
            new Archetype("STATEMENT_PAIR", "Statement 1 and Statement 2. Options cover the four combinations of each being correct or incorrect.", 1, 4, 4),
            new Archetype("ASSERTION_REASON", "An assertion and a reason. The four standard options, including 'both correct but the reason does not explain the assertion'.", 0, 3, 5),
            new Archetype("SUBSTATEMENT_LIST", "Numbered claims 1-4 with options like 'Only 3' or 'Both 1 and 2'.", 1, 3, 4),
            new Archetype("EXPERIMENT_PREDICT", "An apparatus or procedure described fully in words; predict the observation or name the control.", 1, 3, 4),
            new Archetype("MISCONCEPTION_TRAP", "Built around a belief most students hold that is wrong. That belief is the most attractive distractor.", 1, 3, 4),
            new Archetype("DATA_INTERPRET", "A small results table; infer the trend or the anomaly.", 1, 3, 3),
            new Archetype("NUMERICAL_APPLY", "A formula applied with attention to units and to which quantity was actually asked for.", 2, 3, 3),
            new Archetype("CROSS_TOPIC", "Deliberately links two different chapters in one question.", 0, 2, 4),
        },
        ["English"] = new[]
        {
            new Archetype("CONTEXT_VOCAB", "A sentence containing a word in quotation marks; choose its synonym or antonym AS USED HERE. Distractors are valid meanings in other contexts.", 3, 4, 4),
            new Archetype("PREPOSITION_ARTICLE", "A blank needing the correct preposition, article or determiner, where the choice depends on the rest of the sentence.", 4, 3, 2),
            new Archetype("TENSE_MODAL", "Modal perfects and conditionals — 'could have been killed' versus 'should have'.", 2, 4, 4),
            new Archetype("QUESTION_TAG", "Complete the sentence with the right question tag, including negative and 'nothing/nobody' subjects.", 2, 3, 3),
            new Archetype("SPELLING_DISCRIMINATE", "Four near-identical spellings of a genuinely difficult word; exactly one is correct.", 3, 3, 2),
            new Archetype("COMPARATIVE_TRAP", "Comparative and superlative forms, with a double-comparative such as 'most fanciest' among the distractors.", 1, 3, 3),
            new Archetype("TWO_BLANK_AGREEMENT", "Two blanks in one sentence that must agree with each other in person, number or possession.", 1, 3, 3),
            new Archetype("SENTENCE_REARRANGE", "Jumbled fragments to be ordered into one meaningful sentence.", 1, 3, 4),
            new Archetype("PASSAGE_INFERENCE", "A short passage written out in full, then a question whose answer is implied rather than stated.", 1, 3, 5),
            new Archetype("IDIOM_PHRASAL", "An idiom or phrasal verb used in context, not defined in isolation.", 2, 3, 4),
        },
        ["Logical Reasoning"] = new[]
        {
            new Archetype("NUMBER_SERIES", "A numeric series with a rule that combines two operations.", 4, 3, 3),
            new Archetype("CODING_DECODING", "A word coded by a letter or position rule; decode a second word.", 3, 4, 3),
            new Archetype("BLOOD_RELATION", "A relationship described through three or more links, ideally in reported speech.", 2, 4, 5),
            new Archetype("DIRECTION_SENSE", "Several turns and distances; asks for final direction or displacement.", 2, 4, 4),
            new Archetype("SYMBOL_ARITHMETIC", "Operators replaced by letters or symbols; evaluate the expression under the substitution.", 2, 4, 4),
            new Archetype("LETTER_STRING_COUNT", "A long letter string; count occurrences satisfying a before-and-after condition.", 1, 3, 4),
            new Archetype("ODD_ONE_OUT", "Four letter groups or number pairs, three sharing a hidden rule.", 3, 3, 3),
            new Archetype("RANKING_ARRANGEMENT", "Positions in a row or a queue deduced from partial statements.", 2, 3, 4),
            new Archetype("SYLLOGISM", "Two or three premises; determine which conclusions necessarily follow.", 1, 3, 5),
            new Archetype("CALENDAR_CLOCK", "Day-of-week calculation, or the angle between clock hands.", 1, 3, 4),
        },
        ["Cyber"] = new[]
        {
            new Archetype("TERM_FUNCTION", "What a protocol, component or term actually does — phrased as a use case rather than a definition.", 4, 2, 1),
            new Archetype("NOT_VALID", "Which of four is not a valid data type, tag, shortcut or device. Class 6 and above only.", 2, 3, 3),
            new Archetype("SHORTCUT_KEY", "The keyboard shortcut for a described action in Word, Excel or PowerPoint.", 3, 2, 1),
            new Archetype("FULL_FORM", "Expansion of an abbreviation, with plausible near-miss expansions as distractors.", 3, 2, 1),
            new Archetype("COMPARE_CHOOSE", "Two technologies or topologies compared; pick the right one for a stated requirement.", 1, 4, 4),
            new Archetype("HTML_PURPOSE", "The effect of a tag or attribute in a described page.", 1, 3, 3),
            new Archetype("OUTPUT_PREDICT", "A short code or block-logic fragment written out in full; predict its output. Class 7 and above.", 0, 4, 5),
            new Archetype("SCENARIO_TROUBLESHOOT", "A described symptom; identify the cause or the correct fix.", 1, 3, 4),
            new Archetype("SPREADSHEET_FORMULA", "A formula's result, or which formula produces a stated result. Note that cell references such as A1 are not currency.", 1, 3, 4),
        },
    };

    /// <summary>Subjects without a bespoke catalogue fall back to a general shape.</summary>
    private static readonly Archetype[] GenericCatalogue =
    {
        new("DIRECT_CONCEPT", "One syllabus fact applied to a concrete situation.", 5, 2, 0),
        new("MULTI_STATEMENT", "Statements numbered I, II, III with combination options.", 1, 3, 4),
        new("MECHANISM_WHY", "Asks for the reason behind something rather than its name.", 2, 4, 5),
        new("MISCONCEPTION_TRAP", "The most popular wrong belief is the most attractive distractor.", 1, 3, 4),
        new("DATA_INTERPRET", "A small markdown table; infer a derived value or a trend.", 2, 3, 3),
        new("CROSS_TOPIC", "Links two different areas of the syllabus in one question.", 0, 3, 4),
    };

    /// <summary>
    /// Maps whatever subject string reaches us onto a catalogue key. The bank uses several
    /// spellings for the same subject — "Science-Physics", "Computer Science", "Maths",
    /// "Cyber" — so resolve them all in one place. Returns "" when nothing matches.
    /// </summary>
    private static string CatalogueKey(string? subject)
    {
        if (string.IsNullOrWhiteSpace(subject)) return "";
        if (Catalogue.ContainsKey(subject)) return Catalogue.Keys.First(k => k.Equals(subject, StringComparison.OrdinalIgnoreCase));

        // Order matters: "Computer Science" contains "Science", so the computing test has
        // to run first or a Cyber paper is handed the Science syllabus.
        if (subject.Contains("Cyber", StringComparison.OrdinalIgnoreCase) ||
            subject.Contains("Comput", StringComparison.OrdinalIgnoreCase) ||
            subject.Equals("IT", StringComparison.OrdinalIgnoreCase)) return "Cyber";
        if (subject.Contains("Social", StringComparison.OrdinalIgnoreCase)) return "Social Studies";
        if (subject.Contains("Math", StringComparison.OrdinalIgnoreCase)) return "Mathematics";
        if (subject.Contains("Physic", StringComparison.OrdinalIgnoreCase) ||
            subject.Contains("Chem", StringComparison.OrdinalIgnoreCase) ||
            subject.Contains("Bio", StringComparison.OrdinalIgnoreCase) ||
            subject.Contains("Science", StringComparison.OrdinalIgnoreCase)) return "Science";
        if (subject.Contains("Reason", StringComparison.OrdinalIgnoreCase)) return "Logical Reasoning";
        if (subject.Contains("English", StringComparison.OrdinalIgnoreCase)) return "English";
        if (subject.Contains("Hindi", StringComparison.OrdinalIgnoreCase)) return "Hindi";
        if (subject.Contains("General Knowledge", StringComparison.OrdinalIgnoreCase) ||
            subject.Equals("GK", StringComparison.OrdinalIgnoreCase)) return "General Knowledge";
        return "";
    }

    private static Archetype[] For(string subject)
    {
        var key = CatalogueKey(subject);
        return key.Length > 0 && Catalogue.TryGetValue(key, out var found) ? found : GenericCatalogue;
    }

    private static int WeightOf(Archetype a, string difficulty) => difficulty?.ToLowerInvariant() switch
    {
        "olympiad" => a.Olympiad,
        "advanced" => a.Advanced,
        _ => a.Foundation,
    };

    // ── Blueprint ────────────────────────────────────────────────────────────

    /// <summary>
    /// Turns a request for N questions into an explicit per-archetype quota, so the model
    /// cannot fall back on one comfortable question shape. Allocation is proportional to
    /// the tier weights, with the remainder going to the heaviest archetypes.
    /// </summary>
    public static string BuildBlueprint(string subject, int grade, string difficulty, int count)
    {
        var pool = For(subject)
            .Select(a => (Arch: a, Weight: WeightOf(a, difficulty)))
            .Where(x => x.Weight > 0)
            .OrderByDescending(x => x.Weight)
            .ToList();

        if (pool.Count == 0 || count <= 0) return "";

        var totalWeight = pool.Sum(x => x.Weight);
        var quota = new int[pool.Count];
        var assigned = 0;

        for (var i = 0; i < pool.Count; i++)
        {
            quota[i] = (int)Math.Floor((double)count * pool[i].Weight / totalWeight);
            assigned += quota[i];
        }

        // Hand out what rounding left over, heaviest archetype first, wrapping if needed.
        for (var i = 0; assigned < count; i = (i + 1) % pool.Count)
        {
            quota[i]++;
            assigned++;
        }

        // With few questions, prefer variety over depth on a single archetype.
        if (count <= pool.Count)
        {
            Array.Clear(quota);
            for (var i = 0; i < count; i++) quota[i] = 1;
        }

        var lines = pool
            .Select((x, i) => (x.Arch, Count: quota[i]))
            .Where(x => x.Count > 0)
            .Select(x => $"  {x.Count} x {x.Arch.Code}\n        {x.Arch.Description}");

        return $"""

            # Blueprint for this paper — Class {grade} {subject}, {difficulty} tier

            Produce exactly {count} questions in this mix. The counts are binding: do not
            exceed any of them, and do not substitute an archetype that is not listed. Copy
            the archetype code into the "archetype" field of each question so the mix can be
            checked.

            {string.Join("\n", lines)}

            Vary the topics across the paper — do not set every question on the same chapter.
            Vary the position of the correct answer; it must not sit on the same letter more
            than about a third of the time.
            """;
    }

    // ── Anti-patterns ────────────────────────────────────────────────────────

    /// <summary>Failure modes seen in the existing bank, stated as explicit prohibitions.</summary>
    public static string AntiPatterns(string difficulty)
    {
        var common = """

            # Do not produce any of these

              - A question answerable by substituting into a single named formula with no
                prior reasoning about which formula applies.
              - A definition asked directly ("What is photosynthesis?"). Ask instead what
                follows from it.
              - A question whose stem gives away the answer through wording or grammar.
              - A question solvable by testing the four options rather than by reasoning.
              - Arithmetic made hard only by having many digits.
              - Two questions in the same paper that share a solution method and differ only
                in their numbers.
              - Any reference to a figure, diagram, image, chart or pattern you have not
                written out in full.
              - Currency written with a dollar sign, or maths written without $...$.
            """;

        if (difficulty?.Equals("Olympiad", StringComparison.OrdinalIgnoreCase) == true)
        {
            return common + """

              - For this tier specifically: any question a well-prepared student finishes in
                under thirty seconds. Every question must need at least two distinct
                reasoning steps, and at least one step should not be obvious from the stem.
                A student who has memorised the textbook but cannot reason should score
                close to zero on this set.
            """;
        }
        return common;
    }
}
