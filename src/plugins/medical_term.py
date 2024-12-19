from .base import BasePlugin
from typing import Dict, List, Union
import re

class MedicalTermPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.medical_terms = self._load_medical_terms()

    def process(self, content: Union[str, bytes], context: Dict = None) -> Dict:
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
            
        found_terms = []
        for term in self.medical_terms:
            try:
                matches = re.finditer(term['pattern'], content, re.IGNORECASE)
                for match in matches:
                    found_terms.append({
                        'term': match.group(),
                        'position': match.start(),
                        'category': term['category'],
                        'description': term.get('description', '')
                    })
            except Exception:
                print('Error processing a medical term.')
                continue
                
        return {'terms': found_terms}

    def _load_medical_terms(self) -> List[Dict]:
        # TODO: Load from configuration
        return [
            {'pattern': r'\b\w*itis\b', 'category': 'inflammation'},
            {'pattern': r'\b\w*oma\b', 'category': 'tumor'},
            {'pattern': r'\b\w*ectomy\b', 'category': 'surgical_removal'}
        ]