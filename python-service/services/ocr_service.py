import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path
import logging
import os

logger = logging.getLogger(__name__)


class OCRService:
    """Service for extracting text from images and PDFs using Tesseract OCR"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.pdf']
    
    async def extract_text(self, file_path: str) -> str:
        """
        Extract text from image or PDF file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text string
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return await self._extract_from_pdf(file_path)
            else:
                return await self._extract_from_image(file_path)
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise
    
    async def _extract_from_image(self, image_path: str) -> str:
        """Extract text from image file"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            if img is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Preprocess image for better OCR
            processed_img = self._preprocess_image(img)
            
            # Convert to PIL Image
            pil_img = Image.fromarray(processed_img)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(pil_img, lang='eng')
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Image OCR failed: {str(e)}")
            raise
    
    async def _extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            all_text = []
            
            # Extract text from each page
            for i, image in enumerate(images):
                # Convert PIL image to numpy array
                img_array = np.array(image)
                
                # Preprocess
                processed_img = self._preprocess_image(img_array)
                
                # Convert back to PIL
                pil_img = Image.fromarray(processed_img)
                
                # Extract text
                text = pytesseract.image_to_string(pil_img, lang='eng')
                all_text.append(text)
            
            return "\n\n".join(all_text).strip()
            
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
