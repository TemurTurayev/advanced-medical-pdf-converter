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
import pythoncom
import subprocess
import shutil

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

SUPPORTED_FORMATS = {
    'Документы': ['doc', 'docx', 'ppt', 'pptx', 'pdf', 'djvu'],
    'Веб-форматы': ['html', 'htm', 'xml', 'json'],
    'Таблицы': ['csv'],
    'Изображения': ['jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp']
}

class MedicalDocumentConverter:
    def __init__(self):
        # Initialize COM
        pythoncom.CoInitialize()
        
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
            
        # Uninitialize COM
        pythoncom.CoUninitialize()

    def convert_doc(self, file_path: str) -> str:
        try:
            if not self.word:
                self.word = win32com.client.Dispatch('Word.Application')
                self.word.Visible = False
            
            doc = self.word.Documents.Open(str(Path(file_path).resolve()))
            text = doc.Content.Text
            doc.Close()
            return text
        except Exception as e:
            raise ProcessingError(f'Ошибка конвертации DOC файла: {str(e)}')

    def convert_ppt(self, file_path: str) -> str:
        try:
            if not self.powerpoint:
                self.powerpoint = win32com.client.Dispatch('PowerPoint.Application')
            
            file_path = str(Path(file_path).resolve())
            ppt = self.powerpoint.Presentations.Open(file_path, WithWindow=False)
            text_parts = []
            
            for slide in ppt.Slides:
                for shape in slide.Shapes:
                    if hasattr(shape, 'TextFrame'):
                        if shape.TextFrame.HasText:
                            text_parts.append(shape.TextFrame.TextRange.Text)
            
            ppt.Close()
            return '\n'.join(text_parts)
        except Exception as e:
            raise ProcessingError(f'Ошибка конвертации PPT файла: {str(e)}')

    def convert_djvu(self, file_path: str) -> str:
        try:
            # Проверяем наличие ddjvu
            ddjvu_path = shutil.which('ddjvu')
            if not ddjvu_path:
                raise ProcessingError('DjVuLibre (ddjvu) не установлен')
            
            # Создаем временную директорию для конвертации
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_path = os.path.join(temp_dir, 'output.pdf')
                
                # Конвертируем DJVU в PDF
                result = subprocess.run(
                    [ddjvu_path, '-format=pdf', str(Path(file_path).resolve()), pdf_path],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    raise ProcessingError(f'Ошибка конвертации DJVU в PDF: {result.stderr}')
                
                # Конвертируем PDF в изображения
                images = convert_from_path(pdf_path)
                text_parts = []
                
                # Извлекаем текст из каждой страницы
                for image in images:
                    text = pytesseract.image_to_string(image, lang='eng+rus')
                    text_parts.append(text)
                
                return '\n\n'.join(text_parts)
                
        except subprocess.CalledProcessError as e:
            raise ProcessingError(f'Ошибка запуска ddjvu: {str(e)}')
        except Exception as e:
            raise ProcessingError(f'Ошибка обработки DJVU файла: {str(e)}')

    def convert_image(self, image_path: str) -> str:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image, lang='eng+rus')
    
    def process_document(self, file_path: str, file_type: str) -> Dict:
        try:
            text = None
            if file_type == 'pdf':
                images = convert_from_path(file_path)
                text_parts = []
                for image in images:
                    text = pytesseract.image_to_string(image, lang='eng+rus')
                    text_parts.append(text)
                results = [{'text': text} for text in text_parts]

            elif file_type in ['jpg', 'jpeg', 'png', 'tiff', 'bmp', 'tif']:
                text = self.convert_image(file_path)
                results = [{'text': text}]

            elif file_type == 'doc':
                text = self.convert_doc(file_path)
                results = [{'text': text}]

            elif file_type == 'docx':
                text = self.docx_converter.convert(file_path)
                results = [{'text': text}]

            elif file_type == 'ppt':
                text = self.convert_ppt(file_path)
                results = [{'text': text}]

            elif file_type == 'pptx':
                text = self.pptx_converter.convert(file_path)
                results = [{'text': text}]

            elif file_type in ['html', 'htm']:
                text = self.html_converter.convert(file_path)
                results = [{'text': text}]

            elif file_type in ['xml', 'json']:
                text = self.xml_json_converter.convert(file_path)
                results = [{'text': text}]

            elif file_type == 'csv':
                text = self.csv_converter.convert(file_path)
                results = [{'text': text}]

            elif file_type == 'djvu':
                text = self.convert_djvu(file_path)
                results = [{'text': text}]

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
    missing = []
    
    # Проверка DjVuLibre
    if not shutil.which('ddjvu'):
        missing.append('DjVuLibre (ddjvu)')
    
    # Проверка MS Office
    try:
        pythoncom.CoInitialize()
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
        
    finally:
        pythoncom.CoUninitialize()
            
    return missing

def main():
    st.title("Медицинский Документ Конвертер")
    
    with st.expander("Проверка конфигурации", expanded=True):
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
    
    all_formats = [fmt for formats in SUPPORTED_FORMATS.values() for fmt in formats]
    
    uploaded_files = st.file_uploader(
        "Выберите файлы для конвертации",
        type=all_formats,
        accept_multiple_files=True
    )
    
    if uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.text(f"Обработка файла {i+1}/{len(uploaded_files)}")
                
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    results = converter.process_document(tmp_file.name, file_extension)
                    
                    output_folder = "converted_files"
                    os.makedirs(output_folder, exist_ok=True)
                    
                    base_filename = os.path.splitext(uploaded_file.name)[0]
                    output_path = os.path.join(output_folder, f"{base_filename}_результат.txt")
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for page_num, page_result in enumerate(results['pages'], 1):
                            f.write(f"\n--- Страница {page_num} ---\n")
                            f.write(page_result.get('text', ''))
                    
                    progress = (i + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                
                st.success(f"✅ Успешно обработан: {uploaded_file.name}")
                
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