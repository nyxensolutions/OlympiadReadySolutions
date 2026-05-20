namespace OlympiadReady.Api.Data.Entities;

/// <summary>
/// A word in the Hummingbird Spell Bee competition word bank.
/// Grades 1–8, difficulty Easy | Medium | Hard.
/// </summary>
public class SpellBeeWord
{
    public Guid SpellBeeWordId { get; set; }

    /// <summary>The word to be spelled (e.g. "necessary").</summary>
    public string Word { get; set; } = "";

    /// <summary>Grade band: 1–8.</summary>
    public int Grade { get; set; }

    /// <summary>Easy | Medium | Hard</summary>
    public string Difficulty { get; set; } = "Easy";

    /// <summary>Word category (e.g. Animals, Science, General, Vocabulary).</summary>
    public string Category { get; set; } = "General";

    /// <summary>Short definition of the word.</summary>
    public string Definition { get; set; } = "";

    /// <summary>Example sentence using the word.</summary>
    public string UsageSentence { get; set; } = "";

    /// <summary>Language origin hint (e.g. Latin, French, Sanskrit).</summary>
    public string? Origin { get; set; }

    /// <summary>Phonetic pronunciation hint (e.g. "nec-es-sa-ry").</summary>
    public string? Pronunciation { get; set; }

    /// <summary>Tip for remembering the spelling.</summary>
    public string? MemoryTip { get; set; }

    public DateTime CreatedAt { get; set; }
}
