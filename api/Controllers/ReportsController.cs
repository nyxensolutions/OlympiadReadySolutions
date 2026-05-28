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

    public record SubmitReportRequest(Guid QuestionBankId, string Category, string Description);

    [HttpPost]
    [Authorize]
    public async Task<IActionResult> SubmitReport([FromBody] SubmitReportRequest req, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        
        var report = new ReportedQuestion
        {
            UserId = user.UserId,
            QuestionBankId = req.QuestionBankId,
            Category = req.Category,
            Description = req.Description,
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
