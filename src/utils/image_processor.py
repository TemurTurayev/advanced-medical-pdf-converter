import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict

class ImageProcessor:
    """Class for image processing and enhancement"""
    
    @staticmethod
    def enhance_image(image: Image.Image) -> Image.Image:
        """Enhance image for better OCR results"""
        # Convert PIL Image to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        threshold = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(threshold)
        
        # Convert back to PIL Image
        return Image.fromarray(denoised)
    
    @staticmethod
    def detect_orientation(image: Image.Image) -> float:
        """Detect image orientation angle"""
        # Convert to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            angles = []
            for line in lines:
                rho, theta = line[0]
                angle = theta * 180 / np.pi
                angles.append(angle)
            
            # Get the most common angle
            angle_counts = np.bincount(np.array(angles).astype(int))
            most_common_angle = np.argmax(angle_counts)
            
            # Normalize angle
            if most_common_angle > 45:
                most_common_angle = most_common_angle - 90
            
            return most_common_angle
        
        return 0.0
    
    @staticmethod
    def fix_orientation(image: Image.Image) -> Image.Image:
        """Fix image orientation"""
        angle = ImageProcessor.detect_orientation(image)
        if abs(angle) > 0.5:
            return image.rotate(angle, expand=True)
        return image
    
    @staticmethod
    def detect_layout(image: Image.Image) -> Dict[str, List[Tuple[int, int, int, int]]]:
        """Detect document layout (text regions, images, tables)"""
        # Convert to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Initialize results dictionary
        layout = {
            'text_regions': [],
            'images': [],
            'tables': []
        }
        
        # Detect text regions using MSER
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        # Merge nearby regions
        for region in regions:
            x, y, w, h = cv2.boundingRect(region)
            area = w * h
            aspect_ratio = w / float(h)
            
            if area > 100 and 0.1 < aspect_ratio < 10:
                layout['text_regions'].append((x, y, x+w, y+h))
        
        # Detect tables using line detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is not None:
            intersections = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                for other_line in lines:
                    x3, y3, x4, y4 = other_line[0]
                    if abs(x1 - x3) < 10 and abs(y1 - y3) < 10:
                        intersections.append((x1, y1))
            
            if len(intersections) > 4:
                x_coords = [x for x, y in intersections]
                y_coords = [y for x, y in intersections]
                x1, y1 = min(x_coords), min(y_coords)
                x2, y2 = max(x_coords), max(y_coords)
                layout['tables'].append((x1, y1, x2, y2))
        
        return layout