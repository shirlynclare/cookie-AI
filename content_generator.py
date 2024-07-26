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
        
        try:
            response = self.model.generate_content(full_prompt)
            
            if response.prompt_feedback.block_reason:
                return f"Content generation was blocked due to: {response.prompt_feedback.block_reason}"
            
            if not response.candidates:
                return "No content was generated. This might be due to safety constraints."
            
            if response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            else:
                return "Generated content was empty. This might be due to safety constraints."
        
        except Exception as e:
            return f"An error occurred during content generation: {str(e)}"
