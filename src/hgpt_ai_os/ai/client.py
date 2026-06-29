from openai import OpenAI


class LucidAI:

    def __init__(self):
        self.client = OpenAI()

    def ask(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="gpt-5.5",
            input=prompt,
        )
        return response.output_text
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LucidAI:

    def __init__(self):
        self.client = OpenAI()

    def ask(self, prompt: str) -> str:
        response = self.client.responses.create(
            model="gpt-5.5",
            input=prompt,
        )
        return response.output_text
