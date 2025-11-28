import hashlib


# Робимо нормальний ключ (256 біт) з пароля
def generate_key(password):
    return hashlib.sha256(password.encode()).digest()


# Універсальна функція: і шифрує, і дешифрує
def encrypt_decrypt(data, key):
    key_len = len(key)
    # Використовуємо bytearray, щоб змінювати байти на місці
    result = bytearray()

    for i, byte in enumerate(data):
        # XOR кожного байта з байтом ключа по колу
        result.append(byte ^ key[i % key_len])

    return bytes(result)