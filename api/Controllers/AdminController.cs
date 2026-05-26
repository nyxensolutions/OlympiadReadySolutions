using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using CloudinaryDotNet;
using CloudinaryDotNet.Actions;
using Microsoft.AspNetCore.Mvc;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

/// <summary>
/// Internal admin endpoints — protected by a static API key in config (Admin:ApiKey).
/// Not exposed behind Clerk JWT so the developer can hit it from curl/Postman without signing in.
/// </summary>
[ApiController]
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
        if (!IsAuthorised())
            return Unauthorized(new { error = "Missing or invalid X-Admin-Key header." });

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
        if (!IsAuthorised()) return Unauthorized();
        var cloudName  = _config["Cloudinary:CloudName"];
        var apiKey     = _config["Cloudinary:ApiKey"];
        var apiSecret  = _config["Cloudinary:ApiSecret"];
        var appData    = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        var secretsPath = Path.Combine(appData, "Microsoft", "UserSecrets", "olympiadready-api-secrets", "secrets.json");
        return Ok(new
        {
            CloudName    = string.IsNullOrWhiteSpace(cloudName) ? "(empty)" : cloudName,
            ApiKey       = string.IsNullOrWhiteSpace(apiKey)    ? "(empty)" : apiKey[..4] + "****",
            ApiSecret    = string.IsNullOrWhiteSpace(apiSecret) ? "(empty)" : apiSecret[..4] + "****",
            Environment  = _env.EnvironmentName,
            SecretsPath  = secretsPath,
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
        if (!IsAuthorised())
            return Unauthorized(new { error = "Missing or invalid X-Admin-Key header." });

        var stats = await _bank.GetStatsAsync(ct);
        return Ok(stats);
    }

    // ---------------------------------------------------------------
    // POST /api/admin/fix-corrupted-questions
    // ---------------------------------------------------------------
    [HttpPost("fix-corrupted-questions")]
    public async Task<IActionResult> FixCorruptedQuestions([FromQuery] string dirPath, CancellationToken ct)
    {
        if (!IsAuthorised()) return Unauthorized();

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
        if (!IsAuthorised())
            return Unauthorized(new { error = "Missing or invalid X-Admin-Key header." });

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
        if (!IsAuthorised())
            return Unauthorized(new { error = "Missing or invalid X-Admin-Key header." });

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
    // Uploads to Cloudinary and returns: { url: "https://res.cloudinary.com/..." }
    // ---------------------------------------------------------------
    [HttpPost("upload-image")]
    [RequestSizeLimit(10 * 1024 * 1024)] // 10 MB
    public async Task<IActionResult> UploadImage(IFormFile file, CancellationToken ct)
    {
        if (!IsAuthorised())
            return Unauthorized(new { error = "Missing or invalid X-Admin-Key header." });

        if (file == null || file.Length == 0)
            return BadRequest(new { error = "No file provided." });

        var ext = Path.GetExtension(file.FileName);
        if (!_allowedImageExts.Contains(ext))
            return BadRequest(new { error = $"File type {ext} not allowed. Use jpg/png/gif/webp/svg." });

        // Build Cloudinary client from config
        var cloudName  = _config["Cloudinary:CloudName"];
        var apiKey     = _config["Cloudinary:ApiKey"];
        var apiSecret  = _config["Cloudinary:ApiSecret"];
        var folder     = _config["Cloudinary:Folder"] ?? "olympiadready/questions";

        if (string.IsNullOrWhiteSpace(cloudName) || cloudName.StartsWith("REPLACE") ||
            string.IsNullOrWhiteSpace(apiKey)    || apiKey.StartsWith("REPLACE") ||
            string.IsNullOrWhiteSpace(apiSecret) || apiSecret.StartsWith("REPLACE"))
            return StatusCode(503, new { error = "Cloudinary is not configured. Fill in Cloudinary:CloudName/ApiKey/ApiSecret in appsettings." });

        var account    = new Account(cloudName, apiKey, apiSecret);
        var cloudinary = new Cloudinary(account) { Api = { Secure = true } };

        var publicId = $"{folder}/{Guid.NewGuid()}";

        await using var stream = file.OpenReadStream();
        var uploadParams = new ImageUploadParams
        {
            File           = new FileDescription(file.FileName, stream),
            PublicId       = publicId,
            Overwrite      = false,
            UniqueFilename = false,
        };

        var result = await cloudinary.UploadAsync(uploadParams, ct);

        if (result.Error != null)
        {
            _log.LogWarning("Cloudinary upload error: {Msg}", result.Error.Message);
            return StatusCode(502, new { error = $"Cloudinary error: {result.Error.Message}" });
        }

        _log.LogInformation("Cloudinary upload OK: {Url} ({Size} bytes)", result.SecureUrl, file.Length);
        return Ok(new { url = result.SecureUrl.ToString() });
    }

    // ---------------------------------------------------------------
    // POST /api/admin/add-question
    // Header: X-Admin-Key: <value>
    // Body: JSON matching AddQuestionDto
    // ---------------------------------------------------------------
    [HttpPost("add-question")]
    public async Task<IActionResult> AddQuestion([FromBody] AddQuestionDto dto, CancellationToken ct)
    {
        if (!IsAuthorised())
            return Unauthorized(new { error = "Missing or invalid X-Admin-Key header." });

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

    // ---------------------------------------------------------------
    private bool IsAuthorised()
    {
        var configKey = _config["Admin:ApiKey"];
        if (string.IsNullOrWhiteSpace(configKey)) return false;

        Request.Headers.TryGetValue("X-Admin-Key", out var provided);
        return string.Equals(configKey, provided, StringComparison.Ordinal);
    }
}

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
