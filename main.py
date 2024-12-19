import sys
import pg8000
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem

def connect_db():
    try:
        conn = pg8000.connect(
            user="midasxlr",
            password="yourpassword",
            database="midasxlr",
            host="localhost",
            port=5432
        )
        return conn
    except Exception as e:
        QMessageBox.critical(None, "Ошибка подключения", f"Не удалось подключиться к базе данных: {e}")
        return None


def search_books_by_title():
    search_text = entry_search.text()
    if not search_text:
        QMessageBox.warning(None, "Ошибка", "Пожалуйста, введите текст для поиска.")
        return

    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM search_books_by_title(%s)", (search_text,))
                results = cursor.fetchall()
                if results:
                    display_search_results(results)
                else:
                    QMessageBox.information(None, "Поиск", "Книги не найдены.")
        except Exception as e:
            QMessageBox.critical(None, "Ошибка поиска", f"Не удалось выполнить поиск: {e}")
        finally:
            conn.close()


def display_search_results(results):
    table_search.setRowCount(len(results))
    for i, row in enumerate(results):
        for j, value in enumerate(row):
            table_search.setItem(i, j, QTableWidgetItem(str(value)))


def load_categories():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM get_all_categories()")
            categories = cursor.fetchall()
            display_categories(categories)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось загрузить категории: {e}")
        finally:
            conn.close()

def display_categories(categories):
    table_categories.setRowCount(len(categories))
    for i, category in enumerate(categories):
        for j, value in enumerate(category):
            table_categories.setItem(i, j, QTableWidgetItem(str(value)))


def add_category():
    category_name = entry_category_name.text()

    # Проверка на пустые поля
    if not category_name:
        QMessageBox.warning(None, "Ошибка", "Пожалуйста, заполните название категории.")
        return

    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("CALL add_category(%s)", (category_name,))
            conn.commit()
            QMessageBox.information(None, "Успех", "Категория успешно добавлена!")
            clear_category_form()
            load_categories()
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось добавить категорию: {e}")
        finally:
            conn.close()


def clear_category_form():
    entry_category_name.clear()




def delete_category():
    row = table_categories.currentRow()
    if row == -1:
        QMessageBox.warning(None, "Ошибка", "Пожалуйста, выберите категорию для удаления.")
        return
    category_id = table_categories.item(row, 0).text()

    # Подтверждение удаления
    reply = QMessageBox.question(None, "Удалить категорию?", "Вы уверены, что хотите удалить эту категорию?",
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        conn = connect_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM categories WHERE id=%s", (category_id,))
                conn.commit()
                QMessageBox.information(None, "Удаление", "Категория успешно удалена!")
                load_categories()
            except Exception as e:
                QMessageBox.critical(None, "Ошибка", f"Не удалось удалить категорию: {e}")
            finally:
                conn.close()



def add_book():
    title = entry_title.text()
    author = entry_author.text()
    year = entry_year.text()
    category_id = entry_category_id.text()

    if not title or not author or not year or not category_id:
        QMessageBox.warning(None, "Ошибка", "Пожалуйста, заполните все поля.")
        return
    try:
        year = int(year)
    except ValueError:
        QMessageBox.warning(None, "Ошибка", "Год издания должен быть числом.")
        return

    conn = connect_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("CALL add_book(%s, %s, %s, %s)", (title, author, year, category_id))
            conn.commit()
            QMessageBox.information(None, "Успех", "Книга успешно добавлена!")
            clear_form()
            load_books()
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось добавить книгу: {e}")
        finally:
            conn.close()




def load_books():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM get_all_books()")
            books = cursor.fetchall()
            display_books(books)
        except Exception as e:
            QMessageBox.critical(None, "Ошибка", f"Не удалось загрузить книги: {e}")
        finally:
            conn.close()

def display_books(books):
    table_books.setRowCount(len(books))
    for i, book in enumerate(books):
        for j, value in enumerate(book):
            table_books.setItem(i, j, QTableWidgetItem(str(value)))


def create_database():
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("CALL create_database()")
                conn.commit()
                QMessageBox.information(None, "Успех", "База данных успешно создана!")
        except Exception as e:
            QMessageBox.critical(None, "Ошибка создания базы данных", f"Не удалось создать базу данных: {e}")
        finally:
            conn.close()


def delete_database(dbname):
    reply = QMessageBox.question(None, "Удаление базы данных", "Вы уверены, что хотите удалить всю базу данных?",
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        conn = connect_db()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("CALL delete_database(%s)", (dbname,))
                    conn.commit()
                    QMessageBox.information(None, "Удаление", f"База данных {dbname} успешно удалена!")
            except Exception as e:
                QMessageBox.critical(None, "Ошибка удаления базы данных", f"Не удалось удалить базу данных: {e}")
            finally:
                conn.close()

def clear_table():
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Вызов процедуры для удаления таблицы books
                cursor.execute("CALL delete_books_table();")
                conn.commit()
                QMessageBox.information(None, "Удаление", 'Таблица "books" успешно удалена!')
        except Exception as e:
            QMessageBox.critical(None, "Ошибка удаления таблицы", f"Не удалось удалить таблицу 'books': {e}")
        finally:
            conn.close()



def clear_all_tables():
    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("CALL clear_all_tables()")
                conn.commit()
                QMessageBox.information(None, "Очистка", "Таблицы успешно очищены!")
        except Exception as e:
            QMessageBox.critical(None, "Ошибка очистки таблиц", f"Не удалось очистить таблицы: {e}")
        finally:
            conn.close()





def delete_book_by_title():
    title = entry_search.text()
    if not title:
        QMessageBox.warning(None, "Ошибка", "Пожалуйста, введите название книги для удаления.")
        return

    conn = connect_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("CALL delete_book_by_title(%s)", (title,))
                conn.commit()
                QMessageBox.information(None, "Удаление", "Книга успешно удалена!")
                load_books()
        except Exception as e:
            QMessageBox.critical(None, "Ошибка удаления книги", f"Не удалось удалить книгу: {e}")
        finally:
            conn.close()



def clear_form():
    entry_title.clear()
    entry_author.clear()
    entry_year.clear()
    entry_category_id.clear()


def update_books_data():
    """Fetch the data from the 'books' table and update the QTableWidget"""
    conn = connect_db()
    if conn is None:
        QMessageBox.critical(None, "Error", "Failed to connect to database.")
        return

    try:
        with conn.cursor() as cursor:
            # Fetch data from the books table
            cursor.execute("SELECT * FROM books;")
            rows = cursor.fetchall()

            # Update the table in the GUI
            table_books.setRowCount(len(rows))  # Set number of rows
            for i, row in enumerate(rows):
                for j, cell in enumerate(row):
                    table_books.setItem(i, j, QTableWidgetItem(str(cell)))
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to fetch books data: {e}")
    finally:
        conn.close()



def delete_book():
    row = table_books.currentRow()
    if row == -1:
        QMessageBox.warning(None, "Ошибка", "Пожалуйста, выберите книгу для удаления.")
        return
    book_id = table_books.item(row, 0).text()
    reply = QMessageBox.question(None, "Удалить книгу?", "Вы уверены, что хотите удалить эту книгу?",
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    if reply == QMessageBox.Yes:
        conn = connect_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM books WHERE id=%s", (book_id,))
                conn.commit()
                QMessageBox.information(None, "Удаление", "Книга успешно удалена!")
                load_books()
            except Exception as e:
                QMessageBox.critical(None, "Ошибка", f"Не удалось удалить книгу: {e}")
            finally:
                conn.close()


def add_category():
    category_name = entry_category_name.text()

    if not category_name:
        QMessageBox.warning(None, "Ошибка", "Название категории не может быть пустым.")
        return

    try:
        conn = connect_db()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Categories (name) VALUES (%s)",
            (category_name,)
        )

        conn.commit()

        cursor.close()
        conn.close()
        QMessageBox.information(None, "Успех", f"Категория '{category_name}' успешно добавлена.")
        entry_category_name.clear()

    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Ошибка при добавлении категории: {e}")


def go_back_to_categories():
    tabs.setCurrentIndex(4)


app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Библиотечная система")

main_layout = QVBoxLayout()

tabs = QTabWidget()

# Вкладка 1: Добавление книги
tab_add_book = QWidget()
add_book_layout = QVBoxLayout()

label_title = QLabel("Название книги:")
entry_title = QLineEdit()
add_book_layout.addWidget(label_title)
add_book_layout.addWidget(entry_title)

label_author = QLabel("Автор книги:")
entry_author = QLineEdit()
add_book_layout.addWidget(label_author)
add_book_layout.addWidget(entry_author)

label_year = QLabel("Год издания:")
entry_year = QLineEdit()
add_book_layout.addWidget(label_year)
add_book_layout.addWidget(entry_year)

label_category_id = QLabel("Категория (ID):")
entry_category_id = QLineEdit()
add_book_layout.addWidget(label_category_id)
add_book_layout.addWidget(entry_category_id)

button_add_book = QPushButton("Добавить книгу")
button_add_book.clicked.connect(add_book)
add_book_layout.addWidget(button_add_book)

tab_add_book.setLayout(add_book_layout)

# Вкладка 2: Поиск книги
tab_search_books = QWidget()
search_layout = QVBoxLayout()

label_search = QLabel("Поиск книги по названию:")
entry_search = QLineEdit()
search_layout.addWidget(label_search)
search_layout.addWidget(entry_search)

button_search = QPushButton("Поиск")
button_search.clicked.connect(search_books_by_title)
search_layout.addWidget(button_search)

# Таблица для отображения результатов поиска
table_search = QTableWidget()
table_search.setColumnCount(5)  # Количество столбцов: id, title, author, year, category_id
table_search.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Год", "Категория"])
search_layout.addWidget(table_search)



tab_search_books.setLayout(search_layout)

# Вкладка 3: Просмотр списка книг
tab_books = QWidget()
books_layout = QVBoxLayout()

# Таблица для отображения всех книг
table_books = QTableWidget()
table_books.setColumnCount(5)  # Увеличиваем количество колонок для ID и категории
table_books.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Год", "Категория"])
books_layout.addWidget(table_books)

button_edit_book = QPushButton("Обновить")
button_edit_book.clicked.connect(update_books_data)  # Подключаем функцию обновления данных
books_layout.addWidget(button_edit_book)

button_delete_book = QPushButton("Удалить книгу")
button_delete_book.clicked.connect(delete_book)
books_layout.addWidget(button_delete_book)

tab_books.setLayout(books_layout)

# Вкладка 4: Управление базой данных
tab_database = QWidget()
database_layout = QVBoxLayout()

button_create_db = QPushButton("Создать базу данных")
# button_create_db.clicked.connect(create_db)
# database_layout.addWidget(button_create_db)

button_delete_db = QPushButton("Удалить базу данных")
button_delete_db.clicked.connect(delete_database)
database_layout.addWidget(button_delete_db)

button_clear_books = QPushButton("Очистить таблицу книг")
# button_clear_books.clicked.connect(lambda: clear_table("books"))
button_clear_books.clicked.connect(clear_table)

database_layout.addWidget(button_clear_books)

button_clear_all = QPushButton("Очистить все таблицы")
button_clear_all.clicked.connect(clear_all_tables)
database_layout.addWidget(button_clear_all)

tab_database.setLayout(database_layout)

# Вкладка 5: Просмотр категорий
tab_categories = QWidget()
categories_layout = QVBoxLayout()

# Таблица для отображения категорий
table_categories = QTableWidget()
table_categories.setColumnCount(2)  # Два столбца: ID и Название
table_categories.setHorizontalHeaderLabels(["ID", "Название"])
categories_layout.addWidget(table_categories)

button_add_category = QPushButton("Добавить категорию")
button_add_category.clicked.connect(lambda: tabs.setCurrentIndex(5))  # Переход на вкладку добавления категории
categories_layout.addWidget(button_add_category)



button_delete_category = QPushButton("Удалить категорию")
button_delete_category.clicked.connect(delete_category)
categories_layout.addWidget(button_delete_category)

tab_categories.setLayout(categories_layout)

# Вкладка 6: Добавление категории (изначально скрыта)
tab_add_category = QWidget()
add_category_layout = QVBoxLayout()

label_category_name = QLabel("Название категории:")
entry_category_name = QLineEdit()
add_category_layout.addWidget(label_category_name)
add_category_layout.addWidget(entry_category_name)

button_add_category = QPushButton("Добавить категорию")
button_add_category.clicked.connect(add_category)
add_category_layout.addWidget(button_add_category)

button_back = QPushButton("Назад")
button_back.clicked.connect(go_back_to_categories)
add_category_layout.addWidget(button_back)

tab_add_category.setLayout(add_category_layout)

tabs.addTab(tab_add_book, "Добавить книгу")
tabs.addTab(tab_search_books, "Поиск книги")
tabs.addTab(tab_books, "Все книги")
tabs.addTab(tab_categories, "Категории")
tabs.addTab(tab_database, "Управление БД")

tabs.addTab(tab_add_category, "Добавить категорию")
tabs.setTabVisible(5, False)

main_layout.addWidget(tabs)

window.setLayout(main_layout)
load_books()
load_categories()

window.show()

sys.exit(app.exec_())
