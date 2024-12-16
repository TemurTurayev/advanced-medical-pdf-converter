# Detailed Setup Guide

## Windows Setup

### Prerequisites
1. Install Python 3.8+:
   - Download from python.org
   - Check "Add Python to PATH" during installation

2. Install Poppler:
   ```bash
   # Download poppler
   wget https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip
   # Extract to C:\Program Files\poppler-24.08.0
   # Add to PATH: C:\Program Files\poppler-24.08.0\Library\bin
   ```

3. Install Tesseract OCR:
   - Download installer from UB-Mannheim
   - Install with Russian language support
   - Add to PATH: C:\Program Files\Tesseract-OCR

### Application Setup
1. Clone repository:
   ```bash
   git clone https://github.com/TemurTurayev/advanced-medical-pdf-converter.git
   cd advanced-medical-pdf-converter
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure paths in config.py:
   ```python
   POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"
   TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

## Usage Examples

### Basic Usage
```python
from pdf_converter import MedicalPDFConverter

converter = MedicalPDFConverter()
results = converter.process_file("example.pdf")
```

### Batch Processing
```python
files = ["file1.pdf", "file2.pdf", "file3.pdf"]
converter.process_multiple(files)
```

### Custom Dictionary
```python
converter.add_custom_terms("my_terms.txt")
```
