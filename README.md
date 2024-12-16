# Advanced Medical PDF Converter 🏥

Advanced PDF converter specially designed for medical documents. Features OCR capabilities, medical terminology recognition, table detection, and multi-format output support.

## ✨ Features

- 📝 Advanced OCR for medical documents
- 🔍 Medical terminology recognition
- 📊 Table and chart detection
- 🌍 Supports both Russian and English medical terms
- ⚡ Parallel processing for multiple files
- 📈 Real-time progress tracking
- 🎯 Quality assessment metrics
- 📋 Multiple output formats (TXT, HTML, JSON)

## 🛠️ Requirements

- Windows 10/11
- Python 3.8 or higher
- [Poppler](http://blog.alivate.com.au/poppler-windows/) (v24.08.0)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- Required Python packages (see requirements.txt)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/TemurTurayev/advanced-medical-pdf-converter.git
cd advanced-medical-pdf-converter
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Install Poppler:
   - Download Poppler for Windows
   - Extract to `C:\Program Files\poppler-24.08.0`
   - Add to system PATH

4. Install Tesseract OCR:
   - Download installer from official repository
   - Install to default location
   - Add Russian language support during installation

## 🚀 Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Through the web interface:
   - Upload single or multiple PDF files
   - Monitor processing progress
   - Access results in preferred format

3. Results will be saved in `converted_files` folder:
   - `*_результат.txt` - Plain text
   - `*_результат.html` - Formatted HTML with highlights
   - `*_результат.json` - Structured data

## 📊 Features in Detail

### Medical Term Recognition
- Automatic detection of medical terminology
- Support for chemical formulas
- Recognition of medical abbreviations
- Highlighting of important medical terms

### Table Detection
- Automatic table structure recognition
- Conversion to structured format
- Preservation of table layouts
- Support for complex medical tables

### Quality Control
- OCR quality assessment
- Confidence metrics
- Error logging
- Processing statistics

## 🔧 Configuration

Key configuration files are located in:
- `data/dictionaries/` - Medical term dictionaries
- `data/patterns/` - Recognition patterns
- `config.py` - Main configuration file

## 📝 Output Formats

### Text Output
- Clean, readable text
- Preserved document structure
- Page markers
- Extracted tables in text format

### HTML Output
- Color-coded medical terms
- Interactive tooltips
- Formatted tables
- Visual element positioning

### JSON Output
- Structured data format
- Quality metrics
- Element positions
- Processing metadata

## 🤝 Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for guidelines.

## 🆘 Support

For support:
- Open an issue on GitHub
- Contact: @Turayev_Temur (Telegram)
- Email: temurturayev7822@gmail.com

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.
