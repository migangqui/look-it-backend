
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.auth_service import loginByGoogleToken

router = APIRouter()

class LoginRequest(BaseModel):
	id_token: str

@router.post("/login")
async def login(data: LoginRequest):
	jwt_token = await loginByGoogleToken(data.id_token)
	return {"token": jwt_token}
