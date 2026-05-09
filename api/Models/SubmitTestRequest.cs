using System.ComponentModel.DataAnnotations;

namespace OlympiadReady.Api.Models;

public class SubmitTestRequest
{
    [Required]
    public Guid PaperId { get; set; }

    public List<string?> Answers { get; set; } = new();

    [Range(0, 24 * 60 * 60)]
    public int TimeTakenSeconds { get; set; }
}
