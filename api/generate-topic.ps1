param(
    [string]$Subject,
    [int]$Grade,
    [string]$Topic,
    [int]$Count = 25,
    [string]$Difficulty = "Advanced"
)

$AdminKey    = "cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt"
$ClaudeKey   = "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"
$AdminApi    = "http://localhost:5080/api/admin/import-questions"
$ClaudeApi   = "https://api.anthropic.com/v1/messages"
$ClaudeModel = "claude-3-haiku-20240307"

$SystemPrompt = @"
You are a senior examiner with 15+ years of experience writing competitive Olympiad questions for Indian school students.
# Output format — ONLY a valid JSON array, no prose, no code fences:
[
  {
    "QuestionText": "...",
    "Options": ["option A text", "option B text", "option C text", "option D text"],
    "CorrectAnswer": "A",
    "Topic": "$Topic",
    "SubTopic": null,
    "Difficulty": "$Difficulty",
    "Explanation": "2-4 sentence plain-English explanation"
  }
]
CorrectAnswer must be exactly "A", "B", "C", or "D".
"@

$userMsg = "Generate exactly $Count multiple-choice questions for Class $Grade $Subject specifically on the topic '$Topic' at $Difficulty difficulty. Return ONLY the JSON array."

$bodyObj = @{
    model      = $ClaudeModel
    max_tokens = 4000
    system     = $SystemPrompt
    messages   = @(@{ role = "user"; content = $userMsg })
}
$bodyJson = ConvertTo-Json -InputObject $bodyObj -Depth 5

$headers = @{
    "x-api-key"         = $ClaudeKey
    "anthropic-version" = "2023-06-01"
    "content-type"      = "application/json"
}

Write-Host "Calling Claude for $Count questions on $Subject - $Topic..."
try {
    $resp = Invoke-RestMethod -Uri $ClaudeApi -Method Post -Headers $headers -Body $bodyJson -TimeoutSec 120
    $text = ($resp.content | Where-Object { $_.type -eq "text" } | Select-Object -First 1).text

    $start = $text.IndexOf('[')
    $end   = $text.LastIndexOf(']')
    if ($start -lt 0 -or $end -le $start) { throw "No JSON array in response" }
    $jsonArray = $text.Substring($start, $end - $start + 1)
    
    $parsed = $jsonArray | ConvertFrom-Json
    Write-Host "Successfully generated $($parsed.Count) questions."
    
    $encSubject = [Uri]::EscapeDataString($Subject)
    $url = "$AdminApi?subject=$encSubject&grade=$Grade"
    
    $importResp = Invoke-RestMethod -Uri $url -Method Post -Headers @{ "X-Admin-Key" = $AdminKey; "Content-Type" = "application/json; charset=utf-8" } -Body ([System.Text.Encoding]::UTF8.GetBytes($jsonArray))
    
    Write-Host "Imported: Inserted $($importResp.inserted), Skipped $($importResp.skipped), Errors $($importResp.errors.Count)"
} catch {
    Write-Host "Error: $_"
}
