import json
import math

from django.contrib.auth.models import User
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
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
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Image,
    Profile,
    Category,
    Tag,
    Product,
    Review,
)
from .serializers import (
    ImageSerializer,
    ProfileSerializer,
    UserPasswordSerializer,
    CategorySerializer,
    TagSerializer,
    ProductSerializer,
    ReviewSerializer,
    ProductsSerializer,
CatalogFilter,
)


# ПРЕДСТАВЛЕНИЯ ДЛЯ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ:

@extend_schema(
    tags=['profile'],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ProfileView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin):
    """Представление для чтения и изменения информации из профиля пользователя."""

    serializer_class = ProfileSerializer

    def get_object(self) -> 'Profile':
        return Profile.objects.get(user=self.request.user)

    @extend_schema(description="Get user profile")
    def get(self, request: Request) -> Response:
        return self.retrieve(request)

    @extend_schema(description="update user info")
    def post(self, request: Request) -> Response:
        return self.partial_update(request)


@extend_schema(
    description="update user password",
    tags=['profile'],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ChangePasswordView(APIView):
    """Представление для изменения пароля пользователя."""

    serializer_class = UserPasswordSerializer

    def get_object(self):
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

    def perform_create(self, serializer):
        self.image_object = serializer.save()

    def post(self, request: Request, *args, **kwargs) -> Response:
        if request.data.get('avatar'):
            image_object = Image.objects.create(src=request.data.get('avatar'))
        else:
            self.create(request)
            image_object = self.image_object

        (
            Profile.objects
            .filter(user=self.request.user)
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
    """Представление для чтения информации о категориях товаров."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # lookup_field = 'id'


# ПРЕДСТАВЛЕНИЯ ДЛЯ ОПИСАНИЯ ПАРАМЕТРОВ ТОВАРА:

@extend_schema(
    tags=['tags'],
    description='Get tags',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
    parameters=[
        OpenApiParameter(
            name='category',
            description='categoryId',
            default=1,
        ),
    ]
)
class TagView(ListAPIView):
    """Представление для чтения информации о тегах товаров."""

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
    """Представление для чтения информации о товаре."""

    serializer_class = ProductSerializer

    def get_object(self):
        product_id = self.kwargs.get('id')
        return Product.objects.get(id=product_id)


@extend_schema(
    tags=['product'],
    description='post product review',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ProductReviewView(APIView):
    """Представление для добавления отзыва о товаре."""

    serializer_class = ReviewSerializer

    def post(self, request: Request, id: int) -> Response:
        product = Product.objects.get(id=id)

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid()
        serializer.save(product=product)

        reviews = [
            review.rate
            for review in Review.objects.filter(product=product)
            ]

        new_product_rating = round(sum(reviews) / len(reviews), 1)
        product.rating = new_product_rating
        product.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


# ПРЕДСТАВЛЕНИЯ ДЛЯ ОПИСАНИЯ КАТАЛОГА ТОВАРОВ:


class CatalogView(ListAPIView):
    """Представление для чтения каталога товаров."""

    # queryset = Product.objects.all()
    serializer_class = ProductsSerializer

    def get_queryset(self):
        filters = self.request.query_params

        self.title = filters.get('filter[name]')
        self.minPrice = float(filters.get('filter[minPrice]'))
        self.maxPrice = float(filters.get('filter[maxPrice]'))

        self.freeDelivery = bool(filters.get('filter[freeDelivery]'))
        if self.freeDelivery == 'false':
            self.freeDelivery = False

        self.available = filters.get('filter[available]')
        if self.available == 'true':
            self.range_available = (1, 1000)
        else:
            self.range_available = (0, 0)

        self.currentPage = int(filters.get('currentPage'))
        self.sort = filters.get('sort')

        self.sortType = filters.get('sortType')
        if self.sortType == 'inc':
            self.sortType = '-'
        else:
            self.sortType = ''

        self.limit = int(filters.get('limit'))

        self.queryset_all = (
            Product.objects
            .filter(
                title__icontains=self.title,
                price__range=(self.minPrice, self.maxPrice),
                freeDelivery=self.freeDelivery,
                count__range=self.range_available,
            )
            .order_by(f'{self.sortType}{self.sort}')
        )

        queryset = (
            self.queryset_all
            [
            self.limit * (self.currentPage - 1):self.limit * self.currentPage
            ]
        )

        return queryset

    def get(self, request: Request, *args, **kwargs) -> Response:
        obj = super().get(request, *args, **kwargs)

        lastPage = math.ceil(
            self.queryset_all.count() / self.limit
        )

        print("!!!!!!!!!!***", obj.data)
        return Response(
            {
                'items': obj.data,
                'currentPage': self.currentPage,
                'lastPage': lastPage,
            },
            status=status.HTTP_200_OK
        )
    #     serializer = ProductsSerializer(data=obj, many=True)
    #     print(serializer)


        # serializer = ProductsSerializer(data=queryset)
        # serializer.is_valid()
        # serializer.save()
        # return Response(
        #     {
        #         'items': serializer.data,
        #         'currentPage': currentPage,
        #         'lastPage': 10,
        #     },
        #     status=status.HTTP_200_OK
        # )


    # filter_backends = [
    #     DjangoFilterBackend,
    #     OrderingFilter,
    # ]
    # filterset_class = CatalogFilter


    # def get_queryset(self):
    #     print("!!!!!", self.kwargs)
    #     return Product.objects.all()

    # filterset_fields = [
    #     'title',
    #     'price',
    #     'freeDelivery',
    #     'count',
    # ]
    #

    # def get(self, request):
    #     print("!!!!!", request.query_params)
    #     filters = dict(request.query_params)
    #     print("!!!!!", filters)
    #     title = filters.get('filter[name]')
    #     print(title)

        # queryset = Product.objects.all()
        #
        # return Response(queryset.filter(title=title), status=200)

    # queryset = Product.objects.all()
    # serializer_class = ProductFilter
    #
    # filter_backends = [
    #     OrderingFilter,
    #     DjangoFilterBackend,
    # ]
    # ordering_fields = [
    #     'rating',
    #     'price',
    #     'reviews',
    #     'date',
    # ]
    #
    # filterset_fields = [
    #     'title',
    #     'price',
    #     'freeDelivery',
    #     'count',
    # ]

