# main.py
# Головний файл, який збирає всі модулі разом та виконує

# Імпортуємо функції з наших власних модулів
from ciphers import encrypt_caesar, decrypt_caesar, encrypt_vigenere, decrypt_vigenere
from key_generators import generate_caesar_key, generate_vigenere_key
from analysis import bruteforce_caesar, plot_frequencies, calculate_frequencies
from reporting import print_comparison_table, print_conclusions


def main():
    """
    Головна функція:
    1. Збирає персональні дані.
    2. Генерує ключі.
    3. Виконує шифрування/розшифрування.
    4. Демонструє аналіз та висновки.
    5. Запускає бонусні модулі криптоаналізу.
    """
    print("=" * 60)
    print(" ЛАБОРАТОРНА РОБОТА № 2: ЗАХИСТ ОСОБИСТИХ ПОВІДОМЛЕНЬ")
    print(" Виконавець: Швидкой Валерій")
    print("=" * 60)

    # 1. Введення даних
    print("--- 1. ВВЕДЕННЯ ПЕРСОНАЛЬНИХ ДАНИХ ---")
    surname = input("* Введіть ваше прізвище (для ключа Віженера): ")
    date = input("* Введіть вашу дату народження (напр., 11.12.2004): ")

    # Демонстрація на власному тексті [cite: 267]
    original_text = input("* Введіть текст для шифрування: ")

    # Використовуємо текст з прикладу реалізації, якщо нічого не введено
    if not original_text:
        original_text = "Безпека програм та даних – важлива дисципліна"
        print(f"  (Текст не введено. Використано приклад з ТЗ: '{original_text}')")
    print("\n")

    # Конвертуємо у верхній регістр один раз
    original_text_upper = original_text.upper()

    # 2. Генерація ключів
    caesar_shift = generate_caesar_key(date)
    vigenere_key = generate_vigenere_key(surname)

    print("--- 2. ЗГЕНЕРОВАНІ КЛЮЧІ ---")
    print(f"Ключ Цезаря (зсув = сума цифр дати '{date}'): {caesar_shift}")
    print(f"Ключ Віженера (з прізвища '{surname}'): '{vigenere_key}'\n")

    # 3. Шифрування
    print("--- 3. РЕЗУЛЬТАТИ ШИФРУВАННЯ ---")
    caesar_cipher = encrypt_caesar(original_text_upper, caesar_shift)
    vigenere_cipher = encrypt_vigenere(original_text_upper, vigenere_key)

    print(f"Оригінал: {original_text_upper}")
    print(f"Цезар:    {caesar_cipher}")
    print(f"Віженер:  {vigenere_cipher}\n")

    # 4. Перевірка розшифрування
    print("--- 4. ПЕРЕВІРКА РОЗШИФРУВАННЯ ---")
    caesar_decrypted = decrypt_caesar(caesar_cipher, caesar_shift)
    vigenere_decrypted = decrypt_vigenere(vigenere_cipher, vigenere_key)

    print(f"Цезар (розшифр.):    {caesar_decrypted}")
    print(f"Віженер (розшифр.):  {vigenere_decrypted}\n")

    if (caesar_decrypted == original_text_upper and
            vigenere_decrypted == original_text_upper):
        print(">> Перевірка: УСПІШНО! Оригінальний текст відновлено.")
    else:
        print(">> Перевірка: ПОМИЛКА! Текст не відновлено.")

    # 5. Порівняльний аналіз та висновки
    print_comparison_table(vigenere_key, original_text_upper,
                           caesar_cipher, vigenere_cipher)
    print_conclusions()

    # 6. Запуск бонусних функцій (криптоаналіз)
    bruteforce_caesar(caesar_cipher, original_text_upper)

    # Розрахунок частот для графіків
    freq_original = calculate_frequencies(original_text_upper)
    freq_caesar = calculate_frequencies(caesar_cipher)
    freq_vigenere = calculate_frequencies(vigenere_cipher)

    # Побудова графіків (візуалізація)
    plot_frequencies(
        [freq_original, freq_caesar, freq_vigenere],
        [
            f"Оригінальний текст: '{original_text_upper[:40]}'",
            f"Шифр Цезаря (зсув {caesar_shift}): '{caesar_cipher[:40]}'",
            f"Шифр Віженера (ключ '{vigenere_key}'): '{vigenere_cipher[:40]}'"
        ]
    )

    print("\nПрограма успішно завершила роботу.")


# --- ЗАПУСК ПРОГРАМИ ---
if __name__ == "__main__":
    main()