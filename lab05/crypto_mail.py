import hashlib
import base64
import os


def generate_key_from_data(personal_data: str) -> bytes:
    # Створюємо ключ із даних користувача (ПІБ + дата + пароль)
    # Використовуємо SHA-256, щоб отримати фіксований набір байтів
    data_bytes = personal_data.encode('utf-8')
    return hashlib.sha256(data_bytes).digest()


def save_key_to_file(key: bytes, filename: str):
    # Зберігаємо ключ у файл, щоб передати другу
    with open(filename, "wb") as f:
        f.write(key)


def load_key_from_file(filename: str) -> bytes:
    # Завантажуємо ключ з файлу
    with open(filename, "rb") as f:
        return f.read()


def _xor_data(data: bytes, key: bytes) -> bytes:
    # Наш власний алгоритм шифрування (XOR)
    # Просто "змішуємо" байти повідомлення з байтами ключа
    key_len = len(key)
    result = bytearray()

    for i, byte in enumerate(data):
        # Беремо байт ключа по колу
        result.append(byte ^ key[i % key_len])

    return bytes(result)


def encrypt_text(message: str, key: bytes) -> str:
    # 1. Переводимо текст у байти
    message_bytes = message.encode('utf-8')
    # 2. Шифруємо нашим методом
    encrypted_bytes = _xor_data(message_bytes, key)
    # 3. Кодуємо в Base64, щоб вийшов гарний рядок для пошти
    return base64.b64encode(encrypted_bytes).decode('utf-8')


def decrypt_text(encrypted_message_b64: str, key: bytes) -> str:
    try:
        # Розкодовуємо з Base64 назад у байти
        encrypted_bytes = base64.b64decode(encrypted_message_b64)
        # Дешифруємо (XOR працює так само в обидві сторони)
        decrypted_bytes = _xor_data(encrypted_bytes, key)
        return decrypted_bytes.decode('utf-8')
    except Exception:
        return "[ПОМИЛКА] Не той ключ або текст пошкоджено"


def encrypt_file(file_path: str, key: bytes) -> str:
    # Читаємо файл як набір байтів
    with open(file_path, "rb") as file:
        file_data = file.read()

    encrypted_data = _xor_data(file_data, key)

    # Додаємо розширення .enc
    output_path = file_path + ".enc"
    with open(output_path, "wb") as file:
        file.write(encrypted_data)

    return output_path


def decrypt_file(file_path: str, key: bytes) -> str:
    # Читаємо зашифрований файл
    with open(file_path, "rb") as file:
        encrypted_data = file.read()

    decrypted_data = _xor_data(encrypted_data, key)

    # Відновлюємо оригінальну назву (прибираємо .enc)
    if file_path.endswith(".enc"):
        output_path = file_path[:-4]
    else:
        output_path = file_path + ".decrypted"

    with open(output_path, "wb") as file:
        file.write(decrypted_data)

    return output_path