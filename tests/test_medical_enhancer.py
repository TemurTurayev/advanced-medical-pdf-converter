import pytest
import numpy as np
from PIL import Image
from src.tread.medical_enhancer import MedicalEnhancer

@pytest.fixture
def medical_enhancer():
    return MedicalEnhancer()

@pytest.fixture
def sample_image():
    # Create a simple test image with text and a diagram
    img = np.zeros((500, 500), dtype=np.uint8)
    # Add simulated text
    img[100:150, 100:400] = 255  # Text area
    # Add simulated diagram
    cv2.circle(img, (300, 300), 50, 255, -1)
    return Image.fromarray(img)

def test_enhancer_initialization(medical_enhancer):
    assert medical_enhancer is not None
    assert medical_enhancer.config is not None
    assert medical_enhancer.patterns is not None

def test_image_enhancement(medical_enhancer, sample_image):
    enhanced = medical_enhancer.enhance_image(sample_image)
    assert isinstance(enhanced, Image.Image)
    assert enhanced.size == sample_image.size

def test_text_enhancement(medical_enhancer):
    # Create image with simulated text
    text_image = np.zeros((200, 400), dtype=np.uint8)
    text_image[50:70, 50:350] = 255  # Text line
    
    enhanced = medical_enhancer._enhance_text(text_image)
    assert enhanced.shape == text_image.shape
    assert np.mean(enhanced) > np.mean(text_image)  # Text should be clearer

def test_diagram_preservation(medical_enhancer, sample_image):
    # Convert to numpy array
    img_array = np.array(sample_image)
    binary = (img_array > 128).astype(np.uint8) * 255
    
    preserved = medical_enhancer._preserve_diagrams(binary, img_array)
    
    # Check if diagram area is preserved
    assert np.any(preserved[250:350, 250:350] > 0)  # Diagram area

def test_table_detection(medical_enhancer):
    # Create image with simulated table
    table_image = np.zeros((400, 600), dtype=np.uint8)
    # Add table header
    cv2.putText(table_image, 'Parameter', (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    cv2.putText(table_image, 'Value', (250, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    
    tables = medical_enhancer.detect_tables(table_image)
    assert len(tables) > 0
    assert 'region' in tables[0]
    assert 'content' in tables[0]

def test_measurement_recognition():
    enhancer = MedicalEnhancer({
        'ocr_lang': 'eng',
        'ocr_dpi': 300,
        'enhance_medical': True
    })
    
    # Create image with medical measurements
    img = np.zeros((200, 400), dtype=np.uint8)
    cv2.putText(img, '120/80 mmHg', (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    cv2.putText(img, '500 mg', (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    
    # Test measurement detection
    assert '120/80 mmHg' in pytesseract.image_to_string(img)
    assert '500 mg' in pytesseract.image_to_string(img)