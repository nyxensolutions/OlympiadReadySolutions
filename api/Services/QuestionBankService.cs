using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Models;

namespace OlympiadReady.Api.Services;

public class QuestionBankService
{
    private readonly AppDbContext _db;
    private readonly ILogger<QuestionBankService> _log;

    public QuestionBankService(AppDbContext db, ILogger<QuestionBankService> log)
    {
        _db = db;
        _log = log;
    }

    // ---------------------------------------------------------------
    // Query
    // ---------------------------------------------------------------

    /// <summary>
    /// Returns <paramref name="count"/> randomly-sampled questions from the bank
    /// matching subject + grade + difficulty.  Returns null if the bank has
    /// fewer than <paramref name="count"/> questions for that combination.
    /// </summary>
    public async Task<List<Question>?> TryGetRandomAsync(
        string subject, int grade, string? difficulty, int count,
        string? topic = null, CancellationToken ct = default,
        IEnumerable<Guid>? excludeIds = null)
    {
        var (canonicalSubject, _) = SubjectNormalizer.Normalize(subject);
        canonicalSubject ??= subject;

        var excludeSet = excludeIds != null ? new HashSet<Guid>(excludeIds) : null;

        var baseQuery = _db.QuestionBank
            .Where(q => (q.Subject == canonicalSubject || (canonicalSubject == "Science" && (q.Subject == "Science-Physics" || q.Subject == "Science-Chemistry" || q.Subject == "Science-Biology"))) && q.Grade == grade);

        if (difficulty is not null)
            baseQuery = baseQuery.Where(q => q.Difficulty == difficulty);

        if (topic is not null)
            baseQuery = baseQuery.Where(q => q.Topic == topic);

        if (excludeSet != null && excludeSet.Count > 0)
            baseQuery = baseQuery.Where(q => !excludeSet.Contains(q.QuestionBankId));

        var available = await baseQuery.CountAsync(ct);

        if (available < count)
        {
            if (topic != null)
            {
                _log.LogInformation(
                    "QuestionBank: only {Available} questions for {Subject} G{Grade} {Difficulty} topic={Topic}; falling back to any topic",
                    available, subject, grade, difficulty ?? "any", topic);
                return await TryGetRandomAsync(subject, grade, difficulty, count, null, ct, excludeIds);
            }

            _log.LogInformation(
                "QuestionBank: only {Available} questions for {Subject} G{Grade} {Difficulty}; need {Count}",
                available, subject, grade, difficulty ?? "any", count);
            return null;
        }
                
        // Avoid ORDER BY NEWID() in SQL Server as it causes timeouts on large tables.
        // Also avoid loading all IDs into memory for large tables.
        // We'll fetch topics and counts, then pick random offsets.
        var topicsWithCounts = await baseQuery
            .GroupBy(q => q.Topic)
            .Select(g => new { Topic = g.Key, Count = g.Count() })
            .ToListAsync(ct);

        var random = new Random();
        var selectedIds = new HashSet<Guid>();
        
        // Loop through topics round-robin until we have enough questions
        int attempts = 0;
        int maxAttempts = count * 5; // prevent infinite loops

        while (selectedIds.Count < count && topicsWithCounts.Any(t => t.Count > 0) && attempts < maxAttempts)
        {
            topicsWithCounts = topicsWithCounts.OrderBy(_ => random.Next()).ToList();
            foreach (var t in topicsWithCounts.Where(x => x.Count > 0).ToList())
            {
                if (selectedIds.Count >= count) break;

                var skip = random.Next(t.Count);
                var qId = await baseQuery
                    .Where(q => q.Topic == t.Topic)
                    .OrderBy(q => q.QuestionBankId)
                    .Skip(skip)
                    .Select(q => q.QuestionBankId)
                    .FirstOrDefaultAsync(ct);

                if (qId != Guid.Empty && !selectedIds.Contains(qId))
                {
                    selectedIds.Add(qId);
                }
                attempts++;
            }
        }

        var items = await _db.QuestionBank
            .Where(q => selectedIds.Contains(q.QuestionBankId))
            .AsNoTracking()
            .ToListAsync(ct);

        // Optional: shuffle again in memory so the returned order is random,
        // since SQL Server's IN clause doesn't guarantee order.
        items = items.OrderBy(_ => random.Next()).ToList();

        return items.Select(ToQuestion).ToList();
    }

    /// <summary>
    /// Returns the count of seeded questions grouped by (Subject, Grade, Difficulty).
    /// Useful for the admin stats endpoint.
    /// </summary>
    public async Task<List<BankStats>> GetStatsAsync(CancellationToken ct = default)
    {
        // Project to an anonymous type first (EF Core can translate that),
        // then materialise and map to the record in memory.
        var raw = await _db.QuestionBank
            .GroupBy(q => new { q.Subject, q.Grade, q.Difficulty })
            .Select(g => new
            {
                g.Key.Subject,
                g.Key.Grade,
                g.Key.Difficulty,
                Count = g.Count()
            })
            .OrderBy(s => s.Subject).ThenBy(s => s.Grade).ThenBy(s => s.Difficulty)
            .ToListAsync(ct);

        return raw.Select(r => new BankStats(r.Subject, r.Grade, r.Difficulty, r.Count)).ToList();
    }

    // ---------------------------------------------------------------
    // Import
    // ---------------------------------------------------------------

    public record ImportRow(
        string QuestionText,
        string? ImageUrl,
        List<string> Options,
        string CorrectAnswer,   // "A" | "B" | "C" | "D"
        string Topic,
        string? SubTopic,
        string Difficulty,
        string Explanation,
        bool IsReviewed = false,
        DateTime? ReviewedAt = null,
        string? ReviewedBy = null);

    public record ImportResult(int Inserted, int Skipped, List<string> Errors);
    public record BankStats(string Subject, int Grade, string Difficulty, int Count);

    /// <summary>
    /// Bulk-imports questions into the bank for a specific subject + grade.
    /// Rows with validation errors are skipped (error messages collected).
    /// Duplicate detection: exact QuestionText match for same Subject/Grade is skipped.
    /// </summary>
    public async Task<ImportResult> ImportAsync(
        string subject, int grade,
        IEnumerable<ImportRow> rows,
        CancellationToken ct = default)
    {
        var (canonicalSubject, _) = SubjectNormalizer.Normalize(subject);
        canonicalSubject ??= subject;

        // Load existing question texts to deduplicate
        var existingList = await _db.QuestionBank
            .Where(q => q.Subject == canonicalSubject && q.Grade == grade)
            .Select(q => q.QuestionText)
            .ToListAsync(ct);
        var existing = new HashSet<string>(existingList, StringComparer.Ordinal);

        var toInsert = new List<QuestionBankItem>();
        var errors = new List<string>();
        int skipped = 0;

        foreach (var (row, idx) in rows.Select((r, i) => (r, i + 1)))
        {
            var err = Validate(row, idx);
            if (err is not null) { errors.Add(err); continue; }

            if (existing.Contains(row.QuestionText.Trim()))
            {
                _log.LogDebug("Row {Idx}: duplicate QuestionText — skipped", idx);
                skipped++;
                continue;
            }

            toInsert.Add(new QuestionBankItem
            {
                Subject = canonicalSubject,
                Grade = grade,
                Difficulty = Normalise(row.Difficulty),
                Topic = row.Topic.Trim(),
                SubTopic = row.SubTopic?.Trim(),
                QuestionText = row.QuestionText.Trim(),
                ImageUrl = row.ImageUrl?.Trim(),
                // StripOptionPrefix handles "A) ...", "A. ...", "(A) ..." formats that
                // Claude adds despite instructions — the UI renderer adds its own labels.
                OptionsJson = JsonSerializer.Serialize(
                    row.Options.Select((o, i) => StripOptionPrefix(o, i)).ToList()),
                CorrectAnswer = row.CorrectAnswer.Trim().ToUpper(),
                Explanation = row.Explanation.Trim(),
                IsReviewed = row.IsReviewed,
                ReviewedAt = row.ReviewedAt,
                ReviewedBy = row.ReviewedBy
            });

            existing.Add(row.QuestionText.Trim()); // prevent dupes within the same batch
        }

        if (toInsert.Count > 0)
        {
            await _db.QuestionBank.AddRangeAsync(toInsert, ct);
            await _db.SaveChangesAsync(ct);
        }

        return new ImportResult(toInsert.Count, skipped, errors);
    }

    // ---------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------

    private static Question ToQuestion(QuestionBankItem item)
    {
        var options = JsonSerializer.Deserialize<List<string>>(item.OptionsJson) ?? new();

        // Convert letter answer (A/B/C/D) → full option string
        int idx = item.CorrectAnswer.ToUpper() switch
        {
            "A" => 0, "B" => 1, "C" => 2, "D" => 3, _ => 0
        };
        var answer = idx < options.Count ? options[idx] : options.FirstOrDefault() ?? "";

        return new Question
        {
            BankId = item.QuestionBankId,
            Q = item.QuestionText,
            ImageUrl = item.ImageUrl,
            Options = options,
            Answer = answer,
            Explanation = item.Explanation,
            Topic = item.Topic
        };
    }

    // Matches "A) ", "A. ", "A: ", "(A) ", "A- " at the very start of an option string.
    // The expected letter for position i is A/B/C/D — we use it to avoid accidentally
    // stripping a question that genuinely starts with a letter + punctuation (rare but possible).
    private static readonly Regex _prefixRx =
        new(@"^\(?([A-Da-d])[)\.\:\-]\s*", RegexOptions.Compiled);

    /// <summary>
    /// Strips the option-label prefix from an option string if present.
    /// The <paramref name="position"/> (0-based) is used to validate that the letter
    /// matches the expected A/B/C/D position, so we never strip actual question content.
    /// </summary>
    private static string StripOptionPrefix(string option, int position)
    {
        var trimmed = option.Trim();
        var m = _prefixRx.Match(trimmed);
        if (!m.Success) return trimmed;

        // Only strip when the letter matches the expected position (A=0, B=1, C=2, D=3).
        char expected = (char)('A' + position);
        if (char.ToUpper(m.Groups[1].Value[0]) != expected) return trimmed;

        return trimmed[m.Length..].Trim();
    }

    private static string? Validate(ImportRow row, int idx)
    {
        if (string.IsNullOrWhiteSpace(row.QuestionText))
            return $"Row {idx}: QuestionText is empty";
        if (row.Options is null || row.Options.Count != 4)
            return $"Row {idx}: Options must have exactly 4 items";
        if (string.IsNullOrWhiteSpace(row.CorrectAnswer) ||
            !new[] { "A", "B", "C", "D" }.Contains(row.CorrectAnswer.Trim().ToUpper()))
            return $"Row {idx}: CorrectAnswer must be A, B, C, or D";
        if (string.IsNullOrWhiteSpace(row.Difficulty) ||
            !new[] { "foundation", "advanced", "olympiad" }
                .Contains(row.Difficulty.Trim().ToLower()))
            return $"Row {idx}: Difficulty must be Foundation, Advanced, or Olympiad";
        if (string.IsNullOrWhiteSpace(row.Topic))
            return $"Row {idx}: Topic is empty";
        return null;
    }

    private static string Normalise(string s) =>
        s.Trim() switch
        {
            { } v when v.Equals("foundation", StringComparison.OrdinalIgnoreCase) => "Foundation",
            { } v when v.Equals("advanced", StringComparison.OrdinalIgnoreCase) => "Advanced",
            { } v when v.Equals("olympiad", StringComparison.OrdinalIgnoreCase) => "Olympiad",
            { } v => v
        };
}
