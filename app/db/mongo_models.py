from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from enum import Enum

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

class RoleEnum(str, Enum):
    BASE_TOP = "base_top"
    MID_TOP = "mid_top"
    OUTWEAR_TOP = "outwear_top"
    FOOTWEAR = "footwear"
    BOTTOM = "bottom"
    FULL_BODY = "full_body"
    OTHER = "other"


class OccasionEnum(str, Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    ALL = "all"


class GarmentItem(BaseModel):
	id: Optional[str] = Field(None, alias="_id")
	user_id: str
	image_name: str
	type: str
	role: RoleEnum
	color: Optional[str] = None
	occasion: Optional[OccasionEnum] = None
	warmth: Optional[int] = Field(default=None, ge=1, le=5)
	pattern: Optional[str] = None
	pattern_intensity: Optional[int] = Field(default=None, ge=1, le=3)
	creation_date: datetime

	@field_validator('id', mode='before')
	def validate_id(cls, v):
		return _objectid_to_str(cls, v)
    
