
from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.core.auth_service import verify_google_token, get_or_create_user, create_jwt

router = APIRouter()

class LoginRequest(BaseModel):
	id_token: str

@router.post("/login")
async def login(data: LoginRequest):
	payload = await verify_google_token(data.id_token)
	google_id = payload["sub"]
	email = payload["email"]
	user = await get_or_create_user(google_id, email)
	jwt_token = create_jwt(user)
	return {"token": jwt_token}
