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
    ProductSale,
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
    list_display_links = 'id',


# МОДЕЛИ ДЛЯ ОПИСАНИЯ КАТЕГОРИЙ ТОВАРОВ:

class ProductInline(admin.TabularInline):
    model = Product


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """Модель, представляющая подкатегорию товара."""

    list_display = 'id', 'title', 'categories'
    list_display_links = 'id', 'title'
    inlines = [
        ProductInline,
    ]


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
    """Модель, представляющая товар."""

    list_display = 'id', 'title', 'category'
    list_display_links = 'id', 'title'
    inlines = [
        ReviewInline,
    ]


@admin.register(ProductSale)
class ProductSaleAdmin(admin.ModelAdmin):
    """Модель, представляющая товар, участвующий в распродаже."""

    list_display = 'id', 'title'

    def save_related(self, request, form, formsets, change):
        """
        Дополнение метода.

        После сохранения экземпляра модели через административную панель
        изменение поля images(m2m) нужными значениями.
        """
        super(ProductSaleAdmin, self).save_related(request, form, formsets, change)

        images = (
            Product.objects
            .prefetch_related('images')
            .get(id=form.instance.id.id)
            .images.all()
        )
        form.instance.images.set(images)
