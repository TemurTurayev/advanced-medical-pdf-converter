import spacy
import re
from typing import Dict, List, Tuple

def load_enhanced_dictionary():
    """
    Загружает расширенный словарь медицинских терминов
    """
    # Базовый словарь
    terms_dict = {
        'гипергликемия': 'Повышенный уровень глюкозы в крови',
        'ретинопатия': 'Поражение сетчатки глаза',
        # Добавьте больше терминов
    }
    
    return terms_dict

def add_term_variations(terms_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Добавляет вариации написания терминов
    """
    variations = {}
    for term, definition in terms_dict.items():
        # Добавляем вариации с дефисом
        if ' ' in term:
            variations[term.replace(' ', '-')] = definition
        
        # Добавляем вариации с разным регистром
        variations[term.title()] = definition
        variations[term.upper()] = definition
    
    return {**terms_dict, **variations}

def find_terms_in_context(doc, terms_dict: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Находит медицинские термины с учётом контекста
    """
    found_terms = []
    for sent in doc.sents:
        sent_text = sent.text.lower()
        for term, definition in terms_dict.items():
            term_lower = term.lower()
            if term_lower in sent_text:
                found_terms.append({
                    'term': term,
                    'definition': definition,
                    'context': sent.text
                })
    
    return found_terms