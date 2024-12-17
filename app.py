import streamlit as st
import os
import tempfile
from pdf2image import convert_from_path
import pytesseract
import logging
from utils.system_check import verify_system_requirements

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(page_title='Медицинский PDF Конвертер', layout='wide')

# Title
st.title('Медицинский PDF Конвертер')

# System checks
st.header('Проверка конфигурации')

# Verify system requirements
system_ok, system_message = verify_system_requirements()

# Display results with proper formatting
for line in system_message.split('\n'):
    if '✓' in line:  # Check mark
        st.success(line)
    else:
        st.error(line)

if not system_ok:
    st.error('⚠️ Система не готова к работе. Пожалуйста, установите необходимые компоненты.')
    st.stop()

# File uploader
st.header('Выберите PDF файлы')
uploaded_files = st.file_uploader('', type=['pdf'], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Convert PDF to images
            images = convert_from_path(tmp_path)
            
            # Create result file name
            base_name = os.path.splitext(uploaded_file.name)[0]
            result_file = f"{base_name}_результат.txt"

            # Process each page
            with st.spinner(f'Обработка {uploaded_file.name}...'):
                with open(result_file, 'w', encoding='utf-8') as f:
                    for i, image in enumerate(images):
                        text = pytesseract.image_to_string(image, lang='rus+eng')
                        f.write(f'\n--- Страница {i+1} ---\n{text}')

            # Success message
            st.success(f'✅ {uploaded_file.name} обработан успешно!')

            # Download button
            with open(result_file, 'r', encoding='utf-8') as f:
                st.download_button(
                    label=f"⬇️ Скачать результат для {uploaded_file.name}",
                    data=f.read(),
                    file_name=result_file,
                    mime='text/plain'
                )

            # Cleanup
            os.unlink(tmp_path)
            os.unlink(result_file)

        except Exception as e:
            st.error(f'❌ Ошибка при обработке {uploaded_file.name}: {str(e)}')
            logger.error(f'Error processing {uploaded_file.name}: {str(e)}')

    st.success('🎉 Обработка завершена!')
