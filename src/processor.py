from datetime import datetime
from typing import Dict, Any
from plugins.manager import PluginManager
from utils.chunked_processor import ChunkedProcessor
from pdf2image import convert_from_bytes
import pytesseract
import time

class ProcessingError(Exception):
    pass

class DocumentProcessor:
    def __init__(self):
        self.plugin_manager = PluginManager()
        self.chunked_processor = ChunkedProcessor()
    
    def process_document(self, file_data: bytes, file_type: str, progress_callback=None) -> Dict[str, Any]:
        try:
            # Determine if we need chunked processing (for files > 10MB)
            file_size = len(file_data)
            if file_size > 10 * 1024 * 1024:
                return self.process_large_file(file_data, file_type, progress_callback)
            
            # Regular processing for smaller files
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
            raise ProcessingError(f'Ошибка обработки документа: {str(e)}')
    
    def process_large_file(self, file_data: bytes, file_type: str, progress_callback=None) -> Dict[str, Any]:
        try:
            results = []
            
            if file_type == 'pdf':
                # Process PDF in chunks
                for text in self.chunked_processor.process_pdf_in_chunks(file_data, progress_callback):
                    results.append({'text': text})
            
            return {
                'pages': results,
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_pages': len(results)
                }
            }
        
        except Exception as e:
            raise ProcessingError(f'Ошибка обработки большого файла: {str(e)}')