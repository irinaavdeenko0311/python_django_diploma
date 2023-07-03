from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)


# ОБЩИЕ МОДЕЛИ:

def image_directory_path(instance: "Image", filename: str) -> str:
    """Функция для формирования пути, по которому сохраняется изображение."""
    return f"images/{filename}"


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


# МОДЕЛЬ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ:

class Profile(models.Model):
    """Модель Profile: представляет профиль пользователя."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True, max_length=40)
    phone = models.PositiveIntegerField(null=True, blank=True)
    avatar = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Profile {self.user!r}'


# МОДЕЛИ ДЛЯ ОПИСАНИЯ КАТЕГОРИЙ ТОВАРОВ:

class CategoryBase(models.Model):
    """Абстрактная модель, представляющая категорию товара."""

    class Meta:
        abstract = True

    title = models.CharField(max_length=20)
    image = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, blank=True)


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


# МОДЕЛИ ДЛЯ ОПИСАНИЯ ПАРАМЕТРОВ ТОВАРА:

class Tag(models.Model):
    """Модель, представляющая тег товара."""

    name = models.CharField(max_length=20)

    def __str__(self):
        return f'#{self.name}'


class Specification(models.Model):
    """Модель, представляющая технические характеристики товара."""

    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name}:{self.value}'


class Product(models.Model):
    """Модель, представляющая продукт."""

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=8,
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
    specifications = models.ManyToManyField(Specification, related_name="product_specification")
    rating = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(5)]
    )

    def __str__(self):
        return f'{self.title}'


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
