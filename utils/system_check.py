import os
import subprocess
import sys
from typing import Tuple

def check_tesseract() -> Tuple[bool, str]:
    """
    Check if Tesseract is properly installed and configured.
    Returns: (is_installed: bool, message: str)
    """
    try:
        # Check if tesseract is in PATH
        if sys.platform.startswith('win'):
            # Check common installation paths on Windows
            common_paths = [
                r'C:\Program Files\Tesseract-OCR',
                r'C:\Program Files (x86)\Tesseract-OCR',
            ]
            
            # Add these paths to system PATH if found
            for path in common_paths:
                if os.path.exists(path) and path not in os.environ['PATH']:
                    os.environ['PATH'] += os.pathsep + path

        # Try to execute tesseract
        result = subprocess.run(['tesseract', '--version'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
        
        if result.returncode == 0:
            return True, "Tesseract successfully found"
        else:
            return False, "Tesseract is installed but returned an error"
            
    except FileNotFoundError:
        return False, "Tesseract is not installed or not in PATH"
    except Exception as e:
        return False, f"Error checking Tesseract: {str(e)}"

def check_poppler() -> Tuple[bool, str]:
    """
    Check if Poppler is properly installed and configured.
    Returns: (is_installed: bool, message: str)
    """
    try:
        if sys.platform.startswith('win'):
            # Check common installation paths on Windows
            common_paths = [
                r'C:\Program Files\poppler-24.08.0\bin',
                r'C:\Program Files (x86)\poppler-24.08.0\bin',
            ]
            
            # Add these paths to system PATH if found
            for path in common_paths:
                if os.path.exists(path) and path not in os.environ['PATH']:
                    os.environ['PATH'] += os.pathsep + path

        # Try to execute pdftoppm (part of poppler)
        result = subprocess.run(['pdftoppm', '-v'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
        
        if result.returncode == 0:
            return True, "Poppler successfully found"
        else:
            return False, "Poppler is installed but returned an error"
            
    except FileNotFoundError:
        return False, "Poppler is not installed or not in PATH"
    except Exception as e:
        return False, f"Error checking Poppler: {str(e)}"

def verify_system_requirements() -> Tuple[bool, str]:
    """
    Verify all system requirements are met.
    Returns: (all_ok: bool, message: str)
    """
    messages = []
    all_ok = True

    # Check Tesseract
    tesseract_ok, tesseract_msg = check_tesseract()
    if not tesseract_ok:
        all_ok = False
    messages.append(f"Tesseract: {'✓' if tesseract_ok else '✗'} {tesseract_msg}")

    # Check Poppler
    poppler_ok, poppler_msg = check_poppler()
    if not poppler_ok:
        all_ok = False
    messages.append(f"Poppler: {'✓' if poppler_ok else '✗'} {poppler_msg}")

    return all_ok, "\n".join(messages)
