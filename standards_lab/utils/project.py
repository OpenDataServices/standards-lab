from django.conf import settings
import os
import json


def get_project_config(project_name):
    with open(
        os.path.join(settings.ROOT_PROJECTS_DIR, project_name, "settings.json")
    ) as fp:
        return json.load(fp)


def create_new_project(project_name):
    """ Create new project or return config for existing project """

    path = os.path.join(settings.ROOT_PROJECTS_DIR, project_name)

    if os.path.exists(path):
        return get_project_config(project_name)

    os.makedirs(path)

    project = {"name": project_name, "path": path}

    with open(
        os.path.join(settings.ROOT_PROJECTS_DIR, project_name, "settings.json"), "w"
    ) as fp:
        json.dump(project, fp)

    return project
