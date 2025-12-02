# image_analysis.py
# Data model for image analysis results

from dataclasses import dataclass


@dataclass
class ImageAnalysis:
    """Data class representing the result of image analysis."""
    type: str  # Type of garment detected
    color: str  # Dominant color
    tags: list[str]  # List of detected tags

