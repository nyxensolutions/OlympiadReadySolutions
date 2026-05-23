namespace OlympiadReady.Api.Data.Entities;

public class Subscription
{
    public Guid SubscriptionId { get; set; }
    public Guid UserId { get; set; }
    public User? User { get; set; }
    public string PlanName { get; set; } = "Free";
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }

    public int Grade { get; set; }
    public string Subject { get; set; } = "";
    public int AiGenerationsUsed { get; set; }

    public int AmountInPaise { get; set; }
    public string? RazorpayOrderId { get; set; }
    public string? RazorpayPaymentId { get; set; }

    // Computed by SQL — do not set in code.
    public bool IsActive { get; private set; }
}
