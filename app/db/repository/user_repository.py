from app.db.mongo_config import db
from app.db.mongo_models import User

from datetime import datetime
from bson import ObjectId

async def save(user: User):
    user_dict = user.model_dump(by_alias=True, exclude_none=True)
    result = await db["User"].insert_one(user_dict)
    return result.inserted_id

async def find_by_email(email: str):
    doc = await db["User"].find_one({"email": email})
    return User(**doc) if doc else None

async def list():
    cursor = db["User"].find()
    return [User(**doc) async for doc in cursor]
