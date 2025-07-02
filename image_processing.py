import cv2
import numpy as np


def load_image(path):
    """
    Загружает изображение и конвертирует его из BGR в RGB.
    """
    file_bytes = np.fromfile(path, dtype=np.uint8)
    bgr_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if bgr_image is None:
        raise ValueError(f"Не удалось загрузить изображение по пути: {path}")
    return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)


def apply_channel(img, channel):
    """
    Применяет выбранный канал (red, green, blue) к изображению.
    """
    if channel == "original":
        return img.copy()

    channel_map = {"red": 0, "green": 1, "blue": 2}
    idx = channel_map.get(channel)
    if idx is None:
        return img.copy()

    # Обнуляем все каналы, кроме одного
    output = np.zeros_like(img)
    output[:, :, idx] = img[:, :, idx]
    return output


def add_border(img, border_size, color=(128, 0, 128)):  # Пурпурный цвет по умолчанию
    """Добавляет цветную рамку к изображению."""
    return cv2.copyMakeBorder(
        img, border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT, value=color
    )


def negative_effect(img):
    """Применение негативного эффекта к изображению"""
    return cv2.bitwise_not(img)


def draw_line(img, start_point, end_point, thickness, color=(0, 255, 0)):  # Зеленый цвет
    """Рисует линию на изображении."""
    # Создаем копию, чтобы не изменять исходное изображение в `processed_image` напрямую
    img_with_line = img.copy()
    return cv2.line(img_with_line, start_point, end_point, color, thickness)
