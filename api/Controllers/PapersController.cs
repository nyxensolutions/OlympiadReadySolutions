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
            // Free tier  → QuestionBank (pre-seeded, random sample)
            //              Falls back to Claude only when bank is thin.
            // Pro tier   → QuestionPaper cache first, then Claude live.
            // -------------------------------------------------------
            string jsonContent;
            List<Question> questions;
            bool fromBank = false;
            bool fromCache = false;

            if (quota.Tier == "Free")
            {
                var bankQuestions = await _bank.TryGetRandomAsync(
                    req.Subject, req.Grade, req.Difficulty, req.Count, ct);

                if (bankQuestions is not null)
                {
                    _log.LogInformation(
                        "Free tier — serving {Count} questions from QuestionBank for {Subject} G{Grade} {Difficulty}",
                        req.Count, req.Subject, req.Grade, req.Difficulty);
                    questions = bankQuestions;
                    jsonContent = JsonSerializer.Serialize(questions);
                    fromBank = true;
                }
                else
                {
                    // Bank not yet seeded for this combination — fall back to Claude
                    _log.LogInformation(
                        "Free tier — QuestionBank insufficient for {Subject} G{Grade} {Difficulty}; falling back to Claude",
                        req.Subject, req.Grade, req.Difficulty);
                    questions = await _claude.GenerateQuestionsAsync(
                        req.Subject, req.Grade, req.Difficulty, req.Count, ct);
                    jsonContent = JsonSerializer.Serialize(questions);
                }
            }
            else
            {
                // Pro: try the paper cache first (exact config hit reuses stored JSON),
                // otherwise call Claude for fresh live questions.
                var cacheKey = PaperCacheKey.Compute(req.Subject, req.Grade, req.Difficulty, req.Count);

                var cached = await _db.Papers.AsNoTracking()
                    .Where(p => p.ContentHash == cacheKey)
                    .OrderByDescending(p => p.CreatedAt)
                    .FirstOrDefaultAsync(ct);

                if (cached is not null)
                {
                    _log.LogInformation("Pro tier — question cache HIT for {CacheKey}", cacheKey);
                    jsonContent = cached.JsonContent;
                    questions = JsonSerializer.Deserialize<List<Question>>(jsonContent) ?? new();
                    fromCache = true;
                }
                else
                {
                    _log.LogInformation("Pro tier — question cache MISS; calling Claude");
                    questions = await _claude.GenerateQuestionsAsync(
                        req.Subject, req.Grade, req.Difficulty, req.Count, ct);
                    jsonContent = JsonSerializer.Serialize(questions);
                }
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
            _db.Papers.Add(paper);
            await _db.SaveChangesAsync(ct);

            return Ok(new
            {
                paperId = paper.PaperId,
                title = paper.Title,
                subject = paper.Subject,
                grade = paper.Grade,
                difficulty = paper.DifficultyLevel,
                questions,
                fromBank,
                cached = fromCache
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
