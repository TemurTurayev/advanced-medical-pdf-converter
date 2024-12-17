import docx
from typing import Dict, Any
from .base_converter import BaseConverter
from ..utils.medical_terms import extract_medical_terms
from ..utils.table_extractor import extract_tables

class DocxConverter(BaseConverter):
    """Converter for DOCX documents"""

    def convert(self, file_path: str, **kwargs) -> Dict[str, Any]:
        doc = docx.Document(file_path)
        
        # Extract text with formatting
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        # Extract tables
        tables = []
        for table in doc.tables:
            rows = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                rows.append(row_data)
            tables.append(rows)
        
        # Extract metadata
        metadata = {
            'author': doc.core_properties.author,
            'created': doc.core_properties.created,
            'modified': doc.core_properties.modified,
            'title': doc.core_properties.title
        }
        
        # Extract medical terms
        terms = extract_medical_terms(text)
        
        # Document structure
        structure = {
            'headings': [p.text for p in doc.paragraphs if p.style.name.startswith('Heading')],
            'images': len(doc.inline_shapes),
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
        return ['.docx', '.doc']