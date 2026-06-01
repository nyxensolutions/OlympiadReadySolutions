using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using OlympiadReady.Api.Models;

namespace OlympiadReady.Api.Services;

public class AiGenerationService
{
    private const string SystemPrompt = """
        You are a senior examiner with 15+ years of experience writing competitive Olympiad
        questions for Indian school students. Your day-to-day work is preparing question papers
        for SOF (Science Olympiad Foundation) — IMO, NSO, IEO, NCO — and SilverZone Olympiads
        (iiO, iOS, iIO, iOEL). You know the CBSE / NCERT curriculum cold, including the way SOF's
        Achievers Section uses higher-order reasoning compared to the foundational MCQs.

        # Task
        Generate a fresh set of highly rigorous multiple-choice questions tailored to the requested
        Class (1-12), Subject (Math, Science, English, Hindi, Social Studies, General Knowledge,
        Logical Reasoning, Computers, or AI), and Difficulty level.
        Even for lower difficulties, the questions MUST NOT be trivial. You must use an advanced reasoning framework to ensure no question feels 'cheap' or 'generated'.

        # Difficulty calibration

        Foundation
            Tests recall and direct application of a single concept from the prescribed syllabus.
            Distractors are obvious wrong values once the student knows the formula.
            Roughly equivalent to the first 25 questions of an SOF Section A paper.

        Advanced
            Requires composing two related concepts (e.g. "find the perimeter, then convert units"),
            reading a short word problem, or interpreting a small data table or diagram.
            Distractors include classic computational mistakes — sign errors, off-by-one,
            unit confusion, picking a partial answer.

        Olympiad
            Mirrors the Achievers / Section B style — the hardest 5-10 questions in a real
            Olympiad paper that only top-ranked students answer correctly.
            Every question must demand TWO or more of: multi-step reasoning, non-obvious
            insight, applying a concept in an unfamiliar context, or integrating two topics.
            A student who merely memorised NCERT should get this WRONG.
            Distractors are ruthlessly competitive: every wrong option is the result of a
            specific, named error (e.g. "confusing perimeter with area", "forgetting to
            convert units", "applying formula for surface area instead of volume").
            Avoid questions that can be answered by elimination or by plugging numbers.
            For Math: prefer elegant setups — number theory, invariants, geometry with proof
            steps, counting arguments, or multi-variable word problems.
            For Science: test the WHY, not the WHAT — mechanism, exception, experimental
            design, or data interpretation.
            For English / Hindi: passage inference, nuanced vocabulary in context, or
            complex grammatical transformation.
            For Logical Reasoning: multi-step deduction chains, non-trivial patterns,
            or spatial reasoning with 3+ conditions.

        # Question quality bar
          - STRICT REQUIREMENT: There MUST BE EXACTLY ONE unambiguously correct answer. It is a FATAL ERROR to include multiple correct or partially correct options (e.g., asking "Which is an even number?" and providing both 2 and 4 as options). All distractors MUST be completely and undeniably wrong under all mathematical and logical interpretations.
          - No "all of the above" / "none of the above".
          - Exactly 4 options. They should look comparable in length and style — never make the
            correct answer the longest or the only one with units written out.
          - Distractors target real misconceptions, not random distractors. A student who guesses
            should not be able to eliminate options purely from style.
          - Use Indian context where natural: rupees not dollars, Mumbai/Delhi not London,
            cricket not baseball. Names: Aarav, Priya, Rohan, Ananya, Ishaan, Diya, Vihaan, Saanvi.
          - Avoid dated references (current dates, current cricket captains, etc.).
          - For Math, prefer integer or simple fractional answers; if decimals are needed, round to
            two places. State units explicitly when relevant.
          - For Science, ground in NCERT diagrams and standard experiments — don't invent novel
            apparatus the student has never seen.
          - For English, target the actual sub-skills SOF tests: synonyms/antonyms, sentence
            completion, error-spotting, basic grammar (tenses, articles, prepositions),
            short-passage comprehension, vocabulary in context.
          - For Cyber, cover the SOF NCO syllabus: computer fundamentals, MS Office shortcuts,
            input/output devices, basic networking concepts, simple binary/logic, internet safety,
            and (for higher classes) flowcharts, scratch / block coding logic, basic Python.

        # Explanation style
          The 'explanation' field is read by a child and often by a parent who isn't a subject
          expert. Keep it short (2-4 sentences), step-by-step, and plain-English. If a formula
          is used, name it. End by stating which option is correct and why each tempting wrong
          option is wrong if the misconception is non-obvious.

        # Output format

        Return ONLY a valid JSON object with a single key "questions" containing a JSON array. No prose outside the object. No markdown. No code fences.
        Each element MUST follow this schema exactly, with these field names:

        {
          "reasoning_steps": "Required. Step 1: Calculate the exact mathematical/logical correct answer. Step 2: Formulate 3 strictly incorrect distractors. Step 3: Assign the correct answer and distractors to A, B, C, D.",
          "q":           "the question text",
          "options":     ["option A", "option B", "option C", "option D"],
          "correct_option_letter": "A, B, C, or D",
          "answer":      "CRITICAL: Must perfectly match the correct answer calculated in reasoning_steps AND perfectly match the option at correct_option_letter.",
          "explanation": "concise reasoning. MUST agree with the answer and correct_option_letter.",
          "topic":       "syllabus topic, 1-3 words, consistent across questions of the same concept"
        }

        Topic naming guidance (English labels, even for Hindi-language questions):
          Math               → "Fractions", "Decimals", "Algebra", "Geometry",
                               "Mensuration", "Data Handling", "Integers",
                               "Time and Work", "Ratio and Proportion".
          Science            → "Light", "Sound", "Magnetism", "Force and Motion",
                               "Plants", "Human Body", "Matter", "Cells", "Electricity".
          English            → "Synonyms", "Antonyms", "Tenses", "Articles",
                               "Prepositions", "Comprehension", "Vocabulary",
                               "Sentence Completion".
          Hindi              → "Grammar", "Synonyms", "Antonyms", "Idioms",
                               "Comprehension", "Sandhi", "Samaas",
                               "Sentence Correction", "Vocabulary".
          General Knowledge  → "Indian History", "Geography", "Indian Polity",
                               "Sports", "Awards and Honours", "Famous Personalities",
                               "Books and Authors", "Science and Inventions",
                               "World Facts". Avoid current-affairs style questions
                               with dated answers.
          Logical Reasoning  → "Patterns", "Number Series", "Analogies",
                               "Coding-Decoding", "Direction Sense",
                               "Blood Relations", "Syllogisms", "Mirror Images",
                               "Odd One Out", "Ranking".
          Computers          → "Hardware", "MS Word", "MS Excel", "Internet Safety",
                               "Networking Basics", "Binary and Logic", "Algorithms",
                               "Flowcharts", "Python Basics", "HTML Basics".
          AI                 → "AI Concepts", "Machine Learning Basics",
                               "Neural Networks", "Computer Vision",
                               "Natural Language Processing", "Robotics",
                               "Smart Devices", "Chatbots and Voice Assistants",
                               "AI Ethics", "Data and Bias".
          Social Studies     → "Our World", "Indian Geography", "World Geography",
                               "Ancient Indian History", "Medieval Indian History",
                               "Modern Indian History", "Indian Civics",
                               "Environment and Ecology", "Culture and Heritage",
                               "Natural Disasters", "Economics Basics", "Current Affairs".
                               For Social Studies, draw on the SOF ISSO (International Social
                               Studies Olympiad) syllabus aligned with NCERT / CBSE. Cover
                               history, geography, civics, economics. Use factual, verifiable
                               questions — avoid opinion-based content. Avoid questions with
                               answers that change over time (current events, record-holders).

        Pick from the list when applicable; if you must invent a topic, keep it short and consistent.
        Use the SAME topic string for every question targeting the same concept inside one paper.

        Return as many elements as the user requests. Do not number the questions inside 'q' —
        the renderer adds numbering. Do not prefix options with 'A.' / 'B.' — the renderer does that too.

        # MANDATORY SELF-VERIFICATION — do this for every question BEFORE including it in the JSON

        For each question you write, run through ALL of these checks:
        1. Re-read the question stem and independently solve it. What is the correct answer?
        2. Confirm "correct_option_letter" points to that answer (e.g. if the answer is the 2nd option, letter must be "B").
        3. Confirm "answer" is the EXACT TEXT — character-for-character, same capitalisation and punctuation — of the option at that letter position.
        4. Confirm "explanation" explicitly states the key value or phrase from the correct option (e.g. if the answer is "13", the explanation must contain "13", not some other number).
        5. For maths/science numerical answers: recompute the result and verify it matches the correct option, not a distractor.

        If ANY check fails: fix the question before including it. If you cannot fix it confidently, drop it and replace it with a different question.
        It is better to return fewer questions than to return one with a wrong answer.
        """;

    private readonly HttpClient _http;
    private readonly ILogger<AiGenerationService> _log;
    private readonly string _apiKey;
    private readonly string _model;
    private readonly int _maxTokens;

    public AiGenerationService(HttpClient http, IConfiguration config, ILogger<AiGenerationService> log)
    {
        _http = http;
        _log = log;
        _apiKey = config["OpenAi:ApiKey"] ?? "";
        _model = config["OpenAi:Model"] ?? "gpt-4o-mini";
        _maxTokens = int.TryParse(config["OpenAi:MaxTokens"], out var m) ? m : 4096;
    }

    public async Task<List<Question>> GenerateQuestionsAsync(
        string subject, int grade, string difficulty, int count,
        string? topic = null, CancellationToken ct = default,
        string? olympiadLevel = null, string? olympiadId = null)
    {
        if (string.IsNullOrWhiteSpace(_apiKey) || _apiKey.StartsWith("REPLACE_"))
            throw new InvalidOperationException(
                "OpenAI API key not configured. Set OpenAi:ApiKey via user-secrets or appsettings.");

        var topicClause = topic is not null
            ? $" ALL questions must be exclusively about the topic \"{topic}\" — do not include questions on other topics."
            : "";

        var levelClause = olympiadLevel == "L2"
            ? " These questions are for a LEVEL 2 (national/state round) Olympiad student who has already cleared Level 1. " +
              "Increase complexity further — multi-step reasoning, non-obvious insights, competitive distractors. " +
              "Target the Achievers Section / Section B style of top Olympiad papers."
            : " These questions are for a LEVEL 1 (school round) Olympiad student.";

        var olympiadClause = BuildOlympiadClause(olympiadId);

        var hindiClause = subject.Equals("Hindi", StringComparison.OrdinalIgnoreCase)
            ? " IMPORTANT: Because the subject is Hindi, you MUST write the question text, options, and explanation in Hindi (Devanagari script). Topic labels stay in English so the dashboard can group them consistently."
            : " IMPORTANT: All questions, options, and explanations MUST be written entirely in English.";

        var user =
            $"Generate exactly {count} multiple-choice questions for Class {grade} {subject} " +
            $"at {difficulty} difficulty.{topicClause}{levelClause}{olympiadClause}{hindiClause} Follow the schema and rules from the system prompt strictly.";

        // Use the more capable model for Olympiad-level questions to ensure genuine difficulty
        var effectiveModel = difficulty?.Equals("Olympiad", StringComparison.OrdinalIgnoreCase) == true
            ? "gpt-4o"
            : _model;

        var payload = new
        {
            model = effectiveModel,
            max_tokens = _maxTokens,
            messages = new[]
            {
                new { role = "system", content = SystemPrompt },
                new { role = "user", content = user }
            },
            response_format = new { type = "json_object" }
        };

        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Post, "v1/chat/completions");
            req.Headers.Add("Authorization", $"Bearer {_apiKey}");
            req.Content = JsonContent.Create(payload);

            using var res = await _http.SendAsync(req, ct);
            var body = await res.Content.ReadAsStringAsync(ct);

            if (!res.IsSuccessStatusCode)
            {
                _log.LogWarning("OpenAI API error {Status} — falling back to DB questions. Body: {Body}",
                    res.StatusCode, body.Length > 500 ? body[..500] : body);
                return new List<Question>();
            }

            var parsed = JsonSerializer.Deserialize<OpenAiResponse>(body);
            if (parsed is null)
            {
                _log.LogWarning("OpenAI returned empty/unparseable response — falling back to DB questions.");
                return new List<Question>();
            }

            if (parsed.Usage is { } u)
            {
                _log.LogInformation(
                    "OpenAI usage — prompt: {Prompt}, completion: {Completion}, total: {Total}",
                    u.PromptTokens, u.CompletionTokens, u.TotalTokens);
            }

            var content = parsed.Choices?.FirstOrDefault()?.Message?.Content;
            if (string.IsNullOrWhiteSpace(content))
                return new List<Question>();

            var result = JsonSerializer.Deserialize<OpenAiQuestionResponse>(content);
            return result?.Questions ?? new List<Question>();
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "AI generation failed for {Subject} G{Grade} {Difficulty} — falling back to DB questions.",
                subject, grade, difficulty);
            return new List<Question>();
        }
    }

    private static string BuildOlympiadClause(string? olympiadId) => olympiadId switch
    {
        "sof_imo" => " Mirror the SOF IMO (International Mathematics Olympiad) question style exactly: Section A has straightforward curriculum questions; Section B (Achievers) has multi-step reasoning with competitive distractors. Use the SOF IMO vocabulary — \"Achievers Section\", class-level NCERT curriculum alignment, integer or fractional answers preferred.",
        "sof_nso" => " Mirror the SOF NSO (National Science Olympiad) style: Section A has direct NCERT concept questions; Section B (Achievers) uses application and higher-order thinking. Cover Physics, Chemistry, Biology as appropriate for the grade. Align with the NSO Chapter-wise syllabus.",
        "sof_ieo" => " Mirror the SOF IEO (International English Olympiad) pattern: Word and Structure Knowledge, Reading, Spoken and Written Expression. Include synonym/antonym, sentence-rearrangement, comprehension passage inference, and grammar-in-context questions as IEO does.",
        "sof_nco" => " Mirror the SOF NCO (National Cyber Olympiad) syllabus: Computer fundamentals, MS Office, internet basics, binary/logic, networking, and for higher classes: Python basics, HTML/CSS, algorithms. Section B (Achievers) should have application-level coding-logic questions.",
        "sof_isso" => " Mirror the SOF ISSO (International Social Studies Olympiad) pattern: History, Geography, Civics, Economics. Questions should be factual and verifiable. Avoid time-sensitive current-affairs questions.",
        "sof_igko" => " Mirror the SOF IGKO (International General Knowledge Olympiad): Current affairs, science, sports, awards, famous personalities, world facts. All answers must be stable facts — no questions whose answer changes year to year.",
        "silverzone_math" => " Mirror SilverZone iOM (International Olympiad of Mathematics) style: Three sections — Logical Reasoning, Mathematical Reasoning, Everyday Mathematics. Questions are slightly more analytical than SOF; avoid purely computational questions. SilverZone prefers word-problem framing even for algebraic content.",
        "silverzone_science" => " Mirror SilverZone iOS (International Olympiad of Science) style: Application-based questions tied to NCERT; emphasis on experimental reasoning and real-world phenomena. Three sections: Science, Applied Science, Achievers.",
        "silverzone_english" => " Mirror SilverZone iOEL (International Olympiad of English Language) pattern: Word power, language in use, reading comprehension, creative language. Questions are slightly more literary than SOF IEO — include idioms and phrasal verbs.",
        "silverzone_computer" => " Mirror SilverZone iOIT (International Olympiad of Information Technology) pattern: Computer concepts, programming logic (Scratch for lower grades, Python for higher), internet safety, and digital literacy. Align with the iOIT chapter-wise syllabus.",
        "unified_nstse" => " Mirror the NSTSE (National Level Science Talent Search Exam) by Unified Council: Strongly NCERT-aligned, concept-clarity focused. Questions test whether students understand the \"why\" behind answers, not just recall. Avoid questions solvable purely by rote; prefer reasoning-based MCQs. Mathematics section is included for all grades.",
        "unified_uieo" => " Mirror the UIEO (Unified International English Olympiad) by Unified Council: Reading, writing, grammar, and vocabulary. Analytical reading comprehension with inference questions. Grammar questions should test usage in context, not rules by rote.",
        "crest_cmo" => " Mirror CREST CMO (CREST Mathematics Olympiad) style: Online-exam format. Questions are conceptually deep with elegant solutions. CREST favours multi-concept integration — a single question may span geometry + algebra. Distractors should be the results of common one-step errors.",
        "crest_cso" => " Mirror CREST CSO (CREST Science Olympiad) style: Practical, application-based science. Questions often involve a scenario or mini-experiment description before the question. CREST Science leans more applied than SOF NSO.",
        "crest_ceo" => " Mirror CREST CEO (CREST English Olympiad) style: High-quality passages with inference and vocabulary-in-context questions. Grammar questions are usage-based. CREST English tests critical reading more than SOF IEO.",
        "hbcse" => " Mirror the HBCSE National Olympiad Programme (IOQM/RMO/INMO for Math; NSEP/NSEC for Science): These are the most rigorous school Olympiads in India. Even for MCQ practice, questions should demand deep mathematical or scientific reasoning — no direct-formula plugging. For Math: elegant proofs, number theory, combinatorics, geometry with proof steps. For Science: derivation-level understanding, advanced NCERT + beyond. Distractors must be plausible from a partial-reasoning standpoint.",
        "spell_bee" => " This is a Spell Bee competition preparation paper. Focus exclusively on: (1) correct spelling of age-appropriate words, (2) word meanings and usage in context, (3) phonetics and syllabification, (4) antonyms and synonyms, (5) homophones and commonly confused words. Each question must present 4 spelling or vocabulary options. Words should be graded to the class level — simpler for Class 1-3, more complex for Class 8-12.",
        _ => " Questions should follow standard competitive Olympiad exam patterns."
    };

    private class OpenAiResponse
    {
        [JsonPropertyName("choices")]
        public List<OpenAiChoice>? Choices { get; set; }

        [JsonPropertyName("usage")]
        public OpenAiUsage? Usage { get; set; }
    }

    private class OpenAiChoice
    {
        [JsonPropertyName("message")]
        public OpenAiMessage? Message { get; set; }
    }

    private class OpenAiMessage
    {
        [JsonPropertyName("content")]
        public string? Content { get; set; }
    }

    private class OpenAiUsage
    {
        [JsonPropertyName("prompt_tokens")]
        public int PromptTokens { get; set; }

        [JsonPropertyName("completion_tokens")]
        public int CompletionTokens { get; set; }

        [JsonPropertyName("total_tokens")]
        public int TotalTokens { get; set; }
    }

    private class OpenAiQuestionResponse
    {
        [JsonPropertyName("questions")]
        public List<Question>? Questions { get; set; }
    }
}
