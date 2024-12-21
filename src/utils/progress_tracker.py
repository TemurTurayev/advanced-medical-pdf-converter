import streamlit as st
import time
from typing import Optional

class ProgressTracker:
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
        self.progress_bar = None
        self.status_text = None
        
    def init_progress_bar(self):
        """Initialize the progress bar in Streamlit"""
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
        
    def update(self, step: Optional[int] = None, description: Optional[str] = None):
        """Update progress bar and status"""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
            
        if description:
            self.description = description
            
        progress = min(self.current_step / self.total_steps, 1.0)
        
        if self.progress_bar is None:
            self.init_progress_bar()
            
        self.progress_bar.progress(progress)
        elapsed_time = time.time() - self.start_time
        self.status_text.text(f"{self.description}: {progress*100:.1f}% ({elapsed_time:.1f}s)")
        
    def complete(self, success: bool = True):
        """Mark the process as complete"""
        if success:
            self.progress_bar.progress(1.0)
            self.status_text.text(f"{self.description}: Completed in {time.time() - self.start_time:.1f}s")
        else:
            self.status_text.text(f"{self.description}: Failed after {time.time() - self.start_time:.1f}s")