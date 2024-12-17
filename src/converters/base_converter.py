from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseConverter(ABC):
    """Base class for all document converters"""
    
    @abstractmethod
    def convert(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Convert document to desired format
        
        Args:
            file_path: Path to input file
            **kwargs: Additional conversion parameters
            
        Returns:
            Dict containing:
                - text: Extracted text
                - metadata: Document metadata
                - tables: Extracted tables
                - terms: Medical terms
                - structures: Document structure
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> list:
        """Return list of supported input formats"""
        pass