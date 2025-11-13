import steganography  # Імпортуємо наш власний модуль
import os  # Для роботи зі шляхами та файлами


def main_menu():
    """Відображає головне меню та керує вибором користувача."""

    print("\n" + "=" * 50)
    print("      ЛР3: СТЕГАНОГРАФІЯ МЕТОДОМ LSB")
    print(" (з шифруванням Віженера та EOF-маркером)")
    print("=" * 50)
    print("1. Приховати (Encode) повідомлення у зображенні")
    print("2. Витягти (Decode) повідомлення з зображення")
    print("q. Вийти")

    choice = input("Ваш вибір (1, 2 або q): ")
    return choice


def handle_encode():
    """Керує процесом приховування з 'розумним' збереженням."""
    print("\n--- РЕЖИМ ПРИХОВУВАННЯ ---")
    image_path = input("* Введіть шлях до зображення-контейнера (напр. image.png): ")

    if not os.path.exists(image_path):
        print(f"[Помилка] Файл не знайдено: {image_path}. Повернення в меню.")
        return

    message = input("* Введіть секретне повідомлення (підтримує кирилицю): ")
    if not message:
        print("[Помилка] Повідомлення не може бути порожнім. Повернення в меню.")
        return

    key = input("* Введіть секретний ключ (пароль) для шифрування (буде видно): ")
    if not key:
        print("[Попередження] Ви не ввели ключ. Повідомлення НЕ буде зашифровано.")

    # --- "Розумна" логіка збереження ---
    print("\n* Введіть шлях/ім'я для нового файлу (напр. encoded_image.png)")
    output_path_input = input("  (або натисніть ENTER для авто-імені [original_encoded.png]): ")

    output_path = ""
    # Визначаємо папку та ім'я оригінального файлу
    dir_name, file_name = os.path.split(image_path)
    base_name, _ = os.path.splitext(file_name)

    if not output_path_input:
        # 1. КОРИСТУВАЧ НАТИСНУВ ENTER (Авто-ім'я)
        output_base = os.path.join(dir_name, f"{base_name}_encoded")
        output_path = f"{output_base}.png"  # Завжди зберігаємо в PNG

        # --- Логіка уникнення перезапису ---
        counter = 1
        while os.path.exists(output_path):
            # Якщо 'task2_encoded.png' існує, пробуємо 'task2_encoded (1).png'
            output_path = f"{output_base} ({counter}).png"
            counter += 1
        # ---------------------------------

    else:
        # 2. КОРИСТУВАЧ ВВІВ ІМ'Я
        output_path = output_path_input

        # 3. ЗАХИСТ ВІД ПЕРЕЗАПИСУ ОРИГІНАЛУ
        if os.path.abspath(output_path) == os.path.abspath(image_path):
            print(f"\n[ПОМИЛКА] Ви не можете перезаписати оригінальний файл!")
            print(f"Спробуйте інше ім'я.")
            return

        # (Бонус) Додаємо .png, якщо користувач забув вказати розширення
        if not os.path.splitext(output_path)[1]:
            output_path += ".png"
    # ----------------------------------------------

    steganography.hide_message(image_path, message, key, output_path)


def handle_decode():
    """Керує процесом витягування."""
    print("\n--- РЕЖИМ ВИТЯГУВАННЯ ---")
    image_path = input("* Введіть шлях до стегоконтейнера (напр. encoded_image.png): ")

    if not os.path.exists(image_path):
        print(f"[Помилка] Файл не знайдено: {image_path}. Повернення в меню.")
        return

    key = input("* Введіть секретний ключ (пароль) для розшифрування (буде видно): ")
    if not key:
        print("[Попередження] Ви не ввели ключ. Спроба розшифрувати без ключа.")

    message = steganography.extract_message(image_path, key)

    if message:
        print("\n--- ЗНАЙДЕНЕ ПОВІДОМЛЕННЯ ---")
        print(message)
    else:
        print("\n[i] Повідомлення не знайдено (можливо, невірний ключ?).")


# --- Головний цикл програми ---
if __name__ == "__main__":
    while True:
        user_choice = main_menu()

        if user_choice == '1':
            handle_encode()
        elif user_choice == '2':
            handle_decode()
        elif user_choice.lower() == 'q':
            print("\n--- Завершення роботи ---")
            break
        else:
            print("\n[Помилка] Невідома команда. Спробуйте 1, 2 або q.")