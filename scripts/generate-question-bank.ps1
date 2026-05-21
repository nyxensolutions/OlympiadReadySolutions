#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Bulk-generates question bank entries for all missing (subject, grade, difficulty)
    combinations by calling Claude API directly then importing via the admin endpoint.

.NOTES
    Run from repo root:
        pwsh .\scripts\generate-question-bank.ps1
    Or target specific combos:
        pwsh .\scripts\generate-question-bank.ps1 -DryRun
#>
param(
    [switch]$DryRun,
    [int]$QuestionsPerBatch = 50,   # per subject/grade/difficulty call
    [int]$DelayBetweenCallsMs = 2000
)

$AdminKey    = "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt"
$ClaudeKey   = "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"
$AdminApi    = "http://localhost:5080/api/admin"
$ClaudeApi   = "https://api.anthropic.com/v1/messages"
$ClaudeModel = "claude-opus-4-5"

# ─── Generation targets ───────────────────────────────────────────────────────
# Priority 1: Classes 4, 5, 6 – complete blackout for all core subjects
# Priority 2: Spell Bee – Grades 2-12 missing
# Priority 3: Missing grade gaps for GK, Hindi, Social Studies
# Priority 4: Olympiad difficulty boost for thin grades
# Priority 5: Class 1 Advanced/Olympiad missing

$Targets = @(
    # ── Priority 1: Classes 4, 5, 6 ─────────────────────────────────────────
    @{ Subject="Mathematics";       Grade=4;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Mathematics";       Grade=5;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Mathematics";       Grade=6;  Difficulties=@("Foundation","Advanced","Olympiad") }

    @{ Subject="Science";           Grade=4;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Science";           Grade=5;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Science";           Grade=6;  Difficulties=@("Foundation","Advanced","Olympiad") }

    @{ Subject="English";           Grade=4;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="English";           Grade=5;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="English";           Grade=6;  Difficulties=@("Foundation","Advanced","Olympiad") }

    @{ Subject="Logical Reasoning"; Grade=4;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Logical Reasoning"; Grade=5;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Logical Reasoning"; Grade=6;  Difficulties=@("Foundation","Advanced","Olympiad") }

    @{ Subject="Computer Science";  Grade=4;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Computer Science";  Grade=5;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Computer Science";  Grade=6;  Difficulties=@("Foundation","Advanced","Olympiad") }

    @{ Subject="General Knowledge"; Grade=4;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="General Knowledge"; Grade=5;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="General Knowledge"; Grade=6;  Difficulties=@("Foundation","Advanced","Olympiad") }

    @{ Subject="Social Studies";    Grade=4;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Social Studies";    Grade=5;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Social Studies";    Grade=6;  Difficulties=@("Foundation","Advanced","Olympiad") }

    # ── Priority 2: Spell Bee Grades 2-12 ────────────────────────────────────
    @{ Subject="Spell Bee"; Grade=2;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=3;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=4;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=5;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=6;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=7;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=8;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=9;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=10; Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=11; Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Spell Bee"; Grade=12; Difficulties=@("Foundation","Advanced","Olympiad") }

    # ── Priority 3: Missing grade gaps ───────────────────────────────────────
    @{ Subject="General Knowledge"; Grade=7;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="General Knowledge"; Grade=9;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="General Knowledge"; Grade=10; Difficulties=@("Foundation","Advanced","Olympiad") }

    @{ Subject="Hindi"; Grade=4;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Hindi"; Grade=5;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Hindi"; Grade=6;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Hindi"; Grade=7;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Hindi"; Grade=9;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Hindi"; Grade=10; Difficulties=@("Foundation","Advanced","Olympiad") }

    @{ Subject="Social Studies"; Grade=7;  Difficulties=@("Foundation","Advanced","Olympiad") }
    @{ Subject="Social Studies"; Grade=9;  Difficulties=@("Foundation","Advanced","Olympiad") }

    # ── Priority 4: Olympiad difficulty boost (critically thin) ──────────────
    @{ Subject="Science-Chemistry";  Grade=9;  Difficulties=@("Olympiad") }
    @{ Subject="Computer Science";   Grade=9;  Difficulties=@("Olympiad") }
    @{ Subject="Science-Physics";    Grade=9;  Difficulties=@("Olympiad") }
    @{ Subject="Science-Biology";    Grade=9;  Difficulties=@("Olympiad") }
    @{ Subject="English";            Grade=9;  Difficulties=@("Olympiad") }
    @{ Subject="Logical Reasoning";  Grade=9;  Difficulties=@("Olympiad") }
    @{ Subject="Hindi";              Grade=3;  Difficulties=@("Olympiad") }
    @{ Subject="Hindi";              Grade=8;  Difficulties=@("Olympiad") }
    @{ Subject="Science";            Grade=10; Difficulties=@("Olympiad") }
    @{ Subject="Social Studies";     Grade=10; Difficulties=@("Olympiad") }
    @{ Subject="Logical Reasoning";  Grade=12; Difficulties=@("Foundation","Advanced","Olympiad") }

    # ── Priority 5: Class 1 missing Advanced/Olympiad ────────────────────────
    @{ Subject="Mathematics";       Grade=1; Difficulties=@("Advanced","Olympiad") }
    @{ Subject="Science";           Grade=1; Difficulties=@("Advanced","Olympiad") }
    @{ Subject="English";           Grade=1; Difficulties=@("Advanced","Olympiad") }
    @{ Subject="Logical Reasoning"; Grade=1; Difficulties=@("Advanced") }
)

# ─── Claude system prompt (same as ClaudeService.cs) ─────────────────────────
$SystemPrompt = @"
You are a senior examiner with 15+ years of experience writing competitive Olympiad
questions for Indian school students. Your day-to-day work is preparing question papers
for SOF (Science Olympiad Foundation) — IMO, NSO, IEO, NCO — and SilverZone Olympiads.
You know the CBSE / NCERT curriculum cold.

# Task
Generate multiple-choice questions tailored to the requested Class, Subject, and Difficulty.

# Difficulty calibration
Foundation  – recall and direct application of a single concept.
Advanced    – composing two concepts, word problems, data interpretation.
Olympiad    – multi-step reasoning, non-obvious insight, Achievers Section style.

# Quality rules
- Single unambiguous correct answer. Exactly 4 options.
- No "all/none of the above".
- Distractors target real misconceptions.
- Indian context: rupees, Mumbai/Delhi, cricket. Names: Aarav, Priya, Rohan.
- For Spell Bee: focus on spelling, phonetics, syllabification, homophones, synonyms/antonyms.

# Output format — ONLY a valid JSON array, no prose, no code fences:
[
  {
    "QuestionText": "...",
    "Options": ["option A text", "option B text", "option C text", "option D text"],
    "CorrectAnswer": "A",
    "Topic": "1-3 word syllabus topic",
    "SubTopic": null,
    "Difficulty": "Foundation|Advanced|Olympiad",
    "Explanation": "2-4 sentence plain-English explanation"
  }
]
CorrectAnswer must be exactly "A", "B", "C", or "D" (the letter of the correct option).
"@

# ─── Helper: call Claude ──────────────────────────────────────────────────────
function Invoke-Claude {
    param($Subject, $Grade, $Difficulty, $Count)

    $spellBeeExtra = if ($Subject -eq "Spell Bee") {
        " Focus exclusively on: correct spelling, phonetics, syllabification, homophones, synonyms/antonyms, and commonly confused words. Grade the word difficulty appropriately for Class $Grade."
    } else { "" }

    $userMsg = "Generate exactly $Count multiple-choice questions for Class $Grade $Subject at $Difficulty difficulty.$spellBeeExtra Return ONLY the JSON array."

    $body = @{
        model      = $ClaudeModel
        max_tokens = 8096
        system     = $SystemPrompt
        messages   = @(@{ role = "user"; content = $userMsg })
    } | ConvertTo-Json -Depth 5

    $headers = @{
        "x-api-key"         = $ClaudeKey
        "anthropic-version" = "2023-06-01"
        "content-type"      = "application/json"
    }

    try {
        $resp = Invoke-RestMethod -Uri $ClaudeApi -Method Post -Headers $headers -Body $body -TimeoutSec 120
        $text = ($resp.content | Where-Object { $_.type -eq "text" } | Select-Object -First 1).text

        # Extract JSON array from response
        $start = $text.IndexOf('[')
        $end   = $text.LastIndexOf(']')
        if ($start -lt 0 -or $end -le $start) { throw "No JSON array in response" }
        return $text.Substring($start, $end - $start + 1)
    } catch {
        Write-Warning "  Claude error: $_"
        return $null
    }
}

# ─── Helper: import to admin endpoint ────────────────────────────────────────
function Import-Questions {
    param($Subject, $Grade, $JsonBody)

    # URL-encode subject
    $encSubject = [Uri]::EscapeDataString($Subject)
    $url = "$AdminApi/import-questions?subject=$encSubject&grade=$Grade"

    $headers = @{
        "X-Admin-Key"  = $AdminKey
        "Content-Type" = "application/json; charset=utf-8"
    }

    try {
        $resp = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($JsonBody)) -TimeoutSec 30
        return $resp
    } catch {
        Write-Warning "  Import error: $_"
        return $null
    }
}

# ─── Main loop ───────────────────────────────────────────────────────────────
$totalInserted = 0
$totalSkipped  = 0
$totalErrors   = 0
$batchNum      = 0

# Expand targets into individual (subject, grade, difficulty) combos
$allCombos = foreach ($t in $Targets) {
    foreach ($d in $t.Difficulties) {
        [PSCustomObject]@{ Subject=$t.Subject; Grade=$t.Grade; Difficulty=$d }
    }
}

Write-Host "`n=== OlympiadReady Question Bank Generator ===" -ForegroundColor Cyan
Write-Host "Total combos to generate: $($allCombos.Count)" -ForegroundColor Cyan
Write-Host "Questions per batch: $QuestionsPerBatch" -ForegroundColor Cyan
Write-Host "Estimated total questions: $($allCombos.Count * $QuestionsPerBatch)" -ForegroundColor Cyan
if ($DryRun) { Write-Host "DRY RUN - no Claude calls or imports will be made`n" -ForegroundColor Yellow }
Write-Host ""

foreach ($combo in $allCombos) {
    $batchNum++
    $pct = [int](($batchNum / $allCombos.Count) * 100)
    Write-Host "[$batchNum/$($allCombos.Count)] (${pct}%) $($combo.Subject) G$($combo.Grade) $($combo.Difficulty)..." -NoNewline

    if ($DryRun) {
        Write-Host " [DRY RUN]" -ForegroundColor Yellow
        continue
    }

    # Call Claude
    $json = Invoke-Claude -Subject $combo.Subject -Grade $combo.Grade -Difficulty $combo.Difficulty -Count $QuestionsPerBatch

    if (-not $json) {
        Write-Host " CLAUDE FAILED" -ForegroundColor Red
        $totalErrors++
        continue
    }

    # Count questions parsed
    $parsed = $json | ConvertFrom-Json -ErrorAction SilentlyContinue
    $count  = if ($parsed) { $parsed.Count } else { 0 }
    Write-Host " Got $count Qs..." -NoNewline

    # Import
    $result = Import-Questions -Subject $combo.Subject -Grade $combo.Grade -JsonBody $json

    if ($result) {
        $ins = $result.inserted
        $skp = $result.skipped
        $err = $result.errors.Count
        $totalInserted += $ins
        $totalSkipped  += $skp
        $totalErrors   += $err
        Write-Host " Inserted: $ins  Skipped: $skp  Errors: $err" -ForegroundColor Green
        if ($result.errors.Count -gt 0) {
            $result.errors | ForEach-Object { Write-Warning "    $_" }
        }
    } else {
        Write-Host " IMPORT FAILED" -ForegroundColor Red
        $totalErrors++
    }

    # Polite delay between Claude calls
    if ($DelayBetweenCallsMs -gt 0) {
        Start-Sleep -Milliseconds $DelayBetweenCallsMs
    }
}

Write-Host "`n=== Generation Complete ===" -ForegroundColor Cyan
Write-Host "Total Inserted : $totalInserted" -ForegroundColor Green
Write-Host "Total Skipped  : $totalSkipped"  -ForegroundColor Yellow
Write-Host "Total Errors   : $totalErrors" -ForegroundColor Red
