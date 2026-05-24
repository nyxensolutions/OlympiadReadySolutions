using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/leaderboard")]
public class LeaderboardController : ControllerBase
{
    private readonly AppDbContext _db;

    public LeaderboardController(AppDbContext db) => _db = db;

    /// <summary>
    /// Top 10 users by best single-test score % in the last 30 days.
    /// Returns display name (first name only), score%, and medal tier.
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> GetTopTen(CancellationToken ct)
    {
        var since = DateTime.UtcNow.AddDays(-30);

        var rows = await _db.Results
            .AsNoTracking()
            .Where(r => r.CompletedAt >= since && r.TotalQuestions > 0)
            .Select(r => new
            {
                r.UserId,
                r.User!.FullName,
                ScorePct = r.TotalMarks > 0 ? (double)r.EarnedMarks / r.TotalMarks * 100.0 : (double)r.Score / r.TotalQuestions * 100.0
            })
            .ToListAsync(ct);

        var top10 = rows
            .GroupBy(r => r.UserId)
            .Select(g => new
            {
                displayName = FirstName(g.First().FullName),
                bestScorePct = Math.Round(g.Max(r => r.ScorePct), 1),
            })
            .OrderByDescending(x => x.bestScorePct)
            .Take(10)
            .Select((x, i) => new
            {
                rank = i + 1,
                x.displayName,
                x.bestScorePct,
                medal = Medal(x.bestScorePct),
            })
            .ToList();

        return Ok(top10);
    }

    private static string FirstName(string? full)
    {
        if (string.IsNullOrWhiteSpace(full)) return "Student";
        var first = full.Trim().Split(' ')[0];
        return first.Length > 12 ? first[..12] : first;
    }

    private static string Medal(double pct) => pct switch
    {
        >= 90 => "Gold",
        >= 75 => "Silver",
        >= 60 => "Bronze",
        _      => "None",
    };
}
