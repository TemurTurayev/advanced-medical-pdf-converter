import asyncio
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from .errors import ProcessingError

class AsyncProcessor:
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or (asyncio.get_event_loop().get_default_executor()._max_workers)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    async def process_batch(self, items: List[Any], process_func, **kwargs) -> List[Dict]:
        """Process a batch of items asynchronously
        Args:
            items: List of items to process
            process_func: Function to process each item
            **kwargs: Additional arguments for process_func
        Returns:
            List of processing results
        """
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(self.executor, process_func, item, **kwargs)
            for item in items
        ]
        results = []
        try:
            completed = await asyncio.gather(*tasks)
            results.extend(completed)
        except Exception as e:
            raise ProcessingError(f'Batch processing failed: {str(e)}')
        return results
    
    def __del__(self):
        self.executor.shutdown(wait=True)