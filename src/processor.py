class DocumentProcessor:
    def __init__(self):
        self.plugin_manager = PluginManager()
        
    def process_in_chunks(self, file_data: bytes, file_type: str, callback=None) -> Dict:
        try:
            results = []
            
            if file_type == 'pdf':
                # Process PDF page by page
                images = convert_from_bytes(file_data)
                total_pages = len(images)
                
                for i, image in enumerate(images, 1):
                    # Update progress
                    if callback:
                        progress = (i / total_pages) * 100
                        callback(progress, f"Обработка страницы {i}/{total_pages}")
                    
                    # Process page with delay to prevent freezing
                    text = pytesseract.image_to_string(image, lang='eng+rus')
                    results.append({'text': text})
                    
                    # Small delay to allow UI updates
                    time.sleep(0.1)
                    
            return {
                'pages': results,
                'metadata': {
                    'processed_at': datetime.now().isoformat(),
                    'total_pages': len(results)
                }
            }
            
        except Exception as e:
            raise ProcessingError(f'Ошибка обработки документа: {str(e)}')