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
)


# ОБЩИЕ СЕРИАЛИЗАТОРЫ:

class ImageSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Image"""

    class Meta:
        model = Image
        fields = 'src', 'alt'


# СЕРИАЛИЗАТОРЫ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ:

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


# СЕРИАЛИЗАТОРЫ КАТЕГОРИЙ ТОВАРОВ:

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


# СЕРИАЛИЗАТОРЫ ДЛЯ ОПИСАНИЯ ПАРАМЕТРОВ ТОВАРА:

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Tag"""

    class Meta:
        model = Tag
        fields = 'name',


class SpecificationSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Specification"""

    class Meta:
        model = Specification
        fields = 'name', 'value'


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Review"""

    date = serializers.DateTimeField('read_only=True')

    class Meta:
        model = Review
        fields = (
            'author',
            'email',
            'text',
            'rate',
            'date',
        )


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для преобразования данных модели Product"""

    images = ImageSerializer(read_only=True, many=True)
    tags = TagSerializer(read_only=True, many=True)
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
