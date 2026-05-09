using System.ComponentModel.DataAnnotations;

namespace OlympiadReady.Api.Models;

public class PdfExportRequest
{
    public string Title { get; set; } = "Olympiad Ready Practice Paper";

    [Required]
    public string Subject { get; set; } = "Math";

    [Range(1, 12)]
    public int Grade { get; set; } = 6;

    public string Difficulty { get; set; } = "Foundation";

    [Required]
    public List<Question> Questions { get; set; } = new();
}
