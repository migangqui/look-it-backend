from app.db.mongo_config import db
from app.db.mongo_models import GarmentItem
from bson import ObjectId
from bson.errors import InvalidId

garment_items_collection = db["garment_items"]

async def save(garment: GarmentItem):
    garment_dict = garment.model_dump(by_alias=True, exclude_none=True)
    result = await garment_items_collection.insert_one(garment_dict)
    # Update garment with inserted ID
    garment.id = str(result.inserted_id)
    return garment

async def find_by_user_id(user_id: str):
    cursor = garment_items_collection.find({"user_id": user_id})
    return [GarmentItem(**doc) async for doc in cursor]

async def delete_by_id(garment_id: str, user_id: str) -> bool:
    """
    Delete a garment by ID, ensuring it belongs to the specified user.
    
    Args:
        garment_id: The ID of the garment to delete
        user_id: The ID of the user who owns the garment
        
    Returns:
        True if the garment was deleted, False if it was not found
        
    Raises:
        ValueError: If garment_id is not a valid ObjectId
    """
    try:
        object_id = ObjectId(garment_id)
    except InvalidId:
        raise ValueError(f"Invalid garment ID format: {garment_id}")
    
    result = await garment_items_collection.delete_one(
        {"_id": object_id, "user_id": user_id}
    )
    
    return result.deleted_count > 0
