from google.cloud import storage
from fastapi import HTTPException
from google import genai
from app.settings import GEMINI_API_KEY

google_storage_client = storage.Client()
genai_client = genai.Client(api_key=GEMINI_API_KEY)