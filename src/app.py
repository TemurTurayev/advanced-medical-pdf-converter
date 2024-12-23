            st.success("✅ Все дополнительные компоненты найдены")
    
    converter = MedicalDocumentConverter()
    
    all_formats = [fmt for formats in SUPPORTED_FORMATS.values() for fmt in formats]
    
    uploaded_files = st.file_uploader(
        "Выберите файлы для конвертации",
        type=all_formats,
        accept_multiple_files=True
    )
    
    if uploaded_files:
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            page_status = st.empty()
            details_text = st.empty()
        
        # Initialize overall progress tracking
        total_progress = ProcessingProgress(total_files=len(uploaded_files))
        converter.set_progress(total_progress)
        converter.set_status_callback(lambda msg: details_text.text(msg))
        
        for i, uploaded_file in enumerate(uploaded_files, 1):
            try:
                total_progress.update(file=i)
                file_name = uploaded_file.name
                total_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Size in MB
                
                status_text.text(f"Обработка файла {i}/{len(uploaded_files)}: {file_name} ({total_size:.1f} MB)")
                
                file_extension = file_name.split('.')[-1].lower()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
                    details_text.text("Сохранение файла...")
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file.flush()
                    
                    results = converter.process_document(tmp_file.name, file_extension)
                    
                    output_folder = "converted_files"
                    os.makedirs(output_folder, exist_ok=True)
                    
                    base_filename = os.path.splitext(file_name)[0]
                    output_path = os.path.join(output_folder, f"{base_filename}_результат.txt")
                    
                    details_text.text("Сохранение результатов...")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for page_num, page_result in enumerate(results['pages'], 1):
                            f.write(f"\n--- Страница {page_num} ---\n")
                            f.write(page_result.get('text', ''))
                    
                    progress = total_progress.get_progress()
                    progress_bar.progress(progress)
                
                details_text.text("✅ Обработка завершена")
                st.success(f"✅ Успешно обработан: {file_name}")
                
                with open(output_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label=f"⬇️ Скачать результат для {file_name}",
                        data=f.read(),
                        file_name=f"{base_filename}_результат.txt",
                        mime='text/plain'
                    )
                
            except ProcessingError as e:
                st.error(f"❌ Ошибка при обработке {file_name}: {str(e)}")
            
            except Exception as e:
                st.error(f"❌ Неизвестная ошибка при обработке {file_name}: {str(e)}")
            
            finally:
                try:
                    if 'tmp_file' in locals():
                        os.unlink(tmp_file.name)
                    if 'output_path' in locals() and os.path.exists(output_path):
                        os.unlink(output_path)
                except Exception as e:
                    st.warning(f"⚠️ Ошибка при очистке временных файлов: {str(e)}")
        
        # Clear progress display
        progress_container.empty()
        st.success("🎉 Обработка всех файлов завершена!")

if __name__ == "__main__":
    main()