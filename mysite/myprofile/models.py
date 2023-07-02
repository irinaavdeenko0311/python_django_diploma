from django.db import models
from django.contrib.auth.models import User


def profile_avatar_directory_path(instance: "Profile", filename: str) -> str:
    return f"accounts/user_{instance.user.pk}/avatar/{filename}"


class Profile(models.Model):
    """
    Модель Profile: представляет профиль пользователя.

    Связана "один к одному" с :model:`auth.User`
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True, max_length=40)
    phone = models.DecimalField(null=True, blank=True, max_digits=11, decimal_places=0)
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to=profile_avatar_directory_path
    )
