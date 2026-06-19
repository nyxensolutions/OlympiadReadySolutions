namespace OlympiadReady.Api.Data.Entities;

public class School
{
    public Guid SchoolId { get; set; }
    public string Name { get; set; } = "";
    public string City { get; set; } = "";
    public string? LogoUrl { get; set; }
    public string InviteCode { get; set; } = "";
    public DateTime? PilotEndsAt { get; set; }
    public int SeatLimit { get; set; } = 20;
    public string ContactEmail { get; set; } = "";
    public DateTime CreatedAt { get; set; }

    public ICollection<User> Students { get; set; } = new List<User>();
}
