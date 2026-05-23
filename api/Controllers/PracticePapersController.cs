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
[Route("api/practice-papers")]
public class PracticePapersController : ControllerBase
{
    private const int FreeQuestionCount = 10;
    private const int PaidQuestionCount = 50;
    private const int PdfPriceInPaise   = 1900; // ₹19

    // Marker stored in RazorpayOrderId/PaymentId for free-tier records.
    private const string FreeMarker = "FREE";

    private readonly AppDbContext _db;
    private readonly QuestionBankService _bank;
    private readonly PdfService _pdf;
    private readonly UserService _users;
    private readonly RazorpayService _razorpay;
    private readonly ILogger<PracticePapersController> _log;

    public PracticePapersController(
        AppDbContext db,
        QuestionBankService bank,
        PdfService pdf,
        UserService users,
        RazorpayService razorpay,
        ILogger<PracticePapersController> log)
    {
        _db = db;
        _bank = bank;
        _pdf = pdf;
        _users = users;
        _razorpay = razorpay;
        _log = log;
    }

    private static bool IsSubjectAvailable(string subject, int grade)
    {
        return subject switch
        {
            "Math" or "Science" or "English" or "Logical Reasoning" or "Spell Bee" => grade >= 1 && grade <= 12,
            "Computers" or "AI" or "General Knowledge" => grade >= 1 && grade <= 10,
            "Social Studies" or "Hindi" => grade >= 3 && grade <= 10,
            _ => false
        };
    }

    // ── GET /api/practice-papers/subjects?grade=6 ──────────────────────────
    // Returns subjects available for a given grade,
    // and whether the authenticated user has used their one free download.
    [HttpGet("subjects")]
    public async Task<IActionResult> GetSubjects([FromQuery] int grade, CancellationToken ct)
    {
        if (grade < 1 || grade > 12) return BadRequest("Grade must be between 1 and 12.");

        var allPossibleSubjects = new[] {
            "Math", "Science", "English", "Hindi", "Social Studies", 
            "General Knowledge", "Logical Reasoning", "Computers", "AI", "Spell Bee"
        };

        var subjects = allPossibleSubjects
            .Where(s => IsSubjectAvailable(s, grade))
            .ToList();

        // Check which subjects have a free download already used (signed-in only)
        HashSet<string> freeUsed = new();
        List<string> activeSubs = new();
        Dictionary<string, int> weeklyCount = new();

        if (User.Identity?.IsAuthenticated == true)
        {
            var user = await _users.GetOrSyncAsync(User, ct);
            var rows = await _db.PdfPurchases
                .Where(p => p.UserId == user.UserId
                         && p.Grade == grade
                         && p.RazorpayOrderId == FreeMarker)
                .Select(p => p.Subject)
                .ToListAsync(ct);
            freeUsed = rows.ToHashSet();

            activeSubs = await _db.Subscriptions
                .Where(s => s.UserId == user.UserId && s.Grade == grade && s.EndDate > DateTime.UtcNow)
                .Select(s => s.Subject)
                .ToListAsync(ct);

            DateTime now = DateTime.UtcNow;
            int diff = (7 + (now.DayOfWeek - DayOfWeek.Monday)) % 7;
            DateTime startOfWeek = now.AddDays(-1 * diff).Date;

            var purchasesThisWeek = await _db.PdfPurchases
                .Where(p => p.UserId == user.UserId && p.Grade == grade && p.RazorpayOrderId == "SUBSCRIBED_FREE" && p.PurchasedAt >= startOfWeek)
                .Select(p => p.Subject)
                .ToListAsync(ct);

            foreach(var subj in purchasesThisWeek)
            {
                var baseSubj = subj.Contains('|') ? subj.Split('|')[0] : subj;
                if (!weeklyCount.ContainsKey(baseSubj)) weeklyCount[baseSubj] = 0;
                weeklyCount[baseSubj]++;
            }
        }

        var result = subjects.Select(s => new
        {
            subject        = s,
            grade,
            hasFreeDownload = freeUsed.Contains(s),   // true = already used the one free slot
            isSubscribed = activeSubs.Contains(s) || (s.Contains('|') && activeSubs.Contains(s.Split('|')[0])),
            subscribedDownloadsThisWeek = weeklyCount.GetValueOrDefault(s.Contains('|') ? s.Split('|')[0] : s, 0),
            freeQuestions  = FreeQuestionCount,
            paidQuestions  = PaidQuestionCount,
            priceInPaise   = PdfPriceInPaise,
            priceDisplay   = $"₹{PdfPriceInPaise / 100}"
        });

        return Ok(result);
    }

    // ── GET /api/practice-papers/free-pdf?grade=6&subject=Math ────────────
    // One free 10-question PDF per (user, grade, subject). Requires sign-in
    // so the download can be tracked.
    [Authorize]
    [HttpGet("free-pdf")]
    public async Task<IActionResult> FreePdf(
        [FromQuery] int grade,
        [FromQuery] string subject,
        [FromQuery] string? topic,
        CancellationToken ct)
    {
        if (grade < 1 || grade > 12) return BadRequest("Invalid grade.");
        if (string.IsNullOrWhiteSpace(subject)) return BadRequest("Subject is required.");

        var user = await _users.GetOrSyncAsync(User, ct);
        
        // Use a composite key for topics if provided
        var purchaseKey = string.IsNullOrWhiteSpace(topic) ? subject : $"{subject}|{topic}";

        // Enforce one-per-user limit
        var alreadyDownloaded = await _db.PdfPurchases.AnyAsync(
            p => p.UserId == user.UserId
              && p.Grade == grade
              && p.Subject == purchaseKey
              && p.RazorpayOrderId == FreeMarker, ct);

        if (alreadyDownloaded)
            return StatusCode(409, new
            {
                code    = "FREE_LIMIT_REACHED",
                message = $"You have already downloaded the free {purchaseKey} Class {grade} paper. " +
                          $"Get the full 50-question version for ₹{PdfPriceInPaise / 100}."
            });

        var questions = await _bank.TryGetRandomAsync(subject, grade, null, FreeQuestionCount, topic, ct);
        if (questions is null || questions.Count == 0)
            return StatusCode(503, new
            {
                message = $"Not enough questions in bank for {purchaseKey} Class {grade}. Try another subject."
            });

        // Record the free download before streaming
        _db.PdfPurchases.Add(new PdfPurchase
        {
            UserId            = user.UserId,
            Grade             = grade,
            Subject           = purchaseKey,
            RazorpayOrderId   = FreeMarker,
            RazorpayPaymentId = FreeMarker,
            AmountInPaise     = 0,
            PurchasedAt       = DateTime.UtcNow
        });
        await _db.SaveChangesAsync(ct);

        var exportReq = new PdfExportRequest
        {
            Title      = $"Class {grade} {subject} {(string.IsNullOrWhiteSpace(topic) ? "" : $"- {topic} ")}— Free Practice Paper (10 Questions)",
            Subject    = subject,
            Grade      = grade,
            Difficulty = "Mixed",
            Questions  = questions
        };

        var bytes    = _pdf.GeneratePaperPdf(exportReq);
        var filename = $"OlympiadReady-Free-{subject}{(string.IsNullOrWhiteSpace(topic) ? "" : $"-{topic}")}-Class{grade}.pdf";
        _log.LogInformation("Free PDF served: {Subject} {Topic} G{Grade} for {UserId}", subject, topic, grade, user.UserId);
        return File(bytes, "application/pdf", filename);
    }

    // ── POST /api/practice-papers/checkout ────────────────────────────────
    // Creates a Razorpay order for a ₹29 per-download PDF purchase.
    // Each download is a fresh payment — no unlimited re-downloads.
    [Authorize]
    [HttpPost("checkout")]
    public async Task<IActionResult> Checkout([FromBody] PdfCheckoutRequest req, CancellationToken ct)
    {
        if (!_razorpay.IsConfigured)
            return Problem("Payment gateway is not configured.", statusCode: 503);

        if (req.Grade < 1 || req.Grade > 12) return BadRequest("Invalid grade.");
        if (string.IsNullOrWhiteSpace(req.Subject)) return BadRequest("Subject is required.");

        var user  = await _users.GetOrSyncAsync(User, ct);
        var order = await _razorpay.CreatePdfOrderAsync(req.Grade, req.Subject, user.UserId, ct);

        return Ok(new
        {
            orderId  = order.OrderId,
            keyId    = _razorpay.KeyId,
            amount   = order.AmountInPaise,
            currency = order.Currency,
            grade    = req.Grade,
            subject  = req.Subject,
            topic    = req.Topic
        });
    }

    // ── POST /api/practice-papers/verify ──────────────────────────────────
    // Verifies Razorpay payment, records the purchase, then immediately
    // generates and returns the 50-question PDF — one call, one download.
    [Authorize]
    [HttpPost("verify")]
    public async Task<IActionResult> Verify([FromBody] PdfVerifyRequest req, CancellationToken ct)
    {
        if (!_razorpay.VerifySignature(req.OrderId, req.PaymentId, req.Signature))
        {
            _log.LogWarning("PDF purchase signature mismatch for order {OrderId}", req.OrderId);
            return BadRequest("Signature verification failed.");
        }

        if (req.Grade < 1 || req.Grade > 12) return BadRequest("Invalid grade.");
        if (string.IsNullOrWhiteSpace(req.Subject)) return BadRequest("Subject is required.");

        var user = await _users.GetOrSyncAsync(User, ct);
        var purchaseKey = string.IsNullOrWhiteSpace(req.Topic) ? req.Subject : $"{req.Subject}|{req.Topic}";

        // Record each payment — one entry per paid download transaction
        _db.PdfPurchases.Add(new PdfPurchase
        {
            UserId            = user.UserId,
            Grade             = req.Grade,
            Subject           = purchaseKey,
            RazorpayOrderId   = req.OrderId,
            RazorpayPaymentId = req.PaymentId,
            AmountInPaise     = PdfPriceInPaise,
            PurchasedAt       = DateTime.UtcNow
        });
        await _db.SaveChangesAsync(ct);

        // Generate and return the PDF immediately
        var questions = await _bank.TryGetRandomAsync(req.Subject, req.Grade, null, PaidQuestionCount, req.Topic, ct);
        if (questions is null || questions.Count == 0)
            return StatusCode(503, new
            {
                message = $"Not enough questions in bank for {purchaseKey} Class {req.Grade}."
            });

        var exportReq = new PdfExportRequest
        {
            Title      = $"Class {req.Grade} {req.Subject} {(string.IsNullOrWhiteSpace(req.Topic) ? "" : $"- {req.Topic} ")}— Practice Paper (50 Questions)",
            Subject    = req.Subject,
            Grade      = req.Grade,
            Difficulty = "Mixed",
            Questions  = questions
        };

        var bytes    = _pdf.GeneratePaperPdf(exportReq);
        var filename = $"OlympiadReady-{req.Subject}{(string.IsNullOrWhiteSpace(req.Topic) ? "" : $"-{req.Topic}")}-Class{req.Grade}-50Q.pdf";
        _log.LogInformation(
            "Paid PDF served: {Subject} {Topic} G{Grade} for {UserId} via order {OrderId}",
            req.Subject, req.Topic, req.Grade, user.UserId, req.OrderId);

        return File(bytes, "application/pdf", filename);
    }

    // ── POST /api/practice-papers/subscribed-pdf ──────────────────────────
    // Generates a 50-question PDF for subscribed users (limit 10/week).
    [Authorize]
    [HttpPost("subscribed-pdf")]
    public async Task<IActionResult> SubscribedPdf([FromBody] PdfCheckoutRequest req, CancellationToken ct)
    {
        if (req.Grade < 1 || req.Grade > 12) return BadRequest("Invalid grade.");
        if (string.IsNullOrWhiteSpace(req.Subject)) return BadRequest("Subject is required.");

        var user = await _users.GetOrSyncAsync(User, ct);
        var purchaseKey = string.IsNullOrWhiteSpace(req.Topic) ? req.Subject : $"{req.Subject}|{req.Topic}";

        // 1. Check if subscribed
        bool isSubscribed = await _db.Subscriptions.AnyAsync(s => s.UserId == user.UserId && s.Grade == req.Grade && s.Subject == req.Subject && s.EndDate > DateTime.UtcNow, ct);
        if (!isSubscribed) return Forbid();

        // 2. Check weekly limit
        DateTime now = DateTime.UtcNow;
        int diff = (7 + (now.DayOfWeek - DayOfWeek.Monday)) % 7;
        DateTime startOfWeek = now.AddDays(-1 * diff).Date;

        int countThisWeek = await _db.PdfPurchases.CountAsync(p => p.UserId == user.UserId && p.Grade == req.Grade && (p.Subject == req.Subject || p.Subject.StartsWith(req.Subject + "|")) && p.RazorpayOrderId == "SUBSCRIBED_FREE" && p.PurchasedAt >= startOfWeek, ct);

        if (countThisWeek >= 10)
        {
            return StatusCode(429, new { message = "Weekly limit of 10 downloads reached for this subject." });
        }

        // 3. Generate PDF
        var questions = await _bank.TryGetRandomAsync(req.Subject, req.Grade, null, PaidQuestionCount, req.Topic, ct);
        if (questions is null || questions.Count == 0)
            return StatusCode(503, new { message = $"Not enough questions in bank for {purchaseKey} Class {req.Grade}." });

        _db.PdfPurchases.Add(new PdfPurchase
        {
            UserId            = user.UserId,
            Grade             = req.Grade,
            Subject           = purchaseKey,
            RazorpayOrderId   = "SUBSCRIBED_FREE",
            RazorpayPaymentId = "SUBSCRIBED_FREE",
            AmountInPaise     = 0,
            PurchasedAt       = DateTime.UtcNow
        });
        await _db.SaveChangesAsync(ct);

        var exportReq = new PdfExportRequest
        {
            Title      = $"Class {req.Grade} {req.Subject} {(string.IsNullOrWhiteSpace(req.Topic) ? "" : $"- {req.Topic} ")}— Practice Paper (50 Questions)",
            Subject    = req.Subject,
            Grade      = req.Grade,
            Difficulty = "Mixed",
            Questions  = questions
        };

        var bytes    = _pdf.GeneratePaperPdf(exportReq);
        var filename = $"OlympiadReady-{req.Subject}{(string.IsNullOrWhiteSpace(req.Topic) ? "" : $"-{req.Topic}")}-Class{req.Grade}-50Q.pdf";
        _log.LogInformation(
            "Subscribed PDF served: {Subject} {Topic} G{Grade} for {UserId}",
            req.Subject, req.Topic, req.Grade, user.UserId);

        return File(bytes, "application/pdf", filename);
    }
}
