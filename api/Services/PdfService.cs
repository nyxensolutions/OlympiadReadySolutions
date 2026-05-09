using OlympiadReady.Api.Models;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace OlympiadReady.Api.Services;

public class PdfService
{
    private const string Brand = "#2563eb";
    private const string Achiever = "#f59e0b";

    public byte[] GeneratePaperPdf(PdfExportRequest data)
    {
        var doc = Document.Create(c =>
        {
            c.Page(p =>
            {
                p.Size(PageSizes.A4);
                p.Margin(36);
                p.DefaultTextStyle(t => t.FontSize(11).FontFamily(Fonts.Calibri));

                p.Header().Element(BuildHeader(data));
                p.Content().Element(BuildBody(data));
                p.Footer().AlignCenter().Text(t =>
                {
                    t.Span("Olympiad Ready · ").FontSize(9).FontColor(Colors.Grey.Medium);
                    t.CurrentPageNumber().FontSize(9);
                    t.Span(" / ").FontSize(9);
                    t.TotalPages().FontSize(9);
                });
            });

            c.Page(p =>
            {
                p.Size(PageSizes.A4);
                p.Margin(36);
                p.DefaultTextStyle(t => t.FontSize(11));

                p.Header().PaddingBottom(12).Text("Learning Key").FontSize(18).Bold().FontColor(Brand);
                p.Content().Element(BuildAnswerKey(data));
            });
        });

        return doc.GeneratePdf();
    }

    private static Action<IContainer> BuildHeader(PdfExportRequest d) => container =>
    {
        container.PaddingBottom(12).BorderBottom(1).BorderColor(Colors.Grey.Lighten2).PaddingBottom(8).Row(row =>
        {
            row.RelativeItem().Column(col =>
            {
                col.Item().Text("Olympiad Ready").FontSize(16).Bold().FontColor(Brand);
                col.Item().Text(d.Title).FontSize(11).FontColor(Colors.Grey.Darken1);
            });
            row.ConstantItem(180).AlignRight().Column(col =>
            {
                col.Item().Text($"Class {d.Grade} · {d.Subject}").SemiBold();
                col.Item().Text($"Level: {d.Difficulty}").FontColor(Colors.Grey.Darken1).FontSize(10);
                col.Item().Text($"Questions: {d.Questions.Count}").FontColor(Colors.Grey.Darken1).FontSize(10);
            });
        });
    };

    private static Action<IContainer> BuildBody(PdfExportRequest d) => container =>
    {
        container.PaddingTop(12).Column(col =>
        {
            col.Spacing(10);
            for (var i = 0; i < d.Questions.Count; i++)
            {
                var idx = i;
                var q = d.Questions[i];
                col.Item().Element(e => RenderQuestion(e, idx + 1, q));
            }
        });
    };

    private static void RenderQuestion(IContainer container, int number, Question q)
    {
        container.Column(col =>
        {
            col.Item().Row(r =>
            {
                r.AutoItem().PaddingRight(8).Text($"{number}.").Bold().FontColor(Brand);
                r.RelativeItem().Text(q.Q);
            });
            col.Item().PaddingLeft(20).PaddingTop(4).Column(opts =>
            {
                for (var i = 0; i < q.Options.Count; i++)
                {
                    var letter = ((char)('A' + i)).ToString();
                    opts.Item().Text($"({letter})  {q.Options[i]}").FontSize(10);
                }
            });
        });
    }

    private static Action<IContainer> BuildAnswerKey(PdfExportRequest d) => container =>
    {
        container.Column(col =>
        {
            col.Spacing(8);
            for (var i = 0; i < d.Questions.Count; i++)
            {
                var n = i + 1;
                var q = d.Questions[i];
                col.Item().Background(Colors.Grey.Lighten4).Padding(8).Column(c =>
                {
                    c.Item().Row(r =>
                    {
                        r.AutoItem().PaddingRight(6).Text($"Q{n}.").Bold().FontColor(Brand);
                        r.RelativeItem().Text(t =>
                        {
                            t.Span("Answer: ").Bold();
                            t.Span(q.Answer).FontColor(Achiever);
                        });
                    });
                    c.Item().PaddingTop(2).Text(q.Explanation).FontSize(10).FontColor(Colors.Grey.Darken2);
                });
            }
        });
    };
}
