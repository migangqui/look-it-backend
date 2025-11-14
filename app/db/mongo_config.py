# Configuración de la base de datos MongoDB
from motor.motor_asyncio import AsyncIOMotorClient
from app.settings import MONGO_URI

# Conexión a MongoDB
client = AsyncIOMotorClient(MONGO_URI)
db = client["look-it-db"]