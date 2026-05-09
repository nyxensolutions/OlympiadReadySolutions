using System.Security.Claims;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;

namespace OlympiadReady.Api.Services;

public class UserService
{
    private readonly AppDbContext _db;

    public UserService(AppDbContext db)
    {
        _db = db;
    }

    /// <summary>
    /// Look up the User row matching the authenticated Clerk identity, creating one on first sight.
    /// Email/name often aren't in the default Clerk JWT — fields stay blank until a webhook
    /// or a Clerk Backend API call backfills them.
    /// </summary>
    public async Task<User> GetOrSyncAsync(ClaimsPrincipal principal, CancellationToken ct = default)
    {
        var sub = principal.FindFirst("sub")?.Value
            ?? principal.FindFirst(ClaimTypes.NameIdentifier)?.Value
            ?? throw new UnauthorizedAccessException("Authenticated principal has no 'sub' claim.");

        var existing = await _db.Users.FirstOrDefaultAsync(u => u.ExternalId == sub, ct);
        if (existing is not null) return existing;

        var email = principal.FindFirst("email")?.Value
            ?? principal.FindFirst(ClaimTypes.Email)?.Value
            ?? $"{sub}@clerk.local";
        var name = principal.FindFirst("name")?.Value
            ?? principal.FindFirst(ClaimTypes.Name)?.Value;

        var user = new User
        {
            ExternalId = sub,
            Email = email,
            FullName = name
        };
        _db.Users.Add(user);
        await _db.SaveChangesAsync(ct);
        return user;
    }
}
