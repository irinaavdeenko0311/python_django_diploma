from datetime import datetime

import django_filters
from rest_framework import serializers

from .models import (
    Image,
    Profile,
    Category,
    Subcategory,
    Tag,
    Specification,
    Review,
    Product,
    ProductSale,
)


# ОБЩИЕ СЕРИАЛИЗАТОРЫ:

class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Image"""

    class Meta:
        model = Image
        fields = 'src', 'alt'


# СЕРИАЛИЗАТОРЫ ДЛЯ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ:

class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Profile."""

    avatar = ImageSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'fullName',
            'email',
            'phone',
            'avatar',
        )


class UserPasswordSerializer(serializers.Serializer):
    """Сериализатор для преобразования пароля из модели User"""

    currentPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)


# СЕРИАЛИЗАТОРЫ ДЛЯ КАТЕГОРИЙ ТОВАРОВ:

class SubcategorySerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Subcategory"""

    image = ImageSerializer(read_only=True)

    class Meta:
        model = Subcategory
        fields = (
            'id',
            'title',
            'image',
        )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Category"""

    image = ImageSerializer(read_only=True)
    subcategories = SubcategorySerializer(read_only=True, many=True)

    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'image',
            'subcategories',
        )


# СЕРИАЛИЗАТОРЫ ДЛЯ ПАРАМЕТРОВ ТОВАРА:

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Tag."""

    class Meta:
        model = Tag
        fields = 'id', 'name',


class SpecificationSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Specification"""

    class Meta:
        model = Specification
        fields = 'name', 'value'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Review"""

    date = serializers.DateTimeField(
        read_only=True,
        initial=datetime.now(),
        format='%Y-%m-%d %H:%M'
    )

    class Meta:
        model = Review
        fields = (
            'author',
            'email',
            'text',
            'rate',
            'date',
        )


class ProductFullSerializer(serializers.ModelSerializer):
    """
    Сериализатор для преобразования данных модели Product.

    Вывод полной информации о товаре.
    """

    date = serializers.DateTimeField(
        read_only=True,
        format=f'%a %b %d %Y %H:%M:%S %Z%z (Central European Standard Time)'
    )
    images = ImageSerializer(read_only=True, many=True)
    tags = TagSerializer(read_only=True, many=True)
    # tags = serializers.StringRelatedField(many=True)
    reviews = ReviewSerializer(read_only=True, many=True)
    specifications = SpecificationSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'fullDescription',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'specifications',
            'rating',
        )


# СЕРИАЛИЗАТОРЫ ДЛЯ КАТАЛОГА ТОВАРОВ:

class ProductShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для преобразования данных модели Product.

    Вывод частичной информации о товаре - для каталога.
    """

    date = serializers.DateTimeField(
        read_only=True,
        format=f'%a %b %d %Y %H:%M:%S %Z%z (Central European Standard Time)'
    )
    images = ImageSerializer(read_only=True, many=True)
    tags = TagSerializer(read_only=True, many=True)
    reviews = serializers.IntegerField(
        read_only=True,
        source='reviews.count',
    )

    class Meta:
        model = Product
        fields = (
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'rating',
        )


class ProductSaleSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели ProductSale."""

    dateFrom = serializers.DateTimeField(
        read_only=True,
        format=f'%m-%d'
    )
    dateTo = serializers.DateTimeField(
        read_only=True,
        format=f'%m-%d'
    )
    images = ImageSerializer(read_only=True, many=True)

    class Meta:
        model = ProductSale
        fields = (
            'id',
            'price',
            'salePrice',
            'dateFrom',
            'dateTo',
            'title',
            'images',
        )


# class CategoriesFilter(django_filters.FilterSet):
#
#
#     date = serializers.DateTimeField(
#         read_only=True,
#         format=f'%a %b %d %Y %H:%M:%S %Z%z (Central European Standard Time)'
#     )
#     images = ImageSerializer(read_only=True, many=True)
#     tags = TagSerializer(read_only=True, many=True)
#     reviews = serializers.IntegerField(
#         read_only=True,
#         source='reviews.count',
#     )
#
#     class Meta:
#         model = Product
#         fields = (
#             'id',
#             'category',
#             'price',
#             'count',
#             'date',
#             'title',
#             'description',
#             'freeDelivery',
#             'images',
#             'tags',
#             'reviews',
#             'rating',
#         )

# class CatalogFilter(django_filters.FilterSet):
#     category = django_filters.NumberFilter(field_name='category')
#     class Meta:
#         model = Product
#         fields = 'category',

# class CatalogFilter(django_filters.FilterSet):
#     name = django_filters.CharFilter(field_name='title')
#     minPrice = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
#     maxPrice = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
#     freeDelivery = django_filters.BooleanFilter(field_name='freeDelivery')
#     available = django_filters.BooleanFilter(field_name='count')
#
#     class Meta:
#         model = Product
#         fields = [
#             'name',
#             'minPrice',
#             'maxPrice',
#             'freeDelivery',
#             'available',
#         ]
