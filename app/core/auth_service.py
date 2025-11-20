from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_jwt_token(token: str) -> dict:
	try:
		payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
		return payload
	except Exception:
		raise HTTPException(status_code=401, detail="Invalid or expired JWT token")

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
	token = credentials.credentials
	payload = verify_jwt_token(token)
	return payload

# Authentication service: Google ID Token, MongoDB and JWT
from fastapi import HTTPException
from app.db.mongo_models import User
from jose import jwt
from datetime import datetime, timedelta, timezone
import requests
import app.db.repository.user_repository as user_repository
from app.settings import GOOGLE_CLIENT_ID, JWT_SECRET

# Configuration
JWT_ALGORITHM = "HS256"
JWT_EXP_DAYS = 1

async def loginByGoogleToken(id_token: str) -> str:
	payload = await _verify_google_token(id_token)
	google_id = payload["sub"]
	email = payload["email"]
	user = await _get_or_create_user(google_id, email)
	jwt_token = _create_jwt(user)
	return jwt_token

async def _verify_google_token(id_token: str) -> dict:
	url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
	resp = requests.get(url)
	if resp.status_code != 200:
		raise HTTPException(status_code=401, detail="Invalid Google token")
	payload = resp.json()
	if payload.get("aud") != GOOGLE_CLIENT_ID:
		raise HTTPException(status_code=401, detail="Google token not valid for this client")
	return payload

async def _get_or_create_user(google_id: str, email: str) -> User:
	user = await user_repository.find_by_google_id(google_id)
	if user:
		user.last_login_date = datetime.now(timezone.utc)
		await user_repository.save(user)
		return user
	new_user = User(
		google_id=google_id,
		email=email,
		creation_date=datetime.now(timezone.utc),
		last_login_date=datetime.now(timezone.utc)
	)
	inserted_id = await user_repository.save(new_user)
	new_user.id = inserted_id
	return new_user

def _create_jwt(user: User) -> str:
	payload = {
		"sub": user.id,
		"google_id": user.google_id,
		"email": user.email,
		"exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXP_DAYS)
	}
	token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
	return token
