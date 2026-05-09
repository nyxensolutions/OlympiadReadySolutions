using System.ComponentModel.DataAnnotations;

namespace OlympiadReady.Api.Models;

public class CheckoutRequest
{
    [Required]
    public string Plan { get; set; } = "ProMonthly";
}
