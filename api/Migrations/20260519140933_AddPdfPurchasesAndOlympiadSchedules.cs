using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OlympiadReady.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddPdfPurchasesAndOlympiadSchedules : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "OlympiadSchedules",
                columns: table => new
                {
                    OlympiadScheduleId = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    OrgName = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    OlympiadName = table.Column<string>(type: "nvarchar(150)", maxLength: 150, nullable: false),
                    FullName = table.Column<string>(type: "nvarchar(300)", maxLength: 300, nullable: false),
                    Subject = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Stage = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    GradeMin = table.Column<int>(type: "int", nullable: true),
                    GradeMax = table.Column<int>(type: "int", nullable: true),
                    RegistrationWindow = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    ExamDateText = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    ExamDateFrom = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ExamDateTo = table.Column<DateTime>(type: "datetime2", nullable: true),
                    ResultDateText = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: true),
                    OfficialWebsite = table.Column<string>(type: "nvarchar(300)", maxLength: 300, nullable: true),
                    Notes = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    AcademicYear = table.Column<int>(type: "int", nullable: false),
                    LastVerified = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_OlympiadSchedules", x => x.OlympiadScheduleId);
                });

            migrationBuilder.CreateTable(
                name: "PdfPurchases",
                columns: table => new
                {
                    PdfPurchaseId = table.Column<Guid>(type: "uniqueidentifier", nullable: false, defaultValueSql: "NEWID()"),
                    UserId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Grade = table.Column<int>(type: "int", nullable: false),
                    Subject = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    RazorpayOrderId = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    RazorpayPaymentId = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    PurchasedAt = table.Column<DateTime>(type: "datetime2", nullable: false, defaultValueSql: "GETDATE()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PdfPurchases", x => x.PdfPurchaseId);
                    table.ForeignKey(
                        name: "FK_PdfPurchases_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "UserId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_OlympiadSchedules_AcademicYear_OrgName",
                table: "OlympiadSchedules",
                columns: new[] { "AcademicYear", "OrgName" });

            migrationBuilder.CreateIndex(
                name: "IX_PdfPurchases_UserId_Grade_Subject",
                table: "PdfPurchases",
                columns: new[] { "UserId", "Grade", "Subject" });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "OlympiadSchedules");

            migrationBuilder.DropTable(
                name: "PdfPurchases");
        }
    }
}
