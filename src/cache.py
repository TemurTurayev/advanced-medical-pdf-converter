import streamlit as st
from typing import Any, Dict
import hashlib
import json
import os

class ResultCache:
    def __init__(self, cache_dir: str = '.cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, content: bytes, context: Dict = None) -> str:
        """Generate cache key from content and context"""
        hasher = hashlib.sha256(content)
        if context:
            hasher.update(json.dumps(context, sort_keys=True).encode())
        return hasher.hexdigest()
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def _cached_get(cache_dir: str, key: str) -> Any:
        """Static cached method for getting results"""
        cache_file = os.path.join(cache_dir, f'{key}.json')
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None

    def get(self, key: str) -> Any:
        """Get cached result"""
        return self._cached_get(self.cache_dir, key)
    
    def set(self, key: str, value: Any):
        """Cache result"""
        cache_file = os.path.join(self.cache_dir, f'{key}.json')
        with open(cache_file, 'w') as f:
            json.dump(value, f)
    
    def clear(self):
        """Clear cache"""
        for file in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, file))