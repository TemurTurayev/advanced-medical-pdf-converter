import streamlit as st
import os
import tempfile
from PIL import Image
from pdf2image import convert_from_path
from typing import List, Dict, Optional
from datetime import datetime
import sys
from pathlib import Path
import pytesseract
import win32com.client
import subprocess

# Add the project root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.processor import DocumentProcessor
from src.async_processor import AsyncProcessor
from src.plugins.medical_term import MedicalTermPlugin
from src.plugins.table_detector import TableDetectorPlugin
from src.errors import ProcessingError
from src.config import POPPLER_PATH, TESSERACT_PATH
from src.converters.docx_converter import DocxConverter
from src.converters.pptx_converter import PptxConverter
from src.converters.html_converter import HtmlConverter
from src.converters.xml_json_converter import XmlJsonConverter
from src.converters.csv_converter import CsvConverter
from src.utils.progress import ProcessingProgress

SUPPORTED_FORMATS = {
    'Документы': ['doc', 'docx', 'ppt', 'pptx', 'pdf', 'djvu'],
    'Веб-форматы': ['html', 'htm', 'xml', 'json'],
    'Таблицы': ['csv'],
    'Изображения': ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp']
}

class MedicalDocumentConverter:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.async_processor = AsyncProcessor()
        
        # Register plugins
        self.processor.plugin_manager.register_plugin(MedicalTermPlugin())
        self.processor.plugin_manager.register_plugin(TableDetectorPlugin())
        
        # Initialize converters
        self.docx_converter = DocxConverter()
        self.pptx_converter = PptxConverter()
        self.html_converter = HtmlConverter()
        self.xml_json_converter = XmlJsonConverter()
        self.csv_converter = CsvConverter()
        
        # Initialize COM objects for legacy formats
        self.word = None
        self.powerpoint = None
        
        # Initialize progress tracking
        self.progress: Optional[ProcessingProgress] = None
        self.status_callback = None

    def set_progress(self, progress: ProcessingProgress):
        self.progress = progress

    def set_status_callback(self, callback):
        self.status_callback = callback

    def update_status(self, message: str):
        if self.status_callback:
            self.status_callback(message)

    ...

def main():
    st.title("Медицинский Документ Конвертер")
    
    ...
    
    if uploaded_files:
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            page_status = st.empty()
            details_text = st.empty()
        
        # Initialize progress tracking
        total_progress = ProcessingProgress(total_files=len(uploaded_files))
        converter.set_progress(total_progress)
        converter.set_status_callback(lambda msg: details_text.text(msg))
        
        for i, uploaded_file in enumerate(uploaded_files, 1):
            try:
                total_progress.update(file=i)
                file_name = uploaded_file.name
                total_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Size in MB
                
                status_text.text(f"Обработка файла {i}/{len(uploaded_files)}: {file_name} ({total_size:.1f} MB)")
                
                ...
                
                progress = total_progress.get_progress()
                progress_bar.progress(progress)
                
            except Exception as e:
                st.error(f"❌ Ошибка при обработке {file_name}: {str(e)}")
            
            finally:
                try:
                    if 'tmp_file' in locals():
                        os.unlink(tmp_file.name)
                except Exception as e:
                    st.warning(f"⚠️ Ошибка при очистке временных файлов: {str(e)}")
        
        progress_container.empty()
        st.success("🎉 Обработка всех файлов завершена!")

if __name__ == "__main__":
    main()