import os
import subprocess
import sys
import importlib
from typing import Tuple

def check_tesseract() -> Tuple[bool, str]:
    """Check if Tesseract is properly installed and configured."""
    try:
        if sys.platform.startswith('win'):
            common_paths = [
                r'C:\Program Files\Tesseract-OCR',
                r'C:\Program Files (x86)\Tesseract-OCR',
            ]
            
            for path in common_paths:
                if os.path.exists(path) and path not in os.environ['PATH']:
                    os.environ['PATH'] += os.pathsep + path

        result = subprocess.run(['tesseract', '--version'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
        
        if result.returncode == 0:
            return True, "✓ Tesseract установлен"
        else:
            return False, "✗ Tesseract установлен, но возвращает ошибку"
            
    except FileNotFoundError:
        return False, "✗ Tesseract не установлен или не найден"
    except Exception as e:
        return False, f"✗ Ошибка при проверке Tesseract: {str(e)}"

def check_poppler() -> Tuple[bool, str]:
    """Check if Poppler is properly installed and configured."""
    try:
        if sys.platform.startswith('win'):
            common_paths = [
                r'C:\Program Files\poppler-24.08.0\bin',
                r'C:\Program Files (x86)\poppler-24.08.0\bin',
            ]
            
            for path in common_paths:
                if os.path.exists(path) and path not in os.environ['PATH']:
                    os.environ['PATH'] += os.pathsep + path

        result = subprocess.run(['pdftoppm', '-v'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
        
        if result.returncode == 0:
            return True, "✓ Poppler установлен"
        else:
            return False, "✗ Poppler установлен, но возвращает ошибку"
            
    except FileNotFoundError:
        return False, "✗ Poppler не установлен или не найден"
    except Exception as e:
        return False, f"✗ Ошибка при проверке Poppler: {str(e)}"

def check_python_packages() -> Tuple[bool, str]:
    """Check if required Python packages are installed."""
    required_packages = [
        'python-docx',
        'python-pptx',
        'beautifulsoup4',
        'piexif',
        'xmltodict',
        'pandas',
        'numpy',
        'opencv-python'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if not missing_packages:
        return True, "✓ Все необходимые Python пакеты установлены"
    else:
        return False, f"✗ Отсутствуют пакеты: {', '.join(missing_packages)}"

def check_available_languages() -> Tuple[bool, str]:
    """Check if required Tesseract languages are installed."""
    required_langs = ['rus', 'eng']
    
    try:
        result = subprocess.run(['tesseract', '--list-langs'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
        
        if result.returncode == 0:
            available_langs = result.stdout.strip().split('\n')[1:]  # Skip first line (header)
            missing_langs = [lang for lang in required_langs if lang not in available_langs]
            
            if not missing_langs:
                return True, "✓ Все необходимые языки Tesseract установлены"
            else:
                return False, f"✗ Отсутствуют языки Tesseract: {', '.join(missing_langs)}"
        else:
            return False, "✗ Ошибка при проверке языков Tesseract"
            
    except Exception as e:
        return False, f"✗ Ошибка при проверке языков: {str(e)}"

def verify_system_requirements() -> Tuple[bool, str]:
    """Verify all system requirements are met."""
    messages = []
    all_ok = True

    # Check Tesseract
    tesseract_ok, tesseract_msg = check_tesseract()
    if not tesseract_ok:
        all_ok = False
    messages.append(tesseract_msg)

    # Check Poppler
    poppler_ok, poppler_msg = check_poppler()
    if not poppler_ok:
        all_ok = False
    messages.append(poppler_msg)

    # Check Python packages
    packages_ok, packages_msg = check_python_packages()
    if not packages_ok:
        all_ok = False
    messages.append(packages_msg)

    # Check Tesseract languages
    langs_ok, langs_msg = check_available_languages()
    if not langs_ok:
        all_ok = False
    messages.append(langs_msg)

    return all_ok, "\n".join(messages)