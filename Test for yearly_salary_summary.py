import pandas as pd
import random
from pathlib import Path

test_folder = Path("salary_files")
test_folder.mkdir(exist_ok=True)

print("📝 Создаю 12 файлов с зарплатами сотрудников...\n")

EMPLOYEES = [
    {"ID": 1, "ФИО": "Петров Петр Петрович",      "Отдел": "IT",          "Должность": "Разработчик",     "Оклад": 150000, "Начало": 1},
    {"ID": 2, "ФИО": "Сидорова Анна Ивановна",    "Отдел": "Бухгалтерия", "Должность": "Бухгалтер",       "Оклад": 90000,  "Начало": 1},
    {"ID": 3, "ФИО": "Козлов Иван Сергеевич",     "Отдел": "IT",          "Должность": "Тимлид",          "Оклад": 200000, "Начало": 1},
    {"ID": 4, "ФИО": "Морозова Мария Алексеевна", "Отдел": "HR",          "Должность": "HR-менеджер",     "Оклад": 85000,  "Начало": 1},
    {"ID": 5, "ФИО": "Волков Алексей Дмитриевич", "Отдел": "Продажи",     "Должность": "Менеджер продаж", "Оклад": 100000, "Начало": 1},
    {"ID": 6, "ФИО": "Лебедев Дмитрий Олегович",  "Отдел": "Маркетинг",   "Должность": "Маркетолог",      "Оклад": 110000, "Начало": 1},
    {"ID": 7, "ФИО": "Кузнецова Елена Викторовна","Отдел": "Продажи",     "Должность": "Ст. менеджер",    "Оклад": 130000, "Начало": 1},
    {"ID": 8, "ФИО": "Новиков Николай Андреевич", "Отдел": "IT",          "Должность": "Тестировщик",     "Оклад": 95000,  "Начало": 1},
    {"ID": 9, "ФИО": "Соколова Ольга Николаевна", "Отдел": "Бухгалтерия", "Должность": "Гл. бухгалтер",   "Оклад": 170000, "Начало": 1},
    {"ID": 10,"ФИО": "Павлов Сергей Владимирович","Отдел": "Маркетинг",   "Должность": "Дизайнер",        "Оклад": 105000, "Начало": 1},
    {"ID": 11,"ФИО": "Тихонов Роман Игоревич",    "Отдел": "IT",          "Должность": "Аналитик",        "Оклад": 120000, "Начало": 6},
]

VARIANTS = {
    1: ["Петров Петр Петрович", "Петров П.П.", "Петров Пётр Петрович", "П. Петров"],
    2: ["Сидорова Анна Ивановна", "Сидорова А.И.", "А. Сидорова"],
    3: ["Козлов Иван Сергеевич", "Козлов И.С.", "И. Козлов", "Козлов Иван"],
    4: ["Морозова Мария Алексеевна", "Морозова М.А.", "М. Морозова"],
    5: ["Волков Алексей Дмитриевич", "Волков А.Д.", "А. Волков"],
    6: ["Лебедев Дмитрий Олегович", "Лебедев Д.О.", "Д. Лебедев", "Лебедев Дмитрий"],
    7: ["Кузнецова Елена Викторовна", "Кузнецова Е.В.", "Е. Кузнецова"],
    8: ["Новиков Николай Андреевич", "Новиков Н.А.", "Н. Новиков"],
    9: ["Соколова Ольга Николаевна", "Соколова О.Н.", "О. Соколова"],
    10: ["Павлов Сергей Владимирович", "Павлов С.В.", "С. Павлов"],
    11: ["Тихонов Роман Игоревич", "Тихонов Р.И.", "Р. Тихонов"],
}

MONTHS = [
    ("Январь", 1), ("Февраль", 2), ("Март", 3), ("Апрель", 4),
    ("Май", 5), ("Июнь", 6), ("Июль", 7), ("Август", 8),
    ("Сентябрь", 9), ("Октябрь", 10), ("Ноябрь", 11), ("Декабрь", 12),
]

random.seed(42)


def generate_sick_periods():
    sick_periods = {}
    
    for employee in EMPLOYEES:
        emp_id = employee["ID"]
        periods = []
        
        if random.random() < 0.3:
            earliest_sick = employee["Начало"]
            latest_sick = min(10, 12)
            
            if earliest_sick <= latest_sick:
                sick_start = random.randint(earliest_sick, latest_sick)
                duration = random.randint(1, 3)
                periods.append((sick_start, duration))
        
        sick_periods[emp_id] = periods
    
    return sick_periods


def is_on_sick_leave(employee_id, month, sick_periods):
    for start_month, duration in sick_periods.get(employee_id, []):
        if start_month <= month < start_month + duration:
            return True
    return False


def calculate_bonus(employee, month_number):
    bonus = 0
    name = employee["ФИО"]
    
    is_male = any(word in name for word in ["Петрович", "Сергеевич", "Иванович", 
                                             "Дмитриевич", "Андреевич", "Владимирович", 
                                             "Олегович", "Николаевич", "Игоревич"])
    
    if month_number == 12:
        bonus += int(employee["Оклад"] * 0.5)
    
    if month_number == 2 and is_male:
        bonus += 10000
    
    if month_number == 3 and not is_male:
        bonus += 10000
    
    if month_number in [3, 6, 9, 12] and random.random() < 0.3:
        bonus += int(employee["Оклад"] * 0.2)
    
    return bonus


print("🏥 Генерирую периоды больничных...\n")
sick_periods = generate_sick_periods()

for emp_id, periods in sick_periods.items():
    if periods:
        employee = next(e for e in EMPLOYEES if e["ID"] == emp_id)
        for start_month, duration in periods:
            month_name = MONTHS[start_month - 1][0]
            print(f"   {employee['ФИО']:<35} будет на больничном с {month_name} ({duration} мес.)")

print()

for month_name, month_number in MONTHS:
    data = []
    pay_date = f"2024-{month_number:02d}-25"
    
    for employee in EMPLOYEES:
        if month_number < employee["Начало"]:
            continue
        
        if is_on_sick_leave(employee["ID"], month_number, sick_periods):
            continue
        
        base_salary = employee["Оклад"]
        bonus = calculate_bonus(employee, month_number)
        total = base_salary + bonus
        
        fio_variant = random.choice(VARIANTS[employee["ID"]])
        
        data.append({
            "ID": employee["ID"],
            "ФИО": fio_variant,
            "Отдел": employee["Отдел"],
            "Должность": employee["Должность"],
            "Оклад": base_salary,
            "Премия": bonus,
            "Итого": total,
            "Дата выплаты": pay_date
        })
    
    df = pd.DataFrame(data)
    filename = f"Зарплата_{month_name}_2024.xlsx"
    df.to_excel(test_folder / filename, index=False)
    
    month_total = df["Итого"].sum()
    print(f"✅ {filename:<30} | Выплачено: {month_total:>12,} ₽ | Сотрудников: {len(df)}")

print("\n" + "=" * 70)
print(f"📁 Все 12 файлов созданы в папке: {test_folder.absolute()}")
print("=" * 70)
#Made by https://github.com/Serega210810