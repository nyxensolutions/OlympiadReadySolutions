using OlympiadReady.Api.Controllers;

namespace OlympiadReady.Api.Services;

/// <summary>
/// Server copy of web/lib/olympiadPatterns.ts, used when a client (the mobile app) asks for a
/// mock exam without sending sections. Keep the two lists in sync.
/// </summary>
public static class MockExamPatterns
{
    public record Pattern(string Id, string Subject, int MinGrade, int MaxGrade, string Level, int TotalTimeMinutes,
        (string Name, int Questions, int Marks, string Difficulty)[] Sections)
    {
        public List<MockExamSectionConfig> ToSections() => Sections
            .Select(s => new MockExamSectionConfig
            {
                Name = s.Name, Questions = s.Questions, MarksPerQuestion = s.Marks, Difficulty = s.Difficulty, Topics = new(),
            })
            .ToList();
    }

    private const string F = "Foundation", A = "Advanced", O = "Olympiad";

    private static readonly Pattern[] All =
    [
        new("sof_imo_l1_1_4", "Mathematics", 1, 4, "L1", 60, [("Logical Reasoning", 10, 1, F), ("Mathematical Reasoning", 10, 1, F), ("Everyday Mathematics", 10, 1, A), ("Achievers Section", 5, 2, O)]),
        new("sof_imo_l1_5_12", "Mathematics", 5, 12, "L1", 60, [("Logical Reasoning", 15, 1, F), ("Mathematical Reasoning", 20, 1, A), ("Everyday Mathematics", 10, 1, A), ("Achievers Section", 5, 3, O)]),
        new("sof_nso_l1_1_4", "Science", 1, 4, "L1", 60, [("Logical Reasoning", 5, 1, F), ("Science", 25, 1, A), ("Achievers Section", 5, 2, O)]),
        new("sof_nso_l1_5_12", "Science", 5, 12, "L1", 60, [("Logical Reasoning", 10, 1, F), ("Science", 35, 1, A), ("Achievers Section", 5, 3, O)]),
        new("sof_ieo_l1_1_4", "English", 1, 4, "L1", 60, [("Word and Structure Knowledge", 15, 1, F), ("Reading", 10, 1, A), ("Spoken and Written Expression", 5, 1, A), ("Achievers Section", 5, 2, O)]),
        new("sof_ieo_l1_5_12", "English", 5, 12, "L1", 60, [("Word and Structure Knowledge", 25, 1, F), ("Reading", 10, 1, A), ("Spoken and Written Expression", 10, 1, A), ("Achievers Section", 5, 3, O)]),
        new("generic_l2_5_12", "Mathematics", 5, 12, "L2", 60, [("Subject Knowledge", 40, 1, A), ("Achievers Section", 10, 3, O)]),
        new("sof_lr_l1_1_4", "Logical Reasoning", 1, 4, "L1", 60, [("Verbal Reasoning", 10, 1, F), ("Non-Verbal Reasoning", 10, 1, F), ("Achievers Section", 5, 2, O)]),
        new("sof_lr_l1_5_12", "Logical Reasoning", 5, 12, "L1", 60, [("Verbal Reasoning", 15, 1, F), ("Non-Verbal Reasoning", 20, 1, A), ("Achievers Section", 5, 3, O)]),
        new("sof_nco_l1_1_4", "Computer Science", 1, 4, "L1", 60, [("Logical Reasoning", 5, 1, F), ("Computers & IT", 25, 1, A), ("Achievers Section", 5, 2, O)]),
        new("sof_nco_l1_5_10", "Computer Science", 5, 12, "L1", 60, [("Logical Reasoning", 10, 1, F), ("Computers & IT", 35, 1, A), ("Achievers Section", 5, 3, O)]),
        new("sof_ai_l1_1_4", "AI", 1, 4, "L1", 60, [("Core AI Concepts", 15, 1, F), ("Logical Reasoning", 10, 1, F), ("Achievers Section", 5, 2, O)]),
        new("sof_ai_l1_5_10", "AI", 5, 10, "L1", 60, [("Core AI Concepts", 25, 1, A), ("Logical Reasoning", 10, 1, F), ("Achievers Section", 5, 3, O)]),
        new("sof_igko_l1_1_4", "General Knowledge", 1, 4, "L1", 60, [("General Awareness", 20, 1, F), ("Current Affairs", 5, 1, F), ("Life Skills", 5, 1, F), ("Achievers Section", 5, 2, O)]),
        new("sof_igko_l1_5_10", "General Knowledge", 5, 10, "L1", 60, [("General Awareness", 30, 1, A), ("Current Affairs", 10, 1, F), ("Life Skills", 5, 1, F), ("Achievers Section", 5, 3, O)]),
        new("sof_isso_l1_3_4", "Social Studies", 3, 4, "L1", 60, [("History", 10, 1, F), ("Geography", 10, 1, F), ("Civics", 10, 1, F), ("Achievers Section", 5, 2, O)]),
        new("sof_isso_l1_5_10", "Social Studies", 5, 10, "L1", 60, [("History", 15, 1, A), ("Geography", 15, 1, A), ("Civics", 15, 1, A), ("Achievers Section", 5, 3, O)]),
        new("sof_iho_l1_3_4", "Hindi", 3, 4, "L1", 60, [("Vyakaran (Grammar)", 20, 1, F), ("Sahitya (Literature)", 10, 1, F), ("Achievers Section", 5, 2, O)]),
        new("sof_iho_l1_5_10", "Hindi", 5, 10, "L1", 60, [("Vyakaran (Grammar)", 30, 1, A), ("Sahitya (Literature)", 15, 1, F), ("Achievers Section", 5, 3, O)]),
        new("sof_spellbee_l1_1_4", "Spell Bee", 1, 4, "L1", 60, [("Spellings & Vocabulary", 30, 1, F), ("Achievers Section", 5, 2, O)]),
        new("sof_spellbee_l1_5_12", "Spell Bee", 5, 12, "L1", 60, [("Spellings & Vocabulary", 45, 1, A), ("Achievers Section", 5, 3, O)]),
        new("sof_ico_l1_11_12", "Commerce", 11, 12, "L1", 60, [("Accountancy", 15, 1, F), ("Business Studies", 15, 1, F), ("Economics", 15, 1, F), ("Achievers Section", 5, 3, O)]),
    ];

    /// <summary>
    /// The official pattern for this subject/class/level, or (like the website's Level 2 fallback)
    /// a generic two-section paper when no official pattern covers the combination.
    /// </summary>
    public static Pattern Find(string subject, int grade, string level)
    {
        var canonical = SubjectNormalizer.Normalize(subject).Name ?? subject;
        var match = All.FirstOrDefault(p =>
            p.Level == level && grade >= p.MinGrade && grade <= p.MaxGrade &&
            string.Equals(p.Subject, canonical, StringComparison.OrdinalIgnoreCase));
        if (match != null) return match;

        return new Pattern($"generic_{level.ToLowerInvariant()}_{canonical.ToLowerInvariant().Replace(' ', '_')}",
            canonical, 1, 12, level, 60,
            [("Subject Knowledge", grade >= 5 ? 40 : 30, 1, A), ("Achievers Section", 5, grade >= 5 ? 3 : 2, O)]);
    }
}
