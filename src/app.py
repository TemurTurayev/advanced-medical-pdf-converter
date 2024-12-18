import streamlit as st
import os
import tempfile
from PIL import Image
from pdf2image import convert_from_path
from typing import List, Dict
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

    def cleanup(self):
        """Cleanup COM objects"""
        if self.word:
            try:
                self.word.Quit()
            except:
                pass
            self.word = None
            
        if self.powerpoint:
            try:
                self.powerpoint.Quit()
            except:
                pass
            self.powerpoint = None

    def convert_doc(self, file_path: str) -> Dict:
        """Convert legacy DOC file using Word COM object"""
        try:
            if not self.word:
                self.word = win32com.client.Dispatch('Word.Application')
                self.word.Visible = False
            
            doc = self.word.Documents.Open(file_path)
            text = doc.Content.Text
            doc.Close()
            return {'text': text}
        except Exception as e:
            raise ProcessingError(f'Ошибка конвертации DOC файла: {str(e)}')

    def convert_ppt(self, file_path: str) -> Dict:
        """Convert legacy PPT file using PowerPoint COM object"""
        try:
            if not self.powerpoint:
                self.powerpoint = win32com.client.Dispatch('PowerPoint.Application')
            
            ppt = self.powerpoint.Presentations.Open(file_path)
            text_parts = []
            
            for slide in ppt.Slides:
                for shape in slide.Shapes:
                    if hasattr(shape, 'TextFrame'):
                        if shape.TextFrame.HasText:
                            text_parts.append(shape.TextFrame.TextRange.Text)
            
            ppt.Close()
            return {'text': '\n'.join(text_parts)}
        except Exception as e:
            raise ProcessingError(f'Ошибка конвертации PPT файла: {str(e)}')

    def convert_djvu(self, file_path: str) -> Dict:
        """Convert DjVu file using external tools"""
        try:
            # First convert DjVu to PDF using djvulibre
            pdf_path = file_path.rsplit('.', 1)[0] + '.pdf'
            subprocess.run(['ddjvu', '-format=pdf', file_path, pdf_path], check=True)
            
            # Then process the PDF normally
            images = convert_from_path(pdf_path)
            results = self.async_processor.process_batch_sync(
                items=images,
                process_func=self.processor.process_document
            )
            
            # Cleanup temporary PDF
            os.unlink(pdf_path)
            
            return {'text': '\n'.join([r['text'] for r in results])}
        except subprocess.CalledProcessError as e:
            raise ProcessingError(f'Ошибка конвертации DJVU файла: {str(e)}')
        except Exception as e:
            raise ProcessingError(f'Ошибка обработки DJVU файла: {str(e)}')

    def convert_image(self, image_path: str) -> Dict:
        """Convert image file to text using OCR"""
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='eng+rus')
        return {'text': text}
    
    def process_document(self, file_path: str, file_type: str) -> Dict:
        try:
            if file_type == 'pdf':
                # Convert PDF to images
                images = convert_from_path(file_path)
                results = self.async_processor.process_batch_sync(
                    items=images,
                    process_func=self.processor.process_document
                )

            elif file_type in ['jpg', 'jpeg', 'png', 'tiff', 'bmp', 'tif']:
                results = [self.convert_image(file_path)]

            elif file_type == 'doc':
                results = [self.convert_doc(file_path)]

            elif file_type == 'docx':
                # Extract just the text from the docx converter result
                docx_result = self.docx_converter.convert(file_path)
                results = [{'text': docx_result['text']}]

            elif file_type == 'ppt':
                results = [self.convert_ppt(file_path)]

            elif file_type == 'pptx':
                results = [{'text': self.pptx_converter.convert(file_path)}]

            elif file_type in ['html', 'htm']:
                results = [{'text': self.html_converter.convert(file_path)}]

            elif file_type in ['xml', 'json']:
                results = [{'text': self.xml_json_converter.convert(file_path)}]

            elif file_type == 'csv':
                results = [{'text': self.csv_converter.convert(file_path)}]

            elif file_type == 'djvu':
                results = [self.convert_djvu(file_path)]

            else:
                raise ProcessingError(f'Неподдерживаемый формат файла: {file_type}')

            return {
                'pages': results,
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_pages': len(results)
                }
            }

        except Exception as e:
            raise ProcessingError(f'Ошибка обработки документа: {str(e)}')
        finally:
            self.cleanup()

def check_tesseract():
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception as e:
        st.error(f"Ошибка при проверке Tesseract: {str(e)}")
        return False

def check_required_software():
    """Check if required software is installed"""
    missing = []
    
    # Check djvulibre
    try:
        subprocess.run(['ddjvu', '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        missing.append('DjVuLibre (ddjvu)')
        
    # Check Microsoft Office
    try:
        word = win32com.client.Dispatch('Word.Application')
        word.Quit()
    except:
        missing.append('Microsoft Word')
        
    try:
        ppt = win32com.client.Dispatch('PowerPoint.Application')
        ppt.Quit()
    except:
        missing.append('Microsoft PowerPoint')
        
    return missing

def main():
    st.title("Медицинский Документ Конвертер")
    
    # Show configuration status
    with st.expander("Проверка конфигурации"):
        if os.path.exists(POPPLER_PATH):
            st.success("✅ Poppler найден")
        else:
            st.error(f"❌ Poppler не найден: {POPPLER_PATH}")
            
        if os.path.exists(TESSERACT_PATH) and check_tesseract():
            st.success("✅ Tesseract найден")
        else:
            st.error(f"❌ Tesseract не найден: {TESSERACT_PATH}")
            st.stop()
            
        # Check additional software
        missing_software = check_required_software()
        if missing_software:
            st.warning("⚠️ Некоторые форматы могут быть недоступны. Отсутствует ПО:")
            for software in missing_software:
                st.warning(f"- {software}")
        else:
            st.success("✅ Все дополнительные компоненты найдены")
    
    converter = MedicalDocumentConverter()
    
    uploaded_files = st.file_uploader(
        "Выберите файлы для конвертации",
        type=["pdf", "doc", "docx", "ppt", "pptx", "html", "htm", "xml", "json", "csv", 
              "jpg", "jpeg", "png", "tiff", "tif", "bmp", "djvu"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.text(f"Обработка файла {i+1}/{len(uploaded_files)}")
                
                # Get file extension
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    results = converter.process_document(tmp_file.name, file_extension)
                    
                    # Save results
                    output_folder = "converted_files"
                    os.makedirs(output_folder, exist_ok=True)
                    
                    base_filename = os.path.splitext(uploaded_file.name)[0]
                    output_path = os.path.join(output_folder, f"{base_filename}_результат.txt")
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for page_num, page_result in enumerate(results['pages'], 1):
                            f.write(f"\n--- Страница {page_num} ---\n")
                            # Извлекаем текст из результата
                            f.write(page_result.get('text', ''))
                    
                    # Update progress
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                
                st.success(f"✅ Успешно обработан: {uploaded_file.name}")
                
                # Add download button
                with open(output_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label=f"⬇️ Скачать результат для {uploaded_file.name}",
                        data=f.read(),
                        file_name=f"{base_filename}_результат.txt",
                        mime='text/plain'
                    )
                
            except ProcessingError as e:
                st.error(f"❌ Ошибка при обработке {uploaded_file.name}: {str(e)}")
            
            finally:
                try:
                    os.unlink(tmp_file.name)
                    if os.path.exists(output_path):
                        os.unlink(output_path)
                except:
                    pass
        
        progress_bar.empty()
        status_text.empty()
        st.success("🎉 Обработка завершена!")

if __name__ == "__main__":
    main()