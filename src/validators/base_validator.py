from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseValidator(ABC):
    """Базовый класс для валидаторов обработанных документов"""
    
    @abstractmethod
    def validate(self, document: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Проверяет качество обработанного документа
        
        Args:
            document: словарь с обработанным документом
            
        Returns:
            List[Dict[str, str]]: список проблем в формате [{"type": "тип_проблемы", "description": "описание"}]
        """
        pass
        
    @abstractmethod
    def get_confidence_score(self, document: Dict[str, Any]) -> float:
        """
        Возвращает оценку уверенности в качестве обработки
        
        Args:
            document: словарь с обработанным документом
            
        Returns:
            float: оценка от 0.0 до 1.0
        """
        pass
        
    @abstractmethod
    def fix_issues(self, document: Dict[str, Any], issues: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Пытается исправить найденные проблемы
        
        Args:
            document: исходный документ
            issues: список проблем
            
        Returns:
            Dict[str, Any]: исправленный документ
        """
        pass