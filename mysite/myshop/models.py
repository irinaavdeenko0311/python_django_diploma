import os

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)


# ОБЩИЕ МОДЕЛИ:

def image_directory_path(instance: "Image", filename: str) -> str:
    """Функция для формирования пути, по которому сохраняется изображение."""
    return f'{os.getenv("IMAGES_DIRECTORY", "images")}/{filename}'


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

    def __str__(self):
        return f'{self.src}'

    def get_filename(self):
        return os.path.splitext(os.path.basename(self.src.name))[0]


# МОДЕЛИ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ:

class Profile(models.Model):
    """Модель, представляющая профиль пользователя."""

    id = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True, max_length=40)
    phone = models.PositiveIntegerField(null=True, blank=True)
    avatar = models.OneToOneField(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    def __str__(self):
        return f'Профиль #{self.id} {self.user!r}'


# МОДЕЛИ ДЛЯ ОПИСАНИЯ КАТЕГОРИЙ ТОВАРОВ:

class CategoryBase(models.Model):
    """Абстрактная модель, представляющая категорию товара."""

    class Meta:
        abstract = True

    title = models.CharField(max_length=20)
    image = models.OneToOneField(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)


class Category(CategoryBase):
    """Модель, представляющая категорию товара."""

    def __str__(self):
        return f'Категория {self.title!r}'


class Subcategory(CategoryBase):
    """Модель, представляющая подкатегорию товара."""

    categories = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
    )

    def __str__(self):
        return f'Подкатегория {self.title!r}'


# МОДЕЛИ ДЛЯ ОПИСАНИЯ ТОВАРА И ЕГО ПАРАМЕТРОВ:

class Tag(models.Model):
    """Модель, представляющая тег товара."""

    name = models.CharField(max_length=20)

    def __str__(self):
        return f'Тег {self.name!r}'


class Specification(models.Model):
    """Модель, представляющая технические характеристики товара."""

    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name}: {self.value}'


class Product(models.Model):
    """Модель, представляющая товар."""

    category = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    count = models.PositiveSmallIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=30)
    fullDescription = models.TextField(null=True, blank=True)
    freeDelivery = models.BooleanField(default=True)
    images = models.ManyToManyField(Image, related_name="product_image")
    tags = models.ManyToManyField(Tag, related_name="product_tag")
    specifications = models.ManyToManyField(
        Specification,
        related_name="product_specification")
    rating = models.DecimalField(
        decimal_places=1,
        max_digits=3,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    def __str__(self):
        return f'Товар #{self.id} {self.title}'


class Review(models.Model):
    """Модель, представляющая отзыв о товаре."""

    author = models.CharField(max_length=30)
    email = models.EmailField(max_length=50)
    text = models.TextField(null=True, blank=True)
    rate = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5)]
    )
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
    )

    def __str__(self):
        return f'Отзыв #{self.id}, товар {self.product!r}'


class ProductSale(models.Model):
    """Модель, представляющая товар, участвующий в распродаже."""

    id = models.OneToOneField(
        Product,
        primary_key=True,
        on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=15,
        decimal_places=1,
        validators=[MinValueValidator(0.01)]
    )
    salePrice = models.DecimalField(
        max_digits=15,
        decimal_places=1,
        validators=[MinValueValidator(0.01)]
    )
    dateFrom = models.DateTimeField()
    dateTo = models.DateTimeField()
    title = models.CharField(max_length=20)
    images = models.ManyToManyField(
        Image,
        related_name="product_sale_image",
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs) -> None:
        # При создании товара, участвующего в распродаже,
        # данные берутся из модели Product: цена, название и изображения.
        # В модели Product цена меняется на новую сниженную.
        product = (
            Product.objects
            .prefetch_related('images')
            .get(id=self.id.id)
        )

        self.price = product.price
        self.title = product.title

        new_price = self.salePrice
        product.price = new_price
        product.save()

        super(ProductSale, self).save(*args, **kwargs)

        images = product.images.all()
        self.images.set(images)

    def __str__(self):
        return f'SALE Товар #{self.id} {self.title}'


# МОДЕЛИ ДЛЯ ОПИСАНИЯ ЗАКАЗОВ:

class OrderProduct(models.Model):
    """Модель, представляющая товар в заказе."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    count = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f'Товар {self.product!r} - заказ #{self.id}'


class Order(models.Model):
    """Модель, представляющая заказ."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    fullName = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True, max_length=40)
    phone = models.PositiveIntegerField(null=True, blank=True)
    deliveryType = models.CharField(max_length=20, default='ordinary')
    paymentType = models.CharField(max_length=20, default='online')
    totalCost = models.DecimalField(
        max_digits=15,
        decimal_places=1,
        validators=[MinValueValidator(0.01)]
    )
    status = models.CharField(max_length=20, default='created')
    city = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=40, null=True, blank=True)
    products = models.ManyToManyField(
        OrderProduct,
        related_name="order_products"
    )

    def __str__(self):
        return f'Заказ #{self.id} - пользователь {self.user!r}'
