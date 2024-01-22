import uuid
from functools import wraps

import jwt
from accounts.models import ApiToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponseForbidden
from ninja.security import HttpBearer


class ApiTokenAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> str | None:
        try:
            uuid.UUID(token, version=4)
        except ValueError:
            return None

        if ApiToken.objects.filter(token=token).exists():
            request.user = ApiToken.objects.get(token=token).user
            return token
        else:
            return None


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Decode the JWT token
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

            # Get the user information from the token's payload
            user = get_user_model().objects.get(id=payload["id"])
            request.user = user
            return user
        except Exception:
            return None


def require_permission(permission_name):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(permission_name):
                return HttpResponseForbidden("You don't have the required permission!")
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
