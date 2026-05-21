$connectionString = "Server=localhost;Database=OlympiadReady;Integrated Security=True;TrustServerCertificate=True;"
$conn = New-Object System.Data.SqlClient.SqlConnection($connectionString)
$conn.Open()

# Clear existing grade 4 questions to prevent duplicates on re-run
$delCmd = $conn.CreateCommand()
$delCmd.CommandText = "DELETE FROM QuestionBank WHERE Grade = 4"
$delCmd.ExecuteNonQuery() | Out-Null
Write-Host "Cleared existing grade 4 questions."

$seedDir = "D:\Nyxen\OlympiadReady\OlympiadReadySolutions\seed-data"
$files = Get-ChildItem -Path $seedDir -Filter "*grade4*.json"

$count = 0

foreach ($file in $files) {
    # Extract subject alias from filename: sample-[subject alias]-grade4...
    $subjectAlias = ""
    if ($file.Name -match "^sample-(.*?)-grade4") {
        $subjectAlias = $matches[1]
    }

    $subject = switch -Wildcard ($subjectAlias.ToLower()) {
        "logicalreasoning" { "Logical Reasoning" }
        "computer" { "Computer Science" }
        "english" { "English" }
        "generalawareness" { "General Knowledge" }
        "hindi-olympiad" { "Hindi" }
        "mathematics" { "Mathematics" }
        "science" { "Science" }
        "social-studies" { "Social Studies" }
        default { $subjectAlias }
    }

    $grade = 4

    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    try {
        $json = $content | ConvertFrom-Json
    } catch {
        Write-Host "FAILED TO PARSE JSON in file: $($file.Name)"
        Write-Host $_.Exception.Message
        continue
    }

    foreach ($item in $json) {
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "
            INSERT INTO QuestionBank (Subject, Grade, Difficulty, Topic, SubTopic, QuestionText, OptionsJson, CorrectAnswer, Explanation)
            VALUES (@Subject, @Grade, @Difficulty, @Topic, @SubTopic, @QuestionText, @OptionsJson, @CorrectAnswer, @Explanation)
        "
        
        $optionsJson = ConvertTo-Json -InputObject $item.Options -Compress -Depth 10

        # Create parameter objects explicitly to avoid type issues and string encoding bugs
        $cmd.Parameters.Add("@Subject", [System.Data.SqlDbType]::NVarChar).Value = $subject
        $cmd.Parameters.Add("@Grade", [System.Data.SqlDbType]::Int).Value = $grade
        
        $difficulty = if ($null -eq $item.Difficulty) { "Foundation" } else { $item.Difficulty }
        $topic = if ($null -eq $item.Topic) { "" } else { $item.Topic }
        $subTopic = if ($null -eq $item.SubTopic) { "" } else { $item.SubTopic }
        $explanation = if ($null -eq $item.Explanation) { "" } else { $item.Explanation }
        
        $correctAnswerStr = if ($null -eq $item.CorrectAnswer) { "A" } else { $item.CorrectAnswer.Trim() }
        if ($correctAnswerStr.Length -gt 1) {
            $correctAnswerStr = $correctAnswerStr.Substring(0, 1)
        }

        $cmd.Parameters.Add("@Difficulty", [System.Data.SqlDbType]::NVarChar).Value = $difficulty
        $cmd.Parameters.Add("@Topic", [System.Data.SqlDbType]::NVarChar).Value = $topic
        $cmd.Parameters.Add("@SubTopic", [System.Data.SqlDbType]::NVarChar).Value = $subTopic
        $cmd.Parameters.Add("@QuestionText", [System.Data.SqlDbType]::NVarChar).Value = $item.QuestionText
        $cmd.Parameters.Add("@OptionsJson", [System.Data.SqlDbType]::NVarChar).Value = $optionsJson
        $cmd.Parameters.Add("@CorrectAnswer", [System.Data.SqlDbType]::NVarChar).Value = $correctAnswerStr
        $cmd.Parameters.Add("@Explanation", [System.Data.SqlDbType]::NVarChar).Value = $explanation

        try {
            $cmd.ExecuteNonQuery() | Out-Null
            $count++
        } catch {
            Write-Host "Failed to insert question: $($item.QuestionText)"
            Write-Host $_.Exception.Message
        }
    }
}

$conn.Close()
Write-Host "Imported $count grade 4 questions successfully."
