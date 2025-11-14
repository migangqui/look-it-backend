from app.db.mongo_config import db
from app.db.mongo_models import GarmentItem

from datetime import datetime
from bson import ObjectId

async def save(garment: GarmentItem):
    # Asignar _id y creation_date si no existen
    if not hasattr(garment, 'creation_date') or not garment.creation_date:
        garment.creation_date = datetime.now(datetime.timezone.utc)
    garment_dict = garment.model_dump(by_alias=True, exclude_none=True)
    await db["garment_items"].insert_one(garment_dict)
    return garment

async def find_by_user_id(user_id: str):
    cursor = db["garment_items"].find({"user_id": user_id})
    return [GarmentItem(**doc) async for doc in cursor]

async def list():
    cursor = db["garment_items"].find()
    return [GarmentItem(**doc) async for doc in cursor]
