# OlympiadReady Question Bank Quality Scanner & Repair System
# Standalone Utility Script to scan, report, and fix wrong answers.
# Works for both Local SQL Server and Azure SQL Database.

param(
    [string]$ConnectionString,
    [switch]$AutoFix,
    [switch]$LlmVerify,
    [string]$SubjectFilter,
    [int]$GradeFilter
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Resolve Connection String
if ([string]::IsNullOrWhiteSpace($ConnectionString)) {
    $appsettingsPath = Join-Path $scriptDir "appsettings.json"
    if (Test-Path $appsettingsPath) {
        try {
            $config = Get-Content $appsettingsPath -Raw | ConvertFrom-Json
            $ConnectionString = $config.ConnectionStrings.DefaultConnection
            Write-Host "Loaded connection string from appsettings.json." -ForegroundColor Cyan
        } catch {
            Write-Host "Failed to parse appsettings.json. Using local default connection." -ForegroundColor Yellow
        }
    }
    
    if ([string]::IsNullOrWhiteSpace($ConnectionString)) {
        $ConnectionString = "Server=localhost;Database=OlympiadReady;Integrated Security=True;TrustServerCertificate=True;"
    }
}

Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "     OlympiadReady Question Bank Quality Scanner & Repair System" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "Target Connection: $ConnectionString" -ForegroundColor Yellow
Write-Host "Mode: $(if ($AutoFix) { 'Auto-Fix (Apply Changes)' } else { 'Dry-Run (Audit Only)' })" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Green

# 2. Establish DB Connection
$conn = New-Object System.Data.SqlClient.SqlConnection($ConnectionString)
try {
    $conn.Open()
    Write-Host "Successfully connected to the database." -ForegroundColor Green
} catch {
    Write-Host "ERROR: Could not connect to the database. Verify connection string or server status." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Exit
}

# Helper: Clean option text of prefixes and formatting
function Get-CleanOption {
    param ([string]$optionText)
    if ($null -eq $optionText) { return "" }
    # Remove prefix like "A) ", "A. ", "a) "
    $cleaned = $optionText -replace "^\s*[A-Da-d]\s*[\)\.]\s*", ""
    # Clean commas and spaces
    $cleaned = $cleaned.Replace(",", "").Trim()
    return $cleaned
}

# Helper: Solve place value for whole numbers
function Solve-PlaceValueWhole {
    param (
        [string]$digitStr,
        [string]$numberStr
    )
    $cleanNumber = $numberStr.Replace(",", "")
    $digit = $digitStr.Trim()
    
    # Find position from right
    $reversed = -join $cleanNumber.ToCharArray()[($cleanNumber.Length - 1)..0]
    $pos = $reversed.IndexOf($digit)
    if ($pos -eq -1) { return $null }
    
    $val = [double]$digit * [Math]::Pow(10, $pos)
    
    $names = @{
        0 = "Ones"
        1 = "Tens"
        2 = "Hundreds"
        3 = "Thousands"
        4 = "Ten Thousands"
        5 = "Hundred Thousands"
        6 = "Millions"
    }
    
    $placeName = $names[$pos]
    return [PSCustomObject]@{
        Value = $val
        PlaceName = $placeName
    }
}

# Helper: Solve place value for decimal numbers
function Solve-PlaceValueDecimal {
    param (
        [string]$digitStr,
        [string]$numberStr
    )
    $digit = $digitStr.Trim()
    $parts = $numberStr.Split('.')
    if ($parts.Length -ne 2) { return $null }
    $fractionPart = $parts[1]
    
    $pos = $fractionPart.IndexOf($digit) + 1
    if ($pos -eq 0) { return $null }
    
    $names = @{
        1 = "Tenths"
        2 = "Hundredths"
        3 = "Thousandths"
    }
    
    return [PSCustomObject]@{
        Value = [Math]::Pow(10, -$pos)
        PlaceName = $names[$pos]
    }
}

# Helper: Solve simple arithmetic
function Solve-SimpleArithmetic {
    param ([string]$questionText)
    # Match questions like "What is 0 + 0 + 5?" or "What is 50 + 50 - 20?" or "What is 700 - 456?"
    # It dynamically captures the full math expression, normalizes operators, and evaluates safely using DataTable.Compute.
    if ($questionText -match "(?i)what is\s+([\d\s+\-*x/\u2013\u2014\u2212]+)\s*\??$") {
        $expr = $Matches[1].Trim()
        # Remove trailing question mark if any
        $expr = $expr -replace "\?\s*$", ""
        # Clean unicode dashes to standard hyphen
        $expr = $expr -replace "[\u2013\u2014\u2212]", "-"
        # Replace 'x' with '*' for multiplication
        $expr = $expr.Replace("x", "*")
        
        try {
            $dt = New-Object System.Data.DataTable
            $val = $dt.Compute($expr, "")
            return [double]$val
        } catch {
            return $null
        }
    }
    return $null
}

# 3. Query all candidate questions
$query = "SELECT QuestionBankId, QuestionText, OptionsJson, CorrectAnswer, Subject, Grade, Topic, Explanation FROM QuestionBank WHERE 1=1"
if (![string]::IsNullOrWhiteSpace($SubjectFilter)) {
    $query += " AND Subject = @Subject"
}
if ($GradeFilter -gt 0) {
    $query += " AND Grade = @Grade"
}

$cmd = $conn.CreateCommand()
$cmd.CommandText = $query
if (![string]::IsNullOrWhiteSpace($SubjectFilter)) {
    $cmd.Parameters.AddWithValue("@Subject", $SubjectFilter) | Out-Null
}
if ($GradeFilter -gt 0) {
    $cmd.Parameters.AddWithValue("@Grade", $GradeFilter) | Out-Null
}

$reader = $cmd.ExecuteReader()
$questions = New-Object System.Collections.Generic.List[PSObject]

while ($reader.Read()) {
    $q = [PSCustomObject]@{
        Id = $reader["QuestionBankId"].ToString()
        Text = $reader["QuestionText"].ToString()
        OptionsJson = $reader["OptionsJson"].ToString()
        CorrectAnswer = $reader["CorrectAnswer"].ToString().Trim()
        Subject = $reader["Subject"].ToString()
        Grade = [int]$reader["Grade"]
        Topic = $reader["Topic"].ToString()
        Explanation = $reader["Explanation"].ToString()
    }
    $questions.Add($q) | Out-Null
}
$reader.Close()

Write-Host "Loaded $($questions.Count) questions from database to analyze." -ForegroundColor Cyan

# 4. Perform Quality Scanning
$errorsFound = 0
$fixesApplied = 0
$sqlFixes = New-Object System.Text.StringBuilder
$sqlFixes.AppendLine("-- OlympiadReady Question Bank Fix Script") | Out-Null
$sqlFixes.AppendLine("-- Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')") | Out-Null
$sqlFixes.AppendLine("-- Connection: $ConnectionString") | Out-Null
$sqlFixes.AppendLine("BEGIN TRANSACTION;") | Out-Null
$sqlFixes.AppendLine() | Out-Null

foreach ($q in $questions) {
    $isMismatched = $false
    $reason = ""
    $expectedLetter = ""
    $expectedText = ""
    
    # Parse Options
    try {
        $options = $q.OptionsJson | ConvertFrom-Json
    } catch {
        Write-Host "FAIL: Invalid options JSON in question ID: $($q.Id)" -ForegroundColor Red
        continue
    }
    
    if ($options.Count -ne 4) {
        $errorsFound++
        Write-Host "WARN: Question ID $($q.Id) does not have exactly 4 options (found $($options.Count))." -ForegroundColor Yellow
        continue
    }
    
    # Clean options array
    $cleanOptions = @()
    foreach ($opt in $options) {
        $cleanOptions += Get-CleanOption $opt
    }
    
    # -------------------------------------------------------------
    # RULE 1: Place Value Programmatic Verification
    # -------------------------------------------------------------
    if ($q.Text -match "(?i)place\s+value\s+of\s+(?:the\s+digit\s+)?(\d+)\s+in\s+(?:the\s+number\s+)?([\d,]+)") {
        $digit = $Matches[1]
        $number = $Matches[2]
        
        $solution = Solve-PlaceValueWhole $digit $number
        if ($null -ne $solution) {
            # Let's see which option matches
            $matchedIdx = -1
            for ($i = 0; $i -lt 4; $i++) {
                $cleanOpt = $cleanOptions[$i]
                if ($cleanOpt -eq $solution.Value.ToString() -or $cleanOpt.ToLower() -eq $solution.PlaceName.ToLower()) {
                    $matchedIdx = $i
                    break
                }
            }
            
            if ($matchedIdx -ne -1) {
                $expectedLetter = ([char]([int][char]'A' + $matchedIdx)).ToString()
                $expectedText = $options[$matchedIdx]
                
                if ($q.CorrectAnswer -ne $expectedLetter) {
                    $isMismatched = $true
                    $reason = "Place Value Mismatch. Mathematical value of $digit in $number is $($solution.Value) ($($solution.PlaceName)), found at Option $expectedLetter ($expectedText), but stored answer is $($q.CorrectAnswer) ($($options[[char][int]$q.CorrectAnswer[0] - [char]'A']))"
                }
            }
        }
    }
    # Decimal Place Value
    elseif ($q.Text -match "(?i)place\s+value\s+of\s+(?:the\s+digit\s+)?(\d+)\s+in\s+the\s+decimal\s+number\s+([\d,.]+)") {
        $digit = $Matches[1]
        $number = $Matches[2]
        
        $solution = Solve-PlaceValueDecimal $digit $number
        if ($null -ne $solution) {
            $matchedIdx = -1
            for ($i = 0; $i -lt 4; $i++) {
                $cleanOpt = $cleanOptions[$i]
                if ($cleanOpt -eq $solution.Value.ToString() -or $cleanOpt.ToLower() -eq $solution.PlaceName.ToLower()) {
                    $matchedIdx = $i
                    break
                }
            }
            
            if ($matchedIdx -ne -1) {
                $expectedLetter = ([char]([int][char]'A' + $matchedIdx)).ToString()
                $expectedText = $options[$matchedIdx]
                
                if ($q.CorrectAnswer -ne $expectedLetter) {
                    $isMismatched = $true
                    $reason = "Decimal Place Value Mismatch. Mathematical value of $digit in $number is $($solution.Value) ($($solution.PlaceName)), found at Option $expectedLetter ($expectedText), but stored answer is $($q.CorrectAnswer)"
                }
            }
        }
    }
    # -------------------------------------------------------------
    # RULE 2: Simple Arithmetic Verification
    # -------------------------------------------------------------
    elseif ($q.Text -match "(?i)what is\s+([\d\s+\-*x/\u2013\u2014\u2212]+)\s*\??$") {
        $solution = Solve-SimpleArithmetic $q.Text
        if ($null -ne $solution) {
            $matchedIdx = -1
            for ($i = 0; $i -lt 4; $i++) {
                if ($cleanOptions[$i] -eq $solution.ToString()) {
                    $matchedIdx = $i
                    break
                }
            }
            
            if ($matchedIdx -ne -1) {
                $expectedLetter = ([char]([int][char]'A' + $matchedIdx)).ToString()
                $expectedText = $options[$matchedIdx]
                
                if ($q.CorrectAnswer -ne $expectedLetter) {
                    $isMismatched = $true
                    $reason = "Arithmetic Solution Mismatch. Calculated solution to '$($q.Text)' is $solution, found at Option $expectedLetter ($expectedText), but stored answer is $($q.CorrectAnswer)"
                }
            }
        }
    }
    
    # 5. Handle Mismatched Questions
    if ($isMismatched) {
        $errorsFound++
        Write-Host "---------------------------------------------------------------------" -ForegroundColor Yellow
        Write-Host "ERROR FOUND in Question Bank!" -ForegroundColor Red
        Write-Host "Question ID: $($q.Id)" -ForegroundColor Cyan
        Write-Host "Text: $($q.Text)" -ForegroundColor White
        Write-Host "Options: $($q.OptionsJson)" -ForegroundColor Gray
        Write-Host "Stored Answer: $($q.CorrectAnswer)  |  EXPECTED ANSWER: $expectedLetter" -ForegroundColor Magenta
        Write-Host "Reason: $reason" -ForegroundColor Yellow
        
        # Prepare explanation fix
        $fixedExplanation = "Mathematical solution verifies that the correct answer is option $expectedLetter ($expectedText). " + $q.Explanation
        $fixedExplanation = $fixedExplanation.Replace("'", "''")
        
        # Add to SQL fix builder
        $sqlFixes.AppendLine("-- Correcting answer for: $($q.Text.Replace("'", "''"))") | Out-Null
        $sqlFixes.AppendLine("IF EXISTS (SELECT 1 FROM QuestionBank WHERE QuestionBankId = '$($q.Id)')") | Out-Null
        $sqlFixes.AppendLine("BEGIN") | Out-Null
        $sqlFixes.AppendLine("    UPDATE QuestionBank") | Out-Null
        $sqlFixes.AppendLine("    SET CorrectAnswer = '$expectedLetter',") | Out-Null
        $sqlFixes.AppendLine("        Explanation = N'$fixedExplanation'") | Out-Null
        $sqlFixes.AppendLine("    WHERE QuestionBankId = '$($q.Id)';") | Out-Null
        $sqlFixes.AppendLine("END;") | Out-Null
        $sqlFixes.AppendLine() | Out-Null
        
        # Directly Fix in Database if AutoFix switch is set
        if ($AutoFix) {
            $fixCmd = $conn.CreateCommand()
            $fixCmd.CommandText = "UPDATE QuestionBank SET CorrectAnswer = @CorrectAnswer, Explanation = @Explanation WHERE QuestionBankId = @Id"
            $fixCmd.Parameters.AddWithValue("@CorrectAnswer", $expectedLetter) | Out-Null
            $fixCmd.Parameters.AddWithValue("@Explanation", $fixedExplanation) | Out-Null
            $fixCmd.Parameters.AddWithValue("@Id", $q.Id) | Out-Null
            
            try {
                $fixCmd.ExecuteNonQuery() | Out-Null
                $fixesApplied++
                Write-Host ">>> AUTO-FIX: Question bank updated successfully." -ForegroundColor Green
            } catch {
                Write-Host ">>> AUTO-FIX FAILED: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
}

$sqlFixes.AppendLine("COMMIT TRANSACTION;") | Out-Null

# 6. Save SQL fixes to file
$fixFilePath = Join-Path $scriptDir "fix-questions.sql"
[System.IO.File]::WriteAllText($fixFilePath, $sqlFixes.ToString(), [System.Text.Encoding]::UTF8)

Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "                          SCAN SUMMARY" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "Questions Analyzed: $($questions.Count)" -ForegroundColor Cyan
Write-Host "Discrepancies / Errors Detected: $errorsFound" -ForegroundColor Yellow
Write-Host "Fixes Applied Programmatically: $fixesApplied" -ForegroundColor Green
Write-Host "SQL Fixes Script Written to: $fixFilePath" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green

$conn.Close()
