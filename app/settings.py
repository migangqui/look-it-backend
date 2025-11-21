# settings.py
# Configuration initialization and key loading

from app.core.config_service import ConfigService

config = ConfigService()

MONGO_URI = config.get("MONGO_URI")
GOOGLE_CLIENT_ID = config.get("GOOGLE_CLIENT_ID")
JWT_SECRET = config.get("JWT_SECRET")
GCS_BUCKET_NAME = "look-it-storage"