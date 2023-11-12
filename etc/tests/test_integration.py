import json
import os
import re
import sys
import uuid
from http import HTTPStatus
from pathlib import Path

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
    payload = {"input": {"body": {"path": "/v2/discovery/", "method": "GET"}}}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Opa": ENV["OPA_SECRET"],
    }

    payload["input"]["token"] = get_token(username=username, password=password)
    response = requests.post(
        f"{ENV['CANDIG_ENV']['OPA_URL']}/v1/data/permissions/datasets",
        json=payload,
        headers=headers,
    )
    assert dataset in response.json()["result"]


## Is the user a site admin?
def user_admin():
    return [
        ("CANDIG_SITE_ADMIN", True),
        ("CANDIG_NOT_ADMIN", False),
    ]


@pytest.mark.parametrize("user, is_admin", user_admin())
def test_site_admin(user, is_admin):
    payload = {"input": {}}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Opa": ENV["OPA_SECRET"],
    }

    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    payload["input"]["token"] = get_token(username=username, password=password)
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


## Htsget tests:


## Run the main htsget test suite
def test_htsget():
    old_val = os.environ.get("TESTENV_URL")
    os.environ[
        "TESTENV_URL"
    ] = f"http://{ENV['CANDIG_ENV']['CANDIG_DOMAIN']}:{ENV['CANDIG_ENV']['HTSGET_PORT']}"
    retcode = pytest.main(["-x", "lib/htsget/htsget_app/tests/test_htsget_server.py"])
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


def assert_datasets_should_not_exist(datasets):
    """
    Retrieve a list of dataset names from discovery donor api.
    If any of the dataset names is found, the assertion will fail.
    """
    response = requests.get(
        f"{ENV['CANDIG_URL']}/katsu/v2/discovery/donors/", headers=get_headers()
    )
    data = response.json()
    dataset_names = list(data["discovery_donor"].keys())

    assert all(
        dataset_name not in dataset_names for dataset_name in datasets
    ), f"Expected none of {datasets} to exist, but at least one was found."


def ingest_data(endpoint, data, is_admin=False):
    """
    Ingests data into the katsu API at the specified endpoint using a POST request.
    """
    headers = get_headers(is_admin)
    response = requests.post(
        f"{ENV['CANDIG_URL']}/katsu/v2/ingest/{endpoint}/",
        headers=headers,
        json=data,
    )
    return response


def assert_ingest_response_status(response, expected_status, endpoint):
    """
    Asserts that the response status code matches the expected status code for an ingest operation.
    """
    assert response.status_code == expected_status, (
        f"INGEST_{endpoint.upper()} Expected status code {expected_status}, but got {response.status_code}."
        f" Response content: {response.content}"
    )


def perform_ingest_and_assert_status(endpoint, data, is_admin=False):
    """
    Performs data ingest and asserts the response status code depend on permission
    """
    response = ingest_data(endpoint, data, is_admin)
    expected_status = HTTPStatus.CREATED if is_admin else HTTPStatus.FORBIDDEN
    assert_ingest_response_status(response, expected_status, endpoint)


def clean_up_program(test_id):
    """
    Deletes a dataset and all related objects. Expected 204
    """
    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/{test_id}/",
        headers=get_headers(is_admin=True),
    )
    assert (
        delete_response.status_code == HTTPStatus.NO_CONTENT or delete_response.status_code == HTTPStatus.NOT_FOUND
    ), f"CLEAN_UP_PROGRAM Expected status code {HTTPStatus.NO_CONTENT}, but got {delete_response.status_code}."
    f" Response content: {delete_response.content}"


def check_program_ingest(test_id, is_admin=False):
    endpoint = "programs"
    data = [{"program_id": test_id}]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_donor_ingest(test_id, is_admin=False):
    endpoint = "donors"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_diagnosis_ingest(test_id, is_admin=False):
    endpoint = "primary_diagnoses"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_primary_diagnosis_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_specimen_ingest(test_id, is_admin=False):
    endpoint = "specimens"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_primary_diagnosis_id": test_id,
            "submitter_specimen_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_sample_ingest(test_id, is_admin=False):
    endpoint = "sample_registrations"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_specimen_id": test_id,
            "submitter_sample_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_treatment_ingest(test_id, is_admin=False):
    endpoint = "treatments"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_primary_diagnosis_id": test_id,
            "submitter_treatment_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_chemotherapy_ingest(test_id, is_admin=False):
    endpoint = "chemotherapies"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_treatment_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_radiation_ingest(test_id, is_admin=False):
    endpoint = "radiations"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_treatment_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_hormonetherapy_ingest(test_id, is_admin=False):
    endpoint = "hormone_therapies"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_treatment_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_immunotherapy_ingest(test_id, is_admin=False):
    endpoint = "immunotherapies"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_treatment_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_surgery_ingest(test_id, is_admin=False):
    endpoint = "surgeries"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_treatment_id": test_id,
            "margin_types_involved": [],
            "margin_types_not_involved": [],
            "margin_types_not_assessed": [],
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_follow_up_ingest(test_id, is_admin=False):
    endpoint = "follow_ups"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
            "submitter_primary_diagnosis_id": test_id,
            "submitter_treatment_id": test_id,
            "submitter_follow_up_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_biomarker_ingest(test_id, is_admin=False):
    endpoint = "biomarkers"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_comorbidity_ingest(test_id, is_admin=False):
    endpoint = "comorbidities"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_exposure_ingest(test_id, is_admin=False):
    endpoint = "exposures"
    data = [
        {
            "submitter_donor_id": test_id,
            "program_id": test_id,
        },
    ]
    perform_ingest_and_assert_status(endpoint, data, is_admin)


def check_datasets_access(is_admin, authorized_datasets, unauthorized_datasets):
    """
    Checks access to datasets depend on user permission and asserts dataset presence.
    """
    response = requests.get(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/",
        headers=get_headers(is_admin=is_admin),
    )
    programs = list(map(lambda x: x["program_id"], response.json()["results"]))

    # Assert that all authorized datasets are present in programs
    assert all(
        program in programs for program in authorized_datasets
    ), "Authorized datasets missing."

    # Assert that no unauthorized datasets are present in programs
    assert all(
        program not in programs for program in unauthorized_datasets
    ), "Unauthorized datasets present."


# TEST FUNCTIONS
# --------------
def test_katsu_online():
    """
    Verify that Katsu is online and responding as expected.

    Testing Strategy:
    - Send a GET request to health check endpoint with authentication headers.

    Expected result:
    - HTTP 200 OK status
    """
    response = requests.get(
        f"{ENV['CANDIG_URL']}/katsu/v2/service-info", headers=get_headers()
    )
    assert (
        response.status_code == HTTPStatus.OK
    ), f"Expected status code {HTTPStatus.OK}, but got {response.status_code}."
    f" Response content: {response.content}"


def test_authorized_ingests():
    """
    Verify that ingest apis work as expected for admin

    Testing Strategy:
    - Call ingest apis with admin header in subsequent order.
    - If any of ingests fail, the following ingests will not run.
    - Clean up after the test is completed or if any exception occurs.

    Expected result:
    - HTTP 201 CREATED with valid ingest data.
    """
    # to simplify the test data, only 1 unique id is needed
    test_id = "TEST-" + str(uuid.uuid4())
    try:
        check_program_ingest(test_id, is_admin=True)
        check_donor_ingest(test_id, is_admin=True)
        check_diagnosis_ingest(test_id, is_admin=True)
        check_specimen_ingest(test_id, is_admin=True)
        check_sample_ingest(test_id, is_admin=True)
        check_treatment_ingest(test_id, is_admin=True)
        check_chemotherapy_ingest(test_id, is_admin=True)
        check_hormonetherapy_ingest(test_id, is_admin=True)
        check_radiation_ingest(test_id, is_admin=True)
        check_immunotherapy_ingest(test_id, is_admin=True)
        check_surgery_ingest(test_id, is_admin=True)
        check_follow_up_ingest(test_id, is_admin=True)
        check_biomarker_ingest(test_id, is_admin=True)
        check_comorbidity_ingest(test_id, is_admin=True)
        check_exposure_ingest(test_id, is_admin=True)

    finally:
        clean_up_program(test_id)


def test_unauthorized_ingests():
    """
    Verify that ingest apis will not work for non-admin user

    Testing Strategy:
    - Call ingest apis with non-admin header in subsequent order.
    - Attempt to clean up after in case any ingests go through but expected None

    Expected result:
    - HTTP 403 even with valid ingest data.
    """
    # to simplify the test data, only 1 unique id is needed
    test_id = "TEST-" + str(uuid.uuid4())
    try:
        check_program_ingest(test_id, is_admin=False)
        check_donor_ingest(test_id, is_admin=False)
        check_diagnosis_ingest(test_id, is_admin=False)
        check_specimen_ingest(test_id, is_admin=False)
        check_sample_ingest(test_id, is_admin=False)
        check_treatment_ingest(test_id, is_admin=False)
        check_chemotherapy_ingest(test_id, is_admin=False)
        check_hormonetherapy_ingest(test_id, is_admin=False)
        check_radiation_ingest(test_id, is_admin=False)
        check_immunotherapy_ingest(test_id, is_admin=False)
        check_surgery_ingest(test_id, is_admin=False)
        check_follow_up_ingest(test_id, is_admin=False)
        check_biomarker_ingest(test_id, is_admin=False)
        check_comorbidity_ingest(test_id, is_admin=False)
        check_exposure_ingest(test_id, is_admin=False)
    finally:
        delete_response = requests.delete(
            f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/{test_id}/",
            headers=get_headers(True),
        )
        assert (
            delete_response.status_code == HTTPStatus.NOT_FOUND
        ), f"CLEAN_UP_PROGRAM Expected status code {HTTPStatus.NOT_FOUND}, but got {delete_response.status_code}."
    f" Response content: {delete_response.content}"


def test_katsu_users_data_access():
    """
    Verifies user access to authorized datasets while denying access to unauthorized datasets.

    Testing Strategy:
    - Send a GET request to authorized program endpoint as an admin and non-admin user

    Expected result:
    - List of programs that match OPA datasets

    """
    # NOTE: this values are predefined in OPA
    # if the test fails, check with OPA first
    synthetic_datasets = ["SYNTHETIC-1", "SYNTHETIC-2"]
    admin_authorized_datasets = ["SYNTHETIC-2"]
    admin_unauthorized_datasets = [
        "SYNTHETIC-1"
    ]  # even admin does not have read acccess to all
    non_admin_authorized_datasets = ["SYNTHETIC-1"]
    non_admin_unauthorized_datasets = ["SYNTHETIC-2"]

    try:
        # Check if datasets already exist or not
        # If found, skip the test since it could lead to unexpected results
        assert_datasets_should_not_exist(synthetic_datasets)

        # create synthetic datasets that matches OPA access
        endpoint = "programs"
        program_data = [{"program_id": dataset_id} for dataset_id in synthetic_datasets]
        response = ingest_data(endpoint, program_data, is_admin=True)
        assert response.status_code == HTTPStatus.CREATED, "Failed to create programs."

        # Assert access for admin user
        check_datasets_access(
            is_admin=True,
            authorized_datasets=admin_authorized_datasets,
            unauthorized_datasets=admin_unauthorized_datasets,
        )

        # Assert access for non-admin user
        check_datasets_access(
            is_admin=False,
            authorized_datasets=non_admin_authorized_datasets,
            unauthorized_datasets=non_admin_unauthorized_datasets,
        )
    finally:
        for program_id in synthetic_datasets:
            clean_up_program(program_id)


# =========================|| KATSU TEST END ||=============================== #


## HTSGet + katsu:
def test_add_sample_to_genomic():
    test_loc = "https://raw.githubusercontent.com/CanDIG/katsu/develop/chord_metadata_service/mohpackets/data/small_dataset/synthetic_data/SampleRegistration.json"
    response = requests.get(test_loc)
    first_sample = response.json().pop(0)

    site_admin_token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.get(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/{first_sample['program_id']}",
        headers=headers,
    )

    assert response.status_code == 200

    assert len(response.json()["drsobjects"]) > 0
    drs_obj = response.json()["drsobjects"].pop(0)
    drs_obj_match = re.match(r"^(.+)\/(.+?)$", drs_obj)
    if drs_obj_match is not None:
        host = drs_obj_match.group(1)
        drs_obj_name = drs_obj_match.group(2)

        # assign the first member of this cohort to the sample
        sample_drs_obj = {
            "id": first_sample["submitter_sample_id"],
            "contents": [{"drs_uri": [drs_obj], "name": drs_obj_name, "id": drs_obj_name}],
            "version": "v1",
            "cohort": first_sample['program_id'],
            "description": "sample"
        }

        url = f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects"
        response = requests.request("POST", url, json=sample_drs_obj, headers=headers)
        print(response.text)
        assert response.status_code == 200


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
