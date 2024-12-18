import cv2
import numpy as np

def enhance_russian_text(image):
    """
    Улучшает качество распознавания русского текста
    """
    # 1. Предварительная обработка изображения
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # 2. Увеличение контраста
    img = cv2.equalizeHist(img)
    
    # 3. Удаление шума
    img = cv2.medianBlur(img, 3)
    
    # 4. Увеличение размера для лучшего распознавания
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    return img

def apply_advanced_preprocessing(image):
    """
    Применяет расширенную предобработку для сложных изображений
    """
    # 1. Денойзинг
    denoised = cv2.fastNlMeansDenoisingColored(image)
    
    # 2. Улучшение четкости
    kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    # 3. Адаптивная бинаризация
    gray = cv2.cvtColor(sharpened, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    return binary