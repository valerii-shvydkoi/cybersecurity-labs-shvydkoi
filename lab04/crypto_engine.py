import random
import hashlib
import json
import sys

# Збільшуємо ліміт для рекурсії/обчислень
sys.set_int_max_str_digits(10000)

HASH_ALGOS = {
    'SHA-256': hashlib.sha256,
    'SHA-512': hashlib.sha512,
    'MD5': hashlib.md5
}


def is_prime(n, k=5):
    """Тест Міллера-Рабіна на простоту."""
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_large_prime(bits=512):
    """Генерує велике просте число."""
    while True:
        num = random.getrandbits(bits)
        # Робимо непарним і встановлюємо старші біти
        num |= (1 << bits - 1) | 1
        if is_prime(num):
            return num


def gcd(a, b):
    """Найбільший спільний дільник."""
    while b:
        a, b = b, a % b
    return a


def mod_inverse(a, m):
    """Обернений елемент за модулем (Розширений алгоритм Евкліда)."""
    m0, x0, x1 = m, 0, 1
    if m == 1: return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0: x1 += m0
    return x1


def generate_keys_from_data(name: str, dob: str, secret: str) -> (bytes, bytes):
    """
    Генерує ключі RSA вручну на основі персональних даних.
    """
    # 1. Персоналізація генератора
    seed_str = f"{name}|{dob}|{secret}"
    seed_int = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16)
    random.seed(seed_int)

    print("Генерація простих чисел (це може зайняти кілька секунд)...")

    # 2. Генерація p та q (зменшимо бітність до 256 для швидкості в демо)
    p = generate_large_prime(256)
    q = generate_large_prime(256)

    # 3. Обчислення n та функції Ейлера (phi)
    n = p * q
    phi = (p - 1) * (q - 1)

    # 4. Вибір e (публічна експонента)
    e = 65537
    if gcd(e, phi) != 1:  # Малоймовірно, але перевіримо
        e = 3
        while gcd(e, phi) != 1:
            e += 2

    # 5. Обчислення d (приватна експонента)
    d = mod_inverse(e, phi)

    # Формуємо ключі як словники
    pub_key = {"e": e, "n": n}
    priv_key = {"d": d, "n": n}

    # Серіалізуємо в JSON bytes для збереження
    return json.dumps(pub_key).encode(), json.dumps(priv_key).encode()


def sign_file(file_path: str, private_key_bytes: bytes, hash_algo_name: str) -> str:
    """
    Створює цифровий підпис вручну: s = m^d mod n.
    """
    # 1. Завантажуємо ключ
    priv_key = json.loads(private_key_bytes)
    d, n = priv_key["d"], priv_key["n"]

    # 2. Читаємо та хешуємо файл
    hasher = HASH_ALGOS[hash_algo_name]()
    with open(file_path, 'rb') as f:
        file_data = f.read()
        hasher.update(file_data)

    file_hash_int = int(hasher.hexdigest(), 16)

    # 3. Математика підпису (RSA): s = hash^d mod n
    signature_int = pow(file_hash_int, d, n)

    # 4. Зберігаємо підпис
    sig_path = file_path + ".sig"
    with open(sig_path, 'w') as f:
        # Зберігаємо як hex-рядок для зручності читання
        f.write(hex(signature_int))

    return sig_path


def verify_signature(file_path: str, sig_path: str, public_key_bytes: bytes) -> bool:
    """
    Перевіряє підпис вручну: h' = s^e mod n.
    """
    try:
        # 1. Завантажуємо ключ
        pub_key = json.loads(public_key_bytes)
        e, n = pub_key["e"], pub_key["n"]

        # 2. Читаємо підпис
        with open(sig_path, 'r') as f:
            signature_int = int(f.read(), 16)

        # 3. Математика перевірки (RSA): decrypted_hash = s^e mod n
        decrypted_hash_int = pow(signature_int, e, n)

        # 4. Обчислюємо реальний хеш файлу
        with open(file_path, 'rb') as f:
            file_data = f.read()

        for algo_name, algo_func in HASH_ALGOS.items():
            hasher = algo_func()
            hasher.update(file_data)
            current_hash_int = int(hasher.hexdigest(), 16)

            if current_hash_int == decrypted_hash_int:
                return True  # Знайшли збіг!

        return False  # Жоден хеш не підійшов

    except Exception as ex:
        print(f"Помилка верифікації: {ex}")
        return False