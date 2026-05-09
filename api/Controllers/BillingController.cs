using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Authorize]
[Route("api/billing")]
public class BillingController : ControllerBase
{
    private readonly UserService _users;
    private readonly SubscriptionService _subs;
    private readonly RazorpayService _razorpay;
    private readonly ILogger<BillingController> _log;

    public BillingController(
        UserService users,
        SubscriptionService subs,
        RazorpayService razorpay,
        ILogger<BillingController> log)
    {
        _users = users;
        _subs = subs;
        _razorpay = razorpay;
        _log = log;
    }

    [HttpGet("me")]
    public async Task<IActionResult> Me(CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        var quota = await _subs.CheckPaperQuotaAsync(user.UserId, ct);
        return Ok(new
        {
            tier = quota.Tier,
            used = quota.Used,
            limit = quota.Limit,
            allowed = quota.Allowed
        });
    }

    [HttpPost("checkout")]
    public async Task<IActionResult> Checkout([FromBody] CheckoutRequest req, CancellationToken ct)
    {
        if (!_razorpay.IsConfigured)
            return Problem("Razorpay is not configured on the server.", statusCode: 503);

        var user = await _users.GetOrSyncAsync(User, ct);

        try
        {
            var plan = _razorpay.GetPlan(req.Plan);
            var order = await _razorpay.CreateOrderAsync(req.Plan, user.UserId, ct);
            return Ok(new
            {
                orderId = order.OrderId,
                keyId = _razorpay.KeyId,
                amount = order.AmountInPaise,
                currency = order.Currency,
                planName = req.Plan,
                planDisplayName = plan.DisplayName
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

        var plan = _razorpay.GetPlan(req.Plan);
        var user = await _users.GetOrSyncAsync(User, ct);
        await _subs.ActivateProAsync(user.UserId, plan.Days, ct);

        _log.LogInformation(
            "User {UserId} upgraded to {Plan} for {Days} days via order {OrderId}",
            user.UserId, req.Plan, plan.Days, req.OrderId);

        return Ok(new
        {
            tier = "Pro",
            planName = req.Plan,
            days = plan.Days
        });
    }
}
