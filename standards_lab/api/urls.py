from django.urls import path

from api.apps import ApiConfig
import api.views as views

app_name = ApiConfig.name

urlpatterns = [
    path("project/", views.ProjectStatus.as_view(), name="project"),
    path("project/<str:id>", views.ProjectStatus.as_view(), name="project-details"),
]
