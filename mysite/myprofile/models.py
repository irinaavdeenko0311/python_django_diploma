from django.db import models
from django.contrib.auth.models import User


def image_directory_path(instance: "Image", filename: str) -> str:
    return f"images/{filename}"


class Image(models.Model):
    """Модель, представляющая изображение."""

    src = models.ImageField(
        null=True,
        blank=True,
        upload_to=image_directory_path
    )
    alt = models.CharField(
        null=True,
        blank=True,
        max_length=40
    )


class Profile(models.Model):
    """Модель Profile: представляет профиль пользователя."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True, max_length=40)
    phone = models.PositiveIntegerField(null=True, blank=True)
    avatar = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, blank=True)
