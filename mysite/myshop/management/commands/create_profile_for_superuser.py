from django.contrib.auth.models import User
from django.core.management import BaseCommand

from myshop.models import Profile


class Command(BaseCommand):
    """Команда для создания сущности Profile для суперпользователя."""

    def handle(self, *args, **options) -> None:
        for user in User.objects.filter(is_superuser=True):
            Profile.objects.create(id=user)
