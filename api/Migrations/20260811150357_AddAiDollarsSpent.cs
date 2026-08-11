using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace OlympiadReady.Api.Migrations
{
    /// <inheritdoc />
    public partial class AddAiDollarsSpent : Migration
    {
        // This migration was auto-scaffolded against a model snapshot that predates the
        // Schools/ExpoPushToken columns — those were evidently applied out-of-band (the
        // "AddExpoPushToken" migration file has no Designer.cs, so EF's tooling has never
        // actually been able to discover or run it; the column exists in real databases
        // anyway). The scaffold therefore proposed re-creating objects that already exist
        // everywhere except a from-scratch database.
        //
        // Every operation below except AiDollarsSpent — which is genuinely new — is guarded
        // with an existence check, so this migration is a no-op for that drift wherever it's
        // already present, and still creates it correctly on a fresh database. This also
        // finally brings the model snapshot back in sync, so the next `migrations add` stops
        // proposing the same redo.
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<decimal>(
                name: "AiDollarsSpent",
                table: "Users",
                type: "decimal(10,4)",
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.Sql(@"
                IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[Users]') AND name = 'ExpoPushToken')
                BEGIN
                    ALTER TABLE [Users] ADD [ExpoPushToken] nvarchar(max) NULL;
                END");

            migrationBuilder.Sql(@"
                IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[Users]') AND name = 'SchoolId')
                BEGIN
                    ALTER TABLE [Users] ADD [SchoolId] uniqueidentifier NULL;
                END");

            migrationBuilder.Sql(@"
                IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[Users]') AND name = 'SchoolJoinedAt')
                BEGIN
                    ALTER TABLE [Users] ADD [SchoolJoinedAt] datetime2 NULL;
                END");

            migrationBuilder.Sql(@"
                IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'[Users]') AND name = 'TrialExpiresAt')
                BEGIN
                    ALTER TABLE [Users] ADD [TrialExpiresAt] datetime2 NULL;
                END");

            migrationBuilder.Sql(@"
                IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Schools')
                BEGIN
                    CREATE TABLE [Schools] (
                        [SchoolId] uniqueidentifier NOT NULL DEFAULT (NEWID()),
                        [Name] nvarchar(255) NOT NULL,
                        [City] nvarchar(100) NOT NULL,
                        [LogoUrl] nvarchar(500) NULL,
                        [InviteCode] nvarchar(50) NOT NULL,
                        [PilotEndsAt] datetime2 NULL,
                        [SeatLimit] int NOT NULL,
                        [ContactEmail] nvarchar(255) NOT NULL,
                        [CreatedAt] datetime2 NOT NULL DEFAULT (GETUTCDATE()),
                        CONSTRAINT [PK_Schools] PRIMARY KEY ([SchoolId])
                    );
                END");

            migrationBuilder.Sql(@"
                IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Users_SchoolId' AND object_id = OBJECT_ID(N'[Users]'))
                BEGIN
                    CREATE INDEX [IX_Users_SchoolId] ON [Users] ([SchoolId]);
                END");

            migrationBuilder.Sql(@"
                IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Schools_InviteCode' AND object_id = OBJECT_ID(N'[Schools]'))
                BEGIN
                    CREATE UNIQUE INDEX [IX_Schools_InviteCode] ON [Schools] ([InviteCode]);
                END");

            migrationBuilder.Sql(@"
                IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Users_Schools_SchoolId')
                BEGIN
                    ALTER TABLE [Users] ADD CONSTRAINT [FK_Users_Schools_SchoolId]
                        FOREIGN KEY ([SchoolId]) REFERENCES [Schools] ([SchoolId]) ON DELETE SET NULL;
                END");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.Sql(@"
                IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Users_Schools_SchoolId')
                BEGIN
                    ALTER TABLE [Users] DROP CONSTRAINT [FK_Users_Schools_SchoolId];
                END");

            migrationBuilder.Sql(@"
                IF EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Schools')
                BEGIN
                    DROP TABLE [Schools];
                END");

            migrationBuilder.Sql(@"
                IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Users_SchoolId' AND object_id = OBJECT_ID(N'[Users]'))
                BEGIN
                    DROP INDEX [IX_Users_SchoolId] ON [Users];
                END");

            migrationBuilder.DropColumn(
                name: "AiDollarsSpent",
                table: "Users");

            // ExpoPushToken / SchoolId / SchoolJoinedAt / TrialExpiresAt are deliberately left
            // in place on rollback — this migration did not create them in any environment
            // that matters (they pre-existed everywhere except a fresh database), so dropping
            // them here would destroy real columns other migrations and code depend on.
        }
    }
}
