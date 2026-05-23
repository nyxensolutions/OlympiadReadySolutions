import json
import os
import requests
import cloudinary
import cloudinary.uploader
import urllib.parse
from time import sleep

# --- CONFIGURATION ---
GROQ_API_KEY = "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"

CLOUDINARY_CLOUD_NAME = "dyommthef"
CLOUDINARY_API_KEY = "414698218814162"
CLOUDINARY_API_SECRET = "fIHmpWwiIllKPs2qbEeHVNzMMP4"

cloudinary.config(
  cloud_name = CLOUDINARY_CLOUD_NAME,
  api_key = CLOUDINARY_API_KEY,
  api_secret = CLOUDINARY_API_SECRET
)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
POLLINATIONS_IMAGE_URL = "https://image.pollinations.ai/prompt/"

GRADES = [1, 2, 3, 4, 6, 7, 8, 9, 10]
SUBJECTS = ["Logical Reasoning", "Mathematics", "Science", "General Knowledge"]
QUESTIONS_PER_BATCH = 50

# --- SCRIPT ---
def generate_questions(subject, grade, count):
    print(f"[{subject} | G{grade}] Generating {count} questions via AI...")
    
    prompt = f"""
You are an expert Olympiad question creator. Create {count} multiple-choice questions for Grade {grade} students in the subject of {subject}.
CRITICAL REQUIREMENT: Every single question MUST be an image-based question. 
For each question, provide an `ImagePrompt` which is a highly detailed, descriptive prompt that an AI image generator (like DALL-E or Midjourney) can use to create the image required for the question. Do not include text inside the image prompt if possible, describe the visual scenario instead.

Format the output strictly as a JSON object containing a single key "questions" which maps to an array of objects with the following structure. DO NOT wrap it in markdown block quotes. Return only raw JSON.
{{
  "questions": [
    {{
      "QuestionText": "What does this image represent?",
      "Options": ["Option A", "Option B", "Option C", "Option D"],
      "CorrectAnswer": "A",
      "Topic": "Specific topic name",
      "Difficulty": "Foundation or Advanced",
      "Explanation": "Explanation of the correct answer.",
      "ImagePrompt": "A highly detailed illustration of a..."
    }}
  ]
}}
"""
    try:
        response = requests.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "response_format": {"type": "json_object"}
            }
        )
        response.raise_for_status()
        
        resp_json = response.json()
        raw_text = resp_json["choices"][0]["message"]["content"].strip()
        
        # Groq might wrap the output in a JSON object if we force JSON mode, so we handle it
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict) and len(parsed.keys()) == 1:
                # If it wrapped it like {"questions": [...]}, extract the array
                first_key = list(parsed.keys())[0]
                if isinstance(parsed[first_key], list):
                    return parsed[first_key]
            return parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            pass # Fall back to normal parsing below
            
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        questions = json.loads(raw_text)
        return questions
    except Exception as e:
        print(f"[{subject} | G{grade}] Failed to generate text: {e}")
        return []

def generate_and_upload_image(image_prompt, question_index):
    encoded_prompt = urllib.parse.quote(image_prompt)
    image_url = f"{POLLINATIONS_IMAGE_URL}{encoded_prompt}?width=800&height=600&nologo=true"
    
    os.makedirs("temp_images", exist_ok=True)
    temp_file = f"temp_images/temp_{question_index}.jpg"
    
    # Try downloading the image up to 3 times to handle Pollinations timeouts
    for attempt in range(3):
        try:
            print(f"      [{question_index}] Fetching image... (Attempt {attempt+1}/3)")
            response = requests.get(image_url, timeout=120)
            response.raise_for_status()
            
            with open(temp_file, "wb") as f:
                f.write(response.content)
            
            # Now upload the local file to Cloudinary
            upload_result = cloudinary.uploader.upload(temp_file, folder="olympiad_questions")
            
            # Clean up
            os.remove(temp_file)
            
            return upload_result.get("secure_url")
        except Exception as e:
            print(f"      -> Attempt {attempt+1} failed: {e}")
            sleep(3)
            
    print(f"      -> Failed completely to generate/upload image for question {question_index}.")
    return None

def process_batch(subject, grade, count):
    questions = generate_questions(subject, grade, count)
    if not questions:
        print(f"[{subject} | G{grade}] Skipping due to generation failure.")
        return
        
    final_questions = []
    
    for i, q in enumerate(questions):
        image_prompt = q.get("ImagePrompt")
        if image_prompt:
            cloud_url = generate_and_upload_image(image_prompt, i + 1)
            q["ImageUrl"] = cloud_url
            
            # Match your API's Question.cs mapping where Q = QuestionText
            q["Q"] = q.pop("QuestionText", "")
            q["Answer"] = q.pop("CorrectAnswer", "")
            
            if "ImagePrompt" in q:
                del q["ImagePrompt"] 
                
        final_questions.append(q)
        sleep(5) # Prevent hammering the Pollinations API
        
    safe_subject = subject.lower().replace(' ', '_')
    output_filename = f"{safe_subject}_g{grade}.json"
    
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", output_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_questions, f, indent=2, ensure_ascii=False)
        
    print(f"[{subject} | G{grade}] Saved {len(final_questions)} questions to {output_path}")

if __name__ == "__main__":
    print("Starting Olympiad Image-Based Question Generator pipeline...")
    print(f"Target: {len(GRADES)} grades, {len(SUBJECTS)} subjects, {QUESTIONS_PER_BATCH} questions each.")
    print("--------------------------------------------------")
    
    for grade in GRADES:
        for subject in SUBJECTS:
            process_batch(subject, grade, QUESTIONS_PER_BATCH)
            print("Sleeping for 10 seconds before next batch to respect rate limits...")
            sleep(10)
    
    print("\nPipeline Complete! All JSON files are in the 'output' folder.")
