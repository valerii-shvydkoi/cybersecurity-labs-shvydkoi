import random
import hashlib
import sys

# Дозволяємо пітону рахувати дуже великі числа (для ключів)
sys.set_int_max_str_digits(10000)


# Перевірка числа на простоту (тест Міллера-Рабіна)
def is_prime(n, k=5):
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
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True


# Генеруємо велике просте число
def generate_large_prime(bits=256):
    while True:
        # Ставимо біти, щоб число було непарним і потрібної довжини
        num = random.getrandbits(bits) | (1 << bits - 1) | 1
        if is_prime(num): return num


def gcd(a, b):
    while b: a, b = b, a % b
    return a


# Шукаємо обернене число (потрібно для приватного ключа)
def mod_inverse(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1: return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0: x1 += m0
    return x1


# Головна функція: робить пару ключів з пароля
def generate_keys(seed_data):
    # Робимо хеш від пароля, щоб ключі завжди були ті самі
    seed_val = int(hashlib.sha256(seed_data.encode()).hexdigest(), 16)
    random.seed(seed_val)

    # 1. Генеруємо p і q
    p = generate_large_prime()
    q = generate_large_prime()
    n = p * q
    phi = (p - 1) * (q - 1)

    # 2. Шукаємо e (публічна частина)
    e = 65537
    if gcd(e, phi) != 1:
        e = 3
        while gcd(e, phi) != 1: e += 2

    # 3. Шукаємо d (приватна частина)
    d = mod_inverse(e, phi)

    return {"e": e, "n": n}, {"d": d, "n": n}


# Створення підпису (шифруємо хеш файлу)
def sign_data(data, priv_key):
    # Спочатку хеш (SHA-256)
    data_hash = int(hashlib.sha256(data).hexdigest(), 16)
    # Формула RSA: s = m^d mod n
    signature = pow(data_hash, priv_key['d'], priv_key['n'])
    return signature


# Перевірка підпису
def verify_signature(data, signature, pub_key):
    real_hash = int(hashlib.sha256(data).hexdigest(), 16)
    # Розшифровуємо підпис: h = s^e mod n
    decrypted_hash = pow(signature, pub_key['e'], pub_key['n'])
    return real_hash == decrypted_hash