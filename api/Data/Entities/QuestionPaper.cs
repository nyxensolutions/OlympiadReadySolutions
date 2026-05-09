namespace OlympiadReady.Api.Data.Entities;

public class QuestionPaper
{
    public Guid PaperId { get; set; }
    public Guid UserId { get; set; }
    public User? User { get; set; }
    public string? Title { get; set; }
    public int Grade { get; set; }
    public string? Subject { get; set; }
    public string? DifficultyLevel { get; set; }
    public DateTime CreatedAt { get; set; }
    public string JsonContent { get; set; } = "[]";

    // SHA256 hex of (subject|grade|difficulty|count). Same key → reuse questions instead of re-prompting.
    public string? ContentHash { get; set; }
}
