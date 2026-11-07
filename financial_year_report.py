import pandas as pd
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

def merge_excel_files():
    """
    Объединяет все Excel файлы из папки в одну большую таблицу,
    отсортированную по датам, с расширенными колонками.
    """
    print("\n" + "=" * 60)
    print("📊 Объединение Excel файлов в одну таблицу")
    print("=" * 60)
    
    # Шаг 1: Ввод пути к папке
    folder_path = input("\nВведите путь к папке с Excel файлами: ").strip()
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        print("❌ Папка не найдена. Проверьте путь.")
        return
    
    # Шаг 2: Поиск всех Excel файлов
    excel_files = [f for f in folder.iterdir() 
                   if f.suffix.lower() in ['.xlsx', '.xls'] and f.is_file()]
    
    print(f"\n📁 Найдено файлов: {len(excel_files)}")
    
    if not excel_files:
        print("⚠ Excel файлов не найдено.")
        return
    
    # Показываем список файлов
    print("\nФайлы для объединения:")
    for i, file in enumerate(excel_files, 1):
        print(f"   {i}. {file.name}")
    
    # Шаг 3: Подтверждение
    if input("\nНачать объединение? (да/нет): ").strip().lower() != "да":
        print("⏸ Отменено.")
        return
    
    # Шаг 4: Чтение и объединение всех файлов
    print("\n🔄 Читаю файлы...\n")
    
    all_dataframes = []
    
    for file in excel_files:
        try:
            # Читаем Excel файл
            df = pd.read_excel(file)
            
            # ДОБАВЛЯЕМ В СПИСОК (без столбца "Источник")
            all_dataframes.append(df)
            
            print(f"✅ Прочитан: {file.name} ({len(df)} строк)")
            
        except Exception as e:
            print(f"❌ Ошибка чтения {file.name}: {e}")
    
    if not all_dataframes:
        print("\n❌ Не удалось прочитать ни один файл.")
        return
    
    # Шаг 5: Объединение всех таблиц
    print("\n🔗 Объединяю таблицы...")
    
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    print(f"✅ Объединено: {len(merged_df)} строк")
    
    # === ШАГ 6: СОРТИРОВКА ПО ДАТАМ ===
    print("\n📅 Сортирую по датам...")
    
    # Преобразуем столбец "Дата" в формат datetime
    merged_df['Дата'] = pd.to_datetime(merged_df['Дата'])
    
    # Сортируем по столбцу "Дата"
    merged_df = merged_df.sort_values('Дата')
    
    # Сбрасываем индексы
    merged_df = merged_df.reset_index(drop=True)
    
    # Преобразуем datetime обратно в строки формата "YYYY-MM-DD"
    merged_df['Дата'] = merged_df['Дата'].dt.strftime('%Y-%m-%d')
    
    print(f"✅ Отсортировано и формат дат исправлен")
    
    # Шаг 7: Сохранение результата
    output_path = folder / "Объединенная_таблица.xlsx"
    
    print(f"\n💾 Сохраняю результат в: {output_path}")
    
    try:
        merged_df.to_excel(output_path, index=False)
        print(f"\n✅ Файл успешно сохранён!")
        
        # === ШАГ 8: РАСШИРЕНИЕ КОЛОНОК ===
        print("\n📏 Настраиваю ширину колонок...")
        
        # Открываем сохранённый файл через openpyxl
        wb = load_workbook(output_path)
        ws = wb.active  # Активный лист
        
        # Проходим по всем колонкам и настраиваем ширину
        for column in ws.columns:
            # Получаем букву колонки (A, B, C...)
            column_letter = get_column_letter(column[0].column)
            
            # Находим максимальную длину текста в колонке
            max_length = 0
            
            for cell in column:
                try:
                    # Если значение не пустое, считаем его длину
                    if cell.value:
                        cell_length = len(str(cell.value))
                        if cell_length > max_length:
                            max_length = cell_length
                except:
                    pass
            
            # Устанавливаем ширину колонки
            # Добавляем небольшой отступ (+2 символа)
            adjusted_width = max_length + 2
            
            # Для колонки "Комментарий" делаем ещё шире
            header_value = ws[f"{column_letter}1"].value
            if header_value == "Комментарий":
                adjusted_width = max(adjusted_width, 50)  # Минимум 50 символов
            elif header_value == "Категория":
                adjusted_width = max(adjusted_width, 25)  # Минимум 25 символов
            
            # Применяем ширину
            ws.column_dimensions[column_letter].width = adjusted_width
            
            print(f"   ✓ Колонка '{header_value}': {adjusted_width} символов")
        
        # Сохраняем изменения
        wb.save(output_path)
        print(f"✅ Ширина колонок настроена")
        
        # Показываем первые строки результата
        print("\n📋 Первые 10 строк объединённой таблицы:")
        print(merged_df.head(10).to_string())
        
        print("\n📋 Последние 10 строк:")
        print(merged_df.tail(10).to_string())
        
        # Показываем диапазон дат
        print(f"\n📅 Диапазон дат: с {merged_df['Дата'].min()} по {merged_df['Дата'].max()}")
        
    except Exception as e:
        print(f"\n❌ Ошибка сохранения: {e}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Готово! Объединённый файл: {output_path}")
    print("=" * 60)


# Запуск программы
if __name__ == "__main__":
    merge_excel_files()
#Made by https://github.com/Serega210810