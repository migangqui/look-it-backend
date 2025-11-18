from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_jwt_token(token: str) -> dict:
	try:
		payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
		return payload
	except Exception:
		raise HTTPException(status_code=401, detail="Token JWT inválido o expirado")

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
	token = credentials.credentials
	payload = verify_jwt_token(token)
	return payload

# Servicio de autenticación: Google ID Token, MongoDB y JWT
from fastapi import HTTPException
from app.db.mongo_models import User
from jose import jwt
from datetime import datetime, timedelta, timezone
import requests
import app.db.repository.user_repository as user_repository
from app.settings import GOOGLE_CLIENT_ID, JWT_SECRET

# Configuración
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 60

async def verify_google_token(id_token: str) -> dict:
	"""Valida el token ID de Google y retorna el payload."""
	url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
	resp = requests.get(url)
	if resp.status_code != 200:
		raise HTTPException(status_code=401, detail="Token de Google inválido")
	payload = resp.json()
	print(payload.get("aud"))
	print(GOOGLE_CLIENT_ID)
	if payload.get("aud") != GOOGLE_CLIENT_ID:
		raise HTTPException(status_code=401, detail="Token de Google no válido para este cliente")
	return payload

async def get_or_create_user(google_id: str, email: str) -> User:
	"""Busca o crea el usuario en MongoDB."""
	user = await user_repository.find_by_google_id(google_id)
	print(user)
	if user:
		return user
	new_user = User(
		google_id=google_id,
		email=email,
		creation_date=datetime.now(timezone.utc)
	)
	inserted_id = await user_repository.save(new_user)
	new_user.id = inserted_id
	return new_user

def create_jwt(user: User) -> str:
	"""Genera un JWT propio para el usuario autenticado."""
	payload = {
		"sub": user.id,
		"google_id": user.google_id,
		"email": user.email,
		"exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_MINUTES)
	}
	token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
	return token
