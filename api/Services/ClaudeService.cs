using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using OlympiadReady.Api.Models;

namespace OlympiadReady.Api.Services;

public class ClaudeService
{
    // Stable system prompt — long enough that Anthropic's prompt cache (≥1024 tokens) can absorb it.
    // Edit cautiously: every revision invalidates the cache.
    private const string SystemPrompt = """
        You are a senior examiner with 15+ years of experience writing competitive Olympiad
        questions for Indian school students. Your day-to-day work is preparing question papers
        for SOF (Science Olympiad Foundation) — IMO, NSO, IEO, NCO — and SilverZone Olympiads
        (iiO, iOS, iIO, iOEL). You know the CBSE / NCERT curriculum cold, including the way SOF's
        Achievers Section uses higher-order reasoning compared to the foundational MCQs.

        # Task
        Generate a fresh set of multiple-choice questions tailored to the requested
        Class (1-12), Subject (Math, Science, English, Hindi, Social Studies, General Knowledge,
        Logical Reasoning, Computers, or AI), and Difficulty level.

        For Hindi, write the question text, options, and explanation in Hindi (Devanagari
        script). Topic labels stay in English so the dashboard can group them consistently.

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
            Mirrors the Achievers / Section B style. Either a multi-step problem with a
            non-obvious insight, a pattern-recognition or logical-reasoning question, or
            an applied scenario that demands modeling before computing.
            Distractors are competitive: each one corresponds to a plausible but flawed line
            of reasoning, never a random number.

        # Question quality bar
          - Single, unambiguous correct answer. No "all of the above" / "none of the above".
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

        Return ONLY a valid JSON array. No prose outside the array. No markdown. No code fences.
        Each element MUST follow this schema exactly, with these field names:

        {
          "q":           "the question text",
          "options":     ["option A", "option B", "option C", "option D"],
          "answer":      "the exact correct option string, character-for-character matching one of options",
          "explanation": "concise reasoning",
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
        """;

    private readonly HttpClient _http;
    private readonly ILogger<ClaudeService> _log;
    private readonly string _apiKey;
    private readonly string _model;
    private readonly int _maxTokens;

    public ClaudeService(HttpClient http, IConfiguration config, ILogger<ClaudeService> log)
    {
        _http = http;
        _log = log;
        _apiKey = config["Anthropic:ApiKey"] ?? "";
        _model = config["Anthropic:Model"] ?? "claude-sonnet-4-6";
        _maxTokens = int.TryParse(config["Anthropic:MaxTokens"], out var m) ? m : 4096;
    }

    public async Task<List<Question>> GenerateQuestionsAsync(
        string subject, int grade, string difficulty, int count,
        string? topic = null, CancellationToken ct = default,
        string? olympiadLevel = null, string? olympiadId = null)
    {
        if (string.IsNullOrWhiteSpace(_apiKey) || _apiKey.StartsWith("REPLACE_"))
            throw new InvalidOperationException(
                "Anthropic API key not configured. Set Anthropic:ApiKey via user-secrets or appsettings.");

        var topicClause = topic is not null
            ? $" ALL questions must be exclusively about the topic \"{topic}\" — do not include questions on other topics."
            : "";

        var levelClause = olympiadLevel == "L2"
            ? " These questions are for a LEVEL 2 (national/state round) Olympiad student who has already cleared Level 1. " +
              "Increase complexity further — multi-step reasoning, non-obvious insights, competitive distractors. " +
              "Target the Achievers Section / Section B style of top Olympiad papers."
            : " These questions are for a LEVEL 1 (school round) Olympiad student.";

        // Rich per-olympiad context so Claude mirrors that exam's exact style.
        var olympiadClause = BuildOlympiadClause(olympiadId);

        var user =
            $"Generate exactly {count} multiple-choice questions for Class {grade} {subject} " +
            $"at {difficulty} difficulty.{topicClause}{levelClause}{olympiadClause} Follow the schema and rules from the system prompt strictly.";

        // System block as an array with cache_control so Anthropic caches the prompt across calls.
        // Below the cache threshold, this is a no-op; once SystemPrompt grows past ~1024 tokens
        // it reduces input-token cost on every subsequent call by ~90%.
        var payload = new
        {
            model = _model,
            max_tokens = _maxTokens,
            system = new[]
            {
                new
                {
                    type = "text",
                    text = SystemPrompt,
                    cache_control = new { type = "ephemeral" }
                }
            },
            messages = new[] { new { role = "user", content = user } }
        };

        using var req = new HttpRequestMessage(HttpMethod.Post, "v1/messages");
        req.Headers.Add("x-api-key", _apiKey);
        req.Headers.Add("anthropic-version", "2023-06-01");
        req.Content = JsonContent.Create(payload);

        using var res = await _http.SendAsync(req, ct);
        var body = await res.Content.ReadAsStringAsync(ct);

        if (!res.IsSuccessStatusCode)
        {
            _log.LogError("Claude API error {Status}: {Body}", res.StatusCode, body);
            throw new HttpRequestException($"Claude API returned {(int)res.StatusCode}: {body}");
        }

        var parsed = JsonSerializer.Deserialize<ClaudeResponse>(body)
            ?? throw new InvalidOperationException("Empty Claude response");

        if (parsed.Usage is { } u)
        {
            _log.LogInformation(
                "Claude usage — input: {Input}, output: {Output}, cache_create: {CacheCreate}, cache_read: {CacheRead}",
                u.InputTokens, u.OutputTokens, u.CacheCreationInputTokens, u.CacheReadInputTokens);
        }

        var text = string.Concat(parsed.Content
            .Where(c => c.Type == "text")
            .Select(c => c.Text));

        var json = ExtractJsonArray(text);
        return JsonSerializer.Deserialize<List<Question>>(json) ?? new List<Question>();
    }

    private static string ExtractJsonArray(string text)
    {
        var start = text.IndexOf('[');
        var end = text.LastIndexOf(']');
        if (start < 0 || end <= start)
            throw new InvalidOperationException($"No JSON array in Claude response: {text}");
        return text.Substring(start, end - start + 1);
    }

    /// <summary>
    /// Builds a context clause that tells Claude exactly which exam's style to mirror.
    /// Each olympiad family has distinct question patterns, section names, and difficulty conventions.
    /// </summary>
    private static string BuildOlympiadClause(string? olympiadId) => olympiadId switch
    {
        // ── SOF ──────────────────────────────────────────────────────────────
        "sof_imo" => 
            " Mirror the SOF IMO (International Mathematics Olympiad) question style exactly: " +
            "Section A has straightforward curriculum questions; Section B (Achievers) has multi-step " +
            "reasoning with competitive distractors. Use the SOF IMO vocabulary — \"Achievers Section\", " +
            "class-level NCERT curriculum alignment, integer or fractional answers preferred.",

        "sof_nso" =>
            " Mirror the SOF NSO (National Science Olympiad) style: Section A has direct NCERT concept " +
            "questions; Section B (Achievers) uses application and higher-order thinking. " +
            "Cover Physics, Chemistry, Biology as appropriate for the grade. " +
            "Align with the NSO Chapter-wise syllabus.",

        "sof_ieo" =>
            " Mirror the SOF IEO (International English Olympiad) pattern: " +
            "Word and Structure Knowledge, Reading, Spoken and Written Expression. " +
            "Include synonym/antonym, sentence-rearrangement, comprehension passage inference, " +
            "and grammar-in-context questions as IEO does.",

        "sof_nco" =>
            " Mirror the SOF NCO (National Cyber Olympiad) syllabus: " +
            "Computer fundamentals, MS Office, internet basics, binary/logic, " +
            "networking, and for higher classes: Python basics, HTML/CSS, algorithms. " +
            "Section B (Achievers) should have application-level coding-logic questions.",

        "sof_isso" =>
            " Mirror the SOF ISSO (International Social Studies Olympiad) pattern: " +
            "History, Geography, Civics, Economics. Questions should be factual and verifiable. " +
            "Avoid time-sensitive current-affairs questions.",

        "sof_igko" =>
            " Mirror the SOF IGKO (International General Knowledge Olympiad): " +
            "Current affairs, science, sports, awards, famous personalities, world facts. " +
            "All answers must be stable facts — no questions whose answer changes year to year.",

        // ── SilverZone ───────────────────────────────────────────────────────
        "silverzone_math" =>
            " Mirror SilverZone iOM (International Olympiad of Mathematics) style: " +
            "Three sections — Logical Reasoning, Mathematical Reasoning, Everyday Mathematics. " +
            "Questions are slightly more analytical than SOF; avoid purely computational questions. " +
            "SilverZone prefers word-problem framing even for algebraic content.",

        "silverzone_science" =>
            " Mirror SilverZone iOS (International Olympiad of Science) style: " +
            "Application-based questions tied to NCERT; emphasis on experimental reasoning " +
            "and real-world phenomena. Three sections: Science, Applied Science, Achievers.",

        "silverzone_english" =>
            " Mirror SilverZone iOEL (International Olympiad of English Language) pattern: " +
            "Word power, language in use, reading comprehension, creative language. " +
            "Questions are slightly more literary than SOF IEO — include idioms and phrasal verbs.",

        "silverzone_computer" =>
            " Mirror SilverZone iOIT (International Olympiad of Information Technology) pattern: " +
            "Computer concepts, programming logic (Scratch for lower grades, Python for higher), " +
            "internet safety, and digital literacy. Align with the iOIT chapter-wise syllabus.",

        // ── Unified Council ──────────────────────────────────────────────────
        "unified_nstse" =>
            " Mirror the NSTSE (National Level Science Talent Search Exam) by Unified Council: " +
            "Strongly NCERT-aligned, concept-clarity focused. Questions test whether students " +
            "understand the \"why\" behind answers, not just recall. Avoid questions solvable purely " +
            "by rote; prefer reasoning-based MCQs. Mathematics section is included for all grades.",

        "unified_uieo" =>
            " Mirror the UIEO (Unified International English Olympiad) by Unified Council: " +
            "Reading, writing, grammar, and vocabulary. Analytical reading comprehension " +
            "with inference questions. Grammar questions should test usage in context, not rules by rote.",

        // ── CREST ────────────────────────────────────────────────────────────
        "crest_cmo" =>
            " Mirror CREST CMO (CREST Mathematics Olympiad) style: " +
            "Online-exam format. Questions are conceptually deep with elegant solutions. " +
            "CREST favours multi-concept integration — a single question may span geometry + algebra. " +
            "Distractors should be the results of common one-step errors.",

        "crest_cso" =>
            " Mirror CREST CSO (CREST Science Olympiad) style: " +
            "Practical, application-based science. Questions often involve a scenario or mini-experiment " +
            "description before the question. CREST Science leans more applied than SOF NSO.",

        "crest_ceo" =>
            " Mirror CREST CEO (CREST English Olympiad) style: " +
            "High-quality passages with inference and vocabulary-in-context questions. " +
            "Grammar questions are usage-based. CREST English tests critical reading more than SOF IEO.",

        // ── HBCSE ────────────────────────────────────────────────────────────
        "hbcse" =>
            " Mirror the HBCSE National Olympiad Programme (IOQM/RMO/INMO for Math; NSEP/NSEC for Science): " +
            "These are the most rigorous school Olympiads in India. Even for MCQ practice, " +
            "questions should demand deep mathematical or scientific reasoning — no direct-formula plugging. " +
            "For Math: elegant proofs, number theory, combinatorics, geometry with proof steps. " +
            "For Science: derivation-level understanding, advanced NCERT + beyond. " +
            "Distractors must be plausible from a partial-reasoning standpoint.",

        // ── Spell Bee ────────────────────────────────────────────────────────
        "spell_bee" =>
            " This is a Spell Bee competition preparation paper. Focus exclusively on: " +
            "(1) correct spelling of age-appropriate words, " +
            "(2) word meanings and usage in context, " +
            "(3) phonetics and syllabification, " +
            "(4) antonyms and synonyms, " +
            "(5) homophones and commonly confused words. " +
            "Each question must present 4 spelling or vocabulary options. " +
            "Words should be graded to the class level — simpler for Class 1-3, more complex for Class 8-12.",

        // ── Subject-level / open practice (default) ──────────────────────────
        _ => " Questions should follow standard competitive Olympiad exam patterns."
    };

    private class ClaudeResponse
    {
        [JsonPropertyName("content")]
        public List<ClaudeContent> Content { get; set; } = new();

        [JsonPropertyName("usage")]
        public ClaudeUsage? Usage { get; set; }
    }

    private class ClaudeContent
    {
        [JsonPropertyName("type")]
        public string Type { get; set; } = "";

        [JsonPropertyName("text")]
        public string Text { get; set; } = "";
    }

    private class ClaudeUsage
    {
        [JsonPropertyName("input_tokens")]
        public int InputTokens { get; set; }

        [JsonPropertyName("output_tokens")]
        public int OutputTokens { get; set; }

        [JsonPropertyName("cache_creation_input_tokens")]
        public int CacheCreationInputTokens { get; set; }

        [JsonPropertyName("cache_read_input_tokens")]
        public int CacheReadInputTokens { get; set; }
    }
}
