import os
import tempfile
import json

from django.test import override_settings

from api.management.commands.migrateprojectstructure import _handle

from utils.project import delete_project
from django.test import Client, TestCase

TEST_ROOT_PROJECTS_DIR = tempfile.mkdtemp()


@override_settings(ROOT_PROJECTS_DIR=TEST_ROOT_PROJECTS_DIR, DEBUG=True)
class MigrateProjectStructureTests(TestCase):
    """Test that migrateprojectstructure works properly by migrating an old project then making sure we can still load resources"""

    def setUp(self, *args, **kwargs):
        # Create project with old structure
        os.makedirs(os.path.join(TEST_ROOT_PROJECTS_DIR, "testproj"), exist_ok=True)
        with open(
            os.path.join(TEST_ROOT_PROJECTS_DIR, "testproj", "data.json"), "w"
        ) as fp:
            json.dump({"sunny": True}, fp)
        with open(
            os.path.join(TEST_ROOT_PROJECTS_DIR, "testproj", "schema.json"), "w"
        ) as fp:
            json.dump({"weather": True}, fp)
        with open(
            os.path.join(TEST_ROOT_PROJECTS_DIR, "testproj", "settings.json"), "w"
        ) as fp:
            json.dump(
                {
                    "dataFiles": ["data.json"],
                    "schemaFiles": ["schema.json"],
                    "path": os.path.join(TEST_ROOT_PROJECTS_DIR, "testproj"),
                },
                fp,
            )

        # Upgrade to new structure
        _handle()

    def tearDown(self):
        # remove projects from temporary folder.
        for project in os.listdir(TEST_ROOT_PROJECTS_DIR):
            delete_project(project) if project else None

    def test_get_data(self):
        c = Client()
        response = c.get("/api/project/testproj/file/data/data.json")
        self.assertEquals(200, response.status_code)
        self.assertIn("sunny", str(response.content))

    def test_get_schema(self):
        c = Client()
        response = c.get("/api/project/testproj/file/schema/schema.json")
        self.assertEquals(200, response.status_code)
        self.assertIn("weather", str(response.content))
