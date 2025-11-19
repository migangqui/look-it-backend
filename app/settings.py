# settings.py
# Configuration initialization and key loading

from app.core.config_service import ConfigService
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

config = ConfigService()

MONGO_URI = config.get("MONGO_URI")
AZURE_CV_KEY = config.get("AZURE_COMPUTER_VISION_KEY")
AZURE_CV_ENDPOINT = "https://style-app.cognitiveservices.azure.com/"
GOOGLE_CLIENT_ID = config.get("GOOGLE_CLIENT_ID")
JWT_SECRET = config.get("JWT_SECRET")

# Initialize Azure Computer Vision client (singleton)
azure_cv_client = None
if AZURE_CV_KEY and AZURE_CV_ENDPOINT:
    credentials = CognitiveServicesCredentials(AZURE_CV_KEY)
    azure_cv_client = ComputerVisionClient(AZURE_CV_ENDPOINT, credentials)