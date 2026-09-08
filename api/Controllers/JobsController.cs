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
    private readonly IServiceScopeFactory _scopeFactory;

    public JobsController(AppDbContext db, IEmailService email, IConfiguration config, ILogger<JobsController> log, IServiceScopeFactory scopeFactory)
    {
        _db = db;
        _email = email;
        _config = config;
        _log = log;
        _scopeFactory = scopeFactory;
    }

    [HttpPost("weekly-emails")]
    public IActionResult SendWeeklyEmails([FromHeader(Name = "Cron-Key")] string? cronKey)
    {
        var expectedKey = _config["Cron:SecretKey"];
        if (string.IsNullOrEmpty(expectedKey) || cronKey != expectedKey)
            return Unauthorized("Invalid Cron-Key");

        // Fire and forget — cron-job.org has a 30 s timeout; work is done in background.
        _ = Task.Run(async () =>
        {
            using var scope = _scopeFactory.CreateScope();
            var db    = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            var email = scope.ServiceProvider.GetRequiredService<IEmailService>();
            var log   = scope.ServiceProvider.GetRequiredService<ILogger<JobsController>>();

            var since = DateTime.UtcNow.AddDays(-7);

            // Single query: pull activity counts for every user in one go.
            var users = await db.Users
                .Where(u => !string.IsNullOrEmpty(u.Email))
                .Select(u => new
                {
                    u.UserId,
                    u.Email,
                    u.FullName,
                    RecentTests   = db.Results.Count(r => r.UserId == u.UserId && r.CompletedAt >= since),
                    PendingReviews = db.UserMistakes.Count(m => m.UserId == u.UserId && !m.IsResolved),
                })
                .ToListAsync();

            int sent = 0;
            foreach (var u in users.Where(u => u.RecentTests > 0 || u.PendingReviews > 0))
            {
                try
                {
                    var name = string.IsNullOrWhiteSpace(u.FullName)
                        ? u.Email!.Split('@')[0]
                        : u.FullName.Split(' ')[0];

                    // Badges earned this week
                    var recentBadges = await db.UserNotifications
                        .Where(n => n.UserId == u.UserId && n.CreatedAt >= since && n.Title.Contains("New Title"))
                        .Select(n => n.Message)
                        .ToListAsync();

                    var badgesHtml = recentBadges.Any()
                        ? string.Join("", recentBadges.Select(b =>
                            $"<div style=\"padding:8px 12px;background:#fff;border-radius:6px;border-left:4px solid #f59e0b;margin-bottom:8px;font-size:14px;\">🎖️ {b}</div>"))
                        : "";

                    await email.SendWeeklyProgressAsync(
                        u.Email!, name, u.RecentTests, recentBadges.Count,
                        u.PendingReviews, "Top 10%", "Olympiad Contender", badgesHtml);

                    sent++;
                }
                catch (Exception ex)
                {
                    log.LogError(ex, "Weekly email failed for {Email}", u.Email);
                }
            }

            log.LogInformation("Weekly emails sent: {Count}", sent);
        });

        return Accepted(new { queued = true, message = "Weekly emails dispatched in background." });
    }

    [HttpPost("reengagement-emails")]
    public async Task<IActionResult> SendReengagementEmails([FromHeader(Name = "Cron-Key")] string? cronKey, CancellationToken ct)
    {
        var expectedKey = _config["Cron:SecretKey"];
        if (string.IsNullOrEmpty(expectedKey) || cronKey != expectedKey)
            return Unauthorized("Invalid Cron-Key");

        var now = DateTime.UtcNow;
        var windowStart = now.AddHours(-48);
        var windowEnd = now.AddHours(-24);

        // Users who signed up 24-48h ago and only have the auto-generated welcome paper
        var targets = await _db.Users
            .Where(u => !string.IsNullOrEmpty(u.Email)
                     && u.FreeAttemptsUsed == 1
                     && u.CreatedAt >= windowStart
                     && u.CreatedAt < windowEnd)
            .ToListAsync(ct);

        int emailsSent = 0;
        foreach (var user in targets)
        {
            var firstName = string.IsNullOrWhiteSpace(user.FullName) ? user.Email!.Split('@')[0] : user.FullName;
            int papersLeft = SubscriptionService.GetEffectiveLimit(user) - user.FreeAttemptsUsed;
            await _email.SendReengagementEmailAsync(user.Email!, firstName, papersLeft);
            emailsSent++;
        }

        _log.LogInformation("Re-engagement job: sent {Count} emails", emailsSent);
        return Ok(new { success = true, emailsSent });
    }

    // Day 4: Upgrade nudge — free users who signed up 3-4 days ago and haven't subscribed
    [HttpPost("upgrade-nudge-emails")]
    public async Task<IActionResult> SendUpgradeNudgeEmails([FromHeader(Name = "Cron-Key")] string? cronKey, CancellationToken ct)
    {
        var expectedKey = _config["Cron:SecretKey"];
        if (string.IsNullOrEmpty(expectedKey) || cronKey != expectedKey)
            return Unauthorized("Invalid Cron-Key");

        var now = DateTime.UtcNow;
        var windowStart = now.AddDays(-4);
        var windowEnd   = now.AddDays(-3);

        // Free users with no active subscription, signed up 3-4 days ago
        var paidUserIds = await _db.Subscriptions
            .Where(s => s.EndDate > now)
            .Select(s => s.UserId)
            .Distinct()
            .ToListAsync(ct);

        var targets = await _db.Users
            .Where(u => !string.IsNullOrEmpty(u.Email)
                     && !u.Email.EndsWith("@clerk.local")
                     && u.CreatedAt >= windowStart
                     && u.CreatedAt < windowEnd
                     && !paidUserIds.Contains(u.UserId))
            .ToListAsync(ct);

        int sent = 0;
        foreach (var user in targets)
        {
            await _email.SendUpgradeNudgeEmailAsync(user.Email!, user.FullName ?? "");
            sent++;
        }
        _log.LogInformation("Upgrade-nudge job: sent {Count} emails", sent);
        return Ok(new { success = true, emailsSent = sent });
    }

    // Day 7: Offer deadline — free users who signed up 6-7 days ago and haven't subscribed
    [HttpPost("offer-deadline-emails")]
    public async Task<IActionResult> SendOfferDeadlineEmails([FromHeader(Name = "Cron-Key")] string? cronKey, CancellationToken ct)
    {
        var expectedKey = _config["Cron:SecretKey"];
        if (string.IsNullOrEmpty(expectedKey) || cronKey != expectedKey)
            return Unauthorized("Invalid Cron-Key");

        var now = DateTime.UtcNow;
        var windowStart = now.AddDays(-7);
        var windowEnd   = now.AddDays(-6);

        var paidUserIds = await _db.Subscriptions
            .Where(s => s.EndDate > now)
            .Select(s => s.UserId)
            .Distinct()
            .ToListAsync(ct);

        var targets = await _db.Users
            .Where(u => !string.IsNullOrEmpty(u.Email)
                     && !u.Email.EndsWith("@clerk.local")
                     && u.CreatedAt >= windowStart
                     && u.CreatedAt < windowEnd
                     && !paidUserIds.Contains(u.UserId))
            .ToListAsync(ct);

        int sent = 0;
        foreach (var user in targets)
        {
            await _email.SendOfferDeadlineEmailAsync(user.Email!, user.FullName ?? "");
            sent++;
        }
        _log.LogInformation("Offer-deadline job: sent {Count} emails", sent);
        return Ok(new { success = true, emailsSent = sent });
    }

    [HttpPost("upgrade-nudge-emails/test")]
    public async Task<IActionResult> TestUpgradeNudgeEmail([FromQuery] string email, [FromHeader(Name = "Cron-Key")] string? cronKey, CancellationToken ct)
    {
        var expectedKey = _config["Cron:SecretKey"];
        if (string.IsNullOrEmpty(expectedKey) || cronKey != expectedKey)
            return Unauthorized("Invalid Cron-Key");
        if (string.IsNullOrWhiteSpace(email)) return BadRequest("Email is required");

        await _email.SendUpgradeNudgeEmailAsync(email, "Akhil");
        return Ok(new { success = true, message = $"Day-4 upgrade nudge email sent to {email}" });
    }

    [HttpPost("offer-deadline-emails/test")]
    public async Task<IActionResult> TestOfferDeadlineEmail([FromQuery] string email, [FromHeader(Name = "Cron-Key")] string? cronKey, CancellationToken ct)
    {
        var expectedKey = _config["Cron:SecretKey"];
        if (string.IsNullOrEmpty(expectedKey) || cronKey != expectedKey)
            return Unauthorized("Invalid Cron-Key");
        if (string.IsNullOrWhiteSpace(email)) return BadRequest("Email is required");

        await _email.SendOfferDeadlineEmailAsync(email, "Akhil");
        return Ok(new { success = true, message = $"Day-7 offer deadline email sent to {email}" });
    }

    [HttpPost("weekly-emails/test")]
    public async Task<IActionResult> TestWeeklyEmail([FromQuery] string email, [FromHeader(Name = "Cron-Key")] string? cronKey)
    {
        var expectedKey = _config["Cron:SecretKey"];
        if (string.IsNullOrEmpty(expectedKey) || cronKey != expectedKey)
            return Unauthorized("Invalid Cron-Key");

        if (string.IsNullOrWhiteSpace(email)) return BadRequest("Email is required");

        // Probe Brevo directly so we surface real errors instead of always saying "success"
        var apiKey = _config["Brevo:ApiKey"] ?? _config["Brevo__ApiKey"] ?? "";
        var senderEmail = _config["Brevo:SenderEmail"] ?? _config["Brevo__SenderEmail"] ?? "hello@olympiadready.com";
        var senderName = _config["Brevo:SenderName"] ?? _config["Brevo__SenderName"] ?? "OlympiadReady";

        if (string.IsNullOrWhiteSpace(apiKey))
            return StatusCode(500, new { success = false, error = "Brevo API key is not configured (check Brevo__ApiKey in App Settings)" });

        using var http = new HttpClient();
        http.BaseAddress = new Uri("https://api.brevo.com/v3/");
        http.DefaultRequestHeaders.Add("api-key", apiKey);

        var payload = new
        {
            sender = new { name = senderName, email = senderEmail },
            to = new[] { new { email, name = "Test User" } },
            subject = "[OlympiadReady] Test email — Brevo diagnostic",
            htmlContent = "<p>This is a Brevo diagnostic test from the OlympiadReady API. If you received this, transactional email is working correctly.</p>"
        };

        var res = await http.PostAsJsonAsync("smtp/email", payload);
        var body = await res.Content.ReadAsStringAsync();

        if (!res.IsSuccessStatusCode)
            return StatusCode((int)res.StatusCode, new { success = false, brevoStatus = (int)res.StatusCode, error = body });

        return Ok(new { success = true, message = $"Brevo accepted the request — email queued for {email}", brevoResponse = body });
    }
}
