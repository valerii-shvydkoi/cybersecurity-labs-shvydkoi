# ciphers/caesar.py
# Містить логіку для шифру Цезаря

from .common import UKR_ALPHABET, ALPHABET_LEN


def encrypt_caesar(plaintext: str, shift: int) -> str:
    """
    Ключова функція: Шифрує текст шифром Цезаря.

    plaintext: Вхідний текст для шифрування.
    shift: Число (ключ), на яке відбувається зсув.
    Returns: Зашифрований текст.
    """
    ciphertext = ""
    for char in plaintext.upper():
        if char in UKR_ALPHABET:
            index = UKR_ALPHABET.find(char)
            new_index = (index + shift) % ALPHABET_LEN
            ciphertext += UKR_ALPHABET[new_index]
        else:
            # Символи поза алфавітом (пробіли, пунктуація) додаються без змін
            ciphertext += char
    return ciphertext


def decrypt_caesar(ciphertext: str, shift: int) -> str:
    """
    Ключова функція: Розшифровує текст Цезаря.

    ciphertext: Вхідний шифротекст.
    shift: Ключ, який використовувався для шифрування.
    Returns: Розшифрований текст.
    """
    # Розшифрування - це шифрування з негативним зсувом
    return encrypt_caesar(ciphertext, -shift)