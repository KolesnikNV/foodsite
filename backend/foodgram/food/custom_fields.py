import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.Field):
    def to_internal_value(self, data):
        try:
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
            return data
        except (ValueError, TypeError):
            raise serializers.ValidationError("Неверный формат изображения.")

    def to_representation(self, value):
        if value:
            return base64.b64encode(value.read()).decode("utf-8")
        return None


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("Для этого цвета нет имени")
        return data
