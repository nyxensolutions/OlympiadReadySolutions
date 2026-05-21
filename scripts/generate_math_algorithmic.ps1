$questions = @()

function Add-Question {
    param (
        [string]$text,
        [string[]]$options,
        [int]$correctIdx,
        [string]$topic,
        [string]$difficulty,
        [string]$explanation
    )
    $letters = @("A", "B", "C", "D")
    $script:questions += [pscustomobject]@{
        QuestionText = $text
        Options = $options
        CorrectAnswer = $letters[$correctIdx]
        Topic = $topic
        Difficulty = $difficulty
        Explanation = $explanation
    }
}

# --- Topic: Integers ---
for ($i = 0; $i -lt 25; $i++) {
    $a = Get-Random -Minimum -50 -Maximum 50
    $b = Get-Random -Minimum -50 -Maximum 50
    $ans = $a + $b
    
    $opts = @(
        $ans.ToString(),
        ($ans + (Get-Random -Minimum 1 -Maximum 10)).ToString(),
        ($ans - (Get-Random -Minimum 1 -Maximum 10)).ToString()
    )
    if ($ans -ne 0) { $opts += (-$ans).ToString() } else { $opts += "5" }
    
    # Shuffle options
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf($ans.ToString())
    
    Add-Question -text "Evaluate: $a + ($b)" -options $opts -correctIdx $correctIdx -topic "Integers" -difficulty "Foundation" -explanation "The sum of $a and $b is $ans."
}

for ($i = 0; $i -lt 25; $i++) {
    $temp1 = Get-Random -Minimum 5 -Maximum 25
    $drop = Get-Random -Minimum 10 -Maximum 30
    $ans = $temp1 - $drop
    
    $opts = @(
        "$ans`°C",
        "$($ans + 2)`°C",
        "$($ans - 2)`°C",
        "$($temp1 + $drop)`°C"
    )
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf("$ans`°C")
    
    Add-Question -text "The temperature was $temp1`°C in the afternoon. By midnight, it dropped by $drop`°C. What is the temperature at midnight?" -options $opts -correctIdx $correctIdx -topic "Integers" -difficulty "Advanced" -explanation "Initial temperature = $temp1. Drop = $drop. Final = $temp1 - $drop = $ans`°C."
}

# --- Topic: Fractions ---
for ($i = 0; $i -lt 25; $i++) {
    $factor = Get-Random -Minimum 2 -Maximum 12
    $num = Get-Random -Minimum 1 -Maximum 9
    $den = Get-Random -Minimum ($num + 1) -Maximum 12
    $ans = "$num/$den"
    
    $opts = @(
        $ans,
        "$($num+1)/$den",
        "$num/$($den+1)",
        "$den/$num"
    )
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf($ans)
    
    Add-Question -text "Reduce the fraction $($num*$factor)/$($den*$factor) to its simplest form." -options $opts -correctIdx $correctIdx -topic "Fractions" -difficulty "Foundation" -explanation "Divide numerator and denominator by their greatest common divisor, which is $factor. The simplest form is $ans."
}

for ($i = 0; $i -lt 25; $i++) {
    $den1 = Get-Random -InputObject @(2,3,4,5)
    $den2 = Get-Random -InputObject @(3,4,5,7)
    if ($den1 -eq $den2) { $den2++ }
    $num1 = Get-Random -Minimum 1 -Maximum $den1
    $num2 = Get-Random -Minimum 1 -Maximum $den2
    
    $ans_num = ($num1 * $den2) + ($num2 * $den1)
    $ans_den = $den1 * $den2
    $ans = "$ans_num/$ans_den"
    
    $opts = @(
        $ans,
        "$($num1+$num2)/$($den1+$den2)",
        "$([math]::Abs($ans_num-2))/$ans_den",
        "$($ans_num+2)/$ans_den"
    )
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf($ans)
    
    Add-Question -text "Rohan ate $num1/$den1 of a pizza and Sneha ate $num2/$den2 of the same pizza. How much pizza did they eat altogether? (Assuming answer is unsimplified)" -options $opts -correctIdx $correctIdx -topic "Fractions" -difficulty "Advanced" -explanation "LCM of $den1 and $den2 is $ans_den. $num1/$den1 = $($num1*$den2)/$ans_den and $num2/$den2 = $($num2*$den1)/$ans_den. Sum = $ans_num/$ans_den."
}

# --- Topic: Decimals ---
for ($i = 0; $i -lt 25; $i++) {
    $whole = Get-Random -Minimum 0 -Maximum 50
    $tenths = Get-Random -Minimum 0 -Maximum 9
    $hundredths = Get-Random -Minimum 1 -Maximum 9
    $ans = "$whole.$tenths$hundredths"
    
    $opts = @(
        $ans,
        "$whole.$hundredths$tenths",
        "$whole.0$tenths$hundredths",
        "$whole$tenths.$hundredths"
    )
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf($ans)
    
    Add-Question -text "Write as a decimal: $whole + $tenths/10 + $hundredths/100" -options $opts -correctIdx $correctIdx -topic "Decimals" -difficulty "Foundation" -explanation "$tenths/10 is $tenths tenths and $hundredths/100 is $hundredths hundredths. Thus, $ans."
}

for ($i = 0; $i -lt 25; $i++) {
    $price1 = [math]::Round((Get-Random -Minimum 10.0 -Maximum 50.0), 2)
    $price2 = [math]::Round((Get-Random -Minimum 5.0 -Maximum 30.0), 2)
    $paid = 100.00
    $totalPrice = $price1 + $price2
    $ans = [math]::Round($paid - $totalPrice, 2)
    $ansStr = "{0:N2}" -f $ans
    
    $opts = @(
        "₹$ansStr",
        "₹{0:N2}" -f ($ans+1),
        "₹{0:N2}" -f ($ans-1),
        "₹{0:N2}" -f ($ans+0.5)
    )
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf("₹$ansStr")
    
    Add-Question -text "Aarav bought a book for ₹$("{0:N2}" -f $price1) and a pen for ₹$("{0:N2}" -f $price2). He gave a ₹100 note to the shopkeeper. How much change will he get back?" -options $opts -correctIdx $correctIdx -topic "Decimals" -difficulty "Advanced" -explanation "Total cost = $("{0:N2}" -f $price1) + $("{0:N2}" -f $price2) = $("{0:N2}" -f $totalPrice). Change = 100 - $("{0:N2}" -f $totalPrice) = $ansStr."
}

# --- Topic: Ratio and Proportion ---
for ($i = 0; $i -lt 25; $i++) {
    $factor = Get-Random -Minimum 2 -Maximum 10
    $a = Get-Random -Minimum 1 -Maximum 7
    $b = Get-Random -Minimum ($a + 1) -Maximum 9
    $ans = "${a}:${b}"
    
    $opts = @(
        $ans,
        "${b}:${a}",
        "$($a+1):$b",
        "${a}:$($b+1)"
    )
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf($ans)
    
    Add-Question -text "Find the ratio of $($a*$factor) to $($b*$factor) in its simplest form." -options $opts -correctIdx $correctIdx -topic "Ratio and Proportion" -difficulty "Foundation" -explanation "Divide both numbers by their HCF, which is $factor. Ratio is $ans."
}

$questions | ConvertTo-Json -Depth 10 | Out-File ".\scripts\math_g6_algorithmic.json" -Encoding UTF8
Write-Host "Generated $($questions.Length) questions to math_g6_algorithmic.json"
