from django.urls import path
from django.views.generic.base import TemplateView

from ui.apps import UiConfig

app_name = UiConfig.name

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("about", TemplateView.as_view(template_name="about.html"), name="about"),
]
