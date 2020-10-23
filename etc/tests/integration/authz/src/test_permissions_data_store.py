from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import os
import unittest
import time
import requests
import pytest
import json


@pytest.mark.usefixtures("setup")
class TestPermissionsDataStore():
    
    def test_can_access_well_known_public_keys(self):
        # call
        response = requests.request('GET', f'{self.permissions_data_store_url}/v1/identity/oidc/.well-known/keys')
        assert response.status_code == 200 

        # access the keys 
        public_keys=json.loads(response.content)['keys']

        # make sure there is only 1
        assert len(public_keys) == 1

        # make sure they're using rsa
        assert public_keys[0]['alg'] == "RS256"


    # def test_can_get_alices_stuff(self):
    #     pass
    

    # def test_can_get_bobs_stuff(self):
    #     pass