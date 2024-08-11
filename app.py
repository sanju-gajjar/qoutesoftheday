from flask import Flask, send_from_directory
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip
import numpy as np
import random
import os

app = Flask(__name__)

# Directory to save the video
VIDEO_DIR = os.path.join(os.getcwd(), 'videos')
os.makedirs(VIDEO_DIR, exist_ok=True)

# 1. Create a gradient background
def create_gradient_background(width, height, color1, color2):
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    
    gradient = []
    for y in range(height):
        gradient.append(int(255 * (y / height)))
    
    for y in range(height):
        for x in range(width):
            mask.putpixel((x, y), gradient[y])
    
    base.paste(top, (0, 0), mask)
    return base

# 2. Get a random quote
def get_random_quote():
    quotes = [
        "Success is not final, failure is not fatal: It is the courage to continue that counts.",
        "The only way to do great work is to love what you do.",
        "Believe you can and you're halfway there."
    ]
    return random.choice(quotes)

# 3. Create image with gradient background and quote text
def create_image_with_text(image, text):
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 70)  # Provide the path to a TTF file if needed
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font if specific font is not available
    
    # Define the position to place the text
    width, height = image.size
    text_position = (width // 10, height // 3)
    
    # Add the text to the image
    draw.text(text_position, text, font=font, fill="white")
    return image

# 4. Animate text and create a video
def create_video(image, text):
    img_clip = ImageClip(np.array(image)).set_duration(15)
    txt_clip = TextClip(text, fontsize=70, color='white', font='Arial-Bold')
    txt_clip = txt_clip.set_position('center').set_duration(15).fadein(1, (255,255,255))

    video_path = os.path.join(VIDEO_DIR, "daily_quote.mp4")
    video = CompositeVideoClip([img_clip, txt_clip])
    video.write_videofile(video_path, fps=24)

@app.route('/')
def index():
    # Generate video if not already created
    video_path = os.path.join(VIDEO_DIR, "daily_quote.mp4")
    if not os.path.exists(video_path):
        # Define the image size and colors for the gradient
        width, height = 1080, 1920
        color1 = (255, 153, 102)  # Example: soft orange
        color2 = (255, 94, 98)    # Example: soft pink
        
        # Create gradient background
        image = create_gradient_background(width, height, color1, color2)
        
        # Get a random quote
        quote = get_random_quote()
        
        # Add the quote to the image
        image_with_text = create_image_with_text(image, quote)
        
        # Create a video with the image and text
        create_video(image_with_text, quote)

    return '''
    <!doctype html>
    <title>Download Video</title>
    <h1>Your video is ready to download!</h1>
    <a href="/download" download>Click here to download your video</a>
    '''

@app.route('/download')
def download_file():
    video_path = os.path.join(VIDEO_DIR, "daily_quote.mp4")
    return send_from_directory(directory=VIDEO_DIR, path="daily_quote.mp4", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
