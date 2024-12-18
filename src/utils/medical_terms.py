import spacy
import re
from typing import Dict, List, Tuple

def load_medical_dictionary():
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

def extract_medical_terms(text: str) -> List[Dict[str, str]]:
    """
    Извлекает медицинские термины из текста
    
    Args:
        text (str): Входной текст для анализа
        
    Returns:
        List[Dict[str, str]]: Список найденных терминов с их определениями
    """
    try:
        # Загружаем словарь
        terms_dict = load_medical_dictionary()
        terms_dict = add_term_variations(terms_dict)
        
        # Загружаем модель spacy
        try:
            nlp = spacy.load("ru_core_news_lg")
        except:
            nlp = spacy.load("ru_core_news_sm")
            
        # Обрабатываем текст
        doc = nlp(text)
        
        # Ищем термины
        found_terms = find_terms_in_context(doc, terms_dict)
        
        return found_terms
        
    except Exception as e:
        print(f"Error in extract_medical_terms: {str(e)}")
        return []
