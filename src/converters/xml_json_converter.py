import json
import xmltodict
from typing import Dict, Any
from .base_converter import BaseConverter
from ..utils.medical_terms import extract_medical_terms

class XmlJsonConverter(BaseConverter):
    """Converter for XML and JSON files"""

    def convert(self, file_path: str, **kwargs) -> Dict[str, Any]:
        file_ext = file_path.lower().split('.')[-1]
        
        # Read and parse file
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_ext == 'json':
                data = json.load(f)
                text = json.dumps(data, indent=2, ensure_ascii=False)
            else:  # XML
                xml_content = f.read()
                data = xmltodict.parse(xml_content)
                text = xml_content
        
        # Convert to string for term extraction
        if isinstance(data, dict):
            flat_text = json.dumps(data, ensure_ascii=False)
        else:
            flat_text = str(data)
        
        # Extract medical terms
        terms = extract_medical_terms(flat_text)
        
        # Create tables from structured data
        tables = self._extract_tables_from_data(data)
        
        # Document structure
        structure = self._analyze_structure(data)
        
        return {
            'text': text,
            'metadata': {
                'format': file_ext.upper(),
                'size': len(text),
                'structure': structure
            },
            'tables': tables,
            'terms': terms,
            'structure': structure
        }
    
    def _extract_tables_from_data(self, data: Dict) -> list:
        """Extract tabular data from nested structures"""
        tables = []
        
        def process_item(item):
            if isinstance(item, list) and all(isinstance(x, dict) for x in item):
                # If we have a list of similar objects, convert to table
                if item:
                    headers = list(item[0].keys())
                    table = [headers]
                    for row in item:
                        table.append([str(row.get(h, '')) for h in headers])
                    tables.append(table)
            elif isinstance(item, dict):
                for value in item.values():
                    process_item(value)
            elif isinstance(item, list):
                for value in item:
                    process_item(value)
        
        process_item(data)
        return tables
    
    def _analyze_structure(self, data: Dict) -> Dict:
        """Analyze the structure of the data"""
        structure = {
            'type': type(data).__name__,
            'depth': 0,
            'array_counts': 0,
            'object_counts': 0
        }
        
        def analyze_item(item, depth=0):
            structure['depth'] = max(structure['depth'], depth)
            
            if isinstance(item, dict):
                structure['object_counts'] += 1
                for value in item.values():
                    analyze_item(value, depth + 1)
            elif isinstance(item, list):
                structure['array_counts'] += 1
                for value in item:
                    analyze_item(value, depth + 1)
        
        analyze_item(data)
        return structure
    
    def get_supported_formats(self) -> list:
        return ['.json', '.xml']
