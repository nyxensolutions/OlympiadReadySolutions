using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace OlympiadReady.Api.Data.Entities;

public class ReportedQuestion
{
    [Key]
    public Guid ReportId { get; set; }

    [Required]
    public Guid UserId { get; set; }

    [Required]
    public Guid QuestionBankId { get; set; }

    [Required]
    [MaxLength(100)]
    public string Category { get; set; } = ""; // e.g. "Wrong question", "Missing correct options"

    [Required]
    [MaxLength(1000)]
    public string Description { get; set; } = "";

    [Required]
    [MaxLength(50)]
    public string Status { get; set; } = "Pending"; // Pending, Accepted, Rejected

    // Widened from 500: a genuinely useful rejection reason — e.g. the worked solution
    // showing why a question's answer key is wrong — routinely runs past 500 characters.
    // The old limit meant a thorough admin got a raw SqlException / bare 500 with no
    // explanation, which looked identical to a client-side CORS failure in the browser.
    [MaxLength(2000)]
    public string? AdminReason { get; set; }

    public DateTime ReportedAt { get; set; }
    public DateTime? ResolvedAt { get; set; }

    // Navigations
    public User? User { get; set; }
    public QuestionBankItem? Question { get; set; }
}
