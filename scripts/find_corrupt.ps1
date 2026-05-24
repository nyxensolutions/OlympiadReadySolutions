$questions = sqlcmd -S localhost -d OlympiadReady -E -C -h -1 -y 0 -Q "SELECT QuestionText FROM QuestionBank WHERE QuestionText LIKE '%%' OR QuestionText LIKE '%Â%'"
$patterns = @{}
foreach ($q in $questions) {
    if ([string]::IsNullOrWhiteSpace($q)) { continue }
    # Look for - or Â° or ,
    if ($q -match '\-') { $patterns['-']++ }
    if ($q -match 'Â°') { $patterns['Â°']++ }
    if ($q -match ',') { $patterns[',']++ }
    if ($q -match 'â‚¹') { $patterns['â‚¹']++ }
}
Write-Host "Patterns found:"
foreach ($key in $patterns.Keys) {
    Write-Host "$key -> $($patterns[$key]) times"
}
