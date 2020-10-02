import pytest
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import os

@pytest.fixture(scope="session")
def setup(request):

    driver = webdriver.Firefox(executable_path="./geckodriver")
    # TODO ?? : test both Firefox and Chrome

    candig_url= os.environ["CANDIG_PUBLIC_URL"]

    session = request.node
    for item in session.items:
        cls = item.getparent(pytest.Class)
        setattr(cls.obj, "driver", driver)
        setattr(cls.obj, "candig_url", candig_url)
        setattr(cls.obj, "debug_pause_time_seconds", 2)

    yield driver
    driver.close()