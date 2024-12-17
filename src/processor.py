from typing import Dict, List, Optional
from PIL import Image
import numpy as np
from src.plugin_manager import PluginManager
from src.cache import ResultCache
from src.errors import ProcessingError

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
            # Convert to numpy array for OpenCV operations
            np_image = np.array(image)
            image_bytes = image.tobytes()
            
            # Check cache
            cached_result = self.cache.get(image_bytes, context)
            if cached_result:
                return cached_result
            
            # Process through plugins
            results = self.plugin_manager.process_content(np_image, context)
            
            # Cache results
            self.cache.set(image_bytes, results, context)
            
            return results
        except Exception as e:
            raise ProcessingError(f'Document processing failed: {str(e)}')