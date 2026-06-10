using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using Amazon;
using Amazon.Runtime;
using Amazon.S3;
using Amazon.S3.Model;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

/// <summary>
/// Internal admin endpoints — protected by a static API key in config (Admin:ApiKey).
/// Not exposed behind Clerk JWT so the developer can hit it from curl/Postman without signing in.
/// </summary>
using Microsoft.AspNetCore.Authorization;

[ApiController]
[Authorize(Policy = "AdminPolicy")]
[Route("api/admin")]
public class AdminController : ControllerBase
{
    private readonly QuestionBankService _bank;
    private readonly IConfiguration _config;
    private readonly ILogger<AdminController> _log;
    private readonly IWebHostEnvironment _env;

    private readonly OlympiadReady.Api.Data.AppDbContext _db;

    private static readonly JsonSerializerOptions _jsonOpts = new()
    {
        PropertyNameCaseInsensitive = true,
        AllowTrailingCommas = true,         // forgive trailing commas Claude sometimes adds
        Converters = { new OptionsFlexConverter() }
    };

    private static readonly HashSet<string> _allowedImageExts =
        new(StringComparer.OrdinalIgnoreCase) { ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg" };

    public AdminController(
        QuestionBankService bank,
        IConfiguration config,
        ILogger<AdminController> log,
        IWebHostEnvironment env,
        OlympiadReady.Api.Data.AppDbContext db)
    {
        _bank = bank;
        _config = config;
        _log = log;
        _env = env;
        _db = db;
    }

    // ---------------------------------------------------------------
    // POST /api/admin/import-questions?subject=Math&grade=5
    // Header: X-Admin-Key: <value from Admin:ApiKey config>
    // Body: JSON array matching ImportRowDto[]
    //
    // Reads the raw body as UTF-8 so that Unicode characters (em dash,
    // rupee sign, etc.) that Claude includes are preserved correctly,
    // regardless of what Content-Type charset the client declares.
    // ---------------------------------------------------------------
    [HttpPost("import-questions")]
    public async Task<IActionResult> ImportQuestions(
        [FromQuery] string subject,
        [FromQuery] int grade,
        CancellationToken ct)
    {

        if (string.IsNullOrWhiteSpace(subject))
            return BadRequest(new { error = "subject query param is required." });
        if (grade is < 1 or > 12)
            return BadRequest(new { error = "grade must be 1-12." });

        // Normalize to SOF canonical name before any further processing.
        var (canonicalSubject, recognized) = SubjectNormalizer.Normalize(subject);
        if (!recognized)
            return BadRequest(new { error = SubjectNormalizer.UnrecognisedMessage(subject) });
        subject = canonicalSubject!;

        // Read the body ourselves as UTF-8 regardless of the Content-Type charset.
        string rawBody;
        using (var reader = new StreamReader(Request.Body, Encoding.UTF8, detectEncodingFromByteOrderMarks: true, leaveOpen: true))
            rawBody = await reader.ReadToEndAsync(ct);

        if (string.IsNullOrWhiteSpace(rawBody))
            return BadRequest(new { error = "Request body is empty." });

        List<ImportRowDto>? rows;
        try
        {
            rows = JsonSerializer.Deserialize<List<ImportRowDto>>(rawBody, _jsonOpts);
        }
        catch (JsonException ex)
        {
            _log.LogWarning("Import JSON parse error: {Msg}", ex.Message);
            return BadRequest(new { error = $"Invalid JSON: {ex.Message}" });
        }

        if (rows is null || rows.Count == 0)
            return BadRequest(new { error = "Request body must be a non-empty JSON array." });

        _log.LogInformation(
            "Admin import: {Count} rows for {Subject} Grade {Grade}", rows.Count, subject, grade);

        var serviceRows = rows.Select(r => new QuestionBankService.ImportRow(
            r.QuestionText ?? "",
            r.ImageUrl,
            r.Options ?? new(),
            r.CorrectAnswer ?? "",
            r.Topic ?? "",
            r.SubTopic,
            r.Difficulty ?? "",
            r.Explanation ?? ""
        ));

        var result = await _bank.ImportAsync(subject, grade, serviceRows, ct);

        return Ok(new
        {
            inserted = result.Inserted,
            skipped = result.Skipped,
            errors = result.Errors
        });
    }

    // ---------------------------------------------------------------
    // GET /api/admin/config-check  (temporary diagnostic)
    // ---------------------------------------------------------------
    [HttpGet("config-check")]
    public IActionResult ConfigCheck()
    {
        var accountId  = _config["R2:AccountId"];
        var accessKey  = _config["R2:AccessKeyId"];
        var secretKey  = _config["R2:SecretAccessKey"];
        var bucket     = _config["R2:BucketName"];
        var publicUrl  = _config["R2:PublicBaseUrl"];
        var appData    = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        var secretsPath = Path.Combine(appData, "Microsoft", "UserSecrets", "olympiadready-api-secrets", "secrets.json");
        return Ok(new
        {
            AccountId   = string.IsNullOrWhiteSpace(accountId) ? "(empty)" : accountId[..4] + "****",
            AccessKeyId = string.IsNullOrWhiteSpace(accessKey) ? "(empty)" : accessKey[..4] + "****",
            BucketName  = bucket ?? "(empty)",
            PublicBaseUrl = publicUrl ?? "(empty)",
            Environment = _env.EnvironmentName,
            SecretsPath = secretsPath,
            SecretsFileExists = System.IO.File.Exists(secretsPath),
        });
    }

    // ---------------------------------------------------------------
    // GET /api/admin/bank-stats
    // Header: X-Admin-Key: <value>
    // Returns question counts per (subject, grade, difficulty)
    // ---------------------------------------------------------------
    [HttpGet("bank-stats")]
    public async Task<IActionResult> BankStats(CancellationToken ct)
    {

        var stats = await _bank.GetStatsAsync(ct);
        return Ok(stats);
    }

    // ---------------------------------------------------------------
    // POST /api/admin/fix-corrupted-questions
    // ---------------------------------------------------------------
    [HttpPost("fix-corrupted-questions")]
    public async Task<IActionResult> FixCorruptedQuestions([FromQuery] string dirPath, CancellationToken ct)
    {

        if (string.IsNullOrWhiteSpace(dirPath) || !System.IO.Directory.Exists(dirPath))
            return BadRequest(new { error = "Invalid directory path" });

        var allDbQs = await Microsoft.EntityFrameworkCore.EntityFrameworkQueryableExtensions.ToListAsync(_db.QuestionBank, ct);
        int updatedCount = 0;
        int notFoundCount = 0;
        int multipleMatchesCount = 0;
        int errors = 0;

        string Normalize(string s)
        {
            if (string.IsNullOrWhiteSpace(s)) return "";
            var sb = new StringBuilder();
            foreach (var c in s.ToLowerInvariant())
            {
                if (char.IsLetterOrDigit(c)) sb.Append(c);
            }
            return sb.ToString();
        }

        var jsonFiles = System.IO.Directory.GetFiles(dirPath, "*.json", System.IO.SearchOption.AllDirectories);

        foreach (var file in jsonFiles)
        {
            try
            {
                var content = await System.IO.File.ReadAllTextAsync(file, Encoding.UTF8, ct);
                var rows = JsonSerializer.Deserialize<List<ImportRowDto>>(content, _jsonOpts);
                if (rows == null) continue;

                foreach (var row in rows)
                {
                    if (string.IsNullOrWhiteSpace(row.QuestionText)) continue;
                    
                    var normJson = Normalize(row.QuestionText);
                    var candidates = allDbQs.Where(q => q.Topic == row.Topic && (q.Difficulty == row.Difficulty || (q.Difficulty == "Medium" && row.Difficulty == "Advanced")) && Normalize(q.QuestionText) == normJson).ToList();

                    if (candidates.Count == 1)
                    {
                        var dbQ = candidates[0];
                        bool changed = false;

                        if (dbQ.QuestionText != row.QuestionText)
                        {
                            dbQ.QuestionText = row.QuestionText;
                            changed = true;
                        }

                        var newOptionsJson = JsonSerializer.Serialize(row.Options ?? new List<string>(), _jsonOpts);
                        if (dbQ.OptionsJson != newOptionsJson)
                        {
                            dbQ.OptionsJson = newOptionsJson;
                            changed = true;
                        }

                        if (dbQ.Explanation != (row.Explanation ?? ""))
                        {
                            dbQ.Explanation = row.Explanation ?? "";
                            changed = true;
                        }
                        
                        var ans = (row.CorrectAnswer ?? "A").Trim().ToUpperInvariant();
                        if (ans.Length > 0 && (ans[0] == 'A' || ans[0] == 'B' || ans[0] == 'C' || ans[0] == 'D')) {
                            ans = ans[0].ToString();
                        } else if (ans.Length > 1) {
                            ans = ans.Substring(0, 1);
                        } else if (ans.Length == 0) {
                            ans = "A";
                        }

                        if (dbQ.CorrectAnswer != ans)
                        {
                            dbQ.CorrectAnswer = ans;
                            changed = true;
                        }

                        if (changed) updatedCount++;
                    }
                    else if (candidates.Count == 0)
                    {
                        notFoundCount++;
                    }
                    else
                    {
                        multipleMatchesCount++;
                    }
                }
            }
            catch (Exception ex)
            {
                _log.LogError(ex, "Failed to process {file}", file);
                errors++;
            }
        }

        await _db.SaveChangesAsync(ct);

        return Ok(new
        {
            TotalFiles = jsonFiles.Length,
            Updated = updatedCount,
            NotFound = notFoundCount,
            MultipleMatches = multipleMatchesCount,
            Errors = errors
        });
    }

    // ---------------------------------------------------------------
    // GET /api/admin/questions?subject=&grade=&difficulty=&topic=&hasImage=true&page=1&pageSize=20
    // Header: X-Admin-Key: <value>
    // Search/filter questions in the bank for admin preview.
    // ---------------------------------------------------------------
    [HttpGet("questions")]
    public async Task<IActionResult> SearchQuestions(
        [FromQuery] string? subject,
        [FromQuery] int? grade,
        [FromQuery] string? difficulty,
        [FromQuery] string? topic,
        [FromQuery] string? search,
        [FromQuery] bool? hasImage,
        [FromQuery] int page = 1,
        [FromQuery] int pageSize = 20,
        CancellationToken ct = default)
    {

        var query = _db.QuestionBank.AsQueryable();

        if (!string.IsNullOrWhiteSpace(subject))
        {
            var (canonical, _) = SubjectNormalizer.Normalize(subject);
            var s = canonical ?? subject;
            query = query.Where(q => q.Subject == s);
        }
        if (grade.HasValue)
            query = query.Where(q => q.Grade == grade.Value);
        if (!string.IsNullOrWhiteSpace(difficulty))
            query = query.Where(q => q.Difficulty == difficulty);
        if (!string.IsNullOrWhiteSpace(topic))
            query = query.Where(q => q.Topic.Contains(topic));
        if (!string.IsNullOrWhiteSpace(search))
            query = query.Where(q => q.QuestionText.Contains(search));
        if (hasImage == true)
            query = query.Where(q =>
                (q.ImageUrl != null && q.ImageUrl != "") ||
                q.OptionsJson.Contains("http") ||
                q.OptionsJson.Contains("/question-images/"));

        var total = await Microsoft.EntityFrameworkCore.EntityFrameworkQueryableExtensions.CountAsync(query, ct);

        var items = await Microsoft.EntityFrameworkCore.EntityFrameworkQueryableExtensions.ToListAsync(
            query.OrderByDescending(q => q.CreatedAt)
                 .Skip((page - 1) * pageSize)
                 .Take(pageSize),
            ct);

        var results = items.Select(q =>
        {
            List<string> options;
            try { options = System.Text.Json.JsonSerializer.Deserialize<List<string>>(q.OptionsJson) ?? new(); }
            catch { options = new(); }

            return new
            {
                q.QuestionBankId,
                q.Subject,
                q.Grade,
                q.Difficulty,
                q.Topic,
                q.SubTopic,
                q.QuestionText,
                q.ImageUrl,
                Options = options,
                q.CorrectAnswer,
                q.Explanation,
                q.CreatedAt,
            };
        });

        return Ok(new { total, page, pageSize, items = results });
    }

    // ---------------------------------------------------------------
    // DELETE /api/admin/questions/{id}
    // Header: X-Admin-Key: <value>
    // ---------------------------------------------------------------
    [HttpDelete("questions/{id:guid}")]
    public async Task<IActionResult> DeleteQuestion(Guid id, CancellationToken ct)
    {

        var item = await _db.QuestionBank.FindAsync(new object[] { id }, ct);
        if (item is null)
            return NotFound(new { error = "Question not found." });

        _db.QuestionBank.Remove(item);
        await _db.SaveChangesAsync(ct);

        _log.LogInformation("Admin deleted question {Id} ({Subject} G{Grade})", id, item.Subject, item.Grade);
        return Ok(new { message = "Question deleted." });
    }

    // ---------------------------------------------------------------
    // POST /api/admin/upload-image
    // Header: X-Admin-Key: <value>
    // Body: multipart/form-data with field "file"
    // Uploads to Cloudflare R2 and returns: { url: "https://<public-base-url>/questions/..." }
    // ---------------------------------------------------------------
    [HttpPost("upload-image")]
    [RequestSizeLimit(10 * 1024 * 1024)] // 10 MB
    public async Task<IActionResult> UploadImage(IFormFile file, CancellationToken ct)
    {
        if (file == null || file.Length == 0)
            return BadRequest(new { error = "No file provided." });

        var ext = Path.GetExtension(file.FileName).ToLowerInvariant();
        if (!_allowedImageExts.Contains(ext))
            return BadRequest(new { error = $"File type {ext} not allowed. Use jpg/png/gif/webp/svg." });

        var accountId     = _config["R2:AccountId"];
        var accessKeyId   = _config["R2:AccessKeyId"];
        var secretKey     = _config["R2:SecretAccessKey"];
        var bucketName    = _config["R2:BucketName"];
        var publicBaseUrl = _config["R2:PublicBaseUrl"]?.TrimEnd('/');

        if (string.IsNullOrWhiteSpace(accountId)   || accountId.StartsWith("REPLACE") ||
            string.IsNullOrWhiteSpace(accessKeyId) || accessKeyId.StartsWith("REPLACE") ||
            string.IsNullOrWhiteSpace(secretKey)   || secretKey.StartsWith("REPLACE"))
            return StatusCode(503, new { error = "R2 is not configured. Fill in R2:AccountId/AccessKeyId/SecretAccessKey in appsettings or user secrets." });

        var r2Endpoint = $"https://{accountId}.r2.cloudflarestorage.com";
        var s3Config   = new AmazonS3Config
        {
            ServiceURL            = r2Endpoint,
            ForcePathStyle        = true,
            AuthenticationRegion  = "auto",
            DisablePayloadSigning = true,   // R2 does not support AWS chunked upload trailers
        };
        var credentials = new BasicAWSCredentials(accessKeyId, secretKey);
        using var s3    = new AmazonS3Client(credentials, s3Config);

        var objectKey   = $"questions/{Guid.NewGuid()}{ext}";
        var contentType = file.ContentType ?? "application/octet-stream";

        try
        {
            await using var stream = file.OpenReadStream();
            var putRequest = new PutObjectRequest
            {
                BucketName  = bucketName,
                Key         = objectKey,
                InputStream = stream,
                ContentType = contentType,
            };
            // Cache for 1 year in browser + CDN — safe because filenames are UUIDs (immutable)
            putRequest.Headers["Cache-Control"] = "public, max-age=31536000, immutable";

            var result = await s3.PutObjectAsync(putRequest, ct);

            if ((int)result.HttpStatusCode >= 300)
            {
                _log.LogWarning("R2 upload failed with status {Status}", result.HttpStatusCode);
                return StatusCode(502, new { error = $"R2 upload failed: HTTP {(int)result.HttpStatusCode}" });
            }

            var publicUrl = string.IsNullOrWhiteSpace(publicBaseUrl)
                ? $"{r2Endpoint}/{bucketName}/{objectKey}"
                : $"{publicBaseUrl}/{objectKey}";

            _log.LogInformation("R2 upload OK: {Url} ({Size} bytes)", publicUrl, file.Length);
            return Ok(new { url = publicUrl });
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "R2 upload exception for key {Key}", objectKey);
            return StatusCode(500, new { error = $"Upload failed: {ex.Message}" });
        }
    }

    // ---------------------------------------------------------------
    // POST /api/admin/add-question
    // Header: X-Admin-Key: <value>
    // Body: JSON matching AddQuestionDto
    // ---------------------------------------------------------------
    [HttpPost("add-question")]
    public async Task<IActionResult> AddQuestion([FromBody] AddQuestionDto dto, CancellationToken ct)
    {

        if (string.IsNullOrWhiteSpace(dto.Subject))
            return BadRequest(new { error = "subject is required." });
        if (dto.Grade is < 1 or > 12)
            return BadRequest(new { error = "grade must be 1-12." });
        if (string.IsNullOrWhiteSpace(dto.QuestionText))
            return BadRequest(new { error = "questionText is required." });
        if (dto.Options == null || dto.Options.Count != 4)
            return BadRequest(new { error = "Exactly 4 options required." });

        var (canonicalSubject, recognized) = SubjectNormalizer.Normalize(dto.Subject);
        if (!recognized)
            return BadRequest(new { error = SubjectNormalizer.UnrecognisedMessage(dto.Subject) });

        var row = new QuestionBankService.ImportRow(
            QuestionText: dto.QuestionText,
            ImageUrl: dto.ImageUrl,
            Options: dto.Options,
            CorrectAnswer: dto.CorrectAnswer ?? "A",
            Topic: dto.Topic ?? "General",
            SubTopic: dto.SubTopic,
            Difficulty: dto.Difficulty ?? "Foundation",
            Explanation: dto.Explanation ?? ""
        );

        var result = await _bank.ImportAsync(canonicalSubject!, dto.Grade, new[] { row }, ct);

        if (result.Errors.Count > 0)
            return BadRequest(new { error = result.Errors[0] });

        if (result.Skipped > 0)
            return Conflict(new { error = "A question with this text already exists (duplicate skipped)." });

        return Ok(new { message = "Question added successfully.", inserted = result.Inserted });
    }

    // ── PUT /api/admin/questions/{id} — update an existing question ──────────
    [HttpPut("questions/{id:guid}")]
    public async Task<IActionResult> UpdateQuestion(Guid id, [FromBody] AddQuestionDto dto, CancellationToken ct)
    {

        if (string.IsNullOrWhiteSpace(dto.Subject))
            return BadRequest(new { error = "subject is required." });
        if (dto.Grade is < 1 or > 12)
            return BadRequest(new { error = "grade must be 1-12." });
        if (string.IsNullOrWhiteSpace(dto.QuestionText))
            return BadRequest(new { error = "questionText is required." });
        if (dto.Options == null || dto.Options.Count != 4)
            return BadRequest(new { error = "Exactly 4 options required." });
        if (!new[] { "A","B","C","D" }.Contains(dto.CorrectAnswer))
            return BadRequest(new { error = "correctAnswer must be A, B, C, or D." });

        var (canonicalSubject, recognized) = SubjectNormalizer.Normalize(dto.Subject);
        if (!recognized)
            return BadRequest(new { error = SubjectNormalizer.UnrecognisedMessage(dto.Subject) });

        var item = await _db.QuestionBank.FindAsync(new object[] { id }, ct);
        if (item is null)
            return NotFound(new { error = "Question not found." });

        item.Subject      = canonicalSubject!;
        item.Grade        = dto.Grade;
        item.Difficulty   = dto.Difficulty ?? item.Difficulty;
        item.Topic        = dto.Topic?.Trim() ?? item.Topic;
        item.SubTopic     = dto.SubTopic?.Trim() ?? item.SubTopic;
        item.QuestionText = dto.QuestionText.Trim();
        item.ImageUrl     = string.IsNullOrWhiteSpace(dto.ImageUrl) ? null : dto.ImageUrl.Trim();
        item.OptionsJson  = System.Text.Json.JsonSerializer.Serialize(dto.Options);
        item.CorrectAnswer = dto.CorrectAnswer!;
        item.Explanation  = dto.Explanation?.Trim() ?? item.Explanation;

        await _db.SaveChangesAsync(ct);
        return Ok(new { message = "Question updated successfully." });
    }

    // ---------------------------------------------------------------
    // GET /api/admin/badges
    // Returns all users with their computed badge breakdown and physical-reward eligibility.
    // ---------------------------------------------------------------
    [HttpGet("badges")]
    public async Task<IActionResult> GetUserBadges(CancellationToken ct)
    {

        var users = await _db.Users
            .AsNoTracking()
            .Select(u => new
            {
                u.UserId,
                u.FullName,
                u.Email,
                u.CreatedAt,
                u.SubscriptionTier,
                Results = u.Results.Select(r => new
                {
                    r.Score,
                    r.TotalQuestions,
                    r.TimeTakenSeconds,
                    r.CompletedAt,
                    PaperTitle = r.Paper != null ? r.Paper.Title : "",
                    Subject = r.Paper != null ? r.Paper.Subject : ""
                }).ToList()
            })
            .ToListAsync(ct);

        var result = users.Select(u =>
        {
            var results = u.Results;
            var totalTests = results.Count;
            var bestPct = totalTests == 0 ? 0.0 :
                results.Max(r => r.TotalQuestions > 0 ? (double)r.Score / r.TotalQuestions * 100.0 : 0.0);

            // Streak computation
            var practicedDates = results
                .Select(r => r.CompletedAt.Date)
                .Distinct()
                .OrderByDescending(d => d)
                .ToList();

            int streak = 0;
            if (practicedDates.Count > 0)
            {
                var today = DateTime.UtcNow.Date;
                var yesterday = today.AddDays(-1);
                if (practicedDates[0] == today || practicedDates[0] == yesterday)
                {
                    streak = 1;
                    for (int i = 1; i < practicedDates.Count; i++)
                    {
                        var diff = (practicedDates[i - 1] - practicedDates[i]).TotalDays;
                        if (diff == 1) streak++;
                        else break;
                    }
                }
            }

            // Distinct subjects practiced
            var subjectCount = results.Select(r => r.Subject).Where(s => !string.IsNullOrEmpty(s)).Distinct().Count();

            // Subjects where student scored 90%+
            var masteredSubjects = results
                .Where(r => r.TotalQuestions > 0 && (double)r.Score / r.TotalQuestions * 100.0 >= 90)
                .Select(r => r.Subject)
                .Distinct()
                .Count();

            // Max consecutive 90%+ tests
            int maxConsec = 0, curConsec = 0;
            foreach (var r in results.OrderBy(r => r.CompletedAt))
            {
                var pct = r.TotalQuestions > 0 ? (double)r.Score / r.TotalQuestions * 100.0 : 0;
                if (pct >= 90) { curConsec++; maxConsec = Math.Max(maxConsec, curConsec); }
                else curConsec = 0;
            }

            // Comeback King: improved 20+ pct on a retake
            var byPaper = results.GroupBy(r => r.PaperTitle ?? "").ToDictionary(g => g.Key, g => g.OrderBy(r => r.CompletedAt).ToList());
            var hasComeback = byPaper.Values.Any(scores => {
                for (int i = 1; i < scores.Count; i++)
                {
                    var prev = scores[i-1].TotalQuestions > 0 ? (double)scores[i-1].Score / scores[i-1].TotalQuestions * 100.0 : 0;
                    var curr = scores[i].TotalQuestions   > 0 ? (double)scores[i].Score   / scores[i].TotalQuestions   * 100.0 : 0;
                    if (curr - prev >= 20) return true;
                }
                return false;
            });

            var badges = new Dictionary<string, bool>
            {
                // Activity
                ["first_test"]       = totalTests >= 1,
                ["five_tests"]       = totalTests >= 5,
                ["ten_tests"]        = totalTests >= 10,
                ["twenty_five_tests"]= totalTests >= 25,
                ["century"]          = totalTests >= 100,
                // Accuracy
                ["sharpshooter"]     = bestPct >= 90,
                ["perfect"]          = results.Any(r => r.Score == r.TotalQuestions && r.TotalQuestions > 0),
                ["on_fire"]          = maxConsec >= 5,
                ["comeback"]         = hasComeback,
                // Streaks
                ["streak_3"]         = streak >= 3,
                ["streak_7"]         = streak >= 7,
                ["streak_30"]        = streak >= 30,
                // Speed
                ["speed"]            = results.Any(r => r.TotalQuestions >= 10 && r.TimeTakenSeconds < 300),
                ["lightning"]        = results.Any(r => r.TotalQuestions >= 20 && r.TimeTakenSeconds < 480),
                // Breadth
                ["explorer"]         = subjectCount >= 3,
                ["all_rounder"]      = masteredSubjects >= 3,
                // Milestones
                ["mock_exam"]        = results.Any(r => (r.PaperTitle ?? "").StartsWith("Mock Exam")),
                ["mock_3"]           = results.Count(r => (r.PaperTitle ?? "").StartsWith("Mock Exam")) >= 3,
            };

            int earnedCount = badges.Values.Count(v => v);
            bool legendEligible = earnedCount == badges.Count; // all 18 badges

            return new
            {
                userId = u.UserId,
                fullName = u.FullName ?? u.Email,
                email = u.Email,
                joinedAt = u.CreatedAt,
                subscriptionTier = u.SubscriptionTier,
                totalTests,
                bestPct = Math.Round(bestPct, 1),
                streak,
                earnedCount,
                totalBadges = badges.Count,
                badges,
                physicalRewardEligible = legendEligible,
            };
        })
        .OrderByDescending(x => x.earnedCount)
        .ThenByDescending(x => x.totalTests)
        .ToList();

        return Ok(result);
    }

    // ---------------------------------------------------------------
    // GET /api/admin/physical-rewards
    // Lists all physical reward claims with user info.
    // ---------------------------------------------------------------
    [HttpGet("physical-rewards")]
    public async Task<IActionResult> GetPhysicalRewards(CancellationToken ct)
    {

        var claims = await _db.PhysicalRewardClaims
            .AsNoTracking()
            .Include(c => c.User)
            .OrderByDescending(c => c.RequestedAt)
            .Select(c => new
            {
                claimId = c.ClaimId,
                userId = c.UserId,
                studentName = c.StudentName ?? c.User!.FullName ?? c.User.Email,
                email = c.User!.Email,
                rewardType = c.RewardType,
                status = c.Status,
                requestedAt = c.RequestedAt,
                shippedAt = c.ShippedAt,
                adminNotes = c.AdminNotes,
                trackingNumber = c.TrackingNumber,
            })
            .ToListAsync(ct);

        return Ok(claims);
    }

    // ---------------------------------------------------------------
    // PUT /api/admin/physical-rewards/{id}
    // Update status, tracking number, or notes on a claim.
    // ---------------------------------------------------------------
    [HttpPut("physical-rewards/{id:guid}")]
    public async Task<IActionResult> UpdatePhysicalReward(Guid id, [FromBody] UpdateRewardDto dto, CancellationToken ct)
    {

        var claim = await _db.PhysicalRewardClaims.FindAsync(new object[] { id }, ct);
        if (claim is null) return NotFound(new { error = "Claim not found." });

        if (!string.IsNullOrWhiteSpace(dto.Status))
        {
            claim.Status = dto.Status;
            if (dto.Status == "Shipped" && claim.ShippedAt is null)
                claim.ShippedAt = DateTime.UtcNow;
        }
        if (dto.AdminNotes is not null)  claim.AdminNotes = dto.AdminNotes;
        if (dto.TrackingNumber is not null) claim.TrackingNumber = dto.TrackingNumber;

        await _db.SaveChangesAsync(ct);
        return Ok(new { message = "Reward claim updated." });
    }

    // ---------------------------------------------------------------
    // POST /api/admin/physical-rewards/{userId}/claim
    // Manually create a claim on behalf of a student (admin-initiated).
    // ---------------------------------------------------------------
    [HttpPost("physical-rewards/{userId:guid}/claim")]
    public async Task<IActionResult> CreatePhysicalRewardClaim(Guid userId, [FromBody] CreateRewardClaimDto dto, CancellationToken ct)
    {

        var user = await _db.Users.FindAsync(new object[] { userId }, ct);
        if (user is null) return NotFound(new { error = "User not found." });

        var existing = await _db.PhysicalRewardClaims
            .Where(c => c.UserId == userId && c.RewardType == dto.RewardType && c.Status != "Cancelled")
            .AnyAsync(ct);
        if (existing) return Conflict(new { error = "An active claim already exists for this reward type." });

        var claim = new OlympiadReady.Api.Data.Entities.PhysicalRewardClaim
        {
            UserId = userId,
            RewardType = dto.RewardType ?? "olympiad_legend",
            StudentName = dto.StudentName,
            Status = "Pending",
            RequestedAt = DateTime.UtcNow,
        };
        _db.PhysicalRewardClaims.Add(claim);
        await _db.SaveChangesAsync(ct);
        return Ok(new { claimId = claim.ClaimId, message = "Claim created." });
    }

    // ---------------------------------------------------------------
    // GET /api/admin/reports
    // Lists all reported questions.
    // ---------------------------------------------------------------
    [HttpGet("reports")]
    public async Task<IActionResult> GetReports(CancellationToken ct)
    {

        var reports = await _db.ReportedQuestions
            .AsNoTracking()
            .Include(r => r.User)
            .Include(r => r.Question)
            .OrderByDescending(r => r.ReportedAt)
            .Select(r => new
            {
                r.ReportId,
                r.UserId,
                UserEmail = r.User != null ? r.User.Email : "",
                UserFullName = r.User != null ? r.User.FullName : "",
                r.QuestionBankId,
                QuestionText = r.Question != null ? r.Question.QuestionText : "",
                r.Category,
                r.Description,
                r.Status,
                r.AdminReason,
                r.ReportedAt,
                r.ResolvedAt
            })
            .ToListAsync(ct);

        return Ok(reports);
    }

    public record ResolveReportDto(string Status, string? AdminReason);

    // ---------------------------------------------------------------
    // POST /api/admin/reports/{reportId}/resolve
    // Accept or Reject a reported question, sends notification.
    // ---------------------------------------------------------------
    [HttpPost("reports/{reportId:guid}/resolve")]
    public async Task<IActionResult> ResolveReport(Guid reportId, [FromBody] ResolveReportDto dto, CancellationToken ct)
    {

        if (dto.Status != "Accepted" && dto.Status != "Rejected")
            return BadRequest(new { error = "Status must be 'Accepted' or 'Rejected'." });

        var report = await _db.ReportedQuestions.FindAsync(new object[] { reportId }, ct);
        if (report is null) return NotFound(new { error = "Report not found." });

        if (report.Status != "Pending")
            return BadRequest(new { error = "Report is already resolved." });

        report.Status = dto.Status;
        report.AdminReason = dto.AdminReason;
        report.ResolvedAt = DateTime.UtcNow;

        // Create notification
        var message = dto.Status == "Accepted"
            ? "Your question report was reviewed and accepted! Thank you for helping us improve."
            : $"Your question report was reviewed and rejected. Reason: {dto.AdminReason ?? "No reason provided."}";

        var notification = new OlympiadReady.Api.Data.Entities.UserNotification
        {
            UserId = report.UserId,
            Title = $"Report {dto.Status}",
            Message = message,
            CreatedAt = DateTime.UtcNow
        };
        _db.UserNotifications.Add(notification);

        // Check if user unlocked a new title
        if (dto.Status == "Accepted")
        {
            var acceptedCount = await _db.ReportedQuestions
                .Where(r => r.UserId == report.UserId && r.Status == "Accepted")
                .CountAsync(ct);

            var pastResults = await _db.Results
                .AsNoTracking()
                .Where(r => r.UserId == report.UserId && r.TotalQuestions > 0)
                .Select(r => new BadgeCalculator.ResultRow(r.UserId, r.Score, r.TotalQuestions, r.TimeTakenSeconds, r.CompletedAt, r.Paper != null ? r.Paper.Title ?? "" : "", r.Paper != null ? r.Paper.Subject ?? "" : ""))
                .ToListAsync(ct);

            var oldEarned = BadgeCalculator.ComputeBadges(pastResults, acceptedCount).Count(b => b.Earned);
            var oldTitle = BadgeCalculator.GetTitle(oldEarned, 24);

            var newEarned = BadgeCalculator.ComputeBadges(pastResults, acceptedCount + 1).Count(b => b.Earned);
            var newTitle = BadgeCalculator.GetTitle(newEarned, 24);

            if (newTitle != oldTitle && newTitle != "Newcomer")
            {
                _db.UserNotifications.Add(new OlympiadReady.Api.Data.Entities.UserNotification
                {
                    UserId = report.UserId,
                    Title = "New Title Unlocked!",
                    Message = $"Congratulations! You have earned the prestigious {newTitle} title. Download your official certificate in the Achievements panel.",
                    CreatedAt = DateTime.UtcNow
                });
            }

            if (acceptedCount + 1 == 500)
            {
                var user = await _db.Users.FindAsync(new object[] { report.UserId }, ct);
                var rewardExists = await _db.PhysicalRewardClaims
                    .AnyAsync(c => c.UserId == report.UserId && c.RewardType == "super_reporter", ct);

                if (!rewardExists && user != null)
                {
                    _db.PhysicalRewardClaims.Add(new OlympiadReady.Api.Data.Entities.PhysicalRewardClaim
                    {
                        UserId = report.UserId,
                        RewardType = "super_reporter",
                        StudentName = user.FullName ?? user.Email,
                        Status = "Pending",
                        RequestedAt = DateTime.UtcNow
                    });
                }
            }
        }

        await _db.SaveChangesAsync(ct);
        return Ok(new { message = "Report resolved successfully." });
    }

    // ---------------------------------------------------------------

}

// ─── DTOs ─────────────────────────────────────────────────────────────────────
public record UpdateRewardDto(string? Status, string? AdminNotes, string? TrackingNumber);
public record CreateRewardClaimDto(string? RewardType, string? StudentName);

// DTO that matches the JSON schema the user will prepare
public class ImportRowDto
{
    public string? QuestionText { get; set; }
    public string? ImageUrl { get; set; }
    // Accepts both array ["A) ...", "B) ...", ...] and object {"A":"...","B":"...",...} formats.
    [JsonConverter(typeof(OptionsFlexConverter))]
    public List<string>? Options { get; set; }
    /// <summary>A | B | C | D</summary>
    public string? CorrectAnswer { get; set; }
    public string? Topic { get; set; }
    public string? SubTopic { get; set; }
    /// <summary>Foundation | Advanced | Olympiad</summary>
    public string? Difficulty { get; set; }
    public string? Explanation { get; set; }
}

public class AddQuestionDto
{
    public string? Subject { get; set; }
    public int Grade { get; set; }
    public string? Difficulty { get; set; }
    public string? Topic { get; set; }
    public string? SubTopic { get; set; }
    public string? QuestionText { get; set; }
    public string? ImageUrl { get; set; }
    public List<string>? Options { get; set; }
    public string? CorrectAnswer { get; set; }
    public string? Explanation { get; set; }
}

/// <summary>
/// Handles Options as either a JSON array ["A) ...", ...] or an object {"A":"...","B":"...",...}.
/// Normalises the object form to a 4-element array with "A) "/"B) "/"C) "/"D) " prefixes.
/// </summary>
public class OptionsFlexConverter : JsonConverter<List<string>?>
{
    private static readonly string[] _keys = ["A", "B", "C", "D"];

    public override List<string>? Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        if (reader.TokenType == JsonTokenType.Null) return null;

        if (reader.TokenType == JsonTokenType.StartArray)
        {
            var list = new List<string>();
            while (reader.Read() && reader.TokenType != JsonTokenType.EndArray)
                list.Add(reader.GetString() ?? "");
            return list;
        }

        if (reader.TokenType == JsonTokenType.StartObject)
        {
            // {"A": "text", "B": "text", "C": "text", "D": "text"}
            var map = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            while (reader.Read() && reader.TokenType != JsonTokenType.EndObject)
            {
                var key = reader.GetString() ?? "";
                reader.Read();
                map[key] = reader.GetString() ?? "";
            }
            return _keys.Select(k => map.TryGetValue(k, out var v) ? $"{k}) {v}" : "").ToList();
        }

        throw new JsonException($"Options must be an array or object, got {reader.TokenType}.");
    }

    public override void Write(Utf8JsonWriter writer, List<string>? value, JsonSerializerOptions options)
    {
        if (value is null) { writer.WriteNullValue(); return; }
        writer.WriteStartArray();
        foreach (var s in value) writer.WriteStringValue(s);
        writer.WriteEndArray();
    }
}


