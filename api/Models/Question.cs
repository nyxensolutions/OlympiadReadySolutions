using System.Text.Json.Serialization;

namespace OlympiadReady.Api.Models;

public class Question
{
    /// <summary>Tracks the source QuestionBankItem ID for deduplication and reporting.</summary>
    [JsonPropertyName("bankId")]
    public Guid BankId { get; set; }

    [JsonPropertyName("q")]
    public string Q { get; set; } = "";

    [JsonPropertyName("imageUrl")]
    public string? ImageUrl { get; set; }

    [JsonPropertyName("options")]
    public List<string> Options { get; set; } = new();

    [JsonPropertyName("correct_option_letter")]
    public string? CorrectOptionLetter { get; set; }

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
