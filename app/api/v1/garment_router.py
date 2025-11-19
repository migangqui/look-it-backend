from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.auth_service import get_current_user
from app.core.garment_service import upload_garment
from app.db.repository.garmentitem_repository import find_by_user_id, delete_by_id

router = APIRouter()


@router.post("")
async def upload_garment_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a garment image for processing and storage.
    
    Requires authentication. The image will be processed to remove background,
    classified using Azure Computer Vision, and stored in Google Cloud Storage.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content
    image_bytes = await file.read()
    
    # Get user_id from JWT token
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid JWT token: missing user_id")
    
    # Process and save garment
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
    # Get user_id from JWT token
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid JWT token: missing user_id")
    
    # Get garments from repository
    garments = await find_by_user_id(user_id)
    
    return [garment.model_dump() for garment in garments]


@router.delete("/{garment_id}")
async def delete_garment(
    garment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a garment by ID.
    
    Requires authentication. Only allows deletion of garments belonging to the authenticated user.
    """
    # Get user_id from JWT token
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid JWT token: missing user_id")
    
    try:
        # Delete garment (validates ownership)
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
