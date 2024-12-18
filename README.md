# Medical PDF Converter

## Требования к системе
- Python 3.8+
- Tesseract OCR
- Poppler
- Microsoft Office (для .doc и .ppt файлов)
- DjVuLibre (для .djvu файлов)

## Установка дополнительных компонентов

### Windows
1. Microsoft Office:
   - Установите Microsoft Office (Word и PowerPoint)
   
2. DjVuLibre:
   - Скачайте DjVuLibre с официального сайта
   - Добавьте путь к папке bin в переменную PATH

### Linux
```bash
sudo apt-get update
sudo apt-get install djvulibre-bin
```