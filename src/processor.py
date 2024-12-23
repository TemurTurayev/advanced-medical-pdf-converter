import gc
import numpy as np
from datetime import datetime
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import streamlit as st

class DocumentProcessor:
    def process_large_pdf(self, file_path: str, batch_size: int = 10) -> Dict:
        try:
            # Конвертируем PDF в изображения с оптимизацией памяти
            images = convert_from_path(
                file_path,
                dpi=200,  # Уменьшаем DPI для ускорения
                thread_count=4,  # Многопоточная обработка
                grayscale=True,  # Черно-белый режим для уменьшения размера
                size=(1000, None)  # Ограничиваем ширину, сохраняя пропорции
            )
            
            total_pages = len(images)
            results = []
            
            # Обрабатываем частями для экономии памяти
            for i in range(0, total_pages, batch_size):
                batch = images[i:i + batch_size]
                batch_results = []
                
                for img in batch:
                    # Оптимизируем изображение перед OCR
                    img = Image.fromarray(np.array(img))
                    img = img.convert('L')  # Преобразуем в оттенки серого
                    
                    # Применяем пороговую обработку для улучшения контраста
                    threshold = 127
                    img = img.point(lambda p: p > threshold and 255)
                    
                    # Выполняем OCR с оптимизированными параметрами
                    text = pytesseract.image_to_string(
                        img,
                        lang='eng+rus',
                        config='--psm 6 --oem 3'  # Оптимизированные параметры OCR
                    )
                    
                    batch_results.append({'text': text})
                    
                    # Очищаем память
                    del img
                
                results.extend(batch_results)
                
                # Очищаем память после обработки пакета
                del batch
                gc.collect()
                
                # Обновляем прогресс
                progress = (i + len(batch_results)) / total_pages
                st.progress(progress)
                
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
            if file_type == 'pdf':
                # Проверяем размер файла
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # В МБ
                if file_size > 10:  # Если файл больше 10 МБ
                    st.info(f"Обрабатывается большой файл ({file_size:.1f} МБ). Это может занять некоторое время...")
                    return self.process_large_pdf(file_path)
                else:
                    # Обычная обработка для небольших файлов
                    images = convert_from_path(file_path)
                    text_parts = []
                    for image in images:
                        text = pytesseract.image_to_string(image, lang='eng+rus')
                        text_parts.append(text)
                    results = [{'text': text} for text in text_parts]
                    
                return {
                    'pages': results,
                    'metadata': {
                        'processed_at': datetime.now().isoformat(),
                        'total_pages': len(results)
                    }
                }