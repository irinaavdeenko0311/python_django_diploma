from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Profile
from .serializers import ProfileSerializer


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
