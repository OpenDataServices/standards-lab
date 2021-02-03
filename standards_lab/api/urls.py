from django.urls import path

from api.apps import ApiConfig
import api.views as views

app_name = ApiConfig.name

urlpatterns = [
    path("project/<slug:name>", views.ProjectConfig.as_view(), name="project-config"),
    path(
        "project/<slug:name>/upload",
        views.ProjectUploadFile.as_view(),
        name="project-upload",
    ),
    path(
        "project/<slug:name>/process_start",
        views.ProjectProcessStart.as_view(),
        name="project-process_start",
    ),
    path(
        "project/<slug:name>/process_monitor",
        views.ProjectProcessMonitor.as_view(),
        name="project-process_monitor",
    ),
]
