import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys


@override_settings(ROOT_PROJECTS_DIR="/tmp/standards-lab-test")
class BrowserTests(StaticLiveServerTestCase):
    """ Browser test using latest Chrome/Chromium stable"""

    def __init__(self, *args, **kwargs):
        os.makedirs("/tmp/standards-lab-test", exist_ok=True)
        super(BrowserTests, self).__init__(*args, **kwargs)

    def setUp(self, *args, **kwargs):
        capabilities = DesiredCapabilities.CHROME
        capabilities["loggingPrefs"] = {"browser": "ALL"}

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(
            service_args=["--verbose", "--log-path=selenium.log"],
            desired_capabilities=capabilities,
            chrome_options=chrome_options,
        )
        self.driver.set_page_load_timeout(15)

    def tearDown(self):
        self.driver.quit()

        # remove projects from temporary folder.
        for project in os.listdir("/tmp/standards-lab-test"):
            if project:
                for file in os.listdir("/tmp/standards-lab-test/{}".format(project)):
                    if file:
                        os.remove("/tmp/standards-lab-test/{}/{}".format(project, file))
                os.rmdir("/tmp/standards-lab-test/{}".format(project))
        print("project folder", os.listdir("/tmp/standards-lab-test"))


    def get(self, url):
        self.driver.get("%s%s" % (self.live_server_url, url))

    def create_new_project(self, project_name):
        new_project = self.driver.find_element_by_id("new-project")
        new_project.send_keys(project_name)

        submit = self.driver.find_element_by_id("launch-new-project-link")
        submit.send_keys(Keys.RETURN)

    def test_homepage(self):
        self.get("/")

        self.assertIn("Welcome to Open Standards Lab", self.driver.page_source)

    def test_create_new_project(self):
        self.get("/")
        self.create_new_project("new_project_foo")
        body_text = self.driver.find_element_by_tag_name("body").text

        self.assertIn("Open Standards Lab: new_project_foo", body_text)
        self.assertIn("new_project_foo", self.driver.current_url)

    def test_create_new_project_not_accepted_characters(self):
        self.get("/")

        accepted_chars = self.driver.find_element_by_id("accepted-chars-hint")
        # black
        self.assertEqual("rgba(33, 37, 41, 1)", accepted_chars.value_of_css_property("color"))

        self.create_new_project("new project bar")
        current_url = self.driver.current_url.replace("/#", "")

        # homepage
        self.assertEquals(self.live_server_url, current_url)
        # red
        self.assertEqual("rgba(204, 51, 13, 1)", accepted_chars.value_of_css_property("color"))

    def test_available_projects_homepage(self):
        self.get("/")

        body_text = self.driver.find_element_by_tag_name("body").text

        # "Available Projects" only appear when there are projects.
        self.assertNotIn("Available Projects", body_text)

        self.create_new_project("new_project_bar")
        self.driver.set_page_load_timeout(15)
        self.get("/")
        body_text = self.driver.find_element_by_tag_name("body").text

        self.assertIn("Available Projects", body_text)
        self.assertIn("new_project_bar", body_text)
