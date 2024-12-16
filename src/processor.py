import cv2
import numpy as np
import pytesseract
from typing import List, Dict
import re
from PIL import Image

class MedicalImageProcessor:
    @staticmethod
    def detect_tables(image: np.ndarray) -> List[Dict]:
        """Detects tables in the image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, 
                               minLineLength=100, maxLineGap=10)
        [... rest of the code ...]