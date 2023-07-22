from datetime import datetime

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
    OrderProduct,
    Order,
)


# ОБЩИЕ СЕРИАЛИЗАТОРЫ:

class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Image."""

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
    """Сериализатор для преобразования пароля из модели User."""

    currentPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)


# СЕРИАЛИЗАТОРЫ ДЛЯ КАТЕГОРИЙ ТОВАРОВ:

class SubcategorySerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Subcategory."""

    image = ImageSerializer(read_only=True)

    class Meta:
        model = Subcategory
        fields = (
            'id',
            'title',
            'image',
        )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Category."""

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


# СЕРИАЛИЗАТОРЫ ДЛЯ ТОВАРА И ЕГО ПАРАМЕТРОВ:

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Tag."""

    class Meta:
        model = Tag
        fields = 'id', 'name',


class SpecificationSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Specification."""

    class Meta:
        model = Specification
        fields = 'name', 'value'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Review."""

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
        format='%a %b %d %Y %H:%M:%S %Z%z (Central European Standard Time)'
    )
    images = ImageSerializer(read_only=True, many=True)
    tags = TagSerializer(read_only=True, many=True)
    reviews = ReviewSerializer(read_only=True, many=True)
    specifications = SpecificationSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = '__all__'


# СЕРИАЛИЗАТОРЫ ДЛЯ КАТАЛОГА ТОВАРОВ:

class ProductShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для преобразования данных модели Product.

    Вывод частичной информации о товаре.
    """

    date = serializers.DateTimeField(
        read_only=True,
        format='%a %b %d %Y %H:%M:%S %Z%z (Central European Standard Time)'
    )
    images = ImageSerializer(read_only=True, many=True)
    tags = TagSerializer(read_only=True, many=True)
    reviews = serializers.IntegerField(
        read_only=True,
        source='reviews.count',
    )

    class Meta:
        model = Product
        exclude = 'fullDescription',


class ProductSaleSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели ProductSale."""

    dateFrom = serializers.DateTimeField(
        read_only=True,
        format='%m-%d'
    )
    dateTo = serializers.DateTimeField(
        read_only=True,
        format='%m-%d'
    )
    images = ImageSerializer(read_only=True, many=True)

    class Meta:
        model = ProductSale
        fields = '__all__'


# СЕРИАЛИЗАТОРЫ ДЛЯ ЗАКАЗОВ:

class OrderProductSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели OrderProduct."""

    class Meta:
        model = OrderProduct
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Order."""

    createdAt = serializers.DateTimeField(
        read_only=True,
        initial=datetime.now(),
        format='%Y-%m-%d %H:%M'
    )
    products = OrderProductSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = '__all__'
