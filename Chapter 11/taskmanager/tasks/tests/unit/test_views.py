import json
from unittest.mock import MagicMock, patch

from django.http import HttpResponse, JsonResponse
from tasks import services, views


def test_claim_task_success(rf):
    user_id = 1
    task_id = 100
    request = rf.get(f"/claim_task/{task_id}")
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.is_authenticated = True
    request.user = mock_user

    with patch("tasks.services.claim_task") as mock_claim_task:
        response = views.claim_task_view(request, task_id)

        mock_claim_task.assert_called_once_with(user_id, task_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    # Deserialize JSON response content
    response_data = json.loads(response.content.decode())
    assert response_data == {"message": "Task successfully claimed."}


def test_claim_task_not_exist(rf):
    user_id = 1
    task_id = 101
    request = rf.get(f"/claim_task/{task_id}")

    # Create a mock user with MagicMock
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.is_authenticated = True
    request.user = mock_user

    with patch(
        "tasks.services.claim_task", side_effect=services.Task.DoesNotExist
    ) as mock_claim_task:
        response = views.claim_task_view(request, task_id)

        mock_claim_task.assert_called_once_with(user_id, task_id)
        assert isinstance(response, HttpResponse)
        assert response.status_code == 404
        assert response.content.decode() == "Task does not exist."
