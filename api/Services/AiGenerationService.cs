using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using OlympiadReady.Api.Models;

namespace OlympiadReady.Api.Services;

public class AiGenerationService
{
    private readonly HttpClient _http;
    private readonly ILogger<AiGenerationService> _log;
    private readonly string _apiKey;
    private readonly string _model;
    private readonly string _advancedModel;
    private readonly string _hardModel;
    private readonly int _maxTokens;
    private readonly bool _verifyAnswers;
    private readonly bool _strictVerification;
    private readonly int _reasoningTokens;
    private readonly string _reasoningEffort;

    public AiGenerationService(HttpClient http, IConfiguration config, ILogger<AiGenerationService> log)
    {
        _http = http;
        _log = log;
        _apiKey = config["OpenAi:ApiKey"] ?? "";
        _model = config["OpenAi:Model"] ?? "gpt-4o-mini";

        // Advanced runs on its own model, separate from Olympiad. They used to share
        // _hardModel while being charged different credit amounts — Advanced cost as much
        // per call as Olympiad but was billed as if it were cheap. A smaller reasoning model
        // here is untested against the CREST-derived blueprint and should be validated the
        // same way gpt-5.5 was before it takes real traffic; gpt-5.5 is the safe default
        // until that validation happens.
        _advancedModel = config["OpenAi:AdvancedModel"] ?? "gpt-5.5";

        // Olympiad tier needs a model that can actually reason through a multi-constraint
        // number-theory question rather than pattern-match one. Measured on Class 9
        // Mathematics at Olympiad tier: gpt-4o disagreed with its own answer key on 5 of 7
        // questions and only 2 of 10 survived verification; gpt-5.5 returned 10 of 10, all
        // correct on manual check. The default reflects that.
        _hardModel = config["OpenAi:HardModel"] ?? "gpt-5.5";

        _maxTokens = int.TryParse(config["OpenAi:MaxTokens"], out var m) ? m : 4096;

        // Second pass that re-solves each question from the stem alone. Costs roughly one
        // extra call per batch; catches answers the first pass rationalised.
        _verifyAnswers = !bool.TryParse(config["OpenAi:VerifyAnswers"], out var v) || v;

        // When verification cannot run, discard the batch rather than serving unverified
        // questions. Papers fall back to the reviewed bank, which is the right trade: a
        // short paper is recoverable, a wrong answer key in front of a paying student is not.
        _strictVerification = !bool.TryParse(config["OpenAi:StrictVerification"], out var s) || s;

        _reasoningTokens = int.TryParse(config["OpenAi:ReasoningMaxTokens"], out var rt) ? rt : 16000;
        _reasoningEffort = config["OpenAi:ReasoningEffort"] ?? "medium";
    }

    private static readonly Random _shuffleRng = new();

    /// <summary>
    /// Randomises option order in place. Models have a real, measured tendency to place the
    /// correct answer first (10/10 "A" on some subjects in testing) -- this is what prevents
    /// that from reaching a student or, just as importantly, from being permanently baked into
    /// the bank. Nothing shuffles option order again once a question is fetched back from the
    /// bank, so this MUST run before a question is persisted, not only before it is displayed.
    /// Every caller that saves an AI-generated question to QuestionBank must call this first.
    /// </summary>
    public static void ShuffleOptions(IEnumerable<Question> questions)
    {
        foreach (var q in questions)
        {
            if (q.Options == null || q.Options.Count < 2) continue;
            for (int i = q.Options.Count - 1; i > 0; i--)
            {
                int j = _shuffleRng.Next(i + 1);
                (q.Options[i], q.Options[j]) = (q.Options[j], q.Options[i]);
            }
        }
    }

    /// <summary>
    /// The model a given difficulty tier will actually run on. Exposed so a caller can price
    /// a reservation (<see cref="AiPricing.EstimateCost"/>) before committing to the API call —
    /// the two must agree on which model is being paid for.
    /// </summary>
    public string ModelForDifficulty(string? difficulty, string? olympiadLevel = null)
    {
        if (olympiadLevel == "L2" || string.Equals(difficulty, "Olympiad", StringComparison.OrdinalIgnoreCase))
            return _hardModel;
        if (string.Equals(difficulty, "Advanced", StringComparison.OrdinalIgnoreCase))
            return _advancedModel;
        return _model;
    }

    public async Task<AiGenerationResult> GenerateQuestionsAsync(
        string subject, int grade, string difficulty, int count,
        string? topic = null, CancellationToken ct = default,
        string? olympiadLevel = null, string? olympiadId = null)
    {
        if (string.IsNullOrWhiteSpace(_apiKey) || _apiKey.StartsWith("REPLACE_"))
            throw new InvalidOperationException(
                "OpenAI API key not configured. Set OpenAi:ApiKey via user-secrets or appsettings.");

        var topicClause = topic is not null
            ? $"\n\nEvery question must be on the topic \"{topic}\". Where the blueprint asks for "
              + "an archetype that does not fit this topic, choose the closest archetype that does."
            : "";

        var levelClause = olympiadLevel == "L2"
            ? "\n\nThis is a LEVEL 2 paper — the national/state round, sat by students who have already "
              + "cleared Level 1. Pitch every question at the Achievers Section of a real paper."
            : "";

        var olympiadClause = BuildOlympiadClause(olympiadId);

        var hindiClause = subject.Equals("Hindi", StringComparison.OrdinalIgnoreCase)
            ? "\n\nWrite the question text, options and explanation in Hindi (Devanagari). Keep the "
              + "\"topic\" and \"archetype\" fields in English so the dashboard can group them."
            : "\n\nWrite everything in English.";

        var user =
            $"Set a Class {grade} {subject} paper at the {difficulty} tier."
            + $"\n\n{QuestionPromptLibrary.GradeBand(grade)}"
            + QuestionPromptLibrary.SyllabusScope(subject, grade)
            + QuestionPromptLibrary.BuildBlueprint(subject, grade, difficulty, count)
            + QuestionPromptLibrary.AntiPatterns(difficulty)
            + olympiadClause
            + topicClause
            + levelClause
            + hindiClause;

        var effectiveModel = ModelForDifficulty(difficulty, olympiadLevel);
        var payload = BuildPayload(effectiveModel, QuestionPromptLibrary.SystemPrompt, user);

        // Accumulated across the generation call and the verification call, so the caller can
        // bill the account for what was actually spent rather than an estimate. Returned even
        // on a failure path (as whatever was accumulated before the failure, i.e. zero) so a
        // caller who reserved money for this attempt always has a real figure to reconcile
        // against instead of assuming the reservation was fully consumed.
        var usage = new AiGenerationResult { Model = effectiveModel };

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
                return usage;
            }

            var parsed = JsonSerializer.Deserialize<OpenAiResponse>(body);
            if (parsed is null)
            {
                _log.LogWarning("OpenAI returned empty/unparseable response — falling back to DB questions.");
                return usage;
            }

            if (parsed.Usage is { } u)
            {
                usage.PromptTokens += u.PromptTokens;
                usage.CompletionTokens += u.CompletionTokens;
                _log.LogInformation(
                    "OpenAI usage — prompt: {Prompt}, completion: {Completion}, total: {Total}",
                    u.PromptTokens, u.CompletionTokens, u.TotalTokens);
            }

            var content = parsed.Choices?.FirstOrDefault()?.Message?.Content;
            if (string.IsNullOrWhiteSpace(content))
                return usage;

            var result = JsonSerializer.Deserialize<OpenAiQuestionResponse>(content);
            var questions = result?.Questions ?? new List<AiQuestion>();

            var kept = ValidateQuestions(questions, subject, grade, difficulty);

            if (_verifyAnswers && kept.Count > 0)
            {
                var verified = await VerifyAnswersAsync(kept, subject, grade, difficulty, effectiveModel, ct);
                kept = verified.Kept;
                usage.PromptTokens += verified.PromptTokens;
                usage.CompletionTokens += verified.CompletionTokens;
            }

            // "working" and "distractor_errors" exist only to make the model reason before
            // it commits to an answer. They must never reach a student, so drop them here —
            // the declared Question return type would hide them anyway, but clearing is
            // explicit rather than relying on serializer behaviour.
            foreach (var q in kept) { q.Working = null; q.DistractorErrors = null; }

            usage.Questions = kept.Cast<Question>().ToList();
            return usage;
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "AI generation failed for {Subject} G{Grade} {Difficulty} — falling back to DB questions.",
                subject, grade, difficulty);
            return usage;
        }
    }

    /// <summary>
    /// The o-series reasoning models take a different request shape from the chat models:
    /// the token budget is <c>max_completion_tokens</c>, the instruction turn is
    /// <c>developer</c> rather than <c>system</c>, and sampling parameters are rejected.
    /// Sending the chat shape to one of them fails the whole call.
    /// </summary>
    private static bool IsReasoningModel(string model) =>
        model.StartsWith("o1", StringComparison.OrdinalIgnoreCase) ||
        model.StartsWith("o3", StringComparison.OrdinalIgnoreCase) ||
        model.StartsWith("o4", StringComparison.OrdinalIgnoreCase) ||
        model.StartsWith("gpt-5", StringComparison.OrdinalIgnoreCase);

    private Dictionary<string, object> BuildPayload(string model, string instructions, string user)
    {
        var reasoning = IsReasoningModel(model);

        var payload = new Dictionary<string, object>
        {
            ["model"] = model,
            ["messages"] = new[]
            {
                new { role = reasoning ? "developer" : "system", content = instructions },
                new { role = "user", content = user },
            },
            ["response_format"] = new { type = "json_object" },
        };

        if (reasoning)
        {
            // Reasoning tokens are billed against this budget before any answer is emitted,
            // so a chat-sized limit truncates the response to nothing.
            payload["max_completion_tokens"] = Math.Max(_maxTokens, _reasoningTokens);
            payload["reasoning_effort"] = _reasoningEffort;
        }
        else
        {
            payload["max_tokens"] = _maxTokens;
        }

        return payload;
    }

    /// <summary>
    /// Re-solves each question from its stem and options alone, in a fresh context with no
    /// sight of the proposed answer, and keeps only those where the two passes agree.
    ///
    /// The first pass emits its reasoning and its answer in one response, so it rationalises
    /// whatever it wrote rather than checking it — self-attestation, not verification. Asking
    /// a clean context to sit the question is the cheapest way to catch a wrong answer key.
    /// </summary>
    private async Task<(List<AiQuestion> Kept, int PromptTokens, int CompletionTokens)> VerifyAnswersAsync(
        List<AiQuestion> questions, string subject, int grade, string? difficulty,
        string model, CancellationToken ct)
    {
        var paper = questions.Select((q, i) => new
        {
            n = i + 1,
            question = q.Q,
            options = q.Options,
        });

        const string verifierSystem = """
            You are sitting an examination. For each question you are given the stem and four
            options. Work out the answer yourself. You are NOT told the intended answer and
            must not try to guess which option the setter preferred — solve the question.

            If a question cannot be answered as written — it is ambiguous, two options are
            equally correct, no option is correct, or it refers to a figure that is not
            present — report that instead of guessing.

            Return ONLY JSON: {"answers":[{"n":1,"letter":"A","confident":true,"issue":null}]}
            Set "letter" to A, B, C or D. Set "confident" to false and put a one-line reason in
            "issue" when the question is defective.
            """;

        var payload = BuildPayload(model, verifierSystem, JsonSerializer.Serialize(paper));

        // Unverified questions are only served when the operator has explicitly opted out
        // of strict mode; otherwise a failed check discards the batch and the caller falls
        // back to the reviewed bank. Either way this call still cost real tokens, so the
        // usage captured below is returned regardless of which branch is taken.
        var onFailureQuestions = _strictVerification ? new List<AiQuestion>() : questions;
        var promptTokens = 0;
        var completionTokens = 0;

        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Post, "v1/chat/completions");
            req.Headers.Add("Authorization", $"Bearer {_apiKey}");
            req.Content = JsonContent.Create(payload);

            using var res = await _http.SendAsync(req, ct);
            if (!res.IsSuccessStatusCode)
            {
                var err = await res.Content.ReadAsStringAsync(ct);
                _log.LogWarning("Answer verification call failed ({Status}): {Body}. Strict={Strict}.",
                    res.StatusCode, err.Length > 300 ? err[..300] : err, _strictVerification);
                return (onFailureQuestions, promptTokens, completionTokens);
            }

            var body = await res.Content.ReadAsStringAsync(ct);
            var parsedVerify = JsonSerializer.Deserialize<OpenAiResponse>(body);
            if (parsedVerify?.Usage is { } vu)
            {
                promptTokens = vu.PromptTokens;
                completionTokens = vu.CompletionTokens;
            }

            var content = parsedVerify?.Choices?.FirstOrDefault()?.Message?.Content;
            if (string.IsNullOrWhiteSpace(content))
            {
                _log.LogWarning("Answer verification returned nothing. Strict={Strict}.", _strictVerification);
                return (onFailureQuestions, promptTokens, completionTokens);
            }

            var verdicts = JsonSerializer.Deserialize<VerifierResponse>(content)?.Answers;
            if (verdicts is null || verdicts.Count == 0)
            {
                _log.LogWarning("Answer verification returned no verdicts. Strict={Strict}.", _strictVerification);
                return (onFailureQuestions, promptTokens, completionTokens);
            }

            var byIndex = verdicts.ToDictionary(a => a.N, a => a);
            var kept = new List<AiQuestion>();

            for (var i = 0; i < questions.Count; i++)
            {
                var q = questions[i];
                if (!byIndex.TryGetValue(i + 1, out var verdict))
                {
                    // No verdict means no evidence either way. Under strict mode an
                    // unchecked question is not good enough to serve.
                    if (!_strictVerification) kept.Add(q);
                    else _log.LogInformation("Question dropped — verifier returned no verdict for it.");
                    continue;
                }

                if (!verdict.Confident)
                {
                    _log.LogInformation("Question dropped — verifier flagged it as defective: {Issue}. {Subject} G{Grade} {Diff}",
                        verdict.Issue, subject, grade, difficulty);
                    continue;
                }

                var proposed = q.CorrectOptionLetter?.Trim().ToUpperInvariant();
                var solved = verdict.Letter?.Trim().ToUpperInvariant();
                if (!string.IsNullOrEmpty(solved) && !string.IsNullOrEmpty(proposed) && solved != proposed)
                {
                    _log.LogInformation("Question dropped — setter said {Proposed}, independent solve said {Solved}. {Subject} G{Grade} {Diff}",
                        proposed, solved, subject, grade, difficulty);
                    continue;
                }

                kept.Add(q);
            }

            if (kept.Count < questions.Count)
                _log.LogInformation("Answer verification: {Kept}/{Total} agreed for {Subject} G{Grade} {Diff}",
                    kept.Count, questions.Count, subject, grade, difficulty);

            return (kept, promptTokens, completionTokens);
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Answer verification errored. Strict={Strict}.", _strictVerification);
            return (onFailureQuestions, promptTokens, completionTokens);
        }
    }

    /// <summary>
    /// Repairs LaTeX commands destroyed by JSON string-escape processing.
    ///
    /// A model that writes <c>"12 \times 0.60"</c> instead of <c>"12 \\times 0.60"</c> hands us
    /// a legal JSON escape: <c>\t</c> is a tab. The deserialiser therefore stores TAB + "imes",
    /// and the same happens for <c>\rightarrow</c> (CR), <c>\frac</c> (FF), <c>\neq</c> (LF) and
    /// <c>\bar</c> (backspace). The system prompt now demands doubled backslashes, but models
    /// slip, so restore the command here rather than persisting corrupted text.
    /// </summary>
    internal static string RepairLatexEscapes(string? text)
    {
        if (string.IsNullOrEmpty(text)) return text ?? "";

        // Only pay for the scan when a suspect control character is actually present.
        var hasSuspect = false;
        foreach (var c in text)
        {
            if (c is '\t' or '\r' or '\f' or '\b' or '\v' or '\n') { hasSuspect = true; break; }
        }
        if (!hasSuspect) return text;

        foreach (var (ctrl, letter, tail) in LatexEscapeVictims)
        {
            // "\times" arrives as TAB + "imes"; the escape swallowed the 't'.
            // Rebuild it as backslash + letter + tail.
            var broken = ctrl + tail;
            if (text.Contains(broken, StringComparison.Ordinal))
                text = text.Replace(broken, "\\" + letter + tail, StringComparison.Ordinal);
        }
        return text;
    }

    /// <summary>
    /// (control character, letter the escape consumed, remaining tail).
    /// "\t" + "imes" came from "\times", so the letter is 't'.
    /// Longest tails first so "\rightarrow" is matched before "\right".
    /// </summary>
    private static readonly (string Ctrl, string Letter, string Tail)[] LatexEscapeVictims =
    {
        ("\r", "r", "ightarrow"), ("\r", "r", "ight"),
        ("\t", "t", "imes"), ("\t", "t", "heta"), ("\t", "t", "riangle"),
        ("\t", "t", "ext"), ("\t", "t", "an"),
        ("\f", "f", "rac"), ("\f", "f", "orall"),
        ("\b", "b", "eta"), ("\b", "b", "inom"), ("\b", "b", "ar"),
        ("\v", "v", "ec"),
        ("\n", "n", "eq"), ("\n", "n", "abla"),
    };

    /// <summary>Applies <see cref="RepairLatexEscapes"/> across every text field of a question.</summary>
    private static void RepairQuestion(AiQuestion q)
    {
        q.Q = RepairLatexEscapes(q.Q);
        q.Answer = RepairLatexEscapes(q.Answer);
        q.Explanation = RepairLatexEscapes(q.Explanation);
        if (q.Options is not null)
        {
            for (var i = 0; i < q.Options.Count; i++)
                q.Options[i] = RepairLatexEscapes(q.Options[i]);
        }
    }

    private List<AiQuestion> ValidateQuestions(List<AiQuestion> questions, string subject, int grade, string? difficulty)
    {
        var valid = new List<AiQuestion>();
        var imageRefPatterns = new[] { "see figure", "as shown", "in the diagram", "refer to the figure", "from the passage", "in the figure", "shown below", "shown above", "see table", "see chart" };

        foreach (var q in questions)
        {
            // Undo JSON-escape damage before any other check reads these fields.
            RepairQuestion(q);

            // All required text fields must be non-empty
            if (string.IsNullOrWhiteSpace(q.Q) ||
                string.IsNullOrWhiteSpace(q.Answer) ||
                string.IsNullOrWhiteSpace(q.Explanation))
            {
                _log.LogWarning("AI question dropped: missing required field. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // Must have exactly 4 non-empty options
            if (q.Options == null || q.Options.Count != 4 || q.Options.Any(o => string.IsNullOrWhiteSpace(o)))
            {
                _log.LogWarning("AI question dropped: invalid option count ({Count}). Subject={Subject} G{Grade} {Diff}", q.Options?.Count ?? 0, subject, grade, difficulty);
                continue;
            }

            // answer must be one of the 4 options
            if (!q.Options.Any(o => string.Equals(o.Trim(), q.Answer.Trim(), StringComparison.OrdinalIgnoreCase)))
            {
                _log.LogWarning("AI question dropped: answer '{Answer}' not found in options. Subject={Subject} G{Grade} {Diff}", q.Answer, subject, grade, difficulty);
                continue;
            }

            // If correct_option_letter is present, verify it matches the answer
            if (!string.IsNullOrWhiteSpace(q.CorrectOptionLetter))
            {
                var letter = q.CorrectOptionLetter.Trim().ToUpperInvariant();
                if (letter is "A" or "B" or "C" or "D")
                {
                    var idx = letter[0] - 'A';
                    var expectedAnswer = q.Options[idx].Trim();
                    if (!string.Equals(q.Answer.Trim(), expectedAnswer, StringComparison.OrdinalIgnoreCase))
                    {
                        _log.LogWarning("AI question dropped: answer/letter mismatch. Letter={Letter}, Answer='{Answer}', Option='{Option}'. Subject={Subject} G{Grade} {Diff}",
                            letter, q.Answer, expectedAnswer, subject, grade, difficulty);
                        continue;
                    }
                }
            }

            // Reject questions referencing images/diagrams
            var qLower = q.Q.ToLowerInvariant();
            if (imageRefPatterns.Any(p => qLower.Contains(p)))
            {
                _log.LogWarning("AI question dropped: image/diagram reference detected. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // No duplicate options (case-insensitive, trimmed)
            var distinct = q.Options.Select(o => o.Trim().ToLowerInvariant()).Distinct().Count();
            if (distinct < 4)
            {
                _log.LogWarning("AI question dropped: duplicate options detected. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // Two options can be the same expression written in a different order —
            // "$x^2 + \frac{1}{x^2} + 2$" and "$x^2 + 2$ + $\frac{1}{x^2}$" are one answer
            // twice, which makes the question unanswerable. Compare the character multiset
            // of the algebra, which is invariant under reordering of terms.
            var algebraic = q.Options
                .Where(o => o.Length > 10 && o.IndexOfAny(new[] { '\\', '^', '_' }) >= 0)
                .Select(AlgebraFingerprint)
                .ToList();
            if (algebraic.Count > 1 && algebraic.Distinct().Count() < algebraic.Count)
            {
                _log.LogWarning("AI question dropped: two options are the same expression reordered. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // No incomplete options (trailing ellipsis)
            if (q.Options.Any(o => o.TrimEnd().EndsWith("...")))
            {
                _log.LogWarning("AI question dropped: option ends with ellipsis. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // Unbalanced $ or braces render as a red KaTeX error on the student's screen.
            var fields = new[] { q.Q, q.Explanation }.Concat(q.Options);
            if (fields.Any(f => !LatexIsBalanced(f)))
            {
                _log.LogWarning("AI question dropped: unbalanced LaTeX delimiters or braces. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // A "$" before a digit is money, and money must be rupees — otherwise KaTeX
            // swallows it as a formula and strips the spaces out of the sentence.
            if (fields.Any(ContainsDollarCurrency))
            {
                _log.LogWarning("AI question dropped: dollar-sign currency would be parsed as maths. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // The explanation must actually name the answer, not gesture at it.
            if (!ExplanationNamesAnswer(q.Explanation, q.Answer))
            {
                _log.LogWarning("AI question dropped: explanation never states the answer '{Answer}'. Subject={Subject} G{Grade} {Diff}", q.Answer, subject, grade, difficulty);
                continue;
            }

            // The renderer prints options below the stem; a stem that also lists them shows
            // the student the same four choices twice.
            if (StemRepeatsOptions(q.Q, q.Options))
            {
                _log.LogWarning("AI question dropped: options duplicated inside the question text. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // An explanation that only gestures at a method is worse than none.
            if (q.Explanation.Trim().Length < 40)
            {
                _log.LogWarning("AI question dropped: explanation too short to be a solution. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // "All of the above" and friends are forbidden by the prompt but slip through.
            if (q.Options.Any(o => BannedOption.IsMatch(o)))
            {
                _log.LogWarning("AI question dropped: banned option form (all/none of the above). Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            // Young students find negative stems confusing; the prompt forbids them below
            // Class 6, so enforce it rather than trusting the instruction.
            if (grade <= 5 && NegativeStem.IsMatch(q.Q))
            {
                _log.LogWarning("AI question dropped: negative stem below Class 6. Subject={Subject} G{Grade} {Diff}", subject, grade, difficulty);
                continue;
            }

            valid.Add(q);
        }

        if (valid.Count < questions.Count)
            _log.LogInformation("AI validation: {Kept}/{Total} questions passed for {Subject} G{Grade} {Diff}", valid.Count, questions.Count, subject, grade, difficulty);

        return valid;
    }

    private static readonly System.Text.RegularExpressions.Regex NegativeStem =
        new(@"\bNOT\b|\bEXCEPT\b|\bINCORRECT\b|\bFALSE\b|\bcannot\b",
            System.Text.RegularExpressions.RegexOptions.Compiled);

    private static readonly System.Text.RegularExpressions.Regex TwoWords =
        new(@"[A-Za-z]{2,}\s+[A-Za-z]{2,}", System.Text.RegularExpressions.RegexOptions.Compiled);

    private static readonly System.Text.RegularExpressions.Regex ProseWord =
        new(@"\b(?:and|the|for|of|in|is|are|to|from|with|by|on|at|each|per|total|amount|cost|costs|price|profit|paid|bought|sold|spent|saved|rupees?|dollars?)\b",
            System.Text.RegularExpressions.RegexOptions.IgnoreCase | System.Text.RegularExpressions.RegexOptions.Compiled);

    /// <summary>
    /// True when a "$" is being used as a currency symbol rather than a maths delimiter.
    ///
    /// A naive "$ followed by a digit" test is wrong: legitimate LaTeX routinely starts with
    /// a digit ($5^{2x-1}$, $2x$, $11011011_2$), and rejecting those throws away most of a
    /// maths paper. Mirrors the classifier in web/lib/notation.ts — pair the delimiters, then
    /// judge each span by its contents and by what follows the closing "$".
    /// </summary>
    private static bool ContainsDollarCurrency(string? text)
    {
        if (string.IsNullOrEmpty(text) || !text.Contains('$')) return false;

        var marks = new List<int>();
        for (var i = 0; i < text.Length; i++)
            if (text[i] == '$' && (i == 0 || text[i - 1] != '\\')) marks.Add(i);
        if (marks.Count == 0) return false;

        var k = 0;
        while (k < marks.Count - 1)
        {
            int open = marks[k], close = marks[k + 1];
            var content = text[(open + 1)..close];
            var after = close + 1 < text.Length ? text[close + 1] : '\0';

            // Anything carrying LaTeX syntax is maths, whatever else it looks like.
            var definitelyMath = content.IndexOfAny(new[] { '\\', '^', '_', '{', '}' }) >= 0;

            // Money when the "closing" $ is glued to the next amount ("₹20 - $15"), or when
            // the span reads as a sentence rather than an expression.
            var looksLikeMoney = char.IsDigit(after) || (TwoWords.IsMatch(content) && ProseWord.IsMatch(content));

            if (!definitelyMath && looksLikeMoney) return true;
            k += 2;
        }

        // A leftover unpaired "$" stuck to a number is a price.
        if (marks.Count % 2 == 1)
        {
            var last = marks[^1];
            if (last + 1 < text.Length && char.IsDigit(text[last + 1])) return true;
        }
        return false;
    }

    /// <summary>
    /// Options the papers never use and the prompt forbids. "Both 1 and 2" is deliberately
    /// allowed — numbered sub-statement questions are a real and common archetype; it is
    /// only the lettered "Both a and b" and the "of the above" forms that are banned.
    /// </summary>
    private static readonly System.Text.RegularExpressions.Regex BannedOption =
        new(@"^\s*(?:all|none)\s+of\s+the\s+above\s*\.?\s*$|^\s*both\s+[a-d]\s+and\s+[a-d]\s*\.?\s*$|^\s*cannot\s+be\s+determined\s*\.?\s*$",
            System.Text.RegularExpressions.RegexOptions.IgnoreCase | System.Text.RegularExpressions.RegexOptions.Compiled);

    /// <summary>
    /// True when every "$" has a partner and every "{" is closed. KaTeX renders an
    /// unbalanced expression as red error text, so it is better to drop the question.
    /// </summary>
    private static bool LatexIsBalanced(string? text)
    {
        if (string.IsNullOrEmpty(text)) return true;

        var dollars = 0;
        var braces = 0;
        for (var i = 0; i < text.Length; i++)
        {
            if (text[i] == '\\') { i++; continue; }   // escaped character, skip the pair
            if (text[i] == '$') dollars++;
            else if (text[i] == '{') braces++;
            else if (text[i] == '}') braces--;
            if (braces < 0) return false;
        }
        return dollars % 2 == 0 && braces == 0;
    }

    /// <summary>
    /// Order-insensitive signature of an algebraic option: drop delimiters and whitespace,
    /// then sort the remaining characters. Two options that are the same sum written in a
    /// different order collapse to the same fingerprint. Only applied to options that
    /// actually contain LaTeX, so plain numbers like "12" and "21" are never compared this
    /// way.
    /// </summary>
    private static string AlgebraFingerprint(string option)
    {
        var chars = option
            .Where(c => !char.IsWhiteSpace(c) && c != '$' && c != '{' && c != '}')
            .Select(char.ToLowerInvariant)
            .OrderBy(c => c)
            .ToArray();
        return new string(chars);
    }

    /// <summary>
    /// True when the stem already contains the answer options. Models sometimes emit the
    /// full multiple-choice block inside "q" as well as in "options", which renders the
    /// same four choices twice. Two or more full matches is conclusive.
    /// </summary>
    private static bool StemRepeatsOptions(string? stem, List<string>? options)
    {
        if (string.IsNullOrEmpty(stem) || options is null) return false;
        var repeated = options.Count(o =>
            !string.IsNullOrWhiteSpace(o) && o.Trim().Length > 8 &&
            stem.Contains(o.Trim(), StringComparison.OrdinalIgnoreCase));
        return repeated >= 2;
    }

    /// <summary>
    /// A numeric answer must appear verbatim in the explanation — "the answer is 13 cm", not
    /// "therefore it is the second option".
    ///
    /// Only numeric answers are checked. A prose answer can be restated correctly in many
    /// ways ("condenses" explained as "condensation"; an option of "I only" explained by
    /// discussing statement I), so keyword matching there rejects sound questions.
    /// </summary>
    private static bool ExplanationNamesAnswer(string? explanation, string? answer)
    {
        if (string.IsNullOrWhiteSpace(explanation) || string.IsNullOrWhiteSpace(answer)) return false;

        var numbers = System.Text.RegularExpressions.Regex.Matches(answer, @"-?\d+(?:\.\d+)?")
            .Select(m => m.Value)
            .ToList();

        return numbers.Count == 0 || numbers.Any(n => explanation.Contains(n, StringComparison.Ordinal));
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
        public List<AiQuestion>? Questions { get; set; }
    }

    /// <summary>
    /// A generation call's output plus the real token usage it cost, across both the
    /// generation and verification passes. Callers use <see cref="PromptTokens"/> and
    /// <see cref="CompletionTokens"/> with <see cref="AiPricing.ActualCost"/> to reconcile a
    /// pre-call spend reservation against what was actually spent — never estimated.
    /// </summary>
    public class AiGenerationResult
    {
        public List<Question> Questions { get; set; } = new();
        public int PromptTokens { get; set; }
        public int CompletionTokens { get; set; }
        public string Model { get; set; } = "";
    }

    /// <summary>
    /// A generated question plus the fields that exist only to force the model to reason
    /// before committing to an answer. Declared as a subclass so callers receiving
    /// <see cref="Question"/> cannot accidentally serialise the worked solution to a student.
    /// </summary>
    internal class AiQuestion : Question
    {
        /// <summary>The archetype code from the blueprint, used to check the mix.</summary>
        [JsonPropertyName("archetype")]
        public string? Archetype { get; set; }

        /// <summary>The model's own worked solution. Cleared before the question is returned.</summary>
        [JsonPropertyName("working")]
        public string? Working { get; set; }

        /// <summary>One named mistake per wrong option. Cleared before the question is returned.</summary>
        [JsonPropertyName("distractor_errors")]
        public List<string>? DistractorErrors { get; set; }
    }

    private class VerifierResponse
    {
        [JsonPropertyName("answers")]
        public List<VerifierAnswer>? Answers { get; set; }
    }

    private class VerifierAnswer
    {
        [JsonPropertyName("n")]
        public int N { get; set; }

        [JsonPropertyName("letter")]
        public string? Letter { get; set; }

        [JsonPropertyName("confident")]
        public bool Confident { get; set; } = true;

        [JsonPropertyName("issue")]
        public string? Issue { get; set; }
    }
}
