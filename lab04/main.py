import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import crypto_engine
import os


class DigitalSignatureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР4: ОЦП (Швидкой В.В.)")
        self.root.geometry("650x550")

        # Вкладки
        tab_control = ttk.Notebook(root)
        self.tab1 = ttk.Frame(tab_control)
        self.tab2 = ttk.Frame(tab_control)
        self.tab3 = ttk.Frame(tab_control)

        tab_control.add(self.tab1, text='1. Генерація ключів')
        tab_control.add(self.tab2, text='2. Підписати файл')
        tab_control.add(self.tab3, text='3. Перевірити підпис')
        tab_control.pack(expand=1, fill="both")

        self._setup_tab1()
        self._setup_tab2()
        self._setup_tab3()

        self.priv_key = None
        self.pub_key = None

    def _setup_tab1(self):
        frame = ttk.LabelFrame(self.tab1, text="Персональні дані", padding=20)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Label(frame, text="ПІБ:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = ttk.Entry(frame, width=40)
        self.entry_name.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Дата народження:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_dob = ttk.Entry(frame, width=40)
        self.entry_dob.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Секретне слово:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_secret = ttk.Entry(frame, width=40, show="*")
        self.entry_secret.grid(row=2, column=1, pady=5)

        ttk.Button(self.tab1, text="Згенерувати ключі", command=self.generate_keys).pack(pady=10)
        self.lbl_status_gen = ttk.Label(self.tab1, text="", foreground="green")
        self.lbl_status_gen.pack()

    def _setup_tab2(self):
        frame = ttk.LabelFrame(self.tab2, text="Підписання", padding=20)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Button(frame, text="Обрати файл", command=self.select_file_sign).pack(fill="x")
        self.lbl_file_sign = ttk.Label(frame, text="Файл не обрано")
        self.lbl_file_sign.pack(pady=5)

        ttk.Label(frame, text="Алгоритм хешування:").pack(pady=5)
        # Беремо ключі зі словника в engine
        algos = list(crypto_engine.HASH_ALGOS.keys())
        self.combo_hash = ttk.Combobox(frame, values=algos, state="readonly")
        self.combo_hash.current(0)
        self.combo_hash.pack()

        ttk.Button(frame, text="Підписати файл", command=self.sign_file).pack(pady=20, fill="x")

    def _setup_tab3(self):
        frame = ttk.LabelFrame(self.tab3, text="Верифікація", padding=20)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Button(frame, text="1. Обрати файл (документ)", command=self.select_file_verify).pack(fill="x")
        self.lbl_file_verify = ttk.Label(frame, text="Файл не обрано", foreground="gray")
        self.lbl_file_verify.pack(pady=5)

        ttk.Button(frame, text="2. Обрати файл підпису (.sig)", command=self.select_sig_verify).pack(fill="x", pady=5)
        self.lbl_sig_verify = ttk.Label(frame, text="Підпис не обрано", foreground="gray")
        self.lbl_sig_verify.pack(pady=5)

        ttk.Button(frame, text="Перевірити", command=self.verify_file).pack(pady=20, fill="x")
        self.lbl_result = ttk.Label(self.tab3, text="Очікування...", font=("Arial", 14, "bold"))
        self.lbl_result.pack()

    # --- Обробники подій ---

    def generate_keys(self):
        name = self.entry_name.get()
        dob = self.entry_dob.get()
        secret = self.entry_secret.get()

        if not (name and dob and secret):
            messagebox.showerror("Помилка", "Заповніть усі поля!")
            return

        try:
            self.lbl_status_gen.config(text="Генерація простих чисел... Зачекайте...", foreground="blue")
            self.root.update()  # Оновити інтерфейс

            pub, priv = crypto_engine.generate_keys_from_data(name, dob, secret)
            self.pub_key = pub
            self.priv_key = priv

            with open("public.pem", "wb") as f:
                f.write(pub)
            with open("private.pem", "wb") as f:
                f.write(priv)

            self.lbl_status_gen.config(text="Ключі успішно згенеровано (RSA)!", foreground="green")
            messagebox.showinfo("Успіх", "Власна пара ключів RSA створена!")
        except Exception as e:
            self.lbl_status_gen.config(text="Помилка", foreground="red")
            messagebox.showerror("Помилка", str(e))

    def select_file_sign(self):
        self.path_sign = filedialog.askopenfilename()
        if self.path_sign: self.lbl_file_sign.config(text=os.path.basename(self.path_sign))

    def sign_file(self):
        if not hasattr(self, 'path_sign') or not self.priv_key:
            messagebox.showwarning("Увага", "Оберіть файл та згенеруйте ключі.")
            return

        try:
            sig_path = crypto_engine.sign_file(self.path_sign, self.priv_key, self.combo_hash.get())
            messagebox.showinfo("Успіх", f"Файл підписано!\nПідпис: {os.path.basename(sig_path)}")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def select_file_verify(self):
        self.path_ver_file = filedialog.askopenfilename()
        if self.path_ver_file: self.lbl_file_verify.config(text=os.path.basename(self.path_ver_file))

    def select_sig_verify(self):
        self.path_ver_sig = filedialog.askopenfilename(filetypes=[("Signature", "*.sig")])
        if self.path_ver_sig: self.lbl_sig_verify.config(text=os.path.basename(self.path_ver_sig))

    def verify_file(self):
        if not hasattr(self, 'path_ver_file') or not hasattr(self, 'path_ver_sig') or not self.pub_key:
            messagebox.showwarning("Увага", "Оберіть файл, підпис та згенеруйте ключі.")
            return

        valid = crypto_engine.verify_signature(self.path_ver_file, self.path_ver_sig, self.pub_key)

        if valid:
            self.lbl_result.config(text="✅ ПІДПИС ДІЙСНИЙ", foreground="green")
        else:
            self.lbl_result.config(text="❌ ПІДПИС НЕДІЙСНИЙ", foreground="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalSignatureApp(root)
    root.mainloop()