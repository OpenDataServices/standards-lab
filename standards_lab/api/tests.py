from django.test import LiveServerTestCase
from django.urls import URLPattern, reverse_lazy

from utils.project import create_new_project, delete_project


class ApiTests(LiveServerTestCase):

    def setUp(self):
        create_new_project("test", json_format=True)

    def tearDown(self):
        delete_project("test")

    def test_save_project(self):
        pass

    def test_check_mime_type(self):
        pass

    def test_edit_mode(self):
        pass

    def test_update_project(self):
        pass

    def test_delete_file(self):
        pass

    def test_download_file(self):
        pass

    def test_upload_file(self):
        pass

    def test_process_get(self):
        pass

    def test_process_post(self):
        pass