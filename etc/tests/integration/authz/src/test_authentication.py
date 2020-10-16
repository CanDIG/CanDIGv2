import os
import unittest
import time
import requests
import pytest
import json
import base64
import pickle

# -- helper functions --
def fix_padding(data):
    missing_padding = len(data) % 4
    if missing_padding:
        data += "=" * (4 - missing_padding)
    return data


def login(driver, username, password):
    # ensure we were redirected
    assert "Log in to candig" in driver.title

    username_input = driver.find_elements_by_xpath("//*[@id='username']")[0]
    password_input = driver.find_elements_by_xpath("//*[@id='password']")[0]

    login_button = driver.find_elements_by_xpath("//*[@id='kc-login']")[0]

    username_input.send_keys(username)
    password_input.send_keys(password)

    login_button.click()

# -- - --

@pytest.mark.usefixtures("setup")
class TestAuthentication():
    
    # TODO;
    # def test_authentication_does_defend_against_hs256_alg_token_tampering_with_login(self):
        
    #     # get public key
    #     public_key_response = requests.request('GET', self.candigauth_url + "/auth/realms/candig")
    #     jsonified = json.loads(public_key_response.content)
    #     public_key = jsonified['public_key']

    #     # open a logged in browser session
    #     self.driver.get(self.candig_url)

    #     # credentials
    #     u1 = os.environ["KC_TEST_USER"]
    #     p1 = os.environ["KC_TEST_PW"]
    #     login(self.driver, u1, p1)

    #     # get session_id, aka: authN token
    #     cookies = self.driver.get_cookies()

    #     old_authN_token = [json.loads(json.dumps(c)) for c in cookies if 'session_id' in json.dumps(c)][0]['value']

    #     authN_header, authN_payload, authN_signature = old_authN_token.split('.')

    #     decoded_authN_header_json = json.loads(base64.b64decode(fix_padding(authN_header)))


    #     # modify the authN token with 'none' alg
    #     decoded_authN_header_json["alg"] = "HS256"
    #     assert decoded_authN_header_json["alg"] == "HS256"
        

    #     new_authN_header = base64.b64encode(bytes(json.dumps(decoded_authN_header_json), 'utf-8')).decode("utf-8").replace('=', '')
    #     # TODO: Resign new token with public key
    #     new_authN_signature = ""

    #     new_authN_token = f"{new_authN_header}.{authN_payload}.{new_authN_signature}"

        
    #     # verify access with old token
    #     cookies = {'session_id': old_authN_token}
    #     response = requests.request('GET', self.candig_url, cookies=cookies)

    #     assert response.status_code == 200 and "Dashboard" in response.content.decode("utf-8")


    #     # show new token doesn't work
    #     cookies = {'session_id': new_authN_token}
    #     response = requests.request('GET', self.candig_url, cookies=cookies)

    #     assert response.status_code == 401 and "Key not authorised" in response.content.decode("utf-8")
        


    def test_authentication_does_defend_against_none_alg_token_tampering_with_login(self):
        # # test none alg attack against RS256
        # get public key
        public_key_response = requests.request('GET', self.candigauth_url + "/auth/realms/candig")
        jsonified = json.loads(public_key_response.content)
        public_key = jsonified['public_key']

        # open a logged in browser session
        self.driver.get(self.candig_url)

        # credentials
        u1 = os.environ["KC_TEST_USER"]
        p1 = os.environ["KC_TEST_PW"]
        login(self.driver, u1, p1)

        # get session_id, aka: authN token
        cookies = self.driver.get_cookies()

        old_authN_token = [json.loads(json.dumps(c)) for c in cookies if 'session_id' in json.dumps(c)][0]['value']

        authN_header, authN_payload, authN_signature = old_authN_token.split('.')

        decoded_authN_header_json = json.loads(base64.b64decode(fix_padding(authN_header)))


        # modify the authN token with 'none' alg
        decoded_authN_header_json["alg"] = "none"
        assert decoded_authN_header_json["alg"] == "none"
        

        new_authN_header = base64.b64encode(bytes(json.dumps(decoded_authN_header_json), 'utf-8')).decode("utf-8").replace('=', '')
        new_authN_signature = "" # empty to accomodate 'none' alg

        new_authN_token = f"{new_authN_header}.{authN_payload}.{new_authN_signature}"

        
        # verify access with old token
        cookies = {'session_id': old_authN_token}
        response = requests.request('GET', self.candig_url, cookies=cookies)

        assert response.status_code == 200 and "Dashboard" in response.content.decode("utf-8")


        # show new token doesn't work
        cookies = {'session_id': new_authN_token}
        response = requests.request('GET', self.candig_url, cookies=cookies)

        assert response.status_code == 401 and "Key not authorised" in response.content.decode("utf-8")
        