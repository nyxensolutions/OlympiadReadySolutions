using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/spell-bee")]
public class SpellBeeController : ControllerBase
{
    private const int FreeWordLimit = 5;

    private readonly AppDbContext _db;
    private readonly UserService _users;
    private readonly SubscriptionService _subs;
    private readonly ILogger<SpellBeeController> _log;

    public SpellBeeController(
        AppDbContext db, UserService users,
        SubscriptionService subs, ILogger<SpellBeeController> log)
    {
        _db = db;
        _users = users;
        _subs = subs;
        _log = log;
    }

    // ── GET /api/spell-bee/categories?grade=3 ────────────────────────────
    /// <summary>Returns the distinct categories available for a grade.</summary>
    [HttpGet("categories")]
    public async Task<IActionResult> GetCategories([FromQuery] int grade, CancellationToken ct)
    {
        if (grade < 1 || grade > 8) return BadRequest("Grade must be between 1 and 8.");

        var categories = await _db.SpellBeeWords
            .Where(w => w.Grade == grade)
            .Select(w => w.Category)
            .Distinct()
            .OrderBy(c => c)
            .ToListAsync(ct);

        return Ok(categories);
    }

    // ── GET /api/spell-bee/words?grade=3&difficulty=Easy&category=General&count=5 ──
    /// <summary>
    /// Returns randomly-sampled words for a practice round.
    /// Free users get up to 5 words per call; Pro users get up to 20.
    /// Requires sign-in so quota can be applied.
    /// </summary>
    [Authorize]
    [HttpGet("words")]
    public async Task<IActionResult> GetWords(
        [FromQuery] int grade,
        [FromQuery] string difficulty = "Easy",
        [FromQuery] string? category = null,
        [FromQuery] int count = 5,
        CancellationToken ct = default)
    {
        if (grade < 1 || grade > 8) return BadRequest("Grade must be between 1 and 8.");

        var user = await _users.GetOrSyncAsync(User, ct);
        var quota = await _subs.CheckPaperQuotaAsync(user.UserId, ct);

        var maxWords = quota.Tier == "Pro" ? 20 : FreeWordLimit;
        count = Math.Min(count, maxWords);

        var query = _db.SpellBeeWords
            .Where(w => w.Grade == grade && w.Difficulty == difficulty);

        if (!string.IsNullOrWhiteSpace(category))
            query = query.Where(w => w.Category == category);

        var available = await query.CountAsync(ct);

        if (available == 0)
            return StatusCode(503, new
            {
                code = "NO_WORDS",
                message = $"No words in the bank for Grade {grade} — {difficulty} ({category ?? "all categories"}). " +
                          "The word bank is being populated — check back soon."
            });

        var words = await query
            .OrderBy(_ => Guid.NewGuid())
            .Take(count)
            .Select(w => new
            {
                word         = w.Word,
                definition   = w.Definition,
                usageSentence = w.UsageSentence,
                pronunciation = w.Pronunciation,
                memoryTip    = w.MemoryTip,
                origin       = w.Origin,
                category     = w.Category,
                difficulty   = w.Difficulty,
                grade        = w.Grade,
            })
            .AsNoTracking()
            .ToListAsync(ct);

        _log.LogInformation(
            "SpellBee: {Count} words served for Grade {Grade} {Difficulty} user {UserId}",
            words.Count, grade, difficulty, user.UserId);

        return Ok(new
        {
            words,
            tier = quota.Tier,
            isLimited = quota.Tier == "Free",
            maxWords
        });
    }

    // ── GET /api/spell-bee/preview?grade=3 ───────────────────────────────
    /// <summary>Public preview: 3 sample words, no auth required, no quota.</summary>
    [AllowAnonymous]
    [HttpGet("preview")]
    public async Task<IActionResult> Preview([FromQuery] int grade = 3, CancellationToken ct = default)
    {
        var words = await _db.SpellBeeWords
            .Where(w => w.Grade == grade && w.Difficulty == "Easy")
            .OrderBy(_ => Guid.NewGuid())
            .Take(3)
            .Select(w => new
            {
                word         = w.Word,
                definition   = w.Definition,
                usageSentence = w.UsageSentence,
                pronunciation = w.Pronunciation,
                category     = w.Category,
            })
            .AsNoTracking()
            .ToListAsync(ct);

        return Ok(words);
    }

    // ── POST /api/spell-bee/admin/import ─────────────────────────────────
    /// <summary>
    /// Bulk-import words from JSON. Restricted to admin.
    /// Body: array of { word, grade, difficulty, category, definition, usageSentence, origin?, pronunciation?, memoryTip? }
    /// </summary>
    [Authorize]
    [HttpPost("admin/import")]
    public async Task<IActionResult> AdminImport(
        [FromBody] List<SpellBeeImportRow> rows,
        CancellationToken ct)
    {
        // Admin-only guard: use email allowlist or a custom claim in production
        var user = await _users.GetOrSyncAsync(User, ct);
        if (!user.Email.Contains("admin", StringComparison.OrdinalIgnoreCase) &&
            !user.Email.Equals("akhilmittal2008@gmail.com", StringComparison.OrdinalIgnoreCase))
        {
            return Forbid();
        }

        var existingWords = (await _db.SpellBeeWords
            .Select(w => w.Word)
            .ToListAsync(ct))
            .ToHashSet(StringComparer.OrdinalIgnoreCase);

        int inserted = 0, skipped = 0;
        var errors = new List<string>();

        foreach (var (row, i) in rows.Select((r, idx) => (r, idx + 1)))
        {
            if (string.IsNullOrWhiteSpace(row.Word)) { errors.Add($"Row {i}: Word is empty"); continue; }
            if (row.Grade < 1 || row.Grade > 8) { errors.Add($"Row {i}: Grade must be 1–8"); continue; }
            if (!new[] { "Easy", "Medium", "Hard" }.Contains(row.Difficulty, StringComparer.OrdinalIgnoreCase))
            { errors.Add($"Row {i}: Difficulty must be Easy, Medium, or Hard"); continue; }
            if (string.IsNullOrWhiteSpace(row.Definition)) { errors.Add($"Row {i}: Definition is empty"); continue; }

            if (existingWords.Contains(row.Word.Trim())) { skipped++; continue; }

            _db.SpellBeeWords.Add(new Data.Entities.SpellBeeWord
            {
                Word         = row.Word.Trim().ToLowerInvariant(),
                Grade        = row.Grade,
                Difficulty   = CapFirst(row.Difficulty),
                Category     = string.IsNullOrWhiteSpace(row.Category) ? "General" : row.Category.Trim(),
                Definition   = row.Definition.Trim(),
                UsageSentence = row.UsageSentence?.Trim() ?? "",
                Origin       = row.Origin?.Trim(),
                Pronunciation = row.Pronunciation?.Trim(),
                MemoryTip    = row.MemoryTip?.Trim(),
            });
            existingWords.Add(row.Word.Trim());
            inserted++;
        }

        await _db.SaveChangesAsync(ct);

        _log.LogInformation("SpellBee import: {Inserted} inserted, {Skipped} skipped, {Errors} errors",
            inserted, skipped, errors.Count);

        return Ok(new { inserted, skipped, errors });
    }

    private static string CapFirst(string s) =>
        string.IsNullOrEmpty(s) ? s : char.ToUpper(s[0]) + s[1..].ToLower();
}

public record SpellBeeImportRow(
    string Word,
    int Grade,
    string Difficulty,
    string? Category,
    string Definition,
    string? UsageSentence,
    string? Origin,
    string? Pronunciation,
    string? MemoryTip);
