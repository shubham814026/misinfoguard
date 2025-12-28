import re
import logging
from PIL import Image
import numpy as np
import cv2
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class ImageContentClassifier:
    """
    Classifier to detect the type of image content.
    Distinguishes between: photos, documents/screenshots, memes, etc.
    Uses image analysis heuristics (no ML model required).
    """
    
    def __init__(self):
        # Thresholds for classification
        self.text_density_threshold = 0.02  # Minimum text density for document
        self.edge_density_threshold = 0.15  # Edge density for document detection
        self.color_variance_threshold = 5000  # Color variance for photo detection
    
    def classify_image(self, image_path: str) -> Dict:
        """
        Classify an image based on its visual characteristics.
        
        Returns:
            Dict with:
            - image_type: 'photo', 'document', 'screenshot', 'graphic', 'unknown'
            - is_likely_news: True if image likely contains news content
            - confidence: 0-1 confidence score
            - reason: Explanation
        """
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return self._default_result("Could not load image")
            
            # Get image properties
            height, width = img.shape[:2]
            total_pixels = height * width
            
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Calculate various metrics
            edge_density = self._calculate_edge_density(gray)
            color_variance = self._calculate_color_variance(hsv)
            text_regions = self._detect_text_regions(gray)
            has_natural_colors = self._has_natural_photo_colors(hsv)
            aspect_ratio = width / height
            
            # Classification logic
            
            # 1. Document/Screenshot Detection
            # High edge density + text regions + low color variance
            if edge_density > 0.1 and text_regions > 5 and color_variance < 3000:
                return {
                    "image_type": "document",
                    "is_likely_news": True,
                    "confidence": 0.8,
                    "reason": "Image appears to be a document or screenshot with text content"
                }
            
            # 2. Screenshot with some text
            if text_regions > 3 and edge_density > 0.08:
                return {
                    "image_type": "screenshot",
                    "is_likely_news": True,
                    "confidence": 0.7,
                    "reason": "Image appears to be a screenshot with readable content"
                }
            
            # 3. Natural Photo Detection (animals, landscapes, people, objects)
            # High color variance + natural colors + low text regions
            if color_variance > 4000 and has_natural_colors and text_regions < 3:
                return {
                    "image_type": "photo",
                    "is_likely_news": False,
                    "confidence": 0.85,
                    "reason": "Image appears to be a photograph without news text content"
                }
            
            # 4. Photo with moderate characteristics
            if has_natural_colors and text_regions < 2 and color_variance > 2000:
                return {
                    "image_type": "photo",
                    "is_likely_news": False,
                    "confidence": 0.75,
                    "reason": "Image appears to be a natural photograph"
                }
            
            # 5. Graphic/Meme Detection
            # Low natural colors + some text + moderate edges
            if not has_natural_colors and text_regions >= 1 and text_regions <= 5:
                return {
                    "image_type": "graphic",
                    "is_likely_news": False,
                    "confidence": 0.6,
                    "reason": "Image appears to be a graphic or meme"
                }
            
            # 6. If has text regions, assume it might be news
            if text_regions >= 2:
                return {
                    "image_type": "mixed",
                    "is_likely_news": True,
                    "confidence": 0.5,
                    "reason": "Image contains some text content"
                }
            
            # 7. Default - likely a photo without text
            return {
                "image_type": "photo",
                "is_likely_news": False,
                "confidence": 0.6,
                "reason": "Image does not appear to contain news or text content"
            }
            
        except Exception as e:
            logger.error(f"Image classification failed: {str(e)}")
            return self._default_result(f"Classification error: {str(e)}")
    
    def _default_result(self, reason: str) -> Dict:
        """Return default result when classification fails"""
        return {
            "image_type": "unknown",
            "is_likely_news": True,  # Default to True to allow processing
            "confidence": 0.3,
            "reason": reason
        }
    
    def _calculate_edge_density(self, gray: np.ndarray) -> float:
        """Calculate edge density using Canny edge detection"""
        try:
            edges = cv2.Canny(gray, 50, 150)
            edge_pixels = np.sum(edges > 0)
            total_pixels = gray.shape[0] * gray.shape[1]
            return edge_pixels / total_pixels
        except:
            return 0.0
    
    def _calculate_color_variance(self, hsv: np.ndarray) -> float:
        """Calculate color variance (high for natural photos, low for documents)"""
        try:
            # Use Hue and Saturation channels
            h, s, v = cv2.split(hsv)
            
            # Calculate variance
            h_var = np.var(h)
            s_var = np.var(s)
            v_var = np.var(v)
            
            # Combined variance
            return h_var + s_var + v_var
        except:
            return 0.0
    
    def _detect_text_regions(self, gray: np.ndarray) -> int:
        """Detect potential text regions using morphological operations"""
        try:
            # Apply threshold
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Morphological operations to find text-like regions
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
            dilated = cv2.dilate(binary, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours that look like text lines
            text_regions = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect = w / h if h > 0 else 0
                area = w * h
                
                # Text-like regions: wide, not too tall, reasonable size
                if aspect > 2 and area > 500 and h < 100:
                    text_regions += 1
            
            return text_regions
        except:
            return 0
    
    def _has_natural_photo_colors(self, hsv: np.ndarray) -> bool:
        """Check if image has natural photo-like color distribution"""
        try:
            h, s, v = cv2.split(hsv)
            
            # Natural photos typically have:
            # - Moderate saturation (not too vivid)
            # - Good range of values (not flat)
            # - Diverse hue distribution
            
            mean_saturation = np.mean(s)
            saturation_std = np.std(s)
            value_std = np.std(v)
            
            # Natural photos have moderate saturation and good tonal range
            has_natural_sat = 30 < mean_saturation < 180
            has_tonal_range = value_std > 40
            has_sat_variation = saturation_std > 30
            
            return has_natural_sat and has_tonal_range and has_sat_variation
        except:
            return False


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
    