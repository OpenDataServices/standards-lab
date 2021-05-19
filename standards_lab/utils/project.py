from django.conf import settings
from django.core.cache import cache
import os
import json

PROJECT_DATA_FILES_DIRECTORY = "datasets"
PROJECT_SCHEMA_FILES_DIRECTORY = "schemas"


def get_project_config(project_name, json_format=False):
    """Returns the specified project config, optionally in json format"""

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
    """
    Create new project or return config for existing project optionally in json format
    """

    path = os.path.join(settings.ROOT_PROJECTS_DIR, project_name)

    if os.path.exists(path):
        return False, get_project_config(project_name, json_format=json_format)

    os.makedirs(path)

    project = {"name": project_name, "path": path}

    with open(
        os.path.join(settings.ROOT_PROJECTS_DIR, project_name, "settings.json"),
        "w",
    ) as fp:
        json.dump(project, fp)

    os.mkdir(
        os.path.join(
            settings.ROOT_PROJECTS_DIR, project_name, PROJECT_SCHEMA_FILES_DIRECTORY
        )
    )
    os.mkdir(
        os.path.join(
            settings.ROOT_PROJECTS_DIR, project_name, PROJECT_DATA_FILES_DIRECTORY
        )
    )

    cache.set(project_name, project)

    if json_format:
        return True, json.dumps(project)

    return True, project


def delete_project(project_name):
    """
    Delete all the files and directory for a project, and clear it from the cache
    """

    path = os.path.join(settings.ROOT_PROJECTS_DIR, project_name)

    if cache.has_key(project_name):
        cache.delete(project_name)

    # We don't use shutil.rmtree() because
    # when we do https://github.com/OpenDataServices/standards-lab/issues/143 the Django file API has no equivalent,
    # so we may as well set up the idea of looking for files and deleting individually now
    dirs = [
        os.path.join(path, PROJECT_DATA_FILES_DIRECTORY),
        os.path.join(path, PROJECT_SCHEMA_FILES_DIRECTORY),
        path,
    ]
    # Remove files in dirs, then the actial dir
    for dir in dirs:
        if os.path.isdir(dir):
            files = os.listdir(dir)
            for file in files:
                os.remove(os.path.join(dir, file))
            os.rmdir(dir)

    return True


class PathNotFoundForProjectFileException(Exception):
    pass
