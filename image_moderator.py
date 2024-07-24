import google.generativeai as genai
from PIL import Image
import io
import base64
from dotenv import load_dotenv
import os

load_dotenv()

class ImageModerator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def moderate_image(self, image):
        prompt = "Analyze this image and determine if it violates community guidelines. Consider aspects like explicit content, violence, hate symbols, etc. Respond with 'APPROVED' if it's acceptable or 'REJECTED' if it violates guidelines. Provide a brief explanation for your decision."
        
        # Convert the image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Encode the image bytes to base64
        img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')

        # Create the image part
        image_part = {
            "mime_type": "image/png",
            "data": img_base64
        }

        # Generate content
        response = self.model.generate_content([prompt, image_part])
        return response.text