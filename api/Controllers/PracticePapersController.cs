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
    private const int PdfPriceInPaise   = 2900; // ₹29

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

    // ── GET /api/practice-papers/subjects?grade=6 ──────────────────────────
    // Returns subjects available in the question bank for a given grade,
    // and whether the authenticated user has used their one free download.
    [HttpGet("subjects")]
    public async Task<IActionResult> GetSubjects([FromQuery] int grade, CancellationToken ct)
    {
        if (grade < 1 || grade > 12) return BadRequest("Grade must be between 1 and 12.");

        var subjects = await _db.QuestionBank
            .Where(q => q.Grade == grade)
            .Select(q => q.Subject)
            .Distinct()
            .OrderBy(s => s)
            .ToListAsync(ct);

        // Check which subjects have a free download already used (signed-in only)
        HashSet<string> freeUsed = new();
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
        }

        var result = subjects.Select(s => new
        {
            subject        = s,
            grade,
            hasFreeDownload = freeUsed.Contains(s),   // true = already used the one free slot
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
        CancellationToken ct)
    {
        if (grade < 1 || grade > 12) return BadRequest("Invalid grade.");
        if (string.IsNullOrWhiteSpace(subject)) return BadRequest("Subject is required.");

        var user = await _users.GetOrSyncAsync(User, ct);

        // Enforce one-per-user limit
        var alreadyDownloaded = await _db.PdfPurchases.AnyAsync(
            p => p.UserId == user.UserId
              && p.Grade == grade
              && p.Subject == subject
              && p.RazorpayOrderId == FreeMarker, ct);

        if (alreadyDownloaded)
            return StatusCode(409, new
            {
                code    = "FREE_LIMIT_REACHED",
                message = $"You have already downloaded the free {subject} Class {grade} paper. " +
                          $"Get the full 50-question version for ₹{PdfPriceInPaise / 100}."
            });

        var questions = await _bank.TryGetRandomAsync(subject, grade, null, FreeQuestionCount, null, ct);
        if (questions is null || questions.Count == 0)
            return StatusCode(503, new
            {
                message = $"Not enough questions in bank for {subject} Class {grade}. Try another subject."
            });

        // Record the free download before streaming
        _db.PdfPurchases.Add(new PdfPurchase
        {
            UserId            = user.UserId,
            Grade             = grade,
            Subject           = subject,
            RazorpayOrderId   = FreeMarker,
            RazorpayPaymentId = FreeMarker,
            AmountInPaise     = 0,
            PurchasedAt       = DateTime.UtcNow
        });
        await _db.SaveChangesAsync(ct);

        var exportReq = new PdfExportRequest
        {
            Title      = $"Class {grade} {subject} — Free Practice Paper (10 Questions)",
            Subject    = subject,
            Grade      = grade,
            Difficulty = "Mixed",
            Questions  = questions
        };

        var bytes    = _pdf.GeneratePaperPdf(exportReq);
        var filename = $"OlympiadReady-Free-{subject}-Class{grade}.pdf";
        _log.LogInformation("Free PDF served: {Subject} G{Grade} for {UserId}", subject, grade, user.UserId);
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
            subject  = req.Subject
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

        // Record each payment — one entry per paid download transaction
        _db.PdfPurchases.Add(new PdfPurchase
        {
            UserId            = user.UserId,
            Grade             = req.Grade,
            Subject           = req.Subject,
            RazorpayOrderId   = req.OrderId,
            RazorpayPaymentId = req.PaymentId,
            AmountInPaise     = PdfPriceInPaise,
            PurchasedAt       = DateTime.UtcNow
        });
        await _db.SaveChangesAsync(ct);

        // Generate and return the PDF immediately
        var questions = await _bank.TryGetRandomAsync(req.Subject, req.Grade, null, PaidQuestionCount, null, ct);
        if (questions is null || questions.Count == 0)
            return StatusCode(503, new
            {
                message = $"Not enough questions in bank for {req.Subject} Class {req.Grade}."
            });

        var exportReq = new PdfExportRequest
        {
            Title      = $"Class {req.Grade} {req.Subject} — Practice Paper (50 Questions)",
            Subject    = req.Subject,
            Grade      = req.Grade,
            Difficulty = "Mixed",
            Questions  = questions
        };

        var bytes    = _pdf.GeneratePaperPdf(exportReq);
        var filename = $"OlympiadReady-{req.Subject}-Class{req.Grade}-50Q.pdf";
        _log.LogInformation(
            "Paid PDF served: {Subject} G{Grade} for {UserId} via order {OrderId}",
            req.Subject, req.Grade, user.UserId, req.OrderId);

        return File(bytes, "application/pdf", filename);
    }
}
