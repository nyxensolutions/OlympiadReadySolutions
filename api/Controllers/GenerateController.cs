using Microsoft.AspNetCore.Mvc;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/generate")]
public class GenerateController : ControllerBase
{
    private readonly QuestionBankService _bank;
    private readonly ILogger<GenerateController> _log;

    public GenerateController(QuestionBankService bank, ILogger<GenerateController> log)
    {
        _bank = bank;
        _log = log;
    }

    /// <summary>Open endpoint: generates sample questions from the DB, no auth required.</summary>
    [HttpPost("preview")]
    public async Task<ActionResult<List<Question>>> Preview(
        [FromBody] PreviewRequest req, CancellationToken ct)
    {
        try
        {
            // Normalize subject names using SubjectNormalizer
            var (canonicalSubject, recognized) = SubjectNormalizer.Normalize(req.Subject);
            var subject = recognized ? canonicalSubject! : req.Subject;

            // Fetch a mixed difficulty paper: 1 Foundation, 2 Advanced, 2 Olympiad
            var qFoundation = await _bank.TryGetRandomAsync(subject, req.Grade, "Foundation", 1, null, ct) ?? new List<Question>();
            var qAdvanced = await _bank.TryGetRandomAsync(subject, req.Grade, "Advanced", 2, null, ct) ?? new List<Question>();
            var qOlympiad = await _bank.TryGetRandomAsync(subject, req.Grade, "Olympiad", 2, null, ct) ?? new List<Question>();

            var questions = new List<Question>();
            questions.AddRange(qFoundation);
            questions.AddRange(qAdvanced);
            questions.AddRange(qOlympiad);

            if (questions.Count < 5)
            {
                // Fall back to just fetching any 5 random questions if the exact mix isn't fully available
                questions = await _bank.TryGetRandomAsync(subject, req.Grade, null, 5, null, ct) ?? new List<Question>();
            }

            if (questions == null || !questions.Any())
            {
                return Problem("No questions found for this subject and grade.", statusCode: 404);
            }

            return Ok(questions);
        }
        catch (Exception ex)
        {
            _log.LogWarning(ex, "Preview generation failed");
            return Problem(ex.Message, statusCode: 500);
        }
    }
}
