"""
Классы для представления данных приложения:
- Customer (Клиент)
- Product (Товар)
- Order (Заказ)
"""

class Customer:
    """Класс для представления клиента"""
    def __init__(self, id=None, name="", phone="", email="", address=""): # Конструктор класса, принимающий параметры для инициализации объекта.
        self.id = id          # Уникальный идентификатор
        self.name = name      # ФИО клиента
        self.phone = phone    # Номер телефона
        self.email = email    # Email адрес
        self.address = address  # Адрес доставки

    # Специальный метод, определяющий строку, которую вернет объект при выводе
    # Используется для удобного вывода информации о клиенте
    def __repr__(self):
        return f"Customer(id={self.id}, name={self.name})"

class Product:
    """Класс для представления товара"""
    def __init__(self, id=None, name="", price=0.0):
        self.id = id        # Уникальный идентификатор
        self.name = name    # Название товара
        self.price = price  # Цена товара

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price})"

class Order:
    """Класс для представления заказа"""
    def __init__(self, id=None, customer_id=None, product_id=None, date=""):
        self.id = id              # Уникальный идентификатор
        self.customer_id = customer_id  # ID клиента
        self.product_id = product_id    # ID товара
        self.date = date          # Дата заказа в формате ГГГГ-ММ-ДД

    def __repr__(self):
        return f"Order(id={self.id}, customer_id={self.customer_id}, product_id={self.product_id}, date={self.date})"