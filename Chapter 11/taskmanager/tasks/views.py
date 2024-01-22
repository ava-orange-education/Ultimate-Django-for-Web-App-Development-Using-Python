from collections import defaultdict
from datetime import date

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from tasks.forms import ContactForm, EpicFormSet, TaskFormWithRedis

from . import services
from .mixins import SprintTaskMixin
from .models import Task


class TaskListView(PermissionRequiredMixin, ListView):
    permission_required = ("tasks.view_task", "tasks.custom_task")

    model = Task
    template_name = "task_list.html"
    context_object_name = "tasks"
    login_url = "accounts/login/"
    raise_exception = True


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = "tasks/task_form.html"
    form_class = TaskFormWithRedis

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.id})

    def form_valid(self, form):
        # Set the creator to the currently logged in user
        form.instance.creator = self.request.user
        return super().form_valid(form)


class TaskUpdateView(PermissionRequiredMixin, SprintTaskMixin, UpdateView):
    permission_required = ("tasks.change_task",)

    model = Task
    template_name = "tasks/task_form.html"
    form_class = TaskFormWithRedis

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.id})

    def has_permission(self):
        # First, check if the user has the general permission to edit tasks
        has_general_permission = super().has_permission()

        # Then check if the user is either the
        # creator or the owner of this task
        task_id = self.kwargs.get("pk")
        task = get_object_or_404(Task, id=task_id)

        is_creator_or_owner = (
            task.creator == self.request.user or task.owner == self.request.user
        )

        # Return True only if both conditions are met
        return has_general_permission and is_creator_or_owner


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:task-list")


@login_required
def task_home(request):
    # Fetch all tasks at once
    tasks = Task.objects.filter(
        status__in=["UNASSIGNED", "IN_PROGRESS", "DONE", "ARCHIVED"]
    )

    # Initialize dictionaries to hold tasks by status
    context = defaultdict(list)

    # Categorize tasks into their respective lists
    for task in tasks:
        if task.status == "UNASSIGNED":
            context["unassigned_tasks"].append(task)
        elif task.status == "IN_PROGRESS":
            context["in_progress_tasks"].append(task)
        elif task.status == "DONE":
            context["done_tasks"].append(task)
        elif task.status == "ARCHIVED":
            context["archived_tasks"].append(task)

    return render(request, "tasks/home.html", context)


@login_required
def task_by_date(request: HttpRequest, by_date: date) -> HttpResponse:
    template = loader.get_template("task_list.html")
    tasks = services.get_task_by_date(by_date)
    context = {"tasks": tasks}  # data to inject into the template
    html = template.render(context, request)
    return HttpResponse(html)


@permission_required("tasks.add_task")
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


@login_required
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


class ContactFormView(FormView):
    template_name = "tasks/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("tasks:contact-success")

    def form_valid(self, form):
        subject = form.cleaned_data.get("subject")
        message = form.cleaned_data.get("message")
        from_email = form.cleaned_data.get("from_email")

        # You can use Django's send_mail function,
        # here is a simple example that sends the message to your email.
        # Please update 'your-email@example.com' with your email and configure
        # the EMAIL settings in your Django settings file
        services.send_contact_email(
            subject, message, from_email, ["your-email@example.com"]
        )

        return super().form_valid(form)


@login_required
def manage_epic_tasks(request, epic_pk):
    epic = services.get_epic_by_id(epic_pk)
    if not epic:
        raise Http404("Epic does not exist")
    if request.method == "POST":
        formset = EpicFormSet(request.POST, queryset=services.get_tasks_for_epic(epic))
        if formset.is_valid():
            tasks = formset.save(commit=False)
            services.save_tasks_for_epic(epic, tasks)
            formset.save_m2m()  # handle many-to-many relations if there are any
            return redirect("tasks:task-list")
    else:
        formset = EpicFormSet(queryset=services.get_tasks_for_epic(epic))

    return render(request, "tasks/manage_epic.html", {"formset": formset, "epic": epic})
