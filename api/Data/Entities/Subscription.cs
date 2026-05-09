namespace OlympiadReady.Api.Data.Entities;

public class Subscription
{
    public Guid SubscriptionId { get; set; }
    public Guid UserId { get; set; }
    public User? User { get; set; }
    public string PlanName { get; set; } = "Free";
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }

    // Computed by SQL — do not set in code.
    public bool IsActive { get; private set; }
}
