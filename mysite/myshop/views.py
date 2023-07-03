from datetime import datetime

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
    RetrieveAPIView,
)
from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

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
    lookup_field = 'id'


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
class ProductReviewView(CreateAPIView):
    """Представление для добавления отзыва о товаре."""

    serializer_class = ReviewSerializer

    def post(self, request: Request, id) -> Response:
        print("!!!!!!", request.data)

        product = Product.objects.get(id=id)
        author = request.data.get('author')
        email = request.data.get('email')
        text = request.data.get('text')
        rate = request.data.get('rate')
        date = datetime.now()

        Review.objects.create(
            author=author,
            email=email,
            text=text,
            rate=rate,
            date=date,
            product=product,
        )

        if 'csrfmiddlewaretoken' not in request.data:
            request.data.update(date=date)
            request.data.update(product=product)

        serializer = ReviewSerializer(request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)