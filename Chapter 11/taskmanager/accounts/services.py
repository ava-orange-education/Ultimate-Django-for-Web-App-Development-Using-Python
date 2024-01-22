from datetime import datetime, timedelta

import jwt
from accounts.models import ApiToken
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


def generate_token(user: AbstractUser) -> str:
    """
    Retrieves or generates a unique API token for a given user.

    If an API token already exists for the specified user, that token is returned.
    If no token exists, a new token is created and returned.

    Parameters:
    user (AbstractUser): The user instance for whom the token is to be retrieved or generated.

    Returns:
    str: The API token associated with the user.
    """
    token, _ = ApiToken.objects.get_or_create(user=user)
    return str(token.token)


def issue_jwt_token(user: AbstractUser) -> str:
    """
    Generate a JWT (JSON Web Token) for the given user.

    This function creates a JWT with a payload containing the user's ID and an
    expiration time set to 1 day from the current time. The token is encoded
    using the HS256 algorithm.

    Parameters:
    user (AbstractUser): The user instance for whom the token is being issued.

    Returns:
    str: A JWT token as a string.
    """
    payload = {
        "id": user.id,
        "exp": datetime.utcnow() + timedelta(days=1),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token


def issue_jwt_refresh_token(user: AbstractUser) -> str:
    """
    Generate a JWT refresh token for the specified user.

    This function creates a JWT (JSON Web Token) refresh token for the given user.
    The payload of the token includes the user's ID and an expiration time set to 30 days
    from the current time. The token is encoded using the HS256 algorithm with a
    separate secret key designated for refresh tokens.

    Parameters:
    user (AbstractUser): The Django user instance for whom the refresh token is being issued.

    Returns:
    str: A JWT refresh token as a string.
    """
    refresh_token_payload = {
        "id": user.id,
        "exp": datetime.utcnow() + timedelta(days=30),
    }

    refresh_token = jwt.encode(
        refresh_token_payload, settings.JWT_REFRESH_SECRET_KEY, algorithm="HS256"
    )

    return refresh_token


def issue_jwt_token_from_refresh(user: AbstractUser, refresh_token: str) -> str:
    """
    Generate a new JWT access token using a valid refresh token.

    This function decodes the provided JWT refresh token using a specific secret key
    for refresh tokens. It then validates the user ID encoded in the refresh token
    and issues a new access token with a short expiration period (typically 30 minutes).

    Parameters:
    user (AbstractUser): The Django user instance for whom the access token is being issued.
    refresh_token (str): The JWT refresh token used to validate and issue a new access token.

    Returns:
    str: A newly generated JWT access token as a string.
    """
    payload = jwt.decode(
        refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"]
    )
    user = get_user_model().objects.get(id=payload["id"])

    # Issue new access token
    access_token_payload = {
        "id": user.id,
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    return jwt.encode(access_token_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
