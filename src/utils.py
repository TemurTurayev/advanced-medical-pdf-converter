import os
from datetime import datetime
import json
from typing import Dict, Any

def log_error(filename: str, error: str):
    """Writes errors to a log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('conversion_errors.log', 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] File: {filename} | Error: {error}\n")
[... rest of the code ...]