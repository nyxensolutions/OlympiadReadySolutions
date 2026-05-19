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
}
