from django.core.management.base import BaseCommand
from django.conf import settings
from utils.project import (
    get_project_config,
    PROJECT_SCHEMA_FILES_DIRECTORY,
    PROJECT_DATA_FILES_DIRECTORY,
)
import os


class Command(BaseCommand):
    help = "Migrates files in storage to a new structure"

    def handle(self, *args, **options):
        _handle()


def _handle():
    project_names = os.listdir(settings.ROOT_PROJECTS_DIR)
    for project_name in project_names:
        print("Project: " + project_name)
        project = get_project_config(project_name)
        datas_dir = os.path.join(
            settings.ROOT_PROJECTS_DIR, project_name, PROJECT_DATA_FILES_DIRECTORY
        )
        if not os.path.isdir(datas_dir):
            os.mkdir(datas_dir)
        schemas_dir = os.path.join(
            settings.ROOT_PROJECTS_DIR, project_name, PROJECT_SCHEMA_FILES_DIRECTORY
        )
        if not os.path.isdir(schemas_dir):
            os.mkdir(schemas_dir)
        for data_name in project.get("dataFiles", []):
            print("Data Name: " + data_name)
            data_legacy_path = os.path.join(
                settings.ROOT_PROJECTS_DIR, project_name, data_name
            )
            data_new_path = os.path.join(
                settings.ROOT_PROJECTS_DIR,
                project_name,
                PROJECT_DATA_FILES_DIRECTORY,
                data_name,
            )
            if os.path.exists(data_legacy_path) and not os.path.exists(data_new_path):
                os.rename(data_legacy_path, data_new_path)
        for schema_name in project.get("schemaFiles", []):
            print("Schema Name: " + schema_name)
            schema_legacy_path = os.path.join(
                settings.ROOT_PROJECTS_DIR, project_name, schema_name
            )
            schema_new_path = os.path.join(
                settings.ROOT_PROJECTS_DIR,
                project_name,
                PROJECT_SCHEMA_FILES_DIRECTORY,
                schema_name,
            )
            if os.path.exists(schema_legacy_path) and not os.path.exists(
                schema_new_path
            ):
                os.rename(schema_legacy_path, schema_new_path)
