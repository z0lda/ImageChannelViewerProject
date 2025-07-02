import tkinter as tk
import tkinter.messagebox
import os
import cv2

from image_processing import (apply_channel, load_image,
                              negative_effect, draw_line, add_border)
from utils import convert_cv_to_tk, get_file_path, get_file_path_for_save


class ImageChannelViewerApp:
    def __init__(self, root):
        # Основное окно
        self.root = root
        self.root.title("Image Channel Viewer")

        # Загрузка иконки
        try:
            icon_image = tk.PhotoImage(file="assets/img.png")
            self.root.iconphoto(False, icon_image)
        except tk.TclError:
            print("WARNING: Не удалось загрузить иконку приложения из assets/img.png")

        # Задание размеров окна
        self.root.geometry("1000x700")  # Начальный размер
        self.root.minsize(800, 600)  # Минимальный размер

        # Переменные для изображений
        self.original_image = None
        self.processed_image = None
        self.tk_image = None

        # Часть интерфейса с изображением
        self.image_frame = tk.Frame(self.root, bg="#2E2E2E")
        self.image_frame.pack(side="right", fill="both", expand=True)

        # "Холст"
        self.canvas = tk.Label(self.image_frame, bg="#2E2E2E")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

        # Часть интерфейса с элементами управления
        self.control_frame = tk.Frame(self.root, width=250, padx=10, pady=10)
        self.control_frame.pack(side="left", fill="y", expand=False)
        self.control_frame.pack_propagate(False)  # Отключение изменения размеров

        # Рамки

        # Рамка загрузки изображения
        self.load_frame = tk.LabelFrame(self.control_frame, text="Загрузка", padx=5, pady=5)
        self.load_frame.pack(fill="x", pady=(0, 10))

        self.load_image_button = tk.Button(self.load_frame, text="Загрузить c диска",
                                           command=self.load_image_from_file)
        self.load_image_button.pack(fill="x", pady=2)

        self.load_webcam_button = tk.Button(self.load_frame, text="Снимок с веб-камеры",
                                            command=self.capture_image_from_webcam)
        self.load_webcam_button.pack(fill="x", pady=2)

        # Рамка радиоканалов
        self.channel_frame = tk.LabelFrame(self.control_frame, text="Каналы", padx=5, pady=5)
        self.channel_frame.pack(fill="x", pady=(0, 10))

        # Радиокнопки для переключения каналов изображения
        self.channel_var = tk.StringVar(value="original")
        modes = [("Оригинал", "original"), ("Красный", "red"), ("Зелёный", "green"), ("Синий", "blue")]
        for text, mode in modes:
            (tk.Radiobutton(self.channel_frame, text=text, variable=self.channel_var, value=mode,
                            command=self.update_display).pack(anchor="w"))

        # Рамка обработчиков изображения
        self.processing_image_frame = tk.LabelFrame(self.control_frame, text="Обработка", padx=5, pady=5)
        self.processing_image_frame.pack(fill="x", pady=(0, 10))

        self.negative_button = tk.Button(self.processing_image_frame, text="Негатив", command=self.apply_negative)
        self.negative_button.pack(fill="x", pady=2)

        self.border_button = tk.Button(self.processing_image_frame, text="Добавить границы",
                                       command=self.open_border_dialog)
        self.border_button.pack(fill="x", pady=2)

        self.line_button = tk.Button(self.processing_image_frame, text="Нарисовать линию",
                                     command=self.open_line_dialog)
        self.line_button.pack(fill="x", pady=2)

        self.reset_button = tk.Button(self.processing_image_frame, text="Сбросить эффекты",
                                      command=self.reset_to_original)
        self.reset_button.pack(fill="x", pady=(10, 2))

        # Рамка сохранения результата
        self.save_img_frame = tk.LabelFrame(self.control_frame, text="Сохранение", padx=5, pady=5)
        self.save_img_frame.pack(fill="x", pady=(20, 0))

        self.save_img_button = tk.Button(self.save_img_frame, text="Сохранить результат", command=self.save_image)
        self.save_img_button.pack(fill="x", pady=2)

        # Динамическое изменение картинки под новый размер окна
        self.image_frame.bind("<Configure>", self.on_resize)

        # Обновление состояния кнопок
        self.update_button_states()

    def update_button_states(self):
        """Обновление состояния кнопок в зависимости от того, загружено ли изображении"""
        if self.original_image is not None:  # Проверка наличия изображения
            state = "normal"
        else:
            state = "disabled"

        # Список рамок, состояние которых надо обновить
        frames_to_update = [
            self.channel_frame,
            self.processing_image_frame,
            self.save_img_frame
        ]

        # Проход по каждому виджету и их обновление
        for frame in frames_to_update:
            for widget in frame.winfo_children():
                if isinstance(widget, (tk.Button, tk.Radiobutton, tk.Entry)):
                    widget.config(state=state)

    def on_resize(self, event=None):
        self.update_display()

    def update_display(self):
        """Отрисовка изображения с учётом выбранного радиоканала и размера окна"""
        if self.processed_image is None:  # Проверка, есть ли что "рисовать"
            self.canvas.config(image=None)
            self.canvas.image = None
            return

        # Применение фильтра канала
        channel = self.channel_var.get()
        img_with_channel = apply_channel(self.processed_image, channel)

        # Размеры холста
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 2 or canvas_h < 2:
            return

        # Размеры изображения
        h, w = img_with_channel.shape[:2]

        # Коэффициент масштабирования (чтобы изображение поместилось в область холста)
        img_scale = min(canvas_w / w, canvas_h / h)

        if img_scale > 1.0:
            img_scale = 1.0

        new_w = int(w * img_scale)
        new_h = int(h * img_scale)

        # "Перерисовываем" изображение
        resized = cv2.resize(img_with_channel, (new_w, new_h), interpolation=cv2.INTER_AREA)

        self.tk_image = convert_cv_to_tk(resized)  # Конвертация в PhotoImage для Tkinter
        self.canvas.config(image=self.tk_image)
        self.canvas.image = self.tk_image

    def load_image_from_file(self):
        """Загрузка файла из диска"""
        path = get_file_path()
        if not path:
            return

        self.original_image = load_image(path)
        self.reset_to_original()
        self.update_button_states()

    def reset_to_original(self):
        """Установка режима обычного просмотра (без фильтра каналов)
        при загрузке нового изображения"""
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.channel_var.set("original")
            self.update_display()

    def capture_image_from_webcam(self):
        """Получение изображения с вебкамеры"""
        capture = cv2.VideoCapture(0)  # захват видеокамеры
        if not capture:
            tkinter.messagebox.showwarning("Ошибка снимка",
                                           "Не удалось получить кадр с вебкамеры")

        is_successful, frame = capture.read()  # получаем статус и кадр
        capture.release()  # убираем захват видеокамеры

        if is_successful:
            self.original_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.reset_to_original()
        else:
            tkinter.messagebox.showwarning("Ошибка снимка",
                                           "Не удалось получить кадр с вебкамеры")
            self.original_image = None

        self.update_button_states()

    def apply_negative(self):
        """Применение негативного эффекта к изображению"""
        if self.processed_image is None: return
        self.processed_image = negative_effect(self.processed_image)
        self.update_display()

    def open_border_dialog(self):
        """Создание границ (через отдельное окно)"""
        if self.processed_image is None: return

        dialog = InputDialog(self.root, "Добавить рамку", {"Размер (px):": "10"})
        if dialog.result:
            try:
                size = int(dialog.result["Размер (px):"])
                if size <= 0: raise ValueError
                self.processed_image = add_border(self.processed_image, size)
                self.update_display()
            except (ValueError, TypeError):
                tk.messagebox.showerror("Ошибка ввода",
                                        "Размер рамки должен быть целым положительным числом.")

    def open_line_dialog(self):
        """Создание границ (через отдельное окно)"""
        if self.processed_image is None: return

        fields = {"X1:": "10", "Y1:": "10", "X2:": "100", "Y2:": "100", "Толщина:": "5"}
        dialog = InputDialog(self.root, "Нарисовать линию", fields)
        if dialog.result:
            try:
                cords = [int(v) for v in dialog.result.values()]
                if any(c < 0 for c in cords): raise ValueError
                x1, y1, x2, y2, thickness = cords
                self.processed_image = draw_line(self.processed_image,
                                                 (x1, y1),
                                                 (x2, y2), thickness)
                self.update_display()
            except (ValueError, TypeError):
                tk.messagebox.showerror("Ошибка ввода",
                                        "Координаты и толщина должны быть целыми неотрицательными числами.")

    def save_image(self):
        """Сохранение изображения"""
        if self.processed_image is None:
            tk.messagebox.showwarning("Нет изображения", "Сначала загрузите и обработайте изображение.")
            return

        path = get_file_path_for_save()
        if not path:
            return

        try:
            # Подготовка изображения к сохранению
            img_to_save = apply_channel(self.processed_image, self.channel_var.get())
            img_bgr = cv2.cvtColor(img_to_save, cv2.COLOR_RGB2BGR)

            # Получаем расширение файла для правильного кодирования
            extension = os.path.splitext(path)[1]

            # Кодируем изображение в буфер памяти
            result, buffer = cv2.imencode(extension, img_bgr)

            if not result:
                raise IOError("Не удалось закодировать изображение в формат {extension}")

            # Записываем буфер в файл стандартными средствами Python
            with open(path, 'wb') as f:
                f.write(buffer)

            tk.messagebox.showinfo("Успешно", f"Изображение сохранено по пути:\n{path}")

        except Exception as e:
            tk.messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл.\n\nДетали: {e}")


class InputDialog(tk.Toplevel):
    """Класс-шаблон для создания диалоговых окон"""

    def __init__(self, parent, title, fields):
        super().__init__(parent)  # Создание пустого окна
        self.transient(parent)  # "Привязка" его к родительскому
        self.title(title)
        self.parent = parent
        self.result = None
        self.entries = {}

        body = tk.Frame(self)  # Рамка окна
        self.initial_focus = self.create_widgets(body, fields)
        body.pack(padx=15, pady=15)

        self.create_buttons()
        self.grab_set()  # Захват всех событий (пользователь не может кликать по основному окну)

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)  # Обработка закрытия окна
        self.geometry(f"+{parent.winfo_rootx() + 50}+{parent.winfo_rooty() + 50}")
        self.initial_focus.focus_set()  # Установка курсора в первое окно
        self.wait_window(self)

    def create_widgets(self, master, fields):
        """Создание полей для ввода"""
        row = 0
        for label_text, default_value in fields.items():  # Проходимся по словарю

            # Создание текстовой метки и её размещение
            label = tk.Label(master, text=label_text)
            label.grid(row=row, column=0, sticky="w", padx=5, pady=5)

            # Создание поля для ввода и его размещение
            entry = tk.Entry(master)
            entry.grid(row=row, column=1, padx=5, pady=5)
            entry.insert(0, default_value)  # Значение по умолчанию
            self.entries[label_text] = entry
            row += 1
        return self.entries.get(list(fields.keys())[0]) if fields else None

    def create_buttons(self):
        """Создание кнопок"""
        box = tk.Frame(self)

        # Создание и размещение кнопки "ОК"
        ok_btn = tk.Button(box, text="OK", width=10, command=self.ok)
        ok_btn.pack(side="left", padx=5, pady=10)

        # Создание и размещение кнопки "Отмена"
        cancel_btn = tk.Button(box, text="Отмена", width=10, command=self.cancel)
        cancel_btn.pack(side="left", padx=5, pady=10)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def ok(self, event=None):
        self.result = {key: entry.get() for key, entry in self.entries.items()}
        self.parent.focus_set()
        self.destroy()

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()


def run_gui():
    root = tk.Tk()
    app = ImageChannelViewerApp(root)
    root.mainloop()
