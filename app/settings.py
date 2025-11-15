# settings.py
# Inicialización de configuración y carga de claves

from app.core.config_service import ConfigService

config = ConfigService()

MONGO_URI = config.get("MONGO_URI")
AZURE_CV_KEY = config.get("AZURE_COMPUTER_VISION_KEY")