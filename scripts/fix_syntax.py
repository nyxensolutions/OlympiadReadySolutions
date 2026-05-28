import re, ast

with open(r'D:\Nyxen\OlympiadReady\OlympiadReadySolutions\scripts\topup_spellbee_and_thin.py', encoding='utf-8') as f:
    src = f.read()

# Fix pattern like "C": "biologee" -> "C: biologee"
fixed = re.sub(r'"([A-D])": "([^"]*)"', lambda m: f'"{m.group(1)}: {m.group(2)}"', src)

with open(r'D:\Nyxen\OlympiadReady\OlympiadReadySolutions\scripts\topup_spellbee_and_thin.py', 'w', encoding='utf-8') as f:
    f.write(fixed)

try:
    ast.parse(fixed)
    print('Syntax OK')
except SyntaxError as e:
    print(f'Still error at line {e.lineno}: {e.msg}')
    lines = fixed.splitlines()
    for i in range(max(0, e.lineno-3), min(len(lines), e.lineno+2)):
        print(f'{i+1}: {lines[i]}')
