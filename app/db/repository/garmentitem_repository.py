from app.db.mongo_config import db
from app.db.mongo_models import GarmentItem
from bson import ObjectId
from bson.errors import InvalidId
from typing import Optional

garment_items_collection = db["garment_items"]

async def save(garment: GarmentItem):
    garment_dict = garment.model_dump(by_alias=True, exclude_none=True)
    result = await garment_items_collection.insert_one(garment_dict)
    garment.id = str(result.inserted_id)
    return garment

async def find_by_user_id(user_id: str):
    cursor = garment_items_collection.find({"user_id": user_id})
    return [GarmentItem(**doc) async for doc in cursor]

async def find_by_id(garment_id: str, user_id: str) -> Optional[GarmentItem]:
    try:
        object_id = ObjectId(garment_id)
    except InvalidId:
        raise ValueError(f"Invalid garment ID format: {garment_id}")
    
    result = await garment_items_collection.find_one(
        {"_id": object_id, "user_id": user_id}
    )
    
    if result:
        return GarmentItem(**result)
    return None

async def delete_by_id(garment_id: str, user_id: str) -> bool:
    try:
        object_id = ObjectId(garment_id)
    except InvalidId:
        raise ValueError(f"Invalid garment ID format: {garment_id}")
    
    result = await garment_items_collection.delete_one(
        {"_id": object_id, "user_id": user_id}
    )
    
    return result.deleted_count > 0


async def update_by_id(garment_id: str, user_id: str, update_data: dict) -> Optional[GarmentItem]:
    try:
        object_id = ObjectId(garment_id)
    except InvalidId:
        raise ValueError(f"Invalid garment ID format: {garment_id}")
    
    allowed_fields = {
        "type",
        "role",
        "color",
        "occasion",
        "warmth",
        "pattern",
        "pattern_intensity",
    }
    filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields and v is not None}
    
    if not filtered_data:
        raise ValueError("No valid fields to update")
    
    result = await garment_items_collection.find_one_and_update(
        {"_id": object_id, "user_id": user_id},
        {"$set": filtered_data},
        return_document=True
    )
    
    if result:
        return GarmentItem(**result)
    return None
