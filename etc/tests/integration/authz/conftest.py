import pytest
from selenium import webdriver


@pytest.fixture(scope="session")
def setup(request):

    # TODO: use local binary file instead of using PATH
    #binary = FirefoxBinary("~/Public/McGill/CanDIGv2/etc/tests/integration/authz")
    #driver = webdriver.Firefox(firefox_binary=binary)

    # TODO ?? : test both Firefox and Chrome

    driver = webdriver.Firefox()
    session = request.node
    for item in session.items:
        cls = item.getparent(pytest.Class)
        setattr(cls.obj, "driver", driver)
        setattr(cls.obj, "candig_url", "http://candig.local:8080")
        setattr(cls.obj, "debug_pause_time", 0.5)


    yield driver
    driver.close()