# google_cv_service.py
# Google Cloud Vision service for image analysis

from google.cloud import vision
from app.core.cv_service.image_analysis import ImageAnalysis


def analyze_image(image_bytes: bytes) -> ImageAnalysis:
    client = vision.ImageAnnotatorClient()
    
    # Create image object from bytes
    image = vision.Image(content=image_bytes)

    response = client.annotate_image({
        'image': image,
        'features': [
            {'type_': vision.Feature.Type.LABEL_DETECTION},
            {'type_': vision.Feature.Type.IMAGE_PROPERTIES},
        ],
    })
    
    labels = response.label_annotations
    image_properties = response.image_properties_annotation
    
    # Extract garment type (first label after filtering)
    garment_type = None
    tags_list = []
    
    if labels:
        # Sort labels by score (highest to lowest)
        sorted_labels = sorted(labels, key=lambda x: x.score, reverse=True)
        
        # Filter out generic labels like 'clothing' and 'footwear'
        filtered_labels = [
            label for label in sorted_labels 
            if label.description.lower() not in ["clothing", "footwear", "fashion"]
        ]
        if filtered_labels:
            garment_type = filtered_labels[0].description
            tags_list = [label.description for label in filtered_labels]
    
    # Extract dominant color
    color = None
    if image_properties and image_properties.dominant_colors and image_properties.dominant_colors.colors:
        # Get the most dominant color
        dominant_color = image_properties.dominant_colors.colors[0].color
        # Convert RGB to color name or hex (using RGB values)
        # For simplicity, we'll use a basic color name mapping or return RGB
        # You might want to enhance this with a color name library
        rgb = (dominant_color.red, dominant_color.green, dominant_color.blue)
        r, g, b = rgb
        # Convert RGB to a simple color name (basic implementation)
        color = f"rgb({r},{g},{b})"
    
    # If no type found, raise error
    if not garment_type:
        raise ValueError("Could not classify garment type from Google Cloud Vision")
    
    return ImageAnalysis(
        type=garment_type,
        color=color or "",
        tags=tags_list
    )

