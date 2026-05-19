namespace OlympiadReady.Api.Data.Entities;

public class PdfPurchase
{
    public Guid PdfPurchaseId { get; set; }
    public Guid UserId { get; set; }
    public User? User { get; set; }
    public int Grade { get; set; }
    public string Subject { get; set; } = "";
    public string RazorpayOrderId { get; set; } = "";
    public string RazorpayPaymentId { get; set; } = "";
    public DateTime PurchasedAt { get; set; }
}
