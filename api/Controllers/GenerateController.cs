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

    /// <summary>Open endpoint: generates 5 sample questions from the DB, no auth required.</summary>
    [HttpPost("preview")]
    public async Task<ActionResult<List<Question>>> Preview(
        [FromBody] PreviewRequest req, CancellationToken ct)
    {
        try
        {
            var questions = await _bank.TryGetRandomAsync(
                req.Subject, req.Grade, req.Difficulty, req.Count, null, ct);
                
            if (questions == null || questions.Count < req.Count)
            {
                // If not enough questions, just return what we have or an error.
                // Since this is just a preview, let's try to get any questions for that subject/grade
                questions = await _bank.TryGetRandomAsync(
                    req.Subject, req.Grade, null, req.Count, null, ct);
            }

            if (questions == null || !questions.Any())
            {
                return Problem("Not enough sample questions available for this subject and grade.", statusCode: 404);
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
