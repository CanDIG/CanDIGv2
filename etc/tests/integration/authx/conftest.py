import os
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options as ffOptions
from selenium.webdriver.chrome.options import Options as chOptions
import random

# Resources
# Firefox: http://chromedriver.chromium.org/
# Chrome: http://github.com/mozilla/geckodriver/releases

# to run, use `pytest -s -v -n=4` from this directory

@pytest.fixture(scope="session")
def setup(request):

    testname = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]

    headless_mode = (os.environ["HEADLESS_MODE"] == 'True')
    
    if "login" in testname:
        driverenv = os.environ["DRIVER_ENV"]
        common_path = f'{os.getcwd()}/etc/tests/integration/authx'

        if driverenv=="firefox":
            # Firefox
            fireFoxOptions = ffOptions()
            if headless_mode:
                fireFoxOptions.headless = True

            driver = webdriver.Firefox(executable_path=f'{common_path}/geckodriver', options=fireFoxOptions)
        elif driverenv=="chrome":
            # Chrome/Brave
            chromeOptions = chOptions()
            if headless_mode:
                chromeOptions.headless = True
            # Change this to reflect the working machine's setup
            chromeOptions.binary_location = '/usr/bin/brave-browser'

            driver_path = f'{common_path}/chromedriver'
            driver = webdriver.Chrome(options = chromeOptions, executable_path = driver_path)    
        else:
            raise Exception("Missing driver configuration! Please check the Makefile and ensure 'firefox' or 'chrome' is being passed to the run_tests.sh file!")
    
        # Randomly select (within reason) window dimensions and position
        width = random.randint(760,1900)
        height = random.randint(512,1024)
        x = random.randint(0, 500)
        y = random.randint(0, 500)

        driver.set_window_size(width, height)
        driver.set_window_position(x, y, windowHandle ='current')

    else:
        driver=None

    candig_url= os.environ["CANDIG_PUBLIC_URL"]
    candigauth_url= os.environ["KEYCLOAK_PUBLIC_URL"]
    permissions_data_store_url=os.environ['VAULT_SERVICE_PUBLIC_URL']
    #temp
    candig_server_authz_url='http://0.0.0.0:8182/v1/data/permissions/allowed'

    session = request.node
    for item in session.items:
        cls = item.getparent(pytest.Class)
        setattr(cls.obj, "driver", driver)
        setattr(cls.obj, "debug_pause_time_seconds", 0)
        setattr(cls.obj, "candig_url", candig_url)
        setattr(cls.obj, "candigauth_url", candigauth_url)
        setattr(cls.obj, "permissions_data_store_url", permissions_data_store_url)
        setattr(cls.obj, "candig_server_authz_url", candig_server_authz_url)

    yield driver
    if driver != None:
        driver.close()