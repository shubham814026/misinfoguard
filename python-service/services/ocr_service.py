import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path
import logging
import os
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


class OCRService:
    """Service for extracting text from images and PDFs with multi-news detection"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.pdf']
        self.min_text_confidence = 30  # Minimum OCR confidence to accept text
        self.min_text_length = 20  # Minimum characters to consider valid text
    
    async def extract_text(self, file_path: str) -> Dict:
        """
        Extract text from image or PDF file with smart multi-news detection
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict with 'status', 'text', 'news_items' (if multiple), 'message'
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                raw_text = await self._extract_from_pdf(file_path)
            else:
                raw_text = await self._extract_from_image(file_path)
            
            # Validate extracted text
            validation = self._validate_text(raw_text)
            if not validation['is_valid']:
                return {
                    'status': 'invalid',
                    'text': '',
                    'message': validation['message']
                }
            
            # Detect multiple news items
            news_items = self._detect_multiple_news(raw_text)
            
            if len(news_items) > 1:
                return {
                    'status': 'success',
                    'text': raw_text,
                    'news_items': news_items,
                    'count': len(news_items),
                    'message': f'Detected {len(news_items)} separate news items in the image'
                }
            else:
                return {
                    'status': 'success',
                    'text': raw_text,
                    'news_items': [raw_text],
                    'count': 1,
                    'message': 'Single news item detected'
                }
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return {
                'status': 'error',
                'text': '',
                'message': f'Failed to extract text: {str(e)}'
            }
    
    async def _extract_from_image(self, image_path: str) -> str:
        """Extract text from image file with multilingual support"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Check if image is valid (not just noise/garbage)
            if not self._is_valid_image(img):
                raise ValueError("Image appears to be corrupted or contains no readable content")
            
            # Preprocess image for better OCR
            processed_img = self._preprocess_image(img)
            
            # Convert to PIL Image
            pil_img = Image.fromarray(processed_img)
            
            # Extract text using Tesseract with multiple languages
            # Supports English, Spanish, French, German, Hindi, Arabic, Chinese
            text = pytesseract.image_to_string(
                pil_img, 
                lang='eng+spa+fra+deu+hin+ara+chi_sim'
            )
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Image OCR failed: {str(e)}")
            raise
    
    async def _extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file with multilingual support and multi-news detection"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            all_text = []
            
            # Extract text from each page with multilingual OCR
            for i, image in enumerate(images):
                logger.info(f"Processing PDF page {i+1}/{len(images)}")
                
                # Convert PIL image to numpy array
                img_array = np.array(image)
                
                # Preprocess
                processed_img = self._preprocess_image(img_array)
                
                # Convert back to PIL
                pil_img = Image.fromarray(processed_img)
                
                # Extract text with multilingual support
                text = pytesseract.image_to_string(
                    pil_img, 
                    lang='eng+spa+fra+deu+hin+ara+chi_sim'
                )
                
                # Validate text quality
                if self._validate_text(text):
                    all_text.append(text.strip())
                else:
                    logger.warning(f"Page {i+1} text validation failed, skipping")
            
            if not all_text:
                logger.error("No valid text extracted from any PDF page")
                return ""
            
            # Join all pages with clear separator
            combined_text = "\n\n--- PAGE BREAK ---\n\n".join(all_text)
            
            return combined_text.strip()
            
        except Exception as e:
            logger.error(f"PDF OCR failed: {str(e)}")
            raise
    
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy
        - Convert to grayscale
        - Apply denoising
        - Apply thresholding
        - Enhance contrast
        """
        try:
            # Convert to grayscale if needed
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(thresh)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {str(e)}")
            return img
    
    def _is_valid_image(self, img: np.ndarray) -> bool:
        """Check if image contains readable content (not garbage/noise)"""
        try:
            # Check image dimensions
            height, width = img.shape[:2]
            if height < 50 or width < 50:
                return False
            
            # Check if image is too dark or too bright (likely corrupted)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            mean_brightness = np.mean(gray)
            
            if mean_brightness < 10 or mean_brightness > 245:
                return False
            
            # Check variance (low variance = likely blank/noise)
            variance = np.var(gray)
            if variance < 100:
                return False
            
            return True
            
        except:
            return True  # If check fails, assume valid
    
    def _validate_text(self, text: str) -> Dict:
        """Validate extracted text quality"""
        if not text or len(text.strip()) < self.min_text_length:
            return {
                'is_valid': False,
                'message': 'No readable text found in the image. Please upload a clear image with text content.'
            }
        
        # Check if text is mostly gibberish (high ratio of non-alphanumeric)
        alphanumeric_count = sum(c.isalnum() or c.isspace() for c in text)
        gibberish_ratio = 1 - (alphanumeric_count / len(text))
        
        if gibberish_ratio > 0.5:
            return {
                'is_valid': False,
                'message': 'Image appears to contain unreadable or corrupted content. Please upload a clearer image.'
            }
        
        # Check for minimum word count
        words = text.split()
        if len(words) < 5:
            return {
                'is_valid': False,
                'message': 'Insufficient text content detected. Please upload an image with more readable text.'
            }
        
        return {'is_valid': True, 'message': 'Text validation successful'}
    
    def _detect_multiple_news(self, text: str) -> List[str]:
        """Detect and separate multiple news items - handles both images and PDFs"""
        
        # Method 1: Check for PDF page breaks first
        if "--- PAGE BREAK ---" in text:
            logger.info("PDF page breaks detected, splitting by pages")
            segments = [s.strip() for s in text.split("--- PAGE BREAK ---") if s.strip()]
        else:
            # Method 2: Split by very clear separators (multiple blank lines)
            segments = re.split(r'\n\s*\n\s*\n+', text)  # 3+ newlines = different news
            
            if len(segments) == 1:
                # Try splitting by major headlines (ALL CAPS lines)
                segments = re.split(r'\n([A-Z][A-Z\s]{20,})\n', text)
                segments = [s.strip() for s in segments if len(s.strip()) > 50]
        
        if len(segments) <= 1:
            return [text.strip()]  # Single news item
        
        # Check if segments are about the same topic using keyword overlap
        merged_segments = []
        current_segment = segments[0]
        
        for i in range(1, len(segments)):
            next_segment = segments[i]
            
            # Calculate topic similarity
            if self._are_same_topic(current_segment, next_segment):
                # Same topic - merge them
                current_segment += "\n\n" + next_segment
            else:
                # Different topic - save current and start new
                merged_segments.append(current_segment)
                current_segment = next_segment
        
        # Add the last segment
        merged_segments.append(current_segment)
        
        # Filter out very short segments
        valid_segments = []
        for segment in merged_segments:
            cleaned = segment.strip()
            word_count = len(cleaned.split())
            
            # Only consider as separate news if substantial (30+ words)
            if word_count >= 30:
                valid_segments.append(cleaned)
            elif valid_segments:
                # Append short segment to previous one
                valid_segments[-1] += "\n\n" + cleaned
            else:
                valid_segments.append(cleaned)
        
        # If we only have 1-2 segments with high similarity, treat as single news
        if len(valid_segments) == 2 and self._are_same_topic(valid_segments[0], valid_segments[1]):
            return ["\n\n".join(valid_segments)]
        
        logger.info(f"Detected {len(valid_segments)} separate news item(s)")
        return valid_segments if valid_segments else [text.strip()]
    
    def _are_same_topic(self, text1: str, text2: str, threshold: float = 0.3) -> bool:
        """Check if two text segments are about the same topic using keyword overlap"""
        # Extract key entities and words (nouns, proper nouns, numbers)
        words1 = set(re.findall(r'\b[A-Z][a-z]+\b', text1))  # Capitalized words (entities)
        words2 = set(re.findall(r'\b[A-Z][a-z]+\b', text2))
        
        # Add numbers (dates, statistics, etc.)
        nums1 = set(re.findall(r'\b\d+\b', text1))
        nums2 = set(re.findall(r'\b\d+\b', text2))
        
        words1.update(nums1)
        words2.update(nums2)
        
        # Remove common words
        common_stop = {'The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'Of', 'With', 'By'}
        words1 -= common_stop
        words2 -= common_stop
        
        if not words1 or not words2:
            return True  # If no key entities, assume same topic
        
        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        similarity = intersection / union if union > 0 else 0
        
        # If significant keyword overlap, same topic
        return similarity >= threshold
