using System.ComponentModel.DataAnnotations;

namespace OlympiadReady.Api.Models;

public class GeneratePaperRequest : IValidatableObject
{
    [Required]
    public string Subject { get; set; } = "Math";

    [Range(1, 12)]
    public int Grade { get; set; } = 6;

    public string Difficulty { get; set; } = "Foundation";

    [Range(1, 50)]
    public int Count { get; set; } = 10;

    // Mirrors SUBJECT_GRADE_MAP in web/lib/types.ts — keep in sync.
    private static readonly Dictionary<string, (int Min, int Max)> GradeRanges = new(StringComparer.OrdinalIgnoreCase)
    {
        ["Math"]               = (1, 12),
        ["Science"]            = (1, 12),
        ["English"]            = (1, 12),
        ["Logical Reasoning"]  = (1, 12),
        ["Computers"]          = (1, 10),
        ["AI"]                 = (1, 10),
        ["General Knowledge"]  = (1, 10),
        ["Hindi"]              = (3, 10),
    };

    public IEnumerable<ValidationResult> Validate(ValidationContext validationContext)
    {
        if (!GradeRanges.TryGetValue(Subject, out var range))
        {
            yield return new ValidationResult(
                $"'{Subject}' is not a recognised subject.",
                [nameof(Subject)]);
            yield break;
        }

        if (Grade < range.Min || Grade > range.Max)
            yield return new ValidationResult(
                $"{Subject} is not offered for Class {Grade}. Valid range: Class {range.Min}–{range.Max}.",
                [nameof(Grade), nameof(Subject)]);
    }
}
