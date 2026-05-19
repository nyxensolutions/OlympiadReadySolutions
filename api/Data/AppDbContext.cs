using Microsoft.EntityFrameworkCore;
using OlympiadReady.Api.Data.Entities;

namespace OlympiadReady.Api.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
    public DbSet<QuestionPaper> Papers => Set<QuestionPaper>();
    public DbSet<MockTestResult> Results => Set<MockTestResult>();
    public DbSet<Subscription> Subscriptions => Set<Subscription>();
    public DbSet<UserMastery> Mastery => Set<UserMastery>();
    public DbSet<QuestionBankItem> QuestionBank => Set<QuestionBankItem>();
    public DbSet<PdfPurchase> PdfPurchases => Set<PdfPurchase>();
    public DbSet<OlympiadSchedule> OlympiadSchedules => Set<OlympiadSchedule>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<User>(e =>
        {
            e.ToTable("Users");
            e.HasKey(x => x.UserId);
            e.Property(x => x.UserId).HasDefaultValueSql("NEWID()");
            e.Property(x => x.ExternalId).HasMaxLength(255);
            e.HasIndex(x => x.ExternalId)
                .IsUnique()
                .HasFilter("[ExternalId] IS NOT NULL");
            e.Property(x => x.Email).HasMaxLength(255).IsRequired();
            e.Property(x => x.FullName).HasMaxLength(255);
            e.Property(x => x.CreatedAt).HasDefaultValueSql("GETDATE()");
            e.Property(x => x.SubscriptionTier).HasMaxLength(50).HasDefaultValue("Free");
        });

        b.Entity<QuestionPaper>(e =>
        {
            e.ToTable("QuestionPapers");
            e.HasKey(x => x.PaperId);
            e.Property(x => x.PaperId).HasDefaultValueSql("NEWID()");
            e.Property(x => x.Title).HasMaxLength(255);
            e.Property(x => x.Subject).HasMaxLength(100);
            e.Property(x => x.DifficultyLevel).HasMaxLength(50);
            e.Property(x => x.CreatedAt).HasDefaultValueSql("GETDATE()");
            e.Property(x => x.ContentHash).HasMaxLength(64);
            e.HasIndex(x => x.ContentHash);
            e.HasOne(x => x.User)
                .WithMany(u => u.Papers)
                .HasForeignKey(x => x.UserId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        b.Entity<MockTestResult>(e =>
        {
            e.ToTable("MockTestResults");
            e.HasKey(x => x.ResultId);
            e.Property(x => x.ResultId).HasDefaultValueSql("NEWID()");
            e.Property(x => x.CompletedAt).HasDefaultValueSql("GETDATE()");
            e.HasOne(x => x.User)
                .WithMany(u => u.Results)
                .HasForeignKey(x => x.UserId)
                .OnDelete(DeleteBehavior.Restrict);
            e.HasOne(x => x.Paper)
                .WithMany()
                .HasForeignKey(x => x.PaperId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        b.Entity<Subscription>(e =>
        {
            e.ToTable("Subscriptions");
            e.HasKey(x => x.SubscriptionId);
            e.Property(x => x.SubscriptionId).HasDefaultValueSql("NEWID()");
            e.Property(x => x.PlanName).HasMaxLength(50).IsRequired();
            e.Property(x => x.IsActive)
                .HasComputedColumnSql("CASE WHEN [EndDate] > GETDATE() THEN CAST(1 AS BIT) ELSE CAST(0 AS BIT) END");
            e.HasIndex(x => new { x.UserId, x.EndDate });
            e.HasOne(x => x.User)
                .WithMany(u => u.Subscriptions)
                .HasForeignKey(x => x.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        b.Entity<UserMastery>(e =>
        {
            e.ToTable("UserMastery");
            e.HasKey(x => new { x.UserId, x.Subject, x.Topic });
            e.Property(x => x.Subject).HasMaxLength(100);
            e.Property(x => x.Topic).HasMaxLength(100);
            e.Property(x => x.MasteryScore).HasPrecision(5, 2);
            e.Property(x => x.LastUpdated).HasDefaultValueSql("GETDATE()");
            e.HasOne(x => x.User)
                .WithMany(u => u.Mastery)
                .HasForeignKey(x => x.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        b.Entity<PdfPurchase>(e =>
        {
            e.ToTable("PdfPurchases");
            e.HasKey(x => x.PdfPurchaseId);
            e.Property(x => x.PdfPurchaseId).HasDefaultValueSql("NEWID()");
            e.Property(x => x.Subject).HasMaxLength(100).IsRequired();
            e.Property(x => x.RazorpayOrderId).HasMaxLength(100);
            e.Property(x => x.RazorpayPaymentId).HasMaxLength(100);
            e.Property(x => x.PurchasedAt).HasDefaultValueSql("GETDATE()");
            e.HasIndex(x => new { x.UserId, x.Grade, x.Subject });
            e.HasOne(x => x.User)
                .WithMany(u => u.PdfPurchases)
                .HasForeignKey(x => x.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        b.Entity<OlympiadSchedule>(e =>
        {
            e.ToTable("OlympiadSchedules");
            e.HasKey(x => x.OlympiadScheduleId);
            e.Property(x => x.OrgName).HasMaxLength(100).IsRequired();
            e.Property(x => x.OlympiadName).HasMaxLength(150).IsRequired();
            e.Property(x => x.FullName).HasMaxLength(300).IsRequired();
            e.Property(x => x.Subject).HasMaxLength(100).IsRequired();
            e.Property(x => x.Stage).HasMaxLength(100);
            e.Property(x => x.RegistrationWindow).HasMaxLength(200);
            e.Property(x => x.ExamDateText).HasMaxLength(200);
            e.Property(x => x.ResultDateText).HasMaxLength(200);
            e.Property(x => x.OfficialWebsite).HasMaxLength(300);
            e.Property(x => x.Notes).HasMaxLength(500);
            e.HasIndex(x => new { x.AcademicYear, x.OrgName });
        });

        b.Entity<QuestionBankItem>(e =>
        {
            e.ToTable("QuestionBank");
            e.HasKey(x => x.QuestionBankId);
            e.Property(x => x.QuestionBankId).HasDefaultValueSql("NEWID()");
            e.Property(x => x.Subject).HasMaxLength(100).IsRequired();
            e.Property(x => x.Difficulty).HasMaxLength(50).IsRequired();
            e.Property(x => x.Topic).HasMaxLength(100).IsRequired();
            e.Property(x => x.SubTopic).HasMaxLength(150);
            e.Property(x => x.CorrectAnswer).HasMaxLength(1).IsRequired();
            e.Property(x => x.CreatedAt).HasDefaultValueSql("GETDATE()");

            // Composite index for the most common lookup: subject + grade + difficulty
            e.HasIndex(x => new { x.Subject, x.Grade, x.Difficulty });
            // Index for topic drill-down
            e.HasIndex(x => new { x.Subject, x.Grade, x.Difficulty, x.Topic });
        });
    }
}
