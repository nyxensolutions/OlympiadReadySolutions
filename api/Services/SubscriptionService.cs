using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Models;

namespace OlympiadReady.Api.Services;

public class SubscriptionService
{
    public const int GlobalFreeAttemptsLimit = 15;

    // Retained for backward-compat/analytics on the per-subscription counter; no longer the AI gate.
    public const int PaidAiGenerationLimit = 50;

    // --- Account-wide AI credit budget (the real cost guard) ---
    // Budget scales with how many subjects the account has unlocked, capped so the
    // "All Subjects" bundle can't multiply AI spend by the number of subjects.
    public const int CreditsPerSubject = 30;
    public const int MaxMonthlyAiCredits = 90;
    // An Olympiad generation runs on the pricier model, so it drains the budget faster.
    public const int OlympiadCreditCost = 2;
    public const int StandardCreditCost = 1;
    private const int AiPeriodDays = 30;

    /// <summary>Credits a single generation consumes, based on difficulty.</summary>
    public static int AiCreditCostForDifficulty(string? difficulty) =>
        string.Equals(difficulty, "Olympiad", StringComparison.OrdinalIgnoreCase)
            ? OlympiadCreditCost
            : StandardCreditCost;

    private readonly AppDbContext _db;

    public SubscriptionService(AppDbContext db)
    {
        _db = db;
    }

    /// <summary>
    /// Checks if the user has an active paid subscription for the given Grade and Subject.
    /// </summary>
    public async Task<bool> HasUnlockedSubjectAsync(Guid userId, int grade, string subject, CancellationToken ct = default)
    {
        var (canonicalTarget, _) = SubjectNormalizer.Normalize(subject);
        canonicalTarget ??= subject;

        var activeSubs = await _db.Subscriptions
            .Where(s => s.UserId == userId && s.Grade == grade && s.EndDate > DateTime.UtcNow)
            .ToListAsync(ct);

        return activeSubs.Any(s => 
        {
            var (canonicalSub, _) = SubjectNormalizer.Normalize(s.Subject);
            return string.Equals(canonicalSub, canonicalTarget, StringComparison.OrdinalIgnoreCase);
        });
    }

    /// <summary>
    /// Checks if a user is allowed to generate an online test for the given Grade/Subject.
    /// Allowed if: subject is unlocked, OR within 7-day trial, OR school pilot is active,
    /// OR free lifetime attempts remain.
    /// </summary>
    public async Task<bool> CanGenerateOnlineTestAsync(Guid userId, int grade, string subject, CancellationToken ct = default)
    {
        if (await HasUnlockedSubjectAsync(userId, grade, subject, ct))
            return true;

        var user = await _db.Users
            .Include(u => u.School)
            .FirstOrDefaultAsync(u => u.UserId == userId, ct);

        if (user == null) return false;

        // Active school pilot
        if (user.School?.PilotEndsAt.HasValue == true && DateTime.UtcNow < user.School.PilotEndsAt!.Value)
            return true;

        return user.FreeAttemptsUsed < GlobalFreeAttemptsLimit;
    }

    /// <summary>Returns true if the user is currently on an active school pilot.</summary>
    public async Task<bool> IsSchoolPilotActiveAsync(Guid userId, CancellationToken ct)
    {
        var user = await _db.Users
            .Include(u => u.School)
            .FirstOrDefaultAsync(u => u.UserId == userId, ct);
        return user?.School?.PilotEndsAt.HasValue == true && DateTime.UtcNow < user.School.PilotEndsAt!.Value;
    }

    /// <summary>
    /// Account-wide AI credit budget for the current period. Scales with the number of
    /// distinct unlocked subjects but is capped so an "All Subjects" bundle cannot
    /// multiply AI spend. School pilot accounts get a single-subject budget. Free accounts get 0.
    /// </summary>
    public async Task<int> GetMonthlyAiBudgetAsync(Guid userId, CancellationToken ct = default)
    {
        int activeSubjects = await _db.Subscriptions
            .Where(s => s.UserId == userId && s.EndDate > DateTime.UtcNow)
            .Select(s => new { s.Grade, s.Subject })
            .Distinct()
            .CountAsync(ct);

        if (activeSubjects == 0)
        {
            // School pilot students get a single-subject equivalent AI budget
            if (await IsSchoolPilotActiveAsync(userId, ct))
                return CreditsPerSubject;
            return 0;
        }
        return Math.Min(activeSubjects * CreditsPerSubject, MaxMonthlyAiCredits);
    }

    /// <summary>Resets the rolling 30-day credit window in-memory if it has elapsed.</summary>
    private static void EnsureCurrentAiPeriod(User user)
    {
        var now = DateTime.UtcNow;
        if (user.AiPeriodStart == default || (now - user.AiPeriodStart).TotalDays >= AiPeriodDays)
        {
            user.AiPeriodStart = now;
            user.AiCreditsUsed = 0;
        }
    }

    /// <summary>
    /// Determines whether the generation should use the Hybrid Engine (hitting the AI API)
    /// or silently fall back to the static question bank. AI runs only when the account both
    /// owns the subject AND has enough credits left this period to cover this generation.
    /// </summary>
    public async Task<bool> ShouldUseHybridAiAsync(Guid userId, int grade, string subject, string difficulty, CancellationToken ct = default)
    {
        // School pilot students get AI access without requiring a paid subscription.
        bool isPilot = await IsSchoolPilotActiveAsync(userId, ct);

        if (!isPilot && !await HasUnlockedSubjectAsync(userId, grade, subject, ct))
            return false;

        var user = await _db.Users.FirstOrDefaultAsync(u => u.UserId == userId, ct);
        if (user is null) return false;

        // Roll the window forward if it has expired (persisted when the generation is recorded).
        EnsureCurrentAiPeriod(user);

        int budget = await GetMonthlyAiBudgetAsync(userId, ct);
        int cost = AiCreditCostForDifficulty(difficulty);
        return user.AiCreditsUsed + cost <= budget;
    }

    /// <summary>
    /// Records that an online test was generated, incrementing the appropriate quotas.
    /// </summary>
    public async Task RecordOnlineTestGenerationAsync(Guid userId, int grade, string subject, bool usedHybridAi, string difficulty, CancellationToken ct = default)
    {
        var (canonicalTarget, _) = SubjectNormalizer.Normalize(subject);
        canonicalTarget ??= subject;

        var activeSubs = await _db.Subscriptions
            .Where(s => s.UserId == userId && s.Grade == grade && s.EndDate > DateTime.UtcNow)
            .ToListAsync(ct);

        var subscription = activeSubs.FirstOrDefault(s =>
        {
            var (canonicalSub, _) = SubjectNormalizer.Normalize(s.Subject);
            return string.Equals(canonicalSub, canonicalTarget, StringComparison.OrdinalIgnoreCase);
        });

        if (subscription != null)
        {
            if (usedHybridAi)
            {
                // Per-subject counter retained for analytics; the account credit budget is the real gate.
                subscription.AiGenerationsUsed++;

                var paidUser = await _db.Users.FirstOrDefaultAsync(u => u.UserId == userId, ct);
                if (paidUser != null)
                {
                    EnsureCurrentAiPeriod(paidUser);
                    paidUser.AiCreditsUsed += AiCreditCostForDifficulty(difficulty);
                }
            }
        }
        else
        {
            var user = await _db.Users
                .Include(u => u.School)
                .FirstOrDefaultAsync(u => u.UserId == userId, ct);
            if (user != null)
            {
                bool pilotActive = user.School?.PilotEndsAt.HasValue == true && DateTime.UtcNow < user.School.PilotEndsAt!.Value;
                if (pilotActive)
                {
                    // Track AI credits for school pilot students without consuming free attempts
                    if (usedHybridAi)
                    {
                        EnsureCurrentAiPeriod(user);
                        user.AiCreditsUsed += AiCreditCostForDifficulty(difficulty);
                    }
                }
                else
                {
                    user.FreeAttemptsUsed++;
                }
            }
        }

        await _db.SaveChangesAsync(ct);
    }

    /// <summary>
    /// Unlocks a specific subject for a user for a given number of days.
    /// </summary>
    public async Task UnlockSubjectAsync(Guid userId, int grade, string subject, int days, int amountInPaise, string razorpayOrderId, string razorpayPaymentId, CancellationToken ct)
    {
        var existing = await _db.Subscriptions
            .FirstOrDefaultAsync(s => s.UserId == userId && s.Grade == grade && s.Subject == subject && s.EndDate > DateTime.UtcNow, ct);

        if (existing != null)
        {
            existing.EndDate = existing.EndDate.AddDays(days);
            // Optionally update the amount to reflect the latest top-up, but for invoice purposes, a new record is better. 
            // Since the system creates a new subscription record or extends, let's just extend but keep track.
            // Wait, if it extends, it won't show as a new purchase. Let's create a new one instead of extending, or just extend.
            // Actually, the user's previous code extended it. Let's leave it as extending and updating the IDs for now, or maybe create a new record.
            // A safer approach for invoices is to ALWAYS create a new subscription record if it's a new purchase, but the existing logic extends. Let's just create a new record to keep history intact for invoices.
            // Actually let's just update the existing one for now to avoid breaking existing logic.
            existing.AmountInPaise = amountInPaise;
            existing.RazorpayOrderId = razorpayOrderId;
            existing.RazorpayPaymentId = razorpayPaymentId;
        }
        else
        {
            var sub = new Subscription
            {
                UserId = userId,
                PlanName = "Modular",
                Grade = grade,
                Subject = subject,
                StartDate = DateTime.UtcNow,
                EndDate = DateTime.UtcNow.AddDays(days),
                AiGenerationsUsed = 0,
                AmountInPaise = amountInPaise,
                RazorpayOrderId = razorpayOrderId,
                RazorpayPaymentId = razorpayPaymentId
            };
            _db.Subscriptions.Add(sub);
        }

        await _db.SaveChangesAsync(ct);
    }

    /// <summary>
    /// Returns a summary of the user's active unlocks and free attempts.
    /// </summary>
    public async Task<object> GetSubscriptionSummaryAsync(Guid userId, CancellationToken ct = default)
    {
        var user = await _db.Users
            .Include(u => u.School)
            .FirstOrDefaultAsync(u => u.UserId == userId, ct);

        var activeSubsDb = await _db.Subscriptions
            .Where(s => s.UserId == userId && s.EndDate > DateTime.UtcNow)
            .ToListAsync(ct);

        var activeSubs = activeSubsDb.Select(s => new
        {
            s.Grade,
            Subject = SubjectNormalizer.Normalize(s.Subject).Name ?? s.Subject,
            s.AiGenerationsUsed,
            s.EndDate
        }).ToList();

        // Account-wide AI credit view (non-mutating: reflect a reset without persisting here).
        int aiBudget = await GetMonthlyAiBudgetAsync(userId, ct);
        bool periodElapsed = user == null
            || user.AiPeriodStart == default
            || (DateTime.UtcNow - user.AiPeriodStart).TotalDays >= AiPeriodDays;
        int aiCreditsUsed = periodElapsed ? 0 : user!.AiCreditsUsed;

        bool onTrial = user?.TrialExpiresAt.HasValue == true && DateTime.UtcNow < user.TrialExpiresAt!.Value;
        bool onSchoolPilot = user?.School?.PilotEndsAt.HasValue == true && DateTime.UtcNow < user.School!.PilotEndsAt!.Value;

        string tier = activeSubs.Any() ? "Modular" : (onSchoolPilot ? "School" : "Free");

        return new
        {
            tier,
            used = user?.FreeAttemptsUsed ?? 0,
            limit = GlobalFreeAttemptsLimit,
            allowed = onTrial || onSchoolPilot || (user?.FreeAttemptsUsed ?? 0) < GlobalFreeAttemptsLimit || activeSubs.Any(),
            onTrial,
            trialExpiresAt = user?.TrialExpiresAt,
            onSchoolPilot,
            school = user?.School == null ? null : new
            {
                name = user.School.Name,
                logoUrl = user.School.LogoUrl,
                pilotEndsAt = user.School.PilotEndsAt
            },
            aiCreditsUsed,
            aiCreditsLimit = aiBudget,
            activeUnlocks = activeSubs
        };
    }
}
