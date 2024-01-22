from django.urls import path
from django.views.generic import TemplateView

app_name = "tasks"  # This is for namespacing the URLs
urlpatterns = [
    path("", TemplateView.as_view(template_name="tasks/home.html"), name="home"),
    path("help/", TemplateView.as_view(template_name="tasks/help.html"), name="help"),
]
