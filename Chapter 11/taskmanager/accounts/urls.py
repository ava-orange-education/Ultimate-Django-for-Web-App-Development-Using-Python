from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"
urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/",
        views.CustomLoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password_change/",
        PasswordChangeView.as_view(
            success_url=reverse_lazy("accounts:password_change_done"),
            template_name="accounts/password_change_form.html",
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "password_reset/",
        PasswordResetView.as_view(
            success_url=reverse_lazy("accounts:password_reset_done"),
            email_template_name="accounts/custom_password_reset_email.html",
            template_name="accounts/password_reset_form.html",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm_form.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("show-api-token/", views.token_generation_view, name="api-token"),
]
