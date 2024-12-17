from typing import List, Any, Union
from PIL import Image
import cv2
import numpy as np

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
            
            # Extract text from cells
            table_data = []
            current_row = []
            last_y = 0
            
            # Sort contours by Y coordinate first, then X
            sorted_cells = sorted(cell_contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
            
            for cell in sorted_cells:
                x, y, w, h = cv2.boundingRect(cell)
                
                # If this cell is on a new row
                if abs(y - last_y) > 20:  # threshold for new row
                    if current_row:
                        table_data.append(current_row)
                    current_row = []
                    last_y = y
                
                current_row.append('')  # Placeholder for text
                
            # Don't forget the last row
            if current_row:
                table_data.append(current_row)
                
            if table_data:
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

def extract_tables(source: Union[Image.Image, List[Any], Any]) -> List[List[List[str]]]:
    """Extract tables from different types of sources
    
    Args:
        source: Can be:
            - PIL Image object for image-based extraction
            - List of HTML table elements for HTML extraction
            - Document object for document-specific extraction
            
    Returns:
        List of tables, where each table is a list of rows,
        and each row is a list of cell values
    """
    if isinstance(source, Image.Image):
        return extract_tables_from_image(source)
    elif isinstance(source, list):
        return extract_tables_from_html(source)
    else:
        # Try to extract tables based on document type
        if hasattr(source, 'tables'):
            tables = []
            for table in source.tables:
                table_data = []
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        row_data.append(cell.text.strip())
                    table_data.append(row_data)
                tables.append(table_data)
            return tables
        return []