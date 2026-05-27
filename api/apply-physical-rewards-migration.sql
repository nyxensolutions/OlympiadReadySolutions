-- Migration: AddPhysicalRewardClaims
-- Run this once against the OlympiadReady database.

IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'PhysicalRewardClaims')
BEGIN
    CREATE TABLE [PhysicalRewardClaims] (
        [ClaimId]        UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID(),
        [UserId]         UNIQUEIDENTIFIER NOT NULL,
        [RewardType]     NVARCHAR(100)    NOT NULL,
        [Status]         NVARCHAR(50)     NOT NULL DEFAULT 'Pending',
        [RequestedAt]    DATETIME2        NOT NULL DEFAULT GETDATE(),
        [ShippedAt]      DATETIME2        NULL,
        [AdminNotes]     NVARCHAR(500)    NULL,
        [StudentName]    NVARCHAR(255)    NULL,
        [TrackingNumber] NVARCHAR(100)    NULL,
        CONSTRAINT [PK_PhysicalRewardClaims] PRIMARY KEY ([ClaimId]),
        CONSTRAINT [FK_PhysicalRewardClaims_Users_UserId]
            FOREIGN KEY ([UserId]) REFERENCES [Users] ([UserId]) ON DELETE CASCADE
    );

    CREATE INDEX [IX_PhysicalRewardClaims_UserId_RewardType]
        ON [PhysicalRewardClaims] ([UserId], [RewardType]);

    CREATE INDEX [IX_PhysicalRewardClaims_Status]
        ON [PhysicalRewardClaims] ([Status]);

    -- Record in EF migrations history so EF doesn't try to re-create it
    INSERT INTO [__EFMigrationsHistory] ([MigrationId], [ProductVersion])
    VALUES ('20260527153135_AddPhysicalRewardClaims', '8.0.0');

    PRINT 'PhysicalRewardClaims table created successfully.';
END
ELSE
BEGIN
    PRINT 'PhysicalRewardClaims table already exists — skipped.';
END
