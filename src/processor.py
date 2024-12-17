from typing import Dict, List, Optional
from PIL import Image
import numpy as np
from src.plugin_manager import PluginManager
from src.cache import ResultCache
from src.errors import ProcessingError
import pytesseract

class DocumentProcessor:
    def __init__(self):
        self.plugin_manager = PluginManager()
        self.cache = ResultCache()
    
    def process_document(self, image: Image.Image, context: Optional[Dict] = None) -> Dict:
        """Process a single document image
        Args:
            image: PIL Image to process
            context: Optional processing context
        Returns:
            Processing results
        """
        try:
            # First, extract text from image
            text = pytesseract.image_to_string(image, lang='rus+eng')
            
            # Convert to numpy array for OpenCV operations
            np_image = np.array(image)
            
            # Process through plugins with text
            results = self.plugin_manager.process_content({
                'image': np_image,
                'text': text
            }, context)
            
            return results
            
        except Exception as e:
            raise ProcessingError(f'Document processing failed: {str(e)}')