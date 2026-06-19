using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TutorController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly AiTutorService _tutor;
    private readonly UserService _users;
    private readonly SubscriptionService _subs;

    public TutorController(AppDbContext db, AiTutorService tutor, UserService users, SubscriptionService subs)
    {
        _db = db;
        _tutor = tutor;
        _users = users;
        _subs = subs;
    }

    [HttpGet("quota")]
    public async Task<IActionResult> GetQuota([FromQuery] string subject, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        if (user == null) return Unauthorized();

        await _db.Entry(user).Collection(u => u.Subscriptions).LoadAsync(ct);

        bool onSchoolPilot = await _subs.IsSchoolPilotActiveAsync(user.UserId, ct);
        bool hasPaidAccess = onSchoolPilot || user.Subscriptions.Any(s =>
            s.IsActive &&
            (s.Subject.Equals(subject, StringComparison.OrdinalIgnoreCase) ||
             s.Subject.Equals("All Subjects", StringComparison.OrdinalIgnoreCase))
        );

        return Ok(new { hasPaidAccess, freeChatsUsed = user.FreeAiTutorChatsUsed });
    }

    [HttpPost("chat")]
    public async Task<IActionResult> Chat([FromBody] ChatDoubtRequest req, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        if (user == null) return Unauthorized();

        // Ensure subscriptions are loaded since GetOrSyncAsync might not Include them
        await _db.Entry(user).Collection(u => u.Subscriptions).LoadAsync(ct);

        // 1. Check if user has paid access or is on an active school pilot
        bool onSchoolPilot = await _subs.IsSchoolPilotActiveAsync(user.UserId, ct);
        bool hasPaidAccess = onSchoolPilot || user.Subscriptions.Any(s =>
            s.IsActive &&
            (s.Subject.Equals(req.Subject, StringComparison.OrdinalIgnoreCase) ||
             s.Subject.Equals("All Subjects", StringComparison.OrdinalIgnoreCase))
        );

        // 2. If not paid for this subject, check free quota
        if (!hasPaidAccess)
        {
            if (user.FreeAiTutorChatsUsed >= 10)
            {
                return StatusCode(403, new { message = "You have used all 10 of your free AI Tutor chats! Subscribe to any subject to continue chatting." });
            }

            // Increment quota
            user.FreeAiTutorChatsUsed++;
            await _db.SaveChangesAsync(ct);
        }
        else
        {
            // Paid users are limited to 20 user messages per question
            int userMessageCount = req.History.Count(m => m.Role.Equals("user", StringComparison.OrdinalIgnoreCase));
            if (userMessageCount >= 20)
            {
                return StatusCode(403, new { message = "You have reached the maximum of 20 chats for this specific question. Please move on to the next question!" });
            }
        }

        // 3. Call AI Service
        try
        {
            var reply = await _tutor.AskTutorAsync(req, ct);
            return Ok(new { reply, freeChatsUsed = user.FreeAiTutorChatsUsed, hasPaidAccess });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Error communicating with AI Tutor.", details = ex.Message });
        }
    }
}
