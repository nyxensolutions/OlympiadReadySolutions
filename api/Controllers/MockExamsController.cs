using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

public class GenerateMockExamRequest
{
    public string PatternId { get; set; } = "";
    public string Subject { get; set; } = "";
    public int Grade { get; set; }
    public string Level { get; set; } = "L1";
    public string OlympiadId { get; set; } = "";
    public int TotalTimeMinutes { get; set; }
    public List<MockExamSectionConfig> Sections { get; set; } = new();
    /// <summary>"Foundation" | "Advanced" | "Olympiad" — controls difficulty weighting. Defaults to Advanced.</summary>
    public string Complexity { get; set; } = "Advanced";
}

public class MockExamSectionConfig
{
    public string Name { get; set; } = "";
    public int Questions { get; set; }
    public int MarksPerQuestion { get; set; }
    public string Difficulty { get; set; } = "";
    public List<string>? Topics { get; set; }
}

public class MockExamPatternConfig
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string Org { get; set; } = "";
    public string Subject { get; set; } = "";
    public int MinGrade { get; set; }
    public int MaxGrade { get; set; }
    public string Level { get; set; } = "";
    public int TotalTimeMinutes { get; set; }
    public List<MockExamSectionConfig> Sections { get; set; } = new();
}

[ApiController]
[Authorize]
[Route("api/mock-exams")]
public class MockExamsController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly AiGenerationService _ai;
    private readonly UserService _users;
    private readonly SubscriptionService _subs;
    private readonly QuestionBankService _bank;
    private readonly ILogger<MockExamsController> _log;

    public MockExamsController(
        AppDbContext db,
        AiGenerationService ai,
        UserService users,
        SubscriptionService subs,
        QuestionBankService bank,
        ILogger<MockExamsController> log)
    {
        _db = db;
        _ai = ai;
        _users = users;
        _subs = subs;
        _bank = bank;
        _log = log;
    }

    [HttpPost("generate")]
    public async Task<IActionResult> Generate([FromBody] GenerateMockExamRequest req, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);

        // Normalize subject
        var (canonicalSubject, recognized) = SubjectNormalizer.Normalize(req.Subject);
        if (recognized)
        {
            req.Subject = canonicalSubject!;
        }

        // Quota check
        bool isSubscribed = await _subs.HasUnlockedSubjectAsync(user.UserId, req.Grade, req.Subject, ct);

        int mockExamLimit = isSubscribed ? 7 : 1;

        DateTime startOfWeek = DateTime.UtcNow;
        if (isSubscribed)
        {
            int diff = (7 + (startOfWeek.DayOfWeek - DayOfWeek.Monday)) % 7;
            startOfWeek = startOfWeek.AddDays(-1 * diff).Date;
        }
        else
        {
            startOfWeek = DateTime.MinValue; // Free user limit is across all time
        }

        var recentMocks = await _db.Papers
            .Where(p => p.UserId == user.UserId && p.Title != null && p.Title.StartsWith("Mock Exam"))
            .Where(p => p.CreatedAt >= startOfWeek)
            .CountAsync(ct);

        if (recentMocks >= mockExamLimit)
        {
            return StatusCode(402, new { message = isSubscribed ? "You have reached your limit of 7 mock exams per week." : "Free users can only take 1 mock exam total. Please upgrade to continue." });
        }

        bool useHybridAi = await _subs.ShouldUseHybridAiAsync(user.UserId, req.Grade, req.Subject, ct);
        bool isTestAccount = user.Email.Contains("test", StringComparison.OrdinalIgnoreCase) ||
                             user.Email.Contains("razorpay", StringComparison.OrdinalIgnoreCase);

        // Normalise complexity
        var complexity = req.Complexity switch
        {
            "Foundation" => "Foundation",
            "Olympiad"   => "Olympiad",
            _            => "Advanced"   // default
        };

        // Difficulty distribution weights per complexity level
        // Returns a list of (difficulty, fraction) pairs that sum to 1.
        // We use these to split each section's question count across difficulty buckets.
        static List<(string Diff, double Weight)> GetWeights(string complexity) => complexity switch
        {
            "Foundation" => new() { ("Foundation", 0.70), ("Advanced", 0.30) },
            "Olympiad"   => new() { ("Olympiad", 0.60), ("Advanced", 0.30), ("Foundation", 0.10) },
            _            => new() { ("Advanced", 0.50), ("Olympiad", 0.30), ("Foundation", 0.20) }
        };

        var finalQuestions = new List<Question>();
        // Track all selected question IDs across sections to prevent repetition
        var usedIds = new HashSet<Guid>();

        foreach (var section in req.Sections)
        {
            int aiCount = (useHybridAi && !isTestAccount) ? Math.Min(section.Questions, 10) : 0;
            int dbCount = section.Questions - aiCount;

            var sectionQuestions = new List<Question>();

            // ── DB questions: spread across difficulty buckets based on complexity ──
            if (dbCount > 0)
            {
                var weights = GetWeights(complexity);
                int remaining = dbCount;
                int bucketIdx = 0;

                foreach (var (diff, weight) in weights)
                {
                    if (remaining <= 0) break;
                    // Last bucket gets whatever is left to avoid rounding gaps
                    int bucketCount = bucketIdx == weights.Count - 1
                        ? remaining
                        : (int)Math.Round(dbCount * weight);
                    bucketCount = Math.Min(bucketCount, remaining);
                    bucketIdx++;

                    if (bucketCount <= 0) continue;

                    var bankQuestions = await _bank.TryGetRandomAsync(
                        req.Subject, req.Grade, diff, bucketCount, null, ct, usedIds);

                    if (bankQuestions != null)
                    {
                        sectionQuestions.AddRange(bankQuestions);
                        foreach (var q in bankQuestions)
                            if (q.BankId != Guid.Empty) usedIds.Add(q.BankId);
                        remaining -= bankQuestions.Count;
                    }
                }

                // If still short (some difficulty buckets had no questions), fill from any difficulty
                if (remaining > 0)
                {
                    var fillQuestions = await _bank.TryGetRandomAsync(
                        req.Subject, req.Grade, null, remaining, null, ct, usedIds);
                    if (fillQuestions != null)
                    {
                        sectionQuestions.AddRange(fillQuestions);
                        foreach (var q in fillQuestions)
                            if (q.BankId != Guid.Empty) usedIds.Add(q.BankId);
                    }
                }
            }

            // ── AI questions ──
            if (aiCount > 0)
            {
                _log.LogInformation("Hybrid mock: calling AI for {Count} questions section {Section}", aiCount, section.Name);
                var aiQuestions = await _ai.GenerateQuestionsAsync(
                    req.Subject, req.Grade, section.Difficulty, aiCount, null, ct, req.Level, req.OlympiadId);

                sectionQuestions.AddRange(aiQuestions);

                foreach(var q in aiQuestions)
                {
                    int idx = q.Options != null ? q.Options.FindIndex(o => string.Equals(o.Trim(), q.Answer?.Trim(), StringComparison.OrdinalIgnoreCase)) : 0;
                    string letterAnswer = (idx >= 0 && idx <= 3) ? ((char)('A' + idx)).ToString() : "A";

                    var qbItem = new QuestionBankItem
                    {
                        Subject = req.Subject,
                        Grade = req.Grade,
                        Difficulty = section.Difficulty,
                        Topic = q.Topic ?? "General",
                        QuestionText = q.Q ?? "",
                        OptionsJson = JsonSerializer.Serialize(q.Options ?? new List<string>()),
                        CorrectAnswer = letterAnswer,
                        Explanation = q.Explanation ?? "",
                        CreatedAt = DateTime.UtcNow
                    };
                    _db.QuestionBank.Add(qbItem);
                }
            }

            // ── Fallback to AI for any remaining shortfall ──
            int shortfall = section.Questions - sectionQuestions.Count;
            if (shortfall > 0)
            {
                _log.LogInformation("Shortfall of {Shortfall} questions in section '{Section}' for {Subject} G{Grade}. Calling AI fallback...", shortfall, section.Name, req.Subject, req.Grade);
                var aiQuestions = await _ai.GenerateQuestionsAsync(
                    req.Subject, req.Grade, section.Difficulty, shortfall, null, ct, req.Level, req.OlympiadId);

                if (aiQuestions != null && aiQuestions.Any())
                {
                    sectionQuestions.AddRange(aiQuestions);

                    foreach(var q in aiQuestions)
                    {
                        int idx = q.Options != null ? q.Options.FindIndex(o => string.Equals(o.Trim(), q.Answer?.Trim(), StringComparison.OrdinalIgnoreCase)) : 0;
                        string letterAnswer = (idx >= 0 && idx <= 3) ? ((char)('A' + idx)).ToString() : "A";

                        var qbItem = new QuestionBankItem
                        {
                            Subject = req.Subject,
                            Grade = req.Grade,
                            Difficulty = section.Difficulty,
                            Topic = q.Topic ?? "General",
                            QuestionText = q.Q ?? "",
                            OptionsJson = JsonSerializer.Serialize(q.Options ?? new List<string>()),
                            CorrectAnswer = letterAnswer,
                            Explanation = q.Explanation ?? "",
                            CreatedAt = DateTime.UtcNow
                        };
                        _db.QuestionBank.Add(qbItem);
                    }
                }
            }

            // Assign section and marks
            foreach (var q in sectionQuestions)
            {
                q.SectionName = section.Name;
                q.Marks = section.MarksPerQuestion;
                finalQuestions.Add(q);
            }
        }

        if (finalQuestions.Count == 0)
        {
            return StatusCode(503, new { message = "Not enough questions in bank to generate this mock exam." });
        }

        // Shuffle within sections is already handled by DB and AI, but we can shuffle the whole list? 
        // No, Olympiads usually group questions by section! So we should KEEP the order of sections.

        string jsonContent = JsonSerializer.Serialize(finalQuestions);

        var paper = new QuestionPaper
        {
            UserId = user.UserId,
            Title = $"Mock Exam: {req.PatternId} Class {req.Grade}",
            Grade = req.Grade,
            Subject = req.Subject,
            DifficultyLevel = "Olympiad",
            JsonContent = jsonContent,
            ContentHash = $"MOCK_{req.PatternId}_{DateTime.UtcNow.Ticks}"
        };

        _db.Papers.Add(paper);
        await _db.SaveChangesAsync(ct);

        return Ok(new
        {
            paperId = paper.PaperId,
            title = paper.Title,
            subject = paper.Subject,
            grade = paper.Grade,
            difficulty = paper.DifficultyLevel,
            isMockExam = true,
            patternId = req.PatternId,
            questions = finalQuestions
        });
    }
}
