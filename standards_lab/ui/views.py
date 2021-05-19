import os
import subprocess
import processor.cove
from django.conf import settings
from django.http import Http404
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from utils.project import get_project_config, create_new_project, delete_project
from django.shortcuts import render, redirect
from django.views import View


class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = os.listdir(settings.ROOT_PROJECTS_DIR)
        return context


class About(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Not critical if this fails e.g. git not installed
        try:
            context["git_rev"] = subprocess.check_output(
                ["git show --format=format:%h  --no-patch"], shell=True
            ).decode()
        except Exception:
            pass

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
        context["cove_results_pages"] = []
        cove = processor.cove.monitor(context["project"])

        try:

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
            context["error"] = "Results Expired"
        finally:
            return context

        return context


class BaseSysAdmin(View):
    def is_user_sysadmin(self, request):
        # If no password configured, don't allow anyone any access
        if not settings.SYSADMIN_PASSWORD:
            return False

        # Check password
        return request.session.get("sysadminPassword") == settings.SYSADMIN_PASSWORD


class SysAdmin(BaseSysAdmin):
    def get(self, request, *args, **kwargs):
        if not self.is_user_sysadmin(request):
            return redirect("/sysadmin/login")

        return render(request, "sysadmin.html")


class SysAdminLogIn(BaseSysAdmin):
    def get(self, request, *args, **kwargs):
        if self.is_user_sysadmin(request):
            return redirect("ui:sysadmin")

        return render(request, "sysadmin_login.html")

    def post(self, request, *args, **kwargs):
        if self.is_user_sysadmin(request):
            return redirect("ui:sysadmin")

        if request.POST.get("password") == settings.SYSADMIN_PASSWORD:
            request.session["sysadminPassword"] = settings.SYSADMIN_PASSWORD
            return redirect("ui:sysadmin")
        else:
            return redirect("ui:sysadmin_login")


class SysAdminLogOut(BaseSysAdmin):
    def get(self, request, *args, **kwargs):
        request.session["sysadminPassword"] = None
        return redirect("ui:sysadmin_login")


class SysAdminProjects(BaseSysAdmin):
    def get(self, request, *args, **kwargs):
        if not self.is_user_sysadmin(request):
            return redirect("ui:sysadmin_login")

        return render(
            request,
            "sysadmin_projects.html",
            {"projects": os.listdir(settings.ROOT_PROJECTS_DIR)},
        )

    def post(self, request, *args, **kwargs):
        if not self.is_user_sysadmin(request):
            return redirect("ui:sysadmin_login")

        for project_name in os.listdir(settings.ROOT_PROJECTS_DIR):
            if request.POST.get("project_" + project_name) == "1":
                delete_project(project_name)

        return redirect("ui:sysadmin_projects")
