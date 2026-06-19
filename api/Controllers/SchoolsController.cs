using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/schools")]
public class SchoolsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly UserService _userService;
    private readonly IEmailService _email;

    public SchoolsController(AppDbContext db, UserService userService, IEmailService email)
    {
        _db = db;
        _userService = userService;
        _email = email;
    }

    /// <summary>
    /// Public: validate a school invite code and return display info (name, logo).
    /// Used by the onboarding modal before the user commits.
    /// </summary>
    [HttpGet("validate/{code}")]
    public async Task<IActionResult> ValidateCode(string code, CancellationToken ct)
    {
        var school = await _db.Schools.FirstOrDefaultAsync(s => s.InviteCode == code.ToUpper(), ct);
        if (school == null)
            return NotFound(new { message = "Invalid invite code." });

        int currentSeats = await _db.Users.CountAsync(u => u.SchoolId == school.SchoolId, ct);
        if (currentSeats >= school.SeatLimit)
            return BadRequest(new { message = "This school's pilot seats are full." });

        return Ok(new
        {
            school.SchoolId,
            school.Name,
            school.City,
            school.LogoUrl,
            seatsLeft = school.SeatLimit - currentSeats,
            pilotActive = school.PilotEndsAt.HasValue && school.PilotEndsAt > DateTime.UtcNow
        });
    }

    /// <summary>
    /// Authenticated: link the calling user to a school via invite code.
    /// </summary>
    [HttpPost("join")]
    [Authorize]
    public async Task<IActionResult> JoinSchool([FromBody] JoinSchoolRequest req, CancellationToken ct)
    {
        var user = await _userService.GetOrSyncAsync(User, ct);

        if (user.SchoolId.HasValue)
            return BadRequest(new { message = "You are already linked to a school." });

        var school = await _db.Schools.FirstOrDefaultAsync(s => s.InviteCode == req.InviteCode.ToUpper(), ct);
        if (school == null)
            return NotFound(new { message = "Invalid invite code." });

        int currentSeats = await _db.Users.CountAsync(u => u.SchoolId == school.SchoolId, ct);
        if (currentSeats >= school.SeatLimit)
            return BadRequest(new { message = "This school's pilot seats are full." });

        user.SchoolId = school.SchoolId;
        user.SchoolJoinedAt = DateTime.UtcNow;
        // Exhaust the personal free tier so that when the pilot ends the student
        // must upgrade rather than silently falling back to 15 free papers.
        // Paid subscriptions are checked before free-tier quota, so purchasing
        // later is unaffected.
        user.FreeAttemptsUsed = SubscriptionService.GlobalFreeAttemptsLimit;

        // In-app notification for the student
        _db.UserNotifications.Add(new UserNotification
        {
            UserId = user.UserId,
            Title = $"Welcome to {school.Name}! 🏫",
            Message = $"You've been enrolled in the {school.Name} pilot programme and now have full access to OlympiadReady for the duration of the pilot. Enjoy unlimited practice, AI-generated papers, and PDF downloads!",
            IsRead = false,
            CreatedAt = DateTime.UtcNow
        });

        await _db.SaveChangesAsync(ct);

        // Fire-and-forget coordinator email — don't let email failure block the join
        if (!string.IsNullOrWhiteSpace(school.ContactEmail))
        {
            _ = _email.SendSchoolJoinNotificationAsync(
                school.ContactEmail,
                school.Name,
                user.FullName ?? user.Email,
                user.Email
            );
        }

        return Ok(new
        {
            school.Name,
            school.City,
            school.LogoUrl,
            pilotActive = school.PilotEndsAt.HasValue && school.PilotEndsAt > DateTime.UtcNow
        });
    }
}

public record JoinSchoolRequest(string InviteCode);
