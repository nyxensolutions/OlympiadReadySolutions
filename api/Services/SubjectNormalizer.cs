using System.Text.RegularExpressions;

namespace OlympiadReady.Api.Services;

/// <summary>
/// Maps any user-supplied subject string to a SOF-aligned canonical name.
/// Canonical names: Mathematics | Science | English | Hindi | General Knowledge |
///                  Social Studies | Logical Reasoning | Cyber | Commerce | AI
/// </summary>
public static class SubjectNormalizer
{
    public static readonly IReadOnlyList<string> CanonicalSubjects =
    [
        "Mathematics",
        "Science",
        "Science-Physics",
        "Science-Chemistry",
        "Science-Biology",
        "English",
        "Hindi",
        "General Knowledge",
        "Social Studies",
        "Logical Reasoning",
        "Computer Science",
        "Commerce",
        "AI",
        "Spell Bee",
    ];

    // All keys are lowercase; values are canonical names.
    private static readonly Dictionary<string, string> Aliases = new(StringComparer.OrdinalIgnoreCase)
    {
        // Mathematics (SOF IMO)
        ["math"]                     = "Mathematics",
        ["maths"]                    = "Mathematics",
        ["mathematics"]              = "Mathematics",
        ["imo"]                      = "Mathematics",

        // Science — general (SOF NSO, lower grades)
        ["science"]                  = "Science",
        ["nso"]                      = "Science",

        // Science sub-disciplines (SOF NSO higher grades)
        ["science-physics"]          = "Science-Physics",
        ["science physics"]          = "Science-Physics",
        ["sciencephysics"]           = "Science-Physics",
        ["physics"]                  = "Science-Physics",
        ["phy"]                      = "Science-Physics",

        ["science-chemistry"]        = "Science-Chemistry",
        ["science chemistry"]        = "Science-Chemistry",
        ["sciencechemistry"]         = "Science-Chemistry",
        ["chemistry"]                = "Science-Chemistry",
        ["chem"]                     = "Science-Chemistry",
        ["che"]                      = "Science-Chemistry",

        ["science-biology"]          = "Science-Biology",
        ["science biology"]          = "Science-Biology",
        ["sciencebiology"]           = "Science-Biology",
        ["biology"]                  = "Science-Biology",
        ["bio"]                      = "Science-Biology",

        // English (SOF IEO)
        ["english"]                  = "English",
        ["ieo"]                      = "English",
        ["eng"]                      = "English",

        // Hindi (SOF IHO)
        ["hindi"]                    = "Hindi",
        ["iho"]                      = "Hindi",

        // General Knowledge (SOF IGKO)
        ["general knowledge"]        = "General Knowledge",
        ["generalknowledge"]         = "General Knowledge",
        ["gk"]                       = "General Knowledge",
        ["igko"]                     = "General Knowledge",
        ["general studies"]          = "General Knowledge",
        ["gs"]                       = "General Knowledge",

        // Social Studies (SOF ISSO)
        ["social studies"]           = "Social Studies",
        ["socialstudies"]            = "Social Studies",
        ["socialscience"]            = "Social Studies",   // filename prefix alias
        ["sst"]                      = "Social Studies",
        ["ss"]                       = "Social Studies",
        ["social science"]           = "Social Studies",
        ["isso"]                     = "Social Studies",
        ["evs"]                      = "Social Studies",

        // Logical Reasoning (SOF IRAO)
        ["logical reasoning"]        = "Logical Reasoning",
        ["logical-reasoning"]        = "Logical Reasoning",
        ["logicalreasoning"]         = "Logical Reasoning",
        ["reasoning"]                = "Logical Reasoning",
        ["aptitude"]                 = "Logical Reasoning",
        ["reasoning & aptitude"]     = "Logical Reasoning",
        ["reasoning and aptitude"]   = "Logical Reasoning",
        ["irao"]                     = "Logical Reasoning",
        ["lr"]                       = "Logical Reasoning",

        // Computer Science (SOF NCO)
        ["computer science"]         = "Computer Science",
        ["computer-science"]         = "Computer Science",
        ["computerscience"]          = "Computer Science",
        ["cyber"]                    = "Computer Science",
        ["nco"]                      = "Computer Science",
        ["computers"]                = "Computer Science",
        ["computer"]                 = "Computer Science",
        ["cs"]                       = "Computer Science",
        ["it"]                       = "Computer Science",
        ["ict"]                      = "Computer Science",
        ["information technology"]   = "Computer Science",

        // Commerce (SOF ICO)
        ["commerce"]                 = "Commerce",
        ["ico"]                      = "Commerce",
        ["bst"]                      = "Commerce",
        ["business studies"]         = "Commerce",
        ["business"]                 = "Commerce",

        // AI (custom)
        ["ai"]                       = "AI",
        ["artificial intelligence"]  = "AI",

        // Spell Bee (Humming Bird Spelling Competition)
        ["spell bee"]                = "Spell Bee",
        ["spellbee"]                 = "Spell Bee",
        ["spelling bee"]             = "Spell Bee",
        ["spellingbee"]              = "Spell Bee",
        ["hbc"]                      = "Spell Bee",
        ["hummingbird"]              = "Spell Bee",
        ["humming bird"]             = "Spell Bee",
        ["spelling"]                 = "Spell Bee",
        ["spell-bee"]                = "Spell Bee",
    };

    /// <summary>
    /// Attempts to map <paramref name="input"/> to a canonical SOF subject name.
    /// Returns (canonicalName, true) on success, or (null, false) when unrecognised.
    /// Matching is case-insensitive and ignores extra whitespace/hyphens/underscores.
    /// </summary>
    public static (string? Name, bool Recognized) Normalize(string? input)
    {
        if (string.IsNullOrWhiteSpace(input)) return (null, false);

        // Try raw trimmed value first.
        var trimmed = input.Trim();
        if (Aliases.TryGetValue(trimmed, out var hit)) return (hit, true);

        // Collapse internal hyphens, underscores, and multiple spaces into a single space.
        var collapsed = Regex.Replace(trimmed, @"[\s\-_]+", " ").Trim();
        if (Aliases.TryGetValue(collapsed, out hit)) return (hit, true);

        return (null, false);
    }

    /// <summary>
    /// Returns a user-friendly error listing recognised subject names and common aliases.
    /// </summary>
    public static string UnrecognisedMessage(string input) =>
        $"Subject '{input}' was not recognised. " +
        $"Expected one of: {string.Join(", ", CanonicalSubjects)}. " +
        "Common aliases are also accepted (e.g. 'math', 'physics', 'biology', 'chemistry', " +
        "'nco', 'sst', 'computerscience', 'ico').";
}
