import json

from django.urls import reverse
from pytest_bdd import given, scenario, then, when
from tasks.enums import TaskStatus


@scenario("api.feature", "User creates and claims a task")
def test_task_claiming():
    pass


@given("a user with necessary permissions")
def user_with_permissions(user):
    return user


@when("the user creates a task", target_fixture="create_task")
def create_task(client, jwt_token):
    # Code to create a task via the API client
    response = client.post(
        reverse("api-v1:create_task"),
        json.dumps({"title": "Sample Task", "description": "test description"}),
        content_type="application/json",
        headers=jwt_token,
    )
    assert response.status_code == 201, response.json()
    return response.json()  # Assuming the response includes task details


@when("the user claims the created task")
def claim_task(client, create_task, jwt_token):
    task_id = create_task["id"]
    response = client.patch(
        reverse("api-v1:claim_task_api", kwargs={"task_id": task_id}), headers=jwt_token
    )
    assert response.status_code == 200  # Or whatever your API returns


@then("when the user lists tasks, the created task is shown as claimed")
def list_tasks(client, create_task, jwt_token):
    response = client.get("/api/v1/tasks/", headers=jwt_token)
    assert response.status_code == 200
    tasks = response.json()
    items = tasks["items"]
    assert any(
        [
            task["id"] == create_task["id"]
            for task in items
            if task["status"] == TaskStatus.IN_PROGRESS
        ]
    )
