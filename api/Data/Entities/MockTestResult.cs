namespace OlympiadReady.Api.Data.Entities;

public class MockTestResult
{
    public Guid ResultId { get; set; }
    public Guid UserId { get; set; }
    public User? User { get; set; }
    public Guid PaperId { get; set; }
    public QuestionPaper? Paper { get; set; }
    public int Score { get; set; } // correct count
    public int TotalQuestions { get; set; }
    public int TimeTakenSeconds { get; set; }
    public DateTime CompletedAt { get; set; }
    public int TotalMarks { get; set; }
    public int EarnedMarks { get; set; }
}
