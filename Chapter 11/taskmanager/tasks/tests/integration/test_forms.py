import uuid

import pytest
from tasks.forms import TaskFormWithRedis


@pytest.mark.django_db
def test_task_form_with_redis():
    # Create unique UUIDs for testing
    uuid1 = uuid.uuid4()

    # Set up form data
    form_data = {
        "title": "Test Task",
        "description": "Test Description",
        "status": "UNASSIGNED",
        "watchers": "watcher1@example.com, watcher2@example.com",
        "uuid": uuid1,
    }

    # First submission with uuid1
    form = TaskFormWithRedis(data=form_data)
    assert form.is_valid(), f"Form should be valid: {form.errors}"

    # Second submission with the same uuid1 should raise a ValidationError
    form_data["uuid"] = uuid1
    form = TaskFormWithRedis(data=form_data)
    assert not form.is_valid()
    assert form.errors == {"uuid": ["This form has already been submitted."]}
