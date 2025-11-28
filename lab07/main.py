import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import time
import csv
# Підключаємо наші модулі
import rsa_manual
import xor_cipher
import stego_lsb


class SecureVaultApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР7: Комплексний захист даних (Швидкой В.В.)")
        self.root.geometry("950x450")

        # Змінні для ключів і статистики
        self.rsa_pub = None
        self.rsa_priv = None
        self.aes_key = None
        self.stats = []

        style = ttk.Style()
        style.theme_use('clam')

        # Робимо вкладки
        nb = ttk.Notebook(root)
        self.t1 = ttk.Frame(nb)
        self.t2 = ttk.Frame(nb)
        self.t3 = ttk.Frame(nb)

        nb.add(self.t1, text="1. Захист")
        nb.add(self.t2, text="2. Відновлення")
        nb.add(self.t3, text="3. Аналітика")
        nb.pack(fill="both", expand=True)

        self.setup_protect()
        self.setup_extract()
        self.setup_analytics()

    # Записуємо статистику в таблицю
    def log_stat(self, scenario, stage, t_start, size):
        duration = (time.time() - t_start) * 1000  # мс
        self.stats.append({"Scenario": scenario, "Stage": stage, "Time": f"{duration:.2f}", "Size": size})
        self.tree.insert("", "end", values=(scenario, stage, f"{duration:.2f} ms", f"{size} bytes"))

    def setup_protect(self):
        f = ttk.LabelFrame(self.t1, text="Керування захистом", padding=20)
        f.pack(padx=20, pady=20, fill="both")

        ttk.Button(f, text="1. Обрати файл (документ)", command=self.get_file).pack(fill="x", pady=5)
        self.lbl_f = ttk.Label(f, text="...");
        self.lbl_f.pack()

        ttk.Button(f, text="2. Обрати картинку (контейнер)", command=self.get_img).pack(fill="x", pady=5)
        self.lbl_i = ttk.Label(f, text="...");
        self.lbl_i.pack()

        ttk.Label(f, text="Пароль:").pack(pady=5)
        self.entry_pass = ttk.Entry(f, show="*");
        self.entry_pass.pack(fill="x")

        # Основна кнопка
        ttk.Button(f, text="🚀 Захистити", command=self.do_protect).pack(fill="x", pady=20)

        # Бонусна кнопка (авто-тест)
        ttk.Button(f, text="📊 Запустити бенчмарк (тест 3-х методів)", command=self.run_benchmark).pack(fill="x", pady=5)

        self.lbl_status = ttk.Label(f, text="", foreground="blue");
        self.lbl_status.pack()

    def setup_extract(self):
        f = ttk.LabelFrame(self.t2, text="Зворотний процес", padding=20)
        f.pack(padx=20, pady=20, fill="both")

        ttk.Button(f, text="Обрати захищену картинку", command=self.get_stego).pack(fill="x", pady=5)
        self.lbl_s = ttk.Label(f, text="...");
        self.lbl_s.pack()

        ttk.Label(f, text="Пароль:").pack(pady=5)
        self.entry_pass_dec = ttk.Entry(f, show="*");
        self.entry_pass_dec.pack(fill="x")

        ttk.Button(f, text="🔓 Відновити", command=self.do_extract).pack(fill="x", pady=20)
        self.lbl_res = ttk.Label(f, text="", font=("Arial", 12));
        self.lbl_res.pack()

    def setup_analytics(self):
        cols = ("Сценарій", "Етап", "Час", "Розмір")
        self.tree = ttk.Treeview(self.t3, columns=cols, show="headings")
        for c in cols: self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(self.t3, text="💾 Експортувати звіт (CSV)", command=self.export_csv).pack(pady=10)

    # --- ВИБІР ФАЙЛІВ ---
    def get_file(self):
        p = filedialog.askopenfilename()
        if p: self.f_path = p; self.lbl_f.config(text=os.path.basename(p))

    def get_img(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg")])
        if p: self.i_path = p; self.lbl_i.config(text=os.path.basename(p))

    def get_stego(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png")])
        if p: self.s_path = p; self.lbl_s.config(text=os.path.basename(p))

    # --- БЕНЧМАРК (БОНУС) ---
    def run_benchmark(self):
        if not hasattr(self, 'f_path') or not self.entry_pass.get():
            messagebox.showwarning("Увага", "Оберіть файл і введіть пароль!")
            return

        self.stats = [];
        self.tree.delete(*self.tree.get_children())
        pwd = self.entry_pass.get()

        # Генеруємо ключі
        rsa_pub, rsa_priv = rsa_manual.generate_keys(pwd)
        xor_key = xor_cipher.generate_key(pwd)

        with open(self.f_path, 'rb') as f:
            raw_data = f.read()

        # 1. Тільки шифрування
        t0 = time.time()
        enc = xor_cipher.encrypt_decrypt(raw_data, xor_key)
        self.log_stat("1. Only Encryption", "XOR", t0, len(enc))

        # 2. Підпис + Шифрування
        t0 = time.time()
        sig = rsa_manual.sign_data(raw_data, rsa_priv)
        # Спрощено для тесту
        pkg = str(sig).encode() + raw_data
        enc_pkg = xor_cipher.encrypt_decrypt(pkg, xor_key)
        self.log_stat("2. Sign + Encrypt", "RSA+XOR", t0, len(enc_pkg))

        # 3. Повний цикл
        if hasattr(self, 'i_path'):
            self.do_protect(is_benchmark=True)
        else:
            messagebox.showinfo("Бенчмарк", "Тести 1-2 готові. Оберіть картинку для Тесту 3.")

    # --- ЗАХИСТ ---
    def do_protect(self, is_benchmark=False):
        if not hasattr(self, 'f_path') or not hasattr(self, 'i_path'): return
        pwd = self.entry_pass.get()

        if not is_benchmark:
            self.stats = [];
            self.tree.delete(*self.tree.get_children())

        try:
            scenario = "3. Full Protect" if is_benchmark else "Manual Run"

            # 1. Ключі
            t0 = time.time()
            pub, priv = rsa_manual.generate_keys(pwd)
            xor_k = xor_cipher.generate_key(pwd)
            self.rsa_pub, self.rsa_priv, self.aes_key = pub, priv, xor_k
            self.log_stat(scenario, "Gen Keys", t0, 0)

            # 2. Підготовка (зберігаємо розширення файлу)
            file_ext = os.path.splitext(self.f_path)[1].encode('utf-8')
            ext_len = len(file_ext).to_bytes(1, 'big')
            with open(self.f_path, 'rb') as f:
                raw_data = f.read()

            # Структура: [Len][Ext][Data]
            data_with_meta = ext_len + file_ext + raw_data

            # 3. Підпис
            t0 = time.time()
            signature = rsa_manual.sign_data(data_with_meta, priv)
            sig_bytes = signature.to_bytes((signature.bit_length() + 7) // 8, 'big')
            sig_len = len(sig_bytes).to_bytes(4, 'big')

            # Структура: [SigLen][Sig][DataWithMeta]
            signed_package = sig_len + sig_bytes + data_with_meta
            self.log_stat(scenario, "Sign (RSA)", t0, len(signed_package))

            # 4. Шифрування
            t0 = time.time()
            encrypted_package = xor_cipher.encrypt_decrypt(signed_package, xor_k)
            self.log_stat(scenario, "Encrypt (XOR)", t0, len(encrypted_package))

            # 5. Стеганографія
            t0 = time.time()
            # Зберігаємо поруч з оригіналом
            dir_name, file_name = os.path.split(self.i_path)
            base_name = os.path.splitext(file_name)[0]
            out_name = os.path.join(dir_name, f"{base_name}_protected.png")

            stego_lsb.hide_data(self.i_path, encrypted_package, out_name)
            self.log_stat(scenario, "Hide (LSB)", t0, os.path.getsize(out_name))

            self.lbl_status.config(text=f"УСПІХ! Файл: {os.path.basename(out_name)}")
            if not is_benchmark:
                messagebox.showinfo("Готово", "Файл захищено!")

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    # --- ВІДНОВЛЕННЯ ---
    def do_extract(self):
        pwd = self.entry_pass_dec.get()
        try:
            # Відновлюємо ключі
            rsa_pub, _ = rsa_manual.generate_keys(pwd)
            xor_key = xor_cipher.generate_key(pwd)
            scenario = "Restore"

            # 1. Витягуємо
            t0 = time.time()
            encrypted_package = stego_lsb.extract_data(self.s_path)
            self.log_stat(scenario, "Unhide (LSB)", t0, len(encrypted_package))

            # 2. Дешифруємо
            t0 = time.time()
            package = xor_cipher.encrypt_decrypt(encrypted_package, xor_key)
            self.log_stat(scenario, "Decrypt (XOR)", t0, len(package))

            # 3. Перевіряємо підпис
            sig_len = int.from_bytes(package[:4], 'big')
            sig_bytes = package[4: 4 + sig_len]
            data_with_meta = package[4 + sig_len:]
            signature = int.from_bytes(sig_bytes, 'big')

            t0 = time.time()
            if rsa_manual.verify_signature(data_with_meta, signature, rsa_pub):
                self.log_stat(scenario, "Verify (RSA)", t0, 0)

                # Розбираємо метадані
                ext_len = int.from_bytes(data_with_meta[:1], 'big')
                file_ext = data_with_meta[1: 1 + ext_len].decode('utf-8')
                real_data = data_with_meta[1 + ext_len:]

                dir_name = os.path.dirname(self.s_path)
                out_path = os.path.join(dir_name, f"restored_file{file_ext}")

                with open(out_path, "wb") as f:
                    f.write(real_data)

                self.lbl_res.config(text=f"✅ ВІРНО! Відновлено: restored_file{file_ext}", foreground="green")
                messagebox.showinfo("Успіх", "Файл відновлено!")
            else:
                self.lbl_res.config(text="❌ Підпис НЕВІРНИЙ!", foreground="red")

        except Exception as e:
            messagebox.showerror("Збій", f"Помилка: {e}")

    def export_csv(self):
        if not self.stats: return
        # utf-8-sig щоб Excel бачив кирилицю
        with open("security_report.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["Scenario", "Stage", "Time", "Size"])
            writer.writeheader()
            writer.writerows(self.stats)
        messagebox.showinfo("Експорт", "Звіт збережено!")


if __name__ == "__main__":
    root = tk.Tk()
    app = SecureVaultApp(root)
    root.mainloop()