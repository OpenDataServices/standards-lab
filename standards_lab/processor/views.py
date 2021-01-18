from django.http.response import JsonResponse
from django.views.generic import View

import django_rq


class JobStatus(View):
    """ Shows all the jobs for this session """

    def get(self, *args, **kwargs):
        return JsonResponse({})
