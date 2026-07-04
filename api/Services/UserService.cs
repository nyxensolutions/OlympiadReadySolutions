using System.Security.Claims;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;

namespace OlympiadReady.Api.Services;

public class UserService
{
    private readonly AppDbContext _db;
    private readonly IEmailService _email;

    public UserService(AppDbContext db, IEmailService email)
    {
        _db = db;
        _email = email;
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

        var email = principal.FindFirst("email")?.Value
            ?? principal.FindFirst(ClaimTypes.Email)?.Value;
            
        var name = principal.FindFirst("name")?.Value
            ?? principal.FindFirst(ClaimTypes.Name)?.Value;

        var existing = await _db.Users.FirstOrDefaultAsync(u => u.ExternalId == sub, ct);
        if (existing is not null) 
        {
            bool changed = false;
            bool wasAnonymous = false;
            if (!string.IsNullOrEmpty(email) && existing.Email.EndsWith("@clerk.local"))
            {
                existing.Email = email;
                changed = true;
                wasAnonymous = true; // first time we have a real email — send welcome
            }
            if (!string.IsNullOrEmpty(name) && string.IsNullOrEmpty(existing.FullName))
            {
                existing.FullName = name;
                changed = true;
            }
            if (changed)
            {
                await _db.SaveChangesAsync(ct);
            }
            if (wasAnonymous)
                _ = _email.SendWelcomeEmailAsync(email!, existing.FullName ?? "").ContinueWith(t =>
                    Console.WriteLine($"[UserService] Welcome email failed: {t.Exception?.Message}"),
                    System.Threading.Tasks.TaskContinuationOptions.OnlyOnFaulted);
            return existing;
        }

        email ??= $"{sub}@clerk.local";

        var user = new User
        {
            ExternalId = sub,
            Email = email,
            FullName = name
        };
        _db.Users.Add(user);
        await _db.SaveChangesAsync(ct);

        // Fire-and-forget welcome email — don't block the request if it fails
        if (!email.EndsWith("@clerk.local"))
            _ = _email.SendWelcomeEmailAsync(email, name ?? "").ContinueWith(t =>
                Console.WriteLine($"[UserService] Welcome email failed: {t.Exception?.Message}"),
                System.Threading.Tasks.TaskContinuationOptions.OnlyOnFaulted);

        return user;
    }
}
