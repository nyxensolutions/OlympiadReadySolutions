using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OlympiadReady.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddSchoolsAndTrial : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Schools",
                columns: table => new
                {
                    SchoolId = table.Column<Guid>(type: "uniqueidentifier", nullable: false, defaultValueSql: "NEWID()"),
                    Name = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: false),
                    City = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    LogoUrl = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true),
                    InviteCode = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false),
                    PilotEndsAt = table.Column<DateTime>(type: "datetime2", nullable: true),
                    SeatLimit = table.Column<int>(type: "int", nullable: false, defaultValue: 20),
                    ContactEmail = table.Column<string>(type: "nvarchar(255)", maxLength: 255, nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, defaultValueSql: "GETUTCDATE()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Schools", x => x.SchoolId);
                });

            migrationBuilder.AddColumn<Guid>(
                name: "SchoolId",
                table: "Users",
                type: "uniqueidentifier",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "SchoolJoinedAt",
                table: "Users",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "TrialExpiresAt",
                table: "Users",
                type: "datetime2",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_Users_SchoolId",
                table: "Users",
                column: "SchoolId");

            migrationBuilder.CreateIndex(
                name: "IX_Schools_InviteCode",
                table: "Schools",
                column: "InviteCode",
                unique: true);

            migrationBuilder.AddForeignKey(
                name: "FK_Users_Schools_SchoolId",
                table: "Users",
                column: "SchoolId",
                principalTable: "Schools",
                principalColumn: "SchoolId",
                onDelete: ReferentialAction.SetNull);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Users_Schools_SchoolId",
                table: "Users");

            migrationBuilder.DropIndex(
                name: "IX_Users_SchoolId",
                table: "Users");

            migrationBuilder.DropColumn(name: "SchoolId", table: "Users");
            migrationBuilder.DropColumn(name: "SchoolJoinedAt", table: "Users");
            migrationBuilder.DropColumn(name: "TrialExpiresAt", table: "Users");

            migrationBuilder.DropTable(name: "Schools");
        }
    }
}
