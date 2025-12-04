# config_service.py
# Initialization logic and connection to Google Secret Manager (GSM)

from google.cloud import secretmanager
import os

class ConfigService:
	def __init__(self):
		self.secrets = {}
		self._load_secrets()

	def _load_secrets(self):
		# Example: load secrets from Google Secret Manager
		client = secretmanager.SecretManagerServiceClient()
		# Here you should define the names of the secrets to retrieve
		secret_names = ["MONGO_URI", "PRUEBA_SECRETO", "GOOGLE_CLIENT_ID", "JWT_SECRET", "OPENWEATHERMAP_API_KEY"]
		project_id = "look-it-478017"
		for secret_name in secret_names:
			name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
			response = client.access_secret_version(request={"name": name})
			self.secrets[secret_name] = response.payload.data.decode("UTF-8")

	def get(self, key):
		return self.secrets.get(key)
