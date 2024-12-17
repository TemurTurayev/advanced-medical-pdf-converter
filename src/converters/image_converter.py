import pytesseract
from PIL import Image
from typing import Dict, Any
from .base_converter import BaseConverter

class ImageConverter(BaseConverter):
    """Converter for image files (jpg, png, etc.)"""
    
    def __init__(self):
        self.supported_formats = ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
    
    def convert(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Convert image to text using OCR
        
        Args:
            file_path: Path to image file
            **kwargs: Additional conversion parameters
            
        Returns:
            Dict containing extracted text and metadata
        """
        # Open image
        image = Image.open(file_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(image, lang='eng+rus')
        
        # Extract metadata
        metadata = {
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
        }
        
        return {
            'text': text,
            'metadata': metadata,
            'tables': [],
            'terms': [],
            'structures': []
        }
    
    def get_supported_formats(self) -> list:
        """Return list of supported image formats"""
        return self.supported_formats