import re
import json
from pathlib import Path
from typing import List, Dict

def load_medical_dictionary() -> Dict[str, str]:
    """Load medical terms dictionary from file"""
    dictionary_path = Path(__file__).parent.parent / 'data' / 'dictionaries' / 'medical_terms.json'
    try:
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def extract_medical_terms(text: str) -> List[Dict[str, str]]:
    """Extract medical terms from text using dictionary and patterns
    
    Args:
        text: Input text to analyze
        
    Returns:
        List of dicts containing:
            - term: Found medical term
            - context: Term context
            - category: Term category if available
            - definition: Term definition if available
    """
    dictionary = load_medical_dictionary()
    found_terms = []
    
    # Split text into sentences for better context
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        # Look for dictionary terms
        for term, info in dictionary.items():
            if term.lower() in sentence.lower():
                found_terms.append({
                    'term': term,
                    'context': sentence.strip(),
                    'category': info.get('category', ''),
                    'definition': info.get('definition', '')
                })
                
        # Look for common medical patterns
        patterns = [
            r'\b\d+\s*(?:мг|мл|г|%|мкг)\b',  # Doses
            r'\b[A-Z][a-z]*(?:itis|osis|emia|oma)\b',  # Common disease suffixes
            r'\b(?:anti|hyper|hypo|intra|peri)[a-z]+\b',  # Common prefixes
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                term = match.group(0)
                if not any(t['term'] == term for t in found_terms):
                    found_terms.append({
                        'term': term,
                        'context': sentence.strip(),
                        'category': 'pattern_match',
                        'definition': ''
                    })
    
    return found_terms