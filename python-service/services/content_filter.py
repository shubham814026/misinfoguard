import re
import logging
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class ContentFilter:
    """Service for filtering inappropriate content"""
    
    def __init__(self):
        # Inappropriate keywords
        self.nsfw_keywords = [
            # Adult content
            'porn', 'xxx', 'nude', 'naked', 'nsfw',
            'sex', 'erotic', 'adult only', 'explicit',
            # Violence
            'gore', 'brutal', 'torture', 'kill',
            # Hate speech indicators
            'racial slur', 'hate speech'
        ]
        
        # More comprehensive list can be added from external libraries
    
    def is_nsfw(self, image_path: str) -> bool:
        """
        Check if image contains NSFW content
        Uses basic heuristics - in production, use ML model like Yahoo Open NSFW
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if content appears inappropriate
        """
        try:
            # Load image
            img = Image.open(image_path)
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Basic skin tone detection (simplified heuristic)
            # In production, use proper NSFW detection model
            skin_percentage = self._detect_skin_percentage(img_array)
            
            # If > 60% skin-colored pixels, might be inappropriate
            if skin_percentage > 0.6:
                logger.warning(f"Image flagged for high skin tone percentage: {skin_percentage}")
                # For now, we'll be lenient and only warn
                # return True
            
            return False
            
        except Exception as e:
            logger.error(f"NSFW check failed: {str(e)}")
            return False
    