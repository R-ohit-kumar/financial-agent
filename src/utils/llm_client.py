import os
from groq import Groq
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set.")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"  # Free + fast

    def complete(self, messages: list[dict]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
