import json
import os
import requests
import cloudinary
import cloudinary.uploader
import urllib.parse
from time import sleep

# Configuration
CLOUDINARY_CLOUD_NAME = "dyommthef"
CLOUDINARY_API_KEY = "414698218814162"
CLOUDINARY_API_SECRET = "fIHmpWwiIllKPs2qbEeHVNzMMP4"

cloudinary.config(
  cloud_name = CLOUDINARY_CLOUD_NAME,
  api_key = CLOUDINARY_API_KEY,
  api_secret = CLOUDINARY_API_SECRET
)

POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/"
POLLINATIONS_IMAGE_URL = "https://image.pollinations.ai/prompt/"

def generate_questions(subject, grade, count):
    print(f"Generating {count} questions for {subject} Grade {grade}...")
    
    prompt = f"""
You are an expert Olympiad question creator. Create {count} multiple-choice questions for Grade {grade} students in the subject of {subject}.
CRITICAL REQUIREMENT: Every single question MUST be an image-based question. 
For each question, provide an `ImagePrompt` which is a highly detailed, descriptive prompt that an AI image generator (like DALL-E or Midjourney) can use to create the image required for the question. Do not include text inside the image prompt if possible, describe the visual scenario instead.

Format the output strictly as a JSON array of objects with the following structure. DO NOT wrap it in markdown block quotes. Return only raw JSON.
[
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
"""
    
    try:
        response = requests.post(
            POLLINATIONS_TEXT_URL,
            json={"messages": [{"role": "user", "content": prompt}], "model": "mistral"},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        raw_text = response.text.strip()
        
        # Clean up if the model wrapped it in markdown
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        questions = json.loads(raw_text)
        return questions
    except Exception as e:
        print(f"Failed to generate questions: {e}")
        return []

def generate_and_upload_image(image_prompt, question_index):
    print(f"  [{question_index}] Generating image...")
    encoded_prompt = urllib.parse.quote(image_prompt)
    image_url = f"{POLLINATIONS_IMAGE_URL}{encoded_prompt}?width=800&height=600&nologo=true"
    
    try:
        # We can upload directly to cloudinary using the URL
        print(f"  [{question_index}] Uploading to Cloudinary...")
        upload_result = cloudinary.uploader.upload(image_url, folder="olympiad_questions")
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"  [{question_index}] Failed to upload image: {e}")
        return None

def process_batch(subject, grade, count=5):
    questions = generate_questions(subject, grade, count)
    if not questions:
        print("No questions generated.")
        return
        
    final_questions = []
    
    for i, q in enumerate(questions):
        image_prompt = q.get("ImagePrompt")
        if image_prompt:
            cloud_url = generate_and_upload_image(image_prompt, i + 1)
            q["ImageUrl"] = cloud_url
            del q["ImagePrompt"] # Remove prompt before saving
        final_questions.append(q)
        sleep(1) # Rate limiting
        
    output_filename = f"{subject.lower().replace(' ', '_')}_g{grade}_ai_batch.json"
    
    # ensure output directory exists
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", output_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_questions, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccessfully saved {len(final_questions)} questions to {output_path}")

if __name__ == "__main__":
    # Dry run test: 5 questions for General Knowledge Grade 4
    process_batch("General Knowledge", 4, 5)
