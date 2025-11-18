from google import genai
from google.genai import types
from .config import settings
from . import prompts

_client = genai.Client(api_key=settings.GEMINI_API_KEY)
config = types.GenerateContentConfig(
    system_instruction=prompts.SYSTEM_PROMPT_2,
    max_output_tokens=500,
)

def get_gemini_chat():
    chat = _client.chats.create(
        model="gemini-2.5-flash",
        config=config
    )
    return chat
