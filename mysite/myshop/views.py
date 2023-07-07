import json
import math
import random
from datetime import datetime
from operator import itemgetter
from typing import List

from django.forms.models import model_to_dict
from rest_framework import serializers
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Max
from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter, OpenApiExample, extend_schema_view,
)
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import (
    Image,
    Profile,
    Category,
    Tag,
    Product,
    Review,
    Subcategory,
    ProductSale,
)
from .serializers import (
    ImageSerializer,
    ProfileSerializer,
    UserPasswordSerializer,
    CategorySerializer,
    TagSerializer,
    ProductFullSerializer,
    ReviewSerializer,
    ProductShortSerializer,
    ProductSaleSerializer,
)


# ПРЕДСТАВЛЕНИЯ ДЛЯ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ:

###############
class IsActive(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active

@extend_schema(
    tags=['profile'],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ProfileView(
    # UserPassesTestMixin,
LoginRequiredMixin,
    GenericAPIView,
    RetrieveModelMixin,
    UpdateModelMixin
):
    """Представление для чтения и изменения информации из профиля пользователя."""

    serializer_class = ProfileSerializer
    # permission_classes = [IsActive]

    # def test_func(self):
    #     return self.request.user.is_active

    def get_object(self) -> Profile:
        return Profile.objects.get(id=self.request.user)

    @extend_schema(description="Get user profile")
    def get(self, request: Request) -> Response:
        print("!!!!", self.request.user)
        return self.retrieve(request)

    @extend_schema(description="update user info")
    def post(self, request: Request) -> Response:
        return self.partial_update(request)


@extend_schema(
    tags=['profile'],
    description="update user password",
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ChangePasswordView(APIView):
    """Представление для изменения пароля пользователя."""

    serializer_class = UserPasswordSerializer

    def get_object(self) -> User:
        return User.objects.get(id=self.request.user.id)

    def post(self, request: Request) -> Response:
        user_object = self.get_object()
        serializer = UserPasswordSerializer(data=request.data)

        try:
            if serializer.is_valid():
                old_password = serializer.data.get('currentPassword')
                if user_object.check_password(old_password):
                    user_object.set_password(serializer.data.get('newPassword'))
                    user_object.save()
                    update_session_auth_hash(request, user_object)
                    return Response(status=status.HTTP_200_OK)
                else:
                    raise ValidationError("The password you have entered does not match your current one. ")

        except ValidationError as error:
            return Response(error, status=status.HTTP_403_FORBIDDEN)


@extend_schema(
    tags=['profile'],
    description='update user avatar (request.FILES["avatar"] in Django)',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class AvatarView(CreateAPIView):
    """Представление для добавления/изменения аватара профиля пользователя."""

    serializer_class = ImageSerializer

    def perform_create(self, serializer) -> None:
        self.image_object = serializer.save()

    def post(self, request: Request, *args, **kwargs) -> Response:
        if request.data.get('avatar'):
            image_object = Image.objects.create(src=request.data.get('avatar'))
        else:
            self.create(request)
            image_object = self.image_object

        (
            Profile.objects
            .filter(id=self.request.user)
            .update(avatar=image_object)
        )

        return Response(status=status.HTTP_200_OK)


# ПРЕДСТАВЛЕНИЯ ДЛЯ ОПИСАНИЯ КАТЕГОРИЙ ТОВАРОВ:

@extend_schema(
    tags=['catalog'],
    description='get catalog menu',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class CategoriesView(ListAPIView):
    """Представление для вывода категорий товаров."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # lookup_field = 'id'


# ПРЕДСТАВЛЕНИЯ ДЛЯ ОПИСАНИЯ ПАРАМЕТРОВ ТОВАРА:

@extend_schema(
    tags=['tags'],
    description='Get tags',
    parameters=[
        OpenApiParameter(
            name='category',
            description='categoryId',
            default=1,
            type=OpenApiTypes.NUMBER,
        ),
    ],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class TagView(ListAPIView):
    """Представление для вывода тегов товаров."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@extend_schema(
    tags=['product'],
    description='get catalog item',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ProductView(RetrieveAPIView):
    """Представление для вывода информации о товаре."""

    serializer_class = ProductFullSerializer

    def get_object(self) -> Product:
        product_id = self.kwargs.get('id')
        return Product.objects.get(id=product_id)


@extend_schema(
    tags=['product'],
    description='post product review',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ReviewView(APIView):
    """Представление для добавления отзыва о товаре."""

    serializer_class = ReviewSerializer

    def post(self, request: Request, id: int) -> Response:
        product = Product.objects.get(id=id)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)

        # обновление рейтинга товара после добавления нового отзыва:
        reviews = [
            review.rate
            for review in Review.objects.filter(product=product)
            ]

        new_product_rating = round(sum(reviews) / len(reviews), 1)
        product.rating = new_product_rating
        product.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


# ПРЕДСТАВЛЕНИЯ ДЛЯ ОПИСАНИЯ КАТАЛОГА ТОВАРОВ:


@extend_schema(
    tags=['catalog'],
    description='get catalog items',
    parameters=[
        OpenApiParameter(
            name='filter',
            description='search text',
            type=OpenApiTypes.OBJECT,
            default={
                "name": "string",
                "minPrice": 0,
                "maxPrice": 0,
                "freeDelivery": False,
                "available": True
            }
        ),
        OpenApiParameter(
            name='currentPage',
            description='page',
            default=1,
            type=OpenApiTypes.NUMBER,
        ),
        OpenApiParameter(
            name='category',
            type=OpenApiTypes.NUMBER,
        ),
        OpenApiParameter(
            name='sort',
            enum=('rating', 'price', 'reviews', 'date'),
            default='price',
        ),
        OpenApiParameter(
            name='sortType',
            enum=('dec', 'inc'),
            default='inc',
        ),
        OpenApiParameter(
            name='tags',
            description='page',
            type=OpenApiTypes.OBJECT,
            many=True,
        ),
        OpenApiParameter(
            name='limit',
            default=20,
            type=OpenApiTypes.NUMBER,
        ),
    ],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class CatalogView(ListAPIView):
    """Представление для вывода каталога товаров."""

    serializer_class = ProductShortSerializer

    def get_queryset(self) -> QuerySet:
        filter_parameters = self.request.query_params

        self.title = filter_parameters.get('filter[name]')
        self.minPrice = filter_parameters.get('filter[minPrice]')
        self.maxPrice = filter_parameters.get('filter[maxPrice]')

        self.freeDelivery = filter_parameters.get('filter[freeDelivery]')

        self.available = filter_parameters.get('filter[available]')
        if self.available == 'true':
            self.available = True
        else:
            self.available = False

        self.currentPage = int(filter_parameters.get('currentPage'))
        self.category = filter_parameters.get('category')
        self.sort = filter_parameters.get('sort')

        self.sortType = filter_parameters.get('sortType')
        if self.sortType == 'inc':
            self.sortType = '-'
        else:
            self.sortType = ''

        self.tags = filter_parameters.getlist('tags[]')
        self.tags = [tag for tag in self.tags]

        self.limit = int(filter_parameters.get('limit'))

        self.queryset_all = (
            Product.objects
            .annotate(sort=Max(self.sort))
            .filter(
                title__icontains=self.title,
                price__range=(self.minPrice, self.maxPrice),
                count__gte=self.available,
            )
            .order_by(f'{self.sortType}sort')
        )

        if self.freeDelivery == 'true':
            self.queryset_all = self.queryset_all.filter(
                freeDelivery=True
            )

        if self.category:
            self.queryset_all = self.queryset_all.filter(
                category=self.category
            )

        if self.tags:
            self.queryset_all = (
                self.queryset_all.filter(tags__in=self.tags)
                .distinct()
            )

        queryset = (
            self.queryset_all
            [self.limit * (self.currentPage - 1):self.limit * self.currentPage]
        )

        return queryset

    def get(self, request: Request, *args, **kwargs) -> Response:
        response = super().get(request, *args, **kwargs)

        lastPage = math.ceil(
            self.queryset_all.count() / self.limit
        )

        return Response(
            {
                'items': response.data,
                'currentPage': self.currentPage,
                'lastPage': lastPage,
            },
            status=status.HTTP_200_OK
        )


@extend_schema(
    tags=['catalog'],
    description='get catalog popular items',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ProductsPopularView(ListAPIView):
    """Представление для вывода популярных товаров."""

    queryset = Product.objects.order_by('-rating')[:4]
    serializer_class = ProductShortSerializer


@extend_schema(
    tags=['catalog'],
    description='get catalog limeted items',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ProductsLimitedView(ListAPIView):
    """Представление для вывода товаров с ограниченным тиражом."""

    queryset = Product.objects.filter(count__range=(1, 2))
    serializer_class = ProductShortSerializer


@extend_schema(
    tags=['catalog'],
    description='get sales items',
    parameters=[
        OpenApiParameter(
            name='currentPage',
            description='page',
            type=OpenApiTypes.NUMBER,
            default=1
        )
    ],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ProductSaleView(ListAPIView):
    """Представление для вывода товаров, участвующих в распродаже."""

    serializer_class = ProductSaleSerializer
    limit = 5

    def get_queryset(self) -> QuerySet:
        self.currentPage = int(self.request.query_params.get('currentPage'))

        self.queryset_all = ProductSale.objects.all()

        queryset = (
            self.queryset_all
            [self.limit * (self.currentPage - 1):self.limit * self.currentPage]
        )

        return queryset

    def get(self, request: Request, *args, **kwargs) -> Response:
        response = super().get(request, *args, **kwargs)

        lastPage = math.ceil(
            self.queryset_all.count() / self.limit
        )

        return Response(
            {
                'items': response.data,
                'currentPage': self.currentPage,
                'lastPage': lastPage,
            },
            status=status.HTTP_200_OK
        )


@extend_schema(
    tags=['catalog'],
    description='get banner items',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ProductBannersSaleView(ListAPIView):
    """
    Представление для вывода товаров на баннере главной страницы.

    Выводит три товара из случайных категорий.
    После клика на эти товары переход в раздел категории.
    """

    serializer_class = ProductShortSerializer

    def get_queryset(self) -> List[Product]:
        category_count = (
            Subcategory.objects.all()
            .aggregate(category_count=Max('id'))['category_count'])
        categories = random.sample(range(1, category_count + 1), 3)

        return [
            Product.objects
            .filter(category=category)
            .first()
            for category in categories
        ]


@extend_schema(
    tags=['basket'],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class BasketView(ListAPIView):
    """Представление для работы с корзиной"""

    serializer_class = ProductShortSerializer

    def get_queryset(self) -> List[Product]:
        self.basket = self.request.session.get('basket')

        if self.basket:
            return [
                Product.objects.get(id=position['id'])
                for position in self.basket
            ]
        self.request.session['basket'] = list()

    @extend_schema(
        description='Get items in basket',
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        response = super().get(request, *args, **kwargs)

        if self.basket:
            basket_id = [position['id'] for position in self.basket]

        # меняем количество и стоимость товаров (в соответствии с корзиной):
        for product in response.data:
            product_id = product.get('id')

            index = basket_id.index(product_id)
            product_count = self.basket[index]['count']

            product['count'] = product_count
            product['price'] = product['price'] * product_count

        return Response(response.data, status=status.HTTP_200_OK)

    @extend_schema(
        description='Add item to basket',
        examples=[
            OpenApiExample(
                name='product count',
                value={
                    'id': 1,
                    'count': 5,
                },
            ),
        ],
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        basket = self.request.session.get('basket')

        product_id = request.data.get('id')
        product_count = request.data.get('count')

        basket_id = [position['id'] for position in basket]
        if product_id in basket_id:
            index = basket_id.index(product_id)
            basket[index]['count'] += product_count
        else:
            basket.append(dict(id=product_id, count=product_count))

        self.request.session['basket'] = basket

        return self.get(request, *args, **kwargs)

    @extend_schema(
        description='Remove item from basket',
        examples=[
            OpenApiExample(
                name='product count',
                value={
                    'id': 1,
                    'count': 5,
                },
            ),
        ],
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        basket = self.request.session.get('basket')

        product_id = request.data.get('id')
        product_count = request.data.get('count')

        basket_id = [position['id'] for position in basket]
        index = basket_id.index(product_id)
        basket[index]['count'] -= product_count

        if basket[index]['count'] == 0:
            basket.pop(index)

        self.request.session['basket'] = basket

        return self.get(request, *args, **kwargs)
