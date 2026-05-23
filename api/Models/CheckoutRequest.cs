using System.ComponentModel.DataAnnotations;

namespace OlympiadReady.Api.Models;

public class CheckoutRequest
{
    [Required]
    public string BillingCycle { get; set; } = "Monthly"; // "Monthly" or "Annual"
    public int Grade { get; set; }
    public List<string> Subjects { get; set; } = new();
}
