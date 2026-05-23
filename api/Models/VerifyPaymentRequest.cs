using System.ComponentModel.DataAnnotations;

namespace OlympiadReady.Api.Models;

public class VerifyPaymentRequest
{
    [Required]
    public string OrderId { get; set; } = "";

    [Required]
    public string PaymentId { get; set; } = "";

    [Required]
    public string Signature { get; set; } = "";

    [Required]
    public string BillingCycle { get; set; } = "Monthly";
    public int Grade { get; set; }
    public List<string> Subjects { get; set; } = new();
}
