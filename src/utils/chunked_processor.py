import os
from typing import BinaryIO, Generator
import streamlit as st
from PIL import Image
import io
from pdf2image import convert_from_bytes
import pytesseract
import time

class ChunkedProcessor:
    """Process large files in chunks to prevent memory issues"""
    
    CHUNK_SIZE = 5 * 1024 * 1024  # 5MB chunks
    
    @staticmethod
    def process_pdf_in_chunks(file_data: bytes, progress_callback=None) -> Generator[str, None, None]:
        """Process PDF file in chunks"""
        try:
            # Convert PDF bytes to images in memory
            images = convert_from_bytes(file_data, fmt='png')
            total_images = len(images)
            
            for i, image in enumerate(images):
                # Process each image
                text = pytesseract.image_to_string(image, lang='eng+rus')
                
                # Update progress
                if progress_callback:
                    progress = (i + 1) / total_images
                    progress_callback(progress, f"Обработка страницы {i+1}/{total_images}")
                
                # Add small delay to prevent freezing
                time.sleep(0.1)
                
                yield text
                
        except Exception as e:
            st.error(f"Ошибка при обработке PDF: {str(e)}")
            yield ""
    
    @staticmethod
    def process_image_in_chunks(file: BinaryIO, progress_callback=None) -> str:
        """Process large image files in chunks"""
        try:
            # Read image in chunks
            image_data = io.BytesIO()
            while chunk := file.read(ChunkedProcessor.CHUNK_SIZE):
                image_data.write(chunk)
                if progress_callback:
                    progress_callback(0.5, "Чтение изображения...")
            
            # Process image
            image_data.seek(0)
            image = Image.open(image_data)
            
            if progress_callback:
                progress_callback(0.75, "Распознавание текста...")
            
            # Extract text
            text = pytesseract.image_to_string(image, lang='eng+rus')
            
            if progress_callback:
                progress_callback(1.0, "Обработка завершена")
            
            return text
            
        except Exception as e:
            st.error(f"Ошибка при обработке изображения: {str(e)}")
            return ""