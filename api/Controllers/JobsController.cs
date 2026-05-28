using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/jobs")]
public class JobsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly IEmailService _email;
    private readonly IConfiguration _config;
    private readonly ILogger<JobsController> _log;

    public JobsController(AppDbContext db, IEmailService email, IConfiguration config, ILogger<JobsController> log)
    {
        _db = db;
        _email = email;
        _config = config;
        _log = log;
    }

    [HttpPost("weekly-emails")]
    public async Task<IActionResult> SendWeeklyEmails([FromHeader(Name = "Cron-Key")] string? cronKey, CancellationToken ct)
    {
        var expectedKey = _config["Cron:SecretKey"];
        if (!string.IsNullOrEmpty(expectedKey) && cronKey != expectedKey)
        {
            return Unauthorized("Invalid Cron-Key");
        }

        var since = DateTime.UtcNow.AddDays(-7);

        // Get all users who have taken tests this week or have unresolved mistakes
        var activeUsers = await _db.Users
            .Where(u => !string.IsNullOrEmpty(u.Email))
            .ToListAsync(ct);

        int emailsSent = 0;

        foreach (var user in activeUsers)
        {
            var recentTestsCount = await _db.Results
                .CountAsync(r => r.UserId == user.UserId && r.CompletedAt >= since, ct);

            var pendingReviews = await _db.UserMistakes
                .CountAsync(m => m.UserId == user.UserId && !m.IsResolved, ct);

            // If they are completely inactive, we could still send them an email to engage,
            // but let's only send if they have recent activity or pending reviews.
            if (recentTestsCount > 0 || pendingReviews > 0)
            {
                var name = string.IsNullOrWhiteSpace(user.FullName) ? user.Email!.Split('@')[0] : user.FullName.Split(' ')[0];
                
                // Fetch actual badges earned this week
                var recentBadges = await _db.UserNotifications
                    .Where(n => n.UserId == user.UserId && n.CreatedAt >= since && n.Title.Contains("New Title"))
                    .Select(n => n.Message)
                    .ToListAsync(ct);
                    
                string badgesHtml = "";
                if (recentBadges.Any())
                {
                    badgesHtml = string.Join("", recentBadges.Select(b => $"<div style=\"padding: 8px 12px; background: #fff; border-radius: 6px; border-left: 4px solid #f59e0b; margin-bottom: 8px; font-size: 14px;\">🎖️ {b}</div>"));
                }

                // Mock or calculate rank
                string userRank = "4"; // TODO: Implement actual rank calculation
                string topBadgePlatform = "Olympiad Contender"; 

                await _email.SendWeeklyProgressAsync(user.Email!, name, recentTestsCount, recentBadges.Count, pendingReviews, userRank, topBadgePlatform, badgesHtml);
                emailsSent++;
            }
        }

        return Ok(new { success = true, emailsSent });
    }

    [HttpPost("weekly-emails/test")]
    public async Task<IActionResult> TestWeeklyEmail([FromQuery] string email, [FromHeader(Name = "Cron-Key")] string? cronKey)
    {
        var expectedKey = _config["Cron:SecretKey"];
        if (!string.IsNullOrEmpty(expectedKey) && cronKey != expectedKey)
        {
            return Unauthorized("Invalid Cron-Key");
        }

        if (string.IsNullOrWhiteSpace(email)) return BadRequest("Email is required");

        string badgesHtml = "<div style=\"padding: 8px 12px; background: #fff; border-radius: 6px; border-left: 4px solid #f59e0b; margin-bottom: 8px; font-size: 14px;\">🎖️ You unlocked <strong>Knowledge Seeker</strong>!</div>";
        await _email.SendWeeklyProgressAsync(email, "Test User", 5, 2, 1, "4", "Olympiad Contender", badgesHtml);
        return Ok(new { success = true, message = $"Test email sent to {email}" });
    }
}
