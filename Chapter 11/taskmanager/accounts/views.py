from accounts.forms import CustomAuthenticationForm
from accounts.services import generate_token, issue_jwt_refresh_token, issue_jwt_token
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username}!")
            return redirect(
                "accounts:login"
            )  # Redirect to the login page or any other page you want
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm


@login_required
def token_generation_view(request):
    """
    A view that displays the user's API token. If a token does not exist,
    it generates a new one. This view handles only GET requests.
    """
    token = generate_token(request.user)
    jwt_token = issue_jwt_token(request.user)
    refresh_token = issue_jwt_refresh_token(request.user)
    return render(
        request,
        "accounts/token_display.html",
        {"token": token, "jwt_token": jwt_token, "refresh_token": refresh_token},
    )
