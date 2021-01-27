from django.views import View
from django.http import JsonResponse
from django.conf import settings

import json
import os


def OK():
    return JsonResponse({"status": "OK"})


def FAILED(error):
    return JsonResponse({"status": "FAILED", "error": error})


def edit_mode(func):
    def inner(self, request, *args, **kwargs):
        if settings.EDIT_MODE:
            return func(self, request, *args, **kwargs)
        else:
            return FAILED("Sorry - Not in edit mode")

    return inner


class ProjectStatus(View):
    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse(request.session["project"])
        except KeyError:
            return FAILED("No project set")

    @edit_mode
    def post(self, request, *args, **kwargs):
        print(args)
        print(request.body)
        project = json.loads(request.body)

        if not project.get("path"):
            path = os.path.join(settings.ROOT_PROJECTS_DIR, project['name'])
            os.makedirs(path)
            project["path"] = path

            with open(os.path.join(path, "settings.json"), "w") as f:
                json.dump(project, f)

        request.session["project"] = project

        return OK()


class ProjectUploadFile(View):
    @edit_mode
    def post(self, request, *args, **kwargs):
        if not request.session.get("project") or not request.session.get("path"):
            return FAILED("No project started")

        project = request.session.project

        def handle_uploaded_file(f):
            with open(os.join(project["path"], f), 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)