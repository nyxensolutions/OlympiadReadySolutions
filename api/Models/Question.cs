using System.Text.Json.Serialization;

namespace OlympiadReady.Api.Models;

public class Question
{
    [JsonPropertyName("q")]
    public string Q { get; set; } = "";

    [JsonPropertyName("options")]
    public List<string> Options { get; set; } = new();

    [JsonPropertyName("answer")]
    public string Answer { get; set; } = "";

    [JsonPropertyName("explanation")]
    public string Explanation { get; set; } = "";

    [JsonPropertyName("topic")]
    public string? Topic { get; set; }
}
