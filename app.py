import streamlit as st
import os
import tempfile
import logging
import json
from pathlib import Path
from src.converters.docx_converter import DocxConverter
from src.converters.pptx_converter import PptxConverter
from src.converters.html_converter import HtmlConverter
from src.converters.image_converter import ImageConverter
from src.converters.csv_converter import CsvConverter
from src.converters.xml_json_converter import XmlJsonConverter
from utils.system_check import verify_system_requirements

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize converters
converters = {
    '.docx': DocxConverter(),
    '.doc': DocxConverter(),
    '.pptx': PptxConverter(),
    '.ppt': PptxConverter(),
    '.html': HtmlConverter(),
    '.htm': HtmlConverter(),
    '.jpg': ImageConverter(),
    '.jpeg': ImageConverter(),
    '.png': ImageConverter(),
    '.tiff': ImageConverter(),
    '.bmp': ImageConverter(),
    '.csv': CsvConverter(),
    '.json': XmlJsonConverter(),
    '.xml': XmlJsonConverter()
}

# Cache dictionary loading
@st.cache_data
def load_cached_dictionary():
    from src.utils.medical_terms import load_medical_dictionary
    return load_medical_dictionary()

# Set page config
st.set_page_config(
    page_title='Медицинский Конвертер Документов',
    layout='wide'
)

# Title and description
st.title('Медицинский Конвертер Документов')
st.markdown("""Поддерживаемые форматы:
- 📄 Документы: DOCX, PDF
- 📃 Презентации: PPTX
- 🎨 Изображения: JPG, PNG, TIFF, BMP
- 📝 Текстовые форматы: CSV, JSON, XML, HTML""")

# System checks
st.header('Проверка конфигурации')

# Verify system requirements
system_ok, system_message = verify_system_requirements()

# Display results with proper formatting
for line in system_message.split('\n'):
    if '✓' in line:
        st.success(line)
    else:
        st.error(line)

if not system_ok:
    st.error('⚠️ Система не готова к работе. Пожалуйста, установите необходимые компоненты.')
    st.stop()

# File uploader
st.header('Выберите документы')

# Get supported file extensions
supported_formats = set()
for converter in converters.values():
    supported_formats.update(converter.get_supported_formats())

# Add output format selection with descriptions
st.subheader('Настройки конвертации')
col1, col2 = st.columns(2)

with col1:
    output_format = st.radio(
        'Выберите формат вывода:',
        ['TXT', 'HTML', 'JSON'],
        help='TXT - простой текст\nHTML - форматированный текст с подсветкой терминов\nJSON - структурированные данные'
    )

with col2:
    process_tables = st.checkbox(
        'Обрабатывать таблицы',
        value=True,
        help='Извлекать и форматировать таблицы из документов'
    )
    
    highlight_terms = st.checkbox(
        'Подсвечивать медицинские термины',
        value=True,
        help='Выделять и добавлять определения медицинских терминов'
    )

# File uploader
uploaded_files = st.file_uploader(
    '',
    type=list(supported_formats),
    accept_multiple_files=True
)

if uploaded_files:
    # Progress bar for multiple files
    progress_bar = st.progress(0)
    
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            # Update progress
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            
            # Get file extension
            file_ext = Path(uploaded_file.name).suffix.lower()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Get appropriate converter
            converter = converters.get(file_ext)
            
            if converter:
                # Process file
                with st.spinner(f'Обработка {uploaded_file.name}...'):
                    result = converter.convert(
                        tmp_path,
                        process_tables=process_tables,
                        extract_terms=highlight_terms
                    )
                    
                    # Create result files
                    base_name = Path(uploaded_file.name).stem
                    
                    if output_format == 'TXT':
                        output_file = f"{base_name}_результат.txt"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(result['text'])
                            if process_tables and result.get('tables'):
                                f.write('\n\nТАБЛИЦЫ:\n')
                                for table in result['tables']:
                                    for row in table:
                                        f.write('\t'.join(str(cell) for cell in row) + '\n')
                                    f.write('\n')
                        
                        with open(output_file, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label=f"⬇️ Скачать TXT результат",
                                data=f.read(),
                                file_name=output_file,
                                mime='text/plain'
                            )
                    
                    elif output_format == 'HTML':
                        output_file = f"{base_name}_результат.html"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            html_content = result['text']
                            
                            if highlight_terms:
                                for term in result['terms']:
                                    html_content = html_content.replace(
                                        term['term'],
                                        f'<span title="{term["definition"]}" '
                                        f'style="background-color: #e6f3ff;">{term["term"]}</span>'
                                    )
                            
                            if process_tables and result.get('tables'):
                                html_content += '\n<h2>Таблицы:</h2>\n'
                                for table in result['tables']:
                                    html_content += '\n<table border="1">\n'
                                    for row in table:
                                        html_content += '<tr>'
                                        for cell in row:
                                            html_content += f'<td>{cell}</td>'
                                        html_content += '</tr>\n'
                                    html_content += '</table>\n'
                            
                            f.write(f"""<html>
                            <head>
                                <meta charset="utf-8">
                                <style>
                                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                    table {{ border-collapse: collapse; margin: 10px 0; }}
                                    td, th {{ padding: 8px; }}
                                </style>
                            </head>
                            <body>{html_content}</body>
                            </html>""")
                        
                        with open(output_file, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label=f"⬇️ Скачать HTML результат",
                                data=f.read(),
                                file_name=output_file,
                                mime='text/html'
                            )
                    
                    else:  # JSON
                        output_file = f"{base_name}_результат.json"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            # Filter results based on user settings
                            if not process_tables:
                                result.pop('tables', None)
                            if not highlight_terms:
                                result.pop('terms', None)
                            
                            json.dump(result, f, ensure_ascii=False, indent=2)
                        
                        with open(output_file, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label=f"⬇️ Скачать JSON результат",
                                data=f.read(),
                                file_name=output_file,
                                mime='application/json'
                            )

                # Success message
                st.success(f'✅ {uploaded_file.name} обработан успешно!')

            # Cleanup
            os.unlink(tmp_path)
            if 'output_file' in locals():
                os.unlink(output_file)

        except Exception as e:
            st.error(f'❌ Ошибка при обработке {uploaded_file.name}: {str(e)}')
            logger.error(f'Error processing {uploaded_file.name}: {str(e)}')
            continue

    st.success('🎉 Обработка завершена!')
    
# Footer
st.markdown('---')
st.markdown("""
<div style='text-align: center'>
    <p>Разработано для обработки медицинской документации</p>
    <p>Поддержка: @Turayev_Temur | temurturayev7822@gmail.com</p>
</div>
""", unsafe_allow_html=True)