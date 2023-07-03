from django.contrib import admin

from .models import (
    Image,
    Profile,
    Category,
    Subcategory,
    Tag,
    Specification,
    Product,
    Review,
)


# ОБЩИЕ МОДЕЛИ:

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    """Модель, представляющая изображение."""

    list_display = 'id', 'src', 'alt'


# МОДЕЛЬ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ:

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Модель предстваляющая профиль пользователя."""

    list_display = [
        field.name for field in Profile._meta.get_fields()
    ]
    list_display_links = 'id', 'user'


# МОДЕЛИ ДЛЯ ОПИСАНИЯ КАТЕГОРИЙ ТОВАРОВ:

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Модель, представляющая подкатегорию товара."""

    list_display = [
        field.name for field in Subcategory._meta.get_fields()
    ]
    list_display_links = 'id', 'title'


class SubcategoryInline(admin.TabularInline):
    model = Subcategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Модель, представляющая категорию товара."""

    list_display = 'id', 'title', 'image'
    list_display_links = 'id', 'title'
    inlines = [
        SubcategoryInline,
    ]


# МОДЕЛИ ДЛЯ ОПИСАНИЯ ПАРАМЕТРОВ ТОВАРА:

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Модель, представляющая тег товара."""

    list_display = 'id', 'name'
    list_display_links = 'id', 'name'


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    """Модель, представляющая технические характеристики товара."""

    list_display = 'id', 'name', 'value'
    list_display_links = 'id', 'name'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Модель, представляющая отзыв о товаре."""

    list_display = 'id', 'author', 'rate', 'product'
    list_display_links = 'id', 'author'


class ReviewInline(admin.TabularInline):
    model = Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Модель, представляющая продукт."""

    list_display = 'id', 'title', 'category'
    list_display_links = 'id', 'title'
    inlines = [
        ReviewInline,
    ]



