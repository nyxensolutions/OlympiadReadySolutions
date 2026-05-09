using Microsoft.AspNetCore.Mvc;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/generate")]
public class GenerateController : ControllerBase
{
    private readonly ClaudeService _claude;
    private readonly ILogger<GenerateController> _log;

    public GenerateController(ClaudeService claude, ILogger<GenerateController> log)
    {
        _claude = claude;
        _log = log;
    }

    /// <summary>Open endpoint: generates 5 sample questions, no auth required.</summary>
    [HttpPost("preview")]
    public async Task<ActionResult<List<Question>>> Preview(
        [FromBody] PreviewRequest req, CancellationToken ct)
    {
        try
        {
            var questions = await _claude.GenerateQuestionsAsync(
                req.Subject, req.Grade, req.Difficulty, req.Count, ct);
            return Ok(questions);
        }
        catch (InvalidOperationException ex)
        {
            _log.LogWarning(ex, "Preview generation failed");
            return Problem(ex.Message, statusCode: 500);
        }
    }
}
