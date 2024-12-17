from typing import List
import re

def extract_medical_terms(text: str) -> List[str]:
    """
    Extract medical terms from text using regex patterns
    
    Args:
        text: Input text to process
        
    Returns:
        List of found medical terms
    """
    # Basic pattern for medical terms (expand this list based on your needs)
    patterns = [
        r'\b[A-Z][a-z]+(itis|osis|emia|opathy)\b',  # Common medical suffixes
        r'\b(anti|hyper|hypo|intra|peri)[a-z]+\b',  # Common prefixes
        r'\b[A-Z][a-z]+(gram|scope|tomy|plasty)\b', # Medical procedures
        r'\b(MRI|CT|EKG|ECG|CBC)\b',                # Common abbreviations
    ]
    
    terms = []
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        terms.extend([match.group() for match in matches])
    
    return list(set(terms))  # Remove duplicates