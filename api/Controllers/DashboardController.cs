using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/dashboard")]
public class DashboardController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly UserService _users;
    private readonly SubscriptionService _subs;

    public DashboardController(AppDbContext db, UserService users, SubscriptionService subs)
    {
        _db = db;
        _users = users;
        _subs = subs;
    }

    /// <summary>Lightweight subscription + school status used by AppHeader and ConfigForm.</summary>
    [HttpGet("subscription")]
    public async Task<IActionResult> Subscription(CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        var summary = await _subs.GetSubscriptionSummaryAsync(user.UserId, ct);
        return Ok(summary);
    }

    [HttpGet("summary")]
    public async Task<IActionResult> Summary(CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);

        var papers = await _db.Papers
            .AsNoTracking()
            .Where(p => p.UserId == user.UserId)
            .OrderByDescending(p => p.CreatedAt)
            .Take(10)
            .Select(p => new
            {
                paperId = p.PaperId,
                title = p.Title,
                subject = p.Subject,
                grade = p.Grade,
                difficulty = p.DifficultyLevel,
                createdAt = p.CreatedAt
            })
            .ToListAsync(ct);

        var results = await _db.Results
            .AsNoTracking()
            .Where(r => r.UserId == user.UserId)
            .OrderByDescending(r => r.CompletedAt)
            .Take(20)
            .Select(r => new
            {
                resultId = r.ResultId,
                paperId = r.PaperId,
                paperTitle = r.Paper!.Title,
                subject = r.Paper.Subject,
                score = r.Score,
                totalQuestions = r.TotalQuestions,
                timeTakenSeconds = r.TimeTakenSeconds,
                completedAt = r.CompletedAt,
                totalMarks = r.TotalMarks,
                earnedMarks = r.EarnedMarks
            })
            .ToListAsync(ct);

        var mastery = await _db.Mastery
            .AsNoTracking()
            .Where(m => m.UserId == user.UserId)
            .OrderBy(m => m.Subject)
            .ThenBy(m => m.Topic)
            .Select(m => new
            {
                subject = m.Subject,
                topic = m.Topic,
                masteryScore = m.MasteryScore,
                lastUpdated = m.LastUpdated
            })
            .ToListAsync(ct);

        var summary = await _subs.GetSubscriptionSummaryAsync(user.UserId, ct);

        var unresolvedMistakesCount = await _db.UserMistakes
            .CountAsync(m => m.UserId == user.UserId && !m.IsResolved, ct);

        var firstUnresolvedMistake = await _db.UserMistakes
            .AsNoTracking()
            .Where(m => m.UserId == user.UserId && !m.IsResolved)
            .OrderByDescending(m => m.OccurredAt)
            .Select(m => new { m.Subject, m.Grade })
            .FirstOrDefaultAsync(ct);

        var reportedCount = await _db.ReportedQuestions
            .CountAsync(r => r.UserId == user.UserId && r.Status == "Accepted", ct);

        return Ok(new
        {
            subscription = summary,
            papers,
            results,
            mastery,
            mistakeCount = unresolvedMistakesCount,
            mistakeSubject = firstUnresolvedMistake?.Subject,
            mistakeGrade = firstUnresolvedMistake?.Grade,
            reportedCount = reportedCount
        });
    }
}
