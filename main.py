import tkinter as tk
from tkinter import messagebox, ttk
import random
import string
import json
import os

# --- Настройки ---
HISTORY_FILE = "history.json"  # Файл для хранения истории сгенерированных паролей
MIN_LENGTH = 4                 # Минимальная длина пароля
MAX_LENGTH = 32                # Максимальная длина пароля

# --- Логика генерации пароля ---
def generate_password(length, use_digits, use_letters, use_special):
    """
    Генерирует пароль на основе выбранных параметров.
    Объединяет выбранные наборы символов и выбирает из них случайные.
    """
    if length < 1:
        raise ValueError("Длина пароля должна быть больше 0.")

    chars = ''
    if use_digits:
        chars += string.digits          # '0123456789'
    if use_letters:
        chars += string.ascii_letters   # 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if use_special:
        chars += string.punctuation     # Спецсимволы: !"#$%&'()*+,-./:;<=>?@[$$^_`{|}~

    if not chars:
        raise ValueError("Необходимо выбрать хотя бы один тип символов.")

    return ''.join(random.choices(chars, k=length))

# --- Работа с историей (JSON) ---
def load_history():
    """
    Загружает список паролей из файла history.json.
    Если файла нет, возвращает пустой список.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    """
    Сохраняет список паролей в файл history.json.
    ensure_ascii=False позволяет сохранять кириллицу, если она вдруг появится.
    """
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# --- Основная логика приложения ---
def on_generate():
    """
    Обработчик нажатия кнопки "Сгенерировать".
    Здесь происходит валидация, генерация и обновление интерфейса.
    """
    try:
        length = int(scale_length.get()) # Получаем длину слайдера

        # Проверка длины (валидация)
        if length < MIN_LENGTH or length > MAX_LENGTH:
            messagebox.showwarning(
                "Недопустимая длина",
                f"Длина пароля должна быть от {MIN_LENGTH} до {MAX_LENGTH} символов."
            )
            return

        # Получаем значения флажков (True/False)
        use_digits = var_digits.get()
        use_letters = var_letters.get()
        use_special = var_special.get()

        # Генерация пароля (основная логика)
        password = generate_password(length, use_digits, use_letters, use_special)

        # Вывод в интерфейс (очищаем поле и вставляем новый пароль)
        entry_password.delete(0, tk.END)
        entry_password.insert(0, password)

        # Сохранение в историю и обновление таблицы
        history = load_history()
        history.append(password)
        save_history(history)
        update_history_table()

    except ValueError as e:
        messagebox.showerror("Ошибка ввода", str(e))
    except Exception as e:
        messagebox.showerror("Критическая ошибка", "Произошла непредвиденная ошибка.")

def update_history_table():
    """
    Очищает таблицу и заново заполняет её данными из файла истории.
    """
    for item in tree.get_children():
        tree.delete(item)
    for pwd in load_history():
        tree.insert('', 'end', values=(pwd,))

# --- Создание графического интерфейса ---
root = tk.Tk()
root.title("Генератор случайных паролей")
root.geometry("500x450")
root.resizable(False, False) # Запрещаем изменение размера окна
root.configure(bg='#f0f0f0')

# Фрейм настроек (Длина и флажки)
frame_settings = tk.Frame(root, bg='#f0f0f0', padx=10, pady=10)
frame_settings.pack(pady=10)

tk.Label(frame_settings, text="Длина пароля:", bg='#f0f0f0').grid(row=0, column=0)
scale_length = tk.Scale(frame_settings, from_=MIN_LENGTH, to=MAX_LENGTH,
                        orient=tk.HORIZONTAL, length=250)
scale_length.set(12)  # Значение по умолчанию при запуске
scale_length.grid(row=0, column=1, columnspan=2)

# Переменные для хранения состояния флажков (True/False)
var_digits = tk.BooleanVar(value=True)
var_letters = tk.BooleanVar(value=True)
var_special = tk.BooleanVar(value=True)

tk.Checkbutton(frame_settings, text="Цифры", variable=var_digits,
               bg='#f0f0f0').grid(row=1, column=0)
tk.Checkbutton(frame_settings, text="Буквы", variable=var_letters,
               bg='#f0f0f0').grid(row=1, column=1)
tk.Checkbutton(frame_settings, text="Спецсимволы", variable=var_special,
               bg='#f0f0f0').grid(row=1, column=2)

btn_generate = tk.Button(root, text="Сгенерировать", command=on_generate,
                         bg='#4CAF50', fg='white')
btn_generate.pack(pady=5)

# Фрейм вывода пароля и кнопки копирования
frame_output = tk.Frame(root, bg='#f0f0f0')
frame_output.pack(pady=10)

tk.Label(frame_output, text="Ваш пароль:", bg='#f0f0f0').pack(side=tk.LEFT)
entry_password = tk.Entry(frame_output, width=40, font=('Arial', 12))
entry_password.pack(side=tk.LEFT, padx=5)
btn_copy = tk.Button(frame_output, text="Копировать",
                     command=lambda: root.clipboard_clear() or root.clipboard_append(entry_password.get()))
btn_copy.pack(side=tk.LEFT)

# Таблица истории (Treeview) с полосой прокрутки
frame_history = tk.Frame(root)
frame_history.pack(fill='both', expand=True, padx=20, pady=10)

tree = ttk.Treeview(frame_history, columns=('password',), show='headings')
tree.heading('password', text='История паролей')
tree.column('password', width=450) # Ширина колонки под пароль

tree.pack(fill='both', expand=True) # Позволяет таблице занимать всё доступное место

scrollbar = ttk.Scrollbar(frame_history, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set) # Связываем скролл с таблицей
scrollbar.pack(side="right", fill="y")

# Загрузка истории при запуске приложения (отображаем старые пароли сразу)
update_history_table()

# Запуск главного цикла обработки событий (ожидание действий пользователя)
root.mainloop()