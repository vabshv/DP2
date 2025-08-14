import unittest
import os
import sqlite3
from analysis import generate_sales_report, generate_orders_dynamics


class TestAnalysis(unittest.TestCase):
    """Тесты для генерации отчетов"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        # Создаем временную базу данных в памяти
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        # Создаем таблицы
        self.cursor.execute('''CREATE TABLE products (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            price REAL)''')

        self.cursor.execute('''CREATE TABLE orders (
                            id INTEGER PRIMARY KEY,
                            customer_id INTEGER,
                            product_id INTEGER,
                            date TEXT)''')

        # Добавляем тестовые данные
        products = [
            (1, "Ноутбук", 50000),
            (2, "Смартфон", 30000),
        ]
        self.cursor.executemany("INSERT INTO products VALUES (?, ?, ?)", products)

        orders = [
            (1, 1, 1, "2023-10-01"),
            (2, 1, 2, "2023-10-02"),
            (3, 1, 1, "2023-10-03"),
        ]
        self.cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
        self.conn.commit()

        # Сохраняем тестовую БД во временный файл
        self.test_db = "test_store.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        new_conn = sqlite3.connect(self.test_db)
        self.conn.backup(new_conn)
        new_conn.close()

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временную БД
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        # Удаляем созданные отчеты
        for file in os.listdir():
            if file.startswith("top_products_") and file.endswith(".png"):
                os.remove(file)
            if file.startswith("orders_dynamics_") and file.endswith(".png"):
                os.remove(file)

    def test_sales_report(self):
        """Тест генерации отчета по продажам"""
        # Генерируем отчет
        filename = generate_sales_report()

        # Проверяем что функция вернула имя файла
        self.assertIsInstance(filename, str)

        # Проверяем что файл существует
        self.assertTrue(os.path.exists(filename))

        # Проверяем что файл не пустой
        self.assertGreater(os.path.getsize(filename), 1000)

    def test_orders_dynamics(self):
        """Тест генерации отчета по динамике заказов"""
        # Генерируем отчет
        filename = generate_orders_dynamics()

        # Проверяем что функция вернула имя файла
        self.assertIsInstance(filename, str)

        # Проверяем что файл существует
        self.assertTrue(os.path.exists(filename))

        # Проверяем что файл не пустой
        self.assertGreater(os.path.getsize(filename), 1000)


if __name__ == "__main__":
    # Запускаем все тесты
    unittest.main()