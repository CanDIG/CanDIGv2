import os
import unittest
import time
import requests
import pytest
import json
import base64
import hmac
import hashlib
import random

# References:
# https://medium.com/swlh/hacking-json-web-tokens-jwts-9122efe91e4a

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
    
    def test_authentication_does_defend_against_hs256_alg_token_tampering_with_login(self):
        
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
        # "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJubElzV0M4WEZieWFFS1ctZEgwb251R25EQS10T1FmT0lOZ0l5RkN6WlY0In0.eyJleHAiOjE2MDMzOTIyNTQsImlhdCI6MTYwMzM5MTk1NCwiYXV0aF90aW1lIjoxNjAzMzkxOTU0LCJqdGkiOiI0NTgzMjlhNS1mODE1LTQ1NGItOTNmMC1mMjFhZDYyZDc2NzQiLCJpc3MiOiJodHRwOi8vY2FuZGlnYXV0aC5sb2NhbDo4MDgxL2F1dGgvcmVhbG1zL2NhbmRpZyIsImF1ZCI6ImNxX2NhbmRpZyIsInN1YiI6ImNlMWE5ODkxLTA0NzgtNGZjMS1iYjRjLTc3NjZhMGY4MzIxYyIsInR5cCI6IklEIiwiYXpwIjoiY3FfY2FuZGlnIiwic2Vzc2lvbl9zdGF0ZSI6IjYyZGNkOWVhLWE1ZTMtNGQ3OC1hOWMxLWIxMzcxMDQ4YWFkNyIsImFjciI6IjEiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6ImJvYiJ9.aCyMG_NgcE1PQojMvCKT_eTvZCV0BMhIXID7FdYB8MiBXHVIPHQWsBK12f9tyk1xnPTxjh4wAQPCDQU6HSjpJcYhzK-g4P4s1WVS9Phb_UzbFh0Xx7fyehm9uEQX3QlTRdDTZfC6k-3-TnA0JraqwHpwF927vTPW0ozCXPP8STifeFwACMMsvBTOeDEFfE20tXj_iIOnb_LBf68c_iwi56B_vR4LoKD517VnnKrn_Wgo4hoHGZUH2a2NBWym7dhIeHw1s1fh8qOlGnnxCi5a5eXFOi1ujp1xaQmzPLGPl8tWOBNg4wEL-4hfcB_DaHi5arXrLrQK4Q2EkLjM5nVELw"

        authN_header, authN_payload, authN_signature = old_authN_token.split('.')
        # "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJubElzV0M4WEZieWFFS1ctZEgwb251R25EQS10T1FmT0lOZ0l5RkN6WlY0In0"
        # "eyJleHAiOjE2MDMzOTIyNTQsImlhdCI6MTYwMzM5MTk1NCwiYXV0aF90aW1lIjoxNjAzMzkxOTU0LCJqdGkiOiI0NTgzMjlhNS1mODE1LTQ1NGItOTNmMC1mMjFhZDYyZDc2NzQiLCJpc3MiOiJodHRwOi8vY2FuZGlnYXV0aC5sb2NhbDo4MDgxL2F1dGgvcmVhbG1zL2NhbmRpZyIsImF1ZCI6ImNxX2NhbmRpZyIsInN1YiI6ImNlMWE5ODkxLTA0NzgtNGZjMS1iYjRjLTc3NjZhMGY4MzIxYyIsInR5cCI6IklEIiwiYXpwIjoiY3FfY2FuZGlnIiwic2Vzc2lvbl9zdGF0ZSI6IjYyZGNkOWVhLWE1ZTMtNGQ3OC1hOWMxLWIxMzcxMDQ4YWFkNyIsImFjciI6IjEiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6ImJvYiJ9"
        # "aCyMG_NgcE1PQojMvCKT_eTvZCV0BMhIXID7FdYB8MiBXHVIPHQWsBK12f9tyk1xnPTxjh4wAQPCDQU6HSjpJcYhzK-g4P4s1WVS9Phb_UzbFh0Xx7fyehm9uEQX3QlTRdDTZfC6k-3-TnA0JraqwHpwF927vTPW0ozCXPP8STifeFwACMMsvBTOeDEFfE20tXj_iIOnb_LBf68c_iwi56B_vR4LoKD517VnnKrn_Wgo4hoHGZUH2a2NBWym7dhIeHw1s1fh8qOlGnnxCi5a5eXFOi1ujp1xaQmzPLGPl8tWOBNg4wEL-4hfcB_DaHi5arXrLrQK4Q2EkLjM5nVELw"
        
        
        decoded_authN_header_json = json.loads(base64.b64decode(fix_padding(authN_header)))
        # {'alg': 'RS256', 'typ': 'JWT', 'kid': 'nlIsWC8XFbyaEKW-dH0onuGnDA-tOQfOINgIyFCzZV4'}


        # modify the authN token with 'none' alg
        decoded_authN_header_json["alg"] = "HS256"
        assert decoded_authN_header_json["alg"] == "HS256"        
        # {'alg': 'HS256', 'typ': 'JWT', 'kid': 'nlIsWC8XFbyaEKW-dH0onuGnDA-tOQfOINgIyFCzZV4'}

        new_authN_header = base64.b64encode(bytes(json.dumps(decoded_authN_header_json), 'utf-8')).decode("utf-8").replace('=', '')
        # 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCIsICJraWQiOiAibmxJc1dDOFhGYnlhRUtXLWRIMG9udUduREEtdE9RZk9JTmdJeUZDelpWNCJ9'

        # Resign new token with public key
        new_authN_signature = hmac.new(bytes(public_key,"utf-8"), msg=bytes(f"{new_authN_header}.{authN_payload}", "utf-8"), digestmod=hashlib.sha256).hexdigest()
        # '46215c1759b1899ca56d225730c7bf99c30179a5b05e7df6d308f7526e8a0f53'

        new_authN_token = f"{new_authN_header}.{authN_payload}.{new_authN_signature}"
        # 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCIsICJraWQiOiAibmxJc1dDOFhGYnlhRUtXLWRIMG9udUduREEtdE9RZk9JTmdJeUZDelpWNCJ9.eyJleHAiOjE2MDMzOTIyNTQsImlhdCI6MTYwMzM5MTk1NCwiYXV0aF90aW1lIjoxNjAzMzkxOTU0LCJqdGkiOiI0NTgzMjlhNS1mODE1LTQ1NGItOTNmMC1mMjFhZDYyZDc2NzQiLCJpc3MiOiJodHRwOi8vY2FuZGlnYXV0aC5sb2NhbDo4MDgxL2F1dGgvcmVhbG1zL2NhbmRpZyIsImF1ZCI6ImNxX2NhbmRpZyIsInN1YiI6ImNlMWE5ODkxLTA0NzgtNGZjMS1iYjRjLTc3NjZhMGY4MzIxYyIsInR5cCI6IklEIiwiYXpwIjoiY3FfY2FuZGlnIiwic2Vzc2lvbl9zdGF0ZSI6IjYyZGNkOWVhLWE1ZTMtNGQ3OC1hOWMxLWIxMzcxMDQ4YWFkNyIsImFjciI6IjEiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6ImJvYiJ9.46215c1759b1899ca56d225730c7bf99c30179a5b05e7df6d308f7526e8a0f53'


        # verify access with old token
        cookies = {'session_id': old_authN_token}
        response = requests.request('GET', self.candig_url, cookies=cookies)

        assert response.status_code == 200 and "Dashboard" in response.content.decode("utf-8")


        # show new token doesn't work
        cookies = {'session_id': new_authN_token}
        response = requests.request('GET', self.candig_url, cookies=cookies)

        assert response.status_code == 401 and "Key not authorised" in response.content.decode("utf-8")


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
        
    
    def test_authentication_does_defend_against_non_valid_signature_bruteforce_with_login(self):
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

        
        # verify access with old token
        cookies = {'session_id': old_authN_token}
        response = requests.request('GET', self.candig_url, cookies=cookies)

        assert response.status_code == 200 and "Dashboard" in response.content.decode("utf-8")

        start = time.time()         # the variable that holds the starting time
        elapsed = 0                 # the variable that holds the number of seconds elapsed.
        limit_sec=3

        while elapsed < limit_sec : # only run for the limited number of seconds

            new_authN_signature = "" + ("%032x" % random.getrandbits(random.randint(256,1024)))

            new_authN_token = f"{authN_header}.{authN_payload}.{new_authN_signature}"

            # show new token doesn't work
            cookies = {'session_id': new_authN_token}
            response = requests.request('GET', self.candig_url, cookies=cookies)

            assert response.status_code == 401 and "Key not authorised" in response.content.decode("utf-8")
            
            elapsed = time.time() - start # update the time elapsed


    def test_authentication_does_defend_against_secret_key_bruteforce_with_login(self):

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

        
        # verify access with old token
        cookies = {'session_id': old_authN_token}
        response = requests.request('GET', self.candig_url, cookies=cookies)

        assert response.status_code == 200 and "Dashboard" in response.content.decode("utf-8")

        start = time.time()         # the variable that holds the starting time
        elapsed = 0                 # the variable that holds the number of seconds elapsed.
        limit_sec=3

        while elapsed < limit_sec : # only run for the limited number of seconds

            new_random_secret_key = "" + ("%032x" % random.getrandbits(random.randint(256,1024)))

            # Resign new token with new random key
            new_authN_signature = hmac.new(bytes(new_random_secret_key,"utf-8"), msg=bytes(f"{authN_header}.{authN_payload}", "utf-8"), digestmod=hashlib.sha256).hexdigest()
            # '46215c1759b1899ca56d225730c7bf99c30179a5b05e7df6d308f7526e8a0f53'

            new_authN_token = f"{authN_header}.{authN_payload}.{new_authN_signature}"
            # 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCIsICJraWQiOiAibmxJc1dDOFhGYnlhRUtXLWRIMG9udUduREEtdE9RZk9JTmdJeUZDelpWNCJ9.eyJleHAiOjE2MDMzOTIyNTQsImlhdCI6MTYwMzM5MTk1NCwiYXV0aF90aW1lIjoxNjAzMzkxOTU0LCJqdGkiOiI0NTgzMjlhNS1mODE1LTQ1NGItOTNmMC1mMjFhZDYyZDc2NzQiLCJpc3MiOiJodHRwOi8vY2FuZGlnYXV0aC5sb2NhbDo4MDgxL2F1dGgvcmVhbG1zL2NhbmRpZyIsImF1ZCI6ImNxX2NhbmRpZyIsInN1YiI6ImNlMWE5ODkxLTA0NzgtNGZjMS1iYjRjLTc3NjZhMGY4MzIxYyIsInR5cCI6IklEIiwiYXpwIjoiY3FfY2FuZGlnIiwic2Vzc2lvbl9zdGF0ZSI6IjYyZGNkOWVhLWE1ZTMtNGQ3OC1hOWMxLWIxMzcxMDQ4YWFkNyIsImFjciI6IjEiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6ImJvYiJ9.46215c1759b1899ca56d225730c7bf99c30179a5b05e7df6d308f7526e8a0f53'


            # show new token doesn't work
            cookies = {'session_id': new_authN_token}
            response = requests.request('GET', self.candig_url, cookies=cookies)

            assert response.status_code == 401 and "Key not authorised" in response.content.decode("utf-8")
            
            elapsed = time.time() - start # update the time elapsed

