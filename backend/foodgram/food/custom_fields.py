import base64

from django.core import validators
from django.core.files.base import ContentFile
from django.db import models
from rest_framework import serializers


class Hex2NameColor(models.CharField):
    """
    Пользовательское поле модели, представляющее цвет в формате HEX.
    Проверяет, что значение является корректным кодом цвета в формате HEX.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 7)
        super().__init__(*args, **kwargs)
        self.validators.append(
            validators.RegexValidator(
                regex=r"#([a-fA-F0-9]{6})",
                message=(
                    "Введите корректное значение кода цвета в формате HEX."
                ),
            )
        )


class Base64ImageField(serializers.Field):
    """
    Преобразует base64-строку в файловый объект при десериализации.
    Преобразует файловый объект в base64-строку при сериализации.
    """

    def to_internal_value(self, data):
        """
        Преобразует base64-строку в файловый объект.
        """
        try:
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
            return data
        except (ValueError, TypeError):
            raise serializers.ValidationError("Неверный формат изображения.")

    def to_representation(self, value):
        """
        Преобразует файловый объект в base64-строку.
        """
        if value:
            return base64.b64encode(value.read()).decode("utf-8")
        return None
