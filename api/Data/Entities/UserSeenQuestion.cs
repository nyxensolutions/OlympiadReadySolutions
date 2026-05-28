using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace OlympiadReady.Api.Data.Entities;

public class UserSeenQuestion
{
    [Key]
    public int Id { get; set; }

    [Required]
    [MaxLength(200)]
    public string UserId { get; set; } = "";

    [Required]
    public Guid QuestionBankId { get; set; }

    public DateTime SeenAt { get; set; }
}
