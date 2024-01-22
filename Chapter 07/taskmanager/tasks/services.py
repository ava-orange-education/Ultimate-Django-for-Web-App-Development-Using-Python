import datetime
from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404

from .models import Epic, Sprint, Task


class TaskAlreadyClaimedException(Exception):
    pass


def can_add_task_to_sprint(task, sprint_id):
    """
    Checks if a task can be added to a sprint based on the sprint's date range.
    """
    sprint = get_object_or_404(Sprint, id=sprint_id)
    return sprint.start_date <= task.created_at.date() <= sprint.end_date


def get_task_by_date(by_date: date) -> list[Task]:
    return Task.objects.annotate(date_created=TruncDate("created_at")).filter(
        date_created=by_date
    )


def create_task_and_add_to_sprint(
    task_data: dict[str, str], sprint_id: int, creator: User
) -> Task:
    """
    Create a new task and associate it with a sprint.
    """

    # Fetch the sprint by its ID
    sprint = Sprint.objects.get(id=sprint_id)

    # Get the current date and time
    now = datetime.now()

    # Check if the current date and time is
    # within the sprint's start and end dates
    if not (sprint.start_date <= now <= sprint.end_date):
        raise ValidationError(
            "Cannot add task to sprint: \
                               Current date is not within the \
                               sprint's start and end dates."
        )
    with transaction.atomic():
        # Create the task
        task = Task.objects.create(
            title=task_data["title"],
            description=task_data.get("description", ""),
            status=task_data.get("status", "UNASSIGNED"),
            creator=creator,
        )

        # Add the task to the sprint
        sprint.tasks.add(task)

    return task


@transaction.atomic
def claim_task(user_id, task_id):
    # Lock the task row to prevent other transactions from claiming it simultaneously
    task = Task.objects.select_for_update().get(id=task_id)

    # Check if the task is already claimed
    if task.owner_id:
        raise TaskAlreadyClaimedException("Task is already claimed or completed.")

    # Claim the task
    task.status = "IN_PROGRESS"
    task.owner_id = user_id
    task.save()


def claim_task_optimistically(user_id: int, task_id: int) -> None:
    try:
        # Step 1: Read the task and its version
        task = Task.objects.get(id=task_id)
        original_version = task.version

        # Step 2: Check if the task is already claimed
        if task.owner_id:
            raise ValidationError("Task is already claimed or completed.")

        # Step 3: Claim the task
        task.status = "IN_PROGRESS"
        task.owner_id = user_id

        # Step 4: Save the task and update the version,
        # but only if the version hasn't changed
        updated_rows = Task.objects.filter(id=task_id, version=original_version).update(
            status=task.status,
            owner_id=task.owner_id,
            version=F("version") + 1,  # Increment version field
        )

        # If no rows were updated,
        # that means another transaction changed the task
        if updated_rows == 0:
            raise ValidationError("Task was updated by another transaction.")

    except Task.DoesNotExist:
        raise ValidationError("Task does not exist.")


def send_contact_email(
    subject: str, message: str, from_email: str, to_email: str
) -> None:
    send_mail(subject, message, from_email, [to_email])


def get_epic_by_id(epic_id: int) -> Epic | None:
    return Epic.objects.filter(pk=epic_id).first()


def get_tasks_for_epic(epic: Epic) -> list[Task]:
    return Task.objects.filter(epics=epic)


def save_tasks_for_epic(epic: Epic, tasks: list[Task]) -> None:
    for task in tasks:
        task.save()
        task.epics.add(epic)
