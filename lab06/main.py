import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import db_manager
import vulnerabilities


class SQLInjectionDemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ЛР6: Етичний хакінг (Швидкой В.В.)")
        self.root.geometry("950x550")

        # Створюємо базу при запуску
        db_manager.init_db()

        # Стиль для таблиць
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", rowheight=25)

        # Робимо 3 вкладки
        tab_control = ttk.Notebook(root)
        self.tab_search = ttk.Frame(tab_control)
        self.tab_login = ttk.Frame(tab_control)
        self.tab_logs = ttk.Frame(tab_control)

        tab_control.add(self.tab_search, text='1. Пошук (Витік даних)')
        tab_control.add(self.tab_login, text='2. Логін (Злам входу)')
        tab_control.add(self.tab_logs, text='3. Логи (IDS)')
        tab_control.pack(expand=1, fill="both")

        self._init_search_tab()
        self._init_login_tab()
        self._init_logs_tab()

    def log_action(self, module, query, mode, status):
        # Пишемо все в таблицю логів з часом
        timestamp = datetime.now().strftime("%H:%M:%S")
        tag = "normal"

        # Підсвічуємо кольорами
        if status == "ATTACK DETECTED":
            tag = "attack"
        elif status == "BLOCKED BY WAF":
            tag = "waf"
        elif "ERROR" in status:
            tag = "error"
        elif status == "SUCCESS":
            tag = "success"

        self.tree_logs.insert("", 0, values=(timestamp, module, mode, query, status), tags=(tag,))

    def _init_search_tab(self):
        # === Вразлива частина ===
        frame_vuln = tk.LabelFrame(self.tab_search, text="🔴 Вразливий пошук", padx=10, pady=10, fg="red")
        frame_vuln.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_vuln, text="Введіть ім'я:").pack(anchor="w")
        self.entry_vuln_search = tk.Entry(frame_vuln, width=50, font=("Consolas", 10))
        self.entry_vuln_search.pack(fill="x", pady=5)

        tk.Button(frame_vuln, text="🔍 Знайти (Вразливо)", command=self.run_search_vuln, bg="#ffcccc").pack(fill="x", pady=5)

        # Таблиця результатів
        cols = ("ID", "ПІБ", "Факультет", "Стипендія", "Секрет")
        self.tree_vuln = ttk.Treeview(frame_vuln, columns=cols, show="headings", height=4)
        for c in cols: self.tree_vuln.heading(c, text=c); self.tree_vuln.column(c, width=100)
        self.tree_vuln.pack(fill="x")

        # === Захищена частина ===
        frame_sec = tk.LabelFrame(self.tab_search, text="🟢 Захищений пошук (Secure + WAF)", padx=10, pady=10, fg="green")
        frame_sec.pack(fill="x", padx=10, pady=5)

        self.entry_sec_search = tk.Entry(frame_sec, width=50, font=("Consolas", 10))
        self.entry_sec_search.pack(fill="x", pady=5)
        tk.Button(frame_sec, text="🔒 Знайти (Безпечно)", command=self.run_search_secure, bg="#ccffcc").pack(fill="x", pady=5)

        self.tree_sec = ttk.Treeview(frame_sec, columns=cols, show="headings", height=4)
        for c in cols: self.tree_sec.heading(c, text=c); self.tree_sec.column(c, width=100)
        self.tree_sec.pack(fill="x")

    def _init_login_tab(self):
        frame = tk.Frame(self.tab_login, padx=20, pady=20)
        frame.pack()
        tk.Label(frame, text="Панель адміністратора", font=("Arial", 16, "bold")).pack(pady=20)

        frame_form = tk.LabelFrame(frame, text="Авторизація", padx=20, pady=20)
        frame_form.pack()

        tk.Label(frame_form, text="Логін:").grid(row=0, column=0, sticky="e")
        self.entry_login = tk.Entry(frame_form, width=30, font=("Consolas", 10))
        self.entry_login.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(frame_form, text="Пароль:").grid(row=1, column=0, sticky="e")
        self.entry_pass = tk.Entry(frame_form, width=30, font=("Consolas", 10))
        self.entry_pass.grid(row=1, column=1, pady=5, padx=5)

        tk.Button(frame_form, text="🔓 Вхід (Вразливо)", command=self.run_login_vuln, bg="#ffcccc", width=20).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(frame_form, text="🔒 Вхід (Безпечно)", command=self.run_login_secure, bg="#ccffcc", width=20).grid(row=3, column=0, columnspan=2, pady=5)

        self.lbl_login_status = tk.Label(frame, text="Статус: Очікування...", font=("Arial", 12))
        self.lbl_login_status.pack(pady=20)

    def _init_logs_tab(self):
        frame = tk.Frame(self.tab_logs, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        # Таблиця логів
        cols = ("Час", "Модуль", "Режим", "Запит", "Статус")
        self.tree_logs = ttk.Treeview(frame, columns=cols, show="headings")
        self.tree_logs.heading("Час", text="Час");
        self.tree_logs.column("Час", width=80)
        self.tree_logs.heading("Модуль", text="Модуль");
        self.tree_logs.column("Модуль", width=80)
        self.tree_logs.heading("Режим", text="Режим");
        self.tree_logs.column("Режим", width=80)
        self.tree_logs.heading("Запит", text="Деталі (SQL / Ввід)");
        self.tree_logs.column("Запит", width=450)
        self.tree_logs.heading("Статус", text="Статус")

        # Кольори рядків
        self.tree_logs.tag_configure("attack", background="#ffdddd", foreground="red")
        self.tree_logs.tag_configure("success", background="#ddffdd", foreground="green")
        self.tree_logs.tag_configure("waf", background="#ffffcc", foreground="orange")

        self.tree_logs.pack(fill="both", expand=True)

    # --- ОБРОБКА КНОПОК ---

    def run_search_vuln(self):
        inp = self.entry_vuln_search.get()
        # Викликаємо "діряву" функцію
        results, query, error = vulnerabilities.search_vulnerable(inp)

        if error:
            self.log_action("SEARCH", error, "UNSAFE", "SQL ERROR")
            messagebox.showerror("SQL Error", error)
            return

        # Чистимо таблицю і показуємо результат
        for i in self.tree_vuln.get_children(): self.tree_vuln.delete(i)
        for row in results: self.tree_vuln.insert("", "end", values=row)

        # Перевіряємо, чи це була атака (для логів)
        status = "OK"
        if len(results) > 1 or "' OR" in query.upper():
            status = "ATTACK DETECTED"
            messagebox.showwarning("Увага!", f"Витік даних! Показано {len(results)} записів.")

        self.log_action("SEARCH", query, "UNSAFE", status)

    def run_search_secure(self):
        inp = self.entry_sec_search.get()

        # 1. Спочатку перевіряємо через WAF
        is_safe, bad_word = vulnerabilities.waf_check(inp)
        if not is_safe:
            self.log_action("SEARCH", f"Ввід: {inp}", "WAF", "BLOCKED BY WAF")
            messagebox.showerror("WAF Alert", f"Запит заблоковано! Знайдено: {bad_word}")
            return

        # 2. Якщо чисто, то робимо безпечний пошук
        results, query, error = vulnerabilities.search_secure(inp)

        if error: messagebox.showerror("Error", error); return

        for i in self.tree_sec.get_children(): self.tree_sec.delete(i)
        for row in results: self.tree_sec.insert("", "end", values=row)

        self.log_action("SEARCH", query, "SECURE", "OK")
        if not results: messagebox.showinfo("Інфо", "Записів не знайдено.")

    def run_login_vuln(self):
        u, p = self.entry_login.get(), self.entry_pass.get()
        user, query, error = vulnerabilities.login_vulnerable(u, p)

        if error:
            self.log_action("LOGIN", error, "UNSAFE", "SQL ERROR")
            self.lbl_login_status.config(text="SQL Error", fg="red")
            return

        if user:
            self.lbl_login_status.config(text=f"Вхід дозволено: {user[1]} ({user[3]})", fg="green")
            status = "ATTACK DETECTED" if "' --" in query else "SUCCESS"

            if status == "ATTACK DETECTED":
                messagebox.showwarning("Злам!", f"Ви увійшли як {user[1]} без пароля!")

            self.log_action("LOGIN", query, "UNSAFE", status)
        else:
            self.lbl_login_status.config(text="Відмова", fg="red")
            self.log_action("LOGIN", query, "UNSAFE", "FAIL")

    def run_login_secure(self):
        u, p = self.entry_login.get(), self.entry_pass.get()

        # 1. WAF
        is_safe, bad_word = vulnerabilities.waf_check(u)
        if not is_safe:
            self.log_action("LOGIN", f"Ввід: {u}", "WAF", "BLOCKED BY WAF")
            messagebox.showerror("WAF Alert", "Запит заблоковано Firewall!")
            return

        # 2. Безпечний логін
        user, query, error = vulnerabilities.login_secure(u, p)

        if error: messagebox.showerror("Error", error); return

        if user:
            self.lbl_login_status.config(text=f"Вхід: {user[1]}", fg="green")
            self.log_action("LOGIN", query, "SECURE", "SUCCESS")
        else:
            self.lbl_login_status.config(text="Відмова", fg="red")
            self.log_action("LOGIN", query, "SECURE", "BLOCKED")
            messagebox.showinfo("Захист", "Атака не вдалася.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SQLInjectionDemoApp(root)
    root.mainloop()