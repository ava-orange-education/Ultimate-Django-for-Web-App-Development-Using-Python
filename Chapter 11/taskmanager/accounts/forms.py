from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    organization_id = forms.IntegerField(
        required=True, widget=forms.TextInput(attrs={"autofocus": True})
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        organization_id = self.cleaned_data.get("organization_id")

        if username and password and organization_id:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
                organization_id=organization_id,
            )

            if self.user_cache is None:
                raise forms.ValidationError(
                    "Invalid username, password, or organization ID.",
                    code="invalid_login",
                )

        return self.cleaned_data
