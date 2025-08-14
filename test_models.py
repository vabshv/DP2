import unittest
from models import Customer, Product, Order


class TestModels(unittest.TestCase):
    """Простые тесты для моделей данных"""

    def test_customer(self):
        """Тест создания клиента"""
        # Создаем клиента
        customer = Customer(
            id=1,
            name="Иван Иванов",
            phone="+79161234567",
            email="ivan@example.com",
            address="Москва"
        )

        # Проверяем, что данные сохранились правильно
        self.assertEqual(customer.id, 1)
        self.assertEqual(customer.name, "Иван Иванов")
        self.assertEqual(customer.phone, "+79161234567")
        self.assertEqual(customer.email, "ivan@example.com")
        self.assertEqual(customer.address, "Москва")

    def test_product(self):
        """Тест создания товара"""
        # Создаем товар
        product = Product(
            id=101,
            name="Ноутбук",
            price=49999.99
        )

        # Проверяем данные
        self.assertEqual(product.id, 101)
        self.assertEqual(product.name, "Ноутбук")
        self.assertEqual(product.price, 49999.99)

    def test_order(self):
        """Тест создания заказа"""
        # Создаем заказ
        order = Order(
            id=1001,
            customer_id=1,
            product_id=101,
            date="2023-10-15"
        )

        # Проверяем данные
        self.assertEqual(order.id, 1001)
        self.assertEqual(order.customer_id, 1)
        self.assertEqual(order.product_id, 101)
        self.assertEqual(order.date, "2023-10-15")


if __name__ == "__main__":
    # Запускаем все тесты
    unittest.main()