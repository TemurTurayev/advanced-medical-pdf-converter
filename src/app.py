import streamlit as st
import os
from config import CONFIG
from utils.progress_tracker import ProgressTracker
from processors.pdf_processor import PDFProcessor
from processors.document_processor import DocumentProcessor
from processors.image_processor import ImageProcessor

st.set_page_config(
    page_title="Медицинский Документ Конвертер",
    page_icon="🏥",
    layout="wide"
)

st.title("Медицинский Документ Конвертер")

def check_software():
    """Check required software availability"""
    with st.expander("Проверка конфигурации"):
        all_available = True
        for software, details in CONFIG['REQUIRED_SOFTWARE'].items():
            try:
                result = os.system(details['check_command'] + " > /dev/null 2>&1")
                if result == 0:
                    st.success(f"{details['name']} найден")
                else:
                    st.warning(f"{details['name']} не найден - {details['install_guide']}")
                    all_available = False
            except:
                st.warning(f"{details['name']} не найден - {details['install_guide']}")
                all_available = False
        
        if not all_available:
            st.warning("⚠️ Некоторые форматы могут быть недоступны. Отсутствует ПО:")

def process_file(uploaded_file, progress_tracker):
    """Process uploaded file with progress tracking"""
    try:
        file_size = uploaded_file.size
        if file_size > CONFIG['MAX_FILE_SIZE']:
            st.error(f"Файл слишком большой. Максимальный размер: {CONFIG['MAX_FILE_SIZE'] // (1024*1024)}MB")
            return False

        # Determine processor based on file type
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension in ['pdf']:
            processor = PDFProcessor()
        elif file_extension in ['doc', 'docx', 'ppt', 'pptx']:
            processor = DocumentProcessor()
        elif file_extension in ['jpg', 'jpeg', 'png', 'tiff']:
            processor = ImageProcessor()
        else:
            st.error("Неподдерживаемый формат файла")
            return False

        # Process file with progress tracking
        result = processor.process(uploaded_file, progress_tracker)
        return result

    except Exception as e:
        st.error(f"Ошибка при обработке файла: {str(e)}")
        return False

def main():
    check_software()

    # File uploader
    uploaded_files = st.file_uploader(
        "Выберите файлы для конвертации",
        accept_multiple_files=True,
        type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'djvu', 'jpg', 'jpeg', 'png', 'tiff'],
        help=f"Лимит 200MB на файл • DOC, DOCX, PPT, PPTX, PDF, DJVU, HTML, HTM, XML, JSON, CSV, JPG, JPEG, PNG, TIFF, TIF, BMP"
    )

    if uploaded_files:
        for i, file in enumerate(uploaded_files, 1):
            st.write(f"Обработка файла {i}/{len(uploaded_files)}")
            
            # Create progress tracker for this file
            progress_tracker = ProgressTracker(100, f"Обработка файла {file.name}")
            
            # Process file
            success = process_file(file, progress_tracker)
            
            # Update progress
            if success:
                st.success(f"✅ Успешно обработан: {file.name}")
                download_button = st.download_button(
                    f"⬇️ Скачать результат для {file.name}",
                    data=success,
                    file_name=f"processed_{file.name}",
                    mime="application/octet-stream"
                )
            else:
                st.error(f"❌ Ошибка при обработке: {file.name}")

if __name__ == "__main__":
    main()