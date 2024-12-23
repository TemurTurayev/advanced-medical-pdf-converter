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

# Add the project root directory to Python path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from processor import DocumentProcessor

st.set_page_config(
    page_title="Медицинский Документ Конвертер",
    page_icon="🏥",
    layout="wide"
)

st.title("Медицинский Документ Конвертер")

# Проверка настроек
with st.expander("Проверка конфигурации"):
    # Проверка Poppler
    try:
        from pdf2image.pdf2image import get_poppler_path
        if get_poppler_path() is not None:
            st.success("✅ Poppler найден")
    except Exception:
        st.error("❌ Poppler не найден")
    
    # Проверка Tesseract
    try:
        pytesseract.get_tesseract_version()
        st.success("✅ Tesseract найден")
    except Exception:
        st.error("❌ Tesseract не найден")

    # Проверка дополнительного ПО
    missing_software = []
    try:
        import win32com.client
    except ImportError:
        missing_software.append("Microsoft Office")
    
    try:
        import djvu
    except ImportError:
        missing_software.append("DjVuLibre")
    
    if missing_software:
        st.warning("⚠️ Некоторые форматы могут быть недоступны. Отсутствует ПО:")
        for software in missing_software:
            st.warning(f"• {software}")

# Инициализация процессора документов
processor = DocumentProcessor()

# Загрузка файлов
uploaded_files = st.file_uploader(
    "Выберите файлы для конвертации",
    accept_multiple_files=True,
    type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'djvu', 'jpg', 'jpeg', 'png', 'tiff']
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.write(f"Обработка файла {uploaded_file.name}")
        
        # Создание временного файла
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Обработка файла
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress: float, status: str):
                progress_bar.progress(progress)
                status_text.text(status)
            
            with open(tmp_file_path, 'rb') as f:
                file_data = f.read()
                results = processor.process_document(
                    file_data,
                    uploaded_file.name.split('.')[-1].lower(),
                    update_progress
                )
            
            # Отображение результатов
            if results and results.get('pages'):
                st.success(f"✅ Успешно обработан: {uploaded_file.name}")
                
                # Подготовка текста для скачивания
                output_text = ""
                for i, page in enumerate(results['pages'], 1):
                    output_text += f"\n--- Страница {i} ---\n{page['text']}\n"
                
                # Кнопка скачивания
                st.download_button(
                    f"⬇️ Скачать результат для {uploaded_file.name}",
                    output_text,
                    file_name=f"converted_{uploaded_file.name}.txt",
                    mime='text/plain'
                )
            
        except Exception as e:
            st.error(f"❌ Ошибка при обработке {uploaded_file.name}: {str(e)}")
        
        finally:
            # Очистка временных файлов
            try:
                os.unlink(tmp_file_path)
            except:
                pass
            
            # Очистка индикаторов прогресса
            progress_bar.empty()
            status_text.empty()