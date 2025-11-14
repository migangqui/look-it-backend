from app.db.mongo_config import db
from app.db.mongo_models import GarmentItem

garment_items_collection = db["garment_items"]

async def save(garment: GarmentItem):
    garment_dict = garment.model_dump(by_alias=True, exclude_none=True)
    await garment_items_collection.insert_one(garment_dict)
    return garment

async def find_by_user_id(user_id: str):
    cursor = garment_items_collection.find({"user_id": user_id})
    return [GarmentItem(**doc) async for doc in cursor]
