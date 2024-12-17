import streamlit as st
from typing import Any, Dict
import hashlib
import json
import os

class ResultCache:
    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _calculate_key(self, content: bytes, context: Dict = None) -> str:
        """Generate cache key from content and context"""
        hasher = hashlib.sha256(content)
        if context:
            hasher.update(json.dumps(context, sort_keys=True).encode())
        return hasher.hexdigest()
    
    @st.cache_data(ttl=3600)
    def _get_cached(key: str) -> Any:
        """Get cached result - static method for caching"""
        cache_file = os.path.join('.cache', f'{key}.json')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None

    def get(self, content: bytes, context: Dict = None) -> Any:
        """Get result from cache"""
        key = self._calculate_key(content, context)
        return self._get_cached(key)
    
    def set(self, content: bytes, value: Any, context: Dict = None):
        """Cache result"""
        key = self._calculate_key(content, context)
        cache_file = os.path.join(self.cache_dir, f'{key}.json')
        with open(cache_file, 'w') as f:
            json.dump(value, f)
    
    def clear(self):
        """Clear cache"""
        for file in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, file))