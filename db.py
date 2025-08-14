"""
Модуль для работы с базой данных SQLite
Создает и инициализирует БД, выполняет CRUD операции
"""
import sqlite3
import os

DB_NAME = "store.db"


def init_db():
    """Создает базу данных и таблицы, если они не существуют"""
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # Таблица клиентов
        c.execute('''CREATE TABLE IF NOT EXISTS customers (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     phone TEXT,
                     email TEXT,
                     address TEXT)''')

        # Таблица товаров
        c.execute('''CREATE TABLE IF NOT EXISTS products (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     price REAL)''')

        # Таблица заказов
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     customer_id INTEGER NOT NULL,
                     product_id INTEGER NOT NULL,
                     date TEXT NOT NULL,
                     FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                     FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE)''')

        conn.commit()
        conn.close()
        print("База данных создана успешно!")


# Общие функции для работы с БД
def execute_query(query, params=()):
    """Выполняет SQL запрос с параметрами"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(query, params)
        conn.commit()
        last_id = c.lastrowid
        return last_id
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None
    finally:
        conn.close()


def fetch_query(query, params=()):
    """Выполняет SELECT запрос и возвращает все результаты"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(query, params)
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return []
    finally:
        conn.close()


# Функции для работы с клиентами
def get_all_customers():
    """Возвращает всех клиентов"""
    return fetch_query("SELECT * FROM customers")


def add_customer(customer):
    """Добавляет нового клиента"""
    query = "INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)"
    return execute_query(query, (customer.name, customer.phone, customer.email, customer.address))


def update_customer(customer):
    """Обновляет данные клиента"""
    query = "UPDATE customers SET name=?, phone=?, email=?, address=? WHERE id=?"
    execute_query(query, (customer.name, customer.phone, customer.email, customer.address, customer.id))


def delete_customer(customer_id):
    """Удаляет клиента по ID"""
    execute_query("DELETE FROM customers WHERE id=?", (customer_id,))


# Функции для работы с товарами
def get_all_products():
    """Возвращает все товары"""
    return fetch_query("SELECT * FROM products")


def add_product(product):
    """Добавляет новый товар"""
    query = "INSERT INTO products (name, price) VALUES (?, ?)"
    return execute_query(query, (product.name, product.price))


def update_product(product):
    """Обновляет данные товара"""
    query = "UPDATE products SET name=?, price=? WHERE id=?"
    execute_query(query, (product.name, product.price, product.id))


def delete_product(product_id):
    """Удаляет товар по ID"""
    execute_query("DELETE FROM products WHERE id=?", (product_id,))


# Функции для работы с заказами
def get_all_orders():
    """Возвращает все заказы с дополнительной информацией о клиенте и товаре"""
    query = """
    SELECT orders.id, 
           customers.name, 
           customers.phone, 
           products.name, 
           products.price, 
           orders.date 
    FROM orders
    JOIN customers ON customers.id = orders.customer_id
    JOIN products ON products.id = orders.product_id
    """
    return fetch_query(query)


def add_order(order):
    """Добавляет новый заказ"""
    query = "INSERT INTO orders (customer_id, product_id, date) VALUES (?, ?, ?)"
    return execute_query(query, (order.customer_id, order.product_id, order.date))


def update_order(order):
    """Обновляет данные заказа"""
    query = "UPDATE orders SET customer_id=?, product_id=?, date=? WHERE id=?"
    execute_query(query, (order.customer_id, order.product_id, order.date, order.id))


def delete_order(order_id):
    """Удаляет заказ по ID"""
    execute_query("DELETE FROM orders WHERE id=?", (order_id,))


# Инициализация БД при запуске модуля
init_db()