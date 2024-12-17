import os
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import threading
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Class for managing document processing cache"""
    
    def __init__(self, cache_dir: str = '.cache', ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_lock = threading.Lock()
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _get_cache_path(self, key: str) -> str:
        """Get path to cache file for given key"""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def _generate_key(self, file_path: str, params: Dict[str, Any]) -> str:
        """Generate cache key based on file content and processing parameters"""
        # Get file content hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        # Combine with parameters
        params_str = json.dumps(params, sort_keys=True)
        combined = f"{file_hash}_{params_str}"
        
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, file_path: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        key = self._generate_key(file_path, params)
        cache_path = self._get_cache_path(key)
        
        with self.cache_lock:
            try:
                if os.path.exists(cache_path):
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cached = json.load(f)
                    
                    # Check if cache is still valid
                    cached_time = datetime.fromisoformat(cached['_cached_at'])
                    if datetime.now() - cached_time <= self.ttl:
                        logger.info(f"Cache hit for {file_path}")
                        del cached['_cached_at']
                        return cached
                    else:
                        logger.info(f"Cache expired for {file_path}")
                        os.remove(cache_path)
            except Exception as e:
                logger.error(f"Error reading cache: {str(e)}")
        
        return None
    
    def set(self, file_path: str, params: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Save result to cache"""
        key = self._generate_key(file_path, params)
        cache_path = self._get_cache_path(key)
        
        with self.cache_lock:
            try:
                # Add timestamp to cached data
                result_with_time = result.copy()
                result_with_time['_cached_at'] = datetime.now().isoformat()
                
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(result_with_time, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Cached result for {file_path}")
            except Exception as e:
                logger.error(f"Error writing cache: {str(e)}")
    
    def invalidate(self, file_path: str, params: Dict[str, Any]) -> None:
        """Invalidate cache for given file and parameters"""
        key = self._generate_key(file_path, params)
        cache_path = self._get_cache_path(key)
        
        with self.cache_lock:
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                    logger.info(f"Invalidated cache for {file_path}")
                except Exception as e:
                    logger.error(f"Error invalidating cache: {str(e)}")
    
    def clear(self) -> None:
        """Clear all cached data"""
        with self.cache_lock:
            try:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        os.remove(os.path.join(self.cache_dir, filename))
                logger.info("Cleared all cache")
            except Exception as e:
                logger.error(f"Error clearing cache: {str(e)}")
    
    def _start_cleanup_thread(self) -> None:
        """Start background thread for cache cleanup"""
        def cleanup():
            while True:
                logger.debug("Starting cache cleanup")
                with self.cache_lock:
                    try:
                        for filename in os.listdir(self.cache_dir):
                            if filename.endswith('.json'):
                                filepath = os.path.join(self.cache_dir, filename)
                                try:
                                    with open(filepath, 'r', encoding='utf-8') as f:
                                        cached = json.load(f)
                                    cached_time = datetime.fromisoformat(cached['_cached_at'])
                                    if datetime.now() - cached_time > self.ttl:
                                        os.remove(filepath)
                                        logger.debug(f"Removed expired cache file: {filename}")
                                except Exception as e:
                                    logger.error(f"Error during cleanup of {filename}: {str(e)}")
                    except Exception as e:
                        logger.error(f"Error during cache cleanup: {str(e)}")
                
                # Sleep for 1 hour before next cleanup
                threading.Event().wait(3600)
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()