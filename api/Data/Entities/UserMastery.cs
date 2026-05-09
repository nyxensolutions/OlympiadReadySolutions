namespace OlympiadReady.Api.Data.Entities;

public class UserMastery
{
    public Guid UserId { get; set; }
    public User? User { get; set; }
    public string Subject { get; set; } = "";
    public string Topic { get; set; } = "";
    public decimal MasteryScore { get; set; }
    public DateTime LastUpdated { get; set; }
}
