param(
    [string]$File,
    [string]$Subject,
    [int]$Grade
)

$connectionString = "Server=localhost;Database=OlympiadReady;Integrated Security=True;TrustServerCertificate=True;"
$conn = New-Object System.Data.SqlClient.SqlConnection($connectionString)
$conn.Open()

$content = [System.IO.File]::ReadAllText($File, [System.Text.Encoding]::UTF8)
$json = $content | ConvertFrom-Json

$count = 0
foreach ($item in $json) {
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "
        INSERT INTO QuestionBank (Subject, Grade, Difficulty, Topic, SubTopic, QuestionText, OptionsJson, CorrectAnswer, Explanation)
        VALUES (@Subject, @Grade, @Difficulty, @Topic, @SubTopic, @QuestionText, @OptionsJson, @CorrectAnswer, @Explanation)
    "
    
    $optionsJson = ConvertTo-Json -InputObject $item.Options -Compress -Depth 10

    $cmd.Parameters.Add("@Subject", [System.Data.SqlDbType]::NVarChar).Value = $Subject
    $cmd.Parameters.Add("@Grade", [System.Data.SqlDbType]::Int).Value = $Grade
    
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

$conn.Close()
Write-Host "Imported $count questions successfully for $Subject Grade $Grade."
