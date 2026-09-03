using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Models;

namespace OlympiadReady.Api.Services;

public class SubscriptionService
{
    public const int GlobalFreeAttemptsLimit = 5;

    // Users who signed up before the July 2026 tier change keep the original 15-paper limit.
    public const int LegacyFreeAttemptsLimit = 15;
    private static readonly DateTime TierChangeDate = new DateTime(2026, 7, 8, 0, 0, 0, DateTimeKind.Utc);

    public static int GetEffectiveLimit(User user) =>
        user.CreatedAt < TierChangeDate ? LegacyFreeAttemptsLimit : GlobalFreeAttemptsLimit;

    // Retained for backward-compat/analytics on the per-subscription counter; no longer the AI gate.
    public const int PaidAiGenerationLimit = 50;

    // --- Account-wide AI credit budget (the product-facing quota) ---
    // Budget scales with how many subjects the account has unlocked, capped so the
    // "All Subjects" bundle can't multiply AI spend by the number of subjects.
    public const int CreditsPerSubject = 30;
    public const int MaxMonthlyAiCredits = 90;
    // An Olympiad generation runs on the pricier model, so it drains the budget faster.
    public const int OlympiadCreditCost = 2;
    public const int StandardCreditCost = 1;
    private const int AiPeriodDays = 30;

    // A credit charges per QuestionsPerCreditUnit questions, not per request. A flat per-request
    // cost let a 50-question paper cost the same as a 5-question one despite ~10x the tokens —
    // this closes that gap.
    public const int QuestionsPerCreditUnit = 10;

    // --- Hard dollar ceiling (the real cost guard) ---
    // Independent of the credit budget above. Credits are calibrated against assumptions about
    // token usage; this is enforced against real spend, computed from actual OpenAI token
    // counts via AiPricing. If the credit calibration is ever wrong — a prompt change, a model
    // repricing, a pathological response — this is what actually stops the bleeding.
    public const decimal DefaultMonthlyDollarCap = 2.00m;

    /// <summary>Credit cost for a generation of the given size at the given difficulty.</summary>
    public static int AiCreditCost(string? difficulty, int questionCount)
    {
        var units = Math.Max(1, (int)Math.Ceiling(questionCount / (double)QuestionsPerCreditUnit));
        var perUnit = string.Equals(difficulty, "Olympiad", StringComparison.OrdinalIgnoreCase)
            ? OlympiadCreditCost
            : StandardCreditCost;
        return units * perUnit;
    }

    private readonly AppDbContext _db;
    private readonly decimal _monthlyDollarCap;

    public SubscriptionService(AppDbContext db, IConfiguration config)
    {
        _db = db;
        _monthlyDollarCap = decimal.TryParse(config["OpenAi:MonthlyDollarCapPerUser"], out var cap)
            ? cap
            : DefaultMonthlyDollarCap;
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

        return user.FreeAttemptsUsed < GetEffectiveLimit(user);
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

    /// <summary>
    /// Result of an AI-spend reservation attempt. <see cref="Approved"/> reflects a single
    /// atomic database check — no separate confirmation step exists to race against it.
    /// </summary>
    public class AiReservation
    {
        public bool Approved { get; init; }
        public int CreditsReserved { get; init; }
        public decimal DollarsReserved { get; init; }
        public string? DenialReason { get; init; }

        public static readonly AiReservation Denied = new() { Approved = false, DenialReason = "not entitled" };
    }

    /// <summary>
    /// Atomically reserves both the credit cost and an estimated dollar cost for a generation,
    /// in one database round trip, before the (slow, expensive) API call is made.
    ///
    /// This exists because the previous design checked the credit budget, then made the API
    /// call — which measured 45 to 214 seconds in testing — and only deducted credits once it
    /// returned. Two concurrent requests could both read "budget available" before either
    /// wrote back, so the 90-credit cap was advisory under concurrency, not a hard limit. A
    /// single conditional UPDATE closes that: the row lock SQL Server takes for the write
    /// serialises concurrent callers, so the second of two simultaneous requests sees the
    /// first's reservation and is correctly refused if it would exceed the budget.
    ///
    /// The dollar reservation is the actual financial backstop — see
    /// <see cref="DefaultMonthlyDollarCap"/> — and is checked in the same statement, so neither
    /// guard can be satisfied while the other is bypassed.
    ///
    /// Call <see cref="ReconcileAiGenerationAsync"/> once the real outcome is known, whether
    /// the call succeeded, returned fewer questions than requested, or failed outright — an
    /// approved reservation that is never reconciled overstates the account's spend forever.
    /// </summary>
    public async Task<AiReservation> TryReserveAiGenerationAsync(
        Guid userId, int grade, string subject, string difficulty, int questionCount,
        string model, CancellationToken ct = default)
    {
        bool isPilot = await IsSchoolPilotActiveAsync(userId, ct);
        if (!isPilot && !await HasUnlockedSubjectAsync(userId, grade, subject, ct))
            return AiReservation.Denied;

        // Idempotent period rollover. Safe to race: at worst two concurrent requests both reset
        // an already-expired period, which is a harmless no-op the second time.
        await _db.Database.ExecuteSqlInterpolatedAsync($@"
            UPDATE Users SET AiCreditsUsed = 0, AiDollarsSpent = 0, AiPeriodStart = GETUTCDATE()
            WHERE UserId = {userId}
              AND (AiPeriodStart IS NULL OR DATEDIFF(day, AiPeriodStart, GETUTCDATE()) >= {AiPeriodDays})",
            ct);

        var creditCost = AiCreditCost(difficulty, questionCount);
        var dollarEstimate = AiPricing.EstimateCost(model, questionCount);
        var creditBudget = await GetMonthlyAiBudgetAsync(userId, ct);

        var rows = await _db.Database.ExecuteSqlInterpolatedAsync($@"
            UPDATE Users
            SET AiCreditsUsed = AiCreditsUsed + {creditCost},
                AiDollarsSpent = AiDollarsSpent + {dollarEstimate}
            WHERE UserId = {userId}
              AND AiCreditsUsed + {creditCost} <= {creditBudget}
              AND AiDollarsSpent + {dollarEstimate} <= {_monthlyDollarCap}",
            ct);

        if (rows == 0)
            return new AiReservation { Approved = false, DenialReason = "credit or dollar budget exceeded" };

        return new AiReservation { Approved = true, CreditsReserved = creditCost, DollarsReserved = dollarEstimate };
    }

    /// <summary>
    /// True up a reservation against the real outcome: refunds credits for any questions that
    /// were reserved but not delivered, and corrects the dollar ledger from the estimate to the
    /// actual cost computed from real token usage. Safe to call with
    /// <paramref name="actualQuestionsReturned"/> = 0 and <paramref name="actualDollarCost"/> =
    /// 0 for a failed call — that fully refunds the reservation.
    /// </summary>
    public async Task ReconcileAiGenerationAsync(
        Guid userId, string difficulty, int reservedQuestionCount, int actualQuestionsReturned,
        decimal reservedDollars, decimal actualDollarCost, CancellationToken ct = default)
    {
        var reservedCredits = AiCreditCost(difficulty, reservedQuestionCount);
        var actualCredits = actualQuestionsReturned > 0 ? AiCreditCost(difficulty, actualQuestionsReturned) : 0;
        var creditRefund = Math.Max(0, reservedCredits - actualCredits);
        var dollarDelta = actualDollarCost - reservedDollars; // may be negative (refund) or positive (true-up)

        await _db.Database.ExecuteSqlInterpolatedAsync($@"
            UPDATE Users
            SET AiCreditsUsed  = CASE WHEN AiCreditsUsed  - {creditRefund} < 0 THEN 0 ELSE AiCreditsUsed  - {creditRefund} END,
                AiDollarsSpent = CASE WHEN AiDollarsSpent + {dollarDelta}  < 0 THEN 0 ELSE AiDollarsSpent + {dollarDelta}  END
            WHERE UserId = {userId}", ct);
    }

    /// <summary>
    /// Records that an online test was generated: the per-subject analytics counter when AI
    /// was used, or the free-attempt counter when it wasn't and the account isn't on a pilot.
    ///
    /// Credit and dollar accounting no longer happens here — that is
    /// <see cref="TryReserveAiGenerationAsync"/> and <see cref="ReconcileAiGenerationAsync"/>,
    /// called around the AI call itself rather than after the fact, so the spend is gated
    /// before the money is spent rather than merely logged afterwards.
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
                subscription.AiGenerationsUsed++;
        }
        else
        {
            var user = await _db.Users
                .Include(u => u.School)
                .FirstOrDefaultAsync(u => u.UserId == userId, ct);
            if (user != null)
            {
                bool pilotActive = user.School?.PilotEndsAt.HasValue == true && DateTime.UtcNow < user.School.PilotEndsAt!.Value;
                if (!pilotActive)
                    user.FreeAttemptsUsed++;
            }
        }

        await _db.SaveChangesAsync(ct);
    }

    /// <summary>
    /// Unlocks a specific subject for a user for a given number of days.
    /// </summary>
    public async Task UnlockSubjectAsync(Guid userId, int grade, string subject, int days, int amountInPaise, string? razorpayOrderId, string? razorpayPaymentId, string? razorpaySubscriptionId, bool isAutoRenewing, CancellationToken ct)
    {
        // Always create a new subscription row so every payment has its own history record.
        // If an active subscription exists, the new one starts from its EndDate (seamless renewal).
        var existing = await _db.Subscriptions
            .Where(s => s.UserId == userId && s.Grade == grade && s.Subject == subject && s.EndDate > DateTime.UtcNow)
            .OrderByDescending(s => s.EndDate)
            .FirstOrDefaultAsync(ct);

        var startDate = existing != null ? existing.EndDate : DateTime.UtcNow;
        var sub = new Subscription
        {
            UserId = userId,
            PlanName = "Modular",
            Grade = grade,
            Subject = subject,
            StartDate = startDate,
            EndDate = startDate.AddDays(days),
            AiGenerationsUsed = 0,
            AmountInPaise = amountInPaise,
            RazorpayOrderId = razorpayOrderId,
            RazorpayPaymentId = razorpayPaymentId,
            RazorpaySubscriptionId = razorpaySubscriptionId,
            IsAutoRenewing = isAutoRenewing
        };
        _db.Subscriptions.Add(sub);

        // Keep Users.SubscriptionTier in sync so dashboards and emails reflect paid status
        var user = await _db.Users.FindAsync(new object[] { userId }, ct);
        if (user != null && user.SubscriptionTier == "Free")
        {
            user.SubscriptionTier = "Modular";
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

        int effectiveLimit = user != null ? GetEffectiveLimit(user) : GlobalFreeAttemptsLimit;

        return new
        {
            tier,
            used = user?.FreeAttemptsUsed ?? 0,
            limit = effectiveLimit,
            allowed = onTrial || onSchoolPilot || (user?.FreeAttemptsUsed ?? 0) < effectiveLimit || activeSubs.Any(),
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
