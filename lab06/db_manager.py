import sqlite3

DB_NAME = 'university.db'


def init_db():
    # Підключаємось до файлу БД (він створиться сам)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Створюємо таблицю студентів (для пошуку)
    cursor.execute('DROP TABLE IF EXISTS students')
    cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            faculty TEXT NOT NULL,
            scholarship INTEGER,
            secret_data TEXT
        )
    ''')

    # Створюємо таблицю адмінів (для логіну)
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Закидаємо тестові дані (мене і фейкових)
    students = [
        ('Швидкой Валерій', 'Інженерія ПЗ', 2000, 'Паспорт: BX776800'),
        ('Коваленко Дмитро', 'Кібербезпека', 1800, 'Паспорт: АВ123456'),
        ('Мельник Олена', 'Економіка', 1500, 'Паспорт: ВC987654'),
        ('Super Admin', 'DEAN OFFICE', 99999, 'ROOT_KEY_XYZ')
    ]

    users = [
        ('admin', 'admin_123', 'Administrator'),
        ('dean', 'dean_2025', 'Dean'),
        ('guest', '12345', 'Student')
    ]

    cursor.executemany('INSERT INTO students (full_name, faculty, scholarship, secret_data) VALUES (?, ?, ?, ?)', students)
    cursor.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users)

    conn.commit()
    conn.close()
    print("[i] База даних готова.")


def get_connection():
    return sqlite3.connect(DB_NAME)