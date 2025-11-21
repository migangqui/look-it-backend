from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# Reusable validator for ObjectId
def _objectid_to_str(cls, v):
	try:
		from bson import ObjectId
	except ImportError:
		ObjectId = None
	if ObjectId and isinstance(v, ObjectId):
		return str(v)
	return v

# Model for the 'users' collection
class User(BaseModel):
	id: Optional[str] = Field(None, alias="_id")  # ObjectId as string, optional
	google_id: str
	email: str
	creation_date: datetime
	last_login_date: Optional[datetime] = None

	@field_validator('id', mode='before')
	def validate_id(cls, v):
		return _objectid_to_str(cls, v)

class GarmentItem(BaseModel):
	id: Optional[str] = Field(None, alias="_id")
	user_id: str
	image_name: str
	type: str
	role: str  # E.g: Superior Primario, Capa, Inferior
	color: Optional[str] = None
	occasion: Optional[str] = None
	creation_date: datetime

	@field_validator('id', mode='before')
	def validate_id(cls, v):
		return _objectid_to_str(cls, v)
    
