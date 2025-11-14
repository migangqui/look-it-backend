from fastapi import APIRouter, Body
from datetime import datetime, timezone
from app.settings import PRUEBA_SECRETO
from app.db.mongo_models import User
from app.db.repository.user_repository import find_by_email, save, list as list_users

router = APIRouter()

# Endpoint para devolver el secreto PRUEBA_SECRETO
@router.get("/prueba-secreto")
async def get_prueba_secreto():
    return {"prueba_secreto": PRUEBA_SECRETO}

# Endpoint para listar todos los usuarios
@router.get("/users")
async def get_users():
    users = await list_users()
    return [user.dict() for user in users]

@router.get("/users/{email}")
async def get_user_endpoint(email: str):
    user = await find_by_email(email)
    if user:
        return user
    return {"error": "Usuario no encontrado"}

@router.post("/users")
async def crear_usuario_prueba(
    email: str = Body(...),
    google_id: str = Body(...)
):
    user = await find_by_email(email)
    if user:
        return {"error": "El usuario ya existe"}
    nuevo_usuario = User(
        google_id=google_id,
        email=email,
        creation_date=datetime.now(timezone.utc)
    )
    result = await save(nuevo_usuario)
    return {"id": str(result)}