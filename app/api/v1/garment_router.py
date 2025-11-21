from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.auth_service import get_current_user
from app.core.garment_service import upload_garment, update_garment
from app.db.repository.garmentitem_repository import find_by_user_id, delete_by_id

router = APIRouter()


class GarmentUpdate(BaseModel):
    type: Optional[str] = None
    role: Optional[str] = None
    color: Optional[str] = None
    occasion: Optional[str] = None


@router.post("")
async def upload_garment_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await file.read()
    
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid JWT token: missing user_id")
    
    garment = await upload_garment(
        user_id=user_id,
        image_bytes=image_bytes,
        filename=file.filename or "image"
    )
    
    return garment.model_dump()


@router.get("")
async def list_garments(
    current_user: dict = Depends(get_current_user)
):
    """
    List all garments belonging to the authenticated user.
    
    Requires authentication. Returns a list of all garments uploaded by the user.
    """
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid JWT token: missing user_id")
    
    garments = await find_by_user_id(user_id)
    
    return [garment.model_dump() for garment in garments]


@router.delete("/{garment_id}")
async def delete_garment(
    garment_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid JWT token: missing user_id")
    
    try:
        deleted = await delete_by_id(garment_id, user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Garment with ID {garment_id} not found or does not belong to the user"
            )
        
        return {"message": "Garment deleted successfully", "garment_id": garment_id}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting garment: {str(e)}")


@router.patch("/{garment_id}")
async def update_garment_endpoint(
    garment_id: str,
    update_data: GarmentUpdate,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid JWT token: missing user_id")
    
    update_dict = update_data.model_dump(exclude_none=True)
    
    updated_garment = await update_garment(
        garment_id=garment_id,
        user_id=user_id,
        update_data=update_dict
    )
    
    return updated_garment.model_dump()
