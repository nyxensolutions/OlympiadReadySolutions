using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/billing")]
public class BillingController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly UserService _users;
    private readonly SubscriptionService _subs;
    private readonly RazorpayService _razorpay;
    private readonly IEmailService _emailService;
    private readonly ILogger<BillingController> _log;

    public BillingController(
        AppDbContext db,
        UserService users,
        SubscriptionService subs,
        RazorpayService razorpay,
        IEmailService emailService,
        ILogger<BillingController> log)
    {
        _db = db;
        _users = users;
        _subs = subs;
        _razorpay = razorpay;
        _emailService = emailService;
        _log = log;
    }

    [HttpGet("me")]
    public async Task<IActionResult> Me(CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        var summary = await _subs.GetSubscriptionSummaryAsync(user.UserId, ct);
        return Ok(summary);
    }

    [HttpGet("history")]
    public async Task<IActionResult> History(CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);

        var subscriptions = await _db.Subscriptions
            .Where(s => s.UserId == user.UserId)
            .OrderByDescending(s => s.StartDate)
            .Select(s => new
            {
                type              = "subscription",
                id                = s.SubscriptionId,
                planName          = s.PlanName,
                grade             = s.Grade,
                subject           = s.Subject,
                startDate         = s.StartDate,
                endDate           = s.EndDate,
                isActive          = s.IsActive,
                amountInPaise     = s.AmountInPaise,
                razorpayOrderId   = s.RazorpayOrderId,
                razorpayPaymentId = s.RazorpayPaymentId,
                purchasedAt       = s.StartDate
            })
            .ToListAsync(ct);

        var pdfPurchases = await _db.PdfPurchases
            .Where(p => p.UserId == user.UserId)
            .OrderByDescending(p => p.PurchasedAt)
            .Select(p => new
            {
                type              = "pdf",
                id                = p.PdfPurchaseId,
                subject           = p.Subject,
                grade             = p.Grade,
                amountInPaise     = p.AmountInPaise,
                isFree            = p.RazorpayOrderId == "FREE",
                razorpayOrderId   = p.RazorpayOrderId,
                razorpayPaymentId = p.RazorpayPaymentId,
                purchasedAt       = p.PurchasedAt
            })
            .ToListAsync(ct);

        return Ok(new
        {
            currentTier   = subscriptions.Any(s => s.isActive) ? "Modular" : "Free",
            freeAttemptsUsed = user.FreeAttemptsUsed,
            freeAttemptsLimit = SubscriptionService.GlobalFreeAttemptsLimit,
            subscriptions,
            pdfPurchases
        });
    }

    // Subjects available per grade — mirrors PracticePapersController.IsSubjectAvailable
    private static List<string> AllSubjectsForGrade(int grade) => grade switch
    {
        11 or 12 => new() { "Math", "Science", "English", "Logical Reasoning", "Computers", "AI", "General Knowledge", "Commerce" },
        >= 3     => new() { "Math", "Science", "English", "Hindi", "Social Studies", "General Knowledge", "Logical Reasoning", "Computers", "AI" },
        _        => new() { "Math", "Science", "English", "General Knowledge", "Logical Reasoning", "Computers", "AI" }
    };

    [HttpPost("checkout")]
    public async Task<IActionResult> Checkout([FromBody] CheckoutRequest req, CancellationToken ct)
    {
        if (!_razorpay.IsConfigured)
            return Problem("Razorpay is not configured on the server.", statusCode: 503);

        if (req.Subjects == null || req.Subjects.Count == 0)
            return BadRequest("At least one subject must be selected.");

        var user = await _users.GetOrSyncAsync(User, ct);
        bool isChampion = req.Subjects.Contains("All", StringComparer.OrdinalIgnoreCase);

        // For Champion, check that user doesn't already have all subjects active
        var subjectsToCheck = isChampion ? AllSubjectsForGrade(req.Grade) : req.Subjects;
        var alreadyActive   = new List<string>();
        foreach (var subject in subjectsToCheck)
        {
            if (await _subs.HasUnlockedSubjectAsync(user.UserId, req.Grade, subject, ct))
                alreadyActive.Add(subject);
        }
        if (!isChampion && alreadyActive.Count > 0)
            return BadRequest($"You already have an active subscription for Class {req.Grade} {alreadyActive[0]}.");
        if (isChampion && alreadyActive.Count == subjectsToCheck.Count)
            return BadRequest($"You already have an active Champion subscription for Class {req.Grade}.");

        try
        {
            var pricing = _razorpay.CalculatePrice(req.BillingCycle, req.Subjects);
            var order   = await _razorpay.CreateDynamicOrderAsync(pricing.AmountInPaise, pricing.Currency, pricing.DisplayName, user.UserId, ct);

            var transaction = new OlympiadReady.Api.Data.Entities.PaymentTransaction
            {
                UserId          = user.UserId,
                AmountInPaise   = pricing.AmountInPaise,
                Currency        = pricing.Currency,
                RazorpayOrderId = order.OrderId,
                PlanName        = pricing.DisplayName,
                Status          = "Pending",
                Grade           = req.Grade,
                Subjects        = isChampion ? "All" : string.Join(",", req.Subjects),
                Days            = pricing.Days,
                CreatedAt       = DateTime.UtcNow
            };
            _db.PaymentTransactions.Add(transaction);
            await _db.SaveChangesAsync(ct);

            return Ok(new
            {
                orderId         = order.OrderId,
                keyId           = _razorpay.KeyId,
                amount          = pricing.AmountInPaise,
                currency        = pricing.Currency,
                planName        = req.BillingCycle,
                planDisplayName = pricing.DisplayName
            });
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
    }

    [HttpPost("verify")]
    public async Task<IActionResult> Verify([FromBody] VerifyPaymentRequest req, CancellationToken ct)
    {
        if (!_razorpay.VerifySignature(req.OrderId, req.PaymentId, req.Signature))
        {
            _log.LogWarning("Razorpay signature mismatch for order {OrderId}", req.OrderId);
            return BadRequest("Signature verification failed.");
        }

        var transaction = await _db.PaymentTransactions.FirstOrDefaultAsync(t => t.RazorpayOrderId == req.OrderId, ct);
        if (transaction == null)
            return NotFound("Order not found.");

        if (transaction.Status == "Success")
            return Ok(new { success = true, message = "Payment already processed successfully." });

        var user        = await _users.GetOrSyncAsync(User, ct);
        var rawSubjects = transaction.Subjects?.Split(',').ToList() ?? new List<string>();

        // Champion "All" sentinel → expand to every subject for the grade
        var subjects = rawSubjects.Contains("All", StringComparer.OrdinalIgnoreCase)
            ? AllSubjectsForGrade(transaction.Grade)
            : rawSubjects;

        foreach (var subject in subjects)
        {
            int pricePerSubject = transaction.AmountInPaise / (subjects.Count > 0 ? subjects.Count : 1);
            await _subs.UnlockSubjectAsync(user.UserId, transaction.Grade, subject, transaction.Days, pricePerSubject, req.OrderId, req.PaymentId, ct);
        }

        transaction.Status = "Success";
        transaction.RazorpayPaymentId = req.PaymentId;
        await _db.SaveChangesAsync(ct);

        _log.LogInformation(
            "User {UserId} upgraded to {DisplayName} for {Days} days via order {OrderId}",
            user.UserId, transaction.PlanName, transaction.Days, req.OrderId);

        // Run email sending in background so it doesn't delay the checkout response
        var emailStr = user.Email;
        var nameStr = user.FullName ?? "User";
        var planStr = transaction.PlanName ?? "";
        var amt = transaction.AmountInPaise;
        var subjs = subjects;
        
        var scopeFactory = HttpContext.RequestServices.GetRequiredService<IServiceScopeFactory>();

        _ = Task.Run(async () =>
        {
            try
            {
                using var scope = scopeFactory.CreateScope();
                var emailSvc = scope.ServiceProvider.GetRequiredService<IEmailService>();
                await emailSvc.SendSubscriptionReceiptAsync(emailStr, nameStr, planStr, amt, subjs);
            }
            catch (Exception ex)
            {
                // Log failed email (cannot use _log because it might be scoped and disposed)
                Console.WriteLine($"Failed to send receipt email: {ex.Message}");
            }
        });

        return Ok(new
        {
            success = true,
            planName = transaction.PlanName
        });
    }
}
