using System.ComponentModel.DataAnnotations;

namespace OlympiadReady.Api.Models;

public class GeneratePaperRequest
{
    [Required]
    public string Subject { get; set; } = "Math";

    [Range(1, 12)]
    public int Grade { get; set; } = 6;

    public string Difficulty { get; set; } = "Foundation";

    [Range(1, 50)]
    public int Count { get; set; } = 10;
}
