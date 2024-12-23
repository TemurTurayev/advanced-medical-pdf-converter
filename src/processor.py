import gc
import os
import numpy as np
from datetime import datetime
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import streamlit as st
from typing import Dict
from src.errors import ProcessingError
from src.plugin_manager import PluginManager
from time import sleep
import win32com.client
import subprocess

class DocumentProcessor:
    def __init__(self):
        self.plugin_manager = PluginManager()
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

    def convert_doc(self, file_path: str) -> str:
        try:
            if not self.word:
                self.word = win32com.client.Dispatch('Word.Application')
                self.word.Visible = False
            
            doc = self.word.Documents.Open(file_path)
            text = doc.Content.Text
            doc.Close()
            return text
        except Exception as e:
            raise ProcessingError(f'Ошибка конвертации DOC файла: {str(e)}')

    def convert_ppt(self, file_path: str) -> str:
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
            return '\n'.join(text_parts)
        except Exception as e:
            raise ProcessingError(f'Ошибка конвертации PPT файла: {str(e)}')

    def convert_djvu(self, file_path: str) -> str:
        try:
            pdf_path = file_path.rsplit('.', 1)[0] + '.pdf'
            subprocess.run(['ddjvu', '-format=pdf', file_path, pdf_path], check=True)
            
            images = convert_from_path(pdf_path)
            text_parts = []
            for image in images:
                text = pytesseract.image_to_string(image, lang='eng+rus')
                text_parts.append(text)
            
            os.unlink(pdf_path)
            return '\n\n'.join(text_parts)
        except subprocess.CalledProcessError as e:
            raise ProcessingError(f'Ошибка конвертации DJVU файла: {str(e)}')
        except Exception as e:
            raise ProcessingError(f'Ошибка обработки DJVU файла: {str(e)}')

    def process_large_pdf(self, file_path: str, batch_size: int = 5) -> Dict:
        try:
            # Создаем контейнеры для отображения прогресса
            progress_text = st.empty()
            progress_bar = st.progress(0)
            page_progress = st.empty()
            memory_status = st.empty()
            
            progress_text.text('Подготовка к обработке PDF...')
            
            # Конвертируем PDF в изображения с оптимизацией памяти
            images = convert_from_path(
                file_path,
                dpi=150,  # Уменьшаем DPI для ускорения
                thread_count=2,  # Меньше потоков для экономии памяти
                grayscale=True,  # Черно-белый режим
                size=(800, None)  # Меньше разрешение
            )
            
            total_pages = len(images)
            results = []
            progress_text.text('Начало обработки страниц...')
            
            for i in range(0, total_pages, batch_size):
                batch = images[i:i + batch_size]
                batch_results = []
                
                # Информация о прогрессе
                current_page = i + 1
                page_progress.text(f'Обработка страниц: {current_page}-{min(i + batch_size, total_pages)} из {total_pages}')
                
                for img_num, img in enumerate(batch, 1):
                    # Оптимизация изображения
                    img = Image.fromarray(np.array(img))
                    img = img.convert('L')
                    
                    # Улучшение контраста
                    img = img.point(lambda p: p > 127 and 255)
                    
                    progress_text.text(f'Распознавание текста на странице {current_page + img_num - 1}...')
                    
                    # OCR с оптимизированными настройками
                    try:
                        text = pytesseract.image_to_string(
                            img,
                            lang='eng+rus',
                            config='--psm 6 --oem 3 -c tessedit_do_invert=0'
                        )
                    except Exception as e:
                        st.error(f'Ошибка OCR на странице {current_page + img_num - 1}: {str(e)}')
                        text = ''

                    # Обработка текста плагинами
                    processed_text = text
                    for plugin in self.plugin_manager.get_plugins():
                        try:
                            processed_text = plugin.process_text(processed_text)
                        except Exception as e:
                            st.warning(f'Ошибка плагина {plugin.__class__.__name__}: {str(e)}')
                    
                    batch_results.append({'text': processed_text})
                    del img  # Очищаем память
                
                results.extend(batch_results)
                del batch
                gc.collect()
                
                # Обновляем прогресс
                progress = (i + len(batch_results)) / total_pages
                progress_bar.progress(progress)
                sleep(0.1)  # Небольшая пауза для обновления UI
            
            # Завершение
            progress_text.text('Обработка завершена!')
            progress_bar.progress(1.0)
            page_progress.empty()
            memory_status.empty()
            
            return {
                'pages': results,
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_pages': total_pages,
                    'optimization': 'batch_processing'
                }
            }
        except Exception as e:
            raise ProcessingError(f'Ошибка обработки PDF: {str(e)}')
    
    def process_document(self, file_path: str, file_type: str) -> Dict:
        try:
            file_type = file_type.lower()
            
            if file_type == 'pdf':
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # В МБ
                st.info(f'Размер файла: {file_size:.1f} МБ')
                return self.process_large_pdf(file_path)
            
            elif file_type == 'doc':
                text = self.convert_doc(file_path)
                return {
                    'pages': [{'text': text}],
                    'metadata': {
                        'processed_at': datetime.now().isoformat(),
                        'total_pages': 1
                    }
                }
            
            elif file_type == 'ppt':
                text = self.convert_ppt(file_path)
                return {
                    'pages': [{'text': text}],
                    'metadata': {
                        'processed_at': datetime.now().isoformat(),
                        'total_pages': 1
                    }
                }
            
            elif file_type == 'djvu':
                text = self.convert_djvu(file_path)
                return {
                    'pages': [{'text': text}],
                    'metadata': {
                        'processed_at': datetime.now().isoformat(),
                        'total_pages': 1
                    }
                }
            
            else:
                raise ProcessingError(f'Неподдерживаемый формат файла: {file_type}')
        except Exception as e:
            raise ProcessingError(f'Ошибка обработки документа: {str(e)}')
        finally:
            self.cleanup()