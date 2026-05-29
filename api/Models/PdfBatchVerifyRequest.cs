namespace OlympiadReady.Api.Models;

public class PdfBatchVerifyRequest
{
    public string OrderId { get; set; } = "";
    public string PaymentId { get; set; } = "";
    public string Signature { get; set; } = "";

    /// <summary>Same list sent at checkout — used to re-derive what to generate.</summary>
    public List<PdfBatchItem> Items { get; set; } = new();
}
