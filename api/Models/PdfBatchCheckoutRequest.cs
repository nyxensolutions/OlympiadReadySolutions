namespace OlympiadReady.Api.Models;

public class PdfBatchCheckoutRequest
{
    /// <summary>List of PDFs the user wants to purchase (1-12 items).</summary>
    public List<PdfBatchItem> Items { get; set; } = new();
}
