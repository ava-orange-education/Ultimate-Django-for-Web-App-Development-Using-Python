from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class OrganizationUsernameOrEmailBackend(ModelBackend):
    def authenticate(
        self, request, username=None, password=None, organization_id=None, **kwargs
    ):
        UserModel = get_user_model()

        if organization_id is None:
            return None
        try:
            user = UserModel.objects.filter(
                (Q(username__iexact=username) | Q(email__iexact=username))
                & Q(organization_id=organization_id)
            ).first()
        except UserModel.DoesNotExist:
            return None

        if user and user.check_password(password):
            return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
