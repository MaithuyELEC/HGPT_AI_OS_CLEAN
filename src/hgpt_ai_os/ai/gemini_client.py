from dotenv import load_dotenv
from google import genai

load_dotenv(".env")


class GeminiAI:

    def __init__(self):
        self.client = genai.Client()

    def ask(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
        )
        return response.text
