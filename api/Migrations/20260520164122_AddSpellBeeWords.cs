using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OlympiadReady.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddSpellBeeWords : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "SpellBeeWords",
                columns: table => new
                {
                    SpellBeeWordId = table.Column<Guid>(type: "uniqueidentifier", nullable: false, defaultValueSql: "NEWID()"),
                    Word = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false),
                    Grade = table.Column<int>(type: "int", nullable: false),
                    Difficulty = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    Category = table.Column<string>(type: "nvarchar(80)", maxLength: 80, nullable: false),
                    Definition = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    UsageSentence = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false),
                    Origin = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: true),
                    Pronunciation = table.Column<string>(type: "nvarchar(150)", maxLength: 150, nullable: true),
                    MemoryTip = table.Column<string>(type: "nvarchar(300)", maxLength: 300, nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, defaultValueSql: "GETDATE()")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SpellBeeWords", x => x.SpellBeeWordId);
                });

            migrationBuilder.CreateIndex(
                name: "IX_SpellBeeWords_Grade_Difficulty_Category",
                table: "SpellBeeWords",
                columns: new[] { "Grade", "Difficulty", "Category" });

            migrationBuilder.CreateIndex(
                name: "IX_SpellBeeWords_Word",
                table: "SpellBeeWords",
                column: "Word",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "SpellBeeWords");
        }
    }
}
