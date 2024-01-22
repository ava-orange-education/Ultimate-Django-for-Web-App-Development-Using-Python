import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from tasks.models import Task, TaskStatus
from tasks.tests.factories import TaskFactory, UserFactory


@pytest.mark.django_db
def test_successful_claim(client, user, jwt_token):
    task = TaskFactory(status=TaskStatus.UNASSIGNED.value, owner=None)
    response = client.patch(
        reverse("api-v1:claim_task_api", kwargs={"task_id": task.id}), headers=jwt_token
    )
    assert response.status_code == 200
    task.refresh_from_db()
    assert task.status == TaskStatus.IN_PROGRESS.value
    assert task.owner == user


@pytest.mark.django_db
def test_task_not_found(client, user, jwt_token):
    response = client.patch(
        reverse("api-v1:claim_task_api", kwargs={"task_id": 99999}), headers=jwt_token
    )  # Unlikely to exist ID
    assert response.status_code == 404


@pytest.mark.django_db
def test_task_already_claimed(client, user, jwt_token):
    other_user = UserFactory()
    task = TaskFactory(status=TaskStatus.IN_PROGRESS.value, owner=other_user)
    response = client.patch(
        reverse("api-v1:claim_task_api", kwargs={"task_id": task.id}), headers=jwt_token
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_unauthorized_claim_attempt(client, user, jwt_token):
    content_type = ContentType.objects.get_for_model(Task)
    permission = Permission.objects.get(
        codename="change_task", content_type=content_type
    )
    user.user_permissions.remove(permission)
    user.refresh_from_db()
    task = TaskFactory(status=TaskStatus.UNASSIGNED.value, owner=None)
    response = client.patch(
        reverse("api-v1:claim_task_api", kwargs={"task_id": task.id}), headers=jwt_token
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_claim_without_authentication(client):
    task = TaskFactory(status=TaskStatus.UNASSIGNED.value)
    response = client.patch(
        reverse("api-v1:claim_task_api", kwargs={"task_id": task.id})
    )
    assert response.status_code == 401
