using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/reports")]
public class ReportsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly UserService _users;

    public ReportsController(AppDbContext db, UserService users)
    {
        _db = db;
        _users = users;
    }

    public record SubmitReportRequest(string? QuestionBankId, string Category, string Description, string? QuestionText);

    [HttpPost]
    [Authorize]
    public async Task<IActionResult> SubmitReport([FromBody] SubmitReportRequest req, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        
        Guid qId = Guid.Empty;
        if (!string.IsNullOrWhiteSpace(req.QuestionBankId) && Guid.TryParse(req.QuestionBankId, out var parsed))
        {
            qId = parsed;
        }

        var finalDesc = req.Description;
        if (!string.IsNullOrWhiteSpace(req.QuestionText))
        {
            finalDesc += $"\n\n[Question Text]:\n{req.QuestionText}";
        }
        
        var report = new ReportedQuestion
        {
            UserId = user.UserId,
            QuestionBankId = qId,
            Category = req.Category,
            Description = finalDesc.Length > 1000 ? finalDesc[..1000] : finalDesc,
            Status = "Pending"
        };
        
        _db.ReportedQuestions.Add(report);
        await _db.SaveChangesAsync(ct);
        
        return Ok(new { success = true, reportId = report.ReportId });
    }

    [HttpGet("leaderboard")]
    public async Task<IActionResult> GetLeaderboard(CancellationToken ct)
    {
        // Get top 10 users by count of "Accepted" reports
        var topReporters = await _db.ReportedQuestions
            .Where(r => r.Status == "Accepted")
            .GroupBy(r => r.UserId)
            .Select(g => new { UserId = g.Key, Count = g.Count() })
            .OrderByDescending(x => x.Count)
            .Take(10)
            .ToListAsync(ct);

        var userIds = topReporters.Select(x => x.UserId).ToList();
        var users = await _db.Users
            .Where(u => userIds.Contains(u.UserId))
            .ToDictionaryAsync(u => u.UserId, ct);

        var leaderboard = topReporters.Select(r =>
        {
            var user = users.GetValueOrDefault(r.UserId);
            var displayName = user?.FullName;
            if (string.IsNullOrWhiteSpace(displayName))
            {
                var emailParts = user?.Email?.Split('@') ?? new[] { "user", "domain.com" };
                displayName = emailParts[0].Length > 2 
                    ? $"{emailParts[0][..2]}***@{emailParts[1]}" 
                    : $"***@{emailParts[1]}";
            }
            
            return new
            {
                userId = r.UserId,
                displayName = displayName,
                acceptedReports = r.Count
            };
        });

        return Ok(leaderboard);
    }
}
