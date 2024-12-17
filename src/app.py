import streamlit as st
import os
import tempfile
from PIL import Image
from pdf2image import convert_from_path
from typing import List, Dict
from datetime import datetime
import asyncio
import sys
from pathlib import Path

# Add the project root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.processor import DocumentProcessor
from src.async_processor import AsyncProcessor
from src.plugins.medical_term import MedicalTermPlugin
from src.plugins.table_detector import TableDetectorPlugin
from src.errors import ProcessingError

# Конфигурация
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class MedicalPDFConverter:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.async_processor = AsyncProcessor()
        
        # Register plugins
        self.processor.plugin_manager.register_plugin(MedicalTermPlugin())
        self.processor.plugin_manager.register_plugin(TableDetectorPlugin())
    
    async def process_document(self, pdf_path: str) -> Dict:
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
            
            # Process images asynchronously
            results = await self.async_processor.process_batch(
                items=images,
                process_func=self.processor.process_document
            )
            
            return {
                'pages': results,
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_pages': len(results)
                }
            }
        except Exception as e:
            raise ProcessingError(f'Document processing failed: {str(e)}')

def main():
    st.title("Медицинский PDF Конвертер")
    
    # Show configuration status
    with st.expander("Проверка конфигурации"):
        if os.path.exists(POPPLER_PATH):
            st.success("✅ Poppler найден")
        else:
            st.error(f"❌ Poppler не найден: {POPPLER_PATH}")
            
        if os.path.exists(TESSERACT_PATH):
            st.success("✅ Tesseract найден")
        else:
            st.error(f"❌ Tesseract не найден: {TESSERACT_PATH}")
    
    converter = MedicalPDFConverter()
    
    uploaded_files = st.file_uploader(
        "Выберите PDF файлы",
        type="pdf",
        accept_multiple_files=True
    )
    
    if uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.text(f"Обработка файла {i+1}/{len(uploaded_files)}")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    results = asyncio.run(converter.process_document(tmp_file.name))
                    
                    # Save results
                    output_folder = "converted_files"
                    os.makedirs(output_folder, exist_ok=True)
                    
                    base_filename = os.path.splitext(uploaded_file.name)[0]
                    
                    # Update progress
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                
                st.success(f"✅ Успешно обработан: {uploaded_file.name}")
                
            except ProcessingError as e:
                st.error(f"❌ Ошибка при обработке {uploaded_file.name}: {str(e)}")
            
            finally:
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
        
        progress_bar.empty()
        status_text.empty()
        st.success("🎉 Обработка завершена!")

if __name__ == "__main__":
    main()