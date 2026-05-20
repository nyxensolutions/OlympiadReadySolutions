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
    private readonly ClaudeService _claude;
    private readonly UserService _users;
    private readonly SubscriptionService _subs;
    private readonly QuestionBankService _bank;
    private readonly ILogger<PapersController> _log;

    public PapersController(
        AppDbContext db,
        ClaudeService claude,
        UserService users,
        SubscriptionService subs,
        QuestionBankService bank,
        ILogger<PapersController> log)
    {
        _db = db;
        _claude = claude;
        _users = users;
        _subs = subs;
        _bank = bank;
        _log = log;
    }

    [HttpPost("generate")]
    public async Task<IActionResult> Generate(
        [FromBody] GeneratePaperRequest req, CancellationToken ct)
    {
        try
        {
            var user = await _users.GetOrSyncAsync(User, ct);

            var quota = await _subs.CheckPaperQuotaAsync(user.UserId, ct);
            if (!quota.Allowed)
            {
                return StatusCode(StatusCodes.Status402PaymentRequired, new
                {
                    code = "QUOTA_EXCEEDED",
                    message = $"You've used {quota.Used} of {quota.Limit} papers this month on the {quota.Tier} plan.",
                    tier = quota.Tier,
                    used = quota.Used,
                    limit = quota.Limit,
                    upgrade = true
                });
            }

            // -------------------------------------------------------
            // Routing strategy
            // Free tier (or Test Accounts) → QuestionBank (pre-seeded, random sample)
            //              Falls back to Claude only when bank is thin (except for test accounts which will just fail).
            // Pro tier   → QuestionPaper cache first, then Claude live.
            // -------------------------------------------------------
            string jsonContent;
            List<Question> questions;

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
            else if (quota.Tier == "Free" || isTestAccount)
            {
                // Free tier / Test Account: serve from question bank (randomly sampled — fresh selection each time).
                // Falls back to Claude only when the bank has too few questions for this combo.
                var bankQuestions = await _bank.TryGetRandomAsync(
                    req.Subject, req.Grade, req.Difficulty, req.Count, req.Topic, ct);

                if (bankQuestions is not null)
                {
                    _log.LogInformation(
                        "Free tier — serving {Count} questions from bank for {Subject} G{Grade} {Difficulty}",
                        req.Count, req.Subject, req.Grade, req.Difficulty);
                    questions = bankQuestions;
                    jsonContent = JsonSerializer.Serialize(questions);
                }
                else
                {
                    _log.LogWarning(
                        "Free tier — bank insufficient for {Subject} G{Grade} {Difficulty}; returning error",
                        req.Subject, req.Grade, req.Difficulty);
                    return StatusCode(StatusCodes.Status503ServiceUnavailable, new
                    {
                        code = "BANK_INSUFFICIENT",
                        message = $"Not enough questions in the bank for {req.Subject} Class {req.Grade} ({req.Difficulty}) yet. Try a different subject, grade, or difficulty — or upgrade to Pro for AI-generated papers.",
                        upgrade = true
                    });
                }
            }
            else
            {
                // Pro tier: always call Claude for a genuinely fresh, unique paper every time.
                _log.LogInformation("Pro tier — generating fresh questions via Claude");
                questions = await _claude.GenerateQuestionsAsync(
                    req.Subject, req.Grade, req.Difficulty, req.Count, req.Topic, ct, req.OlympiadLevel);
                jsonContent = JsonSerializer.Serialize(questions);
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
