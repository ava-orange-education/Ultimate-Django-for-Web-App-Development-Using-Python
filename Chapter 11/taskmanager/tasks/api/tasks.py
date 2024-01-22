from http import HTTPStatus

from accounts.api.security import require_permission
from accounts.models import TaskManagerUser
from django.http import Http404, HttpRequest, HttpResponse
from django_ratelimit.decorators import ratelimit
from ninja import Path, Router
from ninja.errors import HttpError
from ninja.pagination import paginate
from tasks import services
from tasks.enums import TaskStatus
from tasks.schemas import CreateSchemaOut, PathDate, TaskSchemaIn, TaskSchemaOut
from tasks.services import TaskAlreadyClaimedException

router = Router(tags=["tasks"])


@router.post("/", response={201: CreateSchemaOut})
@require_permission("tasks.add_tasks")
@ratelimit(key="ip", rate="100/h")
def create_task(request: HttpRequest, task_in: TaskSchemaIn):
    creator = TaskManagerUser.objects.first()
    return services.create_task(creator, **task_in.dict())


@router.get("/", response=list[TaskSchemaOut])
@paginate
def list_tasks(request):
    return services.list_tasks()


@router.get("/{int:task_id}", response=TaskSchemaOut)
def get_task(request: HttpRequest, task_id: int):
    task = services.get_task(task_id)
    if task is None:
        raise Http404("Task not found.")

    return task


@router.put("/{int:task_id}")
def update_task(request: HttpRequest, task_id: int, task_data: TaskSchemaIn):
    services.update_task(task_id=task_id, task_data=task_data.dict())
    return HttpResponse(status=HTTPStatus.NO_CONTENT)


@router.delete("/{int:task_id}")
def delete_task(request: HttpRequest, task_id: int):
    services.delete_task(task_id=task_id)
    return HttpResponse(status=HTTPStatus.NO_CONTENT)


@router.get("/archive/{int:year}/{int:month}/{int:day}", response=list[TaskSchemaOut])
@paginate
def archived_tasks(request, created_at: PathDate = Path(...)):
    return services.search_tasks(
        created_at=created_at, status=TaskStatus.ARCHIVED.value
    )


@router.patch("/{int:task_id}/claim")
@require_permission("tasks.change_task")
def claim_task_api(request: HttpRequest, task_id: int):
    try:
        services.claim_task(request.user.pk, task_id)
        return {"message": "Task successfully claimed"}
    except TaskAlreadyClaimedException:
        # Raise an HttpError with status code 400
        raise HttpError(
            status_code=HTTPStatus.BAD_REQUEST, message="Task already claimed"
        )
