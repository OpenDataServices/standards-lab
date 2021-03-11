from utils.project import get_project_config, create_new_project, delete_project

from django.core.cache import cache
from django.test import TestCase


class TestUtils(TestCase):
    def test_delete_project(self):
        created, new_project = create_new_project("test_project", json_format=True)
        delete_project("test_project")
        try:
            project = get_project_config("test_project")
        except FileNotFoundError:
            project = None

        cached_project = cache.get("test_project")

        self.assertEqual(project, None)
        self.assertEqual(cached_project, None)
