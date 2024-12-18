import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the converter"""
    
    # OCR settings
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
    TESSERACT_LANG = os.getenv('TESSERACT_LANG', 'eng+rus')
    
    # Image processing
    MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', '60.0'))
    CONTRAST_FACTOR = float(os.getenv('CONTRAST_FACTOR', '1.5'))
    
    # Medical dictionary
    MEDICAL_DICT_PATH = os.getenv('MEDICAL_DICT_PATH', 'data/medical_dictionary.json')
    
    # Output settings
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'converted_files')
    
    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        if not os.path.exists(cls.TESSERACT_PATH):
            raise ValueError(f'Tesseract not found at {cls.TESSERACT_PATH}')
            
        if not os.path.exists(cls.OUTPUT_DIR):
            os.makedirs(cls.OUTPUT_DIR)
            
        return True