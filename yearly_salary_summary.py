import pandas as pd
import re
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


def auto_adjust_columns(worksheet):
    for column in worksheet.columns:
        column_letter = get_column_letter(column[0].column)
        max_length = 0
        
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        
        header = worksheet[f"{column_letter}1"].value
        if header in ["Все_ФИО", "Должность"]:
            adjusted_width = max(max_length + 2, 50)
        else:
            adjusted_width = max_length + 2
        
        worksheet.column_dimensions[column_letter].width = adjusted_width


NAME_MAP = {
    "П.": "Петр",
    "А.": "Анна",
    "И.": "Иван",
    "М.": "Мария",
    "Д.": "Дмитрий",
    "Е.": "Елена",
    "Н.": "Николай",
    "О.": "Ольга",
    "С.": "Сергей",
    "Р.": "Роман",
}


def normalize_fio(fio):
    fio = str(fio).strip().replace("ё", "е").replace("Ё", "Е")
    fio = re.sub(r'\s+', ' ', fio)
    
    words = fio.split()
    
    if len(words) == 1:
        return fio.title()
    
    normalized_words = []
    for word in words:
        clean_word = word.replace('.', '').strip()
        
        if len(clean_word) == 1 and clean_word.isalpha():
            initial = clean_word.upper() + '.'
            full_name = NAME_MAP.get(initial, clean_word)
            normalized_words.append(full_name)
        else:
            normalized_words.append(word)
    
    result = ' '.join(normalized_words)
    return result.title()


def extract_surname(fio):
    words = fio.split()
    if not words:
        return ""
    
    words = [w for w in words if len(w) > 1]
    
    if not words:
        return ""
    
    for word in words:
        if not any(word.endswith(suffix) for suffix in ['ович', 'евич', 'вна', 'ична']):
            return word
    
    return words[0]


def find_date_column(df):
    possible_names = ['дата выплаты', 'дата', 'дата_выплаты', 'выплата']
    
    for col in df.columns:
        col_lower = col.lower().strip()
        if col_lower in possible_names:
            return col
    
    return None


def clean_dataframe(df, filename):
    df.columns = df.columns.str.strip()
    
    if 'ФИО' in df.columns:
        df['ФИО'] = df['ФИО'].apply(normalize_fio)
    
    if 'Отдел' in df.columns:
        df['Отдел'] = df['Отдел'].astype(str).str.strip()
    
    if 'Должность' in df.columns:
        df['Должность'] = df['Должность'].astype(str).str.strip()
    
    for col in ['Оклад', 'Премия', 'Итого']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    if 'ID' in df.columns:
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
        df = df.dropna(subset=['ID'])
        df['ID'] = df['ID'].astype(int)
    
    date_col = find_date_column(df)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        if date_col != 'Дата выплаты':
            df = df.rename(columns={date_col: 'Дата выплаты'})
    else:
        print(f"⚠ {filename:<30} — не найден столбец с датой. Доступные столбцы: {list(df.columns)}")
        return pd.DataFrame()
    
    return df


def safe_divide(numerator, denominator, default=0):
    try:
        if denominator == 0 or pd.isna(denominator):
            return default
        return numerator / denominator
    except (ZeroDivisionError, TypeError, ValueError):
        return default


def annual_payroll_report():
    print("\n" + "=" * 60)
    print("💰 Годовой отчет по зарплатам сотрудников")
    print("=" * 60)
    
    folder_path = input("\nВведите путь к папке с файлами зарплат: ").strip()
    
    if not folder_path:
        print("❌ Путь не может быть пустым.")
        return
    
    folder = Path(folder_path)
    
    try:
        if not folder.exists():
            print(f"❌ Папка '{folder_path}' не существует.")
            return
        if not folder.is_dir():
            print(f"❌ '{folder_path}' — это не папка.")
            return
    except Exception as e:
        print(f"❌ Ошибка доступа к пути: {e}")
        return
    
    try:
        excel_files = sorted([f for f in folder.iterdir() 
                              if f.suffix.lower() in ['.xlsx', '.xls'] and f.is_file()])
    except PermissionError:
        print("❌ Нет прав доступа к папке.")
        return
    
    print(f"\n📁 Найдено файлов: {len(excel_files)}")
    
    if not excel_files:
        print("⚠ Файлов не найдено.")
        return
    
    print("\nФайлы для обработки:")
    for i, file in enumerate(excel_files, 1):
        print(f"   {i}. {file.name}")
    
    if input("\nНачать обработку? (да/нет): ").strip().lower() != "да":
        print("⏸ Отменено.")
        return
    
    print("\n🔄 Читаю и очищаю файлы...\n")
    
    all_dataframes = []
    errors_count = 0
    
    for file in excel_files:
        try:
            df = pd.read_excel(file)
            
            if df.empty:
                print(f"⚠ {file.name:<30} — пустой файл, пропущен")
                continue
            
            df = clean_dataframe(df, file.name)
            
            if df.empty:
                print(f"⚠ {file.name:<30} — после очистки данных не осталось")
                continue
            
            all_dataframes.append(df)
            print(f"✅ {file.name:<30} ({len(df)} записей)")
            
        except pd.errors.EmptyDataError:
            print(f"❌ {file.name:<30} — файл пуст или поврежден")
            errors_count += 1
        except PermissionError:
            print(f"❌ {file.name:<30} — нет прав доступа (возможно, файл открыт в Excel)")
            errors_count += 1
        except Exception as e:
            print(f"❌ {file.name:<30} — ошибка: {e}")
            errors_count += 1
    
    if not all_dataframes:
        print("\n❌ Не удалось прочитать ни один файл.")
        return
    
    print(f"\n🔗 Объединяю таблицы...")
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"✅ Всего записей: {len(merged_df)}")
    
    if errors_count > 0:
        print(f"⚠ Пропущено файлов с ошибками: {errors_count}")
    
    if 'Дата выплаты' not in merged_df.columns:
        print("\n❌ Критическая ошибка: столбец 'Дата выплаты' отсутствует в объединённых данных.")
        print(f"   Доступные столбцы: {list(merged_df.columns)}")
        return
    
    print("\n📊 Считаю итоги по сотрудникам...\n")
    
    merged_df['Месяц_выплаты'] = merged_df['Дата выплаты'].dt.month
    
    yearly_by_id = merged_df.groupby('ID').agg(
        Все_ФИО=('ФИО', lambda x: ' || '.join(sorted(set(x)))),
        Уникальных_ФИО=('ФИО', 'nunique'),
        Отдел=('Отдел', 'first'),
        Должность=('Должность', 'first'),
        Выплачено_за_год=('Итого', 'sum'),
        Премий_получено=('Премия', 'sum'),
        Месяцев_отработано=('Итого', 'count'),
        Первый_месяц=('Месяц_выплаты', 'min')
    ).reset_index()
    
    yearly_by_id['Потенциально_месяцев'] = 13 - yearly_by_id['Первый_месяц']
    
    yearly_by_id['Месяцев_на_больничном'] = (
        yearly_by_id['Потенциально_месяцев'] - yearly_by_id['Месяцев_отработано']
    ).clip(lower=0)
    
    yearly_by_id['Средняя_зарплата_в_месяц'] = yearly_by_id.apply(
        lambda row: safe_divide(
            row['Выплачено_за_год'],
            row['Месяцев_отработано'],
            default=0
        ),
        axis=1
    ).round(0).astype(int)
    
    yearly_by_id = yearly_by_id.drop(columns=['Первый_месяц', 'Потенциально_месяцев'])
    yearly_by_id = yearly_by_id.sort_values('ID', ascending=True)
    
    print("🔍 Проверяю корректность ФИО для каждого ID...\n")
    
    warnings = []
    for _, row in yearly_by_id.iterrows():
        fio_variants = row['Все_ФИО'].split(' || ')
        surnames = set()
        
        for fio in fio_variants:
            surname = extract_surname(fio)
            if surname:
                surnames.add(surname)
        
        if len(surnames) > 1:
            warning_msg = f"⚠ ВНИМАНИЕ: ID {row['ID']} — обнаружены разные фамилии: {surnames}"
            warnings.append(warning_msg)
            print(warning_msg)
            print(f"   Все варианты ФИО: {row['Все_ФИО']}")
    
    if not warnings:
        print("✅ Все ФИО в группах ID совпадают (одинаковые фамилии)")
    
    print("\n🏆 Итоги по сотрудникам (отсортированы по ID):\n")
    for _, row in yearly_by_id.iterrows():
        sick_info = f"болел: {row['Месяцев_на_больничном']} мес." if row['Месяцев_на_больничном'] > 0 else "не болел"
        print(f"   ID {row['ID']:<2} | {row['Все_ФИО'][:50]:<50} | {row['Выплачено_за_год']:>12,} ₽ | {sick_info}")
    
    total_paid = merged_df['Итого'].sum()
    total_bonuses = merged_df['Премия'].sum()
    total_employees = merged_df['ID'].nunique()
    
    print("\n" + "=" * 60)
    print(f"💰 ОБЩИЙ ФОНД ОПЛАТЫ ТРУДА ЗА ГОД:")
    print(f"   💵 Выплачено всего:    {total_paid:>15,} ₽")
    print(f"   🎁 Из них премии:      {total_bonuses:>15,} ₽")
    print(f"   👥 Сотрудников:        {total_employees:>15}")
    print("=" * 60)
    
    output_path = folder / "Годовой_отчет_по_зарплатам.xlsx"
    print(f"\n💾 Сохраняю отчет в: {output_path}")
    
    try:
        yearly_by_id.to_excel(output_path, index=False)
        print("✅ Файл сохранён")
        
        print("\n📏 Настраиваю ширину колонок...")
        wb = load_workbook(output_path)
        ws = wb.active
        auto_adjust_columns(ws)
        wb.save(output_path)
        print("   ✓ Ширина колонок настроена")
        
    except PermissionError:
        print("❌ Не удалось сохранить файл. Закройте Excel, если файл уже открыт.")
        return
    except Exception as e:
        print(f"\n❌ Ошибка сохранения: {e}")
        return
    
    print("\n" + "=" * 60)
    print(f"🏁 Готово! Отчет: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    annual_payroll_report()