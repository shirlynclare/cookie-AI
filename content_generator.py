import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

class ContentGenerator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_content(self, prompt, content_type):
        full_prompt = f"Generate a {content_type} about {prompt} that is engaging, relevant, and adheres to community guidelines. The content should be coherent and contextually appropriate."
        response = self.model.generate_content(full_prompt)
        return response.text