# image_processor.py
# Function that encapsulates Azure CV and rembg

#from rembg import remove
from io import BytesIO
from PIL import Image
from app.core.cv_service.google_cv_service import analyze_image


def _resize_image(image_bytes: bytes, max_size: int = 1024) -> bytes:
    try:
        # Open image from bytes
        original_image = Image.open(BytesIO(image_bytes))
        
        # Make a copy to preserve original
        image_to_process = original_image.copy()
        
        # Resize using thumbnail (maintains aspect ratio, only reduces if needed)
        # Uses LANCZOS resampling for best quality when reducing
        image_to_process.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        return image_to_process
    except Exception as e:
        raise Exception(f"Error resizing image: {str(e)}")


def process_image(image_bytes: bytes) -> dict:
    # Initial validation
    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("Image bytes cannot be empty")
    
    # 1. Resize image to optimize processing (max 1024x1024 maintaining aspect ratio)
    try:
        resized_image = _resize_image(image_bytes, max_size=1024)
    except Exception as e:
        raise Exception(f"Error resizing image: {str(e)}")
    
    # 2. Processing with rembg to remove background
    try:
        #processed_image = remove(resized_image)
        processed_image = resized_image
    except Exception as e:
        raise Exception(f"Error processing image with rembg: {str(e)}")
    
    # 3. Classification with Computer Vision service
    try:
        # Convert processed image to bytes for CV analysis
        image_stream = BytesIO()
        processed_image.save(image_stream, format='PNG')
        image_bytes_for_analysis = image_stream.getvalue()
        
        # Analyze image using CV service
        analysis_result = analyze_image(image_bytes_for_analysis)
        
        garment_type = analysis_result.type
        tags_list = analysis_result.tags
        color = analysis_result.color

        print(f"Garment type: {garment_type}")
        print(f"Tags list: {tags_list}")
        print(f"Color: {color}")
        
    except Exception as e:
        raise Exception(f"Error classifying image with Computer Vision: {str(e)}")
    
    # 4. Return dictionary with results
    return {
        "processed_image_bytes": image_stream.getvalue(),
        "type": garment_type,
        "tags": tags_list,
        "color": color
    }
