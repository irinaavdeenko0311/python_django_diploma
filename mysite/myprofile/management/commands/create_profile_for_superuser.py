from django.contrib.auth.models import User
from django.core.management import BaseCommand

from myprofile.models import Profile


class Command(BaseCommand):
    """Команда для создания сущности Profile для суперпользователя."""
    def handle(self, *args, **options) -> None:
        user = User.objects.get(username="Admin")
        fullname = user.first_name + user.last_name
        Profile.objects.create(user=user, fullName=fullname)
