import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

class ContentModerator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    def moderate_content(self, content):
        prompt = f"Analyze the following content and determine if it violates community guidelines. Respond with 'APPROVED' if it's acceptable or 'REJECTED' if it violates guidelines. Provide a brief explanation for your decision.\n\nContent: {content}"
        response = self.model.generate_content(prompt)
        return response.text