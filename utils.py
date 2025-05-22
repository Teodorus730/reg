import os
from PIL import Image
from io import BytesIO

def validate_image(file_storage):
    if not file_storage:
        return "Обложка обязательна"

    if file_storage.content_type not in ["image/jpeg", "image/jpg"]:
        return "Обложка должна быть в формате JPEG"

    if len(file_storage.read()) > 10 * 1024 * 1024:
        return "Размер обложки не должен превышать 10 МБ"

    file_storage.stream.seek(0)
    try:
        image = Image.open(file_storage.stream)
    except Exception:
        return "Ошибка при открытии изображения"

    width, height = image.size
    if width != height:
        return "Обложка должна быть квадратной"

    if not (3000 <= width <= 3500):
        return "Размер обложки должен быть от 3000x3000 до 3500x3500 пикселей"

    if image.mode != "RGB":
        return "Цветовой режим обложки должен быть RGB"

    file_storage.stream.seek(0)
    return None

def validate_audio(file_storage):
    if file_storage:
        if file_storage.content_type not in ["audio/wav", "audio/x-wav"]:
            return "Аудиофайл должен быть в формате WAV"
        if len(file_storage.read()) > 500 * 1024 * 1024:
            return "Размер аудиофайла не должен превышать 500 МБ"
        file_storage.stream.seek(0)
    return None

def validate_pdf(file_storage):
    if file_storage:
        if file_storage.content_type != "application/pdf":
            return "Файл должен быть в формате PDF"
        if len(file_storage.read()) > 100 * 1024 * 1024:
            return "Размер PDF не должен превышать 100 МБ"
        file_storage.stream.seek(0)
    return None


def delete_file(filepath):
    if os.path.isfile(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            return False
    else:
        return False
