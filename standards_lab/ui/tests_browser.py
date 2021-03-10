import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


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

    def get(self, url):
        self.driver.get("%s%s" % (self.live_server_url, url))

    def test_page_loads(self):
        self.get("/")

        self.assertIn("Welcome to Open Standards Lab", self.driver.page_source)
