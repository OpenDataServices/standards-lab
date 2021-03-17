import os

import chromedriver_autoinstaller
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

from utils.project import delete_project

# Ensure the correct version of chromedriver is installed
chromedriver_autoinstaller.install()


@override_settings(ROOT_PROJECTS_DIR="/tmp/standards-lab-test", DEBUG=True)
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
            delete_project(project) if project else None

    def get(self, url):
        self.driver.get("%s%s" % (self.live_server_url, url))

    def create_new_project(self, project_name):
        new_project = self.driver.find_element_by_id("new-project")
        new_project.send_keys(project_name)

        submit = self.driver.find_element_by_id("launch-new-project-link")
        submit.send_keys(Keys.RETURN)

    # -----------
    #    HOME
    # -----------

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
        self.assertEqual(
            "rgba(33, 37, 41, 1)", accepted_chars.value_of_css_property("color")
        )

        self.create_new_project("new project bar")
        current_url = self.driver.current_url.replace("/#", "")

        # homepage
        self.assertEquals(self.live_server_url, current_url)
        # red
        self.assertEqual(
            "rgba(204, 51, 13, 1)", accepted_chars.value_of_css_property("color")
        )

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

    # -------------
    #    PROJECT
    # -------------

    def upload_schema_file(self, project_name, file_name):
        # create new project
        self.get("/")
        self.create_new_project(project_name)

        # upload schema file
        schema_upload = self.driver.find_element_by_id("form-control-file-schema")
        schema_upload.send_keys(
            os.path.join(os.path.dirname(__file__), "fixtures", file_name)
        )

    def test_project_settings_project_name_field(self):
        self.get("/")
        self.create_new_project("new_project_foo")

        # project name is pre populated.
        project_name = self.driver.find_element_by_id(
            "project-name-input"
        ).get_attribute("value")

        self.assertEqual("new_project_foo", project_name)

    def test_upload_schema_file(self):
        self.get("/")
        self.create_new_project("new_project_foo")

        schema_upload = self.driver.find_element_by_id("form-control-file-schema")
        schema_upload.send_keys(
            os.path.join(os.path.dirname(__file__), "fixtures", "test_schema.json")
        )
        schema_files = self.driver.find_element_by_id("current-schema-files").text

        self.assertIn("test_schema.json", schema_files)

    def test_schema_file_open_field(self):
        self.upload_schema_file("new_project_foo", "test_schema.json")

        file_open = self.driver.find_element_by_id("schema-open").get_attribute("value")

        # by default it is "schema.json"
        self.assertEqual("schema.json", file_open)

        # click on schema file
        self.driver.find_element_by_xpath(
            "//button[@title='Open test_schema.json']"
        ).click()
        file_open = self.driver.find_element_by_id("schema-open").get_attribute("value")

        self.assertEqual("test_schema.json", file_open)

    def test_schema_json_tree(self):
        self.upload_schema_file("new_project_foo", "test_schema.json")

        json_tree = self.driver.find_element_by_class_name("jsoneditor-tree").text

        self.assertIn("empty object", json_tree)

        # click on schema file
        self.driver.find_element_by_xpath(
            "//button[@title='Open test_schema.json']"
        ).click()
        json_tree = self.driver.find_element_by_class_name("jsoneditor-tree").text

        self.assertIn("Data Standard Schema", json_tree)

    def test_save_schema_file(self):
        """Check that saving the schema file doesn't break anything."""

        self.upload_schema_file("new_project_foo", "test_schema.json")

        # click on schema file
        self.driver.find_element_by_xpath(
            "//button[@title='Open test_schema.json']"
        ).click()

        # click on "Save Schema" button
        self.driver.find_element_by_xpath("//button[text()='Save Schema']").click()
