from fastapi import HTTPException
from google.cloud import storage
from google.cloud.exceptions import NotFound
from datetime import datetime, timezone
from app.core.image_processor import process_image
from app.db.mongo_models import GarmentItem
from app.db.repository.garmentitem_repository import save, update_by_id, delete_by_id, find_by_id
from app.settings import GCS_URL, GCS_BUCKET_NAME
from app.config.google_config import google_storage_client


def _map_type_to_role(type: str) -> str:
    type_lower = type.lower()
    
    if any(keyword in type_lower for keyword in ["shirt", "top", "blouse", "t-shirt", "tshirt", "polo", "dress shirt"]):
        return "top"
    elif any(keyword in type_lower for keyword in ["jacket", "coat", "blazer", "outerwear","windbreaker"]):
        return "outwear"
    elif any(keyword in type_lower for keyword in ["pants", "jeans", "trousers", "trouser", "shorts"]):
        return "bottom"
    elif any(keyword in type_lower for keyword in ["shoe", "boot", "sneaker", "sandal", "footwear"]):
        return "footwear"
    else:
        return "other"


async def upload_garment(user_id: str, image_bytes: bytes, filename: str) -> GarmentItem:
    try:
        processing_result = process_image(image_bytes)
        processed_image_bytes = processing_result["processed_image_bytes"]
        garment_type = processing_result["type"]
        tags = processing_result.get("tags", [])
        color = processing_result.get("color")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error classifying image: {str(e)}")
    
    try:
        mapped_role = _map_type_to_role(garment_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mapping type to role: {str(e)}")
    
    try:
        bucket = google_storage_client.bucket(GCS_BUCKET_NAME)
        
        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        safe_filename = filename.replace(" ", "_").replace("/", "_")
        blob_name = f"garment_images/{user_id}/{timestamp}_{safe_filename}"
        
        blob = bucket.blob(blob_name)
        blob.upload_from_string(processed_image_bytes, content_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading to storage: {str(e)}")
    
    try:
        garment = GarmentItem(
            user_id=user_id,
            image_name=blob_name,
            type=garment_type,
            role=mapped_role,
            color=color,
            occasion=None,
            creation_date=datetime.now(timezone.utc)
        )
        
        await save(garment)
        return garment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving garment: {str(e)}")


async def update_garment(garment_id: str, user_id: str, update_data: dict) -> GarmentItem:
    try:
        updated_garment = await update_by_id(garment_id, user_id, update_data)
        
        if not updated_garment:
            raise HTTPException(
                status_code=404,
                detail=f"Garment with ID {garment_id} not found or does not belong to the user"
            )
        
        return updated_garment
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating garment: {str(e)}")


async def delete_garment(garment_id: str, user_id: str) -> bool:
    try:
        # First, get the garment to obtain the storage_url
        garment = await find_by_id(garment_id, user_id)
        
        if not garment:
            raise HTTPException(
                status_code=404,
                detail=f"Garment with ID {garment_id} not found or does not belong to the user"
            )
        
        # Extract blob_name from storage_url
        # storage_url format: https://storage.googleapis.com/{bucket_name}/{blob_name}
        storage_url = garment.storage_url
        blob_name = storage_url.replace(f"{GCS_URL}/", "")
        
        # Delete the blob from GCS
        try:
            bucket = google_storage_client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)
            blob.delete()
        except NotFound:
            # Blob doesn't exist in GCS, but we continue with MongoDB deletion
            # This can happen if the blob was already deleted manually
            pass
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting image from storage: {str(e)}"
            )
        
        # Delete from MongoDB
        deleted = await delete_by_id(garment_id, user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting garment from database"
            )
        
        return True
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting garment: {str(e)}")
