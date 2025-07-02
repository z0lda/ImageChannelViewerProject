from PIL import Image, ImageTk
from tkinter import filedialog


def convert_cv_to_tk(img):
    """
    Преобразует изображение OpenCV (RGB) в изображение Tkinter.
    """
    pil_img = Image.fromarray(img)
    return ImageTk.PhotoImage(pil_img)


def get_file_path_for_save():
    """Открывает диалог выбора файла для СОХРАНЕНИЯ."""
    return filedialog.asksaveasfilename(
        title="Сохранить изображение как...",
        filetypes=[("PNG file", "*.png"), ("JPEG file", "*.jpg")],
        defaultextension="*.png"
    )


def get_file_path():
    """
    Открывает диалог выбора файла.
    """
    return filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
