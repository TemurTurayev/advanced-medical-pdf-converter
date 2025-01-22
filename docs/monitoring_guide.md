# TREAD Performance Monitoring Guide

## Overview
This guide explains how to use the TREAD monitoring system to track and optimize PDF processing performance.

## Basic Usage

```python
from src.tread.monitoring import TREADMonitor

# Initialize monitor
monitor = TREADMonitor()

# Start processing file
monitor.start_file_processing('medical_document.pdf')

# Log page processing
monitor.log_page_processed(
    page_size=1024*1024,  # 1MB
    ocr_confidence=0.95
)

# Get current stats
stats = monitor.get_current_stats()
print(f"Processing speed: {stats['pages_per_second']:.2f} pages/s")

# Generate report
report = monitor.generate_report()
print(report)
```

## Metrics Tracked

1. Performance Metrics
   - Memory usage (MB)
   - CPU usage (%)
   - Processing time
   - Pages per second
   - OCR accuracy

2. Resource Usage
   - Bytes processed
   - Memory efficiency
   - CPU utilization

3. Quality Metrics
   - OCR confidence
   - Optimization ratio

## Best Practices

1. Regular Monitoring
   ```python
   # Monitor at regular intervals
   for page in document.pages:
       process_page(page)
       monitor.log_page_processed(
           page_size=len(page.content),
           ocr_confidence=page.ocr_score
       )
   ```

2. Performance Optimization
   ```python
   # Check performance regularly
   stats = monitor.get_current_stats()
   if stats['memory_usage_mb'] > 1000:
       # Implement memory optimization
       optimize_memory()
   ```

3. Quality Control
   ```python
   # Monitor OCR quality
   if stats['ocr_accuracy'] < 0.9:
       # Enhance OCR settings
       enhance_ocr_settings()
   ```

## Troubleshooting

1. High Memory Usage
   - Check batch size
   - Monitor memory leaks
   - Implement garbage collection

2. Slow Processing
   - Verify CPU usage
   - Check disk I/O
   - Optimize thread count

3. Poor OCR Quality
   - Adjust DPI settings
   - Check image quality
   - Verify language settings

## Performance Optimization Tips

1. Memory Management
   ```python
   # Optimize memory usage
   import gc
   gc.collect()
   monitor.log_page_processed(...)
   ```

2. Processing Speed
   ```python
   # Use batch processing
   batch_size = 10
   for i in range(0, len(pages), batch_size):
       batch = pages[i:i+batch_size]
       process_batch(batch)
       monitor.log_page_processed(...)
   ```

3. Quality Enhancement
   ```python
   # Enhance OCR quality
   if monitor.get_current_stats()['ocr_accuracy'] < 0.9:
       enhance_image_quality()
       adjust_ocr_settings()
   ```