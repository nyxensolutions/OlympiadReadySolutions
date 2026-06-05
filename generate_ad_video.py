import os
import glob
import sys

try:
    from moviepy import ImageClip, concatenate_videoclips, vfx
except ImportError:
    print("MoviePy is not installed. Please run: pip install moviepy")
    sys.exit(1)

def create_ad_video(image_folder, output_path, duration_per_image=3):
    # Find all PNG and JPG images in the folder
    image_files = sorted(
        glob.glob(os.path.join(image_folder, "*.png")) + 
        glob.glob(os.path.join(image_folder, "*.jpg")) +
        glob.glob(os.path.join(image_folder, "*.jpeg"))
    )
    
    if not image_files:
        print(f"No images found in '{image_folder}'.")
        print("Please save the images you provided into this folder and try again.")
        return

    print(f"Found {len(image_files)} images. Generating video...")

    clips = []
    for img_path in image_files:
        # Create a clip for each image, set duration
        clip = ImageClip(img_path).with_duration(duration_per_image)
        
        # Add a fade-in transition
        clip = clip.with_effects([vfx.CrossFadeIn(0.5)])
        clips.append(clip)

    # Concatenate clips
    video = concatenate_videoclips(clips, method="compose")
    
    # Write to an MP4 file
    print(f"Writing video to {output_path}...")
    video.write_videofile(output_path, fps=24, codec="libx264", audio=False)
    print("Done! Video created successfully.")

if __name__ == "__main__":
    folder = "ad_images"
    output = "olympiad_ready_ad.mp4"
    
    # Ensure the folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"I created a new folder named '{folder}'.")
        print("Please save your 5 images into this folder (e.g., as 1.png, 2.png...) and run this script again.")
    else:
        create_ad_video(folder, output)
