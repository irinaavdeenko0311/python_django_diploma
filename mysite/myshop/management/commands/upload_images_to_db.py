import os

from django.core.management import BaseCommand

from mysite.settings import MEDIA_ROOT
from myshop.models import Image


class Command(BaseCommand):
    """
    Заполнение БД имеющимися изображениями.

    Команда для создания сущностей Image.
    """

    def handle(self, *args, **options) -> None:
        # путь до директории, в которой лежат изображения:
        directory_images = os.getenv("IMAGES_DIRECTORY", 'images')
        path_images = MEDIA_ROOT / directory_images

        for filename in os.listdir(path_images):
            Image.objects.create(
                src=f'{directory_images}/{filename}',
                alt=os.path.splitext(filename)[0],
            )
