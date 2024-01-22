# Code for tasks/views.py
from datetime import date

from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from . import services
from .mixins import SprintTaskMixin
from .models import Task


class TaskListView(ListView):
    model = Task
    template_name = "task_list.html"
    context_object_name = "tasks"


class TaskDetailView(DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskCreateView(CreateView):
    model = Task
    template_name = "tasks/task_form.html"
    fields = ("title", "description")

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.id})


class TaskUpdateView(SprintTaskMixin, UpdateView):
    model = Task
    template_name = "tasks/task_form.html"
    fields = ("title", "description")

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.id})


class TaskDeleteView(DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:task-list")


def task_home(request):
    return redirect(reverse("tasks:ask-list"))


def task_by_date(request: HttpRequest, by_date: date) -> HttpResponse:
    template = loader.get_template("task_list.html")
    tasks = services.get_task_by_date(by_date)
    context = {"tasks": tasks}  # data to inject into the template
    html = template.render(context, request)
    return HttpResponse(html)


def create_task_on_sprint(request: HttpRequest, sprint_id: int) -> HttpResponseRedirect:
    if request.method == "POST":
        task_data: dict[str, str] = {
            "title": request.POST["title"],
            "description": request.POST.get("description", ""),
            "status": request.POST.get("status", "UNASSIGNED"),
        }
        task = services.create_task_and_add_to_sprint(
            task_data, sprint_id, request.user
        )
        return redirect("tasks:task-detail", task_id=task.id)
    raise Http404("Not found")


def claim_task_view(request, task_id):
    user_id = (
        request.user.id
    )  # Assuming you have access to the user ID from the request

    try:
        services.claim_task(user_id, task_id)
        return JsonResponse({"message": "Task successfully claimed."})
    except Task.DoesNotExist:
        return HttpResponse("Task does not exist.", status=404)
    except services.TaskAlreadyClaimedException:
        return HttpResponse("Task is already claimed or completed.", status=400)


def custom_404(request, exception):
    return render(request, "404.html", {}, status=404)
