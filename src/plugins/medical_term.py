from .base import BasePlugin
from typing import Dict, List
import re

class MedicalTermPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.medical_terms = self._load_medical_terms()

    def process(self, content: Dict, context: Dict = None) -> Dict:
        """Process the content using the plugin
        Args:
            content: Dict with 'text' and 'image' keys
            context: Additional context for processing
        Returns:
            Dict with found terms
        """
        text = content.get('text', '')
        if not text:
            return {'terms': []}
            
        found_terms = []
        for term in self.medical_terms:
            matches = re.finditer(term['pattern'], text, re.IGNORECASE)
            for match in matches:
                found_terms.append({
                    'term': match.group(),
                    'position': match.start(),
                    'category': term['category'],
                    'description': term.get('description', '')
                })
        return {'terms': found_terms}

    def _load_medical_terms(self) -> List[Dict]:
        # TODO: Load from configuration
        return [
            {
                'pattern': r'\b\w*itis\b',
                'category': 'inflammation',
                'description': 'Воспалительный процесс'
            },
            {
                'pattern': r'\b\w*oma\b',
                'category': 'tumor',
                'description': 'Опухоль'
            },
            {
                'pattern': r'\b\w*ectomy\b',
                'category': 'surgical_removal',
                'description': 'Хирургическое удаление'
            },
            {
                'pattern': r'\b\w*алгия\b',
                'category': 'pain',
                'description': 'Боль'
            },
            {
                'pattern': r'\b\w*стеноз\b',
                'category': 'stenosis',
                'description': 'Сужение'
            }
        ]