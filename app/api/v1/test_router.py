from fastapi import APIRouter, Body
from datetime import datetime, timezone
from app.db.mongo_models import User
from app.db.repository.user_repository import find_by_email, save, list as list_users

router = APIRouter()

# Endpoint to list all users
@router.get("/users")
async def get_users():
    users = await list_users()
    return [user.model_dump() for user in users]

@router.get("/users/{email}")
async def get_user_endpoint(email: str):
    user = await find_by_email(email)
    if user:
        return user
    return {"error": "User not found"}

@router.post("/users")
async def create_test_user(
    email: str = Body(...),
    google_id: str = Body(...)
):
    user = await find_by_email(email)
    if user:
        return {"error": "User already exists"}
    new_user = User(
        google_id=google_id,
        email=email,
        creation_date=datetime.now(timezone.utc)
    )
    result = await save(new_user)
    return {"id": str(result)}