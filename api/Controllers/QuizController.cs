using System.Text.Json;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/quiz")]
public class QuizController : ControllerBase
{
    private readonly AppDbContext _db;

    public QuizController(AppDbContext db) => _db = db;

    /// <summary>
    /// Returns a single random question for the given grade from the question bank.
    /// Answer is NOT included — client must call POST /api/quiz/answer to reveal it.
    /// </summary>
    [HttpGet("daily")]
    public async Task<IActionResult> Daily([FromQuery] int grade = 6, CancellationToken ct = default)
    {
        if (grade < 1 || grade > 12)
            return BadRequest(new { error = "grade must be between 1 and 12" });

        var count = await _db.QuestionBank.CountAsync(q => q.Grade == grade, ct);
        if (count == 0)
            return NotFound(new { error = "No questions found for this grade." });

        var skip = Random.Shared.Next(0, count);
        var item = await _db.QuestionBank
            .AsNoTracking()
            .Where(q => q.Grade == grade)
            .Skip(skip)
            .FirstOrDefaultAsync(ct);

        if (item is null)
            return NotFound(new { error = "Failed to fetch question." });

        string[] opts;
        try { opts = JsonSerializer.Deserialize<string[]>(item.OptionsJson) ?? []; }
        catch { opts = []; }

        return Ok(new
        {
            questionId = item.QuestionBankId,
            questionText = item.QuestionText,
            options = opts,
            subject = item.Subject,
            topic = item.Topic,
            difficulty = item.Difficulty,
        });
    }

    /// <summary>Reveal the correct answer for a question bank item.</summary>
    [HttpPost("answer")]
    public async Task<IActionResult> Answer([FromBody] AnswerRequest req, CancellationToken ct)
    {
        var item = await _db.QuestionBank
            .AsNoTracking()
            .Where(q => q.QuestionBankId == req.QuestionId)
            .Select(q => new { q.CorrectAnswer, q.Explanation })
            .FirstOrDefaultAsync(ct);

        if (item is null) return NotFound();

        return Ok(new
        {
            correctAnswer = item.CorrectAnswer,
            isCorrect = req.SelectedAnswer.Trim().ToUpper() == item.CorrectAnswer.ToUpper(),
            explanation = item.Explanation,
        });
    }
}

public record AnswerRequest(Guid QuestionId, string SelectedAnswer);
