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
        Class (1-12), Subject (Math, Science, English, Hindi, General Knowledge,
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
        string? topic = null, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(_apiKey) || _apiKey.StartsWith("REPLACE_"))
            throw new InvalidOperationException(
                "Anthropic API key not configured. Set Anthropic:ApiKey via user-secrets or appsettings.");

        var topicClause = topic is not null
            ? $" ALL questions must be exclusively about the topic \"{topic}\" — do not include questions on other topics."
            : "";

        var user =
            $"Generate exactly {count} multiple-choice questions for Class {grade} {subject} " +
            $"at {difficulty} difficulty.{topicClause} Follow the schema and rules from the system prompt strictly.";

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
