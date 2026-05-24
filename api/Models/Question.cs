using System.Text.Json.Serialization;

namespace OlympiadReady.Api.Models;

public class Question
{
    [JsonPropertyName("q")]
    public string Q { get; set; } = "";

    [JsonPropertyName("imageUrl")]
    public string? ImageUrl { get; set; }

    [JsonPropertyName("options")]
    public List<string> Options { get; set; } = new();

    [JsonPropertyName("answer")]
    public string Answer { get; set; } = "";

    [JsonPropertyName("explanation")]
    public string Explanation { get; set; } = "";

    [JsonPropertyName("topic")]
    public string? Topic { get; set; }

    [JsonPropertyName("sectionName")]
    public string? SectionName { get; set; }

    [JsonPropertyName("marks")]
    public int? Marks { get; set; }
}
