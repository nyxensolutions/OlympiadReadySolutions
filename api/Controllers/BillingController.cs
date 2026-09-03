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
                razorpaySubscriptionId = s.RazorpaySubscriptionId,
                isAutoRenewing    = s.IsAutoRenewing,
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
            
            string interval = string.Equals(req.BillingCycle, "Annual", StringComparison.OrdinalIgnoreCase) ? "yearly" : "monthly";
            var planId = await _razorpay.CreateDynamicPlanAsync(pricing.AmountInPaise, pricing.Currency, interval, pricing.DisplayName, ct);
            
            var subId = await _razorpay.CreateSubscriptionAsync(planId, user.UserId, pricing.DisplayName, ct);

            var transaction = new OlympiadReady.Api.Data.Entities.PaymentTransaction
            {
                UserId          = user.UserId,
                AmountInPaise   = pricing.AmountInPaise,
                Currency        = pricing.Currency,
                RazorpaySubscriptionId = subId,
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
                subscriptionId  = subId,
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
        bool isSubscription = !string.IsNullOrEmpty(req.SubscriptionId);
        string idToVerify = isSubscription ? req.SubscriptionId! : req.OrderId!;

        bool sigValid = isSubscription
            ? _razorpay.VerifySubscriptionSignature(idToVerify, req.PaymentId, req.Signature)
            : _razorpay.VerifySignature(idToVerify, req.PaymentId, req.Signature);

        if (!sigValid)
        {
            _log.LogWarning("Razorpay signature mismatch for id {Id}", idToVerify);
            return BadRequest("Signature verification failed.");
        }

        var transaction = isSubscription
            ? await _db.PaymentTransactions.FirstOrDefaultAsync(t => t.RazorpaySubscriptionId == idToVerify, ct)
            : await _db.PaymentTransactions.FirstOrDefaultAsync(t => t.RazorpayOrderId == idToVerify, ct);

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

        int totalPaise = transaction.AmountInPaise;
        int count = subjects.Count > 0 ? subjects.Count : 1;
        int basePrice = totalPaise / count;
        int remainder = totalPaise % count;

        for (int i = 0; i < subjects.Count; i++)
        {
            var subject = subjects[i];
            int priceForThisSubject = basePrice + (i == 0 ? remainder : 0);
            await _subs.UnlockSubjectAsync(user.UserId, transaction.Grade, subject, transaction.Days, priceForThisSubject, req.OrderId, req.PaymentId, req.SubscriptionId, isSubscription, ct);
        }

        transaction.Status = "Success";
        transaction.RazorpayPaymentId = req.PaymentId;
        await _db.SaveChangesAsync(ct);

        _log.LogInformation(
            "User {UserId} upgraded to {DisplayName} for {Days} days via payment {PaymentId}",
            user.UserId, transaction.PlanName, transaction.Days, req.PaymentId);

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

            if (eventType == "payment.captured")
            {
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

                var user = await _db.Users.FindAsync(new object[] { transaction.UserId }, ct);
                if (user == null) return Ok();

                var rawSubjects = transaction.Subjects?.Split(',').ToList() ?? new List<string>();
                var subjects = rawSubjects.Contains("All", StringComparer.OrdinalIgnoreCase)
                    ? AllSubjectsForGrade(transaction.Grade)
                    : rawSubjects;

                foreach (var subject in subjects)
                {
                    int pricePerSubject = transaction.AmountInPaise / (subjects.Count > 0 ? subjects.Count : 1);
                    await _subs.UnlockSubjectAsync(user.UserId, transaction.Grade, subject, transaction.Days, pricePerSubject, orderId, paymentId, null, false, ct);
                }

                transaction.Status = "Success";
                transaction.RazorpayPaymentId = paymentId;
                await _db.SaveChangesAsync(ct);

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
            else if (eventType == "subscription.charged")
            {
                if (doc.RootElement.TryGetProperty("payload", out var payload) &&
                    payload.TryGetProperty("subscription", out var subWrapper) &&
                    subWrapper.TryGetProperty("entity", out var entity) &&
                    payload.TryGetProperty("payment", out var pWrapper) &&
                    pWrapper.TryGetProperty("entity", out var pEntity))
                {
                    var subId = entity.TryGetProperty("id", out var s) ? s.GetString() : null;
                    var paymentId = pEntity.TryGetProperty("id", out var p) ? p.GetString() : null;

                    if (!string.IsNullOrEmpty(subId) && !string.IsNullOrEmpty(paymentId))
                    {
                        // Check if we already processed this payment ID (e.g. from the initial /verify call)
                        var existingTx = await _db.PaymentTransactions.FirstOrDefaultAsync(t => t.RazorpayPaymentId == paymentId, ct);
                        if (existingTx != null)
                        {
                            return Ok();
                        }

                        // This is an auto-renewal charge!
                        var originalTx = await _db.PaymentTransactions
                            .Where(t => t.RazorpaySubscriptionId == subId)
                            .OrderByDescending(t => t.CreatedAt)
                            .FirstOrDefaultAsync(ct);

                        if (originalTx != null)
                        {
                            var newTx = new OlympiadReady.Api.Data.Entities.PaymentTransaction
                            {
                                UserId = originalTx.UserId,
                                AmountInPaise = originalTx.AmountInPaise,
                                Currency = originalTx.Currency,
                                RazorpaySubscriptionId = subId,
                                RazorpayPaymentId = paymentId,
                                PlanName = originalTx.PlanName,
                                Status = "Success",
                                Grade = originalTx.Grade,
                                Subjects = originalTx.Subjects,
                                Days = originalTx.Days,
                                CreatedAt = DateTime.UtcNow
                            };
                            _db.PaymentTransactions.Add(newTx);

                            var user = await _db.Users.FindAsync(new object[] { originalTx.UserId }, ct);
                            if (user != null)
                            {
                                var rawSubjects = originalTx.Subjects?.Split(',').ToList() ?? new List<string>();
                                var subjects = rawSubjects.Contains("All", StringComparer.OrdinalIgnoreCase)
                                    ? AllSubjectsForGrade(originalTx.Grade)
                                    : rawSubjects;

                                int totalPaise = originalTx.AmountInPaise;
                                int count = subjects.Count > 0 ? subjects.Count : 1;
                                int basePrice = totalPaise / count;
                                int remainder = totalPaise % count;

                                for (int i = 0; i < subjects.Count; i++)
                                {
                                    var subject = subjects[i];
                                    int priceForThisSubject = basePrice + (i == 0 ? remainder : 0);
                                    await _subs.UnlockSubjectAsync(user.UserId, originalTx.Grade, subject, originalTx.Days, priceForThisSubject, null, paymentId, subId, true, ct);
                                }
                                await _db.SaveChangesAsync(ct);

                                var emailStr  = user.Email;
                                var nameStr   = user.FullName ?? "User";
                                var planStr   = originalTx.PlanName ?? "";
                                var amt       = originalTx.AmountInPaise;
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
                                    catch (Exception ex) { Console.WriteLine($"Webhook renewal receipt email failed: {ex.Message}"); }
                                });
                            }
                        }
                    }
                }
            }
            else if (eventType == "subscription.cancelled" || eventType == "subscription.halted")
            {
                if (doc.RootElement.TryGetProperty("payload", out var payload) &&
                    payload.TryGetProperty("subscription", out var subWrapper) &&
                    subWrapper.TryGetProperty("entity", out var entity))
                {
                    var subId = entity.TryGetProperty("id", out var s) ? s.GetString() : null;
                    if (!string.IsNullOrEmpty(subId))
                    {
                        var activeSubs = await _db.Subscriptions
                            .Where(s => s.RazorpaySubscriptionId == subId && s.IsAutoRenewing)
                            .ToListAsync(ct);
                        foreach (var sub in activeSubs)
                        {
                            sub.IsAutoRenewing = false;
                        }
                        await _db.SaveChangesAsync(ct);
                    }
                }
            }
        }

        return Ok();
    }

    [HttpPost("cancel-subscription")]
    public async Task<IActionResult> CancelSubscription([FromBody] CancelSubscriptionRequest req, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        
        var activeSubs = await _db.Subscriptions
            .Where(s => s.UserId == user.UserId && s.RazorpaySubscriptionId == req.SubscriptionId && s.IsAutoRenewing)
            .ToListAsync(ct);

        if (activeSubs.Count == 0)
            return NotFound("Active auto-renewing subscription not found.");

        try
        {
            await _razorpay.CancelSubscriptionAsync(req.SubscriptionId, ct);
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Failed to cancel subscription {SubId} with Razorpay", req.SubscriptionId);
            return StatusCode(500, "Failed to cancel with payment provider.");
        }

        foreach (var sub in activeSubs)
        {
            sub.IsAutoRenewing = false;
        }

        await _db.SaveChangesAsync(ct);
        
        var planName = activeSubs.FirstOrDefault()?.PlanName ?? "Subject";
        await _emailService.SendSubscriptionCancelledAsync(user.Email, user.FullName ?? "Student", planName);

        return Ok(new { success = true });
    }
}

public class CancelSubscriptionRequest
{
    [System.ComponentModel.DataAnnotations.Required]
    public string SubscriptionId { get; set; } = "";
}
