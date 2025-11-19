# image_processor.py
# Function that encapsulates Azure CV and rembg

from rembg import remove
from io import BytesIO
from PIL import Image
from app.settings import azure_cv_client


def resize_image(image_bytes: bytes, max_size: int = 1024) -> bytes:
    """
    Resizes an image maintaining aspect ratio to a maximum dimension.
    
    Args:
        image_bytes: Bytes of the original image
        max_size: Maximum width or height (default: 1024)
        
    Returns:
        bytes of the resized image
        
    Raises:
        Exception: If image cannot be processed
    """
    try:
        # Open image from bytes
        original_image = Image.open(BytesIO(image_bytes))
        
        # Make a copy to preserve original
        image_to_process = original_image.copy()
        
        # Resize using thumbnail (maintains aspect ratio, only reduces if needed)
        # Uses LANCZOS resampling for best quality when reducing
        image_to_process.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert back to bytes
        output = BytesIO()
        # Preserve original format if possible, otherwise use PNG
        format = original_image.format if original_image.format else 'PNG'
        image_to_process.save(output, format=format)
        output.seek(0)
        
        return output.getvalue()
    except Exception as e:
        raise Exception(f"Error resizing image: {str(e)}")


def process_image(image_bytes: bytes) -> dict:
    """
    Processes an image received as bytes in memory.
    
    Steps:
    1. Resizes image to max 1024x1024 maintaining aspect ratio
    2. Removes background using rembg
    3. Classifies the image using Azure Computer Vision
    4. Extracts garment type, tags and color
    
    Args:
        image_bytes: Bytes of the original image
        
    Returns:
        dict with:
            - processed_image_bytes: bytes of the image without background
            - type: str with the classified garment type
            - tags: list with additional tags from Azure CV
            - color: str | None with detected color if available
            
    Raises:
        ValueError: If bytes are empty or image is invalid
        Exception: If rembg or Azure CV fails
    """
    # Initial validation
    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("Image bytes cannot be empty")
    
    # 1. Resize image to optimize processing (max 1024x1024 maintaining aspect ratio)
    try:
        resized_image_bytes = resize_image(image_bytes, max_size=1024)
    except Exception as e:
        raise Exception(f"Error resizing image: {str(e)}")
    
    # 2. Processing with rembg to remove background
    try:
        processed_image_bytes = remove(resized_image_bytes)
    except Exception as e:
        raise Exception(f"Error processing image with rembg: {str(e)}")
    
    if not processed_image_bytes or len(processed_image_bytes) == 0:
        raise ValueError("rembg processing did not produce valid results")
    
    # 3. Classification with Azure Computer Vision
    try:
        # Validate Azure CV client is initialized
        if azure_cv_client is None:
            raise Exception("Azure Computer Vision client is not initialized")
        
        # Convert processed bytes to BytesIO to send to Azure CV
        image_stream = BytesIO(processed_image_bytes)
        
        # Get image tags
        tags_result = azure_cv_client.tag_image_in_stream(image_stream)
        
        # Extract garment type (first tag or tag with highest confidence)
        garment_type = None
        tags_list = []
        color = None
        
        if tags_result.tags:
            # Sort tags by confidence (highest to lowest)
            sorted_tags = sorted(tags_result.tags, key=lambda x: x.confidence, reverse=True)
            
            # Remove any tag named 'clothing' from sorted_tags
            filtered_tags = [tag for tag in sorted_tags if tag.name.lower() != "clothing"]

            # First tag is the most relevant (garment type) - after filtering
            garment_type = filtered_tags[0].name if filtered_tags else None
            
            # Save all tags, except 'clothing'
            tags_list = [tag.name for tag in filtered_tags]
            
            # Try to extract color from tags
            color_keywords = ['red', 'blue', 'green', 'yellow', 'black', 'white', 
                            'gray', 'grey', 'brown', 'pink', 'purple', 'orange']
            color = None
            for tag in filtered_tags:
                tag_lower = tag.name.lower()
                if any(color_kw in tag_lower for color_kw in color_keywords):
                    color = tag.name
                    break
        # If no type found, raise error
        if not garment_type:
            raise ValueError("Could not classify garment type from Azure Computer Vision")
        
    except Exception as e:
        raise Exception(f"Error classifying image with Azure Computer Vision: {str(e)}")
    
    # 4. Return dictionary with results
    return {
        "processed_image_bytes": processed_image_bytes,
        "type": garment_type,
        "tags": tags_list,
        "color": color
    }
