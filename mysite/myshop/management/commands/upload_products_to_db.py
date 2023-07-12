from django.core.management import BaseCommand

from myshop.models import (
    Subcategory,
    Image,
    Product,
    Tag,
    Specification
)


def get_image_index(name, list):
    """
    Вспомогательная функция.

    В списке названий изображений находит нужное
    (в соответствии с названием товара).
    Возвращает индекс элемента в списке
    (для последующего получения объекта Image из queryset).
    """
    for i_image_name in range(len(list)):
        if ' '.join(name.split("-")).lower() in list[i_image_name]:
            return i_image_name


def create_product(context):
    """
    Функция для заполнения БД товарами.

    Создание сущностей Product.
    Вынесено в отдельную функцию для использования и командой,
    и через административную панель.
    """
    categories_queryset = Subcategory.objects.all()
    images_queryset = Image.objects.all()
    images_name = [
        ' '.join(image.get_filename().split('_')).lower()
        for image in images_queryset
    ]
    tags_queryset = Tag.objects.all()
    specifications_queryset = Specification.objects.all()

    for product in context:
        category = categories_queryset.get(title=product['category'])
        image_index = get_image_index(product['title'], images_name)
        image_obj = images_queryset[image_index]

        product_obj = Product.objects.create(
            category=category,
            price=product['price'],
            count=product['count'],
            title=product['title'],
            description=product['description'],
            fullDescription=product['fullDescription'],
            freeDelivery=product['freeDelivery'],
            rating=product['rating'],
        )

        product_obj.images.add(image_obj)

        # теги и характеристики разных товаров могут повторяться
        # поэтому либо добавляем товару имеющиеся в БД тег/характеристику
        # либо создаем новые тег/характеристику и добавляем к товару:

        tags = product['tags']
        if isinstance(tags, str):
            tags = tags.split(',')

        for tag in tags:
            if tags_queryset.filter(name=tag).exists():
                tag_obj = tags_queryset.filter(name=tag)[0]
            else:
                tag_obj = Tag.objects.create(name=tag)

            product_obj.tags.add(tag_obj)

        specifications = product['specifications']
        if isinstance(specifications, str):
            specifications = {
                specification.split('-')[0]: specification.split('-')[1]
                for specification in specifications.split(',')
            }

        for name, value in specifications.items():
            if specifications_queryset.filter(name=name, value=value).exists():
                specification_obj = specifications_queryset.filter(
                    name=name,
                    value=value,
                )[0]

            else:
                specification_obj = Specification.objects.create(
                    name=name,
                    value=value,
                )
            product_obj.specifications.add(specification_obj)

        product_obj.save()


class Command(BaseCommand):
    """
    Команда для заполнения БД товарами.
    """

    def handle(self, *args, **options) -> None:
        context = [
            {
                "category": "Прямые диваны",
                "price": 1000,
                "count": 10,
                "title": "Диван Avanti",
                "description": "Компактный и стильный, будет радовать детей и взрослых.",
                "fullDescription": "Его легко собирать, раскладывать и ухаживать за обивкой. "
                                   "Идеальный диван для современных людей, которые стремятся "
                                   "подчеркнуть свою индивидуальность и позитивное отношение к жизни.",
                "freeDelivery": True,
                "tags": ["гостиная", "голубой"],
                "specifications": {
                    "цвет": "голубой",
                    "материал обивки": "микрофибра",
                    "материал каркаса": "дерево",
                    "ширина": 90,
                    "длина": 230,
                    "высота": 100
                },
                "rating": 4.6
            },
            {
                "category": "Шкафы-купе",
                "price": 2000,
                "count": 3,
                "title": "Шкаф Fog",
                "description": "Настоящая находка для ценителей качественной и функциональной мебели.",
                "fullDescription": "Представленная модель выполнена из экологически чистого ЛДСП. "
                                   "При изготовлении применяется современная фурнитура, рассчитанная "
                                   "на длительную и активную эксплуатацию..",
                "freeDelivery": False,
                "tags": ["спальня", "гардеробная"],
                "specifications": {
                    "цвет": "орех",
                    "материал": "ЛДСП",
                    "ширина": 60,
                    "длина": 300,
                    "высота": 250
                },
                "rating": 4.5
            },
        ]
        create_product(context)
