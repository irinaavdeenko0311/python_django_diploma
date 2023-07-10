from django.core.management import BaseCommand

from myshop.models import Category, Subcategory, Image


def get_image_index(category_name, category_list):
    """
    Вспомогательная функция.

    В списке названий изображений находит нужное
    (в соответствии с названием категории товара).
    Возвращает индекс элемента в списке
    (для последующего получения объекта Image из queryset).
    """
    for i_image_name in range(len(category_list)):
        if ' '.join(category_name.split("-")).lower() in category_list[i_image_name]:
            return i_image_name


class Command(BaseCommand):
    """
    Заполнение БД категориями и подкатегориями товаров.

    Команда для создания сущностей Category и Subcategory.
    """

    def handle(self, *args, **options) -> None:
        context = {
            "Диваны и кресла": [
                "Прямые диваны",
                "Угловые диваны",
                "Кресла на ножках",
                "Другие кресла"
            ],
            "Столы и стулья": [
                "Кухонные столы",
                "Журнальные столики",
                "Стулья"
            ],
            "Шкафы и стеллажи": [
                "Распашные шкафы",
                "Шкафы-купе",
                "Стеллажи"
            ],
            "Кровати": [
                "Кровати с подъемным механизмом",
                "Деревянные кровати",
                "Кровати в мягкой обивке"
            ],
            "Тумбы и комоды": [
                "Прикроватные тумбы",
                "Тумбы под телевизор",
                "Комоды"
            ],
        }

        category_images = Image.objects.filter(src__icontains='Категория')
        category_images_name = [
            ' '.join(image.get_filename().split('_')).lower()
            for image in category_images
        ]

        subcategory_images = Image.objects.filter(src__icontains='Подкатегория')
        subcategory_images_name = [
            ' '.join(image.get_filename().split('_')).lower()
            for image in subcategory_images
        ]

        for category, subcategories in context.items():
            # создаем категорию и добавляем к ней изображение:
            category_obj = Category.objects.create(
                title=category
            )
            category_image_index = get_image_index(category, category_images_name)
            image_obj = category_images[category_image_index]
            category_obj.image = image_obj
            category_obj.save()

            # создаем подкатегории и добавляем к ним изображения:
            for subcategory in subcategories:
                subcategory_obj = Subcategory.objects.create(
                    title=subcategory,
                    categories=category_obj,
                )
                subcategory_image_index = get_image_index(subcategory, subcategory_images_name)
                image_obj = subcategory_images[subcategory_image_index]
                subcategory_obj.image = image_obj
                subcategory_obj.save()
