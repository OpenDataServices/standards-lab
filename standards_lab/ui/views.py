from django.http import Http404
from django.views.generic import TemplateView
from utils.project import get_project_config, create_new_project
from django.conf import settings

import os


class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = os.listdir(settings.ROOT_PROJECTS_DIR)
        print(context)
        return context


class ProjectView(TemplateView):
    template_name = "project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["project"] = get_project_config(self.kwargs["project_name"])
            return context
        except FileNotFoundError:
            if self.request.GET.get("new"):
                context["project"] = create_new_project(self.kwargs["project_name"])
                return context

            raise Http404
