import psutil
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging
import json
from dataclasses import dataclass

@dataclass
class ProcessingMetrics:
    memory_usage: float  # MB
    cpu_usage: float    # Percentage
    processing_time: float  # Seconds
    pages_per_second: float
    bytes_processed: int
    ocr_accuracy: float
    optimization_ratio: float

class TREADMonitor:
    def __init__(self, config_path: Optional[str] = None):
        self.start_time = time.time()
        self.log_dir = Path("logs/tread")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self.metrics = []
        self.processed_pages = 0
        self.processed_bytes = 0
        self.current_file = None

    def _setup_logging(self):
        self.logger = logging.getLogger('tread_pdf_monitor')
        handler = logging.FileHandler(self.log_dir / 'performance.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def start_file_processing(self, file_path: str):
        """Start monitoring new file processing"""
        self.current_file = Path(file_path)
        self.start_time = time.time()
        self.initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        self.logger.info(f"Started processing {file_path}")
        self.logger.info(f"Initial memory usage: {self.initial_memory:.2f}MB")

    def log_page_processed(self, page_size: int, ocr_confidence: float = 1.0):
        """Log metrics for processed page"""
        self.processed_pages += 1
        self.processed_bytes += page_size
        
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_diff = current_memory - self.initial_memory
        
        metrics = ProcessingMetrics(
            memory_usage=current_memory,
            cpu_usage=psutil.cpu_percent(),
            processing_time=elapsed_time,
            pages_per_second=self.processed_pages / elapsed_time,
            bytes_processed=self.processed_bytes,
            ocr_accuracy=ocr_confidence,
            optimization_ratio=self.processed_bytes / (memory_diff + 1)
        )
        
        self.metrics.append(metrics)
        self._log_metrics(metrics)

    def _log_metrics(self, metrics: ProcessingMetrics):
        """Log current metrics to file"""
        self.logger.info(
            f"File: {self.current_file.name} | "
            f"Pages: {self.processed_pages} | "
            f"Memory: {metrics.memory_usage:.2f}MB | "
            f"CPU: {metrics.cpu_usage:.1f}% | "
            f"Speed: {metrics.pages_per_second:.2f} pages/s | "
            f"OCR Accuracy: {metrics.ocr_accuracy:.2%}"
        )

    def get_current_stats(self) -> Dict:
        """Get current processing statistics"""
        if not self.metrics:
            return {}

        latest = self.metrics[-1]
        return {
            'file_name': self.current_file.name if self.current_file else None,
            'pages_processed': self.processed_pages,
            'memory_usage_mb': latest.memory_usage,
            'cpu_usage_percent': latest.cpu_usage,
            'processing_time_sec': latest.processing_time,
            'pages_per_second': latest.pages_per_second,
            'bytes_processed': latest.bytes_processed,
            'ocr_accuracy': latest.ocr_accuracy,
            'optimization_ratio': latest.optimization_ratio
        }

    def generate_report(self) -> str:
        """Generate detailed performance report"""
        stats = self.get_current_stats()
        if not stats:
            return "No processing data available"

        report = [
            "TREAD PDF Processing Report",
            "==========================",
            f"File: {stats['file_name']}",
            f"Pages Processed: {stats['pages_processed']}",
            f"Processing Time: {stats['processing_time_sec']:.2f}s",
            f"Memory Usage: {stats['memory_usage_mb']:.2f}MB",
            f"CPU Usage: {stats['cpu_usage_percent']:.1f}%",
            f"Processing Speed: {stats['pages_per_second']:.2f} pages/s",
            f"OCR Accuracy: {stats['ocr_accuracy']:.2%}",
            f"Optimization Ratio: {stats['optimization_ratio']:.2f}",
            "",
            "Performance Analysis:",
            "-------------------"
        ]

        # Add performance analysis
        if stats['memory_usage_mb'] > 1000:
            report.append("⚠️ High memory usage detected")
        if stats['pages_per_second'] < 0.5:
            report.append("⚠️ Processing speed below optimal")
        if stats['ocr_accuracy'] < 0.9:
            report.append("⚠️ Low OCR accuracy detected")

        return '\n'.join(report)

    def save_metrics(self):
        """Save metrics to JSON file"""
        if not self.metrics:
            return

        metrics_file = self.log_dir / f"metrics_{int(time.time())}.json"
        stats = self.get_current_stats()
        
        with open(metrics_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        self.logger.info(f"Metrics saved to {metrics_file}")