import pytest
from src.tread.processor import TREADProcessor

def test_processor_initialization():
    processor = TREADProcessor()
    assert processor is not None
    assert processor.config is not None

def test_pdf_processing():
    processor = TREADProcessor()
    # Add actual test implementation