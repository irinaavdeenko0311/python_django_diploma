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


def create_category(context):
    """
    Функция для заполнения БД категориями и подкатегориями товаров.

    Создание сущностей Category и Subcategory.
    Вынесено в отдельную функцию для использования и командой,
    и через административную панель.
    """

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

    for items in context:
        # создаем категорию и добавляем к ней изображение:
        category_obj = Category.objects.create(
            title=items['category']
        )
        category_image_index = get_image_index(items['category'], category_images_name)
        image_obj = category_images[category_image_index]
        category_obj.image = image_obj
        category_obj.save()

        # создаем подкатегории и добавляем к ним изображения:
        subcategories = items['subcategories']
        if isinstance(subcategories, str):
            subcategories = subcategories.split(',')

        for subcategory in subcategories:
            subcategory_obj = Subcategory.objects.create(
                title=subcategory,
                categories=category_obj,
            )
            subcategory_image_index = get_image_index(subcategory, subcategory_images_name)
            image_obj = subcategory_images[subcategory_image_index]
            subcategory_obj.image = image_obj
            subcategory_obj.save()


class Command(BaseCommand):
    """
    Команда для заполнения БД категориями и подкатегориями товаров.
    """

    def handle(self, *args, **options) -> None:
        context = [
            {
                "category": "Диваны и кресла",
                "subcategories": [
                    "Прямые диваны",
                    "Угловые диваны",
                    "Кресла на ножках",
                    "Другие кресла",
                ]
            },
            {
                "category": "Столы и стулья",
                "subcategories": [
                    "Кухонные столы",
                    "Журнальные столики",
                    "Стулья",
                ]
            },
            {
                "category": "Шкафы и стеллажи",
                "subcategories": [
                    "Распашные шкафы",
                    "Шкафы-купе",
                    "Стеллажи",
                ]
            },
            {
                "category": "Кровати",
                "subcategories": [
                    "Кровати с подъемным механизмом",
                    "Деревянные кровати",
                    "Кровати в мягкой обивке",
                ]
            },
            {
                "category": "Тумбы и комоды",
                "subcategories": [
                    "Прикроватные тумбы",
                    "Тумбы под телевизор",
                    "Комоды",
                ]
            },
        ]
        create_category(context)
