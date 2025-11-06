# analysis.py
# Реалізація бонусних завдань: криптоаналіз та візуалізація

import collections
from ciphers.common import UKR_ALPHABET, ALPHABET_LEN
from ciphers.caesar import decrypt_caesar

# Намагаємось імпортувати matplotlib для бонусного завдання
try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def bruteforce_caesar(ciphertext: str, original_text_upper: str):
    """
    Ключова функція (Бонус): Демонструє Brute Force для шифру Цезаря.
    Друкує всі 32 варіанти перебору та позначає правильний.

    ciphertext: Шифротекст Цезаря.
    original_text_upper: Оригінальний текст для порівняння.
    """
    print("\n--- 🕵️‍♂️ АНАЛІЗ: BRUTE FORCE (ЦЕЗАР) [Бонус] ---")
    print(f"Пошук осмисленого тексту у: '{ciphertext[:50]}'")

    # Проходимо по всіх зсувах
    for shift in range(1, ALPHABET_LEN):
        decrypted_text = decrypt_caesar(ciphertext, shift)

        # Готуємо рядок для виводу
        output_line = f"  Зсув {shift:2}: {decrypted_text[:70]}"

        # Якщо це правильний зсув, додаємо позначку
        if decrypted_text == original_text_upper:
            output_line += "  <-- ЗБІГ!"

        # Друкуємо кожен результат
        print(output_line)


def calculate_frequencies(text: str) -> dict:
    """
    Ключова функція (Бонус): Рахує відносну частоту літер для аналізу.

    text: Вхідний текст.
    Returns: Словник OrderedDict {'літера': частота}, відсортований за алфавітом.
    """
    letters = [char for char in text.upper() if char in UKR_ALPHABET]
    total_letters = len(letters)

    counter = collections.Counter(letters)

    frequencies_ordered = collections.OrderedDict()

    for char in UKR_ALPHABET:
        freq = counter.get(char, 0) / total_letters if total_letters > 0 else 0.0
        frequencies_ordered[char] = freq

    return frequencies_ordered


def plot_frequencies(freq_data_list: list, titles: list):
    """
    Ключова функція (Бонус): Будує стовпчасті діаграми частот.

    freq_data_list: Список словників з даними частот.
    titles: Список заголовків для графіків.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("\n[ПОМИЛКА] Для побудови графіків потрібна бібліотека matplotlib.")
        print("Будь ласка, встановіть її: pip install matplotlib")
        return

    print("\n--- 📊 АНАЛІЗ: ЧАСТОТНИЙ АНАЛІЗ (ГРАФІКИ) [Бонус] ---")
    print("Зачекайте, генерується візуалізація...")

    num_plots = len(freq_data_list)
    fig, axes = plt.subplots(num_plots, 1, figsize=(15, 3 * num_plots), sharey=False)

    if num_plots == 1:
        axes = [axes]

    for i, (data, title) in enumerate(zip(freq_data_list, titles)):
        labels = list(data.keys())
        values = list(data.values())

        axes[i].bar(labels, values, color='cornflowerblue', width=0.6)
        axes[i].set_title(title, fontsize=16)
        axes[i].set_ylabel('Відносна частота', fontsize=12)
        axes[i].set_xlabel('Літера', fontsize=12)
        axes[i].grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    print("Будь ласка, закрийте вікно з графіком, щоб завершити програму.")
    plt.show()