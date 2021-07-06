from django.views import View
from django.http import (
    JsonResponse,
    HttpResponse,
    Http404,
    StreamingHttpResponse,
)
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from utils.project import (
    get_project_config,
    delete_project,
    PROJECT_SCHEMA_FILES_DIRECTORY,
    PROJECT_DATA_FILES_DIRECTORY,
)

import json
import os
import mimetypes
import shutil

import processor.cove


def OK(project):
    return JsonResponse(project)


def FAILED(error, status_code=500):
    r = JsonResponse({"status": "FAILED", "error": error})
    r.status_code = status_code
    return r


def save_project(project):
    """Save the current project to the settings file"""

    project["modified"] = timezone.now().isoformat(timespec="minutes")

    with open(os.path.join(project["path"], "settings.json"), "w") as f:
        json.dump(project, f)

    cache.set(project["name"], project)


class BadMimeTypeException(Exception):
    pass


def check_allowed_project_mime_type(file_path):
    """Raises an exception if the mime of file_path is not in the
    settings ALLOWED_PROJECT_MIME_TYPES otherwise returns the mime type"""
    mime = mimetypes.guess_type(file_path, strict=True)[0]
    if mime not in settings.ALLOWED_PROJECT_MIME_TYPES:
        raise BadMimeTypeException

    return mime


def edit_mode(func):
    def inner(self, request, *args, **kwargs):
        if settings.EDIT_MODE:
            return func(self, request, *args, **kwargs)
        else:
            return FAILED("Sorry - Not in edit mode")

    return inner


def project_owners_only(func):
    def inner(self, request, *args, **kwargs):
        if kwargs["name"] in request.session.get("projects_owned", []):
            return func(self, request, *args, **kwargs)
        else:
            return FAILED("Sorry - No permissions", status_code=401)

    return inner


class ProjectConfig(View):
    """GET returns the project config and POST updates the config.
    DELETE deletes the whole project, with no undo."""

    def get(self, request, *args, **kwargs):
        try:
            return OK(get_project_config(kwargs["name"]))
        except FileNotFoundError:
            raise Http404

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

    @edit_mode
    @project_owners_only
    def delete(self, *args, **kwargs):
        delete_project(kwargs["name"])
        self.request.session["projects_owned"].remove(kwargs["name"])
        return OK({})


class ProjectFile(View):
    def get(self, request, *args, **kwargs):
        type_of_file = kwargs["type"]
        project = get_project_config(kwargs["name"])

        if type_of_file == "data":
            # Check user is requesting a data file that exists
            if not kwargs["file_name"] in project.get("dataFiles", []):
                raise Http404
        elif type_of_file == "schema":
            # Check user is requesting a schema file that exists
            if not kwargs["file_name"] in project.get("schemaFiles", []):
                raise Http404
        else:
            # This means the user is trying to request a type we don't recognise
            raise Http404

        file_path = os.path.join(
            project["path"],
            (
                PROJECT_DATA_FILES_DIRECTORY
                if type_of_file == "data"
                else PROJECT_SCHEMA_FILES_DIRECTORY
            ),
            kwargs["file_name"],
        )

        if not os.path.exists(file_path):
            raise Http404

        mime_type = check_allowed_project_mime_type(file_path)

        # ?attach is present so send this as a download to the user
        if request.GET.get("attach"):
            response = StreamingHttpResponse(
                open(file_path, "rb"), content_type=mime_type
            )
            response[
                "Content-Disposition"
            ] = f"attachment; filename=\"{kwargs['file_name']}\""
            return response

        try:
            return HttpResponse(open(file_path, "r"), content_type=mime_type)
        except UnicodeDecodeError:
            # This will happen if the data is in a binary format such as a zip file
            return FAILED(
                "Editing this file type in Standards Lab is not currently supported"
            )

    @edit_mode
    @project_owners_only
    def delete(self, *args, **kwargs):
        project = get_project_config(kwargs["name"])
        upload_type_key = "%sFiles" % kwargs["type"]

        # We only allow these known upload types
        if upload_type_key not in ["schemaFiles", "dataFiles"]:
            return FAILED("Unknown upload type")

        path = os.path.join(
            settings.ROOT_PROJECTS_DIR,
            project["name"],
            (
                PROJECT_DATA_FILES_DIRECTORY
                if upload_type_key == "dataFiles"
                else PROJECT_SCHEMA_FILES_DIRECTORY
            ),
            kwargs["file_name"],
        )

        try:
            os.remove(path)
        except FileNotFoundError:
            pass

        try:
            project[upload_type_key].remove(kwargs["file_name"])

            if (
                upload_type_key == "schemaFiles"
                and project["rootSchema"] == kwargs["file_name"]
            ):
                del project["rootSchema"]

        except (KeyError, ValueError):
            pass

        save_project(project)

        return OK(project)


class ProjectUploadFile(View):
    def post(self, request, *args, **kwargs):
        project = get_project_config(kwargs["name"])

        upload_type_key = "%sFiles" % request.POST.get("uploadType")

        # We only allow these known upload types
        if upload_type_key not in ["schemaFiles", "dataFiles"]:
            return FAILED("Unknown upload type")

        # We don't want to change schema if not in global edit mode
        # TODO or if (this project has edit disabled and we're not the owner)
        if not settings.EDIT_MODE and upload_type_key == "schema":
            return FAILED("Sorry - not in edit mode")

        file_destination_dir = os.path.join(
            project["path"],
            (
                PROJECT_DATA_FILES_DIRECTORY
                if upload_type_key == "dataFiles"
                else PROJECT_SCHEMA_FILES_DIRECTORY
            ),
        )
        if not os.path.exists(file_destination_dir):
            os.mkdir(file_destination_dir)

        file_destination = os.path.join(
            project["path"],
            (
                PROJECT_DATA_FILES_DIRECTORY
                if upload_type_key == "dataFiles"
                else PROJECT_SCHEMA_FILES_DIRECTORY
            ),
            request.FILES["file"].name,
        )

        with open(file_destination, "wb+") as destination_fp:
            for chunk in request.FILES["file"].chunks():
                destination_fp.write(chunk)

        try:
            check_allowed_project_mime_type(file_destination)
        except BadMimeTypeException:
            os.remove(file_destination)
            return FAILED("Unsupported file type")

        # Update the files list, this also makes the file available for the user
        if not project.get(upload_type_key):
            project[upload_type_key] = []

        # If the same file is uploaded we are replacing it so don't append
        if request.FILES["file"].name not in project[upload_type_key]:
            project[upload_type_key].append(request.FILES["file"].name)

        # If we are uploading a schema file and we haven't got a root Schema defined
        # Then set it as the first schema file.
        try:
            if upload_type_key == "schemaFiles" and not project.get("rootSchema"):
                project["rootSchema"] = project["schemaFiles"][0]
        except IndexError:
            pass

        save_project(project)

        return OK(project)


class ProjectProcess(View):
    def get(self, request, *args, **kwargs):
        project = get_project_config(kwargs["name"])

        return OK({"cove": processor.cove.monitor(project)})

    def post(self, request, *args, **kwargs):
        project = get_project_config(kwargs["name"])
        process_params = json.loads(request.body)

        if process_params.get("action") == "start":
            if process_params.get("processName") == "cove":
                return OK(processor.cove.start(project))
            else:
                return FAILED("Unknown 'processName'")
        else:
            return FAILED("Unknown 'action'")
