import math
import random
from datetime import datetime
from typing import List, Optional

from django.contrib.auth.models import User
from django.db.models import Max
from django.db.models.query import QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample,
)
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    ListCreateAPIView,
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
    Subcategory,
    ProductSale,
    Order,
    OrderProduct,
)
from .serializers import (
    ImageSerializer,
    ProfileSerializer,
    UserPasswordSerializer,
    CategorySerializer,
    TagSerializer,
    ReviewSerializer,
    ProductFullSerializer,
    ProductShortSerializer,
    ProductSaleSerializer,
    OrderSerializer,
)


# ПРЕДСТАВЛЕНИЯ ДЛЯ РАБОТЫ С ПРОФИЛЕМ ПОЛЬЗОВАТЕЛЯ:

@extend_schema(
    tags=['profile'],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class ProfileView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin):
    """Представление для чтения/изменения информации из профиля пользователя."""

    serializer_class = ProfileSerializer

    def get_object(self) -> Profile:
        return Profile.objects.get(id=self.request.user)

    @extend_schema(description="Get user profile")
    def get(self, request: Request) -> Response:
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
                    raise ValidationError(
                        "The password you have entered "
                        "does not match your current one."
                    )

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


# ПРЕДСТАВЛЕНИЯ ДЛЯ РАБОТЫ С КАТЕГОРИЯМИ ТОВАРОВ:

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


# ПРЕДСТАВЛЕНИЯ ДЛЯ РАБОТЫ С ТОВАРОМ И ЕГО ПАРАМЕТРАМИ:

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
        new_product_rating = round(
            float(product.rating) * 0.8 + serializer.data.get('rate') * 0.2,
            1
        )
        product.rating = new_product_rating
        product.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


# ПРЕДСТАВЛЕНИЯ ДЛЯ РАБОТЫ С КАТАЛОГОМ ТОВАРОВ:

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

    queryset = Product.objects.order_by('-rating')[:8]
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

    queryset = Product.objects.filter(count__range=(1, 2))[:16]
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


# ПРЕДСТАВЛЕНИЯ ДЛЯ РАБОТЫ С КОРЗИНОЙ:

@extend_schema(
    tags=['basket'],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class BasketView(ListAPIView):
    """Представление для работы с корзиной."""

    serializer_class = ProductShortSerializer

    def get_queryset(self) -> Optional[List[Product]]:
        self.basket = self.request.session.get('basket')

        if self.basket:
            queryset = list()
            for position in self.basket:
                product = Product.objects.get(id=position['id'])
                # проверка наличия товара:
                if product.count > 0:
                    queryset.append(product)
                    # невозможно добавить в корзину товаров больше,
                    # чем имеется в наличии:
                    if product.count < position['count']:
                        position['count'] = product.count
            return queryset

        self.request.session['basket'] = list()

    @extend_schema(
        description='Get items in basket',
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        response = super().get(request, *args, **kwargs)

        if self.basket:
            basket_id = [position['id'] for position in self.basket]

        # меняем количество товаров в соответствии с корзиной:
        for product in response.data:
            product_id = product.get('id')

            index = basket_id.index(product_id)
            product_count = self.basket[index]['count']

            product['count'] = product_count

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


# ПРЕДСТАВЛЕНИЯ ДЛЯ РАБОТЫ С ЗАКАЗАМИ:

@extend_schema(
    tags=['order'],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class OrdersView(ListCreateAPIView):
    """Представление для чтения и изменения заказов пользователя."""

    serializer_class = OrderSerializer

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        return Order.objects.filter(user=user)

    @extend_schema(description='Get active order')
    def get(self, request: Request, *args, ** kwargs) -> Response:
        response = super().get(request, *args, ** kwargs)

        # Товары заказа хранятся в таблице OrderProduct
        # в формате "товар-количество", но каждом заказе необходимо
        # выводить информацию о товаре в соответствии с
        # сериализатором ProductShortSerializer.
        # Поэтому в сериализаторе каждого товара заменим параметры:
        # count - на количество товара в заказе
        # price - на общую стоимость товаров в заказе:
        for order in response.data:
            for product in order.get('products'):
                product_id = product.get('product')
                product_count = product.get('count')

                product_obj = Product.objects.get(id=product_id)
                serializer = ProductShortSerializer(product_obj).data

                serializer['id'] = product_id
                serializer['count'] = product_count
                product.update(serializer)

        return Response(response.data, status=status.HTTP_200_OK)

    @extend_schema(description='Create order')
    def post(self, request: Request) -> Response:
        totalCost = sum(
            [
                product.get('price') * product.get('count')
                for product in request.data
            ]
        )

        user = request.user

        # если пользователь не авторизован, создается заказ
        # без привязки к пользователю:
        if not user.is_authenticated:
            order = Order.objects.create(
                totalCost=totalCost,
            )
        else:
            profile = Profile.objects.get(id=user)
            fullName = profile.fullName
            email = profile.email
            phone = profile.phone

            order = Order.objects.create(
                user=user,
                fullName=fullName,
                email=email,
                phone=phone,
                totalCost=totalCost,
            )

        for product in request.data:
            product_id = product.get('id')
            product_count = product.get('count')

            order_product = OrderProduct.objects.create(
                product=Product.objects.get(id=product_id),
                count=product_count,
            )

            order.products.add(order_product)

        # если пользователь не авторизован, при оформлении
        # заказа он будет перекинут либо на страницу с
        # авторизацией, либо с регистрацией -
        # чтобы при этом не потерять номер заказа,
        # сохраним его в кэше и после того, как пользователь
        # авторизуется/зарегистрируется, привяжем данный
        # заказ в этому пользователю:
        if not user.is_authenticated:
            self.request.session['order'] = order.id

        return Response(
            {'orderId': order.id},
            status=status.HTTP_200_OK
        )


@extend_schema(
    tags=['order'],
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class OrderView(RetrieveAPIView):
    """Представление для чтения и изменения заказа пользователя."""

    serializer_class = OrderSerializer

    def get_object(self):
        order_id = self.kwargs.get('id')
        return Order.objects.get(id=order_id)

    @extend_schema(description="Get order")
    def get(self, request: Request, id: int) -> Response:
        response = super().get(request, id)

        # Товары заказа хранятся в таблице OrderProduct
        # в формате "товар-количество", но необходимо выводить
        # информацию о товаре в соответствии с
        # сериализатором ProductShortSerializer.
        # Поэтому в сериализаторе каждого товара заменим параметры:
        # count - на количество товара в заказе
        # price - на общую стоимость товаров в заказе:
        for product in response.data.get('products'):
            product_id = product.get('product')
            product_count = product.get('count')

            product_obj = Product.objects.get(id=product_id)
            serializer = ProductShortSerializer(product_obj).data

            serializer['id'] = product_id
            serializer['count'] = product_count
            product.update(serializer)

        return Response(response.data, status=status.HTTP_200_OK)

    @extend_schema(description="Confirm order")
    def post(self, request: Request, id: int) -> Response:
        order = Order.objects.get(id=id)

        order.fullName = request.data.get('fullName')
        order.phone = request.data.get('phone')
        order.email = request.data.get('email')
        order.paymentType = request.data.get('paymentType')
        order.city = request.data.get('city')
        order.address = request.data.get('address')

        current_deliveryType = order.deliveryType
        new_deliveryType = request.data.get('deliveryType')
        if (
                new_deliveryType == 'express'
                and current_deliveryType == 'ordinary'
        ):
            if order.totalCost < 2200:
                order.totalCost -= 200
            order.totalCost += 500
        elif (
                new_deliveryType == 'ordinary'
                and current_deliveryType == 'express'
        ):
            order.totalCost -= 500
            if order.totalCost < 2000:
                order.totalCost += 200

        order.deliveryType = new_deliveryType

        if order.status == 'created':
            order.status = 'accepted'

            # при подтверждении заказа меняем количество товара
            # в наличии в БД:
            products_in_order = request.data.get('products')
            products_id = [product['id'] for product in products_in_order]
            for order_product in order.products.all():
                product_id = order_product.product.id
                index = products_id.index(product_id)
                product_count = products_in_order[index]['count']

                product_obj = Product.objects.get(id=product_id)
                product_obj.count = product_count
                product_obj.save()

        order.save()

        return Response({'orderId': id}, status=status.HTTP_200_OK)


# ПРЕДСТАВЛЕНИЯ ОПЛАТЫ:

@extend_schema(
    tags=['payment'],
    description='Payment',
    responses={
        200: OpenApiResponse(description="successful operation"),
    },
)
class PaymentView(APIView):
    """Представление для оплаты."""

    def post(self, request: Request, id: int) -> Response:
        date_now = datetime.strptime(
            f'{datetime.now().year}-{datetime.now().month}', "%Y-%m"
        )
        date_card = datetime.strptime(
            f"{request.data.get('year')}-{request.data.get('month')}", "%y-%m"
        )
        try:
            if (
                    int(request.data.get('number')) % 2 != 0
                    or len(request.data.get('number')) > 12
                    or date_now > date_card
            ):
                raise ValidationError('ValidationError')

            order = Order.objects.get(id=id)
            order.status = 'paid'
            order.save()

            return Response(status=status.HTTP_200_OK)
        except (ValueError, ValidationError) as error:
            return Response(
                {"unsuccessful operation": str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
