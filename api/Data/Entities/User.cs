namespace OlympiadReady.Api.Data.Entities;

public class User
{
    public Guid UserId { get; set; }
    public string? ExternalId { get; set; }
    public string Email { get; set; } = "";
    public string? FullName { get; set; }
    public DateTime CreatedAt { get; set; }
    public string SubscriptionTier { get; set; } = "Free";

    public List<QuestionPaper> Papers { get; set; } = new();
    public List<MockTestResult> Results { get; set; } = new();
    public List<Subscription> Subscriptions { get; set; } = new();
    public List<UserMastery> Mastery { get; set; } = new();
    public List<PdfPurchase> PdfPurchases { get; set; } = new();
    public List<UserMistake> Mistakes { get; set; } = new();

    public int FreeAttemptsUsed { get; set; }
    
    /// <summary>
    /// Tracks the lifetime number of AI Tutor chat messages a free user has sent. Max 10.
    /// </summary>
    public int FreeAiTutorChatsUsed { get; set; }

    /// <summary>
    /// Account-wide AI generation credits consumed in the current billing period.
    /// A standard (Foundation/Advanced) generation costs 1 credit; an Olympiad
    /// generation costs 2 (it runs on the more expensive model). Reset every 30 days.
    /// </summary>
    public int AiCreditsUsed { get; set; }

    /// <summary>Start of the current 30-day AI-credit period. Rolls forward on first use after expiry.</summary>
    public DateTime AiPeriodStart { get; set; }

    /// <summary>When the 7-day unlimited free trial expires. Set on first user creation.</summary>
    public DateTime? TrialExpiresAt { get; set; }

    /// <summary>School the student belongs to (set via invite code during onboarding).</summary>
    public Guid? SchoolId { get; set; }
    public School? School { get; set; }
    public DateTime? SchoolJoinedAt { get; set; }
}
