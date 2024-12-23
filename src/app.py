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