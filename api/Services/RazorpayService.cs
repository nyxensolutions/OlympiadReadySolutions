using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json.Serialization;

namespace OlympiadReady.Api.Services;

public class RazorpayService
{
    public record PlanConfig(int AmountInPaise, string Currency, int Days, string DisplayName);

    public record OrderResult(string OrderId, int AmountInPaise, string Currency);

    private readonly HttpClient _http;
    private readonly ILogger<RazorpayService> _log;
    private readonly string _keyId;
    private readonly string _keySecret;
    private readonly Dictionary<string, PlanConfig> _plans;

    public RazorpayService(HttpClient http, IConfiguration config, ILogger<RazorpayService> log)
    {
        _http = http;
        _log = log;
        _keyId = config["Razorpay:KeyId"] ?? "";
        _keySecret = config["Razorpay:KeySecret"] ?? "";
        _plans = LoadPlans(config);

        if (!string.IsNullOrEmpty(_keyId) && !string.IsNullOrEmpty(_keySecret))
        {
            var auth = Convert.ToBase64String(Encoding.UTF8.GetBytes($"{_keyId}:{_keySecret}"));
            _http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", auth);
        }
    }

    public string KeyId => _keyId;

    public bool IsConfigured =>
        !string.IsNullOrEmpty(_keyId) && !string.IsNullOrEmpty(_keySecret);

    public PlanConfig GetPlan(string planName)
    {
        if (!_plans.TryGetValue(planName, out var p))
            throw new ArgumentException($"Unknown plan '{planName}'.");
        return p;
    }

    // ── Subscription pricing ───────────────────────────────────────────────
    // ₹129 per subject per month.
    // 3+ subjects in one purchase → 5% off the total.
    // Annual = monthly amount × 10 (rounded up to nearest rupee).
    // "All" in the subjects list must be expanded to actual subjects before calling this.
    public (int AmountInPaise, string Currency, int Days, string DisplayName) CalculatePrice(string billingCycle, List<string> subjects)
    {
        var isAnnual = string.Equals(billingCycle, "Annual", StringComparison.OrdinalIgnoreCase);
        var days     = isAnnual ? 365 : 30;
        int count    = subjects.Count;
        if (count == 0) count = 1;

        const decimal pricePerSubject = 129m;
        decimal multiplier = count >= 3 ? 0.95m : 1.0m;

        // Round up to nearest whole rupee, then convert to paise
        int monthlyRupees = (int)Math.Ceiling(count * pricePerSubject * multiplier);
        int monthlyPaise  = monthlyRupees * 100;
        int amount        = isAnnual ? monthlyPaise * 8 : monthlyPaise;

        string discount     = count >= 3 ? " (5% off)" : "";
        string cycleLabel   = isAnnual ? "Annual" : "Monthly";
        string subjectLabel = count == 1 ? subjects[0] : $"{count} Subjects{discount}";
        string displayName  = $"{subjectLabel} · {cycleLabel}";

        return (amount, "INR", days, displayName);
    }

    // ── Per-PDF batch pricing helpers ─────────────────────────────────────
    // 1-2 PDFs: ₹29 each · 3-5: ₹25 each · 6+: ₹20 each
    public static int PdfUnitPriceInPaise(int count) => count switch
    {
        <= 2 => 2900,
        <= 5 => 2500,
        _    => 2000
    };

    public static int PdfBatchTotalInPaise(int count) => PdfUnitPriceInPaise(count) * count;

    public async Task<OrderResult> CreateDynamicOrderAsync(
        int amountInPaise, string currency, string planName, Guid userId, CancellationToken ct = default)
    {
        if (!IsConfigured)
            throw new InvalidOperationException("Razorpay credentials are not configured.");

        var receipt = $"or_{userId.ToString("N")[..16]}_{DateTimeOffset.UtcNow.ToUnixTimeSeconds()}";

        var payload = new
        {
            amount = amountInPaise,
            currency,
            receipt,
            notes = new { userId = userId.ToString(), plan = planName }
        };

        using var req = new HttpRequestMessage(HttpMethod.Post, "https://api.razorpay.com/v1/orders");
        req.Content = JsonContent.Create(payload);
        using var res = await _http.SendAsync(req, ct);
        var body = await res.Content.ReadAsStringAsync(ct);

        if (!res.IsSuccessStatusCode)
        {
            _log.LogError("Razorpay dynamic order create failed {Status}: {Body}", res.StatusCode, body);
            throw new HttpRequestException($"Razorpay error {(int)res.StatusCode}: {body}");
        }

        var parsed = System.Text.Json.JsonSerializer.Deserialize<RazorpayOrderResponse>(body)
            ?? throw new InvalidOperationException("Empty Razorpay order response");

        return new OrderResult(parsed.Id, parsed.Amount, parsed.Currency);
    }

    public async Task<OrderResult> CreatePdfOrderAsync(
        int grade, string subject, Guid userId, CancellationToken ct = default)
    {
        if (!IsConfigured)
            throw new InvalidOperationException("Razorpay credentials are not configured.");

        const int amountInPaise = 2900; // ₹29
        var receipt = $"pdf_{userId.ToString("N")[..12]}_{grade}_{DateTimeOffset.UtcNow.ToUnixTimeSeconds()}";

        var payload = new
        {
            amount = amountInPaise,
            currency = "INR",
            receipt,
            notes = new { userId = userId.ToString(), grade = grade.ToString(), subject }
        };

        using var req = new HttpRequestMessage(HttpMethod.Post, "https://api.razorpay.com/v1/orders");
        req.Content = JsonContent.Create(payload);
        using var res = await _http.SendAsync(req, ct);
        var body = await res.Content.ReadAsStringAsync(ct);

        if (!res.IsSuccessStatusCode)
        {
            _log.LogError("Razorpay PDF order failed {Status}: {Body}", res.StatusCode, body);
            throw new HttpRequestException($"Razorpay error {(int)res.StatusCode}: {body}");
        }

        var parsed = System.Text.Json.JsonSerializer.Deserialize<RazorpayOrderResponse>(body)
            ?? throw new InvalidOperationException("Empty Razorpay PDF order response");

        return new OrderResult(parsed.Id, parsed.Amount, parsed.Currency);
    }

    public async Task<OrderResult> CreateBatchPdfOrderAsync(
        int pdfCount, int totalAmountInPaise, Guid userId, CancellationToken ct = default)
    {
        if (!IsConfigured)
            throw new InvalidOperationException("Razorpay credentials are not configured.");

        var receipt = $"pdfb_{userId.ToString("N")[..12]}_{pdfCount}_{DateTimeOffset.UtcNow.ToUnixTimeSeconds()}";

        var payload = new
        {
            amount  = totalAmountInPaise,
            currency = "INR",
            receipt,
            notes = new { userId = userId.ToString(), type = "pdf_batch", count = pdfCount.ToString() }
        };

        using var req = new HttpRequestMessage(HttpMethod.Post, "https://api.razorpay.com/v1/orders");
        req.Content = JsonContent.Create(payload);
        using var res = await _http.SendAsync(req, ct);
        var body = await res.Content.ReadAsStringAsync(ct);

        if (!res.IsSuccessStatusCode)
        {
            _log.LogError("Razorpay batch PDF order failed {Status}: {Body}", res.StatusCode, body);
            throw new HttpRequestException($"Razorpay error {(int)res.StatusCode}: {body}");
        }

        var parsed = System.Text.Json.JsonSerializer.Deserialize<RazorpayOrderResponse>(body)
            ?? throw new InvalidOperationException("Empty Razorpay batch PDF order response");

        return new OrderResult(parsed.Id, parsed.Amount, parsed.Currency);
    }

    public bool VerifySignature(string orderId, string paymentId, string signature)
    {
        if (string.IsNullOrEmpty(_keySecret)) return false;
        var payload = $"{orderId}|{paymentId}";
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(_keySecret));
        var computed = Convert.ToHexString(hmac.ComputeHash(Encoding.UTF8.GetBytes(payload)))
            .ToLowerInvariant();
        return CryptographicOperations.FixedTimeEquals(
            Encoding.UTF8.GetBytes(computed),
            Encoding.UTF8.GetBytes(signature.Trim().ToLowerInvariant()));
    }

    private static Dictionary<string, PlanConfig> LoadPlans(IConfiguration config)
    {
        var section = config.GetSection("Razorpay:Plans");
        var dict = new Dictionary<string, PlanConfig>(StringComparer.OrdinalIgnoreCase);
        foreach (var child in section.GetChildren())
        {
            dict[child.Key] = new PlanConfig(
                AmountInPaise: int.TryParse(child["AmountInPaise"], out var a) ? a : 0,
                Currency: child["Currency"] ?? "INR",
                Days: int.TryParse(child["Days"], out var d) ? d : 30,
                DisplayName: child["DisplayName"] ?? child.Key);
        }
        return dict;
    }

    private class RazorpayOrderResponse
    {
        [JsonPropertyName("id")] public string Id { get; set; } = "";
        [JsonPropertyName("amount")] public int Amount { get; set; }
        [JsonPropertyName("currency")] public string Currency { get; set; } = "INR";
    }
}
