using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Models;
using OlympiadReady.Api.Services;

namespace OlympiadReady.Api.Controllers;

[ApiController]
[Route("api/export")]
public class ExportController : ControllerBase
{
    private readonly PdfService _pdf;
    private readonly AppDbContext _db;
    private readonly UserService _users;

    public ExportController(PdfService pdf, AppDbContext db, UserService users)
    {
        _pdf = pdf;
        _db = db;
        _users = users;
    }

    /// <summary>Render an arbitrary question set to PDF.</summary>
    [Authorize]
    [HttpPost("pdf")]
    public IActionResult Pdf([FromBody] PdfExportRequest req)
    {
        if (req.Questions.Count == 0)
            return BadRequest("Questions list is empty.");
        if (req.Questions.Count > 50)
            return BadRequest("Maximum of 50 questions allowed for export at a time.");

        var bytes = _pdf.GeneratePaperPdf(req);
        var filename = $"OlympiadReady-{req.Subject}-Class{req.Grade}-{req.Difficulty}.pdf";
        return File(bytes, "application/pdf", filename);
    }

    /// <summary>Render a saved paper to PDF. Caller must own the paper.</summary>
    [Authorize]
    [HttpGet("pdf/{paperId:guid}")]
    public async Task<IActionResult> PdfFromPaper(Guid paperId, CancellationToken ct)
    {
        var user = await _users.GetOrSyncAsync(User, ct);
        var paper = await _db.Papers.AsNoTracking().FirstOrDefaultAsync(p => p.PaperId == paperId, ct);
        if (paper is null) return NotFound();
        if (paper.UserId != user.UserId) return Forbid();

        var questions = JsonSerializer.Deserialize<List<Question>>(paper.JsonContent) ?? new();
        var bytes = _pdf.GeneratePaperPdf(new PdfExportRequest
        {
            Title = paper.Title ?? "Olympiad Ready Practice Paper",
            Subject = paper.Subject ?? "",
            Grade = paper.Grade,
            Difficulty = paper.DifficultyLevel ?? "",
            Questions = questions
        });

        var filename = $"OlympiadReady-{paper.Subject}-Class{paper.Grade}-{paper.DifficultyLevel}.pdf";
        return File(bytes, "application/pdf", filename);
    }
}
