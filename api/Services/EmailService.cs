using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace OlympiadReady.Api.Services;

public interface IEmailService
{
    Task SendWelcomeEmailAsync(string toEmail, string toName);
    Task SendSubscriptionReceiptAsync(string toEmail, string toName, string planName, int amountInPaise, List<string> subjects);
    Task SendWeeklyProgressAsync(string toEmail, string toName, int testsCompleted, int newBadges, int pendingTests, string userRank, string topBadgePlatform, string userBadgesHtml);
    Task SendSchoolJoinNotificationAsync(string coordinatorEmail, string schoolName, string studentName, string studentEmail);
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

    public async Task SendWelcomeEmailAsync(string toEmail, string toName)
    {
        if (string.IsNullOrWhiteSpace(_apiKey))
        {
            _log.LogWarning("Brevo API key not configured. Skipping welcome email to {Email}", toEmail);
            return;
        }

        var firstName = string.IsNullOrWhiteSpace(toName) ? "there" : toName.Split(' ')[0];

        string htmlContent = $@"
        <div style=""font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;max-width:600px;margin:0 auto;color:#333;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;background:#ffffff;"">
            <div style=""background:#1e3a8a;padding:40px 20px 30px;text-align:center;"">
                <img src=""https://images.olympiadready.com/assets/logo-light.png"" alt=""OlympiadReady"" style=""height:52px;max-width:100%;display:block;margin:0 auto;"" />
                <h1 style=""color:#ffffff;margin:20px 0 0;font-size:26px;font-weight:700;"">Welcome to OlympiadReady! 🎉</h1>
            </div>

            <div style=""padding:36px 32px;"">
                <p style=""font-size:16px;margin-top:0;"">Hi <strong>{firstName}</strong>,</p>
                <p style=""font-size:15px;color:#475569;line-height:1.6;"">
                    You've just unlocked India's most powerful AI-driven Olympiad preparation platform.
                    Here's what you can do right now:
                </p>

                <div style=""margin:24px 0;"">
                    <div style=""display:flex;align-items:flex-start;margin-bottom:16px;"">
                        <span style=""font-size:22px;margin-right:14px;"">📄</span>
                        <div>
                            <strong style=""color:#1e293b;"">15 Free Practice Papers</strong>
                            <p style=""margin:4px 0 0;font-size:14px;color:#64748b;"">SOF-aligned questions for IMO, NSO, IEO, IGKO & more. No card needed.</p>
                        </div>
                    </div>
                    <div style=""display:flex;align-items:flex-start;margin-bottom:16px;"">
                        <span style=""font-size:22px;margin-right:14px;"">🤖</span>
                        <div>
                            <strong style=""color:#1e293b;"">AI Explains Every Answer</strong>
                            <p style=""margin:4px 0 0;font-size:14px;color:#64748b;"">Get step-by-step explanations after every test — instantly.</p>
                        </div>
                    </div>
                    <div style=""display:flex;align-items:flex-start;margin-bottom:16px;"">
                        <span style=""font-size:22px;margin-right:14px;"">📥</span>
                        <div>
                            <strong style=""color:#1e293b;"">Free PDF Downloads</strong>
                            <p style=""margin:4px 0 0;font-size:14px;color:#64748b;"">Download and print practice papers. Study offline anytime.</p>
                        </div>
                    </div>
                    <div style=""display:flex;align-items:flex-start;"">
                        <span style=""font-size:22px;margin-right:14px;"">🏅</span>
                        <div>
                            <strong style=""color:#1e293b;"">Earn Badges & Certificates</strong>
                            <p style=""margin:4px 0 0;font-size:14px;color:#64748b;"">Track your progress and earn real rewards as you improve.</p>
                        </div>
                    </div>
                </div>

                <div style=""background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:20px;margin:28px 0;text-align:center;"">
                    <p style=""margin:0 0 6px;font-size:15px;color:#1e40af;font-weight:600;"">⚡ Ready to take your first practice test?</p>
                    <p style=""margin:0 0 18px;font-size:14px;color:#3b82f6;"">Pick your subject and start right now — it takes less than 2 minutes.</p>
                    <a href=""https://olympiadready.com/dashboard"" style=""background:#1e3a8a;color:#fff;padding:14px 32px;text-decoration:none;border-radius:8px;font-weight:700;font-size:15px;display:inline-block;"">Start Practising Free →</a>
                </div>

                <div style=""background:#fefce8;border:1px solid #fef08a;border-radius:10px;padding:16px 20px;margin-top:24px;"">
                    <p style=""margin:0;font-size:14px;color:#713f12;"">
                        💡 <strong>Pro tip:</strong> After your 15 free papers, unlock unlimited AI-generated practice for just <strong>₹129/subject/month</strong> — less than ₹5 a day.
                    </p>
                </div>
            </div>

            <div style=""background:#f1f5f9;padding:20px;text-align:center;border-top:1px solid #e2e8f0;"">
                <p style=""margin:0;font-size:12px;color:#64748b;"">© {DateTime.UtcNow.Year} OlympiadReady. All rights reserved.</p>
                <p style=""margin:6px 0 0;font-size:12px;color:#94a3b8;"">Questions? Reply to this email — we read every one.</p>
            </div>
        </div>";

        var payload = new
        {
            sender = new { name = _senderName, email = _senderEmail },
            to = new[] { new { email = toEmail, name = toName } },
            subject = "Welcome to OlympiadReady — Your 15 Free Papers Are Ready! 🎉",
            htmlContent
        };

        try
        {
            var res = await _http.PostAsJsonAsync("smtp/email", payload);
            if (!res.IsSuccessStatusCode)
            {
                var err = await res.Content.ReadAsStringAsync();
                _log.LogError("Failed to send welcome email via Brevo. Status: {Status}, Error: {Error}", res.StatusCode, err);
            }
            else
            {
                _log.LogInformation("Successfully sent welcome email to {Email}", toEmail);
            }
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Exception while sending welcome email to {Email}", toEmail);
        }
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

    public async Task SendWeeklyProgressAsync(string toEmail, string toName, int testsCompleted, int newBadges, int pendingTests, string userRank, string topBadgePlatform, string userBadgesHtml)
    {
        if (string.IsNullOrWhiteSpace(_apiKey))
        {
            _log.LogWarning("Brevo API key not configured. Skipping weekly email to {Email}", toEmail);
            return;
        }

        // Fallback for missing user badges
        if (string.IsNullOrWhiteSpace(userBadgesHtml))
        {
            userBadgesHtml = "<p style=\"color: #64748b; font-style: italic;\">Take more mock tests to start earning badges!</p>";
        }

        string htmlContent = $@"
        <div style=""font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; color: #333; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: #ffffff;"">
            <div style=""background: #ffffff; padding: 40px 20px 25px; text-align: center; border-bottom: 3px solid #e0e7ff;"">
                <img src=""https://images.olympiadready.com/assets/logo.png"" alt=""OlympiadReady"" style=""height: 64px; max-width: 100%; display: block; margin: 0 auto; color: #1e3a8a; font-size: 28px; font-weight: bold;"" />
                <h2 style=""color: #1e3a8a; margin: 25px 0 0 0; font-size: 24px; letter-spacing: 0.5px;"">Your Weekly Progress Report</h2>
            </div>
            
            <div style=""padding: 30px;"">
                <p style=""font-size: 16px; margin-top: 0;"">Hi <strong>{toName}</strong>,</p>
                <p style=""font-size: 16px; color: #475569; line-height: 1.5;"">Here is your OlympiadReady progress for the past week. Consistent practice is the key to mastering Olympiad subjects!</p>
                
                <div style=""background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; margin: 25px 0;"">
                    <h3 style=""margin-top: 0; color: #1e293b; font-size: 18px; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px;"">Weekly Stats</h3>
                    <ul style=""list-style: none; padding: 0; margin: 0;"">
                        <li style=""margin-bottom: 12px; font-size: 15px;"">📝 <strong>Tests Completed:</strong> <span style=""float: right; font-weight: bold; color: #4f46e5;"">{testsCompleted}</span></li>
                        <li style=""margin-bottom: 12px; font-size: 15px;"">🏅 <strong>New Badges Earned:</strong> <span style=""float: right; font-weight: bold; color: #4f46e5;"">{newBadges}</span></li>
                        <li style=""font-size: 15px;"">⏳ <strong>Pending Mistake Reviews:</strong> <span style=""float: right; font-weight: bold; color: #ef4444;"">{pendingTests}</span></li>
                    </ul>
                </div>

                <div style=""margin: 25px 0;"">
                    <h3 style=""color: #1e293b; font-size: 18px;"">🏆 Leaderboard Update</h3>
                    <p style=""font-size: 15px; color: #475569;"">Your current platform rank is <strong>#{userRank}</strong>.</p>
                    <p style=""font-size: 15px; color: #475569;"">The highest badge awarded on the platform this week was: <strong style=""color: #b48600;"">{topBadgePlatform}</strong>.</p>
                </div>

                <div style=""margin: 25px 0; background: #fffbeb; border: 1px solid #fef3c7; padding: 20px; border-radius: 8px;"">
                    <h3 style=""margin-top: 0; color: #b45309; font-size: 18px;"">✨ Your Latest Badges</h3>
                    <div style=""margin-top: 10px;"">
                        {userBadgesHtml}
                    </div>
                </div>
                
                <div style=""text-align: center; margin-top: 40px;"">
                    <p style=""font-size: 16px; font-weight: bold; color: #1e293b;"">Ready to boost your rank?</p>
                    <p style=""font-size: 14px; color: #64748b; margin-bottom: 20px;"">Take a quick mock exam right now to earn your next badge!</p>
                    <a href=""https://olympiadready.com/dashboard"" style=""background: #4f46e5; color: #fff; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);"">Start a Quick Test</a>
                </div>
            </div>
            
            <div style=""background: #f1f5f9; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;"">
                <p style=""margin: 0; font-size: 12px; color: #64748b;"">
                    &copy; {DateTime.UtcNow.Year} OlympiadReady. All rights reserved.
                </p>
                <p style=""margin: 8px 0 0 0; font-size: 11px; color: #94a3b8;"">
                    You're receiving this because you're an awesome student on OlympiadReady.
                </p>
            </div>
        </div>";

        var payload = new
        {
            sender = new { name = _senderName, email = _senderEmail },
            to = new[] { new { email = toEmail, name = toName } },
            subject = "Your Weekly OlympiadReady Progress & Leaderboard Stats! 🚀",
            htmlContent = htmlContent
        };

        try
        {
            var res = await _http.PostAsJsonAsync("smtp/email", payload);
            if (!res.IsSuccessStatusCode)
            {
                var err = await res.Content.ReadAsStringAsync();
                _log.LogError("Failed to send weekly email via Brevo. Status: {Status}, Error: {Error}", res.StatusCode, err);
            }
            else
            {
                _log.LogInformation("Successfully sent weekly email to {Email}", toEmail);
            }
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Exception while sending weekly email to {Email}", toEmail);
        }
    }

    public async Task SendSchoolJoinNotificationAsync(string coordinatorEmail, string schoolName, string studentName, string studentEmail)
    {
        if (string.IsNullOrWhiteSpace(_apiKey))
        {
            _log.LogWarning("Brevo API key not configured. Skipping school join email to {Email}", coordinatorEmail);
            return;
        }

        string htmlContent = $@"
        <div style=""font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;"">
            <h2 style=""color: #4f46e5;"">New Student Enrolled — {schoolName}</h2>
            <p>Hello,</p>
            <p>A student has just joined your school's OlympiadReady pilot programme.</p>
            <div style=""background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4f46e5;"">
                <p style=""margin: 0 0 8px;""><strong>Name:</strong> {studentName}</p>
                <p style=""margin: 0;""><strong>Email:</strong> {studentEmail}</p>
            </div>
            <p>They now have full access to OlympiadReady for the duration of the pilot period under <strong>{schoolName}</strong>.</p>
            <p style=""margin-top: 30px; font-size: 12px; color: #64748b;"">
                This is an automated notification from OlympiadReady. Please do not reply to this email.
            </p>
        </div>";

        var payload = new
        {
            sender = new { name = _senderName, email = _senderEmail },
            to = new[] { new { email = coordinatorEmail, name = schoolName } },
            subject = $"New Student Joined: {studentName} — {schoolName} Pilot",
            htmlContent
        };

        try
        {
            var res = await _http.PostAsJsonAsync("smtp/email", payload);
            if (!res.IsSuccessStatusCode)
            {
                var err = await res.Content.ReadAsStringAsync();
                _log.LogError("Failed to send school join email. Status: {Status}, Error: {Error}", res.StatusCode, err);
            }
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Exception sending school join email to {Email}", coordinatorEmail);
        }
    }
}
