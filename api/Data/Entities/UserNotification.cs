using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace OlympiadReady.Api.Data.Entities;

public class UserNotification
{
    [Key]
    public Guid NotificationId { get; set; }

    [Required]
    public Guid UserId { get; set; }

    [Required]
    [MaxLength(200)]
    public string Title { get; set; } = "";

    [Required]
    [MaxLength(1000)]
    public string Message { get; set; } = "";

    public bool IsRead { get; set; }

    public DateTime CreatedAt { get; set; }

    // Navigation
    public User? User { get; set; }
}
