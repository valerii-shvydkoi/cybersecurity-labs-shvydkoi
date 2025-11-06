# key_generators.py
# Функції для генерації ключів на основі персональних даних

import re
from ciphers.common import UKR_ALPHABET, ALPHABET_LEN


def generate_caesar_key(date_str: str) -> int:
    """
    Ключова функція: Генерує ключ Цезаря (зсув) як суму цифр у даті.

    date_str: Рядок з датою (напр., "11.12.2004").
    Returns: Числовий зсув (ключ) для шифру Цезаря.
    """
    digits = re.findall(r'\d', date_str)
    if not digits:
        return 1  # Повертаємо 1, якщо дата порожня

    total_sum = sum(int(d) for d in digits)
    shift = total_sum % ALPHABET_LEN

    # Зсув 0 не має сенсу (A -> A). Беремо 1, якщо сума кратна 33.
    if shift == 0 and total_sum > 0:
        return 1
    return shift


def generate_vigenere_key(surname_str: str) -> str:
    """
    Ключова функція: Генерує ключ Віженера з прізвища.

    surname_str: Рядок з прізвищем.
    Returns: Слово-ключ для шифру Віженера.
    """
    # Залишаємо тільки літери, які є в нашому алфавіті
    key = "".join(char for char in surname_str.upper() if char in UKR_ALPHABET)

    # Запобіжник, якщо прізвище не містить українських літер
    return key or "КЛЮЧ"