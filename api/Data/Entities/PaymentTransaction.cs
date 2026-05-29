using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace OlympiadReady.Api.Data.Entities;

public class PaymentTransaction
{
    [Key]
    public Guid TransactionId { get; set; }

    public Guid UserId { get; set; }
    
    [ForeignKey("UserId")]
    public User? User { get; set; }

    public int AmountInPaise { get; set; }

    [MaxLength(10)]
    public string Currency { get; set; } = "INR";

    [MaxLength(100)]
    public string? RazorpayOrderId { get; set; }

    [MaxLength(100)]
    public string? RazorpayPaymentId { get; set; }

    [MaxLength(100)]
    public string? PlanName { get; set; }

    [MaxLength(50)]
    public string Status { get; set; } = "Pending";

    public int Grade { get; set; }
    
    [MaxLength(200)]
    public string? Subjects { get; set; }

    public int Days { get; set; }

    public DateTime CreatedAt { get; set; }
}
