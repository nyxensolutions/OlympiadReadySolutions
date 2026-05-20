<#
.SYNOPSIS
    Bulk-imports all Spell Bee question JSON files from a folder into OlympiadReady.

.DESCRIPTION
    Scans the target folder for files matching the naming pattern grade{N}_*.json,
    extracts the grade from the filename, and POSTs each file to the admin import endpoint.
    Imports are idempotent: duplicate questions (matched by exact question text + subject + grade)
    are skipped automatically by the API.

.PARAMETER Folder
    Path to the folder containing the JSON question files.
    Defaults to the folder this script lives in.

.PARAMETER ApiBase
    Base URL of the OlympiadReady API.
    Defaults to http://localhost:5080 (local dev).

.PARAMETER AdminKey
    Admin API key. Reads from $env:OLYMPIAD_ADMIN_KEY if not provided.

.PARAMETER Subject
    Subject name to import under. Defaults to "Spell Bee".

.PARAMETER DryRun
    If set, prints what would be imported without actually calling the API.

.EXAMPLE
    # Import all files from the default folder (local dev)
    .\import-spellbee.ps1

.EXAMPLE
    # Import to production
    .\import-spellbee.ps1 -ApiBase "https://api.olympiadready.com" -AdminKey "your-key"

.EXAMPLE
    # Preview what would be imported without touching the DB
    .\import-spellbee.ps1 -DryRun
#>

param(
    [string] $Folder   = $PSScriptRoot,
    [string] $ApiBase  = "http://localhost:5080",
    [string] $AdminKey = $env:OLYMPIAD_ADMIN_KEY,
    [string] $Subject  = "Spell Bee",
    [switch] $DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Validate inputs ────────────────────────────────────────────────────────────
if (-not (Test-Path $Folder)) {
    Write-Error "Folder not found: $Folder"; exit 1
}
if (-not $DryRun -and [string]::IsNullOrWhiteSpace($AdminKey)) {
    Write-Error "Admin key is required. Set `$env:OLYMPIAD_ADMIN_KEY or pass -AdminKey."
    exit 1
}

# ── Discover files ─────────────────────────────────────────────────────────────
# Expected naming: grade1_animals.json, grade3_environment_easy.json, etc.
$files = @(Get-ChildItem -Path $Folder -Filter "grade*.json" |
           Sort-Object Name)

if ($files.Count -eq 0) {
    Write-Warning "No files matching 'grade*.json' found in: $Folder"
    exit 0
}

Write-Host ""
Write-Host "OlympiadReady -- Spell Bee Bulk Import" -ForegroundColor Cyan
Write-Host "  Folder  : $Folder"
Write-Host "  API     : $ApiBase"
Write-Host "  Subject : $Subject"
if ($DryRun) { Write-Host "  MODE    : DRY RUN (no data will be written)" -ForegroundColor Yellow }
Write-Host ""

# ── Summary table: what we found ──────────────────────────────────────────────
$plan = @()
foreach ($file in $files) {
    # Extract grade from filename: grade1_... -> 1, grade12_... -> 12
    if ($file.Name -match '^grade(\d+)') {
        $grade = [int]$Matches[1]
    } else {
        Write-Warning "Skipping '$($file.Name)' - filename must start with grade{N}_"
        continue
    }

    if ($grade -lt 1 -or $grade -gt 12) {
        Write-Warning "Skipping '$($file.Name)' - grade $grade is out of range (1-12)"
        continue
    }

    # Count questions in file
    try {
        $raw   = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
        $items = $raw | ConvertFrom-Json
        $count = if ($items -is [array]) { $items.Count } else { 1 }
    } catch {
        Write-Warning "Skipping '$($file.Name)' - JSON parse error: $_"
        continue
    }

    $plan += [PSCustomObject]@{
        File  = $file.Name
        Grade = $grade
        Questions = $count
        FullPath  = $file.FullName
        RawBody   = $raw
    }
}

if ($plan.Count -eq 0) {
    Write-Warning "No valid files to process."
    exit 0
}

# Print the plan
$plan | Format-Table File, Grade, Questions -AutoSize

$totalQ = ($plan | Measure-Object Questions -Sum).Sum
Write-Host "Total: $($plan.Count) file(s), $totalQ question(s) to submit`n"

if ($DryRun) {
    Write-Host "Dry run complete. No data was sent." -ForegroundColor Yellow
    exit 0
}

# ── Run imports ────────────────────────────────────────────────────────────────
$results = @()
$totalInserted = 0
$totalSkipped  = 0
$totalErrors   = 0

foreach ($item in $plan) {
    $url = "$($ApiBase.TrimEnd('/'))/api/admin/import-questions" +
           "?subject=$([Uri]::EscapeDataString($Subject))&grade=$($item.Grade)"

    Write-Host "Importing  $($item.File)  (Grade $($item.Grade), $($item.Questions) questions)..." -NoNewline

    try {
        $resp = Invoke-RestMethod `
            -Uri         $url `
            -Method      POST `
            -Headers     @{ "X-Admin-Key" = $AdminKey } `
            -Body        ([System.Text.Encoding]::UTF8.GetBytes($item.RawBody)) `
            -ContentType "application/json; charset=utf-8"

        $inserted = $resp.inserted
        $skipped  = $resp.skipped
        $errCount = if ($resp.errors) { $resp.errors.Count } else { 0 }

        $totalInserted += $inserted
        $totalSkipped  += $skipped
        $totalErrors   += $errCount

        $status = if ($errCount -gt 0) { "PARTIAL" } else { "OK" }
        $color  = if ($errCount -gt 0) { "Yellow"  } else { "Green"  }
        Write-Host "  [$status]  inserted=$inserted  skipped=$skipped  errors=$errCount" -ForegroundColor $color

        if ($errCount -gt 0) {
            $resp.errors | ForEach-Object { Write-Host "    Error: $_" -ForegroundColor Yellow }
        }

        $results += [PSCustomObject]@{
            File     = $item.File
            Grade    = $item.Grade
            Inserted = $inserted
            Skipped  = $skipped
            Errors   = $errCount
            Status   = $status
        }
    } catch {
        Write-Host "  [FAILED]" -ForegroundColor Red
        $msg = $_.Exception.Message
        # Try to read the response body for a better error message
        try {
            $stream = $_.Exception.Response.GetResponseStream()
            $reader = [System.IO.StreamReader]::new($stream)
            $msg = $reader.ReadToEnd()
        } catch {}
        Write-Host "    $msg" -ForegroundColor Red
        $totalErrors++
        $results += [PSCustomObject]@{
            File = $item.File; Grade = $item.Grade
            Inserted = 0; Skipped = 0; Errors = 1; Status = "FAILED"
        }
    }
}

# ── Final summary ──────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Import complete" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
$results | Format-Table File, Grade, Inserted, Skipped, Errors, Status -AutoSize
Write-Host "  TOTAL inserted : $totalInserted"
Write-Host "  TOTAL skipped  : $totalSkipped  (already in DB - safe to ignore)"
Write-Host "  TOTAL errors   : $totalErrors"
Write-Host ""

if ($totalErrors -gt 0) {
    Write-Host "Some rows had errors. Check the output above for details." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "All done." -ForegroundColor Green
    exit 0
}
