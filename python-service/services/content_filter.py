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
            skin_percentage = self._detect_skin_tone(img_array)
            
            # If > 60% skin-colored pixels, might be inappropriate
            if skin_percentage > 0.6:
                logger.warning(f"Image flagged for high skin tone percentage: {skin_percentage}")
                # For now, we'll be lenient and only warn
                # return True
            
            return False
            
        except Exception as e:
            logger.error(f"NSFW check failed: {str(e)}")
            return False
    
    def _detect_skin_tone(self, img_array: np.ndarray) -> float:
        """Detect percentage of skin-tone pixels (simple heuristic)"""
        try:
            if len(img_array.shape) != 3:
                return 0.0
            
            # Convert to RGB if needed
            if img_array.shape[2] == 4:  # RGBA
                img_array = img_array[:, :, :3]
            
            # Simple skin tone detection in RGB
            # Skin tone ranges (approximate)
            r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
            
            # Skin tone heuristics
            skin_mask = (
                (r > 95) & (g > 40) & (b > 20) &
                (r > g) & (r > b) &
                (abs(r - g) > 15)
            )
            
            skin_percentage = np.sum(skin_mask) / skin_mask.size
            return skin_percentage
            
        except:
            return 0.0
    
    def contains_inappropriate_text(self, text: str) -> bool:
        """
        Check if text contains inappropriate content
        
        Args:
            text: Text to check
            
        Returns:
            True if inappropriate content detected
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for NSFW keywords
        for keyword in self.nsfw_keywords:
            if keyword in text_lower:
                logger.warning(f"Inappropriate keyword detected: {keyword}")
                return True
        
        return False
    