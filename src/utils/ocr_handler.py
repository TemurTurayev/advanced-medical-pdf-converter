import pytesseract
from .text_preprocessing import enhance_russian_text, apply_advanced_preprocessing
import difflib

def select_best_result(results):
    """
    Выбирает лучший результат OCR из нескольких вариантов
    """
    if not results:
        return ""
    
    # Используем длину текста и количество русских символов как метрики
    def score_text(text):
        russian_chars = sum(1 for c in text if 'а' <= c.lower() <= 'я')
        return len(text) * 0.3 + russian_chars * 0.7
    
    return max(results, key=score_text)

def improve_russian_ocr(image):
    """
    Улучшенное OCR для русского текста
    """
    # 1. Настройка Tesseract для русского языка
    custom_config = r'--oem 3 --psm 6 -l rus+eng'
    
    # 2. Предварительная обработка
    preprocessed_img = enhance_russian_text(image)
    advanced_preprocessed = apply_advanced_preprocessing(image)
    
    # 3. Множественное распознавание с разными параметрами
    results = []
    for img in [preprocessed_img, advanced_preprocessed]:
        for psm in [6, 3, 4]:
            config = f'--oem 3 --psm {psm} -l rus+eng'
            text = pytesseract.image_to_string(img, config=config)
            results.append(text)
    
    # 4. Выбор лучшего результата
    return select_best_result(results)