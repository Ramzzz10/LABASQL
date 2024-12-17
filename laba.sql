-- Создание таблицы Categories
CREATE TABLE IF NOT EXISTS Categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Создание таблицы Books
CREATE TABLE IF NOT EXISTS Books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    author VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    category_id INTEGER REFERENCES Categories(id) ON DELETE SET NULL
);

-- Создание таблицы Readers
CREATE TABLE IF NOT EXISTS Readers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    email VARCHAR(255)
);

-- Создание таблицы Reservations
CREATE TABLE IF NOT EXISTS Reservations (
    id SERIAL PRIMARY KEY,
    reader_id INTEGER REFERENCES Readers(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES Books(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER,
    CONSTRAINT unique_reservation UNIQUE (reader_id, book_id, start_date, end_date)
);





-- 1. Создание базы данных (на случай первого запуска приложения пользователем)



CREATE OR REPLACE PROCEDURE initialize_database()
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'categories') THEN
        CREATE TABLE categories (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
        RAISE NOTICE 'Table "categories" has been created.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'books') THEN
        CREATE TABLE books (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INT NOT NULL,
            category_id INT,
            CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES categories(id)
        );
        RAISE NOTICE 'Table "books" has been created.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM categories) THEN
        INSERT INTO categories (name) VALUES
        ('Fiction'),
        ('Science'),
        ('History');
        RAISE NOTICE 'Default data has been inserted into the "categories" table.';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM books) THEN
        INSERT INTO books (title, author, year, category_id) VALUES
        ('Example Book 1', 'Author 1', 2020, 1),
        ('Example Book 2', 'Author 2', 2021, 2);
        RAISE NOTICE 'Default data has been inserted into the "books" table.';
    END IF;

    RAISE NOTICE 'Database has been initialized or already exists.';
END;
$$;





-- 2.Удаление базы данных
CREATE EXTENSION IF NOT EXISTS dblink;

CREATE OR REPLACE PROCEDURE delete_database(dbname TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Завершаем все активные соединения с базой данных
    PERFORM pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = dbname AND pid <> pg_backend_pid();  -- Не завершаем текущее соединение

    RAISE NOTICE 'All connections to database % have been terminated.', dbname;

    PERFORM dblink_exec('dbname=postgres', 'DROP DATABASE IF EXISTS ' || quote_ident(dbname));

    RAISE NOTICE 'Database % has been deleted successfully.', dbname;
END;
$$;




-- 3.Вывод содержимого таблиц
CREATE OR REPLACE FUNCTION load_books()
RETURNS TABLE(id INT, title TEXT, author TEXT, year INT, category_id INT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY SELECT id, title, author, year, category_id FROM books;
END;
$$;




-- 4. Очистка (частичная - одной, и полная - всех) таблиц
CREATE OR REPLACE PROCEDURE clear_table(table_name TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('TRUNCATE TABLE %I RESTART IDENTITY CASCADE', table_name);
    RAISE NOTICE 'Table % has been cleared successfully.', table_name;
END;
$$;

CREATE OR REPLACE PROCEDURE clear_all_tables()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE books CASCADE;

    TRUNCATE TABLE readers CASCADE;

    TRUNCATE TABLE reservations CASCADE;

    TRUNCATE TABLE categories CASCADE;

    RAISE NOTICE 'Specified tables have been cleared.';
END;
$$;





-- 5. Добавление новых данных
CREATE OR REPLACE PROCEDURE add_book(
    p_title VARCHAR,
    p_author VARCHAR,
    p_year INTEGER,
    p_category_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Categories WHERE id = p_category_id) THEN
        RAISE EXCEPTION 'Category with id % does not exist', p_category_id;
    END IF;

    INSERT INTO Books (title, author, year, category_id)
    VALUES (p_title, p_author, p_year, p_category_id)
    ON CONFLICT (title) DO NOTHING;
END;
$$;


DROP FUNCTION IF EXISTS add_category;

CREATE FUNCTION add_category(category_name TEXT)
RETURNS VOID AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM categories WHERE category_name = category_name) THEN
        INSERT INTO categories (name)
        VALUES (name);
    ELSE
        RAISE NOTICE 'Категория с именем "%" уже существует', category_name;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 6.Поиск по заранее выбранному (вами) текстовому не ключевому полю
DROP FUNCTION IF EXISTS search_books_by_title;
CREATE OR REPLACE FUNCTION search_books_by_title(
    p_title VARCHAR
)
RETURNS TABLE (
    book_id INTEGER,
    book_title VARCHAR,
    book_author VARCHAR,
    book_year INTEGER,
    book_category_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT Books.id, Books.title, Books.author, Books.year, Books.category_id
    FROM Books
    WHERE Books.title ILIKE '%' || p_title || '%';
END;
$$;
-- Создание индекса для ускорения поиска по названию книги
CREATE INDEX IF NOT EXISTS idx_books_title ON Books (title);





-- 7. Обновление кортежа







-- 8. Удаление по заранее выбранному текстовому не ключевому полю
CREATE OR REPLACE PROCEDURE delete_book(
    p_book_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM Books WHERE id = p_book_id;
END;
$$;
-- 9. Удаление конкретной записи, выбранной пользователем



























-- Процедура для обновления книги с проверкой существования категории
CREATE OR REPLACE PROCEDURE update_book(
    p_book_id INTEGER,
    p_title VARCHAR,
    p_author VARCHAR,
    p_year INTEGER,
    p_category_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Categories WHERE id = p_category_id) THEN
        RAISE EXCEPTION 'Category with id % does not exist', p_category_id;
    END IF;

    UPDATE Books
    SET title = p_title, author = p_author, year = p_year, category_id = p_category_id
    WHERE id = p_book_id;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_book(
    p_book_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM Books WHERE id = p_book_id;
END;
$$;

CREATE OR REPLACE PROCEDURE clear_books()
LANGUAGE plpgsql
AS $$
BEGIN
    TRUNCATE TABLE Books RESTART IDENTITY;
END;
$$;




-- Заполнение таблицы Categories данными
INSERT INTO Categories (name) VALUES ('Научная литература')
ON CONFLICT (name) DO NOTHING;

INSERT INTO Categories (name) VALUES ('Художественная литература')
ON CONFLICT (name) DO NOTHING;

-- Заполнение таблицы Books данными
INSERT INTO Books (title, author, year, category_id)
VALUES ('Война и мир', 'Лев Толстой', 1869, 2)
ON CONFLICT (title) DO NOTHING;

INSERT INTO Books (title, author, year, category_id)
VALUES ('Краткая история времени', 'Стивен Хокинг', 1988, 1)
ON CONFLICT (title) DO NOTHING;



