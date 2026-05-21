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
            // Map frontend subject names to DB subject names
            var subject = req.Subject switch
            {
                "Math" => "Mathematics",
                "Computers" => "Computer Science",
                _ => req.Subject
            };

            var questions = await _bank.TryGetRandomAsync(
                subject, req.Grade, req.Difficulty, req.Count, null, ct);
                
            if (questions == null || questions.Count < req.Count)
            {
                // If not enough questions of this difficulty, fall back to any difficulty.
                questions = await _bank.TryGetRandomAsync(
                    subject, req.Grade, null, req.Count, null, ct);
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
