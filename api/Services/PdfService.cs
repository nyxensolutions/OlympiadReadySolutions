using System.Text.RegularExpressions;
using OlympiadReady.Api.Models;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace OlympiadReady.Api.Services;

public class PdfService
{
    private const string Brand   = "#2563eb";
    private const string Achiever = "#f59e0b";
    private const string DarkText = "#1e293b";
    private const string SubText  = "#64748b";
    private const string LightBg  = "#f8fafc";
    private const string BorderGray = "#e2e8f0";
    private const string CorrectGreen = "#16a34a";
    private const string WrongRed    = "#dc2626";

    private readonly string? _logoPath;
    private readonly IWebHostEnvironment _env;
    private static readonly HttpClient _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };

    public PdfService(IWebHostEnvironment env)
    {
        _env = env;
        var candidate = Path.Combine(env.WebRootPath, "logo.png");
        _logoPath = File.Exists(candidate) ? candidate : null;
    }

    /// <summary>
    /// Returns the raw bytes for an image URL — downloading from HTTP/HTTPS or reading from local disk.
    /// Returns null if the image cannot be loaded.
    /// </summary>
    private byte[]? GetImageBytes(string url)
    {
        try
        {
            if (url.StartsWith("http://", StringComparison.OrdinalIgnoreCase) ||
                url.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
            {
                return _httpClient.GetByteArrayAsync(url).GetAwaiter().GetResult();
            }

            var localPath = Path.Combine(_env.ContentRootPath, "..", "web", "public", url.TrimStart('/'));
            return File.Exists(localPath) ? File.ReadAllBytes(localPath) : null;
        }
        catch
        {
            return null;
        }
    }

    public byte[] GeneratePaperPdf(PdfExportRequest data)
    {
        var doc = Document.Create(c =>
        {
            // ── Page 1-N: Questions ───────────────────────────────
            c.Page(p =>
            {
                p.Size(PageSizes.A4);
                p.Margin(40);
                p.DefaultTextStyle(t => t.FontSize(11).FontFamily(Fonts.Calibri).FontColor(DarkText));

                p.Header().Element(container => BuildHeader(container, data));
                p.Content().Element(container => BuildBody(container, data));
                p.Footer().Element(BuildFooter);
            });

            // ── OMR Answer Sheet (blank — student fills this in) ──
            c.Page(p =>
            {
                p.Size(PageSizes.A4);
                p.Margin(40);
                p.DefaultTextStyle(t => t.FontSize(11).FontFamily(Fonts.Calibri).FontColor(DarkText));

                p.Header().Element(container => BuildOmrHeader(container, data));
                p.Content().Element(container => BuildOmrSheet(container, data));
                p.Footer().Element(BuildFooter);
            });

            // ── Final page: Answer Key & Explanations ────────────
            c.Page(p =>
            {
                p.Size(PageSizes.A4);
                p.Margin(40);
                p.DefaultTextStyle(t => t.FontSize(11).FontFamily(Fonts.Calibri).FontColor(DarkText));

                p.Header().Element(container => BuildAnswerKeyHeader(container, data));
                p.Content().Element(container => BuildAnswerKey(container, data));
                p.Footer().Element(BuildFooter);
            });
        });

        return doc.GeneratePdf();
    }

    // ── Header ─────────────────────────────────────────────────────────────────

    private void BuildHeader(IContainer container, PdfExportRequest d)
    {
        container
            .BorderBottom(2).BorderColor(Brand)
            .PaddingBottom(10)
            .Row(row =>
            {
                // Logo block
                row.ConstantItem(70).Column(col =>
                {
                    if (_logoPath != null)
                        col.Item().Height(64).Width(64).Image(_logoPath).FitArea();
                    else
                        col.Item().Height(64).Width(64)
                           .Background(Brand).AlignCenter().AlignMiddle()
                           .Text("OR").Bold().FontSize(18).FontColor(Colors.White);
                });

                row.ConstantItem(10);

                // Title block
                row.RelativeItem().Column(col =>
                {
                    col.Item().Text("OlympiadReady").FontSize(18).Bold().FontColor(Brand);
                    col.Item().Text(d.Title).FontSize(11).FontColor(SubText).SemiBold();
                });

                // Metadata block
                row.ConstantItem(160).AlignRight().Column(col =>
                {
                    col.Item().AlignRight().Text($"Class {d.Grade}  ·  {d.Subject}").SemiBold().FontSize(10);
                    col.Item().AlignRight().Text($"Level: {d.Difficulty}").FontColor(SubText).FontSize(9);
                    col.Item().AlignRight().Text($"{d.Questions.Count} Questions  ·  All MCQ").FontColor(SubText).FontSize(9);
                    col.Item().AlignRight().Text($"Generated: {DateTime.Today:dd MMM yyyy}").FontColor(SubText).FontSize(8);
                });
            });
    }

    private void BuildOmrHeader(IContainer container, PdfExportRequest d)
    {
        container
            .BorderBottom(2).BorderColor(DarkText)
            .PaddingBottom(10)
            .Row(row =>
            {
                row.ConstantItem(70).Column(col =>
                {
                    if (_logoPath != null)
                        col.Item().Height(64).Width(64).Image(_logoPath).FitArea();
                    else
                        col.Item().Height(64).Width(64)
                           .Background(Brand).AlignCenter().AlignMiddle()
                           .Text("OR").Bold().FontSize(18).FontColor(Colors.White);
                });

                row.ConstantItem(10);

                row.RelativeItem().Column(col =>
                {
                    col.Item().Text("OlympiadReady").FontSize(18).Bold().FontColor(Brand);
                    col.Item().Text("OMR Answer Sheet").FontSize(13).SemiBold().FontColor(DarkText);
                    col.Item().PaddingTop(2).Text("Fill one bubble per question. Use a ball-point pen.").FontSize(9).FontColor(SubText);
                });

                row.ConstantItem(160).AlignRight().Column(col =>
                {
                    col.Item().AlignRight().Text($"Class {d.Grade}  ·  {d.Subject}").SemiBold().FontSize(10);
                    col.Item().AlignRight().Text($"Level: {d.Difficulty}").FontColor(SubText).FontSize(9);
                    col.Item().AlignRight().Text($"{d.Questions.Count} Questions").FontColor(SubText).FontSize(9);
                });
            });
    }

    private static void BuildOmrSheet(IContainer container, PdfExportRequest d)
    {
        container.PaddingTop(16).Column(col =>
        {
            // Student info box
            col.Item()
               .Border(1).BorderColor(BorderGray)
               .Background(LightBg)
               .Padding(10)
               .Column(info =>
               {
                   info.Item().Row(row =>
                   {
                       row.RelativeItem().Column(c =>
                       {
                           c.Item().Text("Student Name: ____________________________________").FontSize(10);
                           c.Item().PaddingTop(6).Text("Roll No / Seat No: __________________________").FontSize(10);
                       });
                       row.ConstantItem(20);
                       row.ConstantItem(140).Column(c =>
                       {
                           c.Item().Text("Date: ________________________").FontSize(10);
                           c.Item().PaddingTop(6).Text("Score: __________ / " + d.Questions.Count).FontSize(10);
                       });
                   });
               });

            col.Item().PaddingTop(8).Text(t =>
            {
                t.Span("Instructions: ").Bold().FontSize(9);
                t.Span("Darken the bubble corresponding to your answer completely. Do NOT tick, cross or half-fill. Use only blue/black ink.").FontSize(9).FontColor(SubText);
            });

            // OMR grid — 2 columns of questions side by side
            col.Item().PaddingTop(14).Column(grid =>
            {
                const int cols = 2;
                var rowCount = (int)Math.Ceiling(d.Questions.Count / (double)cols);

                for (var r = 0; r < rowCount; r++)
                {
                    var rowIndex = r;
                    grid.Item().PaddingBottom(4).Row(rowContainer =>
                    {
                        for (var c = 0; c < cols; c++)
                        {
                            var qIdx = rowIndex * cols + c;

                            if (qIdx >= d.Questions.Count)
                            {
                                rowContainer.RelativeItem();
                                continue;
                            }

                            var qNum = qIdx + 1;

                            if (c > 0)
                                rowContainer.ConstantItem(20);

                            rowContainer.RelativeItem().Border(1).BorderColor(BorderGray).Padding(5).Row(qRow =>
                            {
                                // Question number
                                qRow.ConstantItem(28)
                                    .AlignMiddle()
                                    .Text($"Q{qNum}").Bold().FontSize(10).FontColor(Brand);

                                // Bubbles A B C D
                                foreach (var letter in new[] { "A", "B", "C", "D" })
                                {
                                    var l = letter;
                                    qRow.ConstantItem(30).AlignMiddle().AlignCenter().Column(bCol =>
                                    {
                                        bCol.Item().AlignCenter()
                                            .Text(l).FontSize(8).FontColor(SubText).SemiBold();
                                        bCol.Item().AlignCenter()
                                            .Text("○").FontSize(16).FontColor(DarkText);
                                    });
                                }
                            });
                        }
                    });
                }
            });

            // Legend
            col.Item().PaddingTop(12).Text(t =>
            {
                t.Span("⬤ Fill the bubble completely   ").FontSize(9).FontColor(SubText);
                t.Span("○ Unfilled = Not attempted   ").FontSize(9).FontColor(SubText);
                t.Span("Each correct answer = 1 mark  ·  No negative marking").FontSize(9).FontColor(SubText);
            });
        });
    }

    private void BuildAnswerKeyHeader(IContainer container, PdfExportRequest d)
    {
        container
            .BorderBottom(2).BorderColor(Achiever)
            .PaddingBottom(10)
            .Row(row =>
            {
                row.ConstantItem(70).Column(col =>
                {
                    if (_logoPath != null)
                        col.Item().Height(64).Width(64).Image(_logoPath).FitArea();
                    else
                        col.Item().Height(64).Width(64)
                           .Background(Brand).AlignCenter().AlignMiddle()
                           .Text("OR").Bold().FontSize(18).FontColor(Colors.White);
                });

                row.ConstantItem(10);

                row.RelativeItem().Column(col =>
                {
                    col.Item().Text("OlympiadReady").FontSize(18).Bold().FontColor(Brand);
                    col.Item().Text("Answer Key & Explanations").FontSize(13).SemiBold().FontColor(Achiever);
                });

                row.ConstantItem(160).AlignRight().Column(col =>
                {
                    col.Item().AlignRight().Text($"Class {d.Grade}  ·  {d.Subject}").SemiBold().FontSize(10);
                    col.Item().AlignRight().Text($"Level: {d.Difficulty}").FontColor(SubText).FontSize(9);
                });
            });
    }

    // ── Footer ─────────────────────────────────────────────────────────────────

    private static void BuildFooter(IContainer container)
    {
        container
            .BorderTop(1).BorderColor(BorderGray)
            .PaddingTop(6)
            .Row(row =>
            {
                row.RelativeItem().AlignLeft().Text(t =>
                {
                    t.Span($"© {DateTime.Today.Year} OlympiadReady. All rights reserved.").FontSize(8).FontColor(SubText);
                });
                row.RelativeItem().AlignCenter().Text(t =>
                {
                    t.Span("www.olympiadready.com").FontSize(8).FontColor(SubText);
                });
                row.RelativeItem().AlignRight().Text(t =>
                {
                    t.Span("Page ").FontSize(8).FontColor(SubText);
                    t.CurrentPageNumber().FontSize(8).FontColor(SubText);
                    t.Span(" of ").FontSize(8).FontColor(SubText);
                    t.TotalPages().FontSize(8).FontColor(SubText);
                });
            });
    }

    // ── Questions body ─────────────────────────────────────────────────────────

    private void BuildBody(IContainer container, PdfExportRequest d)
    {
        container.PaddingTop(16).Column(col =>
        {
            col.Spacing(14);

            // Instructions box
            col.Item()
               .Background(LightBg)
               .Border(1).BorderColor(BorderGray)
               .Padding(10)
               .Text(t =>
               {
                   t.Span("Instructions: ").Bold().FontSize(9);
                   t.Span("Each question has one correct answer. Circle the letter of your choice. No negative marking unless specified.").FontSize(9).FontColor(SubText);
               });

            for (var i = 0; i < d.Questions.Count; i++)
                col.Item().Element(e => RenderQuestion(e, i + 1, d.Questions[i]));
        });
    }

    private void RenderQuestion(IContainer container, int number, Question q)
    {
        container
            .Border(1).BorderColor(BorderGray)
            .Background(Colors.White)
            .Padding(10)
            .Column(col =>
            {
                // Question text
                col.Item().Row(r =>
                {
                    r.ConstantItem(28).Text($"Q{number}.").Bold().FontColor(Brand).FontSize(11);
                    RenderMarkdownContent(r.RelativeItem(), q.Q, 11);
                });

                if (!string.IsNullOrWhiteSpace(q.ImageUrl))
                {
                    var imgBytes = GetImageBytes(q.ImageUrl);
                    if (imgBytes != null)
                    {
                        col.Item().PaddingTop(8).PaddingLeft(22).Height(120).Image(imgBytes).FitArea();
                    }
                }

                // Options grid (2 columns)
                col.Item().PaddingTop(6).PaddingLeft(22).Row(row =>
                {
                    row.RelativeItem().Column(optCol =>
                    {
                        for (var i = 0; i < q.Options.Count; i += 2)
                        {
                            var letter = (char)('A' + i);
                            optCol.Item().PaddingBottom(4).Row(r => 
                            {
                                r.ConstantItem(24).Text($"({letter})").FontSize(10).FontColor(SubText);
                                RenderMarkdownContent(r.RelativeItem(), q.Options[i], 10, SubText);
                            });
                        }
                    });
                    row.RelativeItem().Column(optCol =>
                    {
                        for (var i = 1; i < q.Options.Count; i += 2)
                        {
                            var letter = (char)('A' + i);
                            optCol.Item().PaddingBottom(4).Row(r => 
                            {
                                r.ConstantItem(24).Text($"({letter})").FontSize(10).FontColor(SubText);
                                RenderMarkdownContent(r.RelativeItem(), q.Options[i], 10, SubText);
                            });
                        }
                    });
                });
            });
    }

    // ── Answer Key body ────────────────────────────────────────────────────────

    private void BuildAnswerKey(IContainer container, PdfExportRequest d)
    {
        container.PaddingTop(16).Column(col =>
        {
            col.Spacing(10);

            // Quick answer grid first
            col.Item().Column(grid =>
            {
                grid.Item()
                    .Background(Brand).Padding(8)
                    .Text("Quick Answer Reference").Bold().FontSize(11).FontColor(Colors.White);

                grid.Item()
                    .Border(1).BorderColor(BorderGray)
                    .Padding(8)
                    .Column(gc =>
                    {
                        var rows = (int)Math.Ceiling(d.Questions.Count / 5.0);
                        for (var r = 0; r < rows; r++)
                        {
                            var rowIdx = r;
                            gc.Item().Row(row =>
                            {
                                for (var c = 0; c < 5; c++)
                                {
                                    var idx = rowIdx * 5 + c;
                                    if (idx >= d.Questions.Count) break;
                                    var q = d.Questions[idx];
                                    var ansIdx = q.Options.IndexOf(q.Answer);
                                    var letter = ansIdx >= 0 ? ((char)('A' + ansIdx)).ToString() : "?";
                                    var colIdx = c;
                                    row.RelativeItem().Text(t =>
                                    {
                                        t.Span($"Q{idx + 1}: ").FontSize(9).FontColor(SubText);
                                        t.Span(letter).Bold().FontSize(9).FontColor(CorrectGreen);
                                        if (colIdx < 4) t.Span("   ").FontSize(9);
                                    });
                                }
                            });
                        }
                    });
            });

            // Detailed explanations
            col.Item()
               .Background(Achiever).Padding(8)
               .Text("Detailed Explanations").Bold().FontSize(11).FontColor(Colors.White);

            for (var i = 0; i < d.Questions.Count; i++)
            {
                var n = i + 1;
                var q = d.Questions[i];
                var ansIdx = q.Options.IndexOf(q.Answer);
                var ansLetter = ansIdx >= 0 ? ((char)('A' + ansIdx)).ToString() : "?";

                col.Item()
                   .Border(1).BorderColor(BorderGray)
                   .Column(c =>
                   {
                        // Question header bar
                       c.Item()
                        .Background(LightBg)
                        .Padding(8)
                        .Row(r =>
                        {
                            r.ConstantItem(28).Text($"Q{n}.").Bold().FontColor(Brand);
                            RenderMarkdownContent(r.RelativeItem(), q.Q, 10);
                        });

                       // Answer + explanation
                       c.Item().Padding(8).Column(inner =>
                       {
                           inner.Item().Text(t =>
                           {
                               t.Span("Correct Answer: ").Bold().FontSize(10);
                               t.Span($"({ansLetter}) ").FontSize(10).FontColor(CorrectGreen).Bold();
                           });
                           RenderMarkdownContent(inner.Item(), q.Answer, 10, CorrectGreen, true);
                           
                           inner.Item().PaddingTop(4).Element(e => RenderMarkdownContent(e, q.Explanation, 9.5f, SubText));
                       });
                   });
            }

            // Copyright footer on answer key page
            col.Item().PaddingTop(12).Text(t =>
            {
                t.Span("This practice paper was generated by OlympiadReady (www.olympiadready.com). ")
                 .FontSize(8).FontColor(SubText);
                t.Span($"© {DateTime.Today.Year} OlympiadReady. Reproduction for personal educational use is permitted. ")
                 .FontSize(8).FontColor(SubText);
                t.Span("Commercial reproduction or redistribution is prohibited.")
                 .FontSize(8).FontColor(SubText);
            });
        });
    }

    // Matches a bare image URL on its own — http(s)://... ending with a known image extension,
    // OR any Cloudinary URL (res.cloudinary.com) regardless of extension.
    private static readonly Regex _bareImageUrlRx = new(
        @"^https?://\S+\.(?:png|jpg|jpeg|gif|webp|svg|bmp)(\?\S*)?$|^https?://res\.cloudinary\.com/\S+$",
        RegexOptions.IgnoreCase | RegexOptions.Compiled);

    private void RenderMarkdownContent(IContainer container, string text, float fontSize = 11, string? fontColor = null, bool isBold = false)
    {
        // Split on both markdown images ![alt](url) AND bare image URLs
        var parts = Regex.Split(text, @"(!\[.*?\]\(.*?\)|https?://(?:res\.cloudinary\.com/\S+|\S+\.(?:png|jpg|jpeg|gif|webp|svg|bmp)(?:\?\S*)?))");
        container.Column(col =>
        {
            foreach (var part in parts)
            {
                if (string.IsNullOrEmpty(part)) continue;

                // Check for markdown image syntax: ![alt](url)
                var mdMatch = Regex.Match(part, @"!\[.*?\]\((.*?)\)");
                if (mdMatch.Success)
                {
                    var imgUrl = mdMatch.Groups[1].Value;
                    var imgBytes = GetImageBytes(imgUrl);
                    if (imgBytes != null)
                        col.Item().PaddingTop(4).PaddingBottom(4).Height(80).Image(imgBytes).FitArea();
                    continue;
                }

                // Check for bare image URL
                if (_bareImageUrlRx.IsMatch(part.Trim()))
                {
                    var imgBytes = GetImageBytes(part.Trim());
                    if (imgBytes != null)
                    {
                        col.Item().PaddingTop(4).PaddingBottom(4).Height(80).Image(imgBytes).FitArea();
                        continue;
                    }
                    // If download failed, fall through and render as text
                }

                col.Item().Text(t =>
                {
                    var span = t.Span(part).FontSize(fontSize);
                    if (fontColor != null) span.FontColor(fontColor);
                    if (isBold) span.Bold();
                });
            }
        });
    }
}
