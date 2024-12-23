import os
from datetime import datetime
from plugins.manager import PluginManager
from pdf2image import convert_from_bytes
import pytesseract

class DocumentProcessor:
    def __init__(self):
        self.plugin_manager = PluginManager()
    
    def process_document(self, file_data: bytes, file_type: str) -> dict:
        try:
            results = []
            if file_type == 'pdf':
                images = convert_from_bytes(file_data)
                for image in images:
                    text = pytesseract.image_to_string(image, lang='eng+rus')
                    results.append({'text': text})
            
            return {
                'pages': results,
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_pages': len(results)
                }
            }
            
        except Exception as e:
            raise Exception(f'Ошибка обработки документа: {str(e)}')