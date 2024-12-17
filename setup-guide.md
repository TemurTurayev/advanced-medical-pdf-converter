# Руководство по установке Medical PDF Converter

## Системные требования

- Windows 10/11
- Python 3.8 или выше
- 4 ГБ ОЗУ (рекомендуется 8 ГБ)
- 2 ГБ свободного места на диске

## Установка Python

1. Скачайте Python с официального сайта: https://www.python.org/downloads/
2. Запустите установщик
3. ✅ Отметьте "Add Python to PATH"
4. Нажмите "Install Now"

## Установка Tesseract OCR

1. Скачайте установщик Tesseract для Windows:
   - https://github.com/UB-Mannheim/tesseract/wiki
   - Выберите последнюю версию (tesseract-ocr-w64-setup-v5.x.x)
2. Запустите установщик
3. Выберите дополнительные языки:
   - ✅ Russian
   - ✅ English
4. Установите в `C:\\Program Files\\Tesseract-OCR`

## Установка Poppler

1. Скачайте Poppler для Windows:
   - http://blog.alivate.com.au/poppler-windows/
   - Выберите версию 24.08.0
2. Распакуйте архив
3. Скопируйте содержимое в `C:\\Program Files\\poppler-24.08.0`
4. Добавьте `C:\\Program Files\\poppler-24.08.0\\bin` в PATH

## Установка зависимостей Python

1. Откройте командную строку от имени администратора
2. Перейдите в папку с проектом:
   ```bash
   cd путь_к_проекту
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Проверка установки

1. Запустите программу:
   ```bash
   streamlit run app.py
   ```
2. Проверьте статус компонентов в разделе "Проверка конфигурации"
3. Все компоненты должны быть отмечены зелёным ✅

## Возможные проблемы

### Tesseract не найден

Добавьте путь в переменные среды:
1. Откройте "Система" -> "Дополнительные параметры системы"
2. "Переменные среды" -> "Path"
3. Добавьте `C:\\Program Files\\Tesseract-OCR`

### Poppler не найден

Добавьте путь в переменные среды:
1. Откройте "Система" -> "Дополнительные параметры системы"
2. "Переменные среды" -> "Path"
3. Добавьте `C:\\Program Files\\poppler-24.08.0\\bin`

### Ошибки при установке пакетов Python

1. Обновите pip:
   ```bash
   python -m pip install --upgrade pip
   ```
2. Установите build tools:
   ```bash
   pip install --upgrade setuptools wheel
   ```
3. Попробуйте установить зависимости снова

## Поддержка

При возникновении проблем:
- Создайте issue на GitHub
- Свяжитесь с разработчиком:
  - Telegram: @Turayev_Temur
  - Email: temurturayev7822@gmail.com