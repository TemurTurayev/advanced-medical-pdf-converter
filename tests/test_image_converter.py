import unittest
from PIL import Image
import numpy as np
from src.converters.image_converter import ImageConverter

class TestImageConverter(unittest.TestCase):
    def setUp(self):
        self.converter = ImageConverter()

    def test_language_detection(self):
        # Test Russian text detection
        russian_text = 'Привет мир'
        self.assertEqual(self.converter.detect_language(russian_text), 'rus')

        # Test English text detection
        english_text = 'Hello world'
        self.assertEqual(self.converter.detect_language(english_text), 'eng')

    def test_image_enhancement(self):
        # Create test image
        img = Image.new('RGB', (100, 100), color='white')
        enhanced = self.converter.enhance_image(img)
        
        # Check if enhancement was applied
        self.assertIsInstance(enhanced, Image.Image)
        self.assertEqual(enhanced.size, (100, 100))

    def test_medical_terms_processing(self):
        text = 'The patient shows signs of retinopathy'
        terms = self.converter.process_medical_terms(text)
        
        # Check if medical terms were detected
        self.assertIsInstance(terms, list)
        self.assertTrue(len(terms) > 0)

if __name__ == '__main__':
    unittest.main()