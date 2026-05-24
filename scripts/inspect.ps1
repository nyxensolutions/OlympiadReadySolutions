$text = sqlcmd -S localhost -d OlympiadReady -E -C -h -1 -Q "SELECT TOP 1 QuestionText FROM QuestionBank WHERE QuestionText LIKE '%109%'"
$text = $text.Trim()
Write-Host "Text: $text"
foreach ($c in $text.ToCharArray()) {
    $val = [int]$c
    Write-Host ("'{0}' -> U+{1:X4}" -f $c, $val)
}
