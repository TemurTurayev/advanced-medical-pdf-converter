import cv2
import numpy as np
from sklearn.cluster import DBSCAN

def extract_schema_features(image):
    """
    Извлекает характеристики схемы
    """
    # 1. Обнаружение линий
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    
    # 2. Обнаружение текстовых блоков
    mser = cv2.MSER_create()
    regions, _ = mser.detectRegions(gray)
    
    # 3. Анализ расположения элементов
    features = {
        'vertical_lines': len([l for l in lines if abs(l[0][2] - l[0][0]) < 5]),
        'horizontal_lines': len([l for l in lines if abs(l[0][3] - l[0][1]) < 5]),
        'text_regions': len(regions)
    }
    
    return features

def classify_schema(features):
    """
    Классифицирует тип схемы на основе характеристик
    """
    if features['horizontal_lines'] > features['vertical_lines'] * 1.5:
        return 'table'
    elif features['vertical_lines'] > features['horizontal_lines'] * 1.5:
        return 'hierarchy'
    else:
        return 'flowchart'