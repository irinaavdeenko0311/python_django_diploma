from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Profile."""
    class Meta:
        model = Profile
        exclude = "id", "user"
