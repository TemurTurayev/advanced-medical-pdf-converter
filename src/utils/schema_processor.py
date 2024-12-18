import cv2
import numpy as np
from typing import Dict, List, Tuple

def detect_schema_type(image) -> str:
    """
    Определяет тип схемы на изображении
    """
    # Поиск линий
    edges = cv2.Canny(image, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    
    # Анализ ориентации линий
    horizontal = 0
    vertical = 0
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x2 - x1) > abs(y2 - y1):
                horizontal += 1
            else:
                vertical += 1
    
    # Определение типа схемы
    if horizontal > vertical * 1.5:
        return 'table'
    elif vertical > horizontal * 1.5:
        return 'hierarchy'
    else:
        return 'flowchart'

def process_table(image):
    """
    Обрабатывает табличную схему
    """
    # Обнаружение ячеек таблицы
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Поиск контуров ячеек
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Сортировка ячеек по позиции
    cells = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 100:  # Фильтруем маленькие контуры
            cells.append((x, y, w, h))
    
    cells.sort(key=lambda x: (x[1], x[0]))  # Сортировка по y, затем по x
    
    return cells

def process_hierarchy(image):
    """
    Обрабатывает иерархическую схему
    """
    # Обнаружение блоков и связей
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Поиск блоков
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Анализ иерархии
    nodes = []
    for i, cnt in enumerate(contours):
        if hierarchy[0][i][3] == -1:  # Только родительские узлы
            x, y, w, h = cv2.boundingRect(cnt)
            if w * h > 100:
                nodes.append({
                    'coords': (x, y, w, h),
                    'level': 0
                })
    
    return nodes

def format_schema_output(schema_type: str, elements: List) -> Dict:
    """
    Форматирует выход для схемы
    """
    return {
        'type': schema_type,
        'elements': elements,
        'structure': 'table' if schema_type == 'table' else 'tree'
    }