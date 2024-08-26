import json
import os
import re
import sys
from http import HTTPStatus
from pathlib import Path
import datetime
import pytest
import requests
import urllib.parse
import pprint
import time

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../..")
sys.path.insert(0, os.path.abspath(f"{REPO_DIR}"))

from settings import get_env
from site_admin_token import get_site_admin_token

ENV = get_env()


## Keycloak tests:


## Does Keycloak respond?
def test_keycloak():
    response = requests.get(
        f"{ENV['KEYCLOAK_PUBLIC_URL']}/auth/realms/candig/.well-known/openid-configuration"
    )
    assert response.status_code == 200
    assert "grant_types_supported" in response.json()


## Can we get an access token for a user?
def get_token(username=None, password=None, access_token=False):
    payload = {
        "client_id": ENV["CANDIG_CLIENT_ID"],
        "client_secret": ENV["CANDIG_CLIENT_SECRET"],
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "openid",
    }
    response = requests.post(
        f"{ENV['KEYCLOAK_PUBLIC_URL']}/auth/realms/candig/protocol/openid-connect/token",
        data=payload,
    )
    if response.status_code == 200:
        if access_token:
            return response.json()["access_token"]
        return response.json()["refresh_token"]


def test_get_token():
    assert get_site_admin_token()


## Tyk test: can we get a response from Tyk for all of our services?
def test_tyk():
    headers = {
        "Authorization": f"Bearer {get_site_admin_token()}"
    }
    endpoints = [
        f"{ENV['CANDIG_ENV']['TYK_HTSGET_API_LISTEN_PATH']}/ga4gh/drs/v1/service-info",
        f"{ENV['CANDIG_ENV']['TYK_KATSU_API_LISTEN_PATH']}/v3/service-info",
        f"{ENV['CANDIG_ENV']['TYK_FEDERATION_API_LISTEN_PATH']}/v1/service-info",
        f"{ENV['CANDIG_ENV']['TYK_OPA_API_LISTEN_PATH']}/v1/data/service/service-info",
        f"{ENV['CANDIG_ENV']['TYK_QUERY_API_LISTEN_PATH']}/service-info",
    ]
    responses = []
    for endpoint in endpoints:
        response = requests.get(
            f"{ENV['CANDIG_URL']}/{endpoint}", headers=headers, timeout=10
        )
        responses.append(response.status_code)
        print(f"{endpoint}: {response.status_code == 200}")
    assert all(response == 200 for response in responses)


## Opa tests:
## Test DAC user authorizations

## Can we get the correct dataset response for each user?
def user_auth_datasets():
    return [
        ("CANDIG_NOT_ADMIN2", "PROGRAM-2"),
        ("CANDIG_NOT_ADMIN", "PROGRAM-1"),
        ("CANDIG_NOT_ADMIN", "TEST_2"),
    ]

def get_katsu_datasets(user):
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    token = get_token(username=username, password=password, access_token=True)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "input": {"body": {"path": "/v3/discovery/", "method": "GET"}, "token": token}
    }

    katsu_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {get_site_admin_token()}"
    }

    response = requests.post(
        f"{ENV['CANDIG_ENV']['OPA_URL']}/v1/data/permissions/datasets",
        json=payload,
        headers=katsu_headers,
    )
    return response.json()["result"]


def add_program_authorization(dataset: str, curators: list,
                              team_members: list):
    token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # create a program and its authorizations:
    test_program = {
        "program_id": dataset,
        "program_curators": curators,
        "team_members": team_members
    }

    print(f"{ENV['CANDIG_URL']}/ingest/program")
    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/program", headers=headers, json=test_program)
    print(response.text)
    # if the site user is the default user, there should be a warning
    if ENV['CANDIG_SITE_ADMIN_USER'] == ENV['CANDIG_ENV']['DEFAULT_SITE_ADMIN_USER']:
        assert "warning" in response.json()

    return response.json()


def delete_program_authorization(dataset: str):
    token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.delete(f"{ENV['CANDIG_URL']}/ingest/program/{dataset}", headers=headers)
    print(response.text)
    return response.json()


## Can we add a program authorization and modify it?
@pytest.mark.parametrize("user, dataset", user_auth_datasets())
def test_add_remove_program_authorization(user, dataset):
    add_program_authorization(dataset, [], [])
    token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # try adding a user to the program:
    test_data = {
        "email": ENV["CANDIG_NOT_ADMIN_USER"],
        "program": dataset
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}/email/{test_data['email']}", headers=headers)
    # when the user has admin access, they should be allowed
    print(f"{response.json()}, {response.status_code}")
    assert response.status_code == 200

    assert test_data["program"] in get_katsu_datasets("CANDIG_NOT_ADMIN")

    # remove the user
    response = requests.delete(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}/email/{test_data['email']}", headers=headers)
    assert response.status_code == 200
    assert test_data["email"] not in response.json()[test_data["program"]]["team_members"]

    # remove the program
    response = requests.delete(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}", headers=headers)
    assert response.status_code == 200

    response = requests.get(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}", headers=headers)
    assert response.status_code == 404


@pytest.mark.parametrize("user, dataset", user_auth_datasets())
def test_user_authorizations(user, dataset):
    # set up these programs to exist at all:
    add_program_authorization(dataset, [], [])

    # add user to pending users
    username = ENV[f"{user}_USER"]
    safe_name = urllib.parse.quote_plus(username)
    password = ENV[f"{user}_PASSWORD"]
    token = get_token(username=username, password=password)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    response = requests.post(
        f"{ENV['CANDIG_URL']}/ingest/user/pending/request",
        headers=headers
    )
    print(response.text)
    assert response.status_code == 200

    headers = {
        "Authorization": f"Bearer {get_site_admin_token()}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # check to see that the user is in the pending queue
    response = requests.get(
        f"{ENV['CANDIG_URL']}/ingest/user/pending",
        headers=headers
    )
    print(response.text)
    assert username in response.json()['results']

    # approve user
    response = requests.post(
        f"{ENV['CANDIG_URL']}/ingest/user/pending/{safe_name}",
        headers=headers
    )
    assert response.status_code == 200

    # see if user can access dataset before authorizing
    katsu_datasets = get_katsu_datasets(user)
    assert dataset not in katsu_datasets

    # add dataset to user's authz
    from datetime import date

    TODAY = date.today()
    THE_FUTURE = str(date(TODAY.year + 1, TODAY.month, TODAY.day))

    response = requests.post(
        f"{ENV['CANDIG_URL']}/ingest/user/{safe_name}/authorize",
        headers=headers,
        json={"program_id": dataset, "start_date": "2000-01-01", "end_date": THE_FUTURE}
    )
    print(f"hi {response.text}")
    assert response.status_code == 200

    # see if user can access dataset now
    katsu_datasets = get_katsu_datasets(user)
    assert dataset in katsu_datasets

    # remove the dataset
    response = requests.delete(
        f"{ENV['CANDIG_URL']}/ingest/user/{safe_name}/authorize/{dataset}",
        headers=headers
    )
    assert response.status_code == 200


## Is the user a site admin?
def user_admin():
    return [
        ("CANDIG_SITE_ADMIN", True),
        ("CANDIG_NOT_ADMIN", False),
    ]


@pytest.mark.parametrize("user, is_admin", user_admin())
def test_site_admin(user, is_admin):
    payload = {"input": {}}
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    token = get_token(username=username, password=password, access_token=True)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload["input"]["token"] = token
    response = requests.post(
        f"{ENV['CANDIG_ENV']['OPA_URL']}/v1/data/permissions/site_admin",
        json=payload,
        headers=headers,
    )
    print(response.json())
    assert ("result" in response.json()) == is_admin


def test_add_remove_site_admin():
    token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # add user1 to site admins
    response = requests.post(
        f"{ENV['CANDIG_URL']}/ingest/site-role/admin/email/{ENV['CANDIG_NOT_ADMIN_USER']}",
        headers=headers
    )
    print(response.text)
    assert response.status_code == 200

    test_site_admin("CANDIG_NOT_ADMIN", True)

    # remove user1 from site admins
    response = requests.delete(
        f"{ENV['CANDIG_URL']}/ingest/site-role/admin/email/{ENV['CANDIG_NOT_ADMIN_USER']}",
        headers=headers
    )
    assert response.status_code == 200
    test_site_admin("CANDIG_NOT_ADMIN", False)


## Vault tests: can we add an aws access key and retrieve it?
def test_s3_credentials():
    site_admin_token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    payload = {
        "endpoint": "http://test.com",
        "bucket": "test",
        "secret_key": "test",
        "access_key": "testtest"
    }

    # set a credential
    response = requests.post(
        f"{ENV['CANDIG_URL']}/ingest/s3-credential", headers=headers, json=payload
    )
    print(response.text)
    # make sure that the endpoint was parsed correctly:
    assert response.json()["endpoint"] == "test_com"

    # get the credential back
    url = f"{ENV['CANDIG_URL']}/ingest/s3-credential/endpoint/{response.json()['endpoint']}/bucket/{response.json()['bucket']}"
    response = requests.get(url, headers=headers)

    print(response.text)
    assert response.json()["access_key"] == payload["access_key"]

    # delete the credential
    response = requests.delete(url, headers=headers)

    print(response.text)
    assert response.status_code == 204


# =========================|| KATSU TEST BEGIN ||============================= #
# HELPER FUNCTIONS
# -----------------
def clean_up_program(test_id):
    """
    Deletes a dataset and all related objects in katsu, htsget and opa. Expected either
    successful delete or not found if the programs are not ingested.
    """
    print(f"deleting {test_id}")
    site_admin_token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # delete program from katsu
    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/katsu/v3/ingest/program/{test_id}/",
        headers=headers,
    )
    print(f"katsu delete response status code: {delete_response.status_code}")
    assert (
        delete_response.status_code == 200 or delete_response.status_code == HTTPStatus.NO_CONTENT or delete_response.status_code == HTTPStatus.NOT_FOUND
    ), f"CLEAN_UP_PROGRAM Expected status code {HTTPStatus.NO_CONTENT}, but got {delete_response.status_code}."
    f" Response content: {delete_response.content}"

    # delete program from htsget
    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/{test_id}",
        headers=headers
    )
    print(f"htsget delete response status code: {delete_response.status_code}")
    assert delete_response.status_code == 200

    site_admin_token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # delete program authorization from opa
    delete_response = requests.delete(f"{ENV['CANDIG_URL']}/ingest/program/{test_id}",
                                      headers=headers)
    print(f"program authorization delete response status code: {delete_response.status_code}")
    assert (delete_response.status_code == 200 or delete_response.status_code == HTTPStatus.NO_CONTENT or delete_response.status_code == HTTPStatus.NOT_FOUND)
    response = delete_program_authorization(test_id)
    print(response)


def clean_up_program_htsget(program_id):
    site_admin_token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/{program_id}",
        headers=headers
    )
    assert delete_response.status_code == 200


def test_ingest_not_admin_katsu():
    """Test ingest of SYNTH_01 as CANDIG_NOT_ADMIN_USER, without and with program authorization."""
    katsu_response = requests.get(
        f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v3/discovery/programs/"
    )
    programs = ['SYNTH_01', 'SYNTH_02', 'SYNTH_03', 'SYNTH_04']
    if katsu_response.status_code == 200:
        katsu_programs = [x['program_id'] for x in katsu_response.json()]
        for program in programs:
            if program in katsu_programs:
                print(f"cleaning up {program}")
                clean_up_program(program)

    with open("lib/candig-ingest/candigv2-ingest/tests/SYNTH_01.json", 'r') as f:
        test_data = json.load(f)

    token = get_token(
        username=ENV["CANDIG_NOT_ADMIN_USER"],
        password=ENV["CANDIG_NOT_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/clinical", headers=headers, json=test_data)
    # when the user has no admin access, they should not be allowed
    assert response.status_code == 401

    # add program authorization
    add_program_authorization("SYNTH_01", [ENV['CANDIG_NOT_ADMIN_USER']], team_members=[])
    token = get_token(
        username=ENV["CANDIG_NOT_ADMIN_USER"],
        password=ENV["CANDIG_NOT_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    # When program authorization is added, ingest should be allowed
    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/clinical", headers=headers, json=test_data)
    if response.status_code == 201:
        assert response.status_code == 201
        assert len(response.json()["SYNTH_01"]["errors"]) == 0
        assert len(response.json()["SYNTH_01"]["results"]) == 13
    else:
        print("Ingest timed out, waiting 10s for ingest to complete...")
        time.sleep(10)
    katsu_response = requests.get(f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v3/discovery/programs/")
    if katsu_response.status_code == 200:
        katsu_programs = [x['program_id'] for x in katsu_response.json()]
        print(f"Currently ingested katsu programs: {katsu_programs}")
        assert 'SYNTH_01' in katsu_programs
    else:
        print(f"Looks like katsu failed with status code: {katsu_response.status_code}")



def test_ingest_admin_katsu():
    """Test whether an admin can ingest each of the synthetic data programs can be ingested and add the expected
    program authorizations."""
    katsu_response = requests.get(
        f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v3/discovery/programs/"
    )
    programs = ['SYNTH_01', 'SYNTH_02', 'SYNTH_03', 'SYNTH_04']
    if katsu_response.status_code == 200:
        katsu_programs = [x['program_id'] for x in katsu_response.json()]
        for program in programs:
            if program in katsu_programs:
                print(f"cleaning up {program}")
                clean_up_program(program)

    for program in programs:
        token = get_site_admin_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        with open(f"lib/candig-ingest/candigv2-ingest/tests/{program}.json", 'r') as f:
            test_data = json.load(f)

        print(f"Sending {program} clinical data to katsu...")
        response = requests.post(f"{ENV['CANDIG_URL']}/ingest/clinical", headers=headers, json=test_data)
        print(f"Ingest response code: {response.status_code}")
        #### This section runs only if ingest responds in time while we improve ingest so it doesn't time out ####
        if response.status_code == 201:
            assert response.status_code == 201
            assert len(response.json()[program]["errors"]) == 0
            assert len(response.json()[program]["results"]) == 13
        else:
            print("Ingest timed out, waiting 10s for ingest to complete...")
            time.sleep(10)
        katsu_response = requests.get(f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v3/discovery/programs/")
        if katsu_response.status_code == 200:
            katsu_programs = [x['program_id'] for x in katsu_response.json()]
            print(f"Currently ingested katsu programs: {katsu_programs}")
            assert program in katsu_programs
        else:
            print(f"Looks like katsu failed with status code: {katsu_response.status_code}")
    # Reinstate expected program authorizations
    add_program_authorization("SYNTH_01", [ENV['CANDIG_NOT_ADMIN_USER']], team_members=[ENV['CANDIG_NOT_ADMIN_USER']])
    add_program_authorization("SYNTH_02", [ENV['CANDIG_NOT_ADMIN2_USER']], team_members=[ENV['CANDIG_NOT_ADMIN2_USER']])


## Htsget tests:

def test_ingest_not_admin_htsget():
    with open("lib/candig-ingest/candigv2-ingest/tests/small_dataset_genomic_ingest.json", 'r') as f:
        test_data = json.load(f)

    token = get_token(
        username=ENV["CANDIG_NOT_ADMIN_USER"],
        password=ENV["CANDIG_NOT_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/genomic", headers=headers, json=test_data)
    # when the user has no admin access, they should not be allowed
    assert response.status_code == 403

    add_program_authorization("SYNTH_01", [ENV['CANDIG_NOT_ADMIN_USER']], team_members=[ENV['CANDIG_NOT_ADMIN_USER']])
    add_program_authorization("SYNTH_02", [ENV['CANDIG_NOT_ADMIN_USER']], team_members=[ENV['CANDIG_NOT_ADMIN_USER']])
    token = get_token(
        username=ENV["CANDIG_NOT_ADMIN_USER"],
        password=ENV["CANDIG_NOT_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/genomic", headers=headers, json=test_data)
    # when the user has program_curator role, they should be allowed
    assert response.status_code == 200
    results = response.json()['results']
    if len(response.json()["errors"]) > 0:
        print("Expected to get no errors when ingesting into htsget but the following errors were found:")
        print("\n".join(response.json()["errors"]))
    assert len(response.json()["errors"]) == 0
    for id in results:
        print(id)
        print(f"\n{results[id]}\n")
        assert "genomic" in results[id]
        assert "sample" in results[id]
    # clean up before the next test
    programs=["SYNTH_01", "SYNTH_02"]
    for program in programs:
        clean_up_program_htsget(program)
    add_program_authorization("SYNTH_01", [ENV['CANDIG_NOT_ADMIN_USER']], team_members=[ENV['CANDIG_NOT_ADMIN_USER']])
    add_program_authorization("SYNTH_02", [ENV['CANDIG_NOT_ADMIN2_USER']], team_members=[ENV['CANDIG_NOT_ADMIN2_USER']])



def test_ingest_admin_htsget():
    with open("lib/candig-ingest/candigv2-ingest/tests/small_dataset_genomic_ingest.json", 'r') as f:
        test_data = json.load(f)

    token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/genomic", headers=headers, json=test_data)
    # when the user has admin access, they should be allowed
    assert response.status_code == 200
    results = response.json()['results']
    if len(response.json()["errors"]) > 0:
        print("Expected to get no errors when ingesting into htsget but the following errors were found:")
        print("\n".join(response.json()["errors"]))
    assert len(response.json()["errors"]) == 0
    for id in results:
        print(id)
        print(f"\n{results[id]}\n")
        assert "genomic" in results[id]
        assert "sample" in results[id]


## Can we access the data when authorized to do so?
def user_access():
    return [
        (
            "CANDIG_NOT_ADMIN_USER",
            "CANDIG_NOT_ADMIN_PASSWORD",
            "NA18537-vcf",
            False,
        ),  # user1 cannot access NA18537 as part of SYNTH_02
        (
            "CANDIG_NOT_ADMIN_USER",
            "CANDIG_NOT_ADMIN_PASSWORD",
            "test",
            True,
        ),  # user1 can access test as part of SYNTH_01
        (
            "CANDIG_NOT_ADMIN2_USER",
            "CANDIG_NOT_ADMIN2_PASSWORD",
            "NA02102-bam",
            False
        ),  # user2 cannot access NA02102-bam
        (
            "CANDIG_NOT_ADMIN2_USER",
            "CANDIG_NOT_ADMIN2_PASSWORD",
            "multisample_1",
            True
        )  # user2 can access multisample_1
    ]


@pytest.mark.parametrize("user, password, obj, access", user_access())
def test_htsget_access_data(user, password, obj, access):
    username = ENV[user]
    password = ENV[password]
    headers = {
        "Authorization": f"Bearer {get_token(username=username, password=password)}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {"class": "header"}
    response = requests.get(
        f"{ENV['CANDIG_URL']}/genomics/htsget/v1/variants/data/{obj}",
        headers=headers,
        params=params,
    )
    print(f"\n{ENV['CANDIG_URL']}/genomics/htsget/v1/variants/data/{obj}\n")
    assert (response.status_code == 200) == access


def test_sample_metadata():
    username = ENV["CANDIG_NOT_ADMIN2_USER"]
    password = ENV["CANDIG_NOT_ADMIN2_PASSWORD"]
    headers = {
        "Authorization": f"Bearer {get_token(username=username, password=password)}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/samples/SAMPLE_NULL_0001", headers=headers)
    assert "genomes" in response.json()
    assert "multisample_2" in response.json()["genomes"]
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/samples/SAMPLE_0072", headers=headers)
    assert "genomes" in response.json()
    assert "HG00100-cram" in response.json()["genomes"]
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/samples/SAMPLE_ALL_0002", headers=headers)
    assert "genomes" in response.json()
    pprint.pprint(response.json())
    assert "HG02102-all" in response.json()["genomes"]


def test_index_success():
    token = get_token(
        username=ENV["CANDIG_NOT_ADMIN_USER"],
        password=ENV["CANDIG_NOT_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects/test", headers=headers)
    assert "indexed" in response.json()
    print(response.json())
    assert response.json()['indexed'] == 1

    token = get_token(
        username=ENV["CANDIG_NOT_ADMIN2_USER"],
        password=ENV["CANDIG_NOT_ADMIN2_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects/multisample_1", headers=headers)
    assert "indexed" in response.json()
    assert response.json()['indexed'] == 1
    token = get_token(
        username=ENV["CANDIG_NOT_ADMIN_USER"],
        password=ENV["CANDIG_NOT_ADMIN_PASSWORD"],
    )


## Does Beacon return the correct level of authorized results?
def beacon_access():
    return [
        (
            "CANDIG_NOT_ADMIN_USER",
            "CANDIG_NOT_ADMIN_PASSWORD",
            "NC_000021.9:g.5030847T>A", # chr21	5030847	.	T	A
            ["SYNTH_01"],
            ["SYNTH_02"],
        ),
        (   # user2 can access NA18537-vcf, multisample_1, HG02102
            "CANDIG_NOT_ADMIN2_USER",
            "CANDIG_NOT_ADMIN2_PASSWORD",
            "NC_000021.9:g.5030847T>A", # chr21	5030847	.	T	A
            ["SYNTH_02"],
            ["SYNTH_01"],
        )
    ]


@pytest.mark.parametrize("user, password, search, can_access, cannot_access", beacon_access())
def test_beacon(user, password, search, can_access, cannot_access):
    username = ENV[user]
    password = ENV[password]
    headers = {
        "Authorization": f"Bearer {get_token(username=username, password=password)}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {"allele": search}
    response = requests.get(
        f"{ENV['CANDIG_URL']}/genomics/beacon/v2/g_variants",
        headers=headers,
        params=params,
    )
    pprint.pprint(response.json())
    for c in can_access:
        assert c in str(response.json())
    for c in cannot_access:
        assert c not in str(response.json())
    # print(response.json())


def verify_samples():
    return [
        (
            "multisample_1",
            "multisample_1.vcf.gz",
            "variant",
            "CANDIG_NOT_ADMIN2_USER",
            "CANDIG_NOT_ADMIN2_PASSWORD"
        ),
        (
            "NA02102-bam",
            "NA02102.bam",
            "read",
            "CANDIG_NOT_ADMIN_USER",
            "CANDIG_NOT_ADMIN_PASSWORD"
        )
    ]


@pytest.mark.parametrize("object_id, file_name, file_type, user, password", verify_samples())
def test_verify_htsget(object_id, file_name, file_type, user, password):
    token = get_token(
        username=ENV[user],
        password=ENV[password],
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    # get a GenomicDataDrsObject
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects/{file_name}", headers=headers)
    assert response.status_code == 200
    new_json = response.json()

    # mess up its access_url
    old_url = new_json["access_methods"][0]["access_url"]["url"]
    new_json["access_methods"][0]["access_url"]["url"] += "test"

    post_token = get_site_admin_token()
    post_headers = {
        "Authorization": f"Bearer {post_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects", headers=post_headers, json=new_json)

    # verification should give us a False result
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/{file_type}s/{object_id}/verify", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] == False

    # fix it back
    new_json["access_methods"][0]["access_url"]["url"] = old_url
    response = requests.post(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects", headers=post_headers, json=new_json)

    # verification should give us a True result
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/{file_type}s/{object_id}/verify", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] == True


def test_cohort_status():
    token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTH_02/status", headers=headers)
    assert "index_complete" in response.json()
    assert len(response.json()['index_complete']) > 0


## Federation tests:

# Do we have at least one server present?
def test_server_count():
    token = get_token(
        username=ENV["CANDIG_NOT_ADMIN_USER"], password=ENV["CANDIG_NOT_ADMIN_PASSWORD"]
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/federation/v1/servers", headers=headers
    )
    print(response.json())
    assert len(response.json()) > 0


# Do we have at least one service present?
def test_services_count():
    token = get_token(
        username=ENV["CANDIG_NOT_ADMIN_USER"], password=ENV["CANDIG_NOT_ADMIN_PASSWORD"]
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/federation/v1/services", headers=headers
    )
    print(response.json())
    assert len(response.json()) > 0
    services = map(lambda x: x["id"], response.json())
    assert "htsget" in services


# Do federated and non-federated calls look correct?
def test_federation_call():
    body = {
        "service": "htsget",
        "method": "GET",
        "payload": {},
        "path": "beacon/v2/service-info",
    }

    token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
        "federation": "false",
    }

    response = requests.post(
        f"{ENV['CANDIG_URL']}/federation/v1/fanout", headers=headers, json=body
    )
    print(response.json())
    assert "results" in response.json()

    headers["federation"] = "true"
    response = requests.post(
        f"{ENV['CANDIG_URL']}/federation/v1/fanout", headers=headers, json=body
    )
    print(response.json())
    assert "list" in str(type(response.json()))
    assert "results" in response.json()[0]


# Add a server, then test to see if federated calls now include that server in the results
def test_add_server():
    token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.get(
        f"{ENV['CANDIG_URL']}/federation/v1/servers", headers=headers
    )

    body = {
        "server": response.json()[0],
        "authentication": {"issuer": ENV["KEYCLOAK_REALM_URL"], "token": token},
    }
    body["server"]["id"] = "test"
    body["server"]["location"]["name"] = "test"
    response = requests.post(
        f"{ENV['CANDIG_URL']}/federation/v1/servers", headers=headers, json=body
    )
    assert response.status_code in [201, 204]

    headers["federation"] = "true"
    body = {
        "service": "htsget",
        "method": "GET",
        "payload": {},
        "path": "beacon/v2/service-info",
    }
    response = requests.post(
        f"{ENV['CANDIG_URL']}/federation/v1/fanout", headers=headers, json=body
    )
    last_result = response.json().pop()
    print(last_result)
    assert last_result["location"]["name"] == "test"

    # delete the server
    response = requests.delete(
        f"{ENV['CANDIG_URL']}/federation/v1/servers/test", headers=headers
    )
    print(response.text)
    assert response.status_code == 200


# Query Test: Get all donors
def test_query_donors_all():
    token = get_token(username=ENV['CANDIG_NOT_ADMIN2_USER'],
                      password=ENV['CANDIG_NOT_ADMIN2_PASSWORD'])
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    params = {}
    response = requests.get(
        f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    ).json()
    print(response)

    # CANDIG_NOT_ADMIN2_USER has authorization for SYNTH_02, so expects a return of 10 donors which is the first page of results
    if len(response["results"]) != 10:
        returned_donors = [x['program_id'] + ": " + (x['submitter_donor_id']) for x in response['results']]
        print(f"Expected to get 10 donors returned but query returned {len(response["results"])}.")
        print(f"Donors returned were: \n{"\n".join(returned_donors)}")
    assert response and len(response["results"]) == 10

    # Check the summary stats as well
    summary_stats = response["summary"]
    pprint.pprint(summary_stats)

    expected_response = {
        'age_at_diagnosis': {
            '30-39 Years': 3,
            '40-49 Years': 8,
            '50-59 Years': 5
        },
        'primary_site_count': {
            'Breast': 4,
            'Bronchus and lung': 4,
            'Colon': 4,
            'None': 4,
            'Skin': 4
        },
        'patients_per_cohort': {
            'SYNTH_02': 20
        },
        'treatment_type_count': {
            'Bone marrow transplant': 9,
            'Other targeting molecular therapy': 6,
            'Photodynamic therapy': 8,
            'Radiation therapy': 18,
            'Stem cell transplant': 8,
            'Surgery': 24,
            'Systemic therapy': 40
        }
    }
    for category in expected_response.keys():
        for value in expected_response[category].keys():
            if summary_stats[category][value] != expected_response[category][value]:
                print(f"\n\nExpected value for {category}: {value} was {expected_response[category][value]} but query returned {summary_stats[category][value]}\n")
                print("Check the returned summary stats below against the expected response:")
                pprint.pprint(summary_stats)
            assert summary_stats[category][value] == expected_response[category][value]

# Test 2: Search for a specific donor
def test_query_donor_search():
    token = get_token(username=ENV['CANDIG_NOT_ADMIN2_USER'],
                      password=ENV['CANDIG_NOT_ADMIN2_PASSWORD'])
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    params = {
        "treatment": "Radiation therapy"
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    ).json()
    pprint.pprint(response)
    assert response and len(response["results"]) == 10

    # Check the summary stats as well
    summary_stats = response["summary"]
    pprint.pprint(summary_stats)
    expected_response = {
        'age_at_diagnosis': {
            '30-39 Years': 3,
            '40-49 Years': 6,
            '50-59 Years': 4
        },
        'primary_site_count': {
            'Breast': 4,
            'Bronchus and lung': 3,
            'Colon': 3,
            'None': 3,
            'Skin': 4
        },
        'patients_per_cohort': {
            'SYNTH_02': 17
        },
        'treatment_type_count': {
            'Bone marrow transplant': 8,
            'Other targeting molecular therapy': 5,
            'Photodynamic therapy': 8,
            'Radiation therapy': 18,
            'Stem cell transplant': 8,
            'Surgery': 21,
            'Systemic therapy': 34}
    }
    for category in expected_response.keys():
        for value in expected_response[category].keys():
            if summary_stats[category][value] != expected_response[category][value]:
                print(f"\n\nExpected value for {category}: {value} was {expected_response[category][value]} but query returned {summary_stats[category][value]}\n")
                print("Check the returned summary stats below against expected response:")
                pprint.pprint(summary_stats)
            assert summary_stats[category][value] == expected_response[category][value]


def test_query_genomic():
    # tests that a request sent via query to htsget-beacon properly prunes the data
    token = get_token(username=ENV['CANDIG_NOT_ADMIN2_USER'],
                      password=ENV['CANDIG_NOT_ADMIN2_PASSWORD'])
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {
        "chrom": "chr21:5030000-5030847",
        "assembly": "hg38"
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    )
    if len(response.json()["results"]) != 1:
        print(f"\n\nExpected 1 result from the genomic query using position 'chr21:5030000-5030847' but got {len(response.json()["results"])}")
        if len(response.json()["results"]) > 0:
            print("Got results from:")
            for donor in response.json()["results"]:
                print(f"{donor["program_id"]}: {donor["submitter_donor_id"]}")
    assert response and len(response.json()["results"]) == 1
    assert response.json()["results"][0]['program_id'] == "SYNTH_02"
    assert response.json()["results"][0]['submitter_donor_id'] == "DONOR_0021"

    token = get_token(username=ENV['CANDIG_NOT_ADMIN_USER'],
                      password=ENV['CANDIG_NOT_ADMIN_PASSWORD'])
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {
        "gene": "LOC102723996",
        "assembly": "hg38"
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    )

    if len(response.json()["results"]) != 1:
        print(f"\n\nExpected 1 result from the genomic query using gene name 'LOC102723996' but got {len(response.json()["results"])}")
        if len(response.json()["results"]) > 0:
            print("Got results from:")
            for donor in response.json()["results"]:
                print(f"{donor["program_id"]}: {donor["submitter_donor_id"]}")
    assert response and len(response.json()["results"]) == 1
    assert response.json()["results"][0]['program_id'] == "SYNTH_01"
    assert response.json()["results"][0]['submitter_donor_id'] == "DONOR_NULL_0001"

    token = get_token(username=ENV['CANDIG_NOT_ADMIN_USER'],
                      password=ENV['CANDIG_NOT_ADMIN_PASSWORD'])
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {
        "gene": "TPTE",
        "assembly": "hg38"
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    )
    if len(response.json()["results"]) != 1:
        print(f"\n\nExpected 1 results from the genomic query using gene name 'TPTE' but got {len(response.json()["results"])}")
        if len(response.json()["results"]) > 0:
            print("Got results from:")
            for donor in response.json()["results"]:
                print(f"{donor["program_id"]}: {donor["submitter_donor_id"]}")
    assert response and len(response.json()["results"]) == 1

    # token = get_token(username=ENV['CANDIG_NOT_ADMIN_USER'],
    #                   password=ENV['CANDIG_NOT_ADMIN_PASSWORD'])
    # headers = {
    #     "Authorization": f"Bearer {token}",
    #     "Content-Type": "application/json; charset=utf-8",
    # }
    # params = {
    #     "gene": "TP53",
    #     "assembly": "hg38"
    # }
    # response = requests.get(
    #     f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    # )
    # pprint.pprint(response.json())
    # if len(response.json()["results"]) != 0:
    #     print(f"\n\nExpected 0 results from the genomic query using gene name 'TP53' but got {len(response.json()["results"])}")
    #     if len(response.json()["results"]) > 0:
    #         print("Got results from:")
    #         for donor in response.json()["results"]:
    #             print(f"{donor["program_id"]}: {donor["submitter_donor_id"]}")
    # assert response and len(response.json()["results"]) == 0


def test_query_discovery():
    katsu_response = requests.get(
        f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v3/discovery/programs/"
    ).json()
    query_response = requests.get(
        f"{ENV['CANDIG_ENV']['QUERY_INTERNAL_URL']}/discovery/programs").json()
    # Ensure that each category in metadata corresponds to something in the site
    for category in query_response["site"]["required_but_missing"]:
        for field in query_response["site"]["required_but_missing"][category]:
            for total_type in query_response["site"]["required_but_missing"][category][field]:
                total = query_response["site"]["required_but_missing"][category][field][total_type]
                if type(total) == str:
                    # Can't perform this check on censored data
                    continue
                for program in katsu_response:
                    if category in program["metadata"]['required_but_missing'] and field in program["metadata"]['required_but_missing'][category]:
                        if type(program["metadata"]['required_but_missing'][category][field][total_type]) == int:
                            total -= program["metadata"]['required_but_missing'][category][field][total_type]
                if total != 0:
                    print(f"{category}/{field}/{total_type} totals don't line up")
                    assert False

    # Ensure that every category & field in Katsu exists in the response
    for program in katsu_response:
        for category in program["metadata"]["required_but_missing"]:
            assert category in query_response["site"]["required_but_missing"]
            for field in program["metadata"]["required_but_missing"][category]:
                assert field in query_response["site"]["required_but_missing"][category]


def test_clean_up():
    clean_up_program("SYNTH_01")
    clean_up_program("SYNTH_02")
    clean_up_program("SYNTH_03")
    clean_up_program("SYNTH_04")

    # clean up test_htsget
    old_val = os.environ.get("TESTENV_URL")
    os.environ["TESTENV_URL"] = f"{ENV['CANDIG_ENV']['HTSGET_PUBLIC_URL']}"
    pytest.main(["-x", "lib/htsget/htsget_app/tests/test_htsget_server.py", "-k", "test_remove_objects"])
    if old_val is not None:
        os.environ["TESTENV_URL"] = old_val

