using System.ComponentModel.DataAnnotations;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Models;

public class GeneratePaperRequest : IValidatableObject
{
    [Required]
    public string Subject { get; set; } = "Mathematics";

    [Range(1, 12)]
    public int Grade { get; set; } = 6;

    public string Difficulty { get; set; } = "Foundation";

    [Range(1, 50)]
    public int Count { get; set; } = 10;

    /// <summary>Optional: restrict questions to this topic (must match QB topic strings).</summary>
    [StringLength(80)]
    public string? Topic { get; set; }

    public bool MistakesOnly { get; set; } = false;

    /// <summary>Olympiad level the student is preparing for: L1 (school round) or L2 (national round).</summary>
    public string? OlympiadLevel { get; set; }

    /// <summary>
    /// The specific olympiad ID the student is targeting (e.g. "sof_imo", "hbcse", "silverzone_math").
    /// Forwarded to ClaudeService to tailor question style, section patterns, and vocabulary.
    /// </summary>
    public string? OlympiadId { get; set; }

    // Mirrors SUBJECT_GRADE_MAP in web/lib/types.ts — keep in sync.
    // Subject names are SOF-canonical; SubjectNormalizer maps aliases before this is checked.
    private static readonly Dictionary<string, (int Min, int Max)> GradeRanges = new(StringComparer.OrdinalIgnoreCase)
    {
        ["Mathematics"]        = (1, 12),
        ["Science"]            = (1, 8),   // general science (NSO junior)
        ["Science-Physics"]    = (6, 12),
        ["Science-Chemistry"]  = (6, 12),
        ["Science-Biology"]    = (6, 12),
        ["English"]            = (1, 12),
        ["Logical Reasoning"]  = (1, 12),
        ["Computer Science"]   = (1, 12),
        ["AI"]                 = (1, 10),
        ["General Knowledge"]  = (1, 10),
        ["Social Studies"]     = (1, 10),
        ["Hindi"]              = (3, 10),
        ["Commerce"]           = (11, 12),
        ["Spell Bee"]          = (1, 12),
    };

    public IEnumerable<ValidationResult> Validate(ValidationContext validationContext)
    {
        // Normalize alias → canonical name in-place so downstream code always sees clean values.
        var (canonical, recognized) = SubjectNormalizer.Normalize(Subject);
        if (!recognized)
        {
            yield return new ValidationResult(
                SubjectNormalizer.UnrecognisedMessage(Subject),
                [nameof(Subject)]);
            yield break;
        }
        Subject = canonical!;

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
