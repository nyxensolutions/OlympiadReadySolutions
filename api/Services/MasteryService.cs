using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Models;

namespace OlympiadReady.Api.Services;

public class MasteryService
{
    private readonly AppDbContext _db;
    private readonly ILogger<MasteryService> _log;

    public MasteryService(AppDbContext db, ILogger<MasteryService> log)
    {
        _db = db;
        _log = log;
    }

    /// <summary>
    /// Group answers by topic, compute % correct, upsert UserMastery rows.
    /// Latest attempt overwrites the prior score — TODO: weighted moving average.
    /// </summary>
    public async Task UpdateFromAttemptAsync(
        Guid userId,
        string subject,
        IReadOnlyList<Question> questions,
        IReadOnlyList<string?> userAnswers,
        CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(subject)) return;
        if (questions.Count != userAnswers.Count)
        {
            _log.LogWarning("MasteryService: question/answer count mismatch ({Q} vs {A})",
                questions.Count, userAnswers.Count);
            return;
        }

        var grouped = questions
            .Select((q, i) => new { Question = q, Picked = userAnswers[i] })
            .Where(x => !string.IsNullOrWhiteSpace(x.Question.Topic))
            .GroupBy(x => x.Question.Topic!.Trim())
            .Where(g => g.Key.Length > 0);

        var now = DateTime.UtcNow;
        foreach (var group in grouped)
        {
            var topic = group.Key;
            var total = group.Count();
            var correct = group.Count(x => x.Picked == x.Question.Answer);
            var pct = (decimal)correct / total * 100m;

            var existing = await _db.Mastery.FirstOrDefaultAsync(
                m => m.UserId == userId && m.Subject == subject && m.Topic == topic, ct);

            if (existing is null)
            {
                _db.Mastery.Add(new UserMastery
                {
                    UserId = userId,
                    Subject = subject,
                    Topic = topic,
                    MasteryScore = pct,
                    LastUpdated = now
                });
            }
            else
            {
                existing.MasteryScore = pct;
                existing.LastUpdated = now;
            }
        }

        await _db.SaveChangesAsync(ct);
    }
}
