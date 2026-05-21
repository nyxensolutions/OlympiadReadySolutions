$connectionString = "Server=localhost;Database=OlympiadReady;Integrated Security=True;TrustServerCertificate=True;"
$conn = New-Object System.Data.SqlClient.SqlConnection($connectionString)
$conn.Open()

function Insert-Question {
    param ($topic, $difficulty, $questionText, $options, $correctAnswerStr, $explanation)
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "INSERT INTO QuestionBank (Subject, Grade, Difficulty, Topic, SubTopic, QuestionText, OptionsJson, CorrectAnswer, Explanation) VALUES (@Subj, @Grd, @Diff, @Top, @SubT, @QText, @Opts, @Corr, @Exp)"
    $cmd.Parameters.Add("@Subj", [System.Data.SqlDbType]::NVarChar).Value = "Mathematics"
    $cmd.Parameters.Add("@Grd", [System.Data.SqlDbType]::Int).Value = 6
    $cmd.Parameters.Add("@Diff", [System.Data.SqlDbType]::NVarChar).Value = $difficulty
    $cmd.Parameters.Add("@Top", [System.Data.SqlDbType]::NVarChar).Value = $topic
    $cmd.Parameters.Add("@SubT", [System.Data.SqlDbType]::NVarChar).Value = ""
    $cmd.Parameters.Add("@QText", [System.Data.SqlDbType]::NVarChar).Value = $questionText
    $cmd.Parameters.Add("@Opts", [System.Data.SqlDbType]::NVarChar).Value = (ConvertTo-Json $options -Compress)
    $cmd.Parameters.Add("@Corr", [System.Data.SqlDbType]::NVarChar).Value = $correctAnswerStr
    $cmd.Parameters.Add("@Exp", [System.Data.SqlDbType]::NVarChar).Value = $explanation
    $cmd.ExecuteNonQuery() | Out-Null
}

$letters = @("A", "B", "C", "D")

function Create-MCQ {
    param ($text, $ansStr, $wrong1, $wrong2, $wrong3, $topic, $difficulty, $explanation)
    $opts = @($ansStr, $wrong1, $wrong2, $wrong3) | Select-Object -Unique
    if ($opts.Length -ne 4) { return } # Skip if not 4 unique
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf($ansStr)
    Insert-Question -topic $topic -difficulty $difficulty -questionText $text -options $opts -correctAnswerStr $letters[$correctIdx] -explanation $explanation
}

Write-Host "Generating Algebra..."
for ($i=0; $i -lt 35; $i++) {
    $c = Get-Random -Min 2 -Max 15
    $var = Get-Random -InputObject @('x','y','z','p','q')
    Create-MCQ "If the cost of one notebook is ₹$c, what is the cost of $var notebooks?" "₹$c$var" "₹$($c+1)$var" "₹$($c-1)$var" "₹$var" "Algebra" "Foundation" "Cost of 1 notebook = $c. Cost of $var notebooks = $c × $var = $c$var."
}

Write-Host "Generating Basic Geometrical Ideas..."
for ($i=0; $i -lt 40; $i++) {
    $pts = Get-Random -Min 3 -Max 10
    $ans = ($pts * ($pts - 1)) / 2
    Create-MCQ "How many distinct line segments can be drawn using $pts non-collinear points?" "$ans" "$($ans+1)" "$($ans-1)" "$($pts*2)" "Basic Geometrical Ideas" "Advanced" "Number of segments = n(n-1)/2 = $pts($($pts-1))/2 = $ans."
}

Write-Host "Generating Data Handling..."
for ($i=0; $i -lt 25; $i++) {
    $scale = Get-Random -Min 10 -Max 50
    $marks = Get-Random -Min 2 -Max 8
    $ans = $scale * $marks
    Create-MCQ "In a bar graph, if 1 unit length represents $scale students, what do $marks units represent?" "$ans students" "$($ans+5) students" "$($ans-10) students" "$($scale*$marks*2) students" "Data Handling" "Foundation" "1 unit = $scale. $marks units = $scale × $marks = $ans."
}

Write-Host "Generating Decimals..."
for ($i=0; $i -lt 30; $i++) {
    $w = Get-Random -Min 1 -Max 20
    $f = Get-Random -Min 1 -Max 99
    $fStr = $f.ToString("D2")
    $ans = [math]::Round($w + ($f / 100), 2)
    Create-MCQ "Convert $w and $f/100 to a decimal." "$ans" "$($ans+0.1)" "$($ans-0.1)" "$($w.$f0)" "Decimals" "Foundation" "$w whole and $f hundredths is $ans."
}

Write-Host "Generating Logical Reasoning..."
for ($i=0; $i -lt 45; $i++) {
    $start = Get-Random -Min 2 -Max 10
    $step = Get-Random -Min 2 -Max 5
    $n1 = $start; $n2 = $start+$step; $n3 = $n2+$step; $n4 = $n3+$step; $ans = $n4+$step
    Create-MCQ "Find the next number in the series: $n1, $n2, $n3, $n4, ..." "$ans" "$($ans+1)" "$($ans-1)" "$($ans+$step)" "Logical Reasoning" "Foundation" "The pattern adds $step each time. $n4 + $step = $ans."
}

Write-Host "Generating Playing with Numbers..."
for ($i=0; $i -lt 35; $i++) {
    $f1 = Get-Random -Min 2 -Max 6
    $f2 = Get-Random -Min 7 -Max 12
    $ans = $f1 * $f2
    Create-MCQ "Which of these is a multiple of both $f1 and $f2?" "$ans" "$($ans+1)" "$($ans-1)" "$($ans+$f1)" "Playing with Numbers" "Foundation" "$ans is divisible by both $f1 and $f2."
}

Write-Host "Generating Practical Geometry..."
for ($i=0; $i -lt 50; $i++) {
    $r = Get-Random -Min 3 -Max 15
    $ans = $r * 2
    Create-MCQ "If the radius of a circle is $r cm, what is the length of its longest chord?" "$ans cm" "$($ans+1) cm" "$r cm" "$($ans*2) cm" "Practical Geometry" "Foundation" "The longest chord is the diameter, which is 2 × radius = 2 × $r = $ans cm."
}

Write-Host "Generating Ratio and Proportion..."
for ($i=0; $i -lt 30; $i++) {
    $a = Get-Random -Min 2 -Max 5
    $b = $a + (Get-Random -Min 1 -Max 4)
    $m = Get-Random -Min 2 -Max 6
    $ans = "$($a*$m):$($b*$m)"
    Create-MCQ "Find the equivalent ratio of ${a}:${b}." "$ans" "$($a*$m+1):$($b*$m)" "$($a*$m):$($b*$m-1)" "${b}:${a}" "Ratio and Proportion" "Foundation" "Multiplying both terms by $m gives $ans."
}

Write-Host "Generating Symmetry..."
for ($i=0; $i -lt 45; $i++) {
    $chars = @('A','B','C','D','E','M','U','V','W')
    $c = Get-Random -InputObject $chars
    Create-MCQ "How many lines of symmetry does the letter '$c' have?" "1" "0" "2" "3" "Symmetry" "Foundation" "The letter $c has 1 line of symmetry."
}

Write-Host "Generating Understanding Elementary Shapes..."
for ($i=0; $i -lt 45; $i++) {
    $hrs = Get-Random -Min 1 -Max 11
    $deg = $hrs * 30
    Create-MCQ "What angle is covered by the hour hand of a clock in $hrs hours?" "$deg°" "$($deg+30)°" "$($deg-30)°" "$($deg*2)°" "Understanding Elementary Shapes" "Advanced" "In 12 hours it covers 360°, so in 1 hour it covers 30°. In $hrs hours: $hrs × 30 = $deg°."
}

Write-Host "Generating Whole Numbers..."
for ($i=0; $i -lt 35; $i++) {
    $n = Get-Random -Min 100 -Max 999
    $ans = $n + 1
    Create-MCQ "What is the successor of $n?" "$ans" "$($n-1)" "$n" "$($n+2)" "Whole Numbers" "Foundation" "The successor is the next number, $n + 1 = $ans."
}

$conn.Close()
Write-Host "Done generating missing math topics."
