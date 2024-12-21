import os

# Configuration settings
CONFIG = {
    # File processing
    'MAX_FILE_SIZE': 200 * 1024 * 1024,  # 200MB in bytes
    'CHUNK_SIZE': 5 * 1024 * 1024,  # 5MB chunks for large files
    'PROCESSING_TIMEOUT': 900,  # 15 minutes timeout
    
    # Progress tracking
    'ENABLE_PROGRESS_BAR': True,
    'PROGRESS_UPDATE_INTERVAL': 0.5,  # seconds
    
    # System checks
    'REQUIRED_SOFTWARE': {
        'poppler': {
            'name': 'Poppler',
            'check_command': 'pdftoppm -h',
            'install_guide': 'Please install Poppler for PDF processing'
        },
        'tesseract': {
            'name': 'Tesseract',
            'check_command': 'tesseract --version',
            'install_guide': 'Please install Tesseract for OCR functionality'
        },
        'djvulibre': {
            'name': 'DjVuLibre',
            'check_command': 'djvulibre-bin -v',
            'install_guide': 'Please install DjVuLibre for DjVu processing'
        }
    },
    
    # Processing settings
    'OCR_LANGUAGES': ['eng', 'rus'],
    'IMAGE_DPI': 300,
    'COMPRESSION_QUALITY': 90,
    
    # Temporary files
    'TEMP_DIR': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp'),
}