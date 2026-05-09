using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/tests")]
public class TestsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly UserService _users;
    private readonly MasteryService _mastery;

    public TestsController(AppDbContext db, UserService users, MasteryService mastery)
    {
        _db = db;
        _users = users;
        _mastery = mastery;
    }

    [HttpPost("submit")]
    public async Task<IActionResult> Submit([FromBody] SubmitTestRequest req, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        var paper = await _db.Papers.AsNoTracking().FirstOrDefaultAsync(p => p.PaperId == req.PaperId, ct);
        if (paper is null) return NotFound("Paper not found");
        if (paper.UserId != user.UserId) return Forbid();

        var questions = JsonSerializer.Deserialize<List<Question>>(paper.JsonContent) ?? new();
        if (req.Answers.Count != questions.Count)
            return BadRequest($"Answer count {req.Answers.Count} does not match question count {questions.Count}");

        var score = questions
            .Zip(req.Answers, (q, a) => q.Answer == a)
            .Count(correct => correct);

        var result = new MockTestResult
        {
            UserId = user.UserId,
            PaperId = paper.PaperId,
            Score = score,
            TotalQuestions = questions.Count,
            TimeTakenSeconds = req.TimeTakenSeconds
        };
        _db.Results.Add(result);
        await _db.SaveChangesAsync(ct);

        await _mastery.UpdateFromAttemptAsync(user.UserId, paper.Subject ?? "", questions, req.Answers, ct);

        return Ok(new
        {
            resultId = result.ResultId,
            score,
            total = questions.Count,
            timeTakenSeconds = result.TimeTakenSeconds
        });
    }
}
