"""
Основной модуль графического интерфейса приложения
Использует Tkinter для создания оконного приложения
"""
import tkinter as tk # Базовый модуль для GUI
from tkinter import ttk, messagebox, filedialog # Виджеты, диалоговые окна
import db
import csv # Работа с CSV-файлами
from datetime import datetime # Работа с датами
from analysis import generate_sales_report, generate_orders_dynamics
from models import Customer, Product, Order  # Импорт классов моделей
import re  # для работы с регулярными выражениями


def is_valid_email(email): # Проверяет корректность email с помощью регулярного выражения
    if not email:
        return True  # Пустой email считается валидным
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None # пытается применить шаблон (pattern) к строке (email), is not None' преобразует результат в булево значение

class EditCustomerDialog(tk.Toplevel): # Диалоговое окно для добавления/редактирования клиента

    def __init__(self, parent, customer=None): # Конструктор класса для инициализации нового экземпляра
        super().__init__(parent)
        self.parent = parent # Сохранение ссылки на родительский виджет
        self.customer = customer # Сохранение объекта клиента

        self.title("Редактирование клиента" if customer else "Добавление клиента") # Динамическое определение заголовка окна: Если передан объект customer (режим редактирования), устанавливаем заголовок "Редактирование клиента", Если customer отсутствует (None, режим создания), устанавливаем "Добавление клиента"
        self.geometry("400x300") # Установка начального размера окна:
        self.resizable(False, False) # Запрет изменения размера окна: ширины, высоты

        # Создаем элементы формы
        # Создание и размещение меток для формы ввода данных клиента
        tk.Label(self, text="ФИО:").grid(row=0, column=0, padx=10, pady=10, sticky="e") # row=0, column=0 - первая строка, первый столбец, padx=10, pady=10 - внешние отступы по 10 пикселей по горизонтали и вертикали sticky="e" - выравнивание по правому краю (east) внутри ячейки сетки
        tk.Label(self, text="Телефон:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self, text="Email:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self, text="Адрес:").grid(row=3, column=0, padx=10, pady=10, sticky="e")

        # Создание полей ввода (Entry) для формы
        # Каждое поле соответствует своей метке в той же строке
        self.name_entry = tk.Entry(self, width=30)
        self.phone_entry = tk.Entry(self, width=30)
        self.email_entry = tk.Entry(self, width=30)
        self.address_entry = tk.Entry(self, width=30)

        # Размещение полей ввода в сетке формы
        # Все поля находятся в колонке 1 (справа от меток)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.phone_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.email_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.address_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Заполняем поля, если редактируем существующего клиента
        if customer:
            # Заполнение поля данными из объекта клиента
            # insert(0, value) - вставка текста в начало поля (позиция 0)
            self.name_entry.insert(0, customer.name)
            self.phone_entry.insert(0, customer.phone)
            self.email_entry.insert(0, customer.email)
            self.address_entry.insert(0, customer.address)

        # Кнопки сохранения/отмены
        btn_frame = tk.Frame(self) # Создаем фрейм для группировки кнопок
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20) # Размещаем фрейм с кнопками в сетке: row=4 - пятая строка (после полей ввода),  column=0 - начиная с первой колонки, columnspan=2 - объединяет две колонки (чтобы кнопки были по центру формы), 20 отступ.

        tk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=10) # Создаем кнопку "Сохранить" внутри фрейма кнопок, command=self.save - привязка к методу save() текущего класса
        tk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=10) # Создаем кнопку "Отмена" внутри фрейма кнопок

    def save(self):
        # Собирает данные из формы и сохраняет клиента
        #   - get(): получение текущего текста из поля ввода
        #   - strip(): удаление пробельных символов в начале и конце строки
        #   - Результат сохраняется в переменную
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get().strip()

        # Флаг для проверки валидности данных
        is_valid = True

        if not name:
            messagebox.showerror("Ошибка", "ФИО обязательно для заполнения")
            self.name_entry.focus_set()  # Устанавливаем фокус на поле
            is_valid = False

        # Проверка корректности email (только если поле не пустое)
        if email and not is_valid_email(email):
            messagebox.showerror(
                "Ошибка",
                "Некорректный формат email.\n"
                "Правильный формат: имя@домен.зона\n"
                "Пример: ivanov@example.com"
            )
            self.email_entry.focus_set()  # Устанавливаем фокус на поле
            is_valid = False

        # Если есть ошибки - не закрываем окно
        if not is_valid:
            return

        # Обновляем или создаем нового клиента
        if self.customer: # Обновляем
            self.customer.name = name
            self.customer.phone = phone
            self.customer.email = email
            self.customer.address = address
            db.update_customer(self.customer)
        else: # Создаем
            # Используем класс Customer из models.ry
            customer = Customer(name=name, phone=phone, email=email, address=address)
            db.add_customer(customer)

        self.parent.load_customers()
        self.destroy()



class EditProductDialog(tk.Toplevel): # Диалоговое окно для добавления/редактирования товара

    def __init__(self, parent, product=None):
        super().__init__(parent)
        self.parent = parent
        self.product = product

        self.title("Редактирование товара" if product else "Добавление товара")
        self.geometry("400x200")
        self.resizable(False, False)

        # Создаем элементы формы
        tk.Label(self, text="Название:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self, text="Цена:").grid(row=1, column=0, padx=10, pady=10, sticky="e")

        self.name_entry = tk.Entry(self, width=30)
        self.price_entry = tk.Entry(self, width=30)

        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.price_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Заполняем поля, если редактируем существующий товар
        if product:
            self.name_entry.insert(0, product.name)
            self.price_entry.insert(0, str(product.price))

        # Кнопки сохранения/отмены
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=10)

    def save(self):
        """Собирает данные из формы и сохраняет товар"""
        name = self.name_entry.get().strip()
        price_str = self.price_entry.get().strip()

        if not name:
            messagebox.showerror("Ошибка", "Название обязательно для заполнения")
            return

        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError("Цена должна быть положительным числом")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректная цена. Введите число (например: 199.99)")
            return

        # Обновляем или создаем новый товар
        if self.product:
            self.product.name = name
            self.product.price = price
            db.update_product(self.product)
        else:
            product = Product(name=name, price=price)
            db.add_product(product)

        self.parent.load_products()
        self.destroy()


class EditOrderDialog(tk.Toplevel):
    """Диалоговое окно для добавления/редактирования заказа"""

    def __init__(self, parent, order=None):
        super().__init__(parent)
        self.parent = parent
        self.order = order

        self.title("Редактирование заказа" if order else "Добавление заказа")
        self.geometry("500x300")
        self.resizable(False, False)

        # Получаем данные для выпадающих списков
        self.customers = db.get_all_customers()
        self.products = db.get_all_products()

        # Создаем элементы формы
        tk.Label(self, text="Клиент:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self, text="Товар:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self, text="Дата заказа:").grid(row=2, column=0, padx=10, pady=10, sticky="e")

        # Выпадающий список для клиентов
        self.customer_var = tk.StringVar(self)
        self.customer_combobox = ttk.Combobox(self, textvariable=self.customer_var, width=40)

        # Формируем список для отображения и словарь для сопоставления
        self.customer_display = []
        self.customer_id_map = {}
        for c in self.customers:
            display_text = f"{c[1]} (ID: {c[0]}, тел: {c[2]})"
            self.customer_display.append(display_text)
            self.customer_id_map[display_text] = c[0]

        self.customer_combobox['values'] = self.customer_display
        self.customer_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Выпадающий список для товаров
        self.product_var = tk.StringVar(self)
        self.product_combobox = ttk.Combobox(self, textvariable=self.product_var, width=40)

        self.product_display = []
        self.product_id_map = {}
        for p in self.products:
            display_text = f"{p[1]} (ID: {p[0]}, цена: {p[2]} руб.)"
            self.product_display.append(display_text)
            self.product_id_map[display_text] = p[0]

        self.product_combobox['values'] = self.product_display
        self.product_combobox.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Поле для даты заказа
        self.date_entry = tk.Entry(self, width=30)
        self.date_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Текущая дата

        # Заполняем поля, если редактируем существующий заказ
        if order:
            # Находим клиента и товар по ID
            customer_display = next(
                (d for d, cid in self.customer_id_map.items() if cid == order.customer_id),
                None
            )

            product_display = next(
                (d for d, pid in self.product_id_map.items() if pid == order.product_id),
                None
            )

            if customer_display:
                self.customer_var.set(customer_display)
            if product_display:
                self.product_var.set(product_display)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, order.date)

        # Кнопки сохранения/отмены
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        tk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=10)

    def save(self):
        """Собирает данные из формы и сохраняет заказ"""
        customer_display = self.customer_var.get().strip()
        product_display = self.product_var.get().strip()
        date = self.date_entry.get().strip()

        if not customer_display or not product_display:
            messagebox.showerror("Ошибка", "Выберите клиента и товар")
            return

        # Получаем ID клиента и товара из словарей
        try:
            customer_id = self.customer_id_map.get(customer_display)
            product_id = self.product_id_map.get(product_display)

            if customer_id is None:
                raise ValueError("Не удалось определить ID клиента")
            if product_id is None:
                raise ValueError("Не удалось определить ID товара")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке данных: {str(e)}")
            return

        # Проверяем дату
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        # Обновляем или создаем новый заказ
        if self.order:
            self.order.customer_id = customer_id
            self.order.product_id = product_id
            self.order.date = date
            db.update_order(self.order)
        else:
            order = Order(customer_id=customer_id, product_id=product_id, date=date)
            db.add_order(order)

        self.parent.load_orders()
        self.destroy()

class App(tk.Tk):
    """Основной класс приложения"""

    def __init__(self):
        super().__init__()
        self.title("Менеджер интернет-магазина")
        self.geometry("1000x700")

        # Создаем вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаем фреймы для вкладок
        self.customer_tab = ttk.Frame(self.notebook)
        self.product_tab = ttk.Frame(self.notebook)
        self.order_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.customer_tab, text="Клиенты")
        self.notebook.add(self.product_tab, text="Товары")
        self.notebook.add(self.order_tab, text="Заказы")
        self.notebook.add(self.report_tab, text="Отчеты")

        # Инициализация вкладок
        self.init_customer_tab()
        self.init_product_tab()
        self.init_order_tab()
        self.init_report_tab()

    def init_customer_tab(self):
        """Инициализация вкладки с клиентами"""
        # Таблица для отображения клиентов
        columns = ("ID", "ФИО", "Телефон", "Email", "Адрес")
        self.customer_tree = ttk.Treeview(self.customer_tab, columns=columns, show="headings")

        # Настройка столбцов
        for col in columns:
            self.customer_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.customer_tree, c))
            self.customer_tree.column(col, width=150)

        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(self.customer_tab, orient=tk.VERTICAL, command=self.customer_tree.yview)
        self.customer_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.customer_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для кнопок
        btn_frame = tk.Frame(self.customer_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки операций
        tk.Button(btn_frame, text="Добавить", command=self.add_customer).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_customer).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_customer).pack(side=tk.LEFT, padx=5)

        # Кнопки импорта/экспорта
        tk.Button(btn_frame, text="Импорт CSV", command=self.import_customer_csv).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Экспорт CSV", command=self.export_customer_csv).pack(side=tk.RIGHT, padx=5)

        # Фрейм для фильтров
        filter_frame = tk.Frame(self.customer_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поля для фильтрации
        tk.Label(filter_frame, text="Фильтр по ФИО:").grid(row=0, column=0, padx=5)
        self.customer_name_filter = tk.Entry(filter_frame, width=20)
        self.customer_name_filter.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Телефон:").grid(row=0, column=2, padx=5)
        self.customer_phone_filter = tk.Entry(filter_frame, width=15)
        self.customer_phone_filter.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="Email:").grid(row=0, column=4, padx=5)
        self.customer_email_filter = tk.Entry(filter_frame, width=20)
        self.customer_email_filter.grid(row=0, column=5, padx=5)

        # Кнопка применения фильтра
        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_customer_filters).grid(row=0, column=6,
                                                                                                   padx=10)

        # Кнопка сброса фильтра
        tk.Button(filter_frame, text="Сбросить", command=self.reset_customer_filters).grid(row=0, column=7, padx=5)



        # Загрузка данных
        self.load_customers()

    def init_product_tab(self):
        """Инициализация вкладки с товарами"""
        # Таблица для отображения товаров
        columns = ("ID", "Название", "Цена")
        self.product_tree = ttk.Treeview(self.product_tab, columns=columns, show="headings")

        # Настройка столбцов
        for col in columns:
            self.product_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.product_tree, c))
            self.product_tree.column(col, width=150)

        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(self.product_tab, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.product_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для кнопок
        btn_frame = tk.Frame(self.product_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки операций
        tk.Button(btn_frame, text="Добавить", command=self.add_product).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_product).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_product).pack(side=tk.LEFT, padx=5)

        # Кнопки импорта/экспорта
        tk.Button(btn_frame, text="Импорт CSV", command=self.import_product_csv).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Экспорт CSV", command=self.export_product_csv).pack(side=tk.RIGHT, padx=5)

        # Фрейм для фильтров
        filter_frame = tk.Frame(self.product_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поля для фильтрации
        tk.Label(filter_frame, text="Название:").grid(row=0, column=0, padx=5)
        self.product_name_filter = tk.Entry(filter_frame, width=20)
        self.product_name_filter.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Цена от:").grid(row=0, column=2, padx=5)
        self.product_price_min_filter = tk.Entry(filter_frame, width=8)
        self.product_price_min_filter.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="до:").grid(row=0, column=4, padx=0)
        self.product_price_max_filter = tk.Entry(filter_frame, width=8)
        self.product_price_max_filter.grid(row=0, column=5, padx=5)

        # Кнопка применения фильтра
        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_product_filters).grid(row=0, column=6,
                                                                                                  padx=10)

        # Кнопка сброса фильтра
        tk.Button(filter_frame, text="Сбросить", command=self.reset_product_filters).grid(row=0, column=7, padx=5)

        # Загрузка данных
        self.load_products()

    def init_order_tab(self):
        """Инициализация вкладки с заказами"""
        # Таблица для отображения заказов
        columns = ("ID", "ФИО клиента", "Телефон", "Товар", "Цена", "Дата заказа")
        self.order_tree = ttk.Treeview(self.order_tab, columns=columns, show="headings")

        # Настройка столбцов
        for col in columns:
            self.order_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.order_tree, c))
            self.order_tree.column(col, width=150)

        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(self.order_tab, orient=tk.VERTICAL, command=self.order_tree.yview)
        self.order_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.order_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для кнопок
        btn_frame = tk.Frame(self.order_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки операций
        tk.Button(btn_frame, text="Добавить", command=self.add_order).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_order).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_order).pack(side=tk.LEFT, padx=5)

        # Кнопки импорта/экспорта
        tk.Button(btn_frame, text="Импорт CSV", command=self.import_order_csv).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Экспорт CSV", command=self.export_order_csv).pack(side=tk.RIGHT, padx=5)

        # Фрейм для фильтров
        filter_frame = tk.Frame(self.order_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поля для фильтрации
        tk.Label(filter_frame, text="Клиент:").grid(row=0, column=0, padx=5)
        self.order_customer_filter = tk.Entry(filter_frame, width=20)
        self.order_customer_filter.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Товар:").grid(row=0, column=2, padx=5)
        self.order_product_filter = tk.Entry(filter_frame, width=20)
        self.order_product_filter.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="Дата от:").grid(row=0, column=4, padx=5)
        self.order_date_min_filter = tk.Entry(filter_frame, width=10)
        self.order_date_min_filter.grid(row=0, column=5, padx=5)

        tk.Label(filter_frame, text="до:").grid(row=0, column=6, padx=0)
        self.order_date_max_filter = tk.Entry(filter_frame, width=10)
        self.order_date_max_filter.grid(row=0, column=7, padx=5)

        # Кнопка применения фильтра
        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_order_filters).grid(row=0, column=8,
                                                                                                padx=10)

        # Кнопка сброса фильтра
        tk.Button(filter_frame, text="Сбросить", command=self.reset_order_filters).grid(row=0, column=9, padx=5)

        # Загрузка данных
        self.load_orders()

    def init_report_tab(self):
        """Инициализация вкладки с отчетами"""
        # Фрейм для кнопок генерации отчетов
        btn_frame = tk.Frame(self.report_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=20)

        # Кнопки генерации отчетов
        tk.Button(btn_frame, text="Топ товаров",
                  command=lambda: self.generate_report("top_products")).pack(side=tk.LEFT, padx=10, pady=5)

        tk.Button(btn_frame, text="Динамика заказов",
                  command=lambda: self.generate_report("orders_dynamics")).pack(side=tk.LEFT, padx=10, pady=5)

        # Область для вывода информации о сгенерированных отчетах
        self.report_info = tk.Text(self.report_tab, height=10, state=tk.DISABLED)
        self.report_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Метка для инструкций
        tk.Label(self.report_tab, text="Отчеты сохраняются в файлы в текущей директории",
                 font=("Arial", 10)).pack(side=tk.BOTTOM, pady=10)

    # Методы для работы с клиентами
    def load_customers(self):
        """Загружает клиентов из БД и отображает в таблице"""
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)

        customers = db.get_all_customers()
        for customer in customers:
            self.customer_tree.insert("", tk.END, values=customer)

    def add_customer(self):
        """Открывает диалог добавления нового клиента"""
        EditCustomerDialog(self)

    def edit_customer(self):
        """Открывает диалог редактирования выбранного клиента"""
        selected = self.customer_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента для редактирования")
            return

        item = self.customer_tree.item(selected[0])
        customer_id = item['values'][0]
        customer_data = db.fetch_query("SELECT * FROM customers WHERE id=?", (customer_id,))[0]

        customer = Customer(
            id=customer_data[0],
            name=customer_data[1],
            phone=customer_data[2],
            email=customer_data[3],
            address=customer_data[4]
        )

        EditCustomerDialog(self, customer)

    def delete_customer(self):
        """Удаляет выбранного клиента"""
        selected = self.customer_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранного клиента?"):
            item = self.customer_tree.item(selected[0])
            customer_id = item['values'][0]
            db.delete_customer(customer_id)
            self.load_customers()

    def import_customer_csv(self):
        """Импортирует клиентов из CSV файла"""
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return

        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Пропускаем заголовок
                for row in reader:
                    if len(row) >= 4:
                        customer = Customer(
                            name=row[0].strip(),
                            phone=row[1].strip(),
                            email=row[2].strip(),
                            address=row[3].strip()
                        )
                        db.add_customer(customer)

            self.load_customers()
            messagebox.showinfo("Успех", "Данные успешно импортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}")

    def export_customer_csv(self):
        """Экспортирует клиентов в CSV файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ФИО", "Телефон", "Email", "Адрес"])

                customers = db.get_all_customers()
                for customer in customers:
                    writer.writerow(customer[1:])  # Пропускаем ID

            messagebox.showinfo("Успех", "Данные успешно экспортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")
    def apply_customer_filters(self):
        """Применяет фильтры для клиентов"""
        self.load_customers()

    def reset_customer_filters(self):
        """Сбрасывает фильтры клиентов"""
        self.customer_name_filter.delete(0, tk.END)
        self.customer_phone_filter.delete(0, tk.END)
        self.customer_email_filter.delete(0, tk.END)
        self.load_customers()

    def load_customers(self):
        """Загружает клиентов с учетом фильтров"""
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)

        # Получаем значения фильтров
        name_filter = self.customer_name_filter.get().strip().lower()
        phone_filter = self.customer_phone_filter.get().strip().lower()
        email_filter = self.customer_email_filter.get().strip().lower()

        # Загрузка данных с фильтрацией
        customers = db.get_all_customers()
        for customer in customers:
            # Применяем фильтры
            matches = True

            if name_filter and name_filter not in customer[1].lower():
                matches = False

            if phone_filter and phone_filter not in customer[2].lower():
                matches = False

            if email_filter and email_filter not in customer[3].lower():
                matches = False

            if matches:
                self.customer_tree.insert("", tk.END, values=customer)

    # Аналогичные методы для товаров и заказов (load_products, add_product, edit_product и т.д.)
    # Для краткости они не приведены, но реализуются по тому же принципу

    # def load_products(self):
    #     """Загружает товары из БД и отображает в таблице"""
    #     for item in self.product_tree.get_children():
    #         self.product_tree.delete(item)
    #
    #     products = db.get_all_products()
    #     for product in products:
    #         self.product_tree.insert("", tk.END, values=product)

    def add_product(self):
        EditProductDialog(self)

    # ... (аналогично для остальных методов товаров)

    def load_orders(self):
        """Загружает заказы из БД и отображает в таблице"""
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)

        orders = db.get_all_orders()
        for order in orders:
            self.order_tree.insert("", tk.END, values=order)

    def add_order(self):
        EditOrderDialog(self)

    def apply_product_filters(self):
        """Применяет фильтры для товаров"""
        self.load_products()

    def reset_product_filters(self):
        """Сбрасывает фильтры товаров"""
        self.product_name_filter.delete(0, tk.END)
        self.product_price_min_filter.delete(0, tk.END)
        self.product_price_max_filter.delete(0, tk.END)
        self.load_products()

    def load_products(self):
        """Загружает товары с учетом фильтров"""
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        # Получаем значения фильтров
        name_filter = self.product_name_filter.get().strip().lower()
        price_min = self.product_price_min_filter.get().strip()
        price_max = self.product_price_max_filter.get().strip()

        # Преобразуем цены в числа, если возможно
        try:
            price_min = float(price_min) if price_min else 0
        except ValueError:
            price_min = 0

        try:
            price_max = float(price_max) if price_max else float('inf')
        except ValueError:
            price_max = float('inf')

        # Загрузка данных с фильтрацией
        products = db.get_all_products()
        for product in products:
            matches = True

            # Фильтр по названию
            if name_filter and name_filter not in product[1].lower():
                matches = False

            # Фильтр по цене
            product_price = float(product[2])
            if product_price < price_min or product_price > price_max:
                matches = False

            if matches:
                self.product_tree.insert("", tk.END, values=product)

    def apply_order_filters(self):
        """Применяет фильтры для заказов"""
        self.load_orders()

    def reset_order_filters(self):
        """Сбрасывает фильтры заказов"""
        self.order_customer_filter.delete(0, tk.END)
        self.order_product_filter.delete(0, tk.END)
        self.order_date_min_filter.delete(0, tk.END)
        self.order_date_max_filter.delete(0, tk.END)
        self.load_orders()

    def load_orders(self):
        """Загружает заказы с учетом фильтров"""
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)

        # Получаем значения фильтров
        customer_filter = self.order_customer_filter.get().strip().lower()
        product_filter = self.order_product_filter.get().strip().lower()
        date_min = self.order_date_min_filter.get().strip()
        date_max = self.order_date_max_filter.get().strip()

        # Загрузка данных с фильтрацией
        orders = db.get_all_orders()
        for order in orders:
            matches = True

            # Фильтр по клиенту (ФИО или телефон)
            if customer_filter:
                customer_match = (customer_filter in order[1].lower() or
                                  customer_filter in order[2].lower())
                if not customer_match:
                    matches = False

            # Фильтр по товару
            if product_filter and product_filter not in order[3].lower():
                matches = False

            # Фильтр по дате
            if date_min and order[5] < date_min:
                matches = False

            if date_max and order[5] > date_max:
                matches = False

            if matches:
                self.order_tree.insert("", tk.END, values=order)


    # Общие методы
    def sort_treeview(self, treeview, col):
        """Сортирует данные в Treeview по выбранному столбцу"""
        data = [(treeview.set(child, col), child) for child in treeview.get_children('')]
        data.sort()

        for index, (_, child) in enumerate(data):
            treeview.move(child, '', index)

    def generate_report(self, report_type):
        """Генерирует отчеты и выводит информацию о результате"""
        try:
            if report_type == "top_products":
                filename = generate_sales_report()
                message = "Отчет 'Топ товаров' сохранен в файл: " + filename
            elif report_type == "orders_dynamics":
                filename = generate_orders_dynamics()
                message = "Отчет 'Динамика заказов' сохранен в файл: " + filename
            else:
                messagebox.showerror("Ошибка", "Неизвестный тип отчета")
                return

            # Выводим информацию о сгенерированном отчете
            self.report_info.config(state=tk.NORMAL)
            self.report_info.delete(1.0, tk.END)
            self.report_info.insert(tk.END, message + "\n\n")
            self.report_info.insert(tk.END, "Чтобы открыть файл, перейдите в папку с программой.")
            self.report_info.config(state=tk.DISABLED)

            messagebox.showinfo("Успех", message)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка генерации отчета: {str(e)}")


    # def load_products(self):
    #     """Загружает товары из БД и отображает в таблице"""
    #     for item in self.product_tree.get_children():
    #         self.product_tree.delete(item)

        products = db.get_all_products()
        for product in products:
            self.product_tree.insert("", tk.END, values=product)

    def add_product(self):
        """Открывает диалог добавления нового товара"""
        EditProductDialog(self)

    def edit_product(self):
        """Открывает диалог редактирования выбранного товара"""
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите товар для редактирования")
            return

        item = self.product_tree.item(selected[0])
        product_id = item['values'][0]
        product_data = db.fetch_query("SELECT * FROM products WHERE id=?", (product_id,))[0]

        product = Product(
            id=product_data[0],
            name=product_data[1],
            price=product_data[2]
        )

        EditProductDialog(self, product)

    def delete_product(self):
        """Удаляет выбранный товар"""
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный товар?"):
            item = self.product_tree.item(selected[0])
            product_id = item['values'][0]
            db.delete_product(product_id)
            self.load_products()

    def import_product_csv(self):
        """Импортирует товары из CSV файла"""
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return

        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Пропускаем заголовок
                for row in reader:
                    if len(row) >= 2:
                        try:
                            price = float(row[1])
                        except ValueError:
                            price = 0.0

                        product = Product(
                            name=row[0].strip(),
                            price=price
                        )
                        db.add_product(product)

            self.load_products()
            messagebox.showinfo("Успех", "Данные успешно импортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}")

    def export_product_csv(self):
        """Экспортирует товары в CSV файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Название", "Цена"])

                products = db.get_all_products()
                for product in products:
                    writer.writerow([product[1], product[2]])  # Название и цена

            messagebox.showinfo("Успех", "Данные успешно экспортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")

    # def load_orders(self):
    #     """Загружает заказы из БД и отображает в таблице"""
    #     for item in self.order_tree.get_children():
    #         self.order_tree.delete(item)
    #
    #     orders = db.get_all_orders()
    #     for order in orders:
    #         self.order_tree.insert("", tk.END, values=order)

    def add_order(self):
        """Открывает диалог добавления нового заказа"""
        EditOrderDialog(self)

    def edit_order(self):
        """Открывает диалог редактирования выбранного заказа"""
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ для редактирования")
            return

        item = self.order_tree.item(selected[0])
        order_id = item['values'][0]
        order_data = db.fetch_query("SELECT * FROM orders WHERE id=?", (order_id,))[0]

        order = Order(
            id=order_data[0],
            customer_id=order_data[1],
            product_id=order_data[2],
            date=order_data[3]
        )

        EditOrderDialog(self, order)

    def delete_order(self):
        """Удаляет выбранный заказ"""
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный заказ?"):
            item = self.order_tree.item(selected[0])
            order_id = item['values'][0]
            db.delete_order(order_id)
            self.load_orders()

    def import_order_csv(self):
        """Импортирует заказы из CSV файла"""
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return

        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Пропускаем заголовок
                for row in reader:
                    if len(row) >= 3:
                        order = Order(
                            customer_id=int(row[0]),
                            product_id=int(row[1]),
                            date=row[2].strip()
                        )
                        db.add_order(order)

            self.load_orders()
            messagebox.showinfo("Успех", "Данные успешно импортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}")

    def export_order_csv(self):
        """Экспортирует заказы в CSV файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID клиента", "ID товара", "Дата заказа"])

                orders = db.fetch_query("SELECT customer_id, product_id, date FROM orders")
                for order in orders:
                    writer.writerow(order)

            messagebox.showinfo("Успех", "Данные успешно экспортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")