import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("GEMINI_API_KEY", "offline-placeholder-key")
client = genai.Client()
GEMINI_EXPLANATION_MODEL = "gemini-flash-lite-latest"