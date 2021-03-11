from django.test import LiveServerTestCase
from django.urls import URLPattern, reverse_lazy

from api.urls import urlpatterns as api_urls
from ui.urls import urlpatterns as ui_urls
from urls import urlpatterns as root_urls
from utils.project import create_new_project, delete_project


# test urls/views Adapted from YQN by Michael Wood GPLv2
class UrlsTests(LiveServerTestCase):
    def _test_get_url(self, path, namespace=False):
        if type(path) is not URLPattern or path.name is None:
            return

        if namespace:
            path_name = "%s:%s" % (namespace, path.name)
        else:
            path_name = path.name

        if "slug" in path.pattern.describe() and "int" in path.pattern.describe():
            url = reverse_lazy(path_name, args=("test", 1))
        elif "int" in path.pattern.describe():
            url = reverse_lazy(path_name, args=(1,))
        elif "slug" in path.pattern.describe():
            url = reverse_lazy(path_name, args=("test",))
        else:
            url = reverse_lazy(path_name)

        response = self.client.get(url, HTTP_HOST="localhost", follow=True)

        print("Tested %s = %s" % (url, response.status_code))

        self.assertTrue(
            response.status_code == 200,
            "Url %s did not return a 200" % url,
        )

    def setUp(self):
        create_new_project("test", json_format=True)

    def tearDown(self):
        delete_project("test")

    def test_url_responds(self):
        """ Basic test to make sure all urls that accept GET requests return """
        for path in root_urls:
            self._test_get_url(path)

        for path in api_urls:
            if path.name == "project-config":
                self._test_get_url(path, "api")

        for path in ui_urls:
            if path.name != "cove-results":
                self._test_get_url(path, "ui")
