import os
import time

import chromedriver_autoinstaller
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.project import delete_project

# Ensure the correct version of chromedriver is installed
chromedriver_autoinstaller.install()

ROOT_PROJECTS_DIR_VALUE = os.getenv(
    "ROOT_PROJECTS_DIR_TEST_VALUE", "/tmp/standards-lab-test"
)


@override_settings(ROOT_PROJECTS_DIR=ROOT_PROJECTS_DIR_VALUE, DEBUG=True)
class BrowserTests(StaticLiveServerTestCase):
    """Browser test using latest Chrome/Chromium stable"""

    def __init__(self, *args, **kwargs):
        os.makedirs(ROOT_PROJECTS_DIR_VALUE, exist_ok=True)
        super(BrowserTests, self).__init__(*args, **kwargs)

    def setUp(self, *args, **kwargs):
        capabilities = DesiredCapabilities.CHROME
        capabilities["loggingPrefs"] = {"browser": "ALL"}

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(
            service_args=["--verbose", "--log-path=selenium.log"],
            desired_capabilities=capabilities,
            chrome_options=chrome_options,
        )
        self.driver.set_page_load_timeout(15)

    def tearDown(self):
        self.driver.quit()

        # remove projects from folder.
        for project in os.listdir(ROOT_PROJECTS_DIR_VALUE):
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

        self.assertIn("Open Standards Lab", self.driver.page_source)

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

    def test_exisiting_projects_homepage(self):
        self.get("/")
        target_string = "Existing Project"

        body_text = self.driver.find_element_by_tag_name("body").text

        # "Existing Projects" only appear when there are projects.
        self.assertNotIn(target_string, body_text)

        self.create_new_project("new_project_bar")
        self.driver.set_page_load_timeout(15)
        self.get("/")
        body_text = self.driver.find_element_by_tag_name("body").text

        self.assertIn(target_string, body_text)
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

    def create_new_project_and_upload_data_file(self, project_name, file_name):
        # create new project
        self.get("/")
        self.create_new_project(project_name)

        # upload data file
        data_upload = self.driver.find_element_by_id("form-control-file-data")
        data_upload.send_keys(
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

    def test_schema_json_editor(self):
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

    def test_upload_data_file(self):
        self.create_new_project_and_upload_data_file(
            "new_project_foo", "test_data.json"
        )

        data_files = self.driver.find_element_by_id("current-data-files").text

        self.assertIn("test_data.json", data_files)

    def test_data_file_open_field(self):
        self.create_new_project_and_upload_data_file(
            "new_project_foo", "test_data.json"
        )

        file_open = self.driver.find_element_by_id("data-open").get_attribute("value")

        # by default it is "untitled.json"
        self.assertEqual("untitled.json", file_open)

        # click on data file
        self.driver.find_element_by_xpath(
            "//button[@title='Open test_data.json']"
        ).click()
        file_open = self.driver.find_element_by_id("data-open").get_attribute("value")

        self.assertEqual("test_data.json", file_open)

    def test_data_json_editor(self):
        self.create_new_project_and_upload_data_file(
            "new_project_foo", "test_data.json"
        )

        json_editor = self.driver.find_element_by_class_name(
            "jsoneditor-mode-code"
        ).text

        self.assertNotIn("grants", json_editor)

        # click on data file
        self.driver.find_element_by_xpath(
            "//button[@title='Open test_data.json']"
        ).click()
        json_editor = self.driver.find_element_by_class_name("ace-jsoneditor").text

        self.assertIn("grants", json_editor)

    def start_project_test(self, project_name, schema_file, data_file):
        # create new project
        self.get("/")
        self.create_new_project(project_name)

        # upload schema file
        schema_upload = self.driver.find_element_by_id("form-control-file-schema")
        schema_upload.send_keys(
            os.path.join(os.path.dirname(__file__), "fixtures", schema_file)
        )

        time.sleep(5)

        self.driver.find_element_by_xpath(
            "//button[@title='Open test_schema.json']"
        ).click()
        self.driver.find_element_by_xpath("//button[text()='Save Schema']").click()

        # upload data file
        data_upload = self.driver.find_element_by_id("form-control-file-data")
        data_upload.send_keys(
            os.path.join(os.path.dirname(__file__), "fixtures", data_file)
        )

        time.sleep(5)

        self.driver.find_element_by_xpath(
            "//button[@title='Open test_data.json']"
        ).click()
        self.driver.find_element_by_xpath("//button[text()='Save Data']").click()

        # start test
        self.driver.find_element_by_xpath("//button[text()='Start Test']").click()

        # Tests can take a while to run
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "view-results-details"))
        )

    def test_project_data_test(self):
        self.start_project_test("new_project_foo", "test_schema.json", "test_data.json")

        self.assertIn(
            "Test Results Summary",
            self.driver.find_element_by_id("test-project-data").text,
        )

    def test_view_results_details_link(self):
        self.start_project_test("new_project_foo", "test_schema.json", "test_data.json")

        self.driver.find_element_by_id("view-results-details").click()

        self.driver.switch_to.window(self.driver.window_handles[-1])

        time.sleep(5)

        heading = self.driver.find_element_by_xpath("//h4").text
        self.assertEqual("Structural Errors", heading)
