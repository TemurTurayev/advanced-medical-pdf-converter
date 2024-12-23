import threading
from typing import Optional


class ProcessingProgress:
    """Класс для отслеживания прогресса обработки файлов и страниц"""
    
    def __init__(self, total_pages: int = 0, total_files: int = 0):
        self.total_pages = total_pages
        self.current_page = 0
        self.total_files = total_files
        self.current_file = 0
        self._lock = threading.Lock()
        
    def update(self, page: Optional[int] = None, file: Optional[int] = None):
        """Обновить прогресс обработки"""
        with self._lock:
            if page is not None:
                self.current_page = page
            if file is not None:
                self.current_file = file
                
    def get_progress(self) -> float:
        """Получить общий прогресс обработки (0.0 - 1.0)"""
        if self.total_files == 0:
            return 0
        file_progress = self.current_file / self.total_files
        if self.total_pages > 0:
            page_progress = self.current_page / self.total_pages
            return (file_progress + page_progress) / 2
        return file_progress