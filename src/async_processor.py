import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable, Any
import multiprocessing

class AsyncProcessor:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.loop = None

    async def process_batch(self, items: List[Any], process_func: Callable) -> List[Any]:
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
        
        tasks = []
        for item in items:
            task = self.loop.run_in_executor(self.executor, process_func, item)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

    def process_batch_sync(self, items: List[Any], process_func: Callable) -> List[Any]:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        self.loop = loop
        return loop.run_until_complete(self.process_batch(items, process_func))

    def __del__(self):
        if self.executor:
            self.executor.shutdown(wait=False)