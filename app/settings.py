# settings.py
# Configuration initialization and key loading

from app.core.config_service import ConfigService

config = ConfigService()

MONGO_URI = config.get("MONGO_URI")
GOOGLE_CLIENT_ID = config.get("GOOGLE_CLIENT_ID")
JWT_SECRET = config.get("JWT_SECRET")
GCS_BUCKET_NAME = "look-it-storage"
GCS_URL = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}"
OPENWEATHERMAP_API_KEY = config.get("OPENWEATHERMAP_API_KEY")
GEMINI_API_KEY = config.get("GEMINI_API_KEY")