import streamlit as st
import os
import tempfile
import logging
import json
from pathlib import Path
from src.converters.docx_converter import DocxConverter
from src.converters.pptx_converter import PptxConverter
from src.converters.html_converter import HtmlConverter
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
    '.htm': HtmlConverter()
}

# Set page config
st.set_page_config(page_title='Медицинский PDF Конвертер', layout='wide')

# Title
st.title('Медицинский Конвертер Документов')

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

# Add PDF format
supported_formats.add('pdf')

uploaded_files = st.file_uploader('', 
                                 type=list(supported_formats), 
                                 accept_multiple_files=True)

# Add output format selection
output_format = st.radio(
    'Выберите формат вывода:',
    ['TXT', 'HTML', 'JSON'],
    horizontal=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
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
                    result = converter.convert(tmp_path)
                    
                    # Create result files
                    base_name = Path(uploaded_file.name).stem
                    
                    if output_format == 'TXT':
                        # Save text result
                        output_file = f"{base_name}_результат.txt"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(result['text'])
                        
                        with open(output_file, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label=f"⬇️ Скачать TXT результат",
                                data=f.read(),
                                file_name=output_file,
                                mime='text/plain'
                            )
                    
                    elif output_format == 'HTML':
                        # Save HTML result with formatting
                        output_file = f"{base_name}_результат.html"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            # Create HTML with terms highlighting
                            html_content = result['text']
                            for term in result['terms']:
                                html_content = html_content.replace(
                                    term['term'],
                                    f'<span title="{term["definition"]}" '
                                    f'style="background-color: #e6f3ff;">{term["term"]}</span>'
                                )
                            
                            # Add tables if present
                            if result.get('tables'):
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
            os.unlink(output_file)

        except Exception as e:
            st.error(f'❌ Ошибка при обработке {uploaded_file.name}: {str(e)}')
            logger.error(f'Error processing {uploaded_file.name}: {str(e)}')

    st.success('🎉 Обработка завершена!')
