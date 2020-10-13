from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import os
import unittest
import time
import requests
import pytest


@pytest.mark.usefixtures("setup")
class TestGateway():
    
    def test_expired_authn(self):
        expired_key="eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJfS1loak5mQlo1MmRmLWtka3JNSFV4d25qRVRZWk9xZXgwaXRsakFfYnlBIn0.eyJleHAiOjE2MDE5MjE2MjYsImlhdCI6MTYwMTkyMTMyNiwiYXV0aF90aW1lIjoxNjAxOTIxMzI2LCJqdGkiOiJlN2Q5N2U5Zi1hZGIxLTQyMzAtODllMS0zYTQ0MDQyMGY0NTkiLCJpc3MiOiJodHRwOi8va2V5Y2xvYWs6ODA4MS9hdXRoL3JlYWxtcy9jYW5kaWciLCJhdWQiOiJjcV9jYW5kaWciLCJzdWIiOiJmOGQ0ZGI3OC1hM2M2LTQ4MjYtYTI1OS1mZWI0OTBhZGI0NjAiLCJ0eXAiOiJJRCIsImF6cCI6ImNxX2NhbmRpZyIsInNlc3Npb25fc3RhdGUiOiI2MmQ4NzI1ZC0zMGQyLTRhOGEtYTY4Ny0zM2M3Yzg0OGU1NjYiLCJhY3IiOiIxIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJib2IifQ.edM7ivjzyYnxD_AbX_Ch9u3k2xcZCqGUkPBKFG9gxWYPTikKrOGqLKNot1AUDywLStDe-SHjAfDV1sU_e0hp5in65k1h_si8-OIJodLwSz4CK-MphLWyw8G3Mc1vxX0s7LjgVr9ztJ2W3AEcgNwoT1CHMaUNIZGBSVUKc_v5tDl31tQz1W4KQH6P-Ga755ccU6KQqTQ5ii2HTwCb9GSfVJqo0Sq31aYE4L9qwxtmgT7PFwkZEoxt5JcB2eVlSqvnGTbzGZJyNif-qPi4N9bF824jxJxD9X_S79eLe4qRVR3QdrqUEtJ5nC1K3XV8eNKcaVAmpijm9i15xS99_t5uDw"
        headers = {'Authorization': f'Bearer {expired_key}'}

        response = requests.request('GET', self.candig_url, headers=headers)

        assert response.status_code == 401 and b'Key not authorised' in response.content


    def test_jibberish_authn(self):
        jibberish_key="ab123.something.that-doesn't-work"
        headers = {'Authorization': f'Bearer {jibberish_key}'}

        response = requests.request('GET', self.candig_url, headers=headers)

        assert response.status_code == 401 and b'Key not authorised' in response.content
        
