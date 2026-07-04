using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/papers")]
public class PapersController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly AiGenerationService _ai;
    private readonly UserService _users;
    private readonly SubscriptionService _subs;
    private readonly QuestionBankService _bank;
    private readonly ILogger<PapersController> _log;

    public PapersController(
        AppDbContext db,
        AiGenerationService ai,
        UserService users,
        SubscriptionService subs,
        QuestionBankService bank,
        ILogger<PapersController> log)
    {
        _db = db;
        _ai = ai;
        _users = users;
        _subs = subs;
        _bank = bank;
        _log = log;
    }

    [HttpPost("generate")]
    [Microsoft.AspNetCore.RateLimiting.EnableRateLimiting("AiGenerationPolicy")]
    public async Task<IActionResult> Generate(
        [FromBody] GeneratePaperRequest req, CancellationToken ct)
    {
        try
        {
            var user = await _users.GetOrSyncAsync(User, ct);

            bool isAllowed = await _subs.CanGenerateOnlineTestAsync(user.UserId, req.Grade, req.Subject, ct);
            if (!isAllowed)
            {
                return StatusCode(StatusCodes.Status402PaymentRequired, new
                {
                    code = "QUOTA_EXCEEDED",
                    message = $"You have used your free attempts. Please unlock Class {req.Grade} {req.Subject} to continue practicing.",
                    upgrade = true
                });
            }

            bool useHybridAi = await _subs.ShouldUseHybridAiAsync(user.UserId, req.Grade, req.Subject, req.Difficulty, ct);
            
            string jsonContent;
            List<Question> questions = new();

            bool isTestAccount = user.Email.Contains("test", StringComparison.OrdinalIgnoreCase) || 
                                 user.Email.Contains("razorpay", StringComparison.OrdinalIgnoreCase);

            if (req.MistakesOnly)
            {
                var query = _db.UserMistakes
                    .AsNoTracking()
                    .Where(m => m.UserId == user.UserId && !m.IsResolved && m.Subject == req.Subject && m.Grade == req.Grade);

                if (!string.IsNullOrEmpty(req.Topic))
                {
                    query = query.Where(m => m.Topic == req.Topic);
                }

                var unresolvedMistakes = await query
                    .OrderBy(m => Guid.NewGuid()) // Random order
                    .Take(req.Count)
                    .ToListAsync(ct);

                if (unresolvedMistakes.Count == 0)
                {
                    return BadRequest(new
                    {
                        code = "NO_MISTAKES",
                        message = $"No unresolved mistakes found for {req.Subject} Class {req.Grade}."
                    });
                }

                questions = unresolvedMistakes
                    .Select(m => JsonSerializer.Deserialize<Question>(m.QuestionJson))
                    .Where(q => q != null)
                    .Cast<Question>()
                    .ToList();

                jsonContent = JsonSerializer.Serialize(questions);
            }
            else
            {
                // Hybrid Logic
                int aiCount = (useHybridAi && !isTestAccount) ? Math.Min(req.Count, 20) : 0;
                int dbCount = req.Count - aiCount;

                var finalQuestions = new List<Question>();

                if (dbCount > 0)
                {
                    var bankQuestions = await FetchBankWithImageMixAsync(
                        req.Subject, req.Grade, req.Difficulty, dbCount, req.Topic, ct);
                    finalQuestions.AddRange(bankQuestions);
                }

                if (aiCount > 0)
                {
                    _log.LogInformation("Hybrid generation: calling AI for {Count} questions (olympiad={OlympiadId})", aiCount, req.OlympiadId ?? "open");
                    var aiQuestions = await _ai.GenerateQuestionsAsync(
                        req.Subject, req.Grade, req.Difficulty, aiCount, req.Topic, ct, req.OlympiadLevel, req.OlympiadId);
                    ShuffleOptions(aiQuestions);
                    finalQuestions.AddRange(aiQuestions);

                    // Flywheel: Save AI questions back to the Question Bank
                    foreach (var q in aiQuestions)
                        SaveAiQuestionToBank(q, req.Subject, req.Grade, req.Difficulty);
                }

                // If AI fell short (or AI was skipped), top up from DB
                int shortfall = req.Count - finalQuestions.Count;
                if (shortfall > 0)
                {
                    var extraBankQuestions = await FetchBankWithImageMixAsync(
                        req.Subject, req.Grade, req.Difficulty, shortfall, req.Topic, ct);
                    finalQuestions.AddRange(extraBankQuestions);
                }

                // Last resort: if DB is still exhausted, call AI regardless of tier
                int aiShortfall = req.Count - finalQuestions.Count;
                if (aiShortfall > 0 && !isTestAccount)
                {
                    _log.LogInformation("DB exhausted shortfall: calling AI for {Count} questions as last resort", aiShortfall);
                    var aiShortfallQuestions = await _ai.GenerateQuestionsAsync(
                        req.Subject, req.Grade, req.Difficulty, aiShortfall, req.Topic, ct, req.OlympiadLevel, req.OlympiadId);
                    ShuffleOptions(aiShortfallQuestions);
                    finalQuestions.AddRange(aiShortfallQuestions);
                    foreach (var q in aiShortfallQuestions)
                        SaveAiQuestionToBank(q, req.Subject, req.Grade, req.Difficulty);
                }

                if (finalQuestions.Count == 0)
                {
                    return StatusCode(StatusCodes.Status503ServiceUnavailable, new
                    {
                        code = "BANK_INSUFFICIENT",
                        message = $"Not enough questions for {req.Subject} Class {req.Grade}. Please try another topic.",
                    });
                }

                questions = finalQuestions.OrderBy(q => Guid.NewGuid()).Take(req.Count).ToList();
                jsonContent = JsonSerializer.Serialize(questions);

                await _subs.RecordOnlineTestGenerationAsync(user.UserId, req.Grade, req.Subject, useHybridAi, req.Difficulty, ct);
            }

            var paper = new QuestionPaper
            {
                UserId = user.UserId,
                Title = $"Class {req.Grade} {req.Subject} · {req.Difficulty}",
                Grade = req.Grade,
                Subject = req.Subject,
                DifficultyLevel = req.Difficulty,
                JsonContent = jsonContent,
                ContentHash = PaperCacheKey.Compute(req.Subject, req.Grade, req.Difficulty, req.Count)
            };
            // ContentHash is kept for future analytics; it is no longer used as a cache lookup key.
            _db.Papers.Add(paper);
            await _db.SaveChangesAsync(ct);

            return Ok(new
            {
                paperId = paper.PaperId,
                title = paper.Title,
                subject = paper.Subject,
                grade = paper.Grade,
                difficulty = paper.DifficultyLevel,
                questions
            });
        }
        catch (InvalidOperationException ex)
        {
            _log.LogWarning(ex, "Paper generation failed");
            return Problem(ex.Message, statusCode: 500);
        }
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> Get(Guid id, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        var paper = await _db.Papers.AsNoTracking().FirstOrDefaultAsync(p => p.PaperId == id, ct);
        if (paper is null) return NotFound();
        if (paper.UserId != user.UserId) return Forbid();

        var questions = JsonSerializer.Deserialize<List<Question>>(paper.JsonContent) ?? new();
        return Ok(new
        {
            paperId = paper.PaperId,
            title = paper.Title,
            subject = paper.Subject,
            grade = paper.Grade,
            difficulty = paper.DifficultyLevel,
            createdAt = paper.CreatedAt,
            questions
        });
    }

    // ---------------------------------------------------------------
    // Flywheel helper
    // ---------------------------------------------------------------

    /// <summary>
    /// Saves one AI-generated question to the QuestionBank.
    /// Validates that q.Answer matches exactly one option before saving.
    /// If the answer cannot be resolved (idx == -1), the question is NOT saved —
    /// it was still shown to the student this session but won't pollute the bank.
    /// </summary>
    // Subjects where image-based questions are meaningful (geometry, science diagrams, etc.)
    private static readonly HashSet<string> _imageSubjects = new(StringComparer.OrdinalIgnoreCase)
    {
        "Mathematics", "Science", "Science-Physics", "Science-Chemistry", "Science-Biology",
        "EVS", "General Knowledge", "GK", "Social Studies", "SST"
    };

    /// <summary>
    /// Fetches from the question bank with ~33% image questions when the subject supports it.
    /// Falls back gracefully if image questions aren't available.
    /// </summary>
    private async Task<List<Question>> FetchBankWithImageMixAsync(
        string subject, int grade, string? difficulty, int count, string? topic, CancellationToken ct,
        IEnumerable<Guid>? excludeIds = null)
    {
        bool wantMix = _imageSubjects.Contains(subject) && count >= 3;
        if (!wantMix)
            return await _bank.TryGetRandomAsync(subject, grade, difficulty, count, topic, ct, excludeIds) ?? new();

        int imageTarget = Math.Max(1, count / 3);

        var imageQs = await _bank.TryGetRandomAsync(subject, grade, difficulty, imageTarget, topic, ct, excludeIds, hasImage: true) ?? new();

        var afterImageExclude = (excludeIds ?? Enumerable.Empty<Guid>())
            .Concat(imageQs.Select(q => q.BankId).Where(id => id != Guid.Empty));

        int textFetch = count - imageQs.Count;
        var textQs = await _bank.TryGetRandomAsync(subject, grade, difficulty, textFetch, topic, ct, afterImageExclude, hasImage: false) ?? new();

        var combined = imageQs.Concat(textQs).ToList();

        // Top up without image filter if either pool was exhausted
        int gap = count - combined.Count;
        if (gap > 0)
        {
            var allExclude = afterImageExclude
                .Concat(textQs.Select(q => q.BankId).Where(id => id != Guid.Empty));
            var fillQs = await _bank.TryGetRandomAsync(subject, grade, difficulty, gap, topic, ct, allExclude) ?? new();
            combined.AddRange(fillQs);
        }

        return combined;
    }

    private static readonly Random _rng = new();

    /// <summary>
    /// Shuffle each question's options in-place. Answer stores full text so it stays correct after reordering.
    /// Fixes LLM bias of placing the correct answer at position A most of the time.
    /// </summary>
    private static void ShuffleOptions(IEnumerable<Question> questions)
    {
        foreach (var q in questions)
        {
            if (q.Options == null || q.Options.Count < 2) continue;
            for (int i = q.Options.Count - 1; i > 0; i--)
            {
                int j = _rng.Next(i + 1);
                (q.Options[i], q.Options[j]) = (q.Options[j], q.Options[i]);
            }
        }
    }

    private void SaveAiQuestionToBank(Question q, string subject, int grade, string difficulty)
    {
        if (q.Options == null || q.Options.Count == 0)
        {
            _log.LogWarning("Flywheel skip — no options for question: {Q}", q.Q?[..Math.Min(80, q.Q?.Length ?? 0)]);
            return;
        }

        int idx = q.Options.FindIndex(o =>
            string.Equals(o.Trim(), q.Answer?.Trim(), StringComparison.OrdinalIgnoreCase));

        if (idx < 0 || idx > 3)
        {
            // Answer text did not match any option — saving with wrong letter would corrupt the bank
            _log.LogWarning(
                "Flywheel skip — answer '{Answer}' not found in options for question: {Q}. Options: {Opts}",
                q.Answer, q.Q?[..Math.Min(80, q.Q?.Length ?? 0)],
                string.Join(" | ", q.Options));
            return;
        }

        string letterAnswer = ((char)('A' + idx)).ToString();

        var newBankId = Guid.NewGuid();
        _db.QuestionBank.Add(new QuestionBankItem
        {
            QuestionBankId = newBankId,
            Subject = subject,
            Grade = grade,
            Difficulty = difficulty,
            Topic = q.Topic ?? "General",
            QuestionText = q.Q ?? "",
            OptionsJson = JsonSerializer.Serialize(q.Options),
            CorrectAnswer = letterAnswer,
            Explanation = q.Explanation ?? "",
            CreatedAt = DateTime.UtcNow
        });
        q.BankId = newBankId;
    }
}
