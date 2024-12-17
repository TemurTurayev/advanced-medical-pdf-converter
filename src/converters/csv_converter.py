import pandas as pd
from typing import Dict, Any
from .base_converter import BaseConverter
from ..utils.medical_terms import extract_medical_terms

class CsvConverter(BaseConverter):
    """Converter for CSV files with medical data support"""

    def convert(self, file_path: str, **kwargs) -> Dict[str, Any]:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Convert to text representation
        text = df.to_string()
        
        # Extract medical terms from all text columns
        terms = []
        for column in df.select_dtypes(include=['object']).columns:
            column_text = ' '.join(df[column].dropna().astype(str))
            terms.extend(extract_medical_terms(column_text))
        
        # Convert DataFrame to list of lists for table representation
        tables = [df.columns.tolist()]
        tables.extend(df.values.tolist())
        
        # Extract metadata
        metadata = {
            'columns': df.columns.tolist(),
            'rows': len(df),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'has_nulls': df.isnull().any().to_dict()
        }
        
        # Document structure
        structure = {
            'column_count': len(df.columns),
            'row_count': len(df),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'text_columns': df.select_dtypes(include=['object']).columns.tolist()
        }
        
        return {
            'text': text,
            'metadata': metadata,
            'tables': [tables],
            'terms': terms,
            'structure': structure
        }
    
    def get_supported_formats(self) -> list:
        return ['.csv']