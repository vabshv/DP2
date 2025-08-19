"""
Модуль для генерации отчетов и визуализации данных
Использует matplotlib для создания графиков
"""
import matplotlib.pyplot as plt # Библиотека для построения графиков
import db
from datetime import datetime # Модуль для работы с датами и временем



def generate_sales_report():
    """
    Генерирует отчет по топу товаров по количеству заказов
    Возвращает имя файла с отчетом
    """
    # Получаем данные из БД
    # Получаем количество заказов по каждому товару и сортируем по убыванию количества
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
    # Разделяем данные на названия товаров и количество заказов
    product_names = [item[0] for item in data] # Список наименований товаров
    order_counts = [item[1] for item in data]  # Список количеств заказов

    # Создание графика
    plt.figure(figsize=(12, 6)) # Устанавливаем размер графика (ширина x высота)
    # Строим гистограмму
    plt.bar(product_names, order_counts, color='skyblue')  # Отображаем столбцы товаров разного цвета
    plt.title('Топ 10 товаров по количеству заказов', fontsize=14) # Заголовок графика
    plt.xlabel('Товар', fontsize=12) # Надпись на оси X
    plt.ylabel('Количество заказов', fontsize=12) # Надпись на оси Y
    plt.xticks(rotation=45, ha='right', fontsize=10)  # Наклон меток на оси X для удобства чтения
    plt.tight_layout()  # Автоматически настраивает расположение элементов графика

    # Генерация имени файла с указанием текущего времени
    filename = f"top_товаров_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    plt.savefig(filename) # Сохраняем график в PNG-файл
    plt.close() # Очищаем графику для последующих построений

    return filename # Возвращаем имя файла с отчётом


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
        return "Нет данных для отчета" # Если данных нет, выдаём сообщение

    # Подготовка данных для графика
    dates = [datetime.strptime(item[0], "%Y-%m-%d") for item in data] # Массив дат
    order_counts = [item[1] for item in data] # Массив чисел заказов

    # Создание графика
    plt.figure(figsize=(12, 6)) # Размер графика

    # Рисуем линию динамики заказов (line plot)
    plt.plot(dates, order_counts, marker='o', linestyle='-', color='green') # Линия зелёного цвета с маркерами точек
    plt.title('Динамика заказов за последние 30 дней', fontsize=14) # Заголовок графика
    plt.xlabel('Дата', fontsize=12) # Метка оси X
    plt.ylabel('Количество заказов', fontsize=12) # Метка оси Y
    plt.grid(True, linestyle='--', alpha=0.7)  # Включаем сетку на график
    plt.tight_layout() # Оптимально размещаем элементы графика

    # Форматирование дат на оси X
    plt.gcf().autofmt_xdate() # Автоформатирование расположения дат на оси X

    # Сохранение в файл
    filename = f"динамика_заказов_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
    plt.savefig(filename) # Сохраняем график в PNG-файл
    plt.close()  # Очищаем графику

    return filename # Возвращаем имя файла с отчётом