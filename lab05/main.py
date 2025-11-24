import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import crypto_mail
import os


class SecureEmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР5: Email шифратор (Швидкой В.В.)")
        self.root.geometry("600x650")

        self.current_key = None

        # Створюємо вкладки для зручності
        tab_control = ttk.Notebook(root)
        self.tab_setup = ttk.Frame(tab_control)
        self.tab_msg = ttk.Frame(tab_control)
        self.tab_file = ttk.Frame(tab_control)

        tab_control.add(self.tab_setup, text='1. Управління ключем')
        tab_control.add(self.tab_msg, text='2. Повідомлення')
        tab_control.add(self.tab_file, text='3. Файли')
        tab_control.pack(expand=1, fill="both")

        self._init_setup_tab()
        self._init_msg_tab()
        self._init_file_tab()

    def _init_setup_tab(self):
        # Блок генерації власного ключа
        frame = ttk.LabelFrame(self.tab_setup, text="Спосіб 1: Створити свій ключ", padding=20)
        frame.pack(padx=20, pady=10, fill="x")

        ttk.Label(frame, text="Ваш Email або ПІБ:").pack(anchor="w")
        self.entry_id = ttk.Entry(frame, width=50)
        self.entry_id.pack(fill="x", pady=5)
        self.entry_id.insert(0, "Valerii Shvydkoi")

        ttk.Label(frame, text="Дата народження:").pack(anchor="w")
        self.entry_dob = ttk.Entry(frame, width=50)
        self.entry_dob.pack(fill="x", pady=5)
        self.entry_dob.insert(0, "11.12.2004")

        ttk.Label(frame, text="Секретна фраза (пароль):").pack(anchor="w", pady=(10, 0))
        self.entry_pass = ttk.Entry(frame, width=50, show="*")
        self.entry_pass.pack(fill="x", pady=5)

        ttk.Button(frame, text="Згенерувати ключ", command=self.generate_key).pack(pady=10, fill="x")

        # Блок для збереження/завантаження (щоб передати другу)
        frame2 = ttk.LabelFrame(self.tab_setup, text="Спосіб 2: Файл ключа (для обміну)", padding=20)
        frame2.pack(padx=20, pady=10, fill="x")

        btn_frame = ttk.Frame(frame2)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="💾 Зберегти ключ у файл", command=self.save_key).pack(side="left", expand=True,
                                                                                         fill="x", padx=5)
        ttk.Button(btn_frame, text="📂 Завантажити ключ", command=self.load_key).pack(side="left", expand=True, fill="x",
                                                                                     padx=5)

        self.lbl_status_key = ttk.Label(self.tab_setup, text="Ключ не встановлено", foreground="red",
                                        font=("Arial", 10, "bold"))
        self.lbl_status_key.pack(pady=10)

    def _init_msg_tab(self):
        frame = ttk.LabelFrame(self.tab_msg, text="Шифрування тексту", padding=20)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(frame, text="Введіть текст або вставте шифр:").pack(anchor="w")
        self.txt_input = tk.Text(frame, height=8)
        self.txt_input.pack(fill="x", pady=5)

        # Кнопка вставки для зручності
        ttk.Button(frame, text="📋 Вставити з буфера", command=self.paste_from_clipboard).pack(anchor="e", pady=(0, 10))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="🔒 ЗАШИФРУВАТИ", command=self.encrypt_text).pack(side="left", expand=True, fill="x",
                                                                                    padx=5)
        ttk.Button(btn_frame, text="🔓 РОЗШИФРУВАТИ", command=self.decrypt_text).pack(side="left", expand=True, fill="x",
                                                                                     padx=5)

        ttk.Label(frame, text="Результат:").pack(anchor="w", pady=(10, 0))
        self.txt_output = tk.Text(frame, height=8, bg="#f0f0f0")
        self.txt_output.pack(fill="x", pady=5)

        ttk.Button(frame, text="📋 Копіювати результат", command=self.copy_to_clipboard).pack(anchor="e", pady=5)

    def _init_file_tab(self):
        frame = ttk.LabelFrame(self.tab_file, text="Робота з файлами", padding=20)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Button(frame, text="Обрати файл", command=self.select_file).pack(fill="x")
        self.lbl_file = ttk.Label(frame, text="Файл не обрано")
        self.lbl_file.pack(pady=5)

        ttk.Button(frame, text="Зашифрувати файл (.enc)", command=self.encrypt_file).pack(fill="x", pady=10)
        ttk.Button(frame, text="Розшифрувати файл", command=self.decrypt_file).pack(fill="x", pady=10)

        self.lbl_status_file = ttk.Label(frame, text="")
        self.lbl_status_file.pack()

    # --- ФУНКЦІОНАЛ ---

    def generate_key(self):
        # Збираємо дані в одну купу
        data = self.entry_id.get() + self.entry_dob.get() + self.entry_pass.get()
        if not self.entry_id.get() or not self.entry_pass.get():
            messagebox.showwarning("Увага", "Заповніть хоча б ПІБ і пароль!")
            return

        self.current_key = crypto_mail.generate_key_from_data(data)
        self.lbl_status_key.config(text="✅ Ключ створено", foreground="green")
        messagebox.showinfo("Готово", "Ключ успішно згенеровано!")

    def save_key(self):
        if not self.current_key:
            messagebox.showwarning("Увага", "Спочатку створіть ключ!")
            return
        path = filedialog.asksaveasfilename(defaultextension=".key", filetypes=[("Key files", "*.key")])
        if path:
            crypto_mail.save_key_to_file(self.current_key, path)
            messagebox.showinfo("Готово", f"Ключ збережено у файл:\n{os.path.basename(path)}")

    def load_key(self):
        path = filedialog.askopenfilename(filetypes=[("Key files", "*.key")])
        if path:
            try:
                self.current_key = crypto_mail.load_key_from_file(path)
                self.lbl_status_key.config(text=f"✅ Ключ завантажено: {os.path.basename(path)}", foreground="blue")
                messagebox.showinfo("Готово", "Ключ завантажено!")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося прочитати файл: {e}")

    def encrypt_text(self):
        if not self.current_key:
            messagebox.showwarning("Помилка", "Немає ключа! Згенеруйте або завантажте його.")
            return
        msg = self.txt_input.get("1.0", tk.END).strip()
        if not msg: return
        try:
            enc = crypto_mail.encrypt_text(msg, self.current_key)
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert("1.0", enc)
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def decrypt_text(self):
        if not self.current_key:
            messagebox.showwarning("Помилка", "Немає ключа!")
            return
        enc_msg = self.txt_input.get("1.0", tk.END).strip()
        if not enc_msg: return
        try:
            dec = crypto_mail.decrypt_text(enc_msg, self.current_key)
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert("1.0", dec)
        except Exception as e:
            messagebox.showerror("Помилка", "Не вдалося розшифрувати.")

    def copy_to_clipboard(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            messagebox.showinfo("Інфо", "Скопійовано в буфер!")
        else:
            messagebox.showwarning("Увага", "Пусто, нічого копіювати.")

    def paste_from_clipboard(self):
        try:
            text = self.root.clipboard_get()
            self.txt_input.delete("1.0", tk.END)
            self.txt_input.insert("1.0", text)
        except tk.TclError:
            pass

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path: self.lbl_file.config(text=os.path.basename(self.file_path))

    def encrypt_file(self):
        if not hasattr(self, 'file_path') or not self.current_key:
            messagebox.showwarning("Увага", "Оберіть файл і ключ!")
            return
        try:
            out = crypto_mail.encrypt_file(self.file_path, self.current_key)
            self.lbl_status_file.config(text=f"Готово! Файл: {os.path.basename(out)}", foreground="green")
            messagebox.showinfo("Успіх", "Файл зашифровано!")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def decrypt_file(self):
        if not hasattr(self, 'file_path') or not self.current_key: return
        try:
            out = crypto_mail.decrypt_file(self.file_path, self.current_key)
            self.lbl_status_file.config(text=f"Готово! Файл: {os.path.basename(out)}", foreground="blue")
            messagebox.showinfo("Успіх", "Файл розшифровано!")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SecureEmailApp(root)
    root.mainloop()