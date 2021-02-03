# Common context processor
from django.conf import settings


def common(request):
    """ Always have these to our template contexts """

    return {
        "EDIT_MODE": settings.EDIT_MODE,
    }
