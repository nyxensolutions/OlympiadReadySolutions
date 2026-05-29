using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OlympiadReady.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddAiCreditQuota : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "AiCreditsUsed",
                table: "Users",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<DateTime>(
                name: "AiPeriodStart",
                table: "Users",
                type: "datetime2",
                nullable: false,
                defaultValueSql: "GETUTCDATE()");

            migrationBuilder.AddColumn<int>(
                name: "Days",
                table: "PaymentTransactions",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<int>(
                name: "Grade",
                table: "PaymentTransactions",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<string>(
                name: "Subjects",
                table: "PaymentTransactions",
                type: "nvarchar(200)",
                maxLength: 200,
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_PaymentTransactions_RazorpayOrderId",
                table: "PaymentTransactions",
                column: "RazorpayOrderId",
                unique: true,
                filter: "[RazorpayOrderId] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_PaymentTransactions_RazorpayPaymentId",
                table: "PaymentTransactions",
                column: "RazorpayPaymentId",
                unique: true,
                filter: "[RazorpayPaymentId] IS NOT NULL");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_PaymentTransactions_RazorpayOrderId",
                table: "PaymentTransactions");

            migrationBuilder.DropIndex(
                name: "IX_PaymentTransactions_RazorpayPaymentId",
                table: "PaymentTransactions");

            migrationBuilder.DropColumn(
                name: "AiCreditsUsed",
                table: "Users");

            migrationBuilder.DropColumn(
                name: "AiPeriodStart",
                table: "Users");

            migrationBuilder.DropColumn(
                name: "Days",
                table: "PaymentTransactions");

            migrationBuilder.DropColumn(
                name: "Grade",
                table: "PaymentTransactions");

            migrationBuilder.DropColumn(
                name: "Subjects",
                table: "PaymentTransactions");
        }
    }
}
