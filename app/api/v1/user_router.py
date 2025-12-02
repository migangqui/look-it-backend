from fastapi import APIRouter, Depends
from app.core.auth_service import get_current_user
from app.db.mongo_models import User
from app.db.repository.user_repository import find_by_email

router = APIRouter()

@router.get("/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    user = await find_by_email(current_user.get("email"))
    return user