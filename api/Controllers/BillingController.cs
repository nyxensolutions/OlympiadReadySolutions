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

    [HttpPost("checkout")]
    public async Task<IActionResult> Checkout([FromBody] CheckoutRequest req, CancellationToken ct)
    {
        if (!_razorpay.IsConfigured)
            return Problem("Razorpay is not configured on the server.", statusCode: 503);

        if (req.Subjects == null || req.Subjects.Count == 0)
            return BadRequest("At least one subject must be selected.");

        var user = await _users.GetOrSyncAsync(User, ct);

        foreach (var subject in req.Subjects)
        {
            bool hasActive = await _subs.HasUnlockedSubjectAsync(user.UserId, req.Grade, subject, ct);
            if (hasActive)
            {
                return BadRequest($"You already have an active subscription for Class {req.Grade} {subject}. You do not need to buy it again.");
            }
        }

        try
        {
            var pricing = _razorpay.CalculatePrice(req.BillingCycle, req.Subjects);
            var order = await _razorpay.CreateDynamicOrderAsync(pricing.AmountInPaise, pricing.Currency, pricing.DisplayName, user.UserId, ct);
            
            return Ok(new
            {
                orderId = order.OrderId,
                keyId = _razorpay.KeyId,
                amount = pricing.AmountInPaise,
                currency = pricing.Currency,
                planName = req.BillingCycle, // Useful for the frontend to track
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

        var pricing = _razorpay.CalculatePrice(req.BillingCycle, req.Subjects);
        var user = await _users.GetOrSyncAsync(User, ct);

        // Unlock all passed subjects
        foreach (var subject in req.Subjects)
        {
            // Divide the total amount evenly across subjects so each has its own valid price history,
            // or just use total amount on the first one and 0 on others?
            // Actually, dividing them gives a fair representation in the history per subject.
            int pricePerSubject = pricing.AmountInPaise / req.Subjects.Count;
            await _subs.UnlockSubjectAsync(user.UserId, req.Grade, subject, pricing.Days, pricePerSubject, req.OrderId, req.PaymentId, ct);
        }

        _log.LogInformation(
            "User {UserId} upgraded to {DisplayName} for {Days} days via order {OrderId}",
            user.UserId, pricing.DisplayName, pricing.Days, req.OrderId);

        // Run email sending in background so it doesn't delay the checkout response
        // We resolve a new scope because the current one might get disposed when the request ends.
        var emailStr = user.Email;
        var nameStr = user.FullName ?? "User";
        var planStr = pricing.DisplayName;
        var amt = pricing.AmountInPaise;
        var subjs = req.Subjects.ToList();

        // Get an IServiceProvider reference before background task starts
        var serviceProvider = HttpContext.RequestServices;

        _ = Task.Run(async () =>
        {
            try
            {
                using var scope = serviceProvider.CreateScope();
                var emailSvc = scope.ServiceProvider.GetRequiredService<IEmailService>();
                await emailSvc.SendSubscriptionReceiptAsync(
                    emailStr, 
                    nameStr, 
                    planStr, 
                    amt, 
                    subjs
                );
            }
            catch (Exception ex)
            {
                _log.LogError(ex, "Failed to send receipt email in background.");
            }
        });

        return Ok(new
        {
            tier = "Modular",
            planName = pricing.DisplayName,
            days = pricing.Days
        });
    }
}
