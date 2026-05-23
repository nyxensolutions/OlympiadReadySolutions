import cloudinary
import cloudinary.uploader

CLOUDINARY_CLOUD_NAME = "dyommthef"
CLOUDINARY_API_KEY = "414698218814162"
CLOUDINARY_API_SECRET = "fIHmpWwiIllKPs2qbEeHVNzMMP4"

cloudinary.config(
  cloud_name = CLOUDINARY_CLOUD_NAME,
  api_key = CLOUDINARY_API_KEY,
  api_secret = CLOUDINARY_API_SECRET
)

image_url = "https://image.pollinations.ai/prompt/a%20cute%20cat"
try:
    print("Asking Cloudinary to fetch:", image_url)
    upload_result = cloudinary.uploader.upload(image_url, folder="olympiad_questions")
    print("Success! URL:", upload_result.get("secure_url"))
except Exception as e:
    print("Failed:", e)
