using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OlympiadReady.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddQuestionReporting : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "ReportedQuestions",
                columns: table => new
                {
                    ReportId = table.Column<Guid>(type: "uniqueidentifier", nullable: false, defaultValueSql: "NEWID()"),
                    UserId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    QuestionBankId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Category = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Description = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: false),
                    Status = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    AdminReason = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    ReportedAt = table.Column<DateTime>(type: "datetime2", nullable: false, defaultValueSql: "GETDATE()"),
                    ResolvedAt = table.Column<DateTime>(type: "datetime2", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ReportedQuestions", x => x.ReportId);
                    table.ForeignKey(
                        name: "FK_ReportedQuestions_QuestionBank_QuestionBankId",
                        column: x => x.QuestionBankId,
                        principalTable: "QuestionBank",
                        principalColumn: "QuestionBankId",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ReportedQuestions_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "UserId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "UserNotifications",
                columns: table => new
                {
                    NotificationId = table.Column<Guid>(type: "uniqueidentifier", nullable: false, defaultValueSql: "NEWID()"),
                    UserId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    Message = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: false),
                    IsRead = table.Column<bool>(type: "bit", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, defaultValueSql: "GETDATE()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserNotifications", x => x.NotificationId);
                    table.ForeignKey(
                        name: "FK_UserNotifications_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "UserId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_ReportedQuestions_QuestionBankId",
                table: "ReportedQuestions",
                column: "QuestionBankId");

            migrationBuilder.CreateIndex(
                name: "IX_ReportedQuestions_Status",
                table: "ReportedQuestions",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_ReportedQuestions_UserId",
                table: "ReportedQuestions",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_UserNotifications_UserId_IsRead",
                table: "UserNotifications",
                columns: new[] { "UserId", "IsRead" });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "ReportedQuestions");

            migrationBuilder.DropTable(
                name: "UserNotifications");
        }
    }
}
