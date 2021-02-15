from django.conf import settings
from django.core.cache import cache
import os
import json


def get_project_config(project_name, json_format=False):
    """ Returns the specified project config, optionally in json format """

    project = cache.get(project_name)
    if project:
        if json_format:
            return json.dumps(project)

        return project

    with open(
        os.path.join(settings.ROOT_PROJECTS_DIR, project_name, "settings.json")
    ) as fp:
        if json_format:
            return fp.read()

        return json.load(fp)


def create_new_project(project_name, json_format=False):
    """ Create new project or return config for existing project optionally in json format """

    path = os.path.join(settings.ROOT_PROJECTS_DIR, project_name)

    if os.path.exists(path):
        return False, get_project_config(project_name, json_format=json_format)

    os.makedirs(path)

    project = {"name": project_name, "path": path}

    with open(
        os.path.join(settings.ROOT_PROJECTS_DIR, project_name, "settings.json"), "w"
    ) as fp:
        json.dump(project, fp)

    cache.set(project_name, project)

    if json_format:
        return True, json.dumps(project)

    return True, project
