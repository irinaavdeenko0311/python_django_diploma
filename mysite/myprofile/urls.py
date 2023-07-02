from django.urls import path

from .views import ProfileView, AvatarView, ChangePasswordView

app_name = "profile"

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile", ProfileView.as_view(), name="profile_with_slash"),
    path("profile/password", ChangePasswordView.as_view(), name="profile_password"),
    path("profile/avatar", AvatarView.as_view(), name="profile_avatar"),
]
