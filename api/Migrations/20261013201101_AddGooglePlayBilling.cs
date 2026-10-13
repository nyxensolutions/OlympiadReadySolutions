using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OlympiadReady.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddGooglePlayBilling : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "GooglePurchaseToken",
                table: "Subscriptions",
                type: "nvarchar(512)",
                maxLength: 512,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Provider",
                table: "Subscriptions",
                type: "nvarchar(20)",
                maxLength: 20,
                nullable: false,
                defaultValue: "Razorpay");

            migrationBuilder.AddColumn<string>(
                name: "GoogleBasePlanId",
                table: "PaymentTransactions",
                type: "nvarchar(50)",
                maxLength: 50,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "GoogleOrderId",
                table: "PaymentTransactions",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "GoogleProductId",
                table: "PaymentTransactions",
                type: "nvarchar(100)",
                maxLength: 100,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "GooglePurchaseToken",
                table: "PaymentTransactions",
                type: "nvarchar(512)",
                maxLength: 512,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Provider",
                table: "PaymentTransactions",
                type: "nvarchar(20)",
                maxLength: 20,
                nullable: false,
                defaultValue: "Razorpay");

            migrationBuilder.CreateIndex(
                name: "IX_Subscriptions_GooglePurchaseToken",
                table: "Subscriptions",
                column: "GooglePurchaseToken",
                filter: "[GooglePurchaseToken] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_PaymentTransactions_GoogleOrderId",
                table: "PaymentTransactions",
                column: "GoogleOrderId",
                unique: true,
                filter: "[GoogleOrderId] IS NOT NULL");

            migrationBuilder.CreateIndex(
                name: "IX_PaymentTransactions_GooglePurchaseToken",
                table: "PaymentTransactions",
                column: "GooglePurchaseToken",
                filter: "[GooglePurchaseToken] IS NOT NULL");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_Subscriptions_GooglePurchaseToken",
                table: "Subscriptions");

            migrationBuilder.DropIndex(
                name: "IX_PaymentTransactions_GoogleOrderId",
                table: "PaymentTransactions");

            migrationBuilder.DropIndex(
                name: "IX_PaymentTransactions_GooglePurchaseToken",
                table: "PaymentTransactions");

            migrationBuilder.DropColumn(
                name: "GooglePurchaseToken",
                table: "Subscriptions");

            migrationBuilder.DropColumn(
                name: "Provider",
                table: "Subscriptions");

            migrationBuilder.DropColumn(
                name: "GoogleBasePlanId",
                table: "PaymentTransactions");

            migrationBuilder.DropColumn(
                name: "GoogleOrderId",
                table: "PaymentTransactions");

            migrationBuilder.DropColumn(
                name: "GoogleProductId",
                table: "PaymentTransactions");

            migrationBuilder.DropColumn(
                name: "GooglePurchaseToken",
                table: "PaymentTransactions");

            migrationBuilder.DropColumn(
                name: "Provider",
                table: "PaymentTransactions");
        }
    }
}
