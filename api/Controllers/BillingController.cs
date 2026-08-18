using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
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

        bool onSchoolPilot = await _subs.IsSchoolPilotActiveAsync(user.UserId, ct);
        var schoolInfo = onSchoolPilot
            ? await _db.Users.Include(u => u.School)
                .Where(u => u.UserId == user.UserId)
                .Select(u => u.School == null ? null : new { u.School.Name, u.School.LogoUrl, u.School.PilotEndsAt })
                .FirstOrDefaultAsync(ct)
            : null;

        string tier = subscriptions.Any(s => s.isActive) ? "Modular" : (onSchoolPilot ? "School" : "Free");

        return Ok(new
        {
            currentTier   = tier,
            onSchoolPilot,
            school        = schoolInfo,
            freeAttemptsUsed = user.FreeAttemptsUsed,
            freeAttemptsLimit = SubscriptionService.GetEffectiveLimit(user),
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

    // ── Razorpay webhook ──────────────────────────────────────────────────────
    // Safety net: if the client-side /verify call fails (browser closes, network
    // drop), Razorpay retries this endpoint server-to-server until we return 200.
    // Configure the webhook URL in Razorpay Dashboard → Webhooks → payment.captured
    // and set Razorpay:WebhookSecret in app settings to the webhook secret shown there.
    [HttpPost("webhook")]
    [AllowAnonymous]
    public async Task<IActionResult> Webhook(CancellationToken ct)
    {
        var webhookSecret = _razorpay.WebhookSecret;
        if (string.IsNullOrEmpty(webhookSecret))
        {
            _log.LogWarning("Razorpay webhook received but WebhookSecret is not configured — skipping.");
            return Ok(); // Return 200 so Razorpay doesn't keep retrying
        }

        // Read raw body for signature verification
        Request.EnableBuffering();
        using var reader = new System.IO.StreamReader(Request.Body, leaveOpen: true);
        var rawBody = await reader.ReadToEndAsync(ct);
        Request.Body.Position = 0;

        // Verify signature: HMAC-SHA256(webhookSecret, rawBody)
        var signature = Request.Headers["X-Razorpay-Signature"].FirstOrDefault() ?? "";
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(webhookSecret));
        var computed = Convert.ToHexString(hmac.ComputeHash(Encoding.UTF8.GetBytes(rawBody))).ToLowerInvariant();
        if (!CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes(computed), Encoding.UTF8.GetBytes(signature.ToLowerInvariant())))
        {
            _log.LogWarning("Razorpay webhook signature mismatch — ignoring.");
            return Ok(); // Still 200 to avoid Razorpay thinking it's a server error
        }

        JsonDocument doc;
        try { doc = JsonDocument.Parse(rawBody); }
        catch { return Ok(); }

        using (doc)
        {
            var eventType = doc.RootElement.TryGetProperty("event", out var ev) ? ev.GetString() : null;
            if (eventType != "payment.captured") return Ok(); // Only handle captures

            // Extract orderId from payment entity
            string? orderId = null;
            string? paymentId = null;
            if (doc.RootElement.TryGetProperty("payload", out var payload) &&
                payload.TryGetProperty("payment", out var paymentWrapper) &&
                paymentWrapper.TryGetProperty("entity", out var entity))
            {
                orderId  = entity.TryGetProperty("order_id",  out var o) ? o.GetString() : null;
                paymentId = entity.TryGetProperty("id",        out var p) ? p.GetString() : null;
            }

            if (string.IsNullOrEmpty(orderId) || string.IsNullOrEmpty(paymentId))
            {
                _log.LogWarning("Webhook: could not extract orderId/paymentId from payload.");
                return Ok();
            }

            var transaction = await _db.PaymentTransactions.FirstOrDefaultAsync(t => t.RazorpayOrderId == orderId, ct);
            if (transaction == null)
            {
                _log.LogWarning("Webhook: no PaymentTransaction found for orderId {OrderId}", orderId);
                return Ok();
            }

            if (transaction.Status == "Success")
            {
                _log.LogInformation("Webhook: order {OrderId} already processed — skipping.", orderId);
                return Ok();
            }

            // Look up the user
            var user = await _db.Users.FindAsync(new object[] { transaction.UserId }, ct);
            if (user == null)
            {
                _log.LogError("Webhook: user {UserId} not found for order {OrderId}", transaction.UserId, orderId);
                return Ok();
            }

            var rawSubjects = transaction.Subjects?.Split(',').ToList() ?? new List<string>();
            var subjects = rawSubjects.Contains("All", StringComparer.OrdinalIgnoreCase)
                ? AllSubjectsForGrade(transaction.Grade)
                : rawSubjects;

            foreach (var subject in subjects)
            {
                int pricePerSubject = transaction.AmountInPaise / (subjects.Count > 0 ? subjects.Count : 1);
                await _subs.UnlockSubjectAsync(user.UserId, transaction.Grade, subject, transaction.Days, pricePerSubject, orderId, paymentId, ct);
            }

            transaction.Status = "Success";
            transaction.RazorpayPaymentId = paymentId;
            await _db.SaveChangesAsync(ct);

            _log.LogInformation("Webhook: unlocked {Plan} for user {UserId} via order {OrderId}", transaction.PlanName, user.UserId, orderId);

            // Send receipt email in background
            var emailStr  = user.Email;
            var nameStr   = user.FullName ?? "User";
            var planStr   = transaction.PlanName ?? "";
            var amt       = transaction.AmountInPaise;
            var subjs     = subjects;
            var scopeFactory = HttpContext.RequestServices.GetRequiredService<IServiceScopeFactory>();
            _ = Task.Run(async () =>
            {
                try
                {
                    using var scope = scopeFactory.CreateScope();
                    var emailSvc = scope.ServiceProvider.GetRequiredService<IEmailService>();
                    await emailSvc.SendSubscriptionReceiptAsync(emailStr, nameStr, planStr, amt, subjs);
                }
                catch (Exception ex) { Console.WriteLine($"Webhook receipt email failed: {ex.Message}"); }
            });
        }

        return Ok();
    }
}
