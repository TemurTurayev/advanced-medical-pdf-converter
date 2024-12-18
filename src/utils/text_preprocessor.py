import cv2
import numpy as np
from typing import Dict, List, Tuple

def enhance_image_quality(image):
    """
    Улучшает качество изображения для OCR
    """
    # Преобразование в grayscale с улучшенным контрастом
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Удаление шума и улучшение четкости
    denoised = cv2.fastNlMeansDenoising(enhanced)
    kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    return sharpened

def detect_text_regions(image):
    """
    Определяет области с текстом на изображении
    """
    # Бинаризация
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Поиск контуров текстовых областей
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    regions = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 20 and h > 20:  # Фильтруем слишком маленькие области
            regions.append((x, y, w, h))
    
    return regions

def process_text_block(image, region):
    """
    Обрабатывает отдельный текстовый блок
    """
    x, y, w, h = region
    roi = image[y:y+h, x:x+w]
    
    # Увеличение размера для лучшего распознавания
    scale = 2.0
    roi = cv2.resize(roi, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Дополнительная обработка для улучшения качества
    _, roi = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return roi

def format_text_output(text: str) -> str:
    """
    Форматирует распознанный текст
    """
    # Удаляем лишние пробелы и переносы строк
    text = ' '.join(text.split())
    
    # Исправляем распространенные ошибки распознавания
    replacements = {
        'rn': 'м',
        '|': 'l',
        '[': '(',
        ']': ')',
        '{': '(',
        '}': ')',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Восстанавливаем структуру документа
    lines = text.split('\n')
    formatted_lines = []
    current_section = None
    
    for line in lines:
        # Определяем заголовки и секции
        if line.isupper():
            current_section = line
            formatted_lines.extend(['', line, ''])
        elif line.strip() and current_section:
            formatted_lines.append('  ' + line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)