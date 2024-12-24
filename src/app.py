# ... (существующий импорт)

def check_required_software():
    missing = []
    install_instructions = {}
    
    # Проверка DjVuLibre
    if not shutil.which('ddjvu'):
        missing.append('DjVuLibre (ddjvu)')
        install_instructions['DjVuLibre (ddjvu)'] = {
            'Windows': 'Скачайте DjVuLibre с http://djvu.sourceforge.net/djvulibre-windows.html',
            'Linux': 'sudo apt-get install djvulibre-bin',
            'MacOS': 'brew install djvulibre'
        }
    
    # ... (остальные проверки)
            
    return missing, install_instructions

def main():
    st.title("Медицинский Документ Конвертер")
    
    with st.expander("Проверка конфигурации", expanded=True):
        if os.path.exists(POPPLER_PATH):
            st.success("✅ Poppler найден")
        else:
            st.error(f"❌ Poppler не найден: {POPPLER_PATH}")
            
        if os.path.exists(TESSERACT_PATH) and check_tesseract():
            st.success("✅ Tesseract найден")
        else:
            st.error(f"❌ Tesseract не найден: {TESSERACT_PATH}")
            st.stop()
            
        # Проверка дополнительного ПО с инструкциями по установке
        missing_software, install_instructions = check_required_software()
        if missing_software:
            st.warning("⚠️ Некоторые форматы могут быть недоступны. Отсутствует ПО:")
            for software in missing_software:
                st.warning(f"- {software}")
                if software in install_instructions:
                    with st.expander(f"📥 Инструкции по установке {software}"):
                        for os_name, instruction in install_instructions[software].items():
                            st.markdown(f"**{os_name}**: `{instruction}`")
        else:
            st.success("✅ Все дополнительные компоненты найдены")

    # ... (остальной код main())

if __name__ == "__main__":
    main()