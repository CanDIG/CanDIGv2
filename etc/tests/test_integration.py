import json
import os
import re
import sys
import uuid
from http import HTTPStatus
from pathlib import Path
import datetime
import pytest
import requests
from dotenv import dotenv_values

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../..")
sys.path.insert(0, os.path.abspath(f"{REPO_DIR}"))

from settings import get_env

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
def get_token(username=None, password=None):
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
        return response.json()["access_token"]


def test_get_token():
    assert get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )


## Tyk test: can we get a response from Tyk for all of our services?
def test_tyk():
    headers = {
        "Authorization": f"Bearer {get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])}"
    }
    endpoints = [
        f"{ENV['CANDIG_ENV']['TYK_HTSGET_API_LISTEN_PATH']}/ga4gh/drs/v1/service-info",
        f"{ENV['CANDIG_ENV']['TYK_KATSU_API_LISTEN_PATH']}/v2/service-info",
        f"{ENV['CANDIG_ENV']['TYK_FEDERATION_API_LISTEN_PATH']}/v1/service-info",
        f"{ENV['CANDIG_ENV']['TYK_OPA_API_LISTEN_PATH']}/v1/data/paths",
        f"{ENV['CANDIG_ENV']['TYK_QUERY_API_LISTEN_PATH']}/service-info"]
    responses = []
    for endpoint in endpoints:
        response = requests.get(
            f"{ENV['CANDIG_URL']}/{endpoint}", headers=headers, timeout=10
        )
        responses.append(response.status_code)
        print(f"{endpoint}: {response.status_code == 200}")
    assert all(response == 200 for response in responses)


## Opa tests:


## Can we get the correct dataset response for each user?
def user_datasets():
    return [
        ("CANDIG_SITE_ADMIN", "SYNTHETIC-2"),
        ("CANDIG_NOT_ADMIN", "SYNTHETIC-1"),
    ]


@pytest.mark.parametrize("user, dataset", user_datasets())
def test_opa_datasets(user, dataset):
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    token = get_token(username=username, password=password)
    payload = {
        "input": {
            "body": {
                "path": "/v2/discovery/", "method": "GET"
            },
            "token": token
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Opa": ENV["OPA_SECRET"],
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        f"{ENV['CANDIG_ENV']['OPA_URL']}/v1/data/permissions/datasets",
        json=payload,
        headers=headers,
    )
    print(f"108 {datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} {json.dumps(payload)} {response.text}")
    assert dataset in response.json()["result"]


## Can we add a dataset to one of the users?
def test_add_opa_dataset():
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    test_data = {
        "email": ENV["CANDIG_SITE_ADMIN_USER"] + "@test.ca",
        "program": "OPA-TEST"
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}/email/{test_data['email']}", headers=headers)
    # when the user has admin access, they should be allowed
    print(f"129 {response.json()}, {response.status_code}")
    assert response.status_code == 200

    test_opa_datasets("CANDIG_SITE_ADMIN", test_data["program"])

    response = requests.delete(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}/email/{test_data['email']}", headers=headers)
    assert response.status_code == 200
    assert test_data['program'] not in response.json()["access"]["controlled_access_list"][test_data["email"]]


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
    token = get_token(username=username, password=password)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Opa": ENV["OPA_SECRET"],
        "Authorization": f"Bearer {token}"
    }

    payload["input"]["token"] = token
    response = requests.post(
        f"{ENV['CANDIG_ENV']['OPA_URL']}/v1/data/idp/site_admin",
        json=payload,
        headers=headers,
    )
    print(response.json())
    assert ("result" in response.json()) == is_admin


## Vault tests: can we add an aws access key and retrieve it, using both the site_admin user and the VAULT_S3_TOKEN?
def test_vault():
    site_admin_token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # log in site_admin
    payload = {"jwt": site_admin_token, "role": "site_admin"}
    response = requests.post(
        f"{ENV['CANDIG_URL']}/vault/v1/auth/jwt/login", json=payload, headers=headers
    )
    assert "auth" in response.json()
    client_token = response.json()["auth"]["client_token"]

    headers["X-Vault-Token"] = client_token
    # delete the test secret, if it exists:
    response = requests.delete(
        f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers
    )
    print(response)
    assert response.status_code == 204

    # confirm that the test secret does not yet exist:
    response = requests.get(
        f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers
    )
    print(response.json())
    assert response.status_code == 404

    # confirm that this works with the CANDIG_S3_TOKEN too:
    headers["X-Vault-Token"] = ENV["VAULT_S3_TOKEN"]
    response = requests.get(
        f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers
    )
    print(response.json())
    assert response.status_code == 404

    # set a secret
    payload = {"url": "test.com", "secret": "test", "access": "testtest"}
    response = requests.post(
        f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers, json=payload
    )
    response = requests.get(
        f"{ENV['CANDIG_URL']}/vault/v1/aws/test-test", headers=headers
    )

    print(response.json())
    assert response.json()["data"]["url"] == payload["url"]


# =========================|| KATSU TEST BEGIN ||============================= #
# HELPER FUNCTIONS
# -----------------
def get_headers(is_admin=False):
    """
    Returns either admin or non-admin HTTP headers for making requests API.
    """
    if is_admin:
        user = ENV.get("CANDIG_SITE_ADMIN_USER")
        password = ENV.get("CANDIG_SITE_ADMIN_PASSWORD")
        user_type = "site admin"
    else:
        user = ENV.get("CANDIG_NOT_ADMIN_USER")
        password = ENV.get("CANDIG_NOT_ADMIN_PASSWORD")
        user_type = "user"

    if not user or not password:
        pytest.skip(f"{user_type.capitalize()} credentials not provided")

    token = get_token(username=user, password=password)

    if not token:
        pytest.fail(f"Failed to authenticate {user_type}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    return headers

def clean_up_program(test_id):
    """
    Deletes a dataset and all related objects. Expected 204
    """
    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/program/{test_id}/",
        headers=get_headers(is_admin=True),
    )
    assert (
        delete_response.status_code == HTTPStatus.NO_CONTENT or delete_response.status_code == HTTPStatus.NOT_FOUND
    ), f"CLEAN_UP_PROGRAM Expected status code {HTTPStatus.NO_CONTENT}, but got {delete_response.status_code}."
    f" Response content: {delete_response.content}"

# =========================|| KATSU TEST END ||=============================== #

def test_ingest_permissions():
    clean_up_program("SYNTHETIC-2")
    clean_up_program("TEST_2")

    with open("lib/candig-ingest/candigv2-ingest/tests/clinical_ingest.json", 'r') as f:
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

    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/clinical", headers=headers, json=test_data)
    # when the user has admin access, they should be allowed
    print(response.json())
    assert response.status_code == 201
    assert len(response.json()["SYNTHETIC-2"]["errors"]) == 0
    assert len(response.json()["TEST_2"]["errors"]) == 0
    assert len(response.json()["SYNTHETIC-2"]["results"]) == 12
    assert len(response.json()["TEST_2"]["results"]) == 5


## Htsget tests:


## Run the main htsget test suite
def test_htsget():
    old_val = os.environ.get("TESTENV_URL")
    os.environ[
        "TESTENV_URL"
    ] = f"{ENV['CANDIG_ENV']['HTSGET_PUBLIC_URL']}"
    retcode = pytest.main(["-x", "lib/htsget/htsget_app/tests/test_htsget_server.py", "-k", "test_remove_objects or test_post_objects or test_index_variantfile"])
    if old_val is not None:
        os.environ["TESTENV_URL"] = old_val
    print(retcode)
    assert retcode == pytest.ExitCode.OK


## Can we add samples to Opa-controlled dataset?
def test_htsget_add_sample_to_dataset():
    site_admin_token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    TESTENV_URL = (
        ENV["CANDIG_ENV"]["HTSGET_PUBLIC_URL"]
        .replace("http://", "drs://")
        .replace("https://", "drs://")
    )
    # Delete cohort SYNTHETIC-1
    response = requests.delete(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTHETIC-1",
        headers=headers,
    )

    # Add NA18537 and multisample_1 to cohort SYNTHETIC-1, which is only authorized for user1:
    payload = {
        "id": "SYNTHETIC-1",
        "drsobjects": [f"{TESTENV_URL}/NA18537", f"{TESTENV_URL}/multisample_1"],
    }

    response = requests.post(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts",
        headers=headers,
        json=payload,
    )
    response = requests.get(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTHETIC-1",
        headers=headers,
    )
    print(response.json())
    assert f"{TESTENV_URL}/multisample_1" in response.json()["drsobjects"]
    assert f"{TESTENV_URL}/multisample_2" not in response.json()["drsobjects"]

    # Delete cohort SYNTHETIC-2
    response = requests.delete(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTHETIC-2",
        headers=headers,
    )

    # Add NA20787 and multisample_2 to cohort SYNTHETIC-2, which is only authorized for user2:
    payload = {
        "id": "SYNTHETIC-2",
        "drsobjects": [f"{TESTENV_URL}/NA20787", f"{TESTENV_URL}/multisample_2"],
    }

    response = requests.post(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts",
        headers=headers,
        json=payload,
    )
    response = requests.get(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTHETIC-2",
        headers=headers,
    )
    print(response.json())
    assert f"{TESTENV_URL}/multisample_2" in response.json()["drsobjects"]
    assert f"{TESTENV_URL}/multisample_1" not in response.json()["drsobjects"]


## Can we access the data when authorized to do so?
def user_access():
    return [
        (
            "CANDIG_SITE_ADMIN",
            "NA18537",
            True,
        ),  # site admin can access all data, even if not specified by dataset
        (
            "CANDIG_NOT_ADMIN",
            "NA18537",
            True,
        ),  # user1 can access NA18537 as part of SYNTHETIC-1
        ("CANDIG_NOT_ADMIN", "NA20787", False),  # user1 cannot access NA20787
    ]


@pytest.mark.parametrize("user, obj, access", user_access())
def test_htsget_access_data(user, obj, access):
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
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
    print(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/variants/data/{obj}")
    assert (response.status_code == 200) == access


## Does Beacon return the correct level of authorized results?
def beacon_access():
    return [
        (
            "CANDIG_SITE_ADMIN",
            "NC_000021.8:g.5030847T>A",
            ["multisample_1", "multisample_2"],
            ["test"],
        ),  # site admin can access all data, even if not specified by dataset
        (
            "CANDIG_NOT_ADMIN",
            "NC_000021.8:g.5030847T>A",
            ["multisample_1"],
            ["multisample_2", "test"],
        ),  # user1 can access NA18537 as part of SYNTHETIC-1
        (
            "CANDIG_NOT_ADMIN",
            "NC_000001.11:g.16565782G>A",
            [],
            ["multisample_1", "multisample_2", "test"],
        ),  # user1 cannot access test
    ]


@pytest.mark.parametrize("user, search, can_access, cannot_access", beacon_access())
def test_beacon(user, search, can_access, cannot_access):
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
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
    for c in can_access:
        assert c in str(response.json())
    for c in cannot_access:
        assert c not in str(response.json())
    print(response.json())


## HTSGet + katsu:
def test_ingest_htsget():
    with open("lib/candig-ingest/candigv2-ingest/tests/genomic_ingest.json", 'r') as f:
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
    print(response.json())
    assert response.status_code == 403

    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/genomic", headers=headers, json=test_data)
    # when the user has admin access, they should be allowed
    print(response.json())
    assert response.status_code == 200
    for id in response.json():
        assert "genomic" in response.json()[id]
        assert "sample" in response.json()[id]


def test_sample_metadata():
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/samples/SAMPLE_REGISTRATION_1", headers=headers)
    assert "genomes" in response.json()
    assert "HG00096.cnv.vcf" in response.json()["genomes"]


def test_index_success():
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # this has already been indexed in test_htsget, so it will def be indexed.
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects/multisample_1", headers=headers)
    assert "indexed" in response.json()
    assert response.json()['indexed'] == 1


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

    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
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
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
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
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    params = {}
    response = requests.get(
        f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    ).json()
    print(response)
    assert response and len(response["results"]) == 4

    # Check the summary stats as well
    summary_stats = response["summary"]
    expected_response = {
        "age_at_diagnosis": {
            "30-39 Years": 2,
            "60-69 Years": 1,
            "70-79 Years": 1
        },
        "cancer_type_count": {
            "Esophagus": 1,
            "Eye and adnexa": 1,
            "Floor of mouth": 1,
            "Gallbladder": 1
        },
        "patients_per_cohort": {
            "SYNTHETIC-2": 4
        },
        "treatment_type_count": {
            "Bone marrow transplant": 1,
            "Chemotherapy": 1,
            "Hormonal therapy": 1,
            "Immunotherapy": 2,
            "Surgery": 1
        }
    }
    for category in expected_response.keys():
        for value in expected_response[category].keys():
            assert summary_stats[category][value] == expected_response[category][value]

# Test 2: Search for a specific donor
def test_query_donor_search():
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    params = {
        "treatment": "Chemotherapy"
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    ).json()
    print(response)
    assert response and len(response["results"]) == 1

    # Check the summary stats as well
    summary_stats = response["summary"]
    expected_response = {
        "age_at_diagnosis": {
            "30-39 Years": 1
        },
        "cancer_type_count": {
            "Eye and adnexa": 1
        },
        "patients_per_cohort": {
            "SYNTHETIC-2": 1
        },
        "treatment_type_count": {
            "Chemotherapy": 1,
            "Immunotherapy": 1,
            "Surgery": 1
        }
    }
    for category in expected_response.keys():
        for value in expected_response[category].keys():
            assert summary_stats[category][value] == expected_response[category][value]
    assert True


def test_query_info():
    # tests that a request sent via query to htsget-beacon will have genomic_query_info in the response. This should be updated when the real response is designed.
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {
        "chrom": "chr21:5030630-5030640",
        "assembly": "hg38"
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    )
    assert "genomic_query_info" in response.json()


def test_query_discovery():
    katsu_response = requests.get(
        f"{ENV['CANDIG_URL']}/{ENV['CANDIG_ENV']['TYK_KATSU_API_LISTEN_PATH']}/v2/discovery/programs/"
    ).json()
    query_response = requests.get(
        f"{ENV['CANDIG_URL']}/{ENV['CANDIG_ENV']['TYK_QUERY_API_LISTEN_PATH']}/discovery/programs"
    ).json()

    # Ensure that each category in metadata corresponds to something in the site
    print(query_response)
    for category in query_response.site.required_but_missing:
        for field in query_response.site.required_but_missing[category]:
            total = query_response.site.required_but_missing[category][field]
            for site in katsu_response:
                total -= site.required_but_missing[category][field]
            if total != 0:
                print(f"{category}/{field} totals don't line up")
                assert False

    # Ensure that every category & field in Katsu exists in the response
    for program in katsu_response:
        for category in katsu_response[program]["metadata"]["required_but_missing"]:
            assert category in query_response.site.required_but_missing
            for field in katsu_response[program]["metadata"]["required_but_missing"][category]:
                assert field in query_response.site.required_but_missing


def test_clean_up():
    clean_up_program("SYNTHETIC-2")
    clean_up_program("TEST_2")
