from app.db.mongo_config import db
from app.db.mongo_models import User

users_collection = db["users"]

async def save(user: User):
    user_dict = user.model_dump(by_alias=True, exclude_none=True)
    result = await users_collection.insert_one(user_dict)
    return result.inserted_id

async def find_by_email(email: str):
    doc = await users_collection.find_one({"email": email})
    return User(**doc) if doc else None

async def list():
    cursor = users_collection.find()
    return [User(**doc) async for doc in cursor]
