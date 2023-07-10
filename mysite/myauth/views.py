import json
import re

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

from myshop.models import Profile


@extend_schema(
    description="sign in",
    tags=['auth'],
    responses={
        200: OpenApiResponse(description="successful operation"),
        500: OpenApiResponse(description="unsuccessful operation"),
    },
    parameters=[
        OpenApiParameter(
            name='username',
            description='username',
            required=True,
        ),
        OpenApiParameter(
            name='password',
            description='password',
            required=True,
        ),
    ]
)
class SignInView(APIView):
    """Представление для обработки попытки входа пользователя в систему."""

    def post(self, request: Request) -> Response:
        username = json.loads(request.body).get('username')
        password = json.loads(request.body).get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    description="sign up",
    tags=['auth'],
    responses={
        200: OpenApiResponse(description="successful operation"),
        500: OpenApiResponse(description="unsuccessful operation"),
    },
    parameters=[
        OpenApiParameter(
            name='name',
            description='name',
            required=True,
        ),
        OpenApiParameter(
            name='username',
            description='username',
            required=True,
        ),
        OpenApiParameter(
            name='password',
            description='password',
            required=True,
        ),
    ]
)
class SignUpView(APIView):
    """Представление для регистрации нового пользователя."""

    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'

    def post(self, request: Request) -> Response:
        name = json.loads(request.body).get('name')
        username = json.loads(request.body).get('username')
        password = json.loads(request.body).get('password')

        try:
            if re.match(self.pattern, password) is None:
                raise ValidationError(
                    'The password must contain characters in both registers, '
                    '"numbers and a minimum length of 8 characters'
                )

            user = User.objects.create_user(
                username=username,
                password=password,
            )

            Profile.objects.create(id=user, fullName=name)

            login(request, user)
            return Response(status=status.HTTP_200_OK)

        except (IntegrityError, ValidationError) as error:
            return Response(
                {"unsuccessful operation": str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    description="sign out",
    tags=['auth'],
    responses={
        200: OpenApiResponse(description="successful operation"),
    }
)
class SignOutView(APIView):
    """Представление для выхода пользователя из системы."""

    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_200_OK)
