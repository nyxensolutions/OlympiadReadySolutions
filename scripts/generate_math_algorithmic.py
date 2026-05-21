import json
import random

questions = []

def add_q(text, options, correct_idx, topic, difficulty, explanation):
    letters = ["A", "B", "C", "D"]
    questions.append({
        "QuestionText": text,
        "Options": options,
        "CorrectAnswer": letters[correct_idx],
        "Topic": topic,
        "Difficulty": difficulty,
        "Explanation": explanation
    })

# --- Topic: Integers ---
for _ in range(25):
    # Foundation: Addition/Subtraction of small integers
    a = random.randint(-50, 50)
    b = random.randint(-50, 50)
    ans = a + b
    opts = [str(ans), str(ans + random.randint(1, 10)), str(ans - random.randint(1, 10)), str(-ans if ans != 0 else random.randint(1,5))]
    random.shuffle(opts)
    add_q(f"Evaluate: {a} + ({b})", opts, opts.index(str(ans)), "Integers", "Foundation", f"The sum of {a} and {b} is {ans}.")

for _ in range(25):
    # Advanced: Word problems with temperature / elevation
    temp1 = random.randint(5, 25)
    drop = random.randint(10, 30)
    ans = temp1 - drop
    opts = [str(ans) + "°C", str(ans + 2) + "°C", str(ans - 2) + "°C", str(temp1 + drop) + "°C"]
    random.shuffle(opts)
    add_q(f"The temperature was {temp1}°C in the afternoon. By midnight, it dropped by {drop}°C. What is the temperature at midnight?", 
          opts, opts.index(str(ans) + "°C"), "Integers", "Advanced", f"Initial temperature = {temp1}. Drop = {drop}. Final = {temp1} - {drop} = {ans}°C.")

# --- Topic: Fractions ---
for _ in range(25):
    # Foundation: Simplification
    factor = random.randint(2, 12)
    num = random.randint(1, 9)
    den = random.randint(num + 1, 12) # ensure proper fraction
    ans = f"{num}/{den}"
    opts = [ans, f"{num+1}/{den}", f"{num}/{den+1}", f"{den}/{num}"]
    random.shuffle(opts)
    add_q(f"Reduce the fraction {num*factor}/{den*factor} to its simplest form.", 
          opts, opts.index(ans), "Fractions", "Foundation", f"Divide numerator and denominator by their greatest common divisor, which is {factor}. The simplest form is {ans}.")

for _ in range(25):
    # Advanced: Addition of unlike fractions
    den1 = random.choice([2, 3, 4, 5])
    den2 = random.choice([3, 4, 5, 7])
    if den1 == den2: den2 += 1
    num1 = random.randint(1, den1 - 1)
    num2 = random.randint(1, den2 - 1)
    # ans = num1/den1 + num2/den2 = (num1*den2 + num2*den1)/(den1*den2)
    ans_num = num1 * den2 + num2 * den1
    ans_den = den1 * den2
    ans = f"{ans_num}/{ans_den}"
    opts = [ans, f"{num1+num2}/{den1+den2}", f"{abs(ans_num-2)}/{ans_den}", f"{ans_num+2}/{ans_den}"]
    random.shuffle(opts)
    add_q(f"Rohan ate {num1}/{den1} of a pizza and Sneha ate {num2}/{den2} of the same pizza. How much pizza did they eat altogether? (Assuming answer is unsimplified)", 
          opts, opts.index(ans), "Fractions", "Advanced", f"LCM of {den1} and {den2} is {ans_den}. {num1}/{den1} = {num1*den2}/{ans_den} and {num2}/{den2} = {num2*den1}/{ans_den}. Sum = {ans_num}/{ans_den}.")

# --- Topic: Decimals ---
for _ in range(25):
    # Foundation: Place value to decimal
    whole = random.randint(0, 50)
    tenths = random.randint(0, 9)
    hundredths = random.randint(1, 9)
    ans = f"{whole}.{tenths}{hundredths}"
    opts = [ans, f"{whole}.{hundredths}{tenths}", f"{whole}.0{tenths}{hundredths}", f"{whole}{tenths}.{hundredths}"]
    random.shuffle(opts)
    add_q(f"Write as a decimal: {whole} + {tenths}/10 + {hundredths}/100", 
          opts, opts.index(ans), "Decimals", "Foundation", f"{tenths}/10 is {tenths} tenths and {hundredths}/100 is {hundredths} hundredths. Thus, {ans}.")

for _ in range(25):
    # Advanced: Decimal word problem
    price1 = round(random.uniform(10.0, 50.0), 2)
    price2 = round(random.uniform(5.0, 30.0), 2)
    paid = 100.00
    ans = round(paid - (price1 + price2), 2)
    opts = [f"₹{ans:.2f}", f"₹{ans+1:.2f}", f"₹{ans-1:.2f}", f"₹{ans+0.5:.2f}"]
    random.shuffle(opts)
    add_q(f"Aarav bought a book for ₹{price1:.2f} and a pen for ₹{price2:.2f}. He gave a ₹100 note to the shopkeeper. How much change will he get back?", 
          opts, opts.index(f"₹{ans:.2f}"), "Decimals", "Advanced", f"Total cost = {price1:.2f} + {price2:.2f} = {price1+price2:.2f}. Change = 100 - {price1+price2:.2f} = {ans:.2f}.")

# --- Topic: Algebra ---
for _ in range(25):
    # Foundation: Simple expressions
    var = random.choice(["x", "y", "z", "p", "q"])
    num = random.randint(2, 15)
    op = random.choice(["more than", "less than", "times"])
    if op == "more than":
        ans = f"{var} + {num}"
        opts = [ans, f"{num} - {var}", f"{var} - {num}", f"{num}{var}"]
    elif op == "less than":
        ans = f"{var} - {num}"
        opts = [ans, f"{num} - {var}", f"{var} + {num}", f"{var}/{num}"]
    else:
        ans = f"{num}{var}"
        opts = [ans, f"{var} + {num}", f"{num} / {var}", f"{var} - {num}"]
    random.shuffle(opts)
    add_q(f"Write the algebraic expression for: {num} {op} {var}", 
          opts, opts.index(ans), "Algebra", "Foundation", f"'{op}' indicates the mathematical operation. The correct expression is {ans}.")

for _ in range(25):
    # Advanced: Solving simple linear equations
    ans_val = random.randint(2, 12)
    coeff = random.randint(2, 6)
    const = random.randint(1, 20)
    rhs = coeff * ans_val + const
    opts = [str(ans_val), str(ans_val + 1), str(ans_val - 1), str(ans_val + 2)]
    random.shuffle(opts)
    add_q(f"Solve for x: {coeff}x + {const} = {rhs}", 
          opts, opts.index(str(ans_val)), "Algebra", "Advanced", f"Subtract {const} from both sides: {coeff}x = {rhs - const}. Divide by {coeff}: x = {ans_val}.")

# --- Topic: Ratio and Proportion ---
for _ in range(25):
    # Foundation: Simplifying ratios
    factor = random.randint(2, 10)
    a = random.randint(1, 7)
    b = random.randint(a + 1, 9)
    ans = f"{a}:{b}"
    opts = [ans, f"{b}:{a}", f"{a+1}:{b}", f"{a}:{b+1}"]
    random.shuffle(opts)
    add_q(f"Find the ratio of {a*factor} to {b*factor} in its simplest form.", 
          opts, opts.index(ans), "Ratio and Proportion", "Foundation", f"Divide both numbers by their HCF, which is {factor}. {a*factor} ÷ {factor} = {a}, and {b*factor} ÷ {factor} = {b}. Ratio is {ans}.")

for _ in range(25):
    # Advanced: Dividing an amount in a given ratio
    ratio1 = random.randint(2, 5)
    ratio2 = random.randint(3, 7)
    if ratio1 == ratio2: ratio2 += 1
    multiplier = random.randint(10, 50)
    total = (ratio1 + ratio2) * multiplier
    ans = ratio1 * multiplier
    opts = [f"₹{ans}", f"₹{ratio2 * multiplier}", f"₹{ans - 10}", f"₹{ans + 10}"]
    random.shuffle(opts)
    add_q(f"Divide ₹{total} between A and B in the ratio {ratio1}:{ratio2}. What is A's share?", 
          opts, opts.index(f"₹{ans}"), "Ratio and Proportion", "Advanced", f"Total parts = {ratio1} + {ratio2} = {ratio1+ratio2}. Value of one part = {total} / {ratio1+ratio2} = {multiplier}. A's share = {ratio1} × {multiplier} = {ans}.")

# Write to file
with open("math_g6_algorithmic.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"Generated {len(questions)} algorithmic questions.")
