from django.http.response import JsonResponse
from django.views.generic import View


class JobStatus(View):
    """ Shows all the jobs for this session """

    def get(self, *args, **kwargs):
        return JsonResponse({})
