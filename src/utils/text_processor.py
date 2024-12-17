import re
from typing import List, Dict

class TextProcessor:
    """Class for text processing and analysis"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text from unnecessary whitespace and special characters"""
        # Remove multiple whitespaces
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:а-яА-Я]', '', text)
        return text.strip()
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Split text into sentences"""
        # Split on sentence endings while preserving them
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def find_abbreviations(text: str) -> List[Dict[str, str]]:
        """Find medical abbreviations in text"""
        # Pattern for potential abbreviations
        pattern = r'\b[A-ZА-Я]{2,}\b'
        
        abbreviations = []
        matches = re.finditer(pattern, text)
        
        for match in matches:
            abbr = match.group(0)
            # Get context (up to 50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            
            abbreviations.append({
                'abbreviation': abbr,
                'context': context
            })
        
        return abbreviations
    
    @staticmethod
    def extract_measurements(text: str) -> List[Dict[str, str]]:
        """Extract medical measurements and values"""
        # Pattern for numbers with units
        pattern = r'\b\d+(?:\.\d+)?\s*(?:mg|ml|g|kg|mm|cm|%|мг|мл|г|кг|мм|см)\b'
        
        measurements = []
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            value = match.group(0)
            # Get context
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            
            measurements.append({
                'value': value,
                'context': context
            })
        
        return measurements
    
    @staticmethod
    def extract_dates(text: str) -> List[Dict[str, str]]:
        """Extract dates from text"""
        # Pattern for various date formats
        patterns = [
            r'\b\d{2}\.\d{2}\.\d{4}\b',  # DD.MM.YYYY
            r'\b\d{2}/\d{2}/\d{4}\b',  # DD/MM/YYYY
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                date = match.group(0)
                # Get context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                
                dates.append({
                    'date': date,
                    'format': pattern,
                    'context': context
                })
        
        return dates