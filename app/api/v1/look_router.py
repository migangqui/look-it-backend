from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.auth_service import get_current_user
from app.core.look_generator import generate_outfits
from app.db.mongo_models import OccasionEnum


router = APIRouter()


class LookRequest(BaseModel):
    occasion: OccasionEnum
    city: str
    country_code: str
    temperature: Optional[float] = None
    date: Optional[date] = None
    cold_sensitivity: float = Field(0, ge=-1, le=1)
    n_results: int = Field(1, ge=1, le=20)


@router.post("")
async def generate_looks(
    body: LookRequest,
    current_user: dict = Depends(get_current_user),
) -> List[list[dict]]:
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid JWT token: missing user_id",
        )

    outfits = await generate_outfits(
        user_id=user_id,
        occasion=body.occasion,
        city=body.city,
        country_code=body.country_code,
        temperature=body.temperature,
        target_date=body.date,
        cold_sensitivity=body.cold_sensitivity,
        n_results=body.n_results,
    )

    return [
        [garment.model_dump() for garment in outfit]
        for outfit in outfits
    ]
