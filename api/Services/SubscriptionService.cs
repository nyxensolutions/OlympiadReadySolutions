using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Models;

namespace OlympiadReady.Api.Services;

public class SubscriptionService
{
    public const int FreeMonthlyPaperLimit = 2;
    public const int ProMonthlyPaperLimit = 50;

    private readonly AppDbContext _db;

    public SubscriptionService(AppDbContext db)
    {
        _db = db;
    }

    public async Task<string> GetActiveTierAsync(Guid userId, CancellationToken ct = default)
    {
        var hasActivePro = await _db.Subscriptions
            .Where(s => s.UserId == userId
                     && s.PlanName == "Pro"
                     && s.EndDate > DateTime.UtcNow)
            .AnyAsync(ct);
        return hasActivePro ? "Pro" : "Free";
    }

    public async Task<QuotaStatus> CheckPaperQuotaAsync(Guid userId, CancellationToken ct = default)
    {
        var tier = await GetActiveTierAsync(userId, ct);
        var limit = tier == "Pro" ? ProMonthlyPaperLimit : FreeMonthlyPaperLimit;

        var now = DateTime.UtcNow;
        var startOfMonth = new DateTime(now.Year, now.Month, 1, 0, 0, 0, DateTimeKind.Utc);
        var used = await _db.Papers
            .Where(p => p.UserId == userId && p.CreatedAt >= startOfMonth)
            .CountAsync(ct);

        return new QuotaStatus(tier, used, limit, used < limit);
    }

    public async Task ActivateProAsync(Guid userId, int days, CancellationToken ct = default)
    {
        var sub = new Subscription
        {
            UserId = userId,
            PlanName = "Pro",
            StartDate = DateTime.UtcNow,
            EndDate = DateTime.UtcNow.AddDays(days)
        };
        _db.Subscriptions.Add(sub);

        var user = await _db.Users.FirstOrDefaultAsync(u => u.UserId == userId, ct);
        if (user is not null) user.SubscriptionTier = "Pro";

        await _db.SaveChangesAsync(ct);
    }
}
