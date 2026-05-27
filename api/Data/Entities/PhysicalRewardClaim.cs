namespace OlympiadReady.Api.Data.Entities;

public class PhysicalRewardClaim
{
    public Guid ClaimId { get; set; }
    public Guid UserId { get; set; }
    public User? User { get; set; }
    public string RewardType { get; set; } = ""; // "olympiad_legend", "subject_mastery", etc.
    public string Status { get; set; } = "Pending"; // Pending, Confirmed, Shipped, Delivered
    public DateTime RequestedAt { get; set; }
    public DateTime? ShippedAt { get; set; }
    public string? AdminNotes { get; set; }
    public string? StudentName { get; set; }
    public string? TrackingNumber { get; set; }
}
