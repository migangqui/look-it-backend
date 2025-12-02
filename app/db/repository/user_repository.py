from bson import ObjectId
from app.db.mongo_config import db
from app.db.mongo_models import User

users_collection = db["users"]

async def save(user: User):
    user_dict = user.model_dump(by_alias=True, exclude_none=True)
    
    if user.id:
        user_id = user_dict.pop("_id")  # Remover _id del dict para el update
        filter = {"_id": ObjectId(user_id)}
        result = await users_collection.update_one(filter, {"$set": user_dict})
        return user_id
    else:
        result = await users_collection.insert_one(user_dict)
        return result.inserted_id

async def find_by_email(email: str):
    doc = await users_collection.find_one({"email": email})
    return User(**doc) if doc else None

async def find_by_google_id(google_id: str):
    doc = await users_collection.find_one({"google_id": google_id})
    return User(**doc) if doc else None

async def list():
    cursor = users_collection.find()
    return [User(**doc) async for doc in cursor]
