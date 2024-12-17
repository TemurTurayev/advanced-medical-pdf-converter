from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from typing import List, Dict, Any
from src.errors import ProcessingError

class AsyncProcessor:
    def __init__(self, max_workers: int = None):
        # Use CPU count instead of event loop
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    def process_batch(self, items: List[Any], process_func, **kwargs) -> List[Dict]:
        """Process a batch of items using thread pool
        Args:
            items: List of items to process
            process_func: Function to process each item
            **kwargs: Additional arguments for process_func
        Returns:
            List of processing results
        """
        futures = []
        results = []
        
        try:
            # Submit all tasks to executor
            for item in items:
                future = self.executor.submit(process_func, item, **kwargs)
                futures.append(future)
            
            # Wait for all tasks to complete
            for future in futures:
                results.append(future.result())
            
            return results
            
        except Exception as e:
            raise ProcessingError(f'Batch processing failed: {str(e)}')
    
    def __del__(self):
        try:
            self.executor.shutdown(wait=False)
        except:
            pass