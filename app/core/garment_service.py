# garment_service.py
# Lógica de subida, rembg, y GCS

from fastapi import HTTPException
from google.cloud import storage
from datetime import datetime, timezone
from app.core.image_processor import process_image
from app.db.mongo_models import GarmentItem
from app.db.repository.garmentitem_repository import save
from app.settings import GCS_BUCKET_NAME


def _map_type_to_role(type: str) -> str:
    type_lower = type.lower()
    
    if any(keyword in type_lower for keyword in ["shirt", "top", "blouse", "t-shirt", "tshirt"]):
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
    # Step 1: Process image
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
    
    # Step 2: Map type to role
    try:
        mapped_role = _map_type_to_role(garment_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mapping type to role: {str(e)}")
    
    # Step 3: Upload to Google Cloud Storage
    try:
        # Create GCS client (uses default credentials)
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        
        # Generate unique filename: {user_id}/{timestamp}_{filename}
        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)  # milliseconds
        # Clean filename to avoid issues with special characters
        safe_filename = filename.replace(" ", "_").replace("/", "_")
        blob_name = f"{user_id}/{timestamp}_{safe_filename}"
        
        # Upload processed image
        blob = bucket.blob(blob_name)
        blob.upload_from_string(processed_image_bytes, content_type="image/png")
        
        # Make blob publicly accessible and get URL
        storage_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{blob_name}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading to storage: {str(e)}")
    
    # Step 4: Create and save GarmentItem
    try:
        garment = GarmentItem(
            user_id=user_id,
            storage_url=storage_url,
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
