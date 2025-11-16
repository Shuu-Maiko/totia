from google import genai
from dotenv import load_dotenv
import os 


load_dotenv()
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
API_KEY = os.getenv('GEMINI_API_KEY') or ' '
client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)

