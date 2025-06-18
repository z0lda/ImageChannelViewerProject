import tkinter as tk


class ImageChannelViewerApp:
    def __init__(self, root):
        # Основное окно
        self.root = root
        self.root.title("Image Channel Viewer")
        icon_image = tk.PhotoImage(file="assets/img.png")
        self.root.iconphoto(False, icon_image)

        # Задание размеров окна
        self.root.geometry("800x600")  # Начальный размер
        self.root.minsize(600, 400)  # Минимальный размер

        # Переменные для изображений
        self.original_image = None
        self.modified_image = None

        # Часть интерфейса с изображением
        self.image_frame = tk.Frame(self.root, bg="black")
        self.image_frame.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Label(self.image_frame, bg="gray")
        self.canvas.pack(fill="both", expand=True)

        # Часть интерфейса с элементами управления
        self.buttons_frame = tk.Frame(self.root, padx=10, pady=10)
        self.buttons_frame.pack(side="left", fill="y")

        # Кнопки загрузки изображения
        # TODO: don't forget to add commands
        tk.Button(self.buttons_frame, text="Загрузить изображение").pack(fill="x", padx=10)
        tk.Button(self.buttons_frame, text="Снять изображение с веб-камеры").pack(fill="x", padx=10, pady=10)

        # Радиокнопки для переключения каналов изображения
        self.channel_var = tk.StringVar(value="original")
        tk.Label(self.buttons_frame, text="Режим отображения:").pack(pady=10)

        for text, mode in [("Оригинал", "original"), ("Красный", "red"), ("Зелёный", "green"), ("Синий", "blue")]:
            tk.Radiobutton(self.buttons_frame, text=text, variable=self.channel_var, value=mode).pack(anchor="w")

        # Дополнительные кнопки (согласно варианту задания)
        # TODO: don't forget to add commands
        tk.Button(self.buttons_frame, text="Негатив").pack(fill="x", padx=10)
        tk.Button(self.buttons_frame, text="Добавить границы").pack(fill="x", padx=10, pady=10)
        tk.Button(self.buttons_frame, text="Нарисовать линию").pack(fill="x", padx=10)

        # Сохранение результата
        # TODO: don't forget to add commands
        tk.Button(self.buttons_frame, text="Сохранить изображение").pack(fill="x", padx=10, pady=40)


def run_gui():
    root = tk.Tk()
    app = ImageChannelViewerApp(root)
    root.mainloop()
