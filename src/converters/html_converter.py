from bs4 import BeautifulSoup
from typing import Dict, Any
import requests
from .base_converter import BaseConverter
from ..utils.medical_terms import extract_medical_terms
from ..utils.table_extractor import extract_tables

class HtmlConverter(BaseConverter):
    """Converter for HTML documents"""

    def convert(self, file_path: str, **kwargs) -> Dict[str, Any]:
        # Handle both local files and URLs
        if file_path.startswith('http'):
            response = requests.get(file_path)
            html_content = response.text
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text(separator='\n')
        
        # Extract tables
        tables = []
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                table_data.append(row_data)
            tables.append(table_data)
        
        # Extract metadata
        metadata = {
            'title': soup.title.string if soup.title else None,
            'meta_description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else None,
            'meta_keywords': soup.find('meta', {'name': 'keywords'})['content'] if soup.find('meta', {'name': 'keywords'}) else None
        }
        
        # Extract medical terms
        terms = extract_medical_terms(text)
        
        # Document structure
        structure = {
            'headings': [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])],
            'links': len(soup.find_all('a')),
            'images': len(soup.find_all('img')),
            'tables': len(tables)
        }
        
        return {
            'text': text,
            'metadata': metadata,
            'tables': tables,
            'terms': terms,
            'structure': structure
        }
    
    def get_supported_formats(self) -> list:
        return ['.html', '.htm']