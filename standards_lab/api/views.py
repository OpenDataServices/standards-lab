from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone

from utils.project import get_project_config

import json
import os
import shutil


def OK(project):
    return JsonResponse(project)


def FAILED(error):
    return JsonResponse({"status": "FAILED", "error": error})


def save_project(project):
    """ Save the current project to the settings file """

    project["modified"] = timezone.now().isoformat(timespec="minutes")

    with open(os.path.join(project["path"], "settings.json"), "w") as f:
        json.dump(project, f)


def edit_mode(func):
    def inner(self, request, *args, **kwargs):
        if settings.EDIT_MODE:
            return func(self, request, *args, **kwargs)
        else:
            return FAILED("Sorry - Not in edit mode")

    return inner


class ProjectConfig(View):
    """ GET returns the project config and POST updates the config """

    def get(self, request, *args, **kwargs):
        try:
            return OK(get_project_config(kwargs["name"]))
        except FileNotFoundError:
            return FAILED("No such project")

    @edit_mode
    def post(self, request, *args, **kwargs):

        project = get_project_config(kwargs["name"])
        project_update = json.loads(request.body)

        # If the project name in the url no longer matches the update then
        # We're creating a new version of the project
        if project["name"] != project_update["name"]:
            try:
                new_path = os.path.join(
                    settings.ROOT_PROJECTS_DIR, project_update["name"]
                )
                shutil.copytree(project_update["path"], new_path, dirs_exist_ok=False)
                # Delete the old path to avoid it overwriting the value later on
                del project_update["path"]
                project["path"] = new_path

                # Update that we own this new project version
                try:
                    projects_owned = request.session["projects_owned"]
                    projects_owned.append(project_update["name"])
                    request.session["projects_owned"] = projects_owned
                except KeyError:
                    request.session["projects_owned"] = [project_update["name"]]

            except FileExistsError:
                return FAILED(
                    "Could not save project with this name as it already exists"
                )
            except shutil.Error:
                return FAILED("Project creation error")

        project.update(project_update)
        save_project(project)

        return OK(project)


class ProjectUploadFile(View):
    def post(self, request, *args, **kwargs):
        project = get_project_config(kwargs["name"])

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

        save_project(project)

        return OK(project)
