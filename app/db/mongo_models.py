from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# Validador reutilizable para ObjectId
def objectid_to_str(cls, v):
	try:
		from bson import ObjectId
	except ImportError:
		ObjectId = None
	if ObjectId and isinstance(v, ObjectId):
		return str(v)
	return v

# Modelo para la colección 'users'
class User(BaseModel):
	id: Optional[str] = Field(None, alias="_id")  # ObjectId como string, opcional
	google_id: str
	email: str
	creation_date: datetime

	@field_validator('id', mode='before')
	def validate_id(cls, v):
		return objectid_to_str(cls, v)

class GarmentItem(BaseModel):
	id: Optional[str] = Field(None, alias="_id")
	user_id: str
	storage_url: str
	type: str
	role: str  # Ej: Superior Primario, Capa, Inferior
	color: Optional[str] = None
	occasion: Optional[str] = None
	creation_date: datetime

	@field_validator('id', mode='before')
	def validate_id(cls, v):
		return objectid_to_str(cls, v)
    
