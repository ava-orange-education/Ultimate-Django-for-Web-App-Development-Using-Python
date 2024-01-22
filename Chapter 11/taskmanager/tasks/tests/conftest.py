import pytest
from accounts.services import issue_jwt_token
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from tasks.models import Task
from tasks.tests.factories import UserFactory


def pytest_bdd_apply_tag(tag, function):
    if tag == "django_db":
        marker = pytest.mark.django_db(transaction=True)
        marker(function)
        return True
    else:
        # Fall back to pytest-bdd's default behavior
        return None


@pytest.fixture
def user() -> AbstractUser:
    user = UserFactory()
    # Ensure the user instance is saved if UserFactory doesn't save it
    user.save()

    # Fetch the content type for the Task model
    content_type = ContentType.objects.get_for_model(Task)

    # Fetch the 'change_task' permission
    change_task_permission = Permission.objects.get(
        codename="change_task",
        content_type=content_type,
    )

    add_task_permission = Permission.objects.get(
        codename="add_tasks",
        content_type=content_type,
    )

    # Assign the permission to the user
    user.user_permissions.add(change_task_permission)
    user.user_permissions.add(add_task_permission)
    return user


@pytest.fixture
def jwt_token(user: AbstractUser) -> dict[str, str]:
    token = issue_jwt_token(user)
    return {"Authorization": f"Bearer {token}"}
