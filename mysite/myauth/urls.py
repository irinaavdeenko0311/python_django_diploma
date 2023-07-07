from django.urls import path

from .views import SignInView, SignUpView, SignOutView

app_name = "auth"

urlpatterns = [
    path("sign-in", SignInView.as_view()),
    path("sign-up", SignUpView.as_view()),
    path("sign-out", SignOutView.as_view()),
]
