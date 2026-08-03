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

        bool isMockExam = paper.Title != null && paper.Title.StartsWith("Mock Exam");

        int score = 0;
        int earnedMarks = 0;
        int totalMarks = 0;

        for (int i = 0; i < questions.Count; i++)
        {
            var q = questions[i];
            var a = req.Answers[i];
            int qMarks = q.Marks ?? 1;
            totalMarks += qMarks;

            if (q.Answer == a)
            {
                score++;
                earnedMarks += qMarks;
            }
        }

        // Get past results to compute tier before
        var pastResults = await _db.Results
            .AsNoTracking()
            .Where(r => r.UserId == user.UserId && r.TotalQuestions > 0)
            .Select(r => new BadgeCalculator.ResultRow(r.UserId, r.Score, r.TotalQuestions, r.TimeTakenSeconds, r.CompletedAt, r.Paper != null ? r.Paper.Title ?? "" : "", r.Paper != null ? r.Paper.Subject ?? "" : ""))
            .ToListAsync(ct);
        var repCount = await _db.ReportedQuestions.CountAsync(r => r.UserId == user.UserId && r.Status == "Accepted", ct);
        
        var oldEarned = BadgeCalculator.ComputeBadges(pastResults, repCount).Count(b => b.Earned);
        var oldTitle = BadgeCalculator.GetTitle(oldEarned, 24);

        // Idempotency: if this paper was already submitted, return the existing result.
        var existing = await _db.Results
            .AsNoTracking()
            .FirstOrDefaultAsync(r => r.UserId == user.UserId && r.PaperId == paper.PaperId, ct);
        if (existing != null)
        {
            return Ok(new
            {
                resultId = existing.ResultId,
                score = existing.Score,
                total = existing.TotalQuestions,
                timeTakenSeconds = existing.TimeTakenSeconds,
                totalMarks = existing.TotalMarks,
                earnedMarks = existing.EarnedMarks
            });
        }

        var result = new MockTestResult
        {
            UserId = user.UserId,
            PaperId = paper.PaperId,
            Score = score,
            TotalQuestions = questions.Count,
            TimeTakenSeconds = req.TimeTakenSeconds,
            CompletedAt = DateTime.UtcNow,
            TotalMarks = totalMarks,
            EarnedMarks = earnedMarks
        };
        _db.Results.Add(result);

        // Process mistakes
        var unresolvedMistakes = await _db.UserMistakes
            .Where(m => m.UserId == user.UserId && !m.IsResolved)
            .ToListAsync(ct);

        for (int i = 0; i < questions.Count; i++)
        {
            var q = questions[i];
            var userAnswer = req.Answers[i];
            var isCorrect = q.Answer == userAnswer;

            // Search for unresolved mistake containing this question text
            var existingMistake = unresolvedMistakes.FirstOrDefault(m => {
                try {
                    var mq = JsonSerializer.Deserialize<Question>(m.QuestionJson);
                    return mq != null && string.Equals(mq.Q?.Trim(), q.Q?.Trim(), StringComparison.OrdinalIgnoreCase);
                } catch {
                    return m.QuestionJson.Contains(q.Q);
                }
            });

            if (!isCorrect)
            {
                if (existingMistake == null)
                {
                    var mistake = new UserMistake
                    {
                        UserId = user.UserId,
                        Subject = paper.Subject ?? "",
                        Grade = paper.Grade,
                        Topic = q.Topic ?? "General",
                        QuestionJson = JsonSerializer.Serialize(q),
                        CorrectAnswer = q.Answer,
                        UserAnswer = userAnswer ?? "",
                        IsResolved = false,
                        OccurredAt = DateTime.UtcNow
                    };
                    _db.UserMistakes.Add(mistake);
                }
            }
            else
            {
                // Clean up all unresolved duplicates of this mistake in the DB
                var matchingMistakes = unresolvedMistakes.Where(m => {
                    try {
                        var mq = JsonSerializer.Deserialize<Question>(m.QuestionJson);
                        return mq != null && string.Equals(mq.Q?.Trim(), q.Q?.Trim(), StringComparison.OrdinalIgnoreCase);
                    } catch {
                        return m.QuestionJson.Contains(q.Q);
                    }
                }).ToList();

                foreach (var m in matchingMistakes)
                {
                    m.IsResolved = true;
                }
            }
        }

        await _db.SaveChangesAsync(ct);

        await _mastery.UpdateFromAttemptAsync(user.UserId, paper.Subject ?? "", questions, req.Answers, ct);

        // Compute tier after
        var newResultRow = new BadgeCalculator.ResultRow(user.UserId, score, questions.Count, req.TimeTakenSeconds, DateTime.UtcNow, paper.Title ?? "", paper.Subject ?? "");
        pastResults.Add(newResultRow);
        
        var newEarned = BadgeCalculator.ComputeBadges(pastResults, repCount).Count(b => b.Earned);
        var newTitle = BadgeCalculator.GetTitle(newEarned, 24);

        if (newTitle != oldTitle && newTitle != "Newcomer")
        {
            _db.UserNotifications.Add(new UserNotification
            {
                UserId = user.UserId,
                Title = "New Title Unlocked!",
                Message = $"Congratulations! You have earned the prestigious {newTitle} title. Download your official certificate in the Achievements panel.",
                CreatedAt = DateTime.UtcNow
            });
            await _db.SaveChangesAsync(ct);
        }

        return Ok(new
        {
            resultId = result.ResultId,
            score,
            total = questions.Count,
            timeTakenSeconds = result.TimeTakenSeconds,
            totalMarks,
            earnedMarks
        });
    }
}
