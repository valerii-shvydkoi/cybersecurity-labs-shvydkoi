from PIL import Image
import struct


# Ховаємо дані в картинку
def hide_data(image_path, data, output_path):
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Додаємо 4 байти на початку - це розмір нашого файлу
    # Щоб потім знати, скільки читати
    header = struct.pack('>I', len(data))
    full_payload = header + data

    # Перевіряємо, чи влізе файл у картинку
    if len(full_payload) * 8 > width * height * 3:
        raise ValueError("Картинка замала! Візьміть більшу.")

    # Переводимо все в біти (0 і 1)
    bits = ''.join(format(byte, '08b') for byte in full_payload)
    bits_len = len(bits)

    idx = 0
    for y in range(height):
        for x in range(width):
            # Беремо піксель
            r, g, b = pixels[x, y]

            # Записуємо біти в молодші розряди (LSB) кожного кольору
            if idx < bits_len:
                r = (r & ~1) | int(bits[idx]);
                idx += 1
            if idx < bits_len:
                g = (g & ~1) | int(bits[idx]);
                idx += 1
            if idx < bits_len:
                b = (b & ~1) | int(bits[idx]);
                idx += 1

            pixels[x, y] = (r, g, b)
            if idx >= bits_len: break
        if idx >= bits_len: break

    # Зберігаємо тільки в PNG (без стиснення)
    img.save(output_path, "PNG")


# Дістаємо дані назад
def extract_data(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    # Генератор, щоб читати біти по одному
    def bit_generator():
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                yield r & 1
                yield g & 1
                yield b & 1

    bits = bit_generator()

    # 1. Читаємо перші 32 біти (розмір файлу)
    size_bits = ""
    for _ in range(32):
        size_bits += str(next(bits))

    data_size = int(size_bits, 2)

    # 2. Читаємо саме повідомлення
    data_bits = ""
    total_bits = data_size * 8
    for _ in range(total_bits):
        data_bits += str(next(bits))

    # Збираємо біти назад у байти
    data_bytes = bytearray()
    for i in range(0, len(data_bits), 8):
        byte_str = data_bits[i:i + 8]
        data_bytes.append(int(byte_str, 2))

    return bytes(data_bytes)