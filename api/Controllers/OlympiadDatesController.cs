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
    // Seeds the schedule table with 2026-27 data. Overwrites existing data.
    [HttpPost("seed")]
    public async Task<IActionResult> Seed(
        [FromHeader(Name = "X-Admin-Key")] string? adminKey,
        [FromServices] IConfiguration config,
        CancellationToken ct)
    {
        var expected = config["Admin:ApiKey"];
        if (string.IsNullOrEmpty(expected) || expected == "REPLACE_WITH_YOUR_ADMIN_KEY" || adminKey != expected)
            return Unauthorized();

        var deleted = await _db.OlympiadSchedules.ExecuteDeleteAsync(ct);

        var now = DateTime.UtcNow;
        var schedules = Build2026Schedules(now);
        _db.OlympiadSchedules.AddRange(schedules);
        await _db.SaveChangesAsync(ct);

        _log.LogInformation("Deleted {Deleted} old records. Seeded {Count} olympiad schedule records", deleted, schedules.Count);
        return Ok(new { deleted = deleted, inserted = schedules.Count });
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
        "Unicus"        => "Unicus Olympiads",
        "AmarUjala"     => "National Olympiads by Amar Ujala (AUNO)",
        _               => org
    };

    private static List<OlympiadSchedule> Build2026Schedules(DateTime verifiedAt) =>
    [
        // ── Unicus ──────────────────────────────────────────────────
        new()
        {
            OrgName = "Unicus", OlympiadName = "UMO", FullName = "Unicus Mathematics Olympiad",
            Subject = "Math", Stage = "Single Level", GradeMin = 1, GradeMax = 11,
            RegistrationWindow = "Open now",
            ExamDateText = "Jul 14, 2026 / Jul 29, 2026",
            ExamDateFrom = new DateTime(2026,7,14), ExamDateTo = new DateTime(2026,7,29),
            ResultDateText = "Aug 2026",
            OfficialWebsite = "https://www.unicusolympiads.com/umo",
            Notes = "Summer Olympiad.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "Unicus", OlympiadName = "USO", FullName = "Unicus Science Olympiad",
            Subject = "Science", Stage = "Single Level", GradeMin = 1, GradeMax = 11,
            RegistrationWindow = "Open now",
            ExamDateText = "Jul 11, 2026 / Jul 25, 2026",
            ExamDateFrom = new DateTime(2026,7,11), ExamDateTo = new DateTime(2026,7,25),
            ResultDateText = "Aug 2026",
            OfficialWebsite = "https://www.unicusolympiads.com/uso",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "Unicus", OlympiadName = "UEO", FullName = "Unicus English Olympiad",
            Subject = "English", Stage = "Single Level", GradeMin = 1, GradeMax = 11,
            RegistrationWindow = "Open now",
            ExamDateText = "Jul 10, 2026 / Jul 22, 2026",
            ExamDateFrom = new DateTime(2026,7,10), ExamDateTo = new DateTime(2026,7,22),
            ResultDateText = "Aug 2026",
            OfficialWebsite = "https://www.unicusolympiads.com/ueo",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "Unicus", OlympiadName = "UGKO", FullName = "Unicus General Knowledge Olympiad",
            Subject = "General Knowledge", Stage = "Single Level", GradeMin = 2, GradeMax = 11,
            RegistrationWindow = "Open now",
            ExamDateText = "Jul 8, 2026 / Jul 15, 2026",
            ExamDateFrom = new DateTime(2026,7,8), ExamDateTo = new DateTime(2026,7,15),
            ResultDateText = "Aug 2026",
            OfficialWebsite = "https://www.unicusolympiads.com/ugko",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "Unicus", OlympiadName = "UCTO", FullName = "Unicus Critical Thinking Olympiad",
            Subject = "Critical Thinking", Stage = "Single Level", GradeMin = 2, GradeMax = 11,
            RegistrationWindow = "Open now",
            ExamDateText = "Jul 9, 2026 / Jul 18, 2026",
            ExamDateFrom = new DateTime(2026,7,9), ExamDateTo = new DateTime(2026,7,18),
            ResultDateText = "Aug 2026",
            OfficialWebsite = "https://www.unicusolympiads.com/ucto",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "Unicus", OlympiadName = "UNMO", FullName = "Unicus Non-Routine Mathematics Olympiad",
            Subject = "Math", Stage = "Single Level", GradeMin = 3, GradeMax = 10,
            RegistrationWindow = "Open now",
            ExamDateText = "Jan 16, 2027 / Jan 28, 2027",
            ExamDateFrom = new DateTime(2027,1,16), ExamDateTo = new DateTime(2027,1,28),
            ResultDateText = "Feb 2027",
            OfficialWebsite = "https://www.unicusolympiads.com/unmo",
            AcademicYear = 2026, LastVerified = verifiedAt
        },

        // ── SOF ─────────────────────────────────────────────────────
        new()
        {
            OrgName = "SOF", OlympiadName = "IMO", FullName = "International Mathematics Olympiad",
            Subject = "Math", Stage = "Level 1", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Sep 2026",
            ExamDateText = "23 Oct, 26 Nov, 10 Dec 2026",
            ExamDateFrom = new DateTime(2026,10,23), ExamDateTo = new DateTime(2026,12,10),
            ResultDateText = "Jan 2027",
            OfficialWebsite = "https://sofworld.org",
            Notes = "Schools register students; individual registrations through school only.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "IMO", FullName = "International Mathematics Olympiad",
            Subject = "Math", Stage = "Level 2", GradeMin = 3, GradeMax = 12,
            RegistrationWindow = "N/A — qualify via Level 1",
            ExamDateText = "Feb 2027",
            ExamDateFrom = new DateTime(2027,2,1), ExamDateTo = new DateTime(2027,2,28),
            ResultDateText = "Apr 2027",
            OfficialWebsite = "https://sofworld.org",
            Notes = "Top rankers from Level 1 qualify automatically.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "ISO / NSO", FullName = "National Science Olympiad",
            Subject = "Science", Stage = "Level 1", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Sep 2026",
            ExamDateText = "30 Oct, 19 Nov, 3 Dec 2026",
            ExamDateFrom = new DateTime(2026,10,30), ExamDateTo = new DateTime(2026,12,3),
            ResultDateText = "Jan 2027",
            OfficialWebsite = "https://sofworld.org",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "IEO", FullName = "International English Olympiad",
            Subject = "English", Stage = "Level 1", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Sep 2026",
            ExamDateText = "30 Sept, 27 Oct, 17 Nov 2026",
            ExamDateFrom = new DateTime(2026,9,30), ExamDateTo = new DateTime(2026,11,17),
            ResultDateText = "Jan 2027",
            OfficialWebsite = "https://sofworld.org",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "NCO", FullName = "National Cyber Olympiad",
            Subject = "Computers", Stage = "Level 1", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Sep 2026",
            ExamDateText = "30 Nov 2026, 19 Jan 2027",
            ExamDateFrom = new DateTime(2026,11,30), ExamDateTo = new DateTime(2027,1,19),
            ResultDateText = "Feb 2027",
            OfficialWebsite = "https://sofworld.org",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SOF", OlympiadName = "IGKO", FullName = "International General Knowledge Olympiad",
            Subject = "General Knowledge", Stage = "Level 1", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Jul – Sep 2026",
            ExamDateText = "22 Sept, 6 Oct, 3 Nov 2026",
            ExamDateFrom = new DateTime(2026,9,22), ExamDateTo = new DateTime(2026,11,3),
            ResultDateText = "Jan 2027",
            OfficialWebsite = "https://sofworld.org",
            AcademicYear = 2026, LastVerified = verifiedAt
        },

        // ── HBCSE ────────────────────────────────────────────────────
        new()
        {
            OrgName = "HBCSE", OlympiadName = "IOQM", FullName = "Indian Olympiad Qualifier in Mathematics",
            Subject = "Math", Stage = "Stage 1", GradeMin = 8, GradeMax = 12,
            RegistrationWindow = "Jun – Jul 2026",
            ExamDateText = "September 6, 2026",
            ExamDateFrom = new DateTime(2026,9,6), ExamDateTo = new DateTime(2026,9,6),
            ResultDateText = "Oct 2026",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "Previously PRMO. Conducted by MTA. 30 questions, 3 hours. No negative marking.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "INMO", FullName = "Indian National Mathematics Olympiad",
            Subject = "Math", Stage = "Stage 2 (RMO → INMO)", GradeMin = 8, GradeMax = 12,
            RegistrationWindow = "N/A — qualify via IOQM/RMO",
            ExamDateText = "January 17, 2027",
            ExamDateFrom = new DateTime(2027,1,17), ExamDateTo = new DateTime(2027,1,17),
            ResultDateText = "Feb – Mar 2027",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "Top ~300 IOQM qualifiers write RMO (Regional MO) first; ~30–35 qualify for INMO.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "NSE (Physics)", FullName = "National Standard Examination in Physics",
            Subject = "Science", Stage = "Stage 1 (IPhO pathway)", GradeMin = 11, GradeMax = 12,
            RegistrationWindow = "Aug – Sep 2026",
            ExamDateText = "November 2026",
            ExamDateFrom = new DateTime(2026,11,29), ExamDateTo = new DateTime(2026,11,29),
            ResultDateText = "Dec 2026 – Jan 2027",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "80 MCQ, 2 hours. Top ~1% qualify for INPhO.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "NSE (Chemistry)", FullName = "National Standard Examination in Chemistry",
            Subject = "Science", Stage = "Stage 1 (IChO pathway)", GradeMin = 11, GradeMax = 12,
            RegistrationWindow = "Aug – Sep 2026",
            ExamDateText = "November 2026",
            ExamDateFrom = new DateTime(2026,11,29), ExamDateTo = new DateTime(2026,11,29),
            ResultDateText = "Dec 2026 – Jan 2027",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "Same day as NSE Physics. Conducted by IAPT. Top ~1% qualify for INChO.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "NSEJS", FullName = "National Standard Examination in Junior Science",
            Subject = "Science", Stage = "Stage 1 (IJSO pathway)", GradeMin = 8, GradeMax = 10,
            RegistrationWindow = "Aug – Sep 2026",
            ExamDateText = "November 2026",
            ExamDateFrom = new DateTime(2026,11,29), ExamDateTo = new DateTime(2026,11,29),
            ResultDateText = "Dec 2026",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            Notes = "International Junior Science Olympiad pathway. For Class 8–10 students.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "IOQJS", FullName = "Indian Olympiad Qualifier in Junior Science",
            Subject = "Science", Stage = "Stage 1 (IJSO pathway)", GradeMin = 8, GradeMax = 10,
            RegistrationWindow = "Jul – Aug 2026",
            ExamDateText = "October 2026",
            ExamDateFrom = new DateTime(2026,10,1), ExamDateTo = new DateTime(2026,10,31),
            ResultDateText = "Nov 2026",
            OfficialWebsite = "https://olympiads.hbcse.tifr.res.in",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "HBCSE", OlympiadName = "ZCO / IOQCS", FullName = "Zonal Computing Olympiad / Indian Olympiad Qualifier in Computer Science",
            Subject = "Computers", Stage = "Stage 1 (IOI pathway)", GradeMin = 8, GradeMax = 12,
            RegistrationWindow = "Sep – Oct 2026",
            ExamDateText = "December 2026",
            ExamDateFrom = new DateTime(2026,12,1), ExamDateTo = new DateTime(2026,12,31),
            ResultDateText = "Jan 2027",
            OfficialWebsite = "https://www.iarcs.org.in/inoi",
            Notes = "Online; multiple choice + short answer. Top scorers advance to INOI. Uses C/C++/Java/Python.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },

        // ── SilverZone ───────────────────────────────────────────────
        new()
        {
            OrgName = "SilverZone", OlympiadName = "iOM", FullName = "International Olympiad of Mathematics",
            Subject = "Math", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jun – Aug 2026",
            ExamDateText = "8 Oct, 18 Nov, 7 Dec 2026",
            ExamDateFrom = new DateTime(2026,10,8), ExamDateTo = new DateTime(2026,12,7),
            ResultDateText = "Feb 2027",
            OfficialWebsite = "https://silverzone.org",
            Notes = "35 questions, 60 minutes. Schools register in bulk. Individual prizes + merit certificates.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SilverZone", OlympiadName = "iOS", FullName = "International Olympiad of Science",
            Subject = "Science", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jun – Aug 2026",
            ExamDateText = "14 Oct, 19 Nov, 8 Dec 2026",
            ExamDateFrom = new DateTime(2026,10,14), ExamDateTo = new DateTime(2026,12,8),
            ResultDateText = "Feb 2027",
            OfficialWebsite = "https://silverzone.org",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SilverZone", OlympiadName = "iOEL", FullName = "International Olympiad of English Language",
            Subject = "English", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jun – Aug 2026",
            ExamDateText = "21 Oct, 26 Nov, 10 Dec 2026",
            ExamDateFrom = new DateTime(2026,10,21), ExamDateTo = new DateTime(2026,12,10),
            ResultDateText = "Feb 2027",
            OfficialWebsite = "https://silverzone.org",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SilverZone", OlympiadName = "iOIT", FullName = "International Olympiad of Information Technology",
            Subject = "Computers", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jun – Aug 2026",
            ExamDateText = "24 Sep, 22 Oct, 25 Nov 2026",
            ExamDateFrom = new DateTime(2026,9,24), ExamDateTo = new DateTime(2026,11,25),
            ResultDateText = "Feb 2027",
            OfficialWebsite = "https://silverzone.org",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "SilverZone", OlympiadName = "STEM", FullName = "Science Technology Engineering Mathematics Olympiad",
            Subject = "Science", Stage = "Single Level", GradeMin = 6, GradeMax = 12,
            RegistrationWindow = "Jun – Aug 2026",
            ExamDateText = "Oct – Dec 2026",
            ExamDateFrom = new DateTime(2026,10,1), ExamDateTo = new DateTime(2026,12,31),
            ResultDateText = "Feb 2027",
            OfficialWebsite = "https://silverzone.org",
            AcademicYear = 2026, LastVerified = verifiedAt
        },

        // ── Unified Council ──────────────────────────────────────────
        new()
        {
            OrgName = "Unified", OlympiadName = "NSTSE", FullName = "National Level Science Talent Search Examination",
            Subject = "Science", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Oct 2026",
            ExamDateText = "Jan – Feb 2027",
            ExamDateFrom = new DateTime(2027,1,1), ExamDateTo = new DateTime(2027,2,28),
            ResultDateText = "Mar – Apr 2027",
            OfficialWebsite = "https://unifiedcouncil.com",
            Notes = "Diagnostic-style, NCERT-based. Awarded from Class 1. Scholarships for toppers.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "Unified", OlympiadName = "UIEO", FullName = "Unified International English Olympiad",
            Subject = "English", Stage = "Single Level", GradeMin = 1, GradeMax = 12,
            RegistrationWindow = "Jul – Oct 2026",
            ExamDateText = "Jan – Feb 2027",
            ExamDateFrom = new DateTime(2027,1,1), ExamDateTo = new DateTime(2027,2,28),
            ResultDateText = "Mar – Apr 2027",
            OfficialWebsite = "https://unifiedcouncil.com",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "Unified", OlympiadName = "UCO", FullName = "Unified Cyber Olympiad",
            Subject = "Computers", Stage = "Single Level", GradeMin = 3, GradeMax = 12,
            RegistrationWindow = "Jul – Oct 2026",
            ExamDateText = "Nov 2026",
            ExamDateFrom = new DateTime(2026,11,1), ExamDateTo = new DateTime(2026,11,30),
            ResultDateText = "Jan 2027",
            OfficialWebsite = "https://unifiedcouncil.com",
            AcademicYear = 2026, LastVerified = verifiedAt
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
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "CREST", OlympiadName = "CSO", FullName = "CREST Science Olympiad",
            Subject = "Science", Stage = "Single Level", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Open year-round",
            ExamDateText = "Online, on-demand scheduling",
            OfficialWebsite = "https://crestolympiads.com",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "CREST", OlympiadName = "CEO", FullName = "CREST English Olympiad",
            Subject = "English", Stage = "Single Level", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Open year-round",
            ExamDateText = "Online, on-demand scheduling",
            OfficialWebsite = "https://crestolympiads.com",
            AcademicYear = 2026, LastVerified = verifiedAt
        },

        // ── SEAMO ────────────────────────────────────────────────────
        new()
        {
            OrgName = "SEAMO", OlympiadName = "SEAMO", FullName = "Southeast Asian Mathematical Olympiad",
            Subject = "Math", Stage = "Paper A/B/C/D/E/X", GradeMin = 4, GradeMax = 12,
            RegistrationWindow = "Jun – Oct 2026",
            ExamDateText = "November 2026",
            ExamDateFrom = new DateTime(2026,11,1), ExamDateTo = new DateTime(2026,11,30),
            ResultDateText = "Jan 2027",
            OfficialWebsite = "https://seamo-official.org",
            Notes = "Multiple difficulty papers (A=easiest, X=hardest/invited). Awards at regional + international level.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },

        // ── ICO (Computing) ─────────────────────────────────────────
        new()
        {
            OrgName = "ICO", OlympiadName = "INOI", FullName = "Indian National Olympiad in Informatics",
            Subject = "Computers", Stage = "Stage 2 (after ZCO/IOQCS)", GradeMin = 8, GradeMax = 12,
            RegistrationWindow = "N/A — qualify via ZCO",
            ExamDateText = "January 2027",
            ExamDateFrom = new DateTime(2027,1,1), ExamDateTo = new DateTime(2027,1,31),
            ResultDateText = "Feb 2027",
            OfficialWebsite = "https://www.iarcs.org.in/inoi",
            Notes = "Top ~200 from ZCO advance. INOI qualifiers attend IOITC camp for IOI team selection.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },

        // ── Amar Ujala National Olympiads (AUNO) ────────────────────
        new()
        {
            OrgName = "AmarUjala", OlympiadName = "AUNO English", FullName = "National English Olympiad by Amar Ujala",
            Subject = "English", Stage = "Level 1", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Open now (Early-bird until 15 Jul 2026)",
            ExamDateText = "23 Sep 2026 / 18 Nov 2026",
            ExamDateFrom = new DateTime(2026,9,23), ExamDateTo = new DateTime(2026,11,18),
            ResultDateText = "After Level 2 (Feb 2027)",
            OfficialWebsite = "https://amarujalaolympiad.com",
            Notes = "New 2026-27 Olympiad by Amar Ujala media group. Individual registration (₹200/subject).",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "AmarUjala", OlympiadName = "AUNO Mathematics", FullName = "National Mathematics Olympiad by Amar Ujala",
            Subject = "Math", Stage = "Level 1", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Open now (Early-bird until 15 Jul 2026)",
            ExamDateText = "28 Sep 2026 / 23 Nov 2026",
            ExamDateFrom = new DateTime(2026,9,28), ExamDateTo = new DateTime(2026,11,23),
            ResultDateText = "After Level 2 (Feb 2027)",
            OfficialWebsite = "https://amarujalaolympiad.com",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "AmarUjala", OlympiadName = "AUNO Science", FullName = "National Science Olympiad by Amar Ujala",
            Subject = "Science", Stage = "Level 1", GradeMin = 3, GradeMax = 10,
            RegistrationWindow = "Open now (Early-bird until 15 Jul 2026)",
            ExamDateText = "25 Sep 2026 / 25 Nov 2026",
            ExamDateFrom = new DateTime(2026,9,25), ExamDateTo = new DateTime(2026,11,25),
            ResultDateText = "After Level 2 (Feb 2027)",
            OfficialWebsite = "https://amarujalaolympiad.com",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "AmarUjala", OlympiadName = "AUNO GK", FullName = "National General Knowledge Olympiad by Amar Ujala",
            Subject = "General Knowledge", Stage = "Level 1", GradeMin = 3, GradeMax = 10,
            RegistrationWindow = "Open now (Early-bird until 15 Jul 2026)",
            ExamDateText = "21 Sep 2026 / 19 Nov 2026",
            ExamDateFrom = new DateTime(2026,9,21), ExamDateTo = new DateTime(2026,11,19),
            ResultDateText = "After Level 2 (Feb 2027)",
            OfficialWebsite = "https://amarujalaolympiad.com",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "AmarUjala", OlympiadName = "AUNO Logical Reasoning", FullName = "National Logical Reasoning Olympiad by Amar Ujala",
            Subject = "Logical Reasoning", Stage = "Level 1", GradeMin = 3, GradeMax = 10,
            RegistrationWindow = "Open now (Early-bird until 15 Jul 2026)",
            ExamDateText = "22 Sep 2026 / 26 Nov 2026",
            ExamDateFrom = new DateTime(2026,9,22), ExamDateTo = new DateTime(2026,11,26),
            ResultDateText = "After Level 2 (Feb 2027)",
            OfficialWebsite = "https://amarujalaolympiad.com",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "AmarUjala", OlympiadName = "AUNO Hindi", FullName = "National Hindi Olympiad by Amar Ujala",
            Subject = "Hindi", Stage = "Level 1", GradeMin = 3, GradeMax = 10,
            RegistrationWindow = "Open now (Early-bird until 15 Jul 2026)",
            ExamDateText = "29 Sep 2026 / 27 Nov 2026",
            ExamDateFrom = new DateTime(2026,9,29), ExamDateTo = new DateTime(2026,11,27),
            ResultDateText = "After Level 2 (Feb 2027)",
            OfficialWebsite = "https://amarujalaolympiad.com",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "AmarUjala", OlympiadName = "AUNO Tech & AI", FullName = "National Tech & AI Olympiad by Amar Ujala",
            Subject = "Computers", Stage = "Level 1 (Online)", GradeMin = 3, GradeMax = 10,
            RegistrationWindow = "Open now (Early-bird until 15 Jul 2026)",
            ExamDateText = "Dates TBA",
            ResultDateText = "After Level 2 (Feb 2027)",
            OfficialWebsite = "https://amarujalaolympiad.com",
            Notes = "Online-only exam. Dates to be announced.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
        new()
        {
            OrgName = "AmarUjala", OlympiadName = "AUNO Finals", FullName = "National Olympiad Level 2 Finals by Amar Ujala",
            Subject = "Multiple", Stage = "Level 2 (Finals)", GradeMin = 1, GradeMax = 10,
            RegistrationWindow = "Qualify via Level 1",
            ExamDateText = "Feb 2027 (2nd/3rd week, tentative)",
            ExamDateFrom = new DateTime(2027,2,8), ExamDateTo = new DateTime(2027,2,22),
            ResultDateText = "Mar 2027",
            OfficialWebsite = "https://amarujalaolympiad.com",
            Notes = "Champions, National, State, District & School Toppers announced. Individual registration — no school required.",
            AcademicYear = 2026, LastVerified = verifiedAt
        },
    ];
}
