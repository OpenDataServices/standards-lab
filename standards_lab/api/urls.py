from django.urls import path

from api.apps import ApiConfig
import api.views as views

app_name = ApiConfig.name

urlpatterns = [
    path("project/", views.ProjectStatus.as_view(), name="project"),
    path("project/<slug:name>", views.ProjectStatus.as_view(), name="project-details"),
    path(
        "project/<slug:name>/upload",
        views.ProjectUploadFile.as_view(),
        name="project-upload",
    ),
]
