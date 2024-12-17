class ProcessingError(Exception):
    """Base class for processing errors"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class OCRError(ProcessingError):
    """Raised when OCR processing fails"""
    pass

class ValidationError(ProcessingError):
    """Raised when validation fails"""
    pass

class PluginError(ProcessingError):
    """Raised when plugin processing fails"""
    pass

class FileProcessingError(ProcessingError):
    """Raised when file processing fails"""
    pass