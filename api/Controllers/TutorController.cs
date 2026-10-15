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

    private const int FreeChatLimit = 10;
    private const int PaidMessagesPerConversation = 20;
    private const int MaxMessageChars = 2000;
    private const int MaxHistoryMessages = 40;

    // Paid = this class and subject unlocked (same rule as practice and mock exams), or an active school pilot.
    private async Task<bool> HasPaidAccessAsync(Guid userId, int grade, string subject, CancellationToken ct) =>
        await _subs.IsSchoolPilotActiveAsync(userId, ct)
        || await _subs.HasUnlockedSubjectAsync(userId, grade, subject, ct);

    [HttpGet("quota")]
    public async Task<IActionResult> GetQuota([FromQuery] string subject, [FromQuery] int? grade, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        if (user == null) return Unauthorized();

        bool hasPaidAccess;
        if (grade is >= 1 and <= 12)
        {
            hasPaidAccess = await HasPaidAccessAsync(user.UserId, grade.Value, subject, ct);
        }
        else
        {
            // App 1.0.0 doesn't send a class: report paid if the subject is unlocked in any class.
            hasPaidAccess = await _subs.IsSchoolPilotActiveAsync(user.UserId, ct);
            for (int g = 1; g <= 12 && !hasPaidAccess; g++)
                hasPaidAccess = await _subs.HasUnlockedSubjectAsync(user.UserId, g, subject, ct);
        }

        return Ok(new { hasPaidAccess, freeChatsUsed = user.FreeAiTutorChatsUsed, freeChatLimit = FreeChatLimit });
    }

    [HttpPost("chat")]
    public async Task<IActionResult> Chat([FromBody] ChatDoubtRequest req, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        if (user == null) return Unauthorized();

        if (string.IsNullOrWhiteSpace(req.UserMessage))
            return BadRequest(new { message = "Please type your doubt first." });
        if (req.UserMessage.Length > MaxMessageChars)
            return BadRequest(new { message = $"Please keep your message under {MaxMessageChars} characters." });

        // Bound what reaches the model regardless of what the client sends.
        req.History = (req.History ?? new())
            .TakeLast(MaxHistoryMessages)
            .Select(m => new ChatDoubtMessage
            {
                Role = m.Role,
                Content = m.Content.Length > 4000 ? m.Content[..4000] : m.Content,
            })
            .ToList();

        bool hasPaidAccess = await HasPaidAccessAsync(user.UserId, req.Grade, req.Subject, ct);

        if (!hasPaidAccess)
        {
            if (user.FreeAiTutorChatsUsed >= FreeChatLimit)
            {
                return StatusCode(403, new
                {
                    code = "QUOTA_EXCEEDED",
                    upgrade = true,
                    message = $"You have used all {FreeChatLimit} of your free AI Tutor chats. Unlock Class {req.Grade} {req.Subject} to keep chatting.",
                });
            }
        }
        else
        {
            int userMessageCount = req.History.Count(m => m.Role.Equals("user", StringComparison.OrdinalIgnoreCase));
            if (userMessageCount >= PaidMessagesPerConversation)
            {
                return StatusCode(403, new
                {
                    code = "CHAT_LIMIT",
                    message = string.IsNullOrWhiteSpace(req.QuestionText)
                        ? $"This chat has reached {PaidMessagesPerConversation} messages. Start a new chat to keep going."
                        : $"You have reached the maximum of {PaidMessagesPerConversation} chats for this question. Please move on to the next question!",
                });
            }
        }

        string reply;
        try
        {
            reply = await _tutor.AskTutorAsync(req, ct);
        }
        catch (Exception)
        {
            return StatusCode(500, new { message = "The AI Tutor is not responding right now. Please try again in a moment." });
        }

        // Count a free chat only once the student actually got a reply.
        if (!hasPaidAccess)
        {
            user.FreeAiTutorChatsUsed++;
            await _db.SaveChangesAsync(ct);
        }

        return Ok(new { reply, freeChatsUsed = user.FreeAiTutorChatsUsed, hasPaidAccess });
    }
}
