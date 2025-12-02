# MongoDB database configuration
from motor.motor_asyncio import AsyncIOMotorClient
from app.settings import MONGO_URI

# MongoDB connection
client = AsyncIOMotorClient(MONGO_URI)
db = client["look-it-db"]