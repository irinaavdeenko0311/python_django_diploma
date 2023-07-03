from django.urls import path

from .views import (
    ProfileView,
    ChangePasswordView,
    AvatarView,
    CategoriesView,
    TagView,
    ProductView,
    ProductReviewView,

)

app_name = "shop"

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile", ProfileView.as_view(), name="profile_with_slash"),
    path("profile/password", ChangePasswordView.as_view(), name="profile_password"),
    path("profile/avatar", AvatarView.as_view(), name="profile_avatar"),

    path("categories", CategoriesView.as_view(), name="categories"),

    path("tags", TagView.as_view(), name="tags"),
    path("product/<int:id>", ProductView.as_view(), name="product"),
    path("product/<int:id>/reviews", ProductReviewView.as_view(), name="product_reviews"),
]
