                with open(output_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label=f"⬇️ Скачать результат для {file_name}",
                        data=f.read(),
                        file_name=f"{base_filename}_результат.txt",
                        mime='text/plain'
                    )
                
            except ProcessingError as e:
                st.error(f"❌ Ошибка при обработке {file_name}: {str(e)}")
            
            finally:
                try:
                    os.unlink(tmp_file.name)
                    if os.path.exists(output_path):
                        os.unlink(output_path)
                except:
                    pass
        
        progress_bar.empty()
        status_text.empty()
        page_status.empty()
        details_text.empty()
        st.success("🎉 Обработка завершена!")

if __name__ == "__main__":
    main()