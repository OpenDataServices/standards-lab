from django.urls import path
from django.views.generic.base import TemplateView

import ui.views
from ui.apps import UiConfig

app_name = UiConfig.name

urlpatterns = [
    path("", ui.views.Home.as_view(), name="home"),
    path("p/<slug:project_name>", ui.views.ProjectView.as_view(), name="project"),
    path(
        "p/<slug:project_name>/cove-results",
        ui.views.CoveResults.as_view(),
        name="cove-results",
    ),
    path(
        "p/<slug:project_name>/cove-results2",
        ui.views.CoveResults2.as_view(),
        name="cove-results2",
    ),
    path("about", TemplateView.as_view(template_name="about.html"), name="about"),
]
