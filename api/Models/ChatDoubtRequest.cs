namespace OlympiadReady.Api.Models;

public class ChatDoubtMessage
{
    public string Role { get; set; } = "";
    public string Content { get; set; } = "";
}

public class ChatDoubtRequest
{
    public string Subject { get; set; } = "";
    public int Grade { get; set; }
    
    // The specific question context
    public string QuestionText { get; set; } = "";
    public string Options { get; set; } = "";
    public string CorrectAnswer { get; set; } = "";
    public string Explanation { get; set; } = "";
    public string UserPick { get; set; } = "";
    
    // Chat payload
    public List<ChatDoubtMessage> History { get; set; } = new();
    public string UserMessage { get; set; } = "";
}
