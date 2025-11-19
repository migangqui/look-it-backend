# image_processor.py
# Function that encapsulates Azure CV and rembg

from rembg import remove
from io import BytesIO
from PIL import Image
from app.settings import azure_cv_client
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes


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
        processed_image = remove(resized_image)
    except Exception as e:
        raise Exception(f"Error processing image with rembg: {str(e)}")
    
    # 3. Classification with Azure Computer Vision
    try:
        # Validate Azure CV client is initialized
        if azure_cv_client is None:
            raise Exception("Azure Computer Vision client is not initialized")

        image_stream = BytesIO()
        processed_image.save(image_stream, format='PNG')
        image_stream.seek(0)
        
        features = [VisualFeatureTypes.tags, VisualFeatureTypes.color]
        azure_analysis_result = azure_cv_client.analyze_image_in_stream(image_stream, features)
        
        # Extract garment type (first tag or tag with highest confidence)
        garment_type = None
        tags_list = []
        color = None

        if azure_analysis_result.color:
            print("\nColor principal:")
            print(f"  Accent Colour: {azure_analysis_result.color.accent_color}")
            print(f"  Dominante en el fondo: {azure_analysis_result.color.dominant_color_background}")
            print(f"  Dominante en el primer plano: {azure_analysis_result.color.dominant_color_foreground}")
            print(f"  Colores dominantes: {', '.join(azure_analysis_result.color.dominant_colors)}")
            print(f"  Es blanco y negro: {azure_analysis_result.color.is_bw_img}")
        else:
            print("\nNo color detected.")
        
        if azure_analysis_result.tags:
            # Sort tags by confidence (highest to lowest)
            sorted_tags = sorted(azure_analysis_result.tags, key=lambda x: x.confidence, reverse=True)
            
            # Remove any tag named 'clothing' from sorted_tags
            filtered_tags = [tag for tag in sorted_tags if tag.name.lower() != "clothing"]

            # First tag is the most relevant (garment type) - after filtering
            garment_type = filtered_tags[0].name if filtered_tags else None
            
            # Save all tags, except 'clothing'
            tags_list = [tag.name for tag in filtered_tags]

            print(f"Tags: {tags_list}")
            
            # Try to extract color from tags
            color_keywords = ['red', 'blue', 'green', 'yellow', 'black', 'white', 
                            'gray', 'grey', 'brown', 'pink', 'purple', 'orange', 'beige', 'khaki']
            color = None
            for tag in filtered_tags:
                print(f"Tag: {tag.name}")
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
        "processed_image_bytes": image_stream.getvalue(),
        "type": garment_type,
        "tags": tags_list,
        "color": color
    }
