using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OlympiadReady.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddUserSeenQuestions : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "PhysicalRewardClaims",
                columns: table => new
                {
                    ClaimId = table.Column<Guid>(type: "uniqueidentifier", nullable: false, defaultValueSql: "NEWID()"),
                    UserId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    RewardType = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Status = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false, defaultValue: "Pending"),
                    RequestedAt = table.Column<DateTime>(type: "datetime2", nullable: false, defaultValueSql: "GETDATE()"),
                    ShippedAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    AdminNotes = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    StudentName = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: true),
                    TrackingNumber = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PhysicalRewardClaims", x => x.ClaimId);
                    table.ForeignKey(
                        name: "FK_PhysicalRewardClaims_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "UserId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "UserSeenQuestions",
                columns: table => new
                {
                    Id = table.Column<int>(type: "int", nullable: false)
                        .Annotation("SqlServer:Identity", "1, 1"),
                    UserId = table.Column<string>(type: "nvarchar(200)", maxLength: 200, nullable: false),
                    QuestionBankId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    SeenAt = table.Column<DateTime>(type: "datetime2", nullable: false, defaultValueSql: "GETDATE()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserSeenQuestions", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_PhysicalRewardClaims_Status",
                table: "PhysicalRewardClaims",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_PhysicalRewardClaims_UserId_RewardType",
                table: "PhysicalRewardClaims",
                columns: new[] { "UserId", "RewardType" });

            migrationBuilder.CreateIndex(
                name: "IX_UserSeenQuestions_UserId_QuestionBankId",
                table: "UserSeenQuestions",
                columns: new[] { "UserId", "QuestionBankId" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "PhysicalRewardClaims");

            migrationBuilder.DropTable(
                name: "UserSeenQuestions");
        }
    }
}
