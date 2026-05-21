$ErrorActionPreference = "Stop"

$connectionString = "Server=localhost;Database=OlympiadReady;Integrated Security=True;TrustServerCertificate=True;"
$conn = New-Object System.Data.SqlClient.SqlConnection($connectionString)
$conn.Open()

$seedDir = "D:\Nyxen\OlympiadReady\OlympiadReadySolutions\seed-data"
$files = Get-ChildItem -Path $seedDir -Filter "sample-hindi-*.json"

$count = 0

foreach ($file in $files) {
    if ($file.Name -match "grade(\d+)") {
        $grade = [int]$matches[1]
    } else {
        $grade = 3 # default fallback
    }

    $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
    $json = $content | ConvertFrom-Json

    foreach ($item in $json) {
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "
            INSERT INTO QuestionBank (Subject, Grade, Difficulty, Topic, SubTopic, QuestionText, OptionsJson, CorrectAnswer, Explanation)
            VALUES (@Subject, @Grade, @Difficulty, @Topic, @SubTopic, @QuestionText, @OptionsJson, @CorrectAnswer, @Explanation)
        "
        
        $optionsJson = ConvertTo-Json -InputObject $item.Options -Compress -Depth 10

        # Create parameter objects explicitly to avoid type issues
        $cmd.Parameters.Add("@Subject", [System.Data.SqlDbType]::NVarChar).Value = "Hindi"
        $cmd.Parameters.Add("@Grade", [System.Data.SqlDbType]::Int).Value = $grade
        
        $difficulty = if ($null -eq $item.Difficulty) { "Foundation" } else { $item.Difficulty }
        $topic = if ($null -eq $item.Topic) { "Hindi" } else { $item.Topic }
        $subTopic = if ($null -eq $item.SubTopic) { "" } else { $item.SubTopic }
        $explanation = if ($null -eq $item.Explanation) { "" } else { $item.Explanation }

        $cmd.Parameters.Add("@Difficulty", [System.Data.SqlDbType]::NVarChar).Value = $difficulty
        $cmd.Parameters.Add("@Topic", [System.Data.SqlDbType]::NVarChar).Value = $topic
        $cmd.Parameters.Add("@SubTopic", [System.Data.SqlDbType]::NVarChar).Value = $subTopic
        $cmd.Parameters.Add("@QuestionText", [System.Data.SqlDbType]::NVarChar).Value = $item.QuestionText
        $cmd.Parameters.Add("@OptionsJson", [System.Data.SqlDbType]::NVarChar).Value = $optionsJson
        $cmd.Parameters.Add("@CorrectAnswer", [System.Data.SqlDbType]::NVarChar).Value = $item.CorrectAnswer
        $cmd.Parameters.Add("@Explanation", [System.Data.SqlDbType]::NVarChar).Value = $explanation

        $cmd.ExecuteNonQuery() | Out-Null
        $count++
    }
}

$conn.Close()
Write-Host "Imported $count questions successfully."
