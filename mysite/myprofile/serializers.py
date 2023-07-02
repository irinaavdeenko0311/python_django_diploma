from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Image, Profile


class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Image"""
    class Meta:
        model = Image
        fields = 'src', 'alt'


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Profile."""

    avatar = ImageSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'fullName',
            'email',
            'phone',
            'avatar',
        )


class UserPasswordSerializer(serializers.Serializer):
    """Сериализатор для преобразования пароля из модели User"""

    currentPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)


