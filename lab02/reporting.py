# reporting.py
# Функції для виведення порівняльного аналізу та висновків

from ciphers.common import ALPHABET_LEN


def print_comparison_table(vigenere_key: str, original_text: str,
                           caesar_cipher: str, vigenere_cipher: str):
    """
    Ключова функція: Друкує порівняльну таблицю згідно з ТЗ.
    Містить: довжина результату, читабельність, складність ключа.
    """

    key_len = len(vigenere_key)
    try:
        if key_len > 15:
            vigenere_complexity_str = f"{ALPHABET_LEN}^{key_len} (дуже велике)"
        else:
            # Форматуємо число з роздільниками для читабельності
            vigenere_complexity_str = f"{ALPHABET_LEN ** key_len:,}"
    except OverflowError:
        vigenere_complexity_str = f"{ALPHABET_LEN}^{key_len} (дуже велике)"

    # Форматуємо опис складності ключа
    caesar_key_desc = f"1 (зсув 1-{ALPHABET_LEN - 1})"
    vigenere_key_desc = f"Довжина {key_len}, складність {vigenere_complexity_str}"

    # Форматуємо довжину
    caesar_len_desc = f"{len(caesar_cipher)} (оригінал: {len(original_text)})"
    vigenere_len_desc = f"{len(vigenere_cipher)} (оригінал: {len(original_text)})"

    print("\n--- 5. ПОРІВНЯЛЬНИЙ АНАЛІЗ ---")
    print(f"{'Критерій':<25} | {'Шифр Цезаря':<35} | {'Шифр Віженера':<35}")
    print("-" * 100)

    print(f"{'Довжина результату':<25} | {caesar_len_desc:<35} | {vigenere_len_desc:<35}")
    print(
        f"{'Читабельність (візуально)':<25} | {'Середня (закономірності видно)':<35} | {'Середня/Низька (випадковий набір)':<35}")
    print(f"{'Складність ключа':<25} | {caesar_key_desc:<35} | {vigenere_key_desc:<35}")


def print_conclusions():
    """
    Ключова функція: Друкує висновки про стійкість.
    """
    print("\nВисновки:")
    print("1. Шифр Цезаря є академічним і не надає реального захисту. Його")
    print("   слабкість у тому, що він зберігає частотні характеристики мови")
    print("   (лише зсуває їх), що робить його вразливим до частотного аналізу")
    print("   та тривіальним для 'brute force'.")
    print("2. Шифр Віженера значно стійкіший. Завдяки поліалфавітній заміні")
    print("   (різні літери тексту шифруються різними зсувами), він 'розмиває'")
    print("   статистичні частоти літер, роблячи простий частотний аналіз")
    print("   неефективним. Це наочно показують графіки.")