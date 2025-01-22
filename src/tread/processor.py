import torch
from typing import Dict, List, Optional
import pytesseract
from PIL import Image
import pdf2image
from .config import TREAD_CONFIG

class TREADProcessor:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or TREAD_CONFIG
        self.cache = {}
        self._init_ocr()

    def _init_ocr(self):
        if self.config['enhance_medical']:
            pytesseract.pytesseract.tesseract_cmd = 'tesseract'
            self.ocr_config = f"--oem 1 --psm 3 -l {self.config['ocr_lang']} --dpi {self.config['ocr_dpi']}"

    def process_pdf(self, pdf_path: str) -> Dict:
        images = self._pdf_to_images(pdf_path)
        results = []
        
        for image in images:
            cache_key = self._get_cache_key(image)
            if cache_key in self.cache:
                results.append(self.cache[cache_key])
                continue
            
            page_result = self._process_page(image)
            if self.config['use_cache']:
                self.cache[cache_key] = page_result
            results.append(page_result)
            
        return self._merge_results(results)