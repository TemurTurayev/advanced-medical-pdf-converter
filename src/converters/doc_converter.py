"""
Legacy DOC format converter
"""
from typing import Optional
import win32com.client
import os
from .base_converter import BaseConverter
from ..errors import ConversionError

class DocConverter(BaseConverter):
    """Converter for legacy .doc format using Win32COM"""
    
    def __init__(self):
        super().__init__()
        self.word = None

    def _init_word(self):
        """Initialize Word application if not already initialized"""
        if self.word is None:
            try:
                self.word = win32com.client.Dispatch('Word.Application')
                self.word.Visible = False
            except Exception as e:
                raise ConversionError(f"Failed to initialize Word: {str(e)}")

    def _cleanup_word(self):
        """Close Word application"""
        if self.word:
            try:
                self.word.Quit()
            except:
                pass
            self.word = None

    def convert(self, file_path: str) -> str:
        """
        Convert DOC file to text
        
        Args:
            file_path: Path to DOC file
            
        Returns:
            Extracted text content
        """
        if not os.path.exists(file_path):
            raise ConversionError(f"File not found: {file_path}")

        try:
            self._init_word()
            doc = self.word.Documents.Open(file_path)
            text = doc.Content.Text
            doc.Close()
            return text
        except Exception as e:
            raise ConversionError(f"Failed to convert DOC file: {str(e)}")
        finally:
            self._cleanup_word()