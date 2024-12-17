import os
from datetime import datetime
import json
from typing import Dict, Any

def log_error(filename: str, error: str):
    """Writes errors to a log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('conversion_errors.log', 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] File: {filename} | Error: {error}\n")

def save_metadata(filename: str, metadata: Dict[str, Any]):
    """Saves metadata to JSON file"""
    output_dir = 'metadata'
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"{filename}_metadata.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def get_file_extension(filename: str) -> str:
    """Returns file extension without dot"""
    return os.path.splitext(filename)[1][1:].lower()

def create_output_path(input_filename: str, output_dir: str = 'converted') -> str:
    """Creates output path for converted file"""
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_filename))[0]
    return os.path.join(output_dir, f"{base_name}_converted.txt")
