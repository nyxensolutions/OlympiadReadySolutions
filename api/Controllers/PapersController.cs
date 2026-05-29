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

            bool useHybridAi = await _subs.ShouldUseHybridAiAsync(user.UserId, req.Grade, req.Subject, ct);
            
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
                    var bankQuestions = await _bank.TryGetRandomAsync(
                        req.Subject, req.Grade, req.Difficulty, dbCount, req.Topic, ct);
                    if (bankQuestions != null) finalQuestions.AddRange(bankQuestions);
                }

                if (aiCount > 0)
                {
                    _log.LogInformation("Hybrid generation: calling AI for {Count} questions (olympiad={OlympiadId})", aiCount, req.OlympiadId ?? "open");
                    var aiQuestions = await _ai.GenerateQuestionsAsync(
                        req.Subject, req.Grade, req.Difficulty, aiCount, req.Topic, ct, req.OlympiadLevel, req.OlympiadId);
                    
                    finalQuestions.AddRange(aiQuestions);
                    
                    // Flywheel: Save AI questions back to the Question Bank
                    foreach(var q in aiQuestions)
                    {
                        int idx = q.Options != null ? q.Options.FindIndex(o => string.Equals(o.Trim(), q.Answer?.Trim(), StringComparison.OrdinalIgnoreCase)) : 0;
                        string letterAnswer = (idx >= 0 && idx <= 3) ? ((char)('A' + idx)).ToString() : "A";

                        var newBankId = Guid.NewGuid();
                        var qbItem = new QuestionBankItem
                        {
                            QuestionBankId = newBankId,
                            Subject = req.Subject,
                            Grade = req.Grade,
                            Difficulty = req.Difficulty,
                            Topic = q.Topic ?? "General",
                            QuestionText = q.Q ?? "",
                            OptionsJson = JsonSerializer.Serialize(q.Options ?? new List<string>()),
                            CorrectAnswer = letterAnswer,
                            Explanation = q.Explanation ?? "",
                            CreatedAt = DateTime.UtcNow
                        };
                        _db.QuestionBank.Add(qbItem);
                        q.BankId = newBankId;
                    }
                }

                // If AI fell short (or AI was skipped), top up from DB
                int shortfall = req.Count - finalQuestions.Count;
                if (shortfall > 0)
                {
                    var extraBankQuestions = await _bank.TryGetRandomAsync(
                        req.Subject, req.Grade, req.Difficulty, shortfall, req.Topic, ct);
                    if (extraBankQuestions != null) finalQuestions.AddRange(extraBankQuestions);
                }

                // Last resort: if DB is still exhausted, call AI regardless of tier
                int aiShortfall = req.Count - finalQuestions.Count;
                if (aiShortfall > 0 && !isTestAccount)
                {
                    _log.LogInformation("DB exhausted shortfall: calling AI for {Count} questions as last resort", aiShortfall);
                    var aiShortfallQuestions = await _ai.GenerateQuestionsAsync(
                        req.Subject, req.Grade, req.Difficulty, aiShortfall, req.Topic, ct, req.OlympiadLevel, req.OlympiadId);
                    finalQuestions.AddRange(aiShortfallQuestions);
                    foreach (var q in aiShortfallQuestions)
                    {
                        int idx = q.Options != null ? q.Options.FindIndex(o => string.Equals(o.Trim(), q.Answer?.Trim(), StringComparison.OrdinalIgnoreCase)) : 0;
                        string letterAnswer = (idx >= 0 && idx <= 3) ? ((char)('A' + idx)).ToString() : "A";
                        var newBankId = Guid.NewGuid();
                        _db.QuestionBank.Add(new QuestionBankItem
                        {
                            QuestionBankId = newBankId,
                            Subject = req.Subject,
                            Grade = req.Grade,
                            Difficulty = req.Difficulty,
                            Topic = q.Topic ?? "General",
                            QuestionText = q.Q ?? "",
                            OptionsJson = JsonSerializer.Serialize(q.Options ?? new List<string>()),
                            CorrectAnswer = letterAnswer,
                            Explanation = q.Explanation ?? "",
                            CreatedAt = DateTime.UtcNow
                        });
                        q.BankId = newBankId;
                    }
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

                await _subs.RecordOnlineTestGenerationAsync(user.UserId, req.Grade, req.Subject, useHybridAi, ct);
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
}
