# config_service.py
# Lógica de inicialización y conexión a Google Secret Manager (GSM)

from google.cloud import secretmanager
import os

class ConfigService:
	def __init__(self):
		self.secrets = {}
		self._load_secrets()

	def _load_secrets(self):
		# Ejemplo: cargar secretos desde Google Secret Manager
		client = secretmanager.SecretManagerServiceClient()
		# Aquí deberías definir los nombres de los secretos a recuperar
		secret_names = ["MONGO_URI", "AZURE_COMPUTER_VISION_KEY", "PRUEBA_SECRETO", "GOOGLE_CLIENT_ID", "JWT_SECRET"]
		project_id = "look-it-478017"
		for secret_name in secret_names:
			name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
			response = client.access_secret_version(request={"name": name})
			self.secrets[secret_name] = response.payload.data.decode("UTF-8")

	def get(self, key):
		return self.secrets.get(key)
