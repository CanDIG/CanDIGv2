from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from selenium.webdriver.common.keys import Keys
import os


def login(driver, username, password):
    # ensure we were redirected
    assert "Log in to candig" in driver.title

    username_input = driver.find_elements_by_xpath("//*[@id='username']")[0]
    password_input = driver.find_elements_by_xpath("//*[@id='password']")[0]

    login_button = driver.find_elements_by_xpath("//*[@id='kc-login']")[0]

    username_input.send_keys(username)
    password_input.send_keys(password)

    login_button.click()




#binary = FirefoxBinary("~/Public/McGill/CanDIGv2/etc/tests/integration/authz")
#driver = webdriver.Firefox(firefox_binary=binary)

# try:
# -- bob
driver = webdriver.Firefox()
driver.get("http://candig.local:8080")

u1 = os.environ["KC_TEST_USER"]
p1 = os.environ["KC_TEST_PW"]
login(driver, u1, p1)

# verify successful login
text=driver.find_elements_by_xpath("/html/body/div[1]/div[1]/a[2]")[0].text
assert "dashboard" in text.lower()

driver.quit()

# -- alice
driver = webdriver.Firefox()
driver.get("http://candig.local:8080")


u2 = os.environ["KC_TEST_USER_TWO"]
p2 = os.environ["KC_TEST_PW_TWO"]
login(driver, u2, p2)

# verify denied login
assert "Access Denied" in driver.find_elements_by_tag_name("body")[0].text

driver.quit()


# except Exception as e:
#     print("here") 
#     #driver.quit()


print("Passed!")