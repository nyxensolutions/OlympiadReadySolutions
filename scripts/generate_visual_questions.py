import os
import json
import random
from PIL import Image, ImageDraw, ImageFont
import time

RUN_ID = int(time.time())

# Set up paths
web_public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "public", "question-images")
os.makedirs(web_public_dir, exist_ok=True)
json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lr_visual_g1.json")

questions = []

def generate_shape_counting(index):
    # Draw random number of shapes (3 to 9)
    img = Image.new("RGB", (300, 200), "white")
    draw = ImageDraw.Draw(img)
    
    shapes = ["circle", "square", "triangle"]
    chosen_shape = random.choice(shapes)
    count = random.randint(3, 9)
    
    positions = []
    for _ in range(count):
        x = random.randint(20, 250)
        y = random.randint(20, 150)
        size = random.randint(20, 40)
        
        # very simple collision avoidance
        overlap = False
        for px, py, ps in positions:
            if abs(x - px) < (size + ps) and abs(y - py) < (size + ps):
                overlap = True
                break
        
        if not overlap:
            positions.append((x, y, size))
            if chosen_shape == "circle":
                draw.ellipse([x, y, x+size, y+size], fill="lightblue", outline="blue")
            elif chosen_shape == "square":
                draw.rectangle([x, y, x+size, y+size], fill="lightgreen", outline="green")
            else:
                draw.polygon([(x+size/2, y), (x, y+size), (x+size, y+size)], fill="pink", outline="red")
    
    # Actual count drawn might be slightly less due to overlap check, so use len(positions)
    actual_count = len(positions)
    
    filename = f"reasoning-{RUN_ID}-{index}.png"
    img.save(os.path.join(web_public_dir, filename))
    
    # Options logic
    correct_opt = str(actual_count)
    wrongs = [str(actual_count + 1), str(actual_count - 1), str(actual_count + 2)]
    wrongs = [w for w in wrongs if int(w) > 0]
    while len(wrongs) < 3:
        wrongs.append(str(random.randint(1, 10)))
        wrongs = list(set(wrongs))
        if correct_opt in wrongs:
            wrongs.remove(correct_opt)
    
    options = [correct_opt] + wrongs[:3]
    random.shuffle(options)
    correct_idx = options.index(correct_opt)
    correct_letter = chr(65 + correct_idx)
    
    questions.append({
        "QuestionText": f"How many {chosen_shape}s are there in the image? (Q{index})",
        "ImageUrl": f"/question-images/{filename}",
        "Options": {
            "A": options[0],
            "B": options[1],
            "C": options[2],
            "D": options[3]
        },
        "CorrectAnswer": correct_letter,
        "Topic": "Patterns and Shapes",
        "SubTopic": "Counting Shapes",
        "Difficulty": "Foundation",
        "Explanation": f"There are exactly {actual_count} {chosen_shape}s visible in the image."
    })

def generate_odd_one_out(index):
    img = Image.new("RGB", (400, 150), "white")
    draw = ImageDraw.Draw(img)
    
    shapes = ["circle", "square", "triangle", "star"]
    base_shape = random.choice(["circle", "square", "triangle"])
    odd_shape = random.choice([s for s in shapes if s != base_shape])
    
    items = [base_shape, base_shape, base_shape, odd_shape]
    random.shuffle(items)
    odd_idx = items.index(odd_shape)
    
    colors = ["red", "blue", "green", "orange", "purple"]
    c = random.choice(colors)
    
    for i, shape in enumerate(items):
        x = 20 + i * 90
        y = 30
        size = 60
        
        # Label A, B, C, D
        draw.text((x + size/2 - 5, y + size + 10), chr(65+i), fill="black")
        
        if shape == "circle":
            draw.ellipse([x, y, x+size, y+size], outline=c, width=3)
        elif shape == "square":
            draw.rectangle([x, y, x+size, y+size], outline=c, width=3)
        elif shape == "triangle":
            draw.polygon([(x+size/2, y), (x, y+size), (x+size, y+size)], outline=c, width=3)
        elif shape == "star":
            # approximate star
            draw.polygon([(x+size/2, y), (x+size*0.6, y+size*0.4), (x+size, y+size*0.4), 
                          (x+size*0.7, y+size*0.6), (x+size*0.8, y+size), (x+size/2, y+size*0.8),
                          (x+size*0.2, y+size), (x+size*0.3, y+size*0.6), (x, y+size*0.4),
                          (x+size*0.4, y+size*0.4)], outline=c, width=3)

    filename = f"reasoning-{RUN_ID}-{index}.png"
    img.save(os.path.join(web_public_dir, filename))
    
    questions.append({
        "QuestionText": f"Which figure is the odd one out? (Q{index})",
        "ImageUrl": f"/question-images/{filename}",
        "Options": {
            "A": "Figure A",
            "B": "Figure B",
            "C": "Figure C",
            "D": "Figure D"
        },
        "CorrectAnswer": chr(65 + odd_idx),
        "Topic": "Patterns and Shapes",
        "SubTopic": "Odd One Out",
        "Difficulty": "Foundation",
        "Explanation": f"Figure {chr(65+odd_idx)} is a {odd_shape}, while the others are {base_shape}s."
    })

def generate_pattern(index):
    img = Image.new("RGB", (400, 150), "white")
    draw = ImageDraw.Draw(img)
    
    colors = ["red", "blue", "green"]
    c1, c2 = random.sample(colors, 2)
    
    # Pattern: c1, c2, c1, c2, ?
    seq = [c1, c2, c1, c2]
    ans_color = c1
    
    for i, col in enumerate(seq):
        x = 20 + i * 70
        y = 40
        size = 50
        draw.ellipse([x, y, x+size, y+size], fill=col)
    
    # Question mark for the last one
    x = 20 + 4 * 70
    y = 40
    size = 50
    draw.rectangle([x, y, x+size, y+size], outline="black", width=2)
    draw.text((x + size/2 - 5, y + size/2 - 5), "?", fill="black")

    filename = f"reasoning-{RUN_ID}-{index}.png"
    img.save(os.path.join(web_public_dir, filename))
    
    # Options
    wrongs = [c for c in ["red", "blue", "green", "yellow", "orange"] if c != ans_color]
    random.shuffle(wrongs)
    opts = [ans_color, wrongs[0], wrongs[1], wrongs[2]]
    random.shuffle(opts)
    
    correct_letter = chr(65 + opts.index(ans_color))
    
    questions.append({
        "QuestionText": f"Which color comes next in the pattern? (Q{index})",
        "ImageUrl": f"/question-images/{filename}",
        "Options": {
            "A": opts[0].capitalize(),
            "B": opts[1].capitalize(),
            "C": opts[2].capitalize(),
            "D": opts[3].capitalize()
        },
        "CorrectAnswer": correct_letter,
        "Topic": "Patterns and Shapes",
        "SubTopic": "Repeating Patterns",
        "Difficulty": "Advanced",
        "Explanation": f"The pattern alternates between {c1} and {c2}. The next color must be {ans_color}."
    })

print("Generating 50 visual questions...")
for i in range(1, 51):
    choice = random.choice([1, 2, 3])
    if choice == 1:
        generate_shape_counting(i)
    elif choice == 2:
        generate_odd_one_out(i)
    else:
        generate_pattern(i)

with open(json_path, 'w') as f:
    json.dump(questions, f, indent=2)

print(f"Generated {len(questions)} questions at {json_path}")
