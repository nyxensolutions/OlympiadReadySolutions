using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Data.Entities;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/olympiad-dates")]
public class OlympiadDatesController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly ILogger<OlympiadDatesController> _log;

    public OlympiadDatesController(AppDbContext db, ILogger<OlympiadDatesController> log)
    {
        _db = db;
        _log = log;
    }

    // ── GET /api/olympiad-dates?year=2025&org=SOF&subject=Math ────────────
    [HttpGet]
    public async Task<IActionResult> Get(
        [FromQuery] int? year,
        [FromQuery] string? org,
        [FromQuery] string? subject,
        CancellationToken ct)
    {
        var query = _db.OlympiadSchedules.AsNoTracking();

        if (year.HasValue)
            query = query.Where(s => s.AcademicYear == year.Value);
        if (!string.IsNullOrWhiteSpace(org))
            query = query.Where(s => s.OrgName == org);
        if (!string.IsNullOrWhiteSpace(subject))
            query = query.Where(s => s.Subject == subject);

        var rows = await query
            .OrderBy(s => s.AcademicYear)
            .ThenBy(s => s.OrgName)
            .ThenBy(s => s.ExamDateFrom ?? DateTime.MaxValue)
            .ToListAsync(ct);

        return Ok(rows.Select(r => new
        {
            id = r.OlympiadScheduleId,
            org = r.OrgName,
            orgFull = GetOrgFull(r.OrgName),
            name = r.OlympiadName,
            fullName = r.FullName,
            subject = r.Subject,
            stage = r.Stage,
            gradeMin = r.GradeMin,
            gradeMax = r.GradeMax,
            registrationWindow = r.RegistrationWindow,
            examDateText = r.ExamDateText,
            examDateFrom = r.ExamDateFrom,
            examDateTo = r.ExamDateTo,
            resultDateText = r.ResultDateText,
            officialWebsite = r.OfficialWebsite,
            notes = r.Notes,
            academicYear = r.AcademicYear,
            lastVerified = r.LastVerified
        }));
    }

    // ── GET /api/olympiad-dates/orgs — distinct org names for filter UI ───
    [HttpGet("orgs")]
    public async Task<IActionResult> GetOrgs(CancellationToken ct)
    {
        var orgs = await _db.OlympiadSchedules
            .AsNoTracking()
            .Select(s => s.OrgName)
            .Distinct()
            .OrderBy(o => o)
            .ToListAsync(ct);

        return Ok(orgs.Select(o => new { org = o, orgFull = GetOrgFull(o) }));
    }

    // ── POST /api/olympiad-dates/seed (admin) ─────────────────────────────
    // Seeds the schedule table with 2025-26 data if it is empty.
    [HttpPost("seed")]
    public async Task<IActionResult> Seed(
        [FromHeader(Name = "X-Admin-Key")] string? adminKey,
        [FromServices] IConfiguration config,
        CancellationToken ct)
    {
        var expected = config["Admin:ApiKey"];
        if (string.IsNullOrEmpty(expected) || adminKey != expected)
            return Unauthorized();

        var count = await _db.OlympiadSchedules.CountAsync(ct);
        if (count > 0)
            return Ok(new { message = $"Already seeded ({count} records). No changes made." });

        var now = DateTime.UtcNow;
        var schedules = Build2025Schedules(now);
        _db.OlympiadSchedules.AddRange(schedules);
        await _db.SaveChangesAsync(ct);

        _log.LogInformation("Seeded {Count} olympiad schedule records", schedules.Count);
        return Ok(new { inserted = schedules.Count });
    }

    // ── Helpers ──────────────────────────────────────────────────────────

    private static string GetOrgFull(string org) => org switch
    {
        "HBCSE"         => "Homi Bhabha Centre for Science Education (TIFR)",
        "SOF"           => "Science Olympiad Foundation",
        "SilverZone"    => "SilverZone Foundation",
        "Unified"       => "Unified Council",
        "CREST"         => "CREST Olympiads",
        "SEAMO"         => "Southeast Asian Mathematical Olympiad",
        "ICO"           => "Indian Computing Olympiad (IARCS)",
        "Humming Bird"  => "Humming Bird Education",
        _               => org
    };

    private static List<OlympiadSchedule> Build2025Schedules(DateTime verifiedAt) =>
    [
        // ── SOF ─────────────────────────────────────────────────────
        new()
        {
            OrgName = "SOF", OlympiadName = "IMO", FullName = "International Mathematics Olympiad",
            Subject = "Math", Stage = "Level 1", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Sep 2025",
            ExamDateText = "Oct – Nov 2025 (schools choose from given slots)",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Jan 2026",
            OfficialWebsite = "https://sofworld.org",
            Notes = "Schools register students; individual registrations through school only.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "IMO", FullName = "International Mathematics Olympiad",
            Subject = "Math", Stage = "Level 2", GradeMin = 3, GradeMax = 12,
            RegistrationWindow = "N/A — qualify via Level 1",
            ExamDateText = "Feb 2026",
            ExamDateFrom = new DateTime(2026,2,1), ExamDateTo = new DateTime(2026,2,28),
            ResultDateText = "Apr 2026",
            OfficialWebsite = "https://sofworld.org",
            Notes = "Top rankers from Level 1 qualify automatically.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "NSO", FullName = "National Science Olympiad",
            Subject = "Science", Stage = "Level 1", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Sep 2025",
            ExamDateText = "Oct – Nov 2025",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Jan 2026",
            OfficialWebsite = "https://sofworld.org",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "IEO", FullName = "International English Olympiad",
            Subject = "English", Stage = "Level 1", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Sep 2025",
            ExamDateText = "Oct – Nov 2025",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Jan 2026",
            OfficialWebsite = "https://sofworld.org",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "NCO", FullName = "National Cyber Olympiad",
            Subject = "Computers", Stage = "Level 1", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Sep 2025",
            ExamDateText = "Oct – Nov 2025",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Jan 2026",
            OfficialWebsite = "https://sofworld.org",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "IGKO", FullName = "International General Knowledge Olympiad",
            Subject = "General Knowledge", Stage = "Level 1", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Jul – Sep 2025",
            ExamDateText = "Oct – Nov 2025",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Jan 2026",
            OfficialWebsite = "https://sofworld.org",
            AcademicYear = 2025, LastVerified = verifiedAt
        },

        // ── HBCSE ────────────────────────────────────────────────────
        new()
        {
            OrgName = "HBCSE", OlympiadName = "IOQM", FullName = "Indian Olympiad Qualifier in Mathematics",
            Subject = "Math", Stage = "Stage 1", GradeMin = 8, GradeMax = 12,
            RegistrationWindow = "Jul – Aug 2025",
            ExamDateText = "September 2025",
            ExamDateFrom = new DateTime(2025,9,7), ExamDateTo = new DateTime(2025,9,7),
            ResultDateText = "Oct 2025",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "Previously PRMO. Conducted by MTA. 30 questions, 3 hours. No negative marking.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "INMO", FullName = "Indian National Mathematics Olympiad",
            Subject = "Math", Stage = "Stage 2 (RMO → INMO)", GradeMin = 8, GradeMax = 12,
            RegistrationWindow = "N/A — qualify via IOQM/RMO",
            ExamDateText = "January 2026",
            ExamDateFrom = new DateTime(2026,1,18), ExamDateTo = new DateTime(2026,1,18),
            ResultDateText = "Feb – Mar 2026",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "Top ~300 IOQM qualifiers write RMO (Regional MO) first; ~30–35 qualify for INMO.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "NSE (Physics)", FullName = "National Standard Examination in Physics",
            Subject = "Science", Stage = "Stage 1 (IPhO pathway)", GradeMin = 11, GradeMax = 12,
            RegistrationWindow = "Aug – Sep 2025",
            ExamDateText = "November 2025 (last Sunday)",
            ExamDateFrom = new DateTime(2025,11,30), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Dec 2025 – Jan 2026",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "80 MCQ, 2 hours. Top ~1% qualify for INPhO.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "NSE (Chemistry)", FullName = "National Standard Examination in Chemistry",
            Subject = "Science", Stage = "Stage 1 (IChO pathway)", GradeMin = 11, GradeMax = 12,
            RegistrationWindow = "Aug – Sep 2025",
            ExamDateText = "November 2025 (last Sunday)",
            ExamDateFrom = new DateTime(2025,11,30), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Dec 2025 – Jan 2026",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "Same day as NSE Physics. Conducted by IAPT. Top ~1% qualify for INChO.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "NSEJS", FullName = "National Standard Examination in Junior Science",
            Subject = "Science", Stage = "Stage 1 (IJSO pathway)", GradeMin = 8, GradeMax = 10,
            RegistrationWindow = "Aug – Sep 2025",
            ExamDateText = "November 2025",
            ExamDateFrom = new DateTime(2025,11,30), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Dec 2025",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "International Junior Science Olympiad pathway. For Class 8–10 students.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "IOQJS", FullName = "Indian Olympiad Qualifier in Junior Science",
            Subject = "Science", Stage = "Stage 1 (IJSO pathway)", GradeMin = 8, GradeMax = 10,
            RegistrationWindow = "Jul – Aug 2025",
            ExamDateText = "October 2025",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,10,31),
            ResultDateText = "Nov 2025",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "ZCO / IOQCS", FullName = "Zonal Computing Olympiad / Indian Olympiad Qualifier in Computer Science",
            Subject = "Computers", Stage = "Stage 1 (IOI pathway)", GradeMin = 8, GradeMax = 12,
            RegistrationWindow = "Sep – Oct 2025",
            ExamDateText = "December 2025",
            ExamDateFrom = new DateTime(2025,12,1), ExamDateTo = new DateTime(2025,12,31),
            ResultDateText = "Jan 2026",
            OfficialWebsite = "https://www.iarcs.org.in/inoi",
            Notes = "Online; multiple choice + short answer. Top scorers advance to INOI. Uses C/C++/Java/Python.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },

        // ── SilverZone ───────────────────────────────────────────────
        new()
        {
            OrgName = "SilverZone", OlympiadName = "iOM", FullName = "International Olympiad of Mathematics",
            Subject = "Math", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jun – Sep 2025",
            ExamDateText = "Oct – Dec 2025 (school decides date within window)",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,12,31),
            ResultDateText = "Feb 2026",
            OfficialWebsite = "https://silverzone.org",
            Notes = "35 questions, 60 minutes. Schools register in bulk. Individual prizes + merit certificates.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SilverZone", OlympiadName = "iOS", FullName = "International Olympiad of Science",
            Subject = "Science", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jun – Sep 2025",
            ExamDateText = "Oct – Dec 2025",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,12,31),
            ResultDateText = "Feb 2026",
            OfficialWebsite = "https://silverzone.org",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SilverZone", OlympiadName = "iOEL", FullName = "International Olympiad of English Language",
            Subject = "English", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jun – Sep 2025",
            ExamDateText = "Oct – Dec 2025",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,12,31),
            ResultDateText = "Feb 2026",
            OfficialWebsite = "https://silverzone.org",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SilverZone", OlympiadName = "iOIT", FullName = "International Olympiad of Information Technology",
            Subject = "Computers", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jun – Sep 2025",
            ExamDateText = "Oct – Dec 2025",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,12,31),
            ResultDateText = "Feb 2026",
            OfficialWebsite = "https://silverzone.org",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SilverZone", OlympiadName = "STEM", FullName = "Science Technology Engineering Mathematics Olympiad",
            Subject = "Science", Stage = "Single Level", GradeMin = 6, GradeMax = 12,
            RegistrationWindow = "Jun – Sep 2025",
            ExamDateText = "Oct – Dec 2025",
            ExamDateFrom = new DateTime(2025,10,1), ExamDateTo = new DateTime(2025,12,31),
            ResultDateText = "Feb 2026",
            OfficialWebsite = "https://silverzone.org",
            AcademicYear = 2025, LastVerified = verifiedAt
        },

        // ── Unified Council ──────────────────────────────────────────
        new()
        {
            OrgName = "Unified", OlympiadName = "NSTSE", FullName = "National Level Science Talent Search Examination",
            Subject = "Science", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Oct 2025",
            ExamDateText = "Jan – Feb 2026",
            ExamDateFrom = new DateTime(2026,1,1), ExamDateTo = new DateTime(2026,2,28),
            ResultDateText = "Mar – Apr 2026",
            OfficialWebsite = "https://unifiedcouncil.com",
            Notes = "Diagnostic-style, NCERT-based. Awarded from Class 1. Scholarships for toppers.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "Unified", OlympiadName = "UIEO", FullName = "Unified International English Olympiad",
            Subject = "English", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Oct 2025",
            ExamDateText = "Jan – Feb 2026",
            ExamDateFrom = new DateTime(2026,1,1), ExamDateTo = new DateTime(2026,2,28),
            ResultDateText = "Mar – Apr 2026",
            OfficialWebsite = "https://unifiedcouncil.com",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "Unified", OlympiadName = "UCO", FullName = "Unified Cyber Olympiad",
            Subject = "Computers", Stage = "Single Level", GradeMin = 3, GradeMax = 12,
            RegistrationWindow = "Jul – Oct 2025",
            ExamDateText = "Nov 2025",
            ExamDateFrom = new DateTime(2025,11,1), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Jan 2026",
            OfficialWebsite = "https://unifiedcouncil.com",
            AcademicYear = 2025, LastVerified = verifiedAt
        },

        // ── CREST ────────────────────────────────────────────────────
        new()
        {
            OrgName = "CREST", OlympiadName = "CMO", FullName = "CREST Mathematics Olympiad",
            Subject = "Math", Stage = "Single Level", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Open year-round",
            ExamDateText = "Online, on-demand scheduling",
            OfficialWebsite = "https://crestolympiads.com",
            Notes = "Online Olympiad; student books own slot. Results within 7 days.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "CREST", OlympiadName = "CSO", FullName = "CREST Science Olympiad",
            Subject = "Science", Stage = "Single Level", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Open year-round",
            ExamDateText = "Online, on-demand scheduling",
            OfficialWebsite = "https://crestolympiads.com",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "CREST", OlympiadName = "CEO", FullName = "CREST English Olympiad",
            Subject = "English", Stage = "Single Level", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Open year-round",
            ExamDateText = "Online, on-demand scheduling",
            OfficialWebsite = "https://crestolympiads.com",
            AcademicYear = 2025, LastVerified = verifiedAt
        },

        // ── SEAMO ────────────────────────────────────────────────────
        new()
        {
            OrgName = "SEAMO", OlympiadName = "SEAMO", FullName = "Southeast Asian Mathematical Olympiad",
            Subject = "Math", Stage = "Paper A/B/C/D/E/X", GradeMin = 4, GradeMax = 12,
            RegistrationWindow = "Jun – Oct 2025",
            ExamDateText = "November 2025",
            ExamDateFrom = new DateTime(2025,11,1), ExamDateTo = new DateTime(2025,11,30),
            ResultDateText = "Jan 2026",
            OfficialWebsite = "https://seamo-official.org",
            Notes = "Multiple difficulty papers (A=easiest, X=hardest/invited). Awards at regional + international level.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },

        // ── ICO (Computing) ─────────────────────────────────────────
        new()
        {
            OrgName = "ICO", OlympiadName = "INOI", FullName = "Indian National Olympiad in Informatics",
            Subject = "Computers", Stage = "Stage 2 (after ZCO/IOQCS)", GradeMin = 8, GradeMax = 12,
            RegistrationWindow = "N/A — qualify via ZCO",
            ExamDateText = "January 2026",
            ExamDateFrom = new DateTime(2026,1,1), ExamDateTo = new DateTime(2026,1,31),
            ResultDateText = "Feb 2026",
            OfficialWebsite = "https://www.iarcs.org.in/inoi",
            Notes = "Top ~200 from ZCO advance. INOI qualifiers attend IOITC camp for IOI team selection.",
            AcademicYear = 2025, LastVerified = verifiedAt
        },
    ];
}
