"""
Модуль для работы с базой данных SQLite
Создает и инициализирует БД, выполняет операции
"""
import sqlite3
import os

DB_NAME = "store.db"


def init_db():
    """Создает базу данных и таблицы, если они не существуют"""
    if not os.path.exists(DB_NAME): # существует ли файл базы данных с именем DB_NAME
        conn = sqlite3.connect(DB_NAME)  # Если база данных не существует, подключаемся к новой пустой базе
        c = conn.cursor() # Получаем объект cursor, используемый для выполнения SQL-запросов


        # Создание таблицы "customers" (клиенты)
        # Столбцы:
        #   id           - уникальный идентификатор клиента, автоматически увеличивается
        #   name         - название или ФИО клиента (обязательно должно быть заполнено)
        #   phone        - телефон клиента (может быть пустым)
        #   email        - электронная почта клиента (может быть пустым)
        #   address      - адрес клиента (может быть пустым)

        c.execute('''CREATE TABLE IF NOT EXISTS customers (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     phone TEXT,
                     email TEXT,
                     address TEXT)''')

        # Создание таблицы "products" (товары)
        # Столбцы:
        #   id       - уникальный идентификатор товара, автоматически увеличивается
        #   name     - название товара (обязательно должно быть заполнено)
        #   price    - цена товара (число с плавающей точкой)

        c.execute('''CREATE TABLE IF NOT EXISTS products (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     price REAL)''')

        # Создание таблицы "orders" (заказы)
        # Столбцы:
        #   id              - уникальный идентификатор заказа, автоматически увеличивается
        #   customer_id     - внешний ключ, ссылающийся на таблицу customers.id
        #   product_id      - внешний ключ, ссылающийся на таблицу products.id
        #   date            - дата оформления заказа (текстовая строка формата ГГГГ-ММ-ДД)

        c.execute('''CREATE TABLE IF NOT EXISTS orders (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     customer_id INTEGER NOT NULL,
                     product_id INTEGER NOT NULL,
                     date TEXT NOT NULL,
                     FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                     FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE)''')

        conn.commit() # Подтверждаем изменения в базе данных
        conn.close() # Закрываем соединение с базой данных
        print("База данных создана успешно!")


# Общие функции для работы с БД

# Функция для выполнения любых SQL-запросов, которые изменяют базу данных (INSERT/UPDATE/DELETE)
def execute_query(query, params=()):
    """Выполняет SQL запрос с параметрами"""
    conn = sqlite3.connect(DB_NAME) # Открываем соединение с базой данных
    c = conn.cursor() # Получаем курсор для выполнения SQL-команд
    try: # код, в котором может возникнуть исключение
        c.execute(query, params) # Выполняем SQL-запрос с предоставленными параметрами
        conn.commit() # Сохраняем изменения в базе данных
        last_id = c.lastrowid  # Получаем идентификатор последней вставленной записи
        return last_id
    except sqlite3.Error as e: # код для обработки исключений
        print(f"Ошибка базы данных: {e}") # Если произошла ошибка, печатаем её и возвращаем None
        return None
    finally: # выполняется всегда, независимо от того, возникло исключение или нет
        conn.close() # Обязательно закрываем соединение с базой данных


# Функция для выполнения SELECT-запросов и возврата всех полученных данных
def fetch_query(query, params=()):
    """Выполняет SELECT запрос и возвращает все результаты"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(query, params)
        return c.fetchall()     # Возвращаем все полученные строки
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return [] # возвращаем пустой список, если ошибка
    finally:
        conn.close()


# Функции для работы с клиентами

# Общая функция для получения всех клиентов из базы данных
def get_all_customers():
    """Возвращает всех клиентов"""
    return fetch_query("SELECT * FROM customers") # Используем fetch_query для получения всех клиентов

# Добавляем нового клиента в базу данных
def add_customer(customer):
    """Добавляет нового клиента"""
    query = "INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)"
    # Передаем значения объекта customer в качестве параметров
    return execute_query(query, (customer.name, customer.phone, customer.email, customer.address))

# Обновляем информацию о клиенте в базе данных
def update_customer(customer):
    """Обновляет данные клиента"""
    query = "UPDATE customers SET name=?, phone=?, email=?, address=? WHERE id=?"
    # Передаем новые свойства клиента и его идентификатор
    execute_query(query, (customer.name, customer.phone, customer.email, customer.address, customer.id))

# Удаляем клиента из базы данных по его идентификатору
def delete_customer(customer_id):
    """Удаляет клиента по ID"""
    execute_query("DELETE FROM customers WHERE id=?", (customer_id,))


# Функции для работы с товарами

# Получаем все товары из базы данных
def get_all_products():
    """Возвращает все товары"""
    return fetch_query("SELECT * FROM products")

# Добавляем новый товар в базу данных
def add_product(product):
    """Добавляет новый товар"""
    query = "INSERT INTO products (name, price) VALUES (?, ?)"
    return execute_query(query, (product.name, product.price))

# Обновляем информацию о товаре в базе данных
def update_product(product):
    """Обновляет данные товара"""
    query = "UPDATE products SET name=?, price=? WHERE id=?"
    execute_query(query, (product.name, product.price, product.id))

# Удаляем товар из базы данных по его идентификатору
def delete_product(product_id):
    """Удаляет товар по ID"""
    execute_query("DELETE FROM products WHERE id=?", (product_id,))


# Функции для работы с заказами

# Получаем все заказы из базы данных с присоединенными данными о клиенте и товаре
def get_all_orders():
    """Возвращает все заказы с дополнительной информацией о клиенте и товаре"""
    # Формируем сложный SQL-запрос с использованием JOIN для объединения нескольких таблиц
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

# Добавляем новый заказ в базу данных
def add_order(order):
    """Добавляет новый заказ"""
    query = "INSERT INTO orders (customer_id, product_id, date) VALUES (?, ?, ?)"
    return execute_query(query, (order.customer_id, order.product_id, order.date))

# Обновляем информацию о заказе в базе данных
def update_order(order):
    """Обновляет данные заказа"""
    query = "UPDATE orders SET customer_id=?, product_id=?, date=? WHERE id=?"
    execute_query(query, (order.customer_id, order.product_id, order.date, order.id))

# Удаляем заказ из базы данных по его идентификатору
def delete_order(order_id):
    """Удаляет заказ по ID"""
    execute_query("DELETE FROM orders WHERE id=?", (order_id,))


# Инициализация БД при запуске модуля
init_db()