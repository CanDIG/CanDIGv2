import os
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.chrome.options import Options

# Resources
# Firefox: http://chromedriver.chromium.org/
# Chrome: http://github.com/mozilla/geckodriver/releases

# to run, use
# pytest -s -v -n=4

@pytest.fixture(scope="session")
def setup(request):

    # Firefox
    #driver = webdriver.Firefox(executable_path="./geckodriver")

    # Chrome/Brave
    options = Options()
    options.binary_location = '/usr/bin/brave-browser'
    driver_path = './chromedriver'
    driver = webdriver.Chrome(options = options, executable_path = driver_path)

    candig_url= os.environ["CANDIG_PUBLIC_URL"]

    session = request.node
    for item in session.items:
        cls = item.getparent(pytest.Class)
        setattr(cls.obj, "driver", driver)
        setattr(cls.obj, "candig_url", candig_url)
        setattr(cls.obj, "debug_pause_time_seconds", 0)

    yield driver
    driver.close()