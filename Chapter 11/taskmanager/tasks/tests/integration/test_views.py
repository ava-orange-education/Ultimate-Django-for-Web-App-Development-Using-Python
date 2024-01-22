import uuid

import pytest
from django.urls import reverse
from tasks.models import Task


@pytest.mark.django_db
def test_valid_form_submission_creates_task(client, django_user_model):
    url = reverse("tasks:task-create")
    user = django_user_model.objects.create_user(
        username="user", password="password", email="test@example.com"
    )
    client.force_login(user)
    get_response = client.get(url)
    csrf_token = get_response.cookies["csrftoken"].value
    unique_title = str(uuid.uuid4())

    data = {
        "title": unique_title,
        "status": "UNASSIGNED",
        "csrfmiddlewaretoken": csrf_token,
        "uuid": uuid.uuid4(),
    }
    assert Task.objects.count() == 0
    response = client.post(url, data)
    assert response.status_code == 302, response.content
    assert Task.objects.count() == 1
    created_task = Task.objects.get(title=unique_title)
    assert created_task.creator == user
