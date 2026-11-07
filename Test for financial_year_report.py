import pandas as pd
import random
from pathlib import Path

# Создаём папку для тестовых файлов
test_folder = Path("test_files_year")
test_folder.mkdir(exist_ok=True)

print("📝 Создаю тестовые Excel файлы за 12 месяцев...\n")

# Месяцы и их "коэффициенты активности" (сезонность)
# Январь — спад после праздников, декабрь — пик
MONTHS = [
    ("Январь", 0.7),
    ("Февраль", 0.85),
    ("Март", 0.95),
    ("Апрель", 1.0),
    ("Май", 0.9),
    ("Июнь", 1.0),
    ("Июль", 0.85),
    ("Август", 0.95),
    ("Сентябрь", 1.1),
    ("Октябрь", 1.15),
    ("Ноябрь", 1.25),
    ("Декабрь", 1.5)
]

# Категории доходов
INCOME_CATEGORIES = [
    ("Продажа товаров", 150000, 250000),
    ("Услуги", 80000, 150000),
    ("Консультации", 40000, 90000),
    ("Подписка", 30000, 60000)
]

# Категории расходов
EXPENSE_CATEGORIES = [
    ("Зарплаты", 120000, 180000),
    ("Аренда офиса", 50000, 50000),
    ("Закупка товаров", 60000, 120000),
    ("Маркетинг", 30000, 70000),
    ("Налоги", 25000, 45000),
    ("Коммунальные услуги", 15000, 25000)
]

# Фиксируем случайность для воспроизводимости
random.seed(42)


def generate_month_data(month_name, coefficient):
    """
    Генерирует данные за один месяц с учётом сезонности.
    
    Аргументы:
        month_name: название месяца
        coefficient: коэффициент активности (0.7 - спад, 1.5 - пик)
    
    Возвращает:
        DataFrame с данными за месяц
    """
    data = []
    
    # Генерируем доходы (5-8 операций за месяц)
    num_income = random.randint(5, 8)
    for _ in range(num_income):
        category, min_val, max_val = random.choice(INCOME_CATEGORIES)
        
        # Базовая сумма * коэффициент сезонности + небольшой шум
        base_amount = random.randint(min_val, max_val)
        amount = int(base_amount * coefficient * random.uniform(0.9, 1.1))
        
        # Случайный день месяца
        day = random.randint(1, 28)
        date = f"2024-{MONTHS.index((month_name, coefficient)) + 1:02d}-{day:02d}"
        
        data.append({
            "Дата": date,
            "Тип": "Доход",
            "Категория": category,
            "Сумма": amount,
            "Комментарий": f"{category} за {day} число"
        })
    
    # Генерируем расходы (6-9 операций за месяц)
    num_expense = random.randint(6, 9)
    for _ in range(num_expense):
        category, min_val, max_val = random.choice(EXPENSE_CATEGORIES)
        
        # Расходы тоже зависят от сезона, но меньше
        base_amount = random.randint(min_val, max_val)
        amount = int(base_amount * random.uniform(0.95, 1.05))
        
        day = random.randint(1, 28)
        date = f"2024-{MONTHS.index((month_name, coefficient)) + 1:02d}-{day:02d}"
        
        data.append({
            "Дата": date,
            "Тип": "Расход",
            "Категория": category,
            "Сумма": amount,
            "Комментарий": f"{category} за {day} число"
        })
    
    # Сортируем по дате
    df = pd.DataFrame(data)
    df = df.sort_values("Дата").reset_index(drop=True)
    
    return df


# === СОЗДАЁМ 12 ФАЙЛОВ ===
total_income = 0
total_expense = 0

for month_name, coefficient in MONTHS:
    # Генерируем данные
    df = generate_month_data(month_name, coefficient)
    
    # Считаем итоги месяца
    month_income = df[df["Тип"] == "Доход"]["Сумма"].sum()
    month_expense = df[df["Тип"] == "Расход"]["Сумма"].sum()
    month_profit = month_income - month_expense
    
    total_income += month_income
    total_expense += month_expense
    
    # Сохраняем в Excel
    filename = f"Финансы_{month_name}_2024.xlsx"
    df.to_excel(test_folder / filename, index=False)
    
    print(f"✅ {filename:<30} | Доход: {month_income:>10,} ₽ | Расход: {month_expense:>10,} ₽ | Прибыль: {month_profit:>10,} ₽")

# === ИТОГ ===
year_profit = total_income - total_expense

print("\n" + "=" * 90)
print(f"📊 ИТОГИ ГОДА:")
print(f"   💰 Общий доход:    {total_income:>12,} ₽")
print(f"   💸 Общие расходы:  {total_expense:>12,} ₽")
print(f"   📈 Чистая прибыль: {year_profit:>12,} ₽")
print("=" * 90)
print(f"\n📁 Все 12 файлов созданы в папке: {test_folder.absolute()}")
print("\nТеперь запусти программу объединения и укажи этот путь!")
#Made by https://github.com/Serega210810