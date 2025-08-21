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
                "Пример: ivanov@example.ru"
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

        self.title("Редактирование товара" if product else "Добавление товара") # Заголовок в зависимости передан ли product
        self.geometry("400x200") # Установка начального размера окна:
        self.resizable(False, False) # Запрет изменения размера окна

        # Создаем элементы формы
        tk.Label(self, text="Название:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self, text="Цена:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        # Создание полей ввода
        self.name_entry = tk.Entry(self, width=30)
        self.price_entry = tk.Entry(self, width=30)
        # Размещение полей ввода в сетке формы
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.price_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Заполняем поля, если редактируем существующий товар
        if product:
            # Заполнение поля данными из объекта клиента
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
        # Инициализируем родительский класс (Toplevel)
        super().__init__(parent)
        self.parent = parent # Связываем окно с родителем
        self.order = order # Храним ссылку на редактируемый заказ (если таковой есть)

        self.title("Редактирование заказа" if order else "Добавление заказа") # Название окна меняется в зависимости от наличия заказа
        self.geometry("500x300") # Размер окна
        self.resizable(False, False)    # Запрещаем менять размер окна

        # Получаем данные для выпадающих списков
        self.customers = db.get_all_customers()  # Все клиенты
        self.products = db.get_all_products()  # Все товары

        # Создаем элементы формы
        tk.Label(self, text="Клиент:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self, text="Товар:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        tk.Label(self, text="Дата заказа:").grid(row=2, column=0, padx=10, pady=10, sticky="e")

        # Выпадающий список для клиентов
        self.customer_var = tk.StringVar(self) # Переменная для хранения выбранного клиента
        self.customer_combobox = ttk.Combobox(self, textvariable=self.customer_var, width=40) # Виджет ComboBox для выбора клиента

        # Формируем список для отображения и словарь для сопоставления
        self.customer_display = [] # Список для отображения в Combobox
        self.customer_id_map = {} # Словарь для сопоставления отображаемого текста с ID клиента
        for c in self.customers:
            display_text = f"{c[1]} (ID: {c[0]}, тел: {c[2]})" # Форматируем текст для отображения
            self.customer_display.append(display_text) # Добавляем в список отображения
            self.customer_id_map[display_text] = c[0] # Связываем отображаемое значение с ID клиента

        self.customer_combobox['values'] = self.customer_display # Устанавливаем список отображения в Combobox
        self.customer_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="w")  # Располагаем Combobox на форме

        # Выпадающий список для товаров
        self.product_var = tk.StringVar(self)  # Переменная для хранения выбранного товара
        self.product_combobox = ttk.Combobox(self, textvariable=self.product_var, width=40) # Виджет ComboBox для выбора товара

        self.product_display = []  # Список для отображения в Combobox
        self.product_id_map = {}  # Словарь для сопоставления отображаемого текста с ID товара
        for p in self.products:
            display_text = f"{p[1]} (ID: {p[0]}, цена: {p[2]} руб.)" # Форматируем текст для отображения
            self.product_display.append(display_text) # Добавляем в список отображения
            self.product_id_map[display_text] = p[0] # Связываем отображаемое значение с ID товара

        self.product_combobox['values'] = self.product_display # Устанавливаем список отображения в Combobox
        self.product_combobox.grid(row=1, column=1, padx=10, pady=10, sticky="w") # Располагаем Combobox на форме

        # Поле для даты заказа
        self.date_entry = tk.Entry(self, width=30) # Виджет Entry для ввода даты
        self.date_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w") # Расположение на форме
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
            self.date_entry.delete(0, tk.END) # Очищаем поле даты
            self.date_entry.insert(0, order.date) # Ставим дату заказа

        # Кнопки сохранения/отмены
        btn_frame = tk.Frame(self) # Рамка для кнопок
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20) # Расположение рамки на форме

        tk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=10) # Кнопка "Сохранить"
        tk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=10) # Кнопка "Отмена"

    def save(self):
        """Собирает данные из формы и сохраняет заказ"""
        customer_display = self.customer_var.get().strip() # Получаем выбранного клиента
        product_display = self.product_var.get().strip() # Получаем выбранный товар
        date = self.date_entry.get().strip() # Получаем введённую дату

        if not customer_display or not product_display:
            messagebox.showerror("Ошибка", "Выберите клиента и товар") # Если не выбраны клиент и товар, выдаём ошибку
            return

        # Получаем ID клиента и товара из словарей
        try:
            customer_id = self.customer_id_map.get(customer_display) # Получаем ID клиента
            product_id = self.product_id_map.get(product_display) # Получаем ID товара

            if customer_id is None:
                raise ValueError("Не удалось определить ID клиента") # Если ID клиента не найден, выдаём ошибку
            if product_id is None:
                raise ValueError("Не удалось определить ID товара")  # Если ID товара не найден, выдаём ошибку
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке данных: {str(e)}") # Обрабатываем общую ошибку
            return

        # Проверяем корректность даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        # Обновляем или создаем новый заказ
        if self.order:
            # Редактируем существующий заказ
            self.order.customer_id = customer_id
            self.order.product_id = product_id
            self.order.date = date
            db.update_order(self.order) # Обновляем заказ в базе данных
        else:
            # Создаем новый заказ
            order = Order(customer_id=customer_id, product_id=product_id, date=date)
            db.add_order(order) # Добавляем новый заказ в базу данных

        self.parent.load_orders() # Обновляем список заказов в основном окне
        self.destroy() # Закрываем окно

# Класс наследуется от класса Tk, предоставляя базовую структуру окна приложения.
class App(tk.Tk):
    """Основной класс приложения"""
    # инициализируется окно приложения, задаётся название (title) и размер окна (geometry)
    def __init__(self):
        super().__init__()
        self.title("Менеджер интернет-магазина")  # заголовок окна
        self.geometry("1000x700")   # Размер окна приложения

        # Создаем вкладки
        # Позволит пользователям переключаться между разными секциями программы
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10) # Заполняем всё пространство окна

        # Создание отдельных фреймов для каждой вкладки
        # Каждый фрейм соответствует своей вкладке: клиенты, товары, заказы, отчёты
        self.customer_tab = ttk.Frame(self.notebook)
        self.product_tab = ttk.Frame(self.notebook)
        self.order_tab = ttk.Frame(self.notebook)
        self.report_tab = ttk.Frame(self.notebook)

        # Добавляем созданные фреймы к notebooks с соответствующими названиями
        self.notebook.add(self.customer_tab, text="Клиенты")
        self.notebook.add(self.product_tab, text="Товары")
        self.notebook.add(self.order_tab, text="Заказы")
        self.notebook.add(self.report_tab, text="Отчеты")

        # Инитируем вкладки, вызывая соответствующие методы
        self.init_customer_tab()
        self.init_product_tab()
        self.init_order_tab()
        self.init_report_tab()

    def init_customer_tab(self):
        """
        Инициализирует вкладку "Клиенты".

        Этот метод создаёт таблицу для отображения клиентов, панель инструментов с кнопками
        для добавления, изменения и удаления клиентов, а также систему фильтрации и сортировки.
        """
        # Столбцы таблицы (колонки, которые будут видны пользователю)
        columns = ("ID", "ФИО", "Телефон", "Email", "Адрес")
        self.customer_tree = ttk.Treeview(self.customer_tab, columns=columns, show="headings")

        # Установка заголовков колонок и определение размеров
        for col in columns:
            self.customer_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.customer_tree, c))
            self.customer_tree.column(col, width=150)

        # Прокручиваемая область справа от таблицы (вертикальная полоса прокрутки)
        scrollbar = ttk.Scrollbar(self.customer_tab, orient=tk.VERTICAL, command=self.customer_tree.yview)
        self.customer_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.customer_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для кнопок
        btn_frame = tk.Frame(self.customer_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки для добавления, редактирования и удаления клиента
        tk.Button(btn_frame, text="Добавить", command=self.add_customer).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_customer).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_customer).pack(side=tk.LEFT, padx=5)

        # Импорт и экспорт данных (работа с файлами .csv)
        tk.Button(btn_frame, text="Импорт CSV", command=self.import_customer_csv).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Экспорт CSV", command=self.export_customer_csv).pack(side=tk.RIGHT, padx=5)

        # Фрейм для фильтров
        filter_frame = tk.Frame(self.customer_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поле для ввода имени клиента
        tk.Label(filter_frame, text="Фильтр по ФИО:").grid(row=0, column=0, padx=5)
        self.customer_name_filter = tk.Entry(filter_frame, width=20)
        self.customer_name_filter.grid(row=0, column=1, padx=5)

        # Остальные поля фильтрации по телефону и Email
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



        # Подгружаем список клиентов из базы данных
        self.load_customers()

    def init_product_tab(self):
        """
        Инициализирует вкладку "Товары".

        Похожий принцип организации, как и у вкладки "Клиенты": таблица, панель инструментов,
        система фильтрации и сортировки.
        """
        # Определение колонок для таблицы товаров
        columns = ("ID", "Название", "Цена")
        self.product_tree = ttk.Treeview(self.product_tab, columns=columns, show="headings")

        # Названия колонок и ширина
        for col in columns:
            self.product_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.product_tree, c))
            self.product_tree.column(col, width=150)

        # Добавляем полосу прокрутки справа
        scrollbar = ttk.Scrollbar(self.product_tab, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.product_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для кнопок
        btn_frame = tk.Frame(self.product_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Основная функциональность: добавить, изменить, удалить продукт
        tk.Button(btn_frame, text="Добавить", command=self.add_product).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_product).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_product).pack(side=tk.LEFT, padx=5)

        # Работа с файлами (.csv): импорт и экспорт
        tk.Button(btn_frame, text="Импорт CSV", command=self.import_product_csv).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Экспорт CSV", command=self.export_product_csv).pack(side=tk.RIGHT, padx=5)

        # Фрейм для фильтров
        filter_frame = tk.Frame(self.product_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Фильтрация товаров по названию и диапазону цен
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
        """
        Инициализирует вкладку "Заказы".
        Подобная организация и функционалы, как и у предыдущих вкладок.

        """
        # Таблица для отображения заказов
        columns = ("ID", "ФИО клиента", "Телефон", "Товар", "Цена", "Дата заказа")
        self.order_tree = ttk.Treeview(self.order_tab, columns=columns, show="headings")

        # Настраиваем заголовки и ширину колонок
        for col in columns:
            self.order_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.order_tree, c))
            self.order_tree.column(col, width=150)

        # Прокрутка справа
        scrollbar = ttk.Scrollbar(self.order_tab, orient=tk.VERTICAL, command=self.order_tree.yview)
        self.order_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.order_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм для кнопок
        btn_frame = tk.Frame(self.order_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Кнопки добавления, редактирования и удаления заказов
        tk.Button(btn_frame, text="Добавить", command=self.add_order).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_order).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_order).pack(side=tk.LEFT, padx=5)

        # Кнопки импорта/экспорта
        tk.Button(btn_frame, text="Импорт CSV", command=self.import_order_csv).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Экспорт CSV", command=self.export_order_csv).pack(side=tk.RIGHT, padx=5)

        # Фрейм для фильтров
        filter_frame = tk.Frame(self.order_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поля фильтрации по клиентским данным и датам
        tk.Label(filter_frame, text="ФИО или Тел:").grid(row=0, column=0, padx=5)
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

        # Подгрузка заказов из базы данных
        self.load_orders()

    def init_report_tab(self):
        """
        Инициализирует вкладку "Отчеты".
        Позволяет генерировать отчёты и выводить уведомления о результатах.
        """
        # Панель инструментов с кнопками генерации отчётов
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

        # Информация о расположении отчётов
        tk.Label(self.report_tab, text="Отчеты сохраняются в файлы в текущей директории",
                 font=("Arial", 10)).pack(side=tk.BOTTOM, pady=10)


    # Функционал работы с клиентами

    def add_customer(self):
        """Открывает форму для добавления нового клиента"""
        EditCustomerDialog(self) # Дополнительный модуль EditCustomerDialog

    def edit_customer(self):
        """Открывает форму для редактирования существующего клиента.    """
        selected = self.customer_tree.selection() # Выбираем выделенного клиента
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента для редактирования")
            return
        # Извлекаем ID клиента
        item = self.customer_tree.item(selected[0])
        customer_id = item['values'][0]
        # Используем дополнительный модуль для подкачки данных по найденному ID
        customer_data = db.fetch_query("SELECT * FROM customers WHERE id=?", (customer_id,))[0]
        # Запоминаем поля для редактирования
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
        # Подтверждаем удаление
        if messagebox.askyesno("Подтверждение", "Удалить выбранного клиента?"):
            item = self.customer_tree.item(selected[0]) # выбран элемент дерева customer_tree (клиент),
            customer_id = item['values'][0] # Определение ID удаляемого клиента
            db.delete_customer(customer_id) # Удаление клиента из базы данных
            self.load_customers() # Перезагружаем список клиентов

    def import_customer_csv(self):
        """Импортирует клиентов из CSV файла"""
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")]) # Выбор пути к файлу
        if not filepath:
            return # Выходим если файл не выбран
        # Чтение данных из файла
        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.reader(f) # Создается объект чтения CSV-файлов
                next(reader)  # Пропускаем заголовок
                for row in reader:
                    if len(row) >= 4: # минимум 4 колонки
                        customer = Customer(
                            name=row[0].strip(), # Имя клиента (очищает лишние пробелы перед и после значения)
                            phone=row[1].strip(), # Телефон клиента
                            email=row[2].strip(), # Email клиента
                            address=row[3].strip() # Адрес клиента
                        )
                        db.add_customer(customer) # новый клиент добавляется в базу данных

            self.load_customers() # обновляет список клиентов
            messagebox.showinfo("Успех", "Данные успешно импортированы")
        except Exception as e: # Если возникает ошибка
            messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}")

    def export_customer_csv(self):
        """Экспортирует клиентов в CSV файл"""
        filepath = filedialog.asksaveasfilename( # Запрашиваем путь к файлу для сохранения
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not filepath:
            return # Выходим если файла нет

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f: # Файл открывается в режиме записи ('w'),
                writer = csv.writer(f) # Создаем объект записи CSV
                writer.writerow(["ФИО", "Телефон", "Email", "Адрес"]) # Заголовки столбцов

                customers = db.get_all_customers() # Получение всех клиентов из базы
                for customer in customers:
                    writer.writerow(customer[1:])  # Пропускаем ID путем среза customer[1:]

            messagebox.showinfo("Успех", "Данные успешно экспортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")

    def apply_customer_filters(self):
        """Применяет фильтры для клиентов"""
        self.load_customers()

    def reset_customer_filters(self):
        """Сбрасывает фильтры клиентов"""
        self.customer_name_filter.delete(0, tk.END) # очистка всего текста, внутри поля
        self.customer_phone_filter.delete(0, tk.END)
        self.customer_email_filter.delete(0, tk.END)
        self.load_customers() # Обновление списка клиентов

    def load_customers(self):
        """Загружает клиентов с учетом фильтров"""
        # Удаляем все существующие элементы из дерева клиентов
        # Это необходимо для обновления после изменений фильтров
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)

        # Получаем значения фильтров из соответствующих полей ввода,
        # преобразуя их в нижний регистр и обрезая лишнее пространство
        name_filter = self.customer_name_filter.get().strip().lower()
        phone_filter = self.customer_phone_filter.get().strip().lower()
        email_filter = self.customer_email_filter.get().strip().lower()

        # Выполняем запрос ко всей базе данных клиентов
        customers = db.get_all_customers()
        # Проходим по каждому клиенту и применяем фильтры
        for customer in customers:
            matches = True # Изначально считаем, что клиент соответствует условиям фильтрации
            #   если фильтр пустой (существование самого фильтра) and присутствует ли содержимое фильтра в соответствующем поле
            if name_filter and name_filter not in customer[1].lower(): # customer[1] — это имя клиента
                matches = False

            if phone_filter and phone_filter not in customer[2].lower(): # customer[2] — номер телефона
                matches = False

            if email_filter and email_filter not in customer[3].lower(): # customer[3] — email
                matches = False

            # Если клиент прошел проверку по всем фильтрам, добавляем его в дерево клиентов
            if matches:
                self.customer_tree.insert("", tk.END, values=customer)


    # Аналогичные методы для товаров и заказов (load_orders, add_order, load_products, add_product,  edit_product и т.д.)

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
                    if len(row) >= 2: # минимум 2 колонки
                        try:
                            price = float(row[1]) # цена товара
                        except ValueError:
                            price = 0.0 # если ошибка (не float) = 0

                        product = Product(
                            name=row[0].strip(), # название товара
                            price=price # цена
                        )
                        db.add_product(product) # добавляем в базу

            self.load_products() # обновляет список товаров
            messagebox.showinfo("Успех", "Данные успешно импортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}")

    def export_product_csv(self):
        """Экспортирует товары в CSV файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        ) # Запрашиваем путь к файлу для сохранения
        if not filepath:
            return # Выходим если файла нет

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f: # Файл для записи ('w')
                writer = csv.writer(f) # Создаем объект записи CSV
                writer.writerow(["Название", "Цена"]) # Заголовки столбцов

                products = db.get_all_products() # Получение всех товаров из базы
                for product in products:
                    writer.writerow([product[1], product[2]])  # Название и цена

            messagebox.showinfo("Успех", "Данные успешно экспортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")


    def apply_order_filters(self):
        """Применяет фильтры для заказов"""
        self.load_orders()

    def reset_order_filters(self):
        """Сбрасывает фильтры заказов"""
        self.order_customer_filter.delete(0, tk.END) # очистка всего текста, внутри поля
        self.order_product_filter.delete(0, tk.END)
        self.order_date_min_filter.delete(0, tk.END)
        self.order_date_max_filter.delete(0, tk.END)
        self.load_orders() # Обновление списка клиентов

    def load_orders(self):
        """Загружает заказы с учетом фильтров"""
        for item in self.order_tree.get_children():
            self.order_tree.delete(item) # Удаляем все существующие элементы из дерева

        # Получаем значения фильтров, преобразуя их в нижний регистр и обрезая лишнее пространство
        customer_filter = self.order_customer_filter.get().strip().lower()
        product_filter = self.order_product_filter.get().strip().lower()
        date_min = self.order_date_min_filter.get().strip()
        date_max = self.order_date_max_filter.get().strip()

        # Загрузка данных с фильтрацией
        orders = db.get_all_orders()
        for order in orders:
            matches = True # Изначально считаем, что все подходят фильтру

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

            if matches: # Если прошел проверку по всем фильтрам, добавляем его в дерево
                self.order_tree.insert("", tk.END, values=order)

    def add_order(self):
        """Открывает диалог добавления нового заказа"""
        EditOrderDialog(self)

    def edit_order(self):
        """Открывает диалог редактирования выбранного заказа"""
        selected = self.order_tree.selection() # Выбираем выделенный заказ
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заказ для редактирования")
            return
        # Извлекаем ID
        item = self.order_tree.item(selected[0])
        order_id = item['values'][0]
        # Получаем данные по найденному ID
        order_data = db.fetch_query("SELECT * FROM orders WHERE id=?", (order_id,))[0]
        # Запоминаем поля для редактирования, текущими значениями
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
            order_id = item['values'][0] # Определение ID
            db.delete_order(order_id) # Удаление из базы по ID
            self.load_orders() # Перезагружаем список

    def import_order_csv(self):
        """Импортирует заказы из CSV файла"""
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return # Выходим если файл не выбран
        # Чтение данных из файла
        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.reader(f) # Создается объект чтения CSV-файлов
                next(reader)  # Пропускаем заголовок
                for row in reader:
                    if len(row) >= 3: # минимум 3 колонки
                        order = Order(
                            customer_id=int(row[0]), # ID клиента
                            product_id=int(row[1]), # ID товара
                            date=row[2].strip() # дата заказа
                        )
                        db.add_order(order) # новый заказ добавляется в базу данных

            self.load_orders() # обновляет список
            messagebox.showinfo("Успех", "Данные успешно импортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}")

    def export_order_csv(self):
        """Экспортирует заказы в CSV файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        ) # Запрашиваем путь к файлу для сохранения
        if not filepath:
            return # Выходим если файла нет

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID клиента", "ID товара", "Дата заказа"]) # Заголовки столбцов
                # Получение всех заказов из базы
                orders = db.fetch_query("SELECT customer_id, product_id, date FROM orders")
                for order in orders:
                    writer.writerow(order)

            messagebox.showinfo("Успех", "Данные успешно экспортированы")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")


    # Общие методы
    def sort_treeview(self, treeview, col): # Treeview, в котором нужно произвести сортировку. col: Имя колонки, по которой будет выполнена сортировка.
        """
        Сортирует данные в Treeview по выбранному столбцу
        получаем все элементы метод get_children.
        Формируем список кортежей, где каждый кортеж содержит:
        значения колонки, уникальные идентификатор

        """
        data = [(treeview.set(child, col), child) for child in treeview.get_children('')]
        data.sort() # Мы используем метод sort() непосредственно на списке кортежей

        for index, (_, child) in enumerate(data):
            treeview.move(child, '', index) # Метод move() перемещает элемент (child) на новую позицию в дереве.

    def generate_report(self, report_type):
        """Генерирует отчеты и выводит информацию о результате"""
        try:
            if report_type == "top_products": # Генерация отчета "Топ товаров"
                filename = generate_sales_report() # Генерируем отчёт продаж
                message = "Отчет 'Топ товаров' сохранен в файл: " + filename # Формируем сообщение
            elif report_type == "orders_dynamics": # Генерация отчета "Динамика заказов"
                filename = generate_orders_dynamics() # Генерируем динамику заказов
                message = "Отчет 'Динамика заказов' сохранен в файл: " + filename # Формируем сообщение
            else:
                messagebox.showerror("Ошибка", "Неизвестный тип отчета") # Сообщаем об ошибке
                return

            # Выводим информацию о создании отчета в специальное текстовое поле
            self.report_info.config(state=tk.NORMAL)  # Включаем возможность редактирования поля
            self.report_info.delete(1.0, tk.END) # Очищаем предыдущее содержание
            self.report_info.insert(tk.END, message + "\n\n") # Вставляем новое сообщение
            self.report_info.insert(tk.END, "Чтобы открыть файл, перейдите в папку с программой.") # Дополнительная подсказка
            self.report_info.config(state=tk.DISABLED) # Возвращаем режим "только для чтения"
            # Дополнительно показываем окошко с информацией о сохранении отчета
            messagebox.showinfo("Успех", message)
        except Exception as e: # Ловим любые непредвиденные ошибки
            messagebox.showerror("Ошибка", f"Ошибка генерации отчета: {str(e)}")

