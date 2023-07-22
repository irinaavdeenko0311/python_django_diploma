from django.contrib.auth.models import User
from django.core.management import BaseCommand

from myshop.models import Profile


class Command(BaseCommand):
    """Команда для создания пользователя - сущности User и Profile."""

    def handle(self, *args, **options) -> None:
        context = {
            "name": "Иван",
            "username": "Ivan",
            "password": "Qwerty123"
        }
        user = User.objects.create_user(
            username=context.get('username'),
            password=context.get('password'),
        )

        Profile.objects.create(id=user, fullName=context.get('name'))
