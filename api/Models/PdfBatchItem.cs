namespace OlympiadReady.Api.Models;

public class PdfBatchItem
{
    public int Grade { get; set; }
    public string Subject { get; set; } = "";
    public string? Topic { get; set; }
}
