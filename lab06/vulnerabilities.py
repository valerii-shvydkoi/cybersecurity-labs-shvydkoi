import sqlite3
from db_manager import get_connection


# --- ФІЛЬТР АТАК (WAF) ---
def waf_check(input_str):
    # Простий фільтр: шукаємо "погані" слова
    bad_words = ["'", "--", "UNION", "OR ", "1=1", "DROP", "SELECT"]

    for word in bad_words:
        if word in input_str.upper():  # Перевіряємо без урахування регістру
            return False, word  # Знайшли атаку
    return True, None


# --- ПОШУК (Search) ---

def search_vulnerable(user_input):
    conn = get_connection()
    cursor = conn.cursor()

    # ВРАЗЛИВІСТЬ
    # Я просто вставляю текст користувача прямо в запит.
    # Це дозволяє дописати свій SQL код (напр. ' OR '1'='1).
    query = f"SELECT * FROM students WHERE full_name = '{user_input}'"

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results, query, None
    except Exception as e:
        return [], query, str(e)
    finally:
        conn.close()


def search_secure(user_input):
    conn = get_connection()
    cursor = conn.cursor()

    # ЗАХИСТ (Спосіб 1: '?' style)
    # Використовую знак питання. База сама зрозуміє, що це просто текст.
    query = "SELECT * FROM students WHERE full_name = ?"

    try:
        cursor.execute(query, (user_input,))  # Передаємо дані окремо
        results = cursor.fetchall()
        return results, f"{query} [PARAMS: ('{user_input}',)]", None
    except Exception as e:
        return [], query, str(e)
    finally:
        conn.close()


# --- ЛОГІН (Auth) ---

def login_vulnerable(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    # ВРАЗЛИВІСТЬ
    # Можна зайти як 'admin' --' без пароля
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        cursor.execute(query)
        user = cursor.fetchone()
        return user, query, None
    except Exception as e:
        return None, query, str(e)
    finally:
        conn.close()


def login_secure(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    # ЗАХИСТ (Спосіб 2: Named style)
    # Використовую іменовані параметри (:u, :p) для різноманітності.
    # Це теж безпечно.
    query = "SELECT * FROM users WHERE username = :u AND password = :p"

    try:
        cursor.execute(query, {"u": username, "p": password})
        user = cursor.fetchone()
        return user, f"{query} [PARAMS: {{...}}]", None
    except Exception as e:
        return None, query, str(e)
    finally:
        conn.close()