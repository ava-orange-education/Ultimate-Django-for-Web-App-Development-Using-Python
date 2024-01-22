from accounts.api.security import ApiTokenAuth, JWTAuth
from accounts.api.views import router as accounts_router
from django.core.exceptions import ObjectDoesNotExist
from ninja import NinjaAPI
from tasks.api.tasks import router as tasks_router

api_v1 = NinjaAPI(version="v1", auth=[ApiTokenAuth(), JWTAuth()])

api_v1.add_router("/tasks/", tasks_router)
api_v1.add_router("/accounts/", accounts_router)


@api_v1.exception_handler(ObjectDoesNotExist)
def on_object_does_not_exist(request, exc):
    return api_v1.create_response(
        request,
        {"message": "Not found"},
        status=404,
    )
