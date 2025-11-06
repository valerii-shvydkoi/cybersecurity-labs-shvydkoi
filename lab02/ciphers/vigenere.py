# ciphers/vigenere.py
# Містить логіку для шифру Віженера

from .common import UKR_ALPHABET, ALPHABET_LEN


def encrypt_vigenere(plaintext: str, key_word: str) -> str:
    """
    Ключова функція: Шифрує текст шифром Віженера.

    plaintext: Вхідний текст для шифрування.
    key_word: Слово (ключ), яке використовується для поліалфавітного зсуву.
    Returns: Зашифрований текст.
    """
    ciphertext = ""
    key_index = 0
    key_word = key_word.upper()

    # Перевірка на випадок порожнього ключа
    if not key_word:
        return plaintext.upper()

    for char in plaintext.upper():
        if char in UKR_ALPHABET:
            # Знаходимо індекс літери тексту
            text_index = UKR_ALPHABET.find(char)

            # Знаходимо поточну літеру ключа та її зсув
            key_char = key_word[key_index % len(key_word)]
            key_shift = UKR_ALPHABET.find(key_char)

            # Застосовуємо зсув (як у Цезаря, але з динамічним ключем)
            new_index = (text_index + key_shift) % ALPHABET_LEN
            ciphertext += UKR_ALPHABET[new_index]

            # Індекс ключа рухається, лише якщо ми зашифрували літеру
            key_index += 1
        else:
            ciphertext += char
    return ciphertext


def decrypt_vigenere(ciphertext: str, key_word: str) -> str:
    """
    Ключова функція: Розшифровує текст Віженера.

    ciphertext: Вхідний шифротекст.
    key_word: Ключ, який використовувався для шифрування.
    Returns: Розшифрований текст.
    """
    plaintext = ""
    key_index = 0
    key_word = key_word.upper()

    if not key_word:
        return ciphertext

    for char in ciphertext.upper():
        if char in UKR_ALPHABET:
            # Знаходимо індекс літери шифротексту
            cipher_index = UKR_ALPHABET.find(char)

            # Знаходимо поточну літеру ключа та її зсув
            key_char = key_word[key_index % len(key_word)]
            key_shift = UKR_ALPHABET.find(key_char)

            # Застосовуємо зворотній зсув
            new_index = (cipher_index - key_shift + ALPHABET_LEN) % ALPHABET_LEN
            plaintext += UKR_ALPHABET[new_index]

            key_index += 1
        else:
            plaintext += char
    return plaintext