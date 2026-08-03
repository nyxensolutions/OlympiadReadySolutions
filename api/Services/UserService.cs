using System.Net.Http.Headers;
using System.Security.Claims;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;

namespace OlympiadReady.Api.Services;

public class UserService
{
    private readonly AppDbContext _db;
    private readonly IEmailService _email;
    private readonly IHttpClientFactory _http;
    private readonly IConfiguration _config;
    private readonly ILogger<UserService> _log;

    public UserService(AppDbContext db, IEmailService email, IHttpClientFactory http, IConfiguration config, ILogger<UserService> log)
    {
        _db = db;
        _email = email;
        _http = http;
        _config = config;
        _log = log;
    }

    private async Task<string?> FetchNameFromClerkAsync(string externalId)
    {
        var secret = _config["Clerk:SecretKey"];
        if (string.IsNullOrEmpty(secret)) return null;
        try
        {
            var client = _http.CreateClient();
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", secret);
            client.DefaultRequestHeaders.UserAgent.ParseAdd("OlympiadReady-API/1.0");
            client.DefaultRequestHeaders.Accept.ParseAdd("application/json");
            var res = await client.GetAsync($"https://api.clerk.com/v1/users/{externalId}");
            if (!res.IsSuccessStatusCode) return null;
            using var doc = JsonDocument.Parse(await res.Content.ReadAsStringAsync());
            var first = doc.RootElement.TryGetProperty("first_name", out var f) ? f.GetString() ?? "" : "";
            var last  = doc.RootElement.TryGetProperty("last_name",  out var l) ? l.GetString() ?? "" : "";
            var full  = $"{first} {last}".Trim();
            return string.IsNullOrEmpty(full) ? null : full;
        }
        catch (Exception ex)
        {
            _log.LogWarning("[UserService] Clerk name fetch failed for {ExternalId}: {Err}", externalId, ex.Message);
            return null;
        }
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

        _log.LogInformation("[UserService] GetOrSyncAsync sub={Sub} emailInJwt={EmailInJwt}", sub, email ?? "(none)");

        var existing = await _db.Users.FirstOrDefaultAsync(u => u.ExternalId == sub, ct);
        if (existing is not null)
        {
            _log.LogInformation("[UserService] Existing user found id={Id} storedEmail={StoredEmail}", existing.UserId, existing.Email);
            bool changed = false;
            bool wasAnonymous = false;
            if (!string.IsNullOrEmpty(email) && existing.Email.EndsWith("@clerk.local"))
            {
                existing.Email = email;
                changed = true;
                wasAnonymous = true; // first time we have a real email — send welcome
            }
            if (string.IsNullOrEmpty(existing.FullName))
            {
                var resolvedName = !string.IsNullOrEmpty(name) ? name : await FetchNameFromClerkAsync(sub);
                if (!string.IsNullOrEmpty(resolvedName))
                {
                    existing.FullName = resolvedName;
                    changed = true;
                }
            }
            if (changed)
            {
                await _db.SaveChangesAsync(ct);
            }
            if (wasAnonymous)
            {
                _log.LogInformation("[UserService] Backfill path — sending welcome email to {Email}", email);
                _ = _email.SendWelcomeEmailAsync(email!, existing.FullName ?? "").ContinueWith(t =>
                    _log.LogError("[UserService] Welcome email failed (backfill): {Err}", t.Exception?.Message),
                    System.Threading.Tasks.TaskContinuationOptions.OnlyOnFaulted);
            }
            return existing;
        }

        email ??= $"{sub}@clerk.local";
        _log.LogInformation("[UserService] New user — creating with email={Email}", email);

        var user = new User
        {
            ExternalId = sub,
            Email = email,
            FullName = name
        };
        _db.Users.Add(user);

        try
        {
            await _db.SaveChangesAsync(ct);
        }
        catch (Microsoft.EntityFrameworkCore.DbUpdateException)
        {
            // Race condition: another concurrent request created this user a split-second earlier.
            // Clear the tracker and re-fetch the winner's row, then backfill + email if needed.
            _db.ChangeTracker.Clear();
            var concurrent = await _db.Users.FirstOrDefaultAsync(u => u.ExternalId == sub, ct);
            if (concurrent is null) throw;

            if (!string.IsNullOrEmpty(email) && !email.EndsWith("@clerk.local") && concurrent.Email.EndsWith("@clerk.local"))
            {
                concurrent.Email = email;
                if (!string.IsNullOrEmpty(name) && string.IsNullOrEmpty(concurrent.FullName))
                    concurrent.FullName = name;
                await _db.SaveChangesAsync(ct);
                _log.LogInformation("[UserService] Race-condition path — sending welcome email to {Email}", email);
                _ = _email.SendWelcomeEmailAsync(email, name ?? "").ContinueWith(t =>
                    _log.LogError("[UserService] Welcome email failed (race): {Err}", t.Exception?.Message),
                    System.Threading.Tasks.TaskContinuationOptions.OnlyOnFaulted);
            }
            else
            {
                _log.LogInformation("[UserService] Race-condition path — no email backfill needed, concurrent.Email={ConcurrentEmail}", concurrent.Email);
            }
            return concurrent;
        }

        // This request won the race — fire welcome email
        if (!email.EndsWith("@clerk.local"))
        {
            _log.LogInformation("[UserService] New user created — sending welcome email to {Email}", email);
            _ = _email.SendWelcomeEmailAsync(email, name ?? "").ContinueWith(t =>
                _log.LogError("[UserService] Welcome email failed (new user): {Err}", t.Exception?.Message),
                System.Threading.Tasks.TaskContinuationOptions.OnlyOnFaulted);
        }
        else
        {
            _log.LogInformation("[UserService] New user created with clerk.local placeholder — welcome email deferred until backfill");
        }

        return user;
    }
}
