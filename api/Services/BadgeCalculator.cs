using OlympiadReady.Api.Data;

namespace OlympiadReady.Api.Services;

public static class BadgeCalculator
{
    public record ResultRow(Guid UserId, int Score, int TotalQuestions, int TimeTakenSeconds, DateTime CompletedAt, string PaperTitle, string Subject);
    public record BadgeResult(string Id, bool Earned);

    public static List<BadgeResult> ComputeBadges(List<ResultRow> rs, int reportedCount)
    {
        int total    = rs.Count;
        double bestPct = total == 0 ? 0 : rs.Max(r => r.TotalQuestions > 0 ? (double)r.Score / r.TotalQuestions * 100.0 : 0.0);

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
            new("mock_10",           rs.Count(r => r.PaperTitle.StartsWith("Mock Exam")) >= 10),
            new("mock_25",           rs.Count(r => r.PaperTitle.StartsWith("Mock Exam")) >= 25),
            new("flawless_mock",     rs.Any(r => r.PaperTitle.StartsWith("Mock Exam") && r.Score == r.TotalQuestions && r.TotalQuestions > 0)),
            new("weekend_warrior",   rs.Any(r => r.CompletedAt.DayOfWeek == DayOfWeek.Saturday || r.CompletedAt.DayOfWeek == DayOfWeek.Sunday)),
            new("bug_hunter",        reportedCount >= 10),
            new("bug_exterminator",  reportedCount >= 50),
        };
    }

    public static string GetTitle(int earned, int total) => (earned, total) switch
    {
        var (e, t) when e == t && t > 0 => "Olympiad Legend",
        (>= 14, _) => "Champion Scholar",
        (>= 10, _) => "Olympiad Contender",
        (>= 6,  _) => "Knowledge Seeker",
        (>= 3,  _) => "Rising Star",
        (>= 1,  _) => "Rookie Scholar",
        _           => "Newcomer",
    };
}
