import datetime

# --- Глобальні налаштування ---

# Словник для транслітерації кирилиці (для аналізу ПІБ)
TRANSLIT_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ie',
    'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i', 'к': 'k', 'л': 'l',
    'м': 'м', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'iu',
    'я': 'ia',
}

# Рядок, що містить усі спецсимволи для перевірки
SPECIAL_CHARS = r"!@#$%^&*()_+-=[]{};':\"\\|,.<>/?~`"


# --- Ключові функції ---

def transliterate(text: str) -> str:
    """Допоміжна функція для транслітерації кириличного тексту на латиницю."""
    return "".join(TRANSLIT_MAP.get(char, char) for char in text.lower())


def get_personal_tokens(name: str, surname: str, dob_str: str) -> set:
    """
    Створює набір "небезпечних токенів" з особистих даних (ПІБ, дата народження).
    Ці токени використовуються для перевірки пароля.
    """
    tokens = set()

    if name:
        tokens.add(name.lower())
        tokens.add(transliterate(name))
    if surname:
        tokens.add(surname.lower())
        tokens.add(transliterate(surname))

    # Обробка дати народження у форматі ДД.ММ.РРРР
    if dob_str:
        try:
            # Використовуємо datetime.datetime для коректної роботи зі стандартним модулем
            dob = datetime.datetime.strptime(dob_str, "%d.%m.%Y")

            # Додаємо компоненти дати
            tokens.add(str(dob.day))
            tokens.add(str(dob.month))
            tokens.add(str(dob.year))
            tokens.add(str(dob.year)[-2:])  # останні 2 цифри року
            tokens.add(f"{dob.day:02d}{dob.month:02d}")  # формат ДДММ
        except ValueError:
            # Ігноруємо, якщо користувач ввів дату неправильно
            pass

    # Повертаємо токени довжиною 2+ символів
    return {token for token in tokens if len(token) >= 2}


def analyze_password(password: str, personal_tokens: set) -> dict:
    """
    Аналізує пароль за критеріями (довжина, класи символів, особисті дані)
    та повертає словник з результатами.
    """
    analysis = {
        "score": 0,
        "problems": [],
        "recommendations": [],
        "personal_matches": [],
        "missing_classes": [],
    }

    # 1. Оцінка довжини
    length = len(password)
    if length < 8:
        analysis["problems"].append("Довжина пароля менша за 8 символів.")
        analysis["score"] += 1
    elif length < 12:
        # Довжина від 8 до 11 - це зона рекомендації, але не проблема.
        analysis["score"] += 4
    else:  # 12+ символів
        analysis["score"] += 6  # Максимальний бонус: 6 балів

    # 2. Оцінка класів символів
    classes = 0
    if any(c.islower() for c in password):
        classes += 1
    else:
        analysis["problems"].append("Відсутні малі літери.")
        analysis["missing_classes"].append("малі літери")

    if any(c.isupper() for c in password):
        classes += 1
    else:
        analysis["problems"].append("Відсутні великі літери.")
        analysis["missing_classes"].append("великі літери")

    if any(c.isdigit() for c in password):
        classes += 1
    else:
        analysis["problems"].append("Відсутні цифри.")
        analysis["missing_classes"].append("цифри")

    if any(c in SPECIAL_CHARS for c in password):
        classes += 1
    else:
        analysis["problems"].append("Відсутні спеціальні символи.")
        analysis["missing_classes"].append("спеціальні символи")

    analysis["score"] += classes  # +4 бали за 4 класи

    # 3. Штрафи за прості послідовності
    password_lower = password.lower()
    if "123" in password or "abc" in password_lower or "qwe" in password_lower:
        analysis["problems"].append("Знайдено прості послідовності (наприклад, '123', 'abc').")
        analysis["score"] -= 2  # Штраф

    # 4. Штрафи за персональні дані (Найбільший штраф)
    for token in personal_tokens:
        if token in password_lower:  # Перевіряємо збіг у нижньому регістрі
            analysis["personal_matches"].append(token)

    if analysis["personal_matches"]:  # Якщо знайдено хоча б один збіг
        analysis["problems"].append("Пароль містить персональні дані!")
        analysis["recommendations"].append("!!! НІКОЛИ не використовуйте особисті дані в паролях !!!")
        analysis["score"] -= 5  # Найбільший штраф

    # 5. Фіналізація оцінки та рекомендацій
    analysis["score"] = max(1, min(10, analysis["score"]))  # Обмежуємо оцінку діапазоном [1, 10]

    # Логіка рекомендацій
    if length < 8:
        analysis["recommendations"].append("Збільште довжину пароля щонайменше до 8 символів.")
    elif length < 12:
        analysis["recommendations"].append("Збільште довжину пароля щонайменше до 12 символів.")

    if analysis["missing_classes"]:
        missing = ", ".join(analysis["missing_classes"])
        analysis["recommendations"].append(f"Додайте символи: {missing}.")

    # Якщо проблем не виявлено, додаємо позитивний відгук
    if not analysis["problems"] and not analysis["personal_matches"]:
        analysis["recommendations"].append("Пароль виглядає надійним.")

    return analysis  # Повертаємо словник з результатами аналізу


def main():
    """
    Головна функція програми, що керує циклом аналізу.
    Особисті дані (ПІБ, ДН) збираються одноразово для підвищення ефективності тестування.
    """
    print("-------------- АНАЛІЗАТОР БЕЗПЕКИ ПАРОЛІВ ---------------")

    # 1. Збір персональних даних (одноразово)
    print("\n=====================================================")
    print(" ЕТАП 1: ВВЕДЕННЯ ОСОБИСТИХ ДАНИХ ДЛЯ АНАЛІЗУ ЗБІГІВ")
    print("=====================================================")

    name = input("Ім'я (напр. Валерій): ")
    surname = input("Прізвище (напр. Швидкой): ")
    dob_str = input("Дата народження (ДД.ММ.РРРР): ")

    # Генерація токенів
    personal_tokens = get_personal_tokens(name, surname, dob_str)
    print(f"\n[i] Створено {len(personal_tokens)} персональних токенів для перевірки.")

    # 2. Основний цикл для тестування паролів
    while True:
        print("\n=====================================================")
        print(" ЕТАП 2: АНАЛІЗ ПАРОЛЯ")
        print("=====================================================")

        # Ввід пароля з можливістю виходу
        password = input("Пароль для аналізу (Введіть 'q' для виходу): ")

        # Умова виходу
        if password.lower() == 'q':
            print("\n--- Завершення роботи аналізатора ---")
            break

        if not password:
            print("[Помилка] Пароль не може бути порожнім. Спробуйте ще раз.")
            continue

        # 3. Аналіз та друк результатів
        result = analyze_password(password, personal_tokens)

        print("\n------------------ РЕЗУЛЬТАТИ АНАЛІЗУ ------------------")

        # Визначення текстового ярлика
        score_label = "Слабкий"
        if result["score"] >= 8:
            score_label = "Дуже сильний"
        elif result["score"] >= 5:
            score_label = "Середній"

        print(f"\nОцінка: {result['score']}/10 ({score_label})")

        # Виведення унікальних персональних збігів
        unique_matches = sorted(list(set(result['personal_matches'])))
        if unique_matches:
            print(f"!!! ЗНАЙДЕНО ПЕРСОНАЛЬНІ ЗБІГИ: {', '.join(unique_matches)}")
        else:
            print("Персональні збіги: відсутні")

        # Виведення унікальних проблем
        if result["problems"]:
            print("\nВиявлені проблеми:")
            for problem in sorted(list(set(result["problems"]))):
                print(f"  • {problem}")

        # Виведення унікальних рекомендацій
        if result["recommendations"]:
            print("\nРекомендації:")
            for rec in sorted(list(set(result["recommendations"]))):
                print(f"  • {rec}")


# --- Точка входу в програму ---
if __name__ == "__main__":
    # Запускаємо головну функцію
    main()
