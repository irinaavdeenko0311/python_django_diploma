from django.urls import path

# from rest_framework.routers import DefaultRouter

from .views import (
    ProfileView,
    ChangePasswordView,
    AvatarView,
    CategoriesView,
    TagView,
    ProductView,
    ProductReviewView,

    CatalogView,
)

app_name = "shop"

# routers = DefaultRouter()
# routers.register('categories', CategoriesView)

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile", ProfileView.as_view(), name="profile_with_slash"),
    path("profile/password", ChangePasswordView.as_view(), name="profile_password"),
    path("profile/avatar", AvatarView.as_view(), name="profile_avatar"),

    path("categories", CategoriesView.as_view()),
    # path("", include(routers.urls)),

    path("tags", TagView.as_view(), name="tags"),
    path("product/<int:id>", ProductView.as_view(), name="product"),
    path("product/<int:id>/reviews", ProductReviewView.as_view(), name="product_reviews"),

    path("catalog", CatalogView.as_view(), name="catalog"),
]
