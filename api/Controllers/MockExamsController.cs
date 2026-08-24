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
    [Microsoft.AspNetCore.RateLimiting.EnableRateLimiting("AiGenerationPolicy")]
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

        int mockExamLimit = isSubscribed ? 7 : 3;

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
            return StatusCode(402, new { message = isSubscribed ? "You have reached your limit of 7 mock exams per week." : "You've used your 3 free mock exams — upgrade to unlock 7 fresh mock exams every week." });
        }

        // Level 2 always uses Olympiad-only difficulty — no easy or mid questions.
        bool isLevel2 = req.Level == "L2";

        // Normalise complexity (overridden to Olympiad for L2)
        var complexity = isLevel2 ? "Olympiad" : req.Complexity switch
        {
            "Foundation" => "Foundation",
            "Olympiad"   => "Olympiad",
            _            => "Advanced"
        };

        bool isTestAccount = user.Email.Contains("test", StringComparison.OrdinalIgnoreCase) ||
                             user.Email.Contains("razorpay", StringComparison.OrdinalIgnoreCase);

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
            // Fill the whole section from the bank. AI is a fallback for what the bank
            // cannot supply, decided per section in Phase 2 — not a slice reserved up front.
            int dbCount = section.Questions;
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
        //
        // Each section reserves its own credit/dollar cost before calling AI. Sections run
        // concurrently via Task.WhenAll, but the reservation is a single atomic SQL UPDATE
        // (see SubscriptionService.TryReserveAiGenerationAsync) — SQL Server serialises
        // concurrent writes to the same user row, so two sections reserving at the same
        // instant still correctly see each other's committed spend rather than racing.
        var aiTasks = req.Sections.Select(async (section, i) =>
        {
            // Only generate what the bank could not fill. The old Math.Max(aiCount, shortfall)
            // meant a section the bank had covered completely still triggered an API call —
            // once per section, in parallel, on every mock exam.
            int shortfall = section.Questions - sectionDbQuestions[i].Count;
            if (shortfall <= 0 || isTestAccount)
                return (Questions: new List<Question>(), AiWasUsed: false);

            // L2 always generates Olympiad-level questions regardless of section difficulty
            var aiDifficulty = isLevel2 ? "Olympiad" : section.Difficulty;
            var model = _ai.ModelForDifficulty(aiDifficulty, req.Level);

            var reservation = await _subs.TryReserveAiGenerationAsync(
                user.UserId, req.Grade, req.Subject, aiDifficulty, shortfall, model, ct);

            if (!reservation.Approved)
            {
                _log.LogInformation("Section '{Section}' AI skipped ({Subject} G{Grade}): {Reason}",
                    section.Name, req.Subject, req.Grade, reservation.DenialReason);
                return (Questions: new List<Question>(), AiWasUsed: false);
            }

            _log.LogInformation(
                "Parallel AI call: {Count} {Diff} questions for section '{Section}' ({Subject} G{Grade}, {Model}, reserved {Credits}cr/${Dollars})",
                shortfall, aiDifficulty, section.Name, req.Subject, req.Grade, model,
                reservation.CreditsReserved, reservation.DollarsReserved);

            var genResult = await _ai.GenerateQuestionsAsync(
                req.Subject, req.Grade, aiDifficulty, shortfall, null, ct, req.Level, req.OlympiadId);

            var actualCost = AiPricing.ActualCost(genResult.Model, genResult.PromptTokens, genResult.CompletionTokens);
            await _subs.ReconcileAiGenerationAsync(
                user.UserId, aiDifficulty, shortfall, genResult.Questions.Count,
                reservation.DollarsReserved, actualCost, ct);

            return (Questions: genResult.Questions, AiWasUsed: genResult.Questions.Count > 0);
        }).ToList();

        var allAiResults = await Task.WhenAll(aiTasks);
        bool aiUsed = allAiResults.Any(r => r.AiWasUsed);

        // ── Phase 3: merge DB + AI results, persist new AI questions, DB-fill any remaining gap ──
        for (int i = 0; i < req.Sections.Count; i++)
        {
            var section = req.Sections[i];
            var sectionQuestions = sectionDbQuestions[i];
            var aiQuestions = allAiResults[i].Questions;

            sectionQuestions.AddRange(aiQuestions);

            // Shuffle before persisting, not just before display — nothing re-shuffles a
            // question's options once it is read back from the bank, so an unshuffled save
            // here would permanently bake in the model's real, measured tendency to place the
            // correct answer first.
            AiGenerationService.ShuffleOptions(aiQuestions);

            // Persist AI-generated questions to bank for future reuse
            foreach (var q in aiQuestions)
            {
                int idx = q.Options?.FindIndex(o => string.Equals(o.Trim(), q.Answer?.Trim(), StringComparison.OrdinalIgnoreCase)) ?? -1;
                if (idx < 0 || idx > 3)
                {
                    // Answer text didn't match any option -- saving with a guessed letter
                    // would bank a question with the wrong answer marked correct.
                    _log.LogWarning("Mock exam flywheel skip — answer '{Answer}' not found in options for question: {Q}",
                        q.Answer, q.Q?[..Math.Min(80, q.Q?.Length ?? 0)]);
                    continue;
                }
                string letterAnswer = ((char)('A' + idx)).ToString();

                var newBankId = Guid.NewGuid();
                _db.QuestionBank.Add(new QuestionBankItem
                {
                    QuestionBankId = newBankId,
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
                q.BankId = newBankId;
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

        // Charge the account AI credit budget once per AI-backed mock (Olympiad complexity costs more).
        if (aiUsed)
            await _subs.RecordOnlineTestGenerationAsync(user.UserId, req.Grade, req.Subject, true, complexity, ct);

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
