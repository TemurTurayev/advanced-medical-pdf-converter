from typing import List, Any
import cv2
import numpy as np
from PIL import Image

def extract_tables_from_image(image: Image.Image) -> List[List[List[str]]]:
    """Extract tables from image using OpenCV
    
    Args:
        image: PIL Image object
        
    Returns:
        List of tables, where each table is a list of rows,
        and each row is a list of cell values
    """
    # Convert PIL image to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect lines
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    
    # Detect table grid
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, 
                                    cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1)))
    contours = cv2.findContours(detected_lines, cv2.RETR_TREE, 
                               cv2.CHAIN_APPROX_SIMPLE)[0]
    
    tables = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:  # Filter small contours
            # Get table boundaries
            x, y, w, h = cv2.boundingRect(cnt)
            table_img = thresh[y:y+h, x:x+w]
            
            # Find cells in table
            cell_contours = cv2.findContours(table_img, cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)[0]
            
            # Extract text from cells using Tesseract
            table_data = []
            for cell in sorted(cell_contours, key=lambda c: (c[0][0][1], c[0][0][0])):
                cell_x, cell_y, cell_w, cell_h = cv2.boundingRect(cell)
                cell_img = Image.fromarray(table_img[cell_y:cell_y+cell_h,
                                                   cell_x:cell_x+cell_w])
                # TODO: Add text extraction from cell using Tesseract
                table_data.append('')
                
            tables.append(table_data)
            
    return tables

def extract_tables_from_html(html_tables: List[Any]) -> List[List[List[str]]]:
    """Extract tables from HTML table elements
    
    Args:
        html_tables: List of HTML table elements
        
    Returns:
        List of tables in normalized format
    """
    tables = []
    for table in html_tables:
        table_data = []
        for row in table.find_all('tr'):
            row_data = []
            for cell in row.find_all(['td', 'th']):
                row_data.append(cell.get_text(strip=True))
            table_data.append(row_data)
        tables.append(table_data)
    return tables