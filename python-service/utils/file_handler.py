from fastapi import UploadFile
import os
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileHandler:
    """Service for handling file uploads and validation"""
    
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        self.allowed_extensions = {
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'pdf'
        }
        
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB default
    
    def validate_file(self, file: UploadFile) -> bool:
        """
        Validate uploaded file
        
        Args:
            file: UploadFile object
            
        Returns:
            True if valid
        """
        # Check filename
        if not file.filename:
            return False
        
        # Check extension
        ext = file.filename.split('.')[-1].lower()
        if ext not in self.allowed_extensions:
            logger.warning(f"Invalid file extension: {ext}")
            return False
        
        return True
    
    async def save_upload(self, file: UploadFile) -> str:
        """
        Save uploaded file to disk
        
        Args:
            file: UploadFile object
            
        Returns:
            Path to saved file
        """
        try:
            # Generate unique filename
            ext = file.filename.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            file_path = self.upload_dir / unique_filename
            
            # Save file
            contents = await file.read()
            
            # Check file size
            if len(contents) > self.max_file_size:
                raise ValueError(f"File too large: {len(contents)} bytes")
            
            with open(file_path, 'wb') as f:
                f.write(contents)
            
            logger.info(f"File saved: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"File save failed: {str(e)}")
            raise
    
    def cleanup_file(self, file_path: str):
        """
        Delete temporary file
        
        Args:
            file_path: Path to file
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"File cleanup failed: {str(e)}")
