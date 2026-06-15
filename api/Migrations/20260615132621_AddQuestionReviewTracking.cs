using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OlympiadReady.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddQuestionReviewTracking : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<bool>(
                name: "IsReviewed",
                table: "QuestionBank",
                type: "bit",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<DateTime>(
                name: "ReviewedAt",
                table: "QuestionBank",
                type: "datetime2",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "ReviewedBy",
                table: "QuestionBank",
                type: "nvarchar(256)",
                maxLength: 256,
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_QuestionBank_IsReviewed",
                table: "QuestionBank",
                column: "IsReviewed");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_QuestionBank_IsReviewed",
                table: "QuestionBank");

            migrationBuilder.DropColumn(
                name: "IsReviewed",
                table: "QuestionBank");

            migrationBuilder.DropColumn(
                name: "ReviewedAt",
                table: "QuestionBank");

            migrationBuilder.DropColumn(
                name: "ReviewedBy",
                table: "QuestionBank");
        }
    }
}
