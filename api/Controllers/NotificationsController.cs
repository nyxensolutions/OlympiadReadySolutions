using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/notifications")]
[Authorize]
public class NotificationsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly UserService _users;

    public NotificationsController(AppDbContext db, UserService users)
    {
        _db = db;
        _users = users;
    }

    [HttpGet]
    public async Task<IActionResult> GetNotifications(CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        
        var notifications = await _db.UserNotifications
            .Where(n => n.UserId == user.UserId)
            .OrderByDescending(n => n.CreatedAt)
            .Take(50) // Return last 50 notifications
            .Select(n => new
            {
                n.NotificationId,
                n.Title,
                n.Message,
                n.IsRead,
                n.CreatedAt
            })
            .ToListAsync(ct);

        return Ok(notifications);
    }

    [HttpPost("register-token")]
    public async Task<IActionResult> RegisterToken([FromBody] RegisterTokenRequest req, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(req.ExpoPushToken))
            return BadRequest(new { message = "Token is required." });

        var user = await _users.GetOrSyncAsync(User, ct);
        user.ExpoPushToken = req.ExpoPushToken.Trim();
        await _db.SaveChangesAsync(ct);
        return Ok(new { success = true });
    }

    [HttpPost("mark-read")]
    public async Task<IActionResult> MarkAsRead(CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        
        var unreadNotifications = await _db.UserNotifications
            .Where(n => n.UserId == user.UserId && !n.IsRead)
            .ToListAsync(ct);

        foreach (var n in unreadNotifications)
        {
            n.IsRead = true;
        }

        if (unreadNotifications.Any())
        {
            await _db.SaveChangesAsync(ct);
        }

        return Ok(new { success = true });
    }
}

public record RegisterTokenRequest(string ExpoPushToken);
