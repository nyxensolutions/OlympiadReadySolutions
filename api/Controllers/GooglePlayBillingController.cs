using System.Text;
using System.Text.Json;
using Google;
using Google.Apis.AndroidPublisher.v3.Data;
using Google.Apis.Auth;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

/// <summary>
/// Google Play subscriptions for the Android app. Flow:
/// 1. app calls /prepare → server records a pending order and says which product/base plan to buy;
/// 2. app buys it with obfuscatedAccountId = user id, obfuscatedProfileId = transaction id;
/// 3. app calls /verify with the purchase token → server checks with Google, unlocks, acknowledges;
/// 4. Google Real-time Developer Notifications (Pub/Sub push to /rtdn) keep renewals, cancellations
///    and refunds in sync. Every path re-reads the purchase from Google, so clients can't forge state.
/// </summary>
[ApiController]
[Authorize]
[Route("api/billing/google")]
public class GooglePlayBillingController : ControllerBase
{
    private const string Provider = "GooglePlay";

    private readonly AppDbContext _db;
    private readonly UserService _users;
    private readonly SubscriptionService _subs;
    private readonly RazorpayService _pricing;
    private readonly GooglePlayService _play;
    private readonly IConfiguration _config;
    private readonly ILogger<GooglePlayBillingController> _log;

    public GooglePlayBillingController(
        AppDbContext db,
        UserService users,
        SubscriptionService subs,
        RazorpayService pricing,
        GooglePlayService play,
        IConfiguration config,
        ILogger<GooglePlayBillingController> log)
    {
        _db = db;
        _users = users;
        _subs = subs;
        _pricing = pricing;
        _play = play;
        _config = config;
        _log = log;
    }

    [HttpPost("prepare")]
    public async Task<IActionResult> Prepare([FromBody] CheckoutRequest req, CancellationToken ct)
    {
        if (!_play.IsConfigured)
            return Problem("Google Play billing is not configured on the server.", statusCode: 503);
        if (req.Grade is < 1 or > 12)
            return BadRequest("Invalid class.");
        if (req.Subjects == null || req.Subjects.Count == 0)
            return BadRequest("At least one subject must be selected.");

        var user = await _users.GetOrSyncAsync(User, ct);
        bool isChampion = req.Subjects.Contains("All", StringComparer.OrdinalIgnoreCase);
        var gradeSubjects = BillingController.AllSubjectsForGrade(req.Grade);

        if (!isChampion)
        {
            var unknown = req.Subjects.FirstOrDefault(s => !gradeSubjects.Contains(s, StringComparer.OrdinalIgnoreCase));
            if (unknown != null)
                return BadRequest($"{unknown} is not available for Class {req.Grade}.");
            if (req.Subjects.Distinct(StringComparer.OrdinalIgnoreCase).Count() != req.Subjects.Count)
                return BadRequest("Each subject can only be selected once.");
        }

        var subjectsToCheck = isChampion ? gradeSubjects : req.Subjects;
        var alreadyActive = new List<string>();
        foreach (var subject in subjectsToCheck)
        {
            if (await _subs.HasUnlockedSubjectAsync(user.UserId, req.Grade, subject, ct))
                alreadyActive.Add(subject);
        }
        if (!isChampion && alreadyActive.Count > 0)
            return BadRequest($"You already have an active subscription for Class {req.Grade} {alreadyActive[0]}.");
        if (isChampion && alreadyActive.Count == subjectsToCheck.Count)
            return BadRequest($"You already have an active Champion subscription for Class {req.Grade}.");

        bool isAnnual = string.Equals(req.BillingCycle, "Annual", StringComparison.OrdinalIgnoreCase);
        var pricing = _pricing.CalculatePrice(req.BillingCycle, req.Subjects);

        var tx = new PaymentTransaction
        {
            UserId = user.UserId,
            Provider = Provider,
            AmountInPaise = pricing.AmountInPaise,
            Currency = pricing.Currency,
            PlanName = pricing.DisplayName,
            Status = "Pending",
            Grade = req.Grade,
            Subjects = isChampion ? "All" : string.Join(",", req.Subjects),
            Days = pricing.Days,
            GoogleProductId = GooglePlayService.ProductIdFor(isChampion, req.Subjects.Count),
            GoogleBasePlanId = GooglePlayService.BasePlanIdFor(isAnnual),
            CreatedAt = DateTime.UtcNow,
        };
        _db.PaymentTransactions.Add(tx);
        await _db.SaveChangesAsync(ct);

        return Ok(new
        {
            productId = tx.GoogleProductId,
            basePlanId = tx.GoogleBasePlanId,
            obfuscatedAccountId = user.UserId.ToString("N"),
            obfuscatedProfileId = tx.TransactionId.ToString("N"),
            amountInPaise = tx.AmountInPaise,
            planDisplayName = tx.PlanName,
        });
    }

    [HttpPost("verify")]
    public async Task<IActionResult> Verify([FromBody] GooglePlayVerifyRequest req, CancellationToken ct)
    {
        if (!_play.IsConfigured)
            return Problem("Google Play billing is not configured on the server.", statusCode: 503);
        if (string.IsNullOrWhiteSpace(req.PurchaseToken))
            return BadRequest("Missing purchase token.");

        var user = await _users.GetOrSyncAsync(User, ct);

        SubscriptionPurchaseV2 purchase;
        try
        {
            purchase = await _play.GetSubscriptionAsync(req.PurchaseToken, ct);
        }
        catch (GoogleApiException ex) when (ex.HttpStatusCode is System.Net.HttpStatusCode.NotFound or System.Net.HttpStatusCode.BadRequest or System.Net.HttpStatusCode.Gone)
        {
            _log.LogWarning("Google Play rejected purchase token for user {UserId}: {Message}", user.UserId, ex.Message);
            return BadRequest("This purchase could not be found on Google Play.");
        }

        var result = await SyncPurchaseAsync(req.PurchaseToken, purchase, user.UserId, ct);
        return result.Outcome switch
        {
            SyncOutcome.Granted => Ok(new { success = true, planName = result.PlanName, endDate = result.EndDateUtc }),
            SyncOutcome.Pending => Accepted(new { success = false, pending = true, message = "Your payment is pending. Your plan will start as soon as Google Play confirms it." }),
            SyncOutcome.NotActive => Ok(new { success = false, message = "This subscription is no longer active." }),
            SyncOutcome.WrongAccount => StatusCode(403, "This purchase belongs to a different OlympiadReady account."),
            _ => NotFound("We couldn't match this purchase to an order. Please contact support@olympiadready.com."),
        };
    }

    /// <summary>
    /// Google Play Real-time Developer Notifications, delivered by a Cloud Pub/Sub push subscription.
    /// </summary>
    [HttpPost("rtdn")]
    [AllowAnonymous]
    public async Task<IActionResult> Rtdn([FromBody] PubSubPushEnvelope envelope, CancellationToken ct)
    {
        if (!await IsAuthenticPubSubPushAsync())
            return Unauthorized();

        var data = envelope.Message?.Data;
        if (string.IsNullOrEmpty(data))
            return Ok();

        string? token;
        try
        {
            using var doc = JsonDocument.Parse(Encoding.UTF8.GetString(Convert.FromBase64String(data)));
            var root = doc.RootElement;

            if (root.TryGetProperty("packageName", out var pkg) && pkg.GetString() != _play.PackageName)
                return Ok();
            if (root.TryGetProperty("testNotification", out _))
            {
                _log.LogInformation("Google Play RTDN test notification received.");
                return Ok();
            }
            if (!root.TryGetProperty("subscriptionNotification", out var sn))
                return Ok();

            token = sn.TryGetProperty("purchaseToken", out var t) ? t.GetString() : null;
        }
        catch (Exception ex) when (ex is FormatException or JsonException)
        {
            _log.LogWarning(ex, "Unreadable Google Play RTDN payload — acknowledging to stop retries.");
            return Ok();
        }

        if (string.IsNullOrEmpty(token) || !_play.IsConfigured)
            return Ok();

        SubscriptionPurchaseV2 purchase;
        try
        {
            purchase = await _play.GetSubscriptionAsync(token, ct);
        }
        catch (GoogleApiException ex) when (ex.HttpStatusCode is System.Net.HttpStatusCode.NotFound or System.Net.HttpStatusCode.Gone)
        {
            _log.LogWarning("RTDN for a purchase token Google no longer knows: {Message}", ex.Message);
            return Ok();
        }

        var result = await SyncPurchaseAsync(token, purchase, expectedUserId: null, ct);
        _log.LogInformation("Google Play RTDN processed: {Outcome}", result.Outcome);
        // Non-2xx makes Pub/Sub retry; only transient failures (thrown above) should do that.
        return Ok();
    }

    private enum SyncOutcome { Granted, Pending, NotActive, WrongAccount, NoMatch }

    private record SyncResult(SyncOutcome Outcome, string? PlanName = null, DateTime? EndDateUtc = null);

    private async Task<SyncResult> SyncPurchaseAsync(
        string token, SubscriptionPurchaseV2 purchase, Guid? expectedUserId, CancellationToken ct)
    {
        var ids = purchase.ExternalAccountIdentifiers;
        if (!Guid.TryParseExact(ids?.ObfuscatedExternalAccountId, "N", out var accountUserId))
        {
            _log.LogWarning("Google Play purchase without our account id — cannot match it.");
            return new SyncResult(SyncOutcome.NoMatch);
        }
        if (expectedUserId.HasValue && expectedUserId.Value != accountUserId)
            return new SyncResult(SyncOutcome.WrongAccount);

        var tx = await _db.PaymentTransactions
            .Where(t => t.Provider == Provider && t.GooglePurchaseToken == token)
            .OrderBy(t => t.CreatedAt)
            .FirstOrDefaultAsync(ct);
        if (tx == null && Guid.TryParseExact(ids?.ObfuscatedExternalProfileId, "N", out var txId))
            tx = await _db.PaymentTransactions.FirstOrDefaultAsync(t => t.TransactionId == txId && t.Provider == Provider, ct);

        if (tx == null || tx.UserId != accountUserId)
        {
            _log.LogWarning("No pending Google Play order matches purchase for user {UserId}.", accountUserId);
            return new SyncResult(SyncOutcome.NoMatch);
        }

        var lineItem = purchase.LineItems?.FirstOrDefault();
        if (lineItem == null || lineItem.ProductId != tx.GoogleProductId ||
            (lineItem.OfferDetails?.BasePlanId is { } basePlan && basePlan != tx.GoogleBasePlanId))
        {
            _log.LogWarning("Google Play product {ProductId} does not match order {TxId} ({Expected}).",
                lineItem?.ProductId, tx.TransactionId, tx.GoogleProductId);
            return new SyncResult(SyncOutcome.NoMatch);
        }

        var state = purchase.SubscriptionState;
        if (state == "SUBSCRIPTION_STATE_PENDING")
            return new SyncResult(SyncOutcome.Pending);

        // CANCELED still has access until expiry; ON_HOLD/PAUSED/EXPIRED do not.
        bool hasAccess = state is "SUBSCRIPTION_STATE_ACTIVE" or "SUBSCRIPTION_STATE_IN_GRACE_PERIOD" or "SUBSCRIPTION_STATE_CANCELED";
        DateTime expiry = lineItem.ExpiryTimeDateTimeOffset?.UtcDateTime ?? DateTime.UtcNow;
        DateTime endDate = hasAccess ? expiry : DateTime.UtcNow;
        bool autoRenewing = hasAccess && lineItem.AutoRenewingPlan?.AutoRenewEnabled == true;

        var rawSubjects = tx.Subjects?.Split(',').ToList() ?? new List<string>();
        var subjects = rawSubjects.Contains("All", StringComparer.OrdinalIgnoreCase)
            ? BillingController.AllSubjectsForGrade(tx.Grade)
            : rawSubjects;

        bool firstGrant = tx.Status != "Success";
        if (firstGrant)
        {
            if (!hasAccess)
                return new SyncResult(SyncOutcome.NotActive);
            tx.Status = "Success";
            tx.GooglePurchaseToken = token;
            tx.GoogleOrderId = lineItem.LatestSuccessfulOrderId;
        }
        else if (!string.IsNullOrEmpty(lineItem.LatestSuccessfulOrderId) && lineItem.LatestSuccessfulOrderId != tx.GoogleOrderId &&
                 !await _db.PaymentTransactions.AnyAsync(t => t.GoogleOrderId == lineItem.LatestSuccessfulOrderId, ct))
        {
            _db.PaymentTransactions.Add(new PaymentTransaction
            {
                UserId = tx.UserId,
                Provider = Provider,
                AmountInPaise = tx.AmountInPaise,
                Currency = tx.Currency,
                PlanName = tx.PlanName,
                Status = "Success",
                Grade = tx.Grade,
                Subjects = tx.Subjects,
                Days = tx.Days,
                GoogleProductId = tx.GoogleProductId,
                GoogleBasePlanId = tx.GoogleBasePlanId,
                GooglePurchaseToken = token,
                GoogleOrderId = lineItem.LatestSuccessfulOrderId,
                CreatedAt = DateTime.UtcNow,
            });
        }

        await _subs.SyncGooglePlayEntitlementAsync(
            tx.UserId, tx.Grade, subjects, token, endDate, autoRenewing, tx.AmountInPaise, ct);

        if (hasAccess && purchase.AcknowledgementState == "ACKNOWLEDGEMENT_STATE_PENDING")
        {
            // Google refunds unacknowledged purchases after 3 days.
            await _play.AcknowledgeAsync(lineItem.ProductId, token, ct);
        }

        if (firstGrant)
            SendReceiptInBackground(tx, subjects);

        return hasAccess
            ? new SyncResult(SyncOutcome.Granted, tx.PlanName, endDate)
            : new SyncResult(SyncOutcome.NotActive);
    }

    private void SendReceiptInBackground(PaymentTransaction tx, List<string> subjects)
    {
        var scopeFactory = HttpContext.RequestServices.GetRequiredService<IServiceScopeFactory>();
        var userId = tx.UserId;
        var plan = tx.PlanName ?? "";
        var amount = tx.AmountInPaise;
        _ = Task.Run(async () =>
        {
            try
            {
                using var scope = scopeFactory.CreateScope();
                var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
                var user = await db.Users.FindAsync(userId);
                if (user == null) return;
                var email = scope.ServiceProvider.GetRequiredService<IEmailService>();
                await email.SendSubscriptionReceiptAsync(user.Email, user.FullName ?? "User", plan, amount, subjects);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Google Play receipt email failed: {ex.Message}");
            }
        });
    }

    /// <summary>
    /// When GooglePlay:RtdnAudience is set, require the OIDC token Pub/Sub attaches to push requests
    /// (and, if set, that it was minted for GooglePlay:RtdnServiceAccountEmail).
    /// </summary>
    private async Task<bool> IsAuthenticPubSubPushAsync()
    {
        var audience = _config["GooglePlay:RtdnAudience"];
        if (string.IsNullOrWhiteSpace(audience))
            return true;

        var header = Request.Headers.Authorization.FirstOrDefault();
        if (header == null || !header.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase))
            return false;

        try
        {
            var payload = await GoogleJsonWebSignature.ValidateAsync(
                header["Bearer ".Length..],
                new GoogleJsonWebSignature.ValidationSettings { Audience = new[] { audience } });
            var expectedEmail = _config["GooglePlay:RtdnServiceAccountEmail"];
            return string.IsNullOrWhiteSpace(expectedEmail) ||
                   (payload.EmailVerified && string.Equals(payload.Email, expectedEmail, StringComparison.OrdinalIgnoreCase));
        }
        catch (InvalidJwtException ex)
        {
            _log.LogWarning("Rejected Google Play RTDN push with invalid token: {Message}", ex.Message);
            return false;
        }
    }
}

public class GooglePlayVerifyRequest
{
    public string PurchaseToken { get; set; } = "";
}

public class PubSubPushEnvelope
{
    public PubSubMessage? Message { get; set; }
    public string? Subscription { get; set; }
}

public class PubSubMessage
{
    public string? Data { get; set; }
    public string? MessageId { get; set; }
}
