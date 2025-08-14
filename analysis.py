"""
Модуль для генерации отчетов и визуализации данных
Использует matplotlib для создания графиков
"""
import matplotlib.pyplot as plt
import db
from datetime import datetime


def generate_sales_report():
    """
    Генерирует отчет по топу товаров по количеству заказов
    Возвращает имя файла с отчетом
    """
    # Получаем данные из БД
    query = """
    SELECT products.name, COUNT(orders.id) as order_count
    FROM orders
    JOIN products ON products.id = orders.product_id
    GROUP BY products.name
    ORDER BY order_count DESC
    LIMIT 10
    """
    data = db.fetch_query(query)

    if not data:
        return "Нет данных для отчета"

    # Подготовка данных для графика
    product_names = [item[0] for item in data]
    order_counts = [item[1] for item in data]

    # Создание графика
    plt.figure(figsize=(12, 6))
    plt.bar(product_names, order_counts, color='skyblue')
    plt.title('Топ 10 товаров по количеству заказов', fontsize=14)
    plt.xlabel('Товар', fontsize=12)
    plt.ylabel('Количество заказов', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    # Сохранение в файл
    filename = f"top_products_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    plt.savefig(filename)
    plt.close()

    return filename


def generate_orders_dynamics():
    """
    Генерирует отчет по динамике заказов за последние 30 дней
    Возвращает имя файла с отчетом
    """
    # Получаем данные из БД за последние 30 дней
    query = """
    SELECT date, COUNT(id) as order_count
    FROM orders
    WHERE date >= date('now', '-30 days')
    GROUP BY date
    ORDER BY date
    """
    data = db.fetch_query(query)

    if not data:
        return "Нет данных для отчета"

    # Подготовка данных для графика
    dates = [datetime.strptime(item[0], "%Y-%m-%d") for item in data]
    order_counts = [item[1] for item in data]

    # Создание графика
    plt.figure(figsize=(12, 6))
    plt.plot(dates, order_counts, marker='o', linestyle='-', color='green')
    plt.title('Динамика заказов за последние 30 дней', fontsize=14)
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Количество заказов', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Форматирование дат на оси X
    plt.gcf().autofmt_xdate()

    # Сохранение в файл
    filename = f"orders_dynamics_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    plt.savefig(filename)
    plt.close()

    return filename