from django.views import View
from django.http import JsonResponse
from django.conf import settings

import json


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

        request.session["project"] = project

        return OK()
