import json
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


## Keycloak test: can we get an access token for a user?
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


def test_get_token():
    assert get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])


## Tyk test: can we get a response from Tyk for a service?
def test_tyk():
    headers = {
        'Authorization': f"Bearer {get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])}"
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/{ENV['CANDIG_ENV']['TYK_HTSGET_API_LISTEN_PATH']}/ga4gh/drs/v1/service-info", headers=headers)
    assert response.status_code == 200


## Opa tests:

## Can we get the correct dataset response for each user?
def user_datasets():
    return [
        ('CANDIG_SITE_ADMIN', "SYNTHETIC-2"),
        ('CANDIG_NOT_ADMIN', "SYNTHETIC-1"),
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


## Is the user a site admin?
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


## Vault tests: can we add an aws access key and retrieve it, using both the site_admin user and the VAULT_S3_TOKEN?
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


## Htsget tests:

## Run the main htsget test suite
def test_htsget():
    old_val = os.environ.get("TESTENV_URL")
    os.environ['TESTENV_URL'] = f"http://{ENV['CANDIG_ENV']['CANDIG_DOMAIN']}:{ENV['CANDIG_ENV']['HTSGET_APP_PORT']}"
    retcode = pytest.main(["-x", "lib/htsget-server/htsget_app/tests/test_htsget_server.py"])
    if old_val is not None:
        os.environ['TESTENV_URL'] = old_val
    print(retcode)
    assert retcode == pytest.ExitCode.OK


## Can we add samples to Opa-controlled dataset?
def test_htsget_add_sample_to_dataset():
    site_admin_token = get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])
    headers = {
        'Authorization': f"Bearer {site_admin_token}",
        'Content-Type': 'application/json; charset=utf-8'
    }

    # Delete dataset SYNTHETIC-1
    response = requests.delete(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets/SYNTHETIC-1", headers=headers)

    # Add NA18537 and multisample_1 to dataset SYNTHETIC-1, which is only authorized for user1:
    payload = {
        "id": "SYNTHETIC-1",
        "drsobjects": [
            "drs://localhost/NA18537",
            "drs://localhost/multisample_1"
        ]
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets", headers=headers, json=payload)
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets/SYNTHETIC-1", headers=headers)
    print(response.json())
    assert "drs://localhost/multisample_1" in response.json()['drsobjects']
    assert "drs://localhost/multisample_2" not in response.json()['drsobjects']


## Can we access the data when authorized to do so?
def user_access():
    return [
        ('CANDIG_SITE_ADMIN', 'NA18537', True), # site admin can access all data, even if not specified by dataset
        ('CANDIG_NOT_ADMIN', 'NA18537', True), # user1 can access NA18537 as part of SYNTHETIC-1
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


## Does Beacon return the correct level of authorized results?
def beacon_access():
    return [
        ('CANDIG_SITE_ADMIN', 'NC_000021.8:g.5030847T>A', ['multisample_1', 'multisample_2'], ['test']), # site admin can access all data, even if not specified by dataset
        ('CANDIG_NOT_ADMIN', 'NC_000021.8:g.5030847T>A', ['multisample_1'], ['multisample_2', 'test']), # user1 can access NA18537 as part of SYNTHETIC-1
        ('CANDIG_NOT_ADMIN', 'NC_000001.11:g.16565782G>A', [], ['multisample_1', 'multisample_2', 'test']), # user1 cannot access test
    ]

@pytest.mark.parametrize('user, search, can_access, cannot_access', beacon_access())
def test_beacon(user, search, can_access, cannot_access):
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    headers = {
        'Authorization': f"Bearer {get_token(username=username, password=password)}",
        'Content-Type': 'application/json; charset=utf-8',
    }
    params = {
        'allele': search
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/beacon/v2/g_variants", headers=headers, params=params)
    for c in can_access:
        assert c in str(response.json())
    for c in cannot_access:
        assert c not in str(response.json())
    print(response.json())


## Katsu tests:

# set up katsu: ingest the small synthetic dataset from GitHub
def test_setup_katsu():
    test_loc = "https://raw.githubusercontent.com/CanDIG/katsu/develop/chord_metadata_service/mohpackets/data/small_dataset/synthetic_data/Program.json"
    response = requests.get(test_loc)
    assert response.status_code == 200

    site_admin_token = get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])
    headers = {
        'Authorization': f"Bearer {site_admin_token}",
        'Content-Type': 'application/json; charset=utf-8'
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/katsu/moh/v1/ingest/programs", headers=headers, json=response.json())
    print(response.json())
    if response.status_code >= 400:
        errors = response.json()['error during ingest_programs']
        assert "code='unique'" in errors and "program_id" in errors # this means that the error was just that the program IDs already exist
    else:
        assert response.status_code >= 200 and response.status_code < 300

    test_loc = "https://raw.githubusercontent.com/CanDIG/katsu/develop/chord_metadata_service/mohpackets/data/small_dataset/synthetic_data/Donor.json"
    response = requests.get(test_loc)
    assert response.status_code == 200
    response = requests.post(f"{ENV['CANDIG_URL']}/katsu/moh/v1/ingest/donors", headers=headers, json=response.json())
    print(response.json())
    if response.status_code >= 400:
        errors = response.json()['error during ingest_donors']
        assert "code='unique'" in errors and "donor_id" in errors # this means that the error was just that the program IDs already exist
    else:
        assert response.status_code >= 200 and response.status_code < 300


# Can each user only see results from their authorized datasets?
def user_auth_datasets():
    return [
        ('CANDIG_SITE_ADMIN', "SYNTHETIC-2", "SYNTHETIC-1"),
        ('CANDIG_NOT_ADMIN', "SYNTHETIC-1", "SYNTHETIC-2"),
    ]

@pytest.mark.parametrize('user, dataset, not_dataset', user_auth_datasets())
def test_katsu_users(user, dataset, not_dataset):
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f"Bearer {get_token(username=username, password=password)}"
    }

    response = requests.get(f"{ENV['CANDIG_URL']}/katsu/moh/v1/authorized/programs/", headers=headers)
    programs = list(map(lambda x: x['program_id'], response.json()['results']))
    print(programs)
    assert dataset in programs
    assert not_dataset not in programs

    response = requests.get(f"{ENV['CANDIG_URL']}/katsu/moh/v1/authorized/donors/", headers=headers)
    assert len(response.json()) > 0
    print(response.json())
    donors = list(map(lambda x: x['program_id'], response.json()['results']))
    print(donors)
    assert dataset in donors
    assert not_dataset not in donors


## Federation tests:
def test_server_count():
    with open(f"{REPO_DIR}/tmp/federation/servers.json") as fp:
        servers = json.load(fp)
        token = get_token(username=ENV['CANDIG_NOT_ADMIN_USER'], password=ENV['CANDIG_NOT_ADMIN_PASSWORD'])
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json; charset=utf-8'
        }
        response = requests.get(f"{ENV['CANDIG_URL']}/federation/servers", headers=headers)
        print(response.json())
        assert len(response.json()) == len(servers['servers'])
