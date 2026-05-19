namespace OlympiadReady.Api.Data.Entities;

public class OlympiadSchedule
{
    public int OlympiadScheduleId { get; set; }
    public string OrgName { get; set; } = "";          // e.g. "SOF", "HBCSE"
    public string OlympiadName { get; set; } = "";     // e.g. "IMO", "INMO"
    public string FullName { get; set; } = "";         // e.g. "International Mathematics Olympiad"
    public string Subject { get; set; } = "";          // Math / Science / English / ...
    public string? Stage { get; set; }                 // Level 1, Level 2, NSE, INO, etc.
    public int? GradeMin { get; set; }
    public int? GradeMax { get; set; }
    public string? RegistrationWindow { get; set; }   // e.g. "Jul – Sep 2025"
    public string? ExamDateText { get; set; }          // e.g. "November 2025 (multiple dates)"
    public DateTime? ExamDateFrom { get; set; }
    public DateTime? ExamDateTo { get; set; }
    public string? ResultDateText { get; set; }
    public string? OfficialWebsite { get; set; }
    public string? Notes { get; set; }
    public int AcademicYear { get; set; }              // e.g. 2025 for 2025-26
    public DateTime LastVerified { get; set; }
}
