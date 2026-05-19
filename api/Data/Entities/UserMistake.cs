using System;

namespace OlympiadReady.Api.Data.Entities;

public class UserMistake
{
    public Guid MistakeId { get; set; }
    public Guid UserId { get; set; }
    public User? User { get; set; }
    public string Subject { get; set; } = "";
    public int Grade { get; set; }
    public string Topic { get; set; } = "";
    public string QuestionJson { get; set; } = "";
    public string CorrectAnswer { get; set; } = "";
    public string UserAnswer { get; set; } = "";
    public bool IsResolved { get; set; }
    public DateTime OccurredAt { get; set; }
}
