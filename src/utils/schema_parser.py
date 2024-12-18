import cv2
import numpy as np
from .schema_detector import extract_schema_features, classify_schema

def detect_blocks(image):
    """
    Обнаруживает блоки на схеме
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Находим контуры
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    blocks = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 100:  # Фильтруем маленькие контуры
            blocks.append({'x': x, 'y': y, 'width': w, 'height': h})
    
    return blocks

def detect_connections(image):
    """
    Обнаруживает связи между блоками
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    
    connections = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        connections.append({'start': (x1, y1), 'end': (x2, y2)})
    
    return connections

def parse_schema(image, schema_type):
    """
    Парсит схему в зависимости от её типа
    """
    if schema_type == 'flowchart':
        blocks = detect_blocks(image)
        connections = detect_connections(image)
        return {'type': 'flowchart', 'blocks': blocks, 'connections': connections}
    
    elif schema_type == 'table':
        # Извлечение таблицы
        return {'type': 'table', 'cells': parse_table(image)}
    
    elif schema_type == 'hierarchy':
        # Извлечение иерархии
        return {'type': 'hierarchy', 'nodes': parse_hierarchy(image)}
    
    return None