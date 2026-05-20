namespace OlympiadReady.Api.Models;

public class PdfVerifyRequest
{
    public string OrderId { get; set; } = "";
    public string PaymentId { get; set; } = "";
    public string Signature { get; set; } = "";
    public int Grade { get; set; }
    public string Subject { get; set; } = "";
    public string? Topic { get; set; }
}
