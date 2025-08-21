import unittest
import os
import sqlite3
from analysis import generate_sales_report, generate_orders_dynamics


class TestAnalysis(unittest.TestCase):
    """Тесты для генерации отчетов"""

    def tearDown(self):
        # """Очистка после каждого теста"""
        # Удаляем созданные отчеты (графики), чтобы не засорять папку
        for file in os.listdir():
            if file.startswith("top_товаров_") and file.endswith(".png"):
                os.remove(file)
            if file.startswith("динамика_заказов_") and file.endswith(".png"):
                os.remove(file)

    def test_sales_report(self):
        """Тест генерации отчета по продажам"""
        # Вызываем тестируемую функцию
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