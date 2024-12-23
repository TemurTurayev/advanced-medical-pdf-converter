import gc
import os
import numpy as np
from datetime import datetime
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import streamlit as st
from typing import Dict, List
from src.errors import ProcessingError
from src.plugin_manager import PluginManager
from time import sleep
import win32com.client
import subprocess
from pathlib import Path
import tempfile

class DocumentProcessor:
    def __init__(self):
        self.plugin_manager = PluginManager()
        self.word = None
        self.powerpoint = None
        self.temp_dir = Path(tempfile.mkdtemp())

    def cleanup(self):
        try:
            # Очистка временных файлов
            if self.temp_dir.exists():
                for file in self.temp_dir.glob('*'):
                    try:
                        file.unlink()
                    except:
                        pass
                self.temp_dir.rmdir()
        except:
            pass

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

    def process_pdf_in_chunks(self, pdf_path: str, first_page: int, last_page: int) -> List[dict]:
        try:
            # Конвертируем только указанный диапазон страниц
            images = convert_from_path(
                pdf_path,
                first_page=first_page,
                last_page=last_page,
                dpi=150,
                thread_count=2,
                grayscale=True,
                size=(800, None),
                fmt='png',  # Используем PNG для лучшего качества
                output_folder=str(self.temp_dir),  # Сохраняем во временную директорию
                paths_only=True  # Возвращаем только пути к файлам
            )
            
            results = []
            for img_path in images:
                try:
                    # Загружаем и обрабатываем одно изображение
                    with Image.open(img_path) as img:
                        img = img.convert('L')
                        img = img.point(lambda p: p > 127 and 255)
                        
                        text = pytesseract.image_to_string(
                            img,
                            lang='eng+rus',
                            config='--psm 6 --oem 3 -c tessedit_do_invert=0'
                        )
                        
                        # Обработка текста плагинами
                        processed_text = text
                        for plugin in self.plugin_manager.get_plugins():
                            try:
                                processed_text = plugin.process_text(processed_text)
                            except Exception as e:
                                st.warning(f'Ошибка плагина {plugin.__class__.__name__}: {str(e)}')
                        
                        results.append({'text': processed_text})
                finally:
                    # Удаляем временный файл изображения
                    try:
                        Path(img_path).unlink()
                    except:
                        pass
            
            return results
        except Exception as e:
            raise ProcessingError(f'Ошибка обработки страниц {first_page}-{last_page}: {str(e)}')

    def process_large_pdf(self, file_path: str, chunk_size: int = 10) -> Dict:
        try:
            # Создаем контейнеры для отображения прогресса
            status_text = st.empty()
            progress_bar = st.progress(0)
            chunk_progress = st.empty()
            
            # Получаем общее количество страниц
            from pdf2image.pdf2image import pdfinfo_from_path
            pdf_info = pdfinfo_from_path(file_path)
            total_pages = pdf_info['Pages']
            
            status_text.text(f'Найдено страниц: {total_pages}')
            all_results = []
            
            # Обрабатываем PDF по частям
            for start_page in range(1, total_pages + 1, chunk_size):
                end_page = min(start_page + chunk_size - 1, total_pages)
                
                chunk_progress.text(f'Обработка страниц {start_page}-{end_page} из {total_pages}')
                
                # Обрабатываем текущую порцию страниц
                chunk_results = self.process_pdf_in_chunks(file_path, start_page, end_page)
                all_results.extend(chunk_results)
                
                # Обновляем прогресс
                progress = len(all_results) / total_pages
                progress_bar.progress(progress)
                
                # Принудительно очищаем память
                gc.collect()
                sleep(0.1)  # Небольшая пауза для обновления UI
            
            status_text.text('Обработка завершена!')
            progress_bar.progress(1.0)
            chunk_progress.empty()
            
            return {
                'pages': all_results,
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_pages': total_pages,
                    'optimization': 'chunk_processing'
                }
            }
        except Exception as e:
            raise ProcessingError(f'Ошибка обработки PDF: {str(e)}')
        finally:
            self.cleanup()

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