# azure_cv_service.py
# Azure Computer Vision service for image analysis

from io import BytesIO
from app.settings import azure_cv_client
from app.core.cv_service.image_analysis import ImageAnalysis
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes


def analyze_image(image_bytes: bytes) -> ImageAnalysis:
    """
    Analyze an image using Azure Computer Vision API.
    
    Args:
        image_bytes: Image bytes to analyze
        
    Returns:
        ImageAnalysis object with type, color, and tags
        
    Raises:
        Exception: If Azure CV client is not initialized or analysis fails
        ValueError: If garment type could not be classified
    """
    # Validate Azure CV client is initialized
    if azure_cv_client is None:
        raise Exception("Azure Computer Vision client is not initialized")

    image_stream = BytesIO(image_bytes)
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
        filtered_tags = [tag for tag in sorted_tags if (tag.name.lower() != "clothing" and tag.name.lower() != "footwear")]

        # First tag is the most relevant (garment type) - after filtering
        garment_type = filtered_tags[0].name if filtered_tags else None
        
        # Save all tags, except 'clothing'
        tags_list = [tag.name for tag in filtered_tags]

        print(f"Tags: {tags_list}")
    
    if azure_analysis_result.color:
        color = azure_analysis_result.color.dominant_color_foreground.lower()
    
    # If no type found, raise error
    if not garment_type:
        raise ValueError("Could not classify garment type from Azure Computer Vision")
    
    return ImageAnalysis(
        type=garment_type,
        color=color or "",
        tags=tags_list
    )

