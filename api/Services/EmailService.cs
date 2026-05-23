using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace OlympiadReady.Api.Services;

public interface IEmailService
{
    Task SendSubscriptionReceiptAsync(string toEmail, string toName, string planName, int amountInPaise, List<string> subjects);
}

public class BrevoEmailService : IEmailService
{
    private readonly HttpClient _http;
    private readonly ILogger<BrevoEmailService> _log;
    private readonly string _apiKey;
    private readonly string _senderEmail;
    private readonly string _senderName;

    public BrevoEmailService(HttpClient http, IConfiguration config, ILogger<BrevoEmailService> log)
    {
        _http = http;
        _log = log;
        _apiKey = config["Brevo:ApiKey"] ?? "";
        _senderEmail = config["Brevo:SenderEmail"] ?? "no-reply@olympiadready.com";
        _senderName = config["Brevo:SenderName"] ?? "OlympiadReady";
        
        _http.BaseAddress = new Uri("https://api.brevo.com/v3/");
        _http.DefaultRequestHeaders.Add("api-key", _apiKey);
    }

    public async Task SendSubscriptionReceiptAsync(string toEmail, string toName, string planName, int amountInPaise, List<string> subjects)
    {
        if (string.IsNullOrWhiteSpace(_apiKey))
        {
            _log.LogWarning("Brevo API key not configured. Skipping email to {Email}", toEmail);
            return;
        }

        string subjectListHtml = string.Join("", subjects.Select(s => $"<li>{s}</li>"));
        string totalAmount = (amountInPaise / 100.0).ToString("F2");

        string htmlContent = $@"
        <div style=""font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;"">
            <h2 style=""color: #4f46e5;"">Welcome to OlympiadReady!</h2>
            <p>Hi {toName},</p>
            <p>Thank you for your purchase. Your account has been successfully upgraded.</p>
            
            <div style=""background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;"">
                <h3 style=""margin-top: 0;"">Receipt Summary</h3>
                <p><strong>Plan:</strong> {planName}</p>
                <p><strong>Total Paid:</strong> ₹{totalAmount}</p>
                <p><strong>Unlocked Subjects:</strong></p>
                <ul style=""margin-bottom: 0;"">
                    {subjectListHtml}
                </ul>
            </div>
            
            <p>You can now access <strong>Level 2 (Achievers) practice questions</strong>, enjoy unlimited AI generations, and view detailed explanations for the unlocked subjects.</p>
            
            <p style=""margin-top: 30px;"">
                <a href=""https://olympiadready.com/dashboard"" style=""background: #4f46e5; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;"">Go to Dashboard</a>
            </p>
            
            <p style=""margin-top: 40px; font-size: 12px; color: #64748b;"">
                If you have any questions, feel free to reply to this email.
            </p>
        </div>";

        var payload = new
        {
            sender = new { name = _senderName, email = _senderEmail },
            to = new[] { new { email = toEmail, name = toName } },
            subject = "Your OlympiadReady Subscription Receipt",
            htmlContent = htmlContent
        };

        try
        {
            var res = await _http.PostAsJsonAsync("smtp/email", payload);
            if (!res.IsSuccessStatusCode)
            {
                var err = await res.Content.ReadAsStringAsync();
                _log.LogError("Failed to send email via Brevo. Status: {Status}, Error: {Error}", res.StatusCode, err);
            }
            else
            {
                _log.LogInformation("Successfully sent receipt email to {Email}", toEmail);
            }
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Exception while sending email to {Email}", toEmail);
        }
    }
}
