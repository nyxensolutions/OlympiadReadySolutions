using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

/// <summary>
/// Generates and validates HMAC-signed share tokens for the parent dashboard.
/// Tokens encode: userId|expiry(unix-seconds), signed with HMAC-SHA256 using Share:Secret.
/// Format: base64url(userId|expiry) + "." + base64url(hmac)
/// </summary>
[ApiController]
[Route("api/share")]
public class ShareController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly UserService _users;
    private readonly SubscriptionService _subs;
    private readonly IConfiguration _config;

    public ShareController(
        AppDbContext db, UserService users,
        SubscriptionService subs, IConfiguration config)
    {
        _db = db;
        _users = users;
        _subs = subs;
        _config = config;
    }

    /// <summary>Generate a 30-day read-only share token for the calling user.</summary>
    [Authorize]
    [HttpGet("token")]
    public async Task<IActionResult> GetToken(CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        var token = CreateToken(user.UserId.ToString(), 30);
        return Ok(new { token });
    }

    /// <summary>Read-only dashboard summary — no auth required; validates share token.</summary>
    [HttpGet("{token}/summary")]
    public async Task<IActionResult> Summary(string token, CancellationToken ct)
    {
        if (!TryValidateToken(token, out var userId))
            return Unauthorized(new { error = "Link expired or invalid." });

        if (!Guid.TryParse(userId, out var guid))
            return BadRequest();

        var papers = await _db.Papers
            .AsNoTracking()
            .Where(p => p.UserId == guid)
            .OrderByDescending(p => p.CreatedAt)
            .Take(10)
            .Select(p => new
            {
                paperId = p.PaperId,
                title = p.Title,
                subject = p.Subject,
                grade = p.Grade,
                difficulty = p.DifficultyLevel,
                createdAt = p.CreatedAt
            })
            .ToListAsync(ct);

        var results = await _db.Results
            .AsNoTracking()
            .Where(r => r.UserId == guid)
            .OrderByDescending(r => r.CompletedAt)
            .Take(20)
            .Select(r => new
            {
                resultId = r.ResultId,
                paperId = r.PaperId,
                paperTitle = r.Paper!.Title,
                subject = r.Paper.Subject,
                score = r.Score,
                totalQuestions = r.TotalQuestions,
                timeTakenSeconds = r.TimeTakenSeconds,
                completedAt = r.CompletedAt
            })
            .ToListAsync(ct);

        var mastery = await _db.Mastery
            .AsNoTracking()
            .Where(m => m.UserId == guid)
            .OrderBy(m => m.Subject).ThenBy(m => m.Topic)
            .Select(m => new
            {
                subject = m.Subject,
                topic = m.Topic,
                masteryScore = m.MasteryScore,
                lastUpdated = m.LastUpdated
            })
            .ToListAsync(ct);

        var summary = await _subs.GetSubscriptionSummaryAsync(guid, ct);

        return Ok(new
        {
            subscription = summary,
            papers,
            results,
            mastery
        });
    }

    // ── Token helpers ────────────────────────────────────────────────────────

    private string CreateToken(string userId, int validDays)
    {
        var expiry = DateTimeOffset.UtcNow.AddDays(validDays).ToUnixTimeSeconds();
        var payload = $"{userId}|{expiry}";
        var payloadB64 = Base64UrlEncode(Encoding.UTF8.GetBytes(payload));
        var sig = ComputeHmac(payloadB64);
        return $"{payloadB64}.{sig}";
    }

    private bool TryValidateToken(string token, out string userId)
    {
        userId = "";
        var parts = token.Split('.');
        if (parts.Length != 2) return false;

        var expectedSig = ComputeHmac(parts[0]);
        if (!CryptographicEquals(expectedSig, parts[1])) return false;

        string payload;
        try { payload = Encoding.UTF8.GetString(Base64UrlDecode(parts[0])); }
        catch { return false; }

        var segments = payload.Split('|');
        if (segments.Length != 2) return false;

        if (!long.TryParse(segments[1], out var expiry)) return false;
        if (DateTimeOffset.UtcNow.ToUnixTimeSeconds() > expiry) return false;

        userId = segments[0];
        return true;
    }

    private string ComputeHmac(string data)
    {
        var secret = _config["Share:Secret"] ?? "olympiad-ready-share-secret-change-in-prod";
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(secret));
        var hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(data));
        return Base64UrlEncode(hash);
    }

    private static bool CryptographicEquals(string a, string b) =>
        a.Length == b.Length && HMACSHA256.HashData(
            Encoding.UTF8.GetBytes("constant"),
            Encoding.UTF8.GetBytes(a)
        ).SequenceEqual(HMACSHA256.HashData(
            Encoding.UTF8.GetBytes("constant"),
            Encoding.UTF8.GetBytes(b)
        ));

    private static string Base64UrlEncode(byte[] data) =>
        Convert.ToBase64String(data).TrimEnd('=').Replace('+', '-').Replace('/', '_');

    private static byte[] Base64UrlDecode(string s)
    {
        s = s.Replace('-', '+').Replace('_', '/');
        s = s.PadRight(s.Length + (4 - s.Length % 4) % 4, '=');
        return Convert.FromBase64String(s);
    }
}
