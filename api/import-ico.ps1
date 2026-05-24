$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Sanitize a string: replace known Unicode → ASCII, then strip anything that
# is not a printable ASCII character (32-126) or common whitespace (9, 10, 13).
# This ensures zero junk reaches the database regardless of what the JSON file
# contains.
# ---------------------------------------------------------------------------
function Sanitize-Text([string]$text) {
    if ($null -eq $text) { return "" }

    # Explicit Unicode → ASCII substitutions
    $map = [ordered]@{
        [char]0x20B9 = "Rs."    # ₹ Indian Rupee
        [char]0x00A3 = "GBP"   # £ Pound
        [char]0x20AC = "EUR"   # € Euro
        [char]0x2018 = "'"     # ' left single quote
        [char]0x2019 = "'"     # ' right single quote
        [char]0x201C = '"'     # " left double quote
        [char]0x201D = '"'     # " right double quote
        [char]0x2032 = "'"     # ′ prime
        [char]0x2033 = '"'     # ″ double prime
        [char]0x2013 = "-"     # – en dash
        [char]0x2014 = "-"     # — em dash
        [char]0x2012 = "-"     # ‒ figure dash
        [char]0x2015 = "-"     # ― horizontal bar
        [char]0x2212 = "-"     # − minus sign
        [char]0x2026 = "..."   # … ellipsis
        [char]0x00D7 = "x"     # × multiplication
        [char]0x00F7 = "/"     # ÷ division
        [char]0x2265 = ">="    # ≥
        [char]0x2264 = "<="    # ≤
        [char]0x2260 = "!="    # ≠
        [char]0x221A = "sqrt"  # √
        [char]0x00B2 = "^2"    # ²
        [char]0x00B3 = "^3"    # ³
        [char]0x00B9 = "^1"    # ¹
        [char]0x00BD = "1/2"   # ½
        [char]0x00BC = "1/4"   # ¼
        [char]0x00BE = "3/4"   # ¾
        [char]0x00B0 = " degrees" # °
        [char]0x00B7 = "."     # · middle dot
        [char]0x2022 = "-"     # • bullet
        [char]0x00A0 = " "     # non-breaking space
        [char]0x00AB = '"'     # «
        [char]0x00BB = '"'     # »
        [char]0x03B1 = "alpha" # α
        [char]0x03B2 = "beta"  # β
        [char]0x03C0 = "pi"    # π
        [char]0x03B4 = "delta" # δ
        [char]0x03B8 = "theta" # θ
    }
    foreach ($kv in $map.GetEnumerator()) {
        $text = $text.Replace([string]$kv.Key, $kv.Value)
    }

    # Drop every character that is not printable ASCII or common whitespace
    $sb = [System.Text.StringBuilder]::new($text.Length)
    foreach ($ch in $text.ToCharArray()) {
        $code = [int]$ch
        if ($code -eq 9 -or $code -eq 10 -or $code -eq 13 -or ($code -ge 32 -and $code -le 126)) {
            [void]$sb.Append($ch)
        }
        # All other characters are silently dropped
    }

    # Collapse double spaces that may result from character removal
    $result = [System.Text.RegularExpressions.Regex]::Replace($sb.ToString(), " {2,}", " ").Trim()
    return $result
}

# ---------------------------------------------------------------------------
$connectionString = "Server=localhost;Database=OlympiadReady;Integrated Security=True;TrustServerCertificate=True;"
$conn = New-Object System.Data.SqlClient.SqlConnection($connectionString)
$conn.Open()

$seedDir = "D:\Nyxen\OlympiadReady\OlympiadReadySolutions\seeded"

# ICO files: Grade 11 and 12 Commerce
$files = Get-ChildItem -Path $seedDir -Filter "sample-commerce-grade1*.json"

$count   = 0
$skipped = 0

foreach ($file in $files) {
    if ($file.Name -match "grade(\d+)") {
        $grade = [int]$matches[1]
    } else {
        Write-Warning "Could not determine grade from filename: $($file.Name) - skipping"
        continue
    }

    Write-Host "Processing $($file.Name) (Grade $grade)..."

    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    $json = $content | ConvertFrom-Json

    foreach ($item in $json) {
        $qText = Sanitize-Text $item.QuestionText
        if ([string]::IsNullOrWhiteSpace($qText)) {
            $skipped++
            continue
        }

        # Sanitize each option individually before re-serializing
        $cleanOptions = @()
        foreach ($opt in $item.Options) {
            $cleanOptions += Sanitize-Text $opt
        }
        $optionsJson = ConvertTo-Json -InputObject $cleanOptions -Compress -Depth 10

        $difficulty  = Sanitize-Text $(if ($null -eq $item.Difficulty  -or $item.Difficulty  -eq "") { "Foundation" } else { $item.Difficulty })
        $topic       = Sanitize-Text $(if ($null -eq $item.Topic       -or $item.Topic       -eq "") { "Commerce"    } else { $item.Topic })
        $subTopic    = Sanitize-Text $(if ($null -eq $item.SubTopic)   { "" } else { $item.SubTopic })
        $explanation = Sanitize-Text $(if ($null -eq $item.Explanation){ "" } else { $item.Explanation })
        $answer      = $(if ($null -eq $item.CorrectAnswer) { "A" } else { ($item.CorrectAnswer).ToString().Trim().ToUpper() })

        # Validate answer letter
        if ($answer -notin @("A","B","C","D")) { $answer = "A" }

        $cmd = $conn.CreateCommand()
        $cmd.CommandText = @"
            INSERT INTO QuestionBank
                (QuestionBankId, Subject, Grade, Difficulty, Topic, SubTopic, QuestionText, OptionsJson, CorrectAnswer, Explanation, CreatedAt)
            VALUES
                (NEWID(), @Subject, @Grade, @Difficulty, @Topic, @SubTopic, @QuestionText, @OptionsJson, @CorrectAnswer, @Explanation, GETUTCDATE())
"@

        $cmd.Parameters.Add("@Subject",       [System.Data.SqlDbType]::NVarChar).Value = "Commerce"
        $cmd.Parameters.Add("@Grade",         [System.Data.SqlDbType]::Int).Value      = $grade
        $cmd.Parameters.Add("@Difficulty",    [System.Data.SqlDbType]::NVarChar).Value = $difficulty
        $cmd.Parameters.Add("@Topic",         [System.Data.SqlDbType]::NVarChar).Value = $topic
        $cmd.Parameters.Add("@SubTopic",      [System.Data.SqlDbType]::NVarChar).Value = $subTopic
        $cmd.Parameters.Add("@QuestionText",  [System.Data.SqlDbType]::NVarChar).Value = $qText
        $cmd.Parameters.Add("@OptionsJson",   [System.Data.SqlDbType]::NVarChar).Value = $optionsJson
        $cmd.Parameters.Add("@CorrectAnswer", [System.Data.SqlDbType]::NVarChar).Value = $answer
        $cmd.Parameters.Add("@Explanation",   [System.Data.SqlDbType]::NVarChar).Value = $explanation

        $cmd.ExecuteNonQuery() | Out-Null
        $count++
    }
    Write-Host "  -> Done: $($file.Name)"
}

$conn.Close()
Write-Host ""
Write-Host "Done. Imported: $count | Skipped (empty): $skipped"
