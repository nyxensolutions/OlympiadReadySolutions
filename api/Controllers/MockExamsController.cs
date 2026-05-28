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

        // Level 2 always uses Olympiad-only difficulty — no easy or mid questions.
        bool isLevel2 = req.Level == "L2";

        // Normalise complexity (overridden to Olympiad for L2)
        var complexity = isLevel2 ? "Olympiad" : req.Complexity switch
        {
            "Foundation" => "Foundation",
            "Olympiad"   => "Olympiad",
            _            => "Advanced"
        };

        // Difficulty distribution weights per complexity level.
        // L2 / Olympiad complexity: 100% Olympiad difficulty — no mixing.
        static List<(string Diff, double Weight)> GetWeights(string complexity) => complexity switch
        {
            "Foundation" => new() { ("Foundation", 0.70), ("Advanced", 0.30) },
            "Olympiad"   => new() { ("Olympiad", 1.00) },   // L2 / Olympiad: pure hard
            _            => new() { ("Advanced", 0.50), ("Olympiad", 0.30), ("Foundation", 0.20) }
        };

        var finalQuestions = new List<Question>();
        
        var historicalIds = await _db.UserSeenQuestions
            .Where(x => x.UserId == user.UserId.ToString())
            .Select(x => x.QuestionBankId)
            .ToListAsync(ct);
            
        // Shared used-ID set — accessed only after all DB fetches complete, so no race condition
        var usedIds = new HashSet<Guid>(historicalIds);

        // ── Phase 1: fetch DB questions for all sections (sequential to avoid ID collisions) ──
        var sectionDbQuestions = new List<List<Question>>();
        foreach (var section in req.Sections)
        {
            int aiCount = (useHybridAi && !isTestAccount) ? Math.Min(section.Questions, 10) : 0;
            int dbCount = section.Questions - aiCount;
            var sectionQuestions = new List<Question>();

            if (dbCount > 0)
            {
                var weights = GetWeights(complexity);
                int remaining = dbCount;
                int bucketIdx = 0;

                foreach (var (diff, weight) in weights)
                {
                    if (remaining <= 0) break;
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
            sectionDbQuestions.Add(sectionQuestions);
        }

        // ── Phase 2: fire all AI calls in parallel ──
        var aiTasks = req.Sections.Select((section, i) =>
        {
            int aiCount = (useHybridAi && !isTestAccount) ? Math.Min(section.Questions, 10) : 0;
            int shortfall = section.Questions - sectionDbQuestions[i].Count;
            int totalAiNeeded = Math.Max(aiCount, shortfall);

            if (totalAiNeeded <= 0)
                return Task.FromResult<List<Question>>(new List<Question>());

            // L2 always generates Olympiad-level questions regardless of section difficulty
            var aiDifficulty = isLevel2 ? "Olympiad" : section.Difficulty;

            _log.LogInformation("Parallel AI call: {Count} {Diff} questions for section '{Section}' ({Subject} G{Grade})",
                totalAiNeeded, aiDifficulty, section.Name, req.Subject, req.Grade);

            return _ai.GenerateQuestionsAsync(
                req.Subject, req.Grade, aiDifficulty, totalAiNeeded, null, ct, req.Level, req.OlympiadId);
        }).ToList();

        var allAiResults = await Task.WhenAll(aiTasks);

        // ── Phase 3: merge DB + AI results, persist new AI questions, DB-fill any remaining gap ──
        for (int i = 0; i < req.Sections.Count; i++)
        {
            var section = req.Sections[i];
            var sectionQuestions = sectionDbQuestions[i];
            var aiQuestions = allAiResults[i] ?? new List<Question>();

            sectionQuestions.AddRange(aiQuestions);

            // Persist AI-generated questions to bank for future reuse
            foreach (var q in aiQuestions)
            {
                int idx = q.Options != null ? q.Options.FindIndex(o => string.Equals(o.Trim(), q.Answer?.Trim(), StringComparison.OrdinalIgnoreCase)) : 0;
                string letterAnswer = (idx >= 0 && idx <= 3) ? ((char)('A' + idx)).ToString() : "A";

                _db.QuestionBank.Add(new QuestionBankItem
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
                });
            }

            // Always back-fill from DB if still short (AI timed out, returned fewer, or was skipped)
            int gap = section.Questions - sectionQuestions.Count;
            if (gap > 0)
            {
                // L2: back-fill only from Olympiad difficulty; never fall back to easier questions
                var fillDifficulty = isLevel2 ? "Olympiad" : section.Difficulty;

                _log.LogInformation(
                    "DB back-fill: {Gap} {Diff} questions needed for section '{Section}' after AI ({Subject} G{Grade})",
                    gap, fillDifficulty, section.Name, req.Subject, req.Grade);

                // For L2: try Olympiad only (no easier fallback).
                // For L1: try specific difficulty first, then any difficulty.
                var fill = isLevel2
                    ? await _bank.TryGetRandomAsync(req.Subject, req.Grade, "Olympiad", gap, null, ct, usedIds)
                    : await _bank.TryGetRandomAsync(req.Subject, req.Grade, fillDifficulty, gap, null, ct, usedIds)
                        ?? await _bank.TryGetRandomAsync(req.Subject, req.Grade, null, gap, null, ct, usedIds);

                if (fill != null)
                {
                    sectionQuestions.AddRange(fill);
                    foreach (var q in fill)
                        if (q.BankId != Guid.Empty) usedIds.Add(q.BankId);
                }
            }

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
        
        // Record all questions shown in this exam so they aren't repeated
        var newlySeenIds = finalQuestions
            .Where(q => q.BankId != Guid.Empty && !historicalIds.Contains(q.BankId))
            .Select(q => q.BankId)
            .Distinct()
            .ToList();

        if (newlySeenIds.Any())
        {
            var seenRecords = newlySeenIds.Select(id => new UserSeenQuestion
            {
                UserId = user.UserId.ToString(),
                QuestionBankId = id
            });
            _db.UserSeenQuestions.AddRange(seenRecords);
        }
        
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
