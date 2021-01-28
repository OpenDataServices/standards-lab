from django.views import View
from django.http import JsonResponse
from django.conf import settings

import json
import os


def OK(request):
    return JsonResponse(request.session["project"])


def FAILED(error):
    return JsonResponse({"status": "FAILED", "error": error})


def save_project(request, project):
    """ Save the current project to the session and a settings file """

    request.session["project"] = project

    with open(os.path.join(project["path"], "settings.json"), "w") as f:
        json.dump(project, f)


def edit_mode(func):
    def inner(self, request, *args, **kwargs):
        if settings.EDIT_MODE:
            return func(self, request, *args, **kwargs)
        else:
            return FAILED("Sorry - Not in edit mode")

    return inner


class ProjectStatus(View):
    class SessionProjectMissmatch(Exception):
        pass

    def get(self, request, *args, **kwargs):
        try:
            if not request.session["project"]["name"] == kwargs["name"]:
                raise self.SessionProjectMissmatch

            # Load the project from the session
            return OK(request)
        except (KeyError, self.SessionProjectMissmatch):
            # Load the project from the settings file
            try:
                with open(
                    os.path.join(
                        settings.ROOT_PROJECTS_DIR, kwargs["name"], "settings.json"
                    )
                ) as fp:
                    request.session["project"] = json.load(fp)
                    return OK(request)
            except FileNotFoundError:
                return FAILED("No such project")

    @edit_mode
    def post(self, request, *args, **kwargs):
        """ Updates or creates a project """

        project_update = json.loads(request.body)

        try:
            request.session["project"].update(project_update)
            project = request.session["project"]
        except KeyError:
            project = project_update

        if kwargs["name"] != project["name"]:
            return FAILED("Project and session missmatch")

        # Create project working directory if needed
        path = os.path.join(settings.ROOT_PROJECTS_DIR, project["name"])
        if not os.path.exists(path):
            os.makedirs(path)
            project["path"] = path

        save_project(request, project)

        return OK(request)


class ProjectUploadFile(View):
    def post(self, request, *args, **kwargs):
        if not request.session.get("project"):
            return FAILED("No project session started")

        project = request.session["project"]

        if kwargs["name"] != project["name"]:
            return FAILED("Project and session missmatch")

        upload_type_key = "%sFiles" % request.POST.get("uploadType")

        # We only allow these known upload types
        if upload_type_key not in ["schemaFiles", "dataFiles"]:
            return FAILED("Unknown upload type")

        # We don't want to change schema if not in edit mode
        if not settings.EDIT_MODE and upload_type_key == "schema":
            return FAILED("Sorry - not in edit mode")

        with open(
            os.path.join(project["path"], request.FILES["file"].name), "wb+"
        ) as destination:
            for chunk in request.FILES["file"].chunks():
                destination.write(chunk)

        # Update the files list
        if not project.get(upload_type_key):
            project[upload_type_key] = []

        project[upload_type_key].append(request.FILES["file"].name)

        save_project(request, project)

        return OK(request)
