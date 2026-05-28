using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/leaderboard")]
public class LeaderboardController : ControllerBase
{
    private readonly AppDbContext _db;

    public LeaderboardController(AppDbContext db) => _db = db;

    [HttpGet]
    public async Task<IActionResult> GetTopTen(CancellationToken ct)
    {
        var since = DateTime.UtcNow.AddDays(-30);

        // Score rows — last 30 days only
        var recentRows = await _db.Results
            .AsNoTracking()
            .Where(r => r.CompletedAt >= since && r.TotalQuestions > 0)
            .Select(r => new ScoreRow(
                r.UserId,
                r.User!.FullName,
                r.User!.Email,
                r.TotalMarks > 0
                    ? (double)r.EarnedMarks / r.TotalMarks * 100.0
                    : (double)r.Score / r.TotalQuestions * 100.0))
            .ToListAsync(ct);

        // All results — needed for badge computation (streaks need full history)
        var allResults = await _db.Results
            .AsNoTracking()
            .Where(r => r.TotalQuestions > 0)
            .Select(r => new BadgeCalculator.ResultRow(
                r.UserId,
                r.Score,
                r.TotalQuestions,
                r.TimeTakenSeconds,
                r.CompletedAt,
                r.Paper != null ? r.Paper.Title  ?? "" : "",
                r.Paper != null ? r.Paper.Subject ?? "" : ""))
            .ToListAsync(ct);

        var allByUser = allResults.GroupBy(r => r.UserId).ToDictionary(g => g.Key, g => g.ToList());

        var reportedCounts = await _db.ReportedQuestions
            .AsNoTracking()
            .Where(r => r.Status == "Accepted")
            .GroupBy(r => r.UserId)
            .Select(g => new { UserId = g.Key, Count = g.Count() })
            .ToDictionaryAsync(x => x.UserId, x => x.Count, ct);

        var top10 = recentRows
            .GroupBy(r => r.UserId)
            .Select(g =>
            {
                var userId       = g.Key;
                var displayName  = FirstName(g.First().FullName, g.First().Email);
                var bestScorePct = Math.Round(g.Max(r => r.ScorePct), 1);

                var userResults  = allByUser.TryGetValue(userId, out var ur) ? ur.Select(r => new BadgeCalculator.ResultRow(r.UserId, r.Score, r.TotalQuestions, r.TimeTakenSeconds, r.CompletedAt, r.PaperTitle, r.Subject)).ToList() : new List<BadgeCalculator.ResultRow>();
                var repCount     = reportedCounts.TryGetValue(userId, out var c) ? c : 0;
                var badges       = BadgeCalculator.ComputeBadges(userResults, repCount);
                var earnedIds    = badges.Where(b => b.Earned).Select(b => b.Id).ToList();
                var title        = BadgeCalculator.GetTitle(earnedIds.Count, badges.Count);

                return (displayName, bestScorePct, badgeCount: earnedIds.Count, title, earnedIds);
            })
            .OrderByDescending(x => x.bestScorePct)
            .Take(10)
            .Select((x, i) => new
            {
                rank           = i + 1,
                x.displayName,
                x.bestScorePct,
                medal          = Medal(x.bestScorePct),
                x.badgeCount,
                x.title,
                earnedBadgeIds = x.earnedIds,
            })
            .ToList();

        return Ok(top10);
    }

    [HttpGet("reporters")]
    public async Task<IActionResult> GetTopReporters(CancellationToken ct)
    {
        var topReporters = await _db.ReportedQuestions
            .AsNoTracking()
            .Where(r => r.Status == "Accepted")
            .GroupBy(r => r.UserId)
            .Select(g => new { UserId = g.Key, Count = g.Count() })
            .OrderByDescending(x => x.Count)
            .Take(10)
            .ToListAsync(ct);

        if (!topReporters.Any()) return Ok(new List<object>());

        var userIds = topReporters.Select(x => x.UserId).ToList();
        var users = await _db.Users
            .Where(u => userIds.Contains(u.UserId))
            .ToDictionaryAsync(u => u.UserId, ct);

        var result = topReporters.Select((x, i) => new
        {
            rank = i + 1,
            displayName = FirstName(users.TryGetValue(x.UserId, out var u) ? u.FullName : "", users.TryGetValue(x.UserId, out var u2) ? u2.Email : ""),
            reportedCount = x.Count,
            medal = x.Count >= 10 ? "Gold" : (x.Count >= 5 ? "Silver" : "Bronze")
        }).ToList();

        return Ok(result);
    }

    // ── Typed helpers ────────────────────────────────────────────────────────

    private record ScoreRow(Guid UserId, string? FullName, string? Email, double ScorePct);

    private static string FirstName(string? full, string? email)
    {
        if (!string.IsNullOrWhiteSpace(full))
        {
            var first = full.Trim().Split(' ')[0];
            return first.Length > 12 ? first[..12] : first;
        }
        if (!string.IsNullOrWhiteSpace(email))
        {
            var parts = email.Split('@');
            if (parts.Length > 0 && !string.IsNullOrWhiteSpace(parts[0]) && !parts[0].Contains("clerk.local"))
            {
                var prefix = parts[0];
                return prefix.Length > 12 ? prefix[..12] : prefix;
            }
        }
        return "Student";
    }

    private static string Medal(double pct) => pct switch
    {
        >= 90 => "Gold",
        >= 75 => "Silver",
        >= 60 => "Bronze",
        _     => "None",
    };
}
