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
            .Select(r => new ResultRow(
                r.UserId,
                r.Score,
                r.TotalQuestions,
                r.TimeTakenSeconds,
                r.CompletedAt,
                r.Paper != null ? r.Paper.Title  ?? "" : "",
                r.Paper != null ? r.Paper.Subject ?? "" : ""))
            .ToListAsync(ct);

        var allByUser = allResults.GroupBy(r => r.UserId).ToDictionary(g => g.Key, g => g.ToList());

        var top10 = recentRows
            .GroupBy(r => r.UserId)
            .Select(g =>
            {
                var userId       = g.Key;
                var displayName  = FirstName(g.First().FullName, g.First().Email);
                var bestScorePct = Math.Round(g.Max(r => r.ScorePct), 1);

                var userResults  = allByUser.TryGetValue(userId, out var ur) ? ur : new List<ResultRow>();
                var badges       = ComputeBadges(userResults);
                var earnedIds    = badges.Where(b => b.Earned).Select(b => b.Id).ToList();
                var title        = GetTitle(earnedIds.Count, badges.Count);

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

    // ── Typed helpers ────────────────────────────────────────────────────────

    private record ScoreRow(Guid UserId, string? FullName, string? Email, double ScorePct);

    private record ResultRow(
        Guid UserId, int Score, int TotalQuestions, int TimeTakenSeconds,
        DateTime CompletedAt, string PaperTitle, string Subject);

    private record BadgeResult(string Id, bool Earned);

    private static List<BadgeResult> ComputeBadges(List<ResultRow> rs)
    {
        int total    = rs.Count;
        double bestPct = total == 0 ? 0 : rs.Max(r => r.TotalQuestions > 0 ? (double)r.Score / r.TotalQuestions * 100.0 : 0.0);

        // Streak
        var dates = rs.Select(r => r.CompletedAt.Date).Distinct().OrderByDescending(d => d).ToList();
        int streak = 0;
        if (dates.Count > 0)
        {
            var today     = DateTime.UtcNow.Date;
            var yesterday = today.AddDays(-1);
            if (dates[0] == today || dates[0] == yesterday)
            {
                streak = 1;
                for (int i = 1; i < dates.Count; i++)
                {
                    if ((dates[i - 1] - dates[i]).TotalDays == 1) streak++;
                    else break;
                }
            }
        }

        int subjectCount     = rs.Select(r => r.Subject).Where(s => !string.IsNullOrEmpty(s)).Distinct().Count();
        int masteredSubjects = rs.Where(r => r.TotalQuestions > 0 && (double)r.Score / r.TotalQuestions * 100.0 >= 90)
                                 .Select(r => r.Subject).Distinct().Count();

        int maxConsec = 0, curConsec = 0;
        foreach (var r in rs.OrderBy(r => r.CompletedAt))
        {
            double pct = r.TotalQuestions > 0 ? (double)r.Score / r.TotalQuestions * 100.0 : 0;
            if (pct >= 90) { curConsec++; maxConsec = Math.Max(maxConsec, curConsec); }
            else curConsec = 0;
        }

        var byPaper = rs.GroupBy(r => r.PaperTitle ?? "").ToDictionary(g => g.Key, g => g.OrderBy(r => r.CompletedAt).ToList());
        bool hasComeback = byPaper.Values.Any(scores => {
            for (int i = 1; i < scores.Count; i++)
            {
                double prev = scores[i-1].TotalQuestions > 0 ? (double)scores[i-1].Score / scores[i-1].TotalQuestions * 100.0 : 0;
                double curr = scores[i].TotalQuestions   > 0 ? (double)scores[i].Score   / scores[i].TotalQuestions   * 100.0 : 0;
                if (curr - prev >= 20) return true;
            }
            return false;
        });

        return new List<BadgeResult>
        {
            new("first_test",        total >= 1),
            new("five_tests",        total >= 5),
            new("ten_tests",         total >= 10),
            new("twenty_five_tests", total >= 25),
            new("century",           total >= 100),
            new("sharpshooter",      bestPct >= 90),
            new("perfect",           rs.Any(r => r.Score == r.TotalQuestions && r.TotalQuestions > 0)),
            new("on_fire",           maxConsec >= 5),
            new("comeback",          hasComeback),
            new("streak_3",          streak >= 3),
            new("streak_7",          streak >= 7),
            new("streak_30",         streak >= 30),
            new("speed",             rs.Any(r => r.TotalQuestions >= 10 && r.TimeTakenSeconds < 300)),
            new("lightning",         rs.Any(r => r.TotalQuestions >= 20 && r.TimeTakenSeconds < 480)),
            new("explorer",          subjectCount >= 3),
            new("all_rounder",       masteredSubjects >= 3),
            new("mock_exam",         rs.Any(r => r.PaperTitle.StartsWith("Mock Exam"))),
            new("mock_3",            rs.Count(r => r.PaperTitle.StartsWith("Mock Exam")) >= 3),
        };
    }

    private static string GetTitle(int earned, int total) => (earned, total) switch
    {
        var (e, t) when e == t && t > 0 => "Olympiad Legend",
        (>= 14, _) => "Champion Scholar",
        (>= 10, _) => "Olympiad Contender",
        (>= 6,  _) => "Knowledge Seeker",
        (>= 3,  _) => "Rising Star",
        (>= 1,  _) => "Rookie Scholar",
        _           => "Newcomer",
    };

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
