namespace OlympiadReady.Api.Data.Entities;

public class QuestionBankItem
{
    public Guid QuestionBankId { get; set; }

    /// <summary>SOF-canonical: Mathematics | Science | English | Hindi | General Knowledge | Social Studies | Logical Reasoning | Cyber | Commerce | AI</summary>
    public string Subject { get; set; } = "";

    public int Grade { get; set; }

    /// <summary>Foundation | Advanced | Olympiad</summary>
    public string Difficulty { get; set; } = "";

    /// <summary>Top-level syllabus topic (matches ClaudeService topic vocabulary)</summary>
    public string Topic { get; set; } = "";

    /// <summary>Finer sub-concept within the topic (e.g. "Computation Operations")</summary>
    public string? SubTopic { get; set; }

    public string QuestionText { get; set; } = "";

    /// <summary>Optional URL for an image related to the question</summary>
    public string? ImageUrl { get; set; }

    /// <summary>JSON array of 4 option strings (no A./B. prefix)</summary>
    public string OptionsJson { get; set; } = "[]";

    /// <summary>Single letter: A | B | C | D — index into OptionsJson (0-based: A=0, B=1, C=2, D=3)</summary>
    public string CorrectAnswer { get; set; } = "A";

    public string Explanation { get; set; } = "";

    public DateTime CreatedAt { get; set; }

    // ── Review tracking ────────────────────────────────────────────────────────
    /// <summary>
    /// True when an admin has manually verified this question via the CMS.
    /// AI-generated and script-imported questions default to false.
    /// </summary>
    public bool IsReviewed { get; set; } = false;

    /// <summary>UTC timestamp of the last manual review action.</summary>
    public DateTime? ReviewedAt { get; set; }

    /// <summary>Clerk sub (userId) of the admin who last reviewed this question.</summary>
    public string? ReviewedBy { get; set; }
}
