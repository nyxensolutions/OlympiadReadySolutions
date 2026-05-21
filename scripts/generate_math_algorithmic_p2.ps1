$script:questions = @()

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

# --- Topic: Basic Geometrical Ideas & Elementary Shapes ---
$shapes = @(
    @{name="triangle"; sides=3; sym=3},
    @{name="square"; sides=4; sym=4},
    @{name="pentagon"; sides=5; sym=5},
    @{name="hexagon"; sides=6; sym=6},
    @{name="octagon"; sides=8; sym=8}
)
for ($i = 0; $i -lt 30; $i++) {
    # Foundation
    $s = Get-Random -InputObject $shapes
    $opts = @($s.sides.ToString(), ($s.sides+1).ToString(), ($s.sides-1).ToString(), ($s.sides+2).ToString())
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf($s.sides.ToString())
    Add-Question -text "How many sides does a regular $($s.name) have?" -options $opts -correctIdx $correctIdx -topic "Basic Geometrical Ideas" -difficulty "Foundation" -explanation "A $($s.name) is a polygon with $($s.sides) sides."
}

for ($i = 0; $i -lt 30; $i++) {
    # Advanced - Angles
    $rightAngles = Get-Random -Minimum 2 -Maximum 6
    $deg = $rightAngles * 90
    $opts = @(
        "$deg degrees",
        "$($deg+90) degrees",
        "$($deg-90) degrees",
        "$($deg*2) degrees"
    )
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf("$deg degrees")
    Add-Question -text "What is the measure of $rightAngles right angles?" -options $opts -correctIdx $correctIdx -topic "Understanding Elementary Shapes" -difficulty "Advanced" -explanation "One right angle is 90 degrees. $rightAngles right angles = $rightAngles × 90 = $deg degrees."
}

# --- Topic: Mensuration ---
for ($i = 0; $i -lt 40; $i++) {
    # Foundation: Perimeter/Area of Rectangle
    $l = Get-Random -Minimum 10 -Maximum 50
    $b = Get-Random -Minimum 5 -Maximum ($l - 1)
    $isArea = Get-Random -InputObject @($true, $false)
    if ($isArea) {
        $ans = $l * $b
        $opts = @("$ans sq cm", "$($ans+10) sq cm", "$($ans-10) sq cm", "$($l+$b) sq cm")
        $opts = $opts | Sort-Object { Get-Random }
        $correctIdx = $opts.IndexOf("$ans sq cm")
        Add-Question -text "Find the area of a rectangle with length $l cm and breadth $b cm." -options $opts -correctIdx $correctIdx -topic "Mensuration" -difficulty "Foundation" -explanation "Area = length × breadth = $l × $b = $ans sq cm."
    } else {
        $ans = 2 * ($l + $b)
        $opts = @("$ans cm", "$($ans+2) cm", "$($ans-2) cm", "$($l*$b) cm")
        $opts = $opts | Sort-Object { Get-Random }
        $correctIdx = $opts.IndexOf("$ans cm")
        Add-Question -text "Find the perimeter of a rectangle with length $l cm and breadth $b cm." -options $opts -correctIdx $correctIdx -topic "Mensuration" -difficulty "Foundation" -explanation "Perimeter = 2 × (length + breadth) = 2 × ($l + $b) = $ans cm."
    }
}

for ($i = 0; $i -lt 40; $i++) {
    # Advanced: Cost of fencing
    $s = Get-Random -Minimum 20 -Maximum 100
    $rate = Get-Random -Minimum 5 -Maximum 25
    $peri = 4 * $s
    $cost = $peri * $rate
    $opts = @("₹$cost", "₹$($cost+100)", "₹$($cost-100)", "₹$($peri)")
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf("₹$cost")
    Add-Question -text "Find the cost of fencing a square park of side $s m at the rate of ₹$rate per meter." -options $opts -correctIdx $correctIdx -topic "Mensuration" -difficulty "Advanced" -explanation "Perimeter of square = 4 × side = 4 × $s = $peri m. Cost = $peri × $rate = ₹$cost."
}

# --- Topic: Data Handling ---
for ($i = 0; $i -lt 30; $i++) {
    $scale = Get-Random -Minimum 5 -Maximum 50
    $pics = Get-Random -Minimum 2 -Maximum 12
    $ans = $scale * $pics
    $opts = @("$ans", "$($ans+$scale)", "$($ans-$scale)", "$($scale*$pics + 5)")
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf("$ans")
    Add-Question -text "In a pictograph, if one symbol represents $scale books, how many books are represented by $pics symbols?" -options $opts -correctIdx $correctIdx -topic "Data Handling" -difficulty "Foundation" -explanation "1 symbol = $scale books. $pics symbols = $pics × $scale = $ans books."
}

# --- Topic: Symmetry ---
for ($i = 0; $i -lt 30; $i++) {
    $s = Get-Random -InputObject $shapes
    $opts = @($s.sym.ToString(), ($s.sym+1).ToString(), ($s.sym-1).ToString(), "0")
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf($s.sym.ToString())
    Add-Question -text "How many lines of symmetry does a regular $($s.name) have?" -options $opts -correctIdx $correctIdx -topic "Symmetry" -difficulty "Foundation" -explanation "A regular polygon with n sides has n lines of symmetry. A regular $($s.name) has $($s.sym) sides, thus $($s.sym) lines of symmetry."
}

# --- Topic: Algebra (Additional) ---
for ($i = 0; $i -lt 30; $i++) {
    $x = Get-Random -Minimum 5 -Maximum 20
    $c = Get-Random -Minimum 2 -Maximum 10
    $ans = $x - $c
    $opts = @("$ans", "$($ans+1)", "$($ans-1)", "$($x+$c)")
    $opts = $opts | Sort-Object { Get-Random }
    $correctIdx = $opts.IndexOf("$ans")
    Add-Question -text "Rohan's current age is x years. What was his age $c years ago if x = $x?" -options $opts -correctIdx $correctIdx -topic "Algebra" -difficulty "Foundation" -explanation "Age $c years ago = x - $c. If x = $x, then $x - $c = $ans years."
}

# Ensure valid options formatting (4 unique)
$validQuestions = @()
foreach ($q in $script:questions) {
    $uniqueOpts = $q.Options | Select-Object -Unique
    if ($uniqueOpts.Length -eq 4) {
        $validQuestions += $q
    }
}

$validQuestions | ConvertTo-Json -Depth 10 | Out-File ".\scripts\math_g6_algorithmic_p2.json" -Encoding UTF8
Write-Host "Generated $($validQuestions.Length) unique questions to math_g6_algorithmic_p2.json"
