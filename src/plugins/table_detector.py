from .base import BasePlugin
from typing import Dict, List
import cv2
import numpy as np

class TableDetectorPlugin(BasePlugin):
    def process(self, content: np.ndarray, context: Dict = None) -> Dict:
        gray = cv2.cvtColor(content, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is None:
            return {'tables': []}
        
        tables = self._detect_tables(lines)
        return {'tables': tables}
    
    def _detect_tables(self, lines) -> List[Dict]:
        tables = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Table detection logic
            if abs(x2 - x1) > 100 and abs(y2 - y1) > 100:
                tables.append({
                    'x1': int(x1),
                    'y1': int(y1),
                    'x2': int(x2),
                    'y2': int(y2)
                })
        return tables