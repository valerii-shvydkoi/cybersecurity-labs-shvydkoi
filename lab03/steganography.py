from PIL import Image

# Маркер кінця повідомлення (EOF - End Of File)
# Вирішує проблему "цифрового шуму" (Крок 1) та є бонусною вимогою.
EOF_MARKER = "||[EOF]||"


def _apply_vigenere(data_bytes: bytes, key: str, mode: str) -> bytes:
    """
    (Бонус) Застосовує шифр Віженера. Працює виключно на байтах.

    Args:
        data_bytes (bytes): Вхідні байти (з тексту або шифротексту).
        key (str): Ключ (пароль) у вигляді UTF-8 рядка.
        mode (str): 'encrypt' (зашифрувати) або 'decrypt' (розшифрувати).

    Returns:
        bytes: Результат операції (зашифровані або розшифровані байти).
    """
    if not key:
        return data_bytes

    result_bytes = bytearray()
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)

    for i, byte in enumerate(data_bytes):
        key_byte = key_bytes[i % key_len]

        if mode == 'encrypt':
            new_byte = (byte + key_byte) & 0xFF
        else:  # 'decrypt'
            new_byte = (byte - key_byte + 256) & 0xFF

        result_bytes.append(new_byte)

    return bytes(result_bytes)


def bytes_to_binary(data_bytes: bytes) -> str:
    """Допоміжна функція: Конвертує байти у бінарний рядок."""
    return ''.join(format(byte, '08b') for byte in data_bytes)


def binary_to_bytes(binary_data: str) -> bytes:
    """Допоміжна функція: Конвертує бінарний рядок назад у байти."""
    byte_array = bytearray()
    for i in range(0, len(binary_data), 8):
        byte_chunk = binary_data[i:i + 8]
        if len(byte_chunk) == 8:
            byte_array.append(int(byte_chunk, 2))
    return bytes(byte_array)


def hide_message(image_path: str, message: str, key: str, output_path: str):
    """
    Ключова функція: Приховує повідомлення у зображенні.
    Виконує шифрування Віженером та додає EOF маркер.
    """
    print(f"[i] Завантаження зображення: {image_path}")
    try:
        image = Image.open(image_path).convert('RGB')
    except FileNotFoundError:
        print(f"[Помилка] Файл не знайдено: {image_path}")
        return False

    # 1. Додаємо маркер до повідомлення (str + str)
    message_with_marker = message + EOF_MARKER

    # 2. Конвертуємо в байти (UTF-8)
    message_bytes = message_with_marker.encode('utf-8')

    # 3. Шифруємо байти (якщо є ключ)
    if key:
        data_to_hide = _apply_vigenere(message_bytes, key, 'encrypt')
        print(f"[i] Повідомлення зашифровано ключем.")
    else:
        data_to_hide = message_bytes
        print("[Попередження] Ключ не введено. Приховування тексту без шифрування.")

    # 4. Конвертуємо фінальні байти в бінарний рядок
    binary_message = bytes_to_binary(data_to_hide)
    message_length = len(binary_message)

    width, height = image.size
    total_pixels = width * height

    # Перевіряємо, чи достатньо місця (кожен піксель = 3 біти: R, G, B)
    if message_length > total_pixels * 3:
        print(f"[Помилка] Повідомлення занадто велике для цього зображення.")
        print(f"  Потрібно: {message_length} біт")
        print(f"  Доступно: {total_pixels * 3} біт.")
        return False

    print(f"[i] Приховування {message_length} біт у {total_pixels} пікселів...")

    pixels = image.load()
    data_index = 0

    # Проходимо по кожному пікселю та кожному каналу (R, G, B)
    for y in range(height):
        for x in range(width):
            # Використовуємо list(), щоб мати можливість змінювати піксель
            pixel = list(pixels[x, y])

            for channel in range(3):  # 0=R, 1=G, 2=B
                if data_index < message_length:
                    # "Хірургічна" заміна молодшого біта
                    bit = binary_message[data_index]
                    pixel[channel] = (pixel[channel] & ~1) | int(bit)
                    data_index += 1

            pixels[x, y] = tuple(pixel)

            if data_index >= message_length: break
        if data_index >= message_length: break

    # Зберігаємо у PNG (формат без втрат), щоб уникнути
    # побічних ефектів стиснення JPEG/PNG, виявлених у Кроці 2.
    image.save(output_path, "PNG")
    print(f"\n[Успіх] Повідомлення приховано та збережено у: {output_path}")
    return True


def extract_message(image_path: str, key: str) -> str:
    """
    Ключова функція: Витягує повідомлення з зображення.
    Шукає EOF маркер та виконує дешифрування Віженером.
    """
    print(f"[i] Завантаження зображення для аналізу: {image_path}")
    try:
        image = Image.open(image_path).convert('RGB')
    except FileNotFoundError:
        print(f"[Помилка] Файл не знайдено: {image_path}")
        return None

    pixels = image.load()
    width, height = image.size

    binary_message = ""
    print("[i] Початок LSB-аналізу... Читання бітів...")

    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            for channel in range(3):  # 0=R, 1=G, 2=B
                # Читаємо молодший біт
                bit = pixel[channel] & 1
                binary_message += str(bit)

                # Оптимізація: перевіряємо кожні 8 біт (1 байт)
                if len(binary_message) % 8 == 0:

                    # 1. Конвертуємо біти в байти
                    current_bytes = binary_to_bytes(binary_message)

                    # 2. Дешифруємо байти (якщо є ключ)
                    data_to_check = _apply_vigenere(current_bytes, key, 'decrypt')

                    # 3. Намагаємося декодувати як UTF-8
                    try:
                        current_text = data_to_check.decode('utf-8')

                        # 4. Перевіряємо маркер
                        if current_text.endswith(EOF_MARKER):
                            print("[Успіх] Знайдено маркер кінця повідомлення [EOF].")
                            if key:
                                print(f"[i] Повідомлення дешифровано.")
                            # Повертаємо текст БЕЗ маркера
                            return current_text[:-len(EOF_MARKER)]

                    except UnicodeDecodeError:
                        # Це нормально, ми просто ще не дочитали
                        # повний UTF-8 символ. Продовжуємо читати.
                        continue

    print("[Помилка] Прочитано все зображення, але маркер [EOF] не знайдено.")
    return None