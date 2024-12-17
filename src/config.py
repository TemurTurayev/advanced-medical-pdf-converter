import os

# Paths
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR"

# Environment setup
os.environ['PATH'] += os.pathsep + POPPLER_PATH
os.environ['PATH'] += os.pathsep + TESSERACT_PATH