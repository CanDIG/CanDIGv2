import os
import sys
import pytest
import requests
from dotenv import dotenv_values
from pathlib import Path

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../..")
sys.path.insert(0, os.path.abspath(f"{REPO_DIR}"))

from settings import get_env
ENV = get_env()

def get_token(username=None, password=None):
    payload = {
        "client_id": ENV["CANDIG_CLIENT_ID"],
        "client_secret": ENV["CANDIG_CLIENT_SECRET"],
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "openid"
    }
    response = requests.post(f"{ENV['KEYCLOAK_PUBLIC_URL']}/auth/realms/candig/protocol/openid-connect/token", data=payload)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        assert False


def test_get_token():
    get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])


def test_tyk():
    headers = {
        'Authorization': f"Bearer {get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])}"
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/{ENV['CANDIG_ENV']['TYK_HTSGET_API_LISTEN_PATH']}/ga4gh/drs/v1/service-info", headers=headers)
    assert response.status_code == 200


def user_datasets():
    return [
        ('CANDIG_SITE_ADMIN', "controlled5"),
        ('CANDIG_NOT_ADMIN', "controlled4"),
    ]

@pytest.mark.parametrize('user, dataset', user_datasets())
def test_opa_datasets(user, dataset):
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    payload = {
        "input": {
            "body": {
              "path": "/katsu/moh/v1/dataset",
              "method": "GET"
            }
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Opa': ENV['OPA_SECRET']
    }

    payload['input']['token'] = get_token(username=username, password=password)
    response = requests.post(f"{ENV['CANDIG_ENV']['OPA_URL']}/v1/data/permissions/datasets", json=payload, headers=headers)
    assert dataset in response.json()['result']


def user_admin():
    return [
        ('CANDIG_SITE_ADMIN', True),
        ('CANDIG_NOT_ADMIN', False),
    ]

@pytest.mark.parametrize('user, is_admin', user_admin())
def test_site_admin(user, is_admin):
    payload = {
        "input": {}
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Opa': ENV['OPA_SECRET']
    }

    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    payload['input']['token'] = get_token(username=username, password=password)
    response = requests.post(f"{ENV['CANDIG_ENV']['OPA_URL']}/v1/data/idp/site_admin", json=payload, headers=headers)
    print(response.json())
    assert ('result' in response.json()) == is_admin


def test_vault():
    site_admin_token = get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])
    headers = {
        'Authorization': f"Bearer {site_admin_token}",
        'Content-Type': 'application/json; charset=utf-8'
    }

    # log in site_admin
    payload = {
        "jwt": site_admin_token,
        "role": "site_admin"
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/vault/v1/auth/jwt/login", json=payload, headers=headers)
    assert 'auth' in response.json()
    client_token = response.json()['auth']['client_token']

    headers["X-Vault-Token"] = client_token
    # delete the test secret, if it exists:
    response = requests.delete(f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers)
    print(response)
    assert response.status_code == 204

    # confirm that the test secret does not yet exist:
    response = requests.get(f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers)
    print(response.json())
    assert response.status_code == 404

    # confirm that this works with the CANDIG_S3_TOKEN too:
    headers["X-Vault-Token"] = ENV['VAULT_S3_TOKEN']
    response = requests.get(f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers)
    print(response.json())
    assert response.status_code == 404

    # set a secret
    payload = {
        "url": "test.com",
        "secret": "test",
        "access": "testtest"
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers, json=payload)
    response = requests.get(f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers)

    print(response.json())
    assert response.json()['data']['url'] == payload['url']


def test_htsget():
    retcode = pytest.main(["lib/htsget-server/htsget_app/tests/test_htsget_server.py"])
    print(retcode)
    assert retcode == pytest.ExitCode.OK


def test_htsget_add_sample_to_dataset():
    # Add NA18537 to dataset controlled4, which is only authorized for user1:
    site_admin_token = get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])
    headers = {
        'Authorization': f"Bearer {site_admin_token}",
        'Content-Type': 'application/json; charset=utf-8'
    }

    payload = {
        "id": "controlled4",
        "drsobjects": [
            "drs://localhost/NA18537"
        ]
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets", headers=headers, json=payload)


def user_access():
    return [
        ('CANDIG_SITE_ADMIN', 'NA18537', True), # site admin can access all data, even if not specified by dataset
        ('CANDIG_NOT_ADMIN', 'NA18537', True), # user1 can access NA18537 as part of controlled4
        ('CANDIG_NOT_ADMIN', 'NA20787', False), # user1 cannot access NA20787
    ]

@pytest.mark.parametrize('user, obj, access', user_access())
def test_htsget_access_data(user, obj, access):
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    headers = {
        'Authorization': f"Bearer {get_token(username=username, password=password)}",
        'Content-Type': 'application/json; charset=utf-8',
    }
    params = {
        'class': 'header'
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/variants/data/{obj}", headers=headers, params=params)
    print(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/v1/variants/data/{obj}")
    assert (response.status_code == 200) == access
