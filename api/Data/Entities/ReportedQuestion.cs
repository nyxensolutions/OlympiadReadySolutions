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

    [MaxLength(500)]
    public string? AdminReason { get; set; }

    public DateTime ReportedAt { get; set; }
    public DateTime? ResolvedAt { get; set; }

    // Navigations
    public User? User { get; set; }
    public QuestionBankItem? Question { get; set; }
}
