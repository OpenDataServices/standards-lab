import os
import processor.cove
from django.conf import settings
from django.http import Http404
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from utils.project import get_project_config, create_new_project


class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = os.listdir(settings.ROOT_PROJECTS_DIR)
        return context


class ProjectView(TemplateView):
    template_name = "project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["project"] = get_project_config(
                self.kwargs["project_name"], json_format=True
            )
            return context
        except FileNotFoundError:
            # Create new project
            if self.request.GET.get("new"):
                created_by_me, context["project"] = create_new_project(
                    self.kwargs["project_name"], json_format=True
                )

                if created_by_me:
                    # We created this project so add it to our session's project's owned array
                    try:
                        projects_owned = self.request.session["projects_owned"]
                        projects_owned.append(self.kwargs["project_name"])
                        self.request.session["projects_owned"] = projects_owned
                    except KeyError:
                        self.request.session["projects_owned"] = [
                            self.kwargs["project_name"]
                        ]

                return context

        raise Http404


class CoveResults(TemplateView):
    template_name = "cove_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context["project"] = get_project_config(self.kwargs["project_name"])
        except FileNotFoundError:
            return Http404

        # Render the lib-cove-web results snippets
        try:
            context["cove_results_pages"] = []
            cove = processor.cove.monitor(context["project"])

            for file_result in cove:
                snippet_context = cove[file_result]["result"]["context"]
                snippet_context["request"] = {
                    "current_app_base_template": "cove_results_snippet_base.html"
                }

                context["cove_results_pages"].append(
                    {
                        "html": render_to_string(
                            "cove_results_snippet.html", snippet_context
                        ),
                        "file_name": file_result,
                    }
                )

        except KeyError:
            return {"results": "expired"}

        return context
