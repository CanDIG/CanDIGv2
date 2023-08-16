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


## Tyk test: can we get a response from Tyk for a service?
def test_tyk():
    headers = {
        "Authorization": f"Bearer {get_token(username=ENV['CANDIG_SITE_ADMIN_USER'], password=ENV['CANDIG_SITE_ADMIN_PASSWORD'])}"
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/{ENV['CANDIG_ENV']['TYK_HTSGET_API_LISTEN_PATH']}/ga4gh/drs/v1/service-info",
        headers=headers,
    )
    assert response.status_code == 200


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
    # Delete dataset SYNTHETIC-1
    response = requests.delete(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets/SYNTHETIC-1",
        headers=headers,
    )

    # Add NA18537 and multisample_1 to dataset SYNTHETIC-1, which is only authorized for user1:
    payload = {
        "id": "SYNTHETIC-1",
        "drsobjects": [f"{TESTENV_URL}/NA18537", f"{TESTENV_URL}/multisample_1"],
    }

    response = requests.post(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets",
        headers=headers,
        json=payload,
    )
    response = requests.get(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets/SYNTHETIC-1",
        headers=headers,
    )
    print(response.json())
    assert f"{TESTENV_URL}/multisample_1" in response.json()["drsobjects"]
    assert f"{TESTENV_URL}/multisample_2" not in response.json()["drsobjects"]

    # Delete dataset SYNTHETIC-2
    response = requests.delete(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets/SYNTHETIC-2",
        headers=headers,
    )

    # Add NA20787 and multisample_2 to dataset SYNTHETIC-2, which is only authorized for user2:
    payload = {
        "id": "SYNTHETIC-2",
        "drsobjects": [f"{TESTENV_URL}/NA20787", f"{TESTENV_URL}/multisample_2"],
    }

    response = requests.post(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets",
        headers=headers,
        json=payload,
    )
    response = requests.get(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets/SYNTHETIC-2",
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
    print(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/v1/variants/data/{obj}")
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


# ===========================|| KATSU ||========================================#
def test_katsu_online(katsu_headers):
    """
    Verify that Katsu is online and responding as expected.

    Testing Strategy:
    - Send a GET request to health check endpoint with authentication headers.

    Expected result:
    - HTTP 200 OK status
    """
    response = requests.get(
        f"{ENV['CANDIG_URL']}/katsu/v2/version_check", headers=katsu_headers
    )
    assert (
        response.status_code == HTTPStatus.OK
    ), f"Expected status code {HTTPStatus.OK}, but got {response.status_code}."
    f" Response content: {response.content}"


@pytest.fixture
def katsu_headers():
    admin_user = ENV.get("CANDIG_SITE_ADMIN_USER")
    admin_pass = ENV.get("CANDIG_SITE_ADMIN_PASSWORD")

    if not admin_user or not admin_pass:
        pytest.skip("Site admin credentials not provided")

    site_admin_token = get_token(
        username=admin_user,
        password=admin_pass,
    )
    if not site_admin_token:
        pytest.fail("Failed to authenticate site admin")

    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    yield headers


def cleanup_program(program_id, katsu_headers, name):
    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/{program_id}/",
        headers=katsu_headers,
    )

    assert (
        delete_response.status_code == HTTPStatus.NO_CONTENT
    ), f"{name} expected status code {HTTPStatus.NO_CONTENT}, but got {delete_response.status_code}."
    f" Response content: {delete_response.content}"


# def test_authorized_ingest_program(katsu_headers):
#     program_id = "TEST-" + str(uuid.uuid4())
#     ingest_data = [
#         {"program_id": program_id},
#     ]

#     try:
#         response = requests.post(
#             f"{ENV['CANDIG_URL']}/katsu/v2/ingest/programs",
#             headers=katsu_headers,
#             json=ingest_data,
#         )

#         assert (
#             response.status_code == HTTPStatus.CREATED
#         ), f"Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
#         f" Response content: {response.content}"
#     finally:
#         cleanup_program(program_id, katsu_headers, "test_authorized_ingest_program")


# def test_authorized_ingest_donor(katsu_headers):
#     program_id = "TEST-" + str(uuid.uuid4())
#     donor_id = "TEST-" + str(uuid.uuid4())
#     program_data = [
#         {"program_id": program_id},
#     ]
#     donor_data = [
#         {
#             "submitter_donor_id": donor_id,
#             "program_id": program_id,
#         },
#     ]

#     try:
#         requests.post(
#             f"{ENV['CANDIG_URL']}/katsu/v2/ingest/programs",
#             headers=katsu_headers,
#             json=program_data,
#         )
#         response = requests.post(
#             f"{ENV['CANDIG_URL']}/katsu/v2/ingest/donors",
#             headers=katsu_headers,
#             json=donor_data,
#         )

#         assert (
#             response.status_code == HTTPStatus.CREATED
#         ), f"Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
#         f" Response content: {response.content}"

#     finally:
#         cleanup_program(program_id, katsu_headers, "test_authorized_ingest_donor")


def test_authorized_ingest(katsu_headers):
    # to simplify the test data, only 1 unique id is needed
    test_id = "TEST-" + str(uuid.uuid4())
    try:
        # Ingest program
        program_data = [{"program_id": test_id}]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/programs",
            headers=katsu_headers,
            json=program_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_PROGRAM Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest donor
        donor_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/donors",
            headers=katsu_headers,
            json=donor_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_DONOR Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest primary diagnosis
        diagnosis_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_primary_diagnosis_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/primary_diagnoses",
            headers=katsu_headers,
            json=diagnosis_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_PRIMARY Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest specimen
        specimen_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_primary_diagnosis_id": test_id,
                "submitter_specimen_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/specimens",
            headers=katsu_headers,
            json=specimen_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_SPECIMEN Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest sample registration
        sample_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_specimen_id": test_id,
                "submitter_sample_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/sample_registrations",
            headers=katsu_headers,
            json=sample_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_SAMPLE Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest treatment
        treatment_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_primary_diagnosis_id": test_id,
                "submitter_treatment_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/treatments",
            headers=katsu_headers,
            json=treatment_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_TREATMENT Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest chemo
        chemotherapy_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_treatment_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/chemotherapies",
            headers=katsu_headers,
            json=chemotherapy_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_CHEMOTHERAPY Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest hormonetherapy
        hormonetherapy_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_treatment_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/hormone_therapies",
            headers=katsu_headers,
            json=hormonetherapy_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_HORMONE Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest radiation
        radiation_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_treatment_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/radiations",
            headers=katsu_headers,
            json=radiation_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_RADIATION Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest immunotherapy
        immunotherapy_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_treatment_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/immunotherapies",
            headers=katsu_headers,
            json=immunotherapy_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_IMMUNOTHERAPY Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest surgery
        surgery_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_treatment_id": test_id,
                "margin_types_involved": [],
                "margin_types_not_involved": [],
                "margin_types_not_assessed": [],
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/surgeries",
            headers=katsu_headers,
            json=surgery_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_SURGERY Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest follow_up
        follow_up_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
                "submitter_primary_diagnosis_id": test_id,
                "submitter_treatment_id": test_id,
                "submitter_follow_up_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/follow_ups",
            headers=katsu_headers,
            json=follow_up_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_FOLLOW_UP Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest biomarker
        biomarker_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/biomarkers",
            headers=katsu_headers,
            json=biomarker_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_BIOMARKER Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest comorbidity
        comorbidity_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/comorbidities",
            headers=katsu_headers,
            json=comorbidity_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_COMORBIDITY Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

        # Ingest exposure
        exposure_data = [
            {
                "submitter_donor_id": test_id,
                "program_id": test_id,
            },
        ]
        response = requests.post(
            f"{ENV['CANDIG_URL']}/katsu/v2/ingest/exposures",
            headers=katsu_headers,
            json=exposure_data,
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f"INGEST_EXPOSURE Expected status code {HTTPStatus.CREATED}, but got {response.status_code}."
            f" Response content: {response.content}"
        )

    finally:
        # cleanup_program(program_id, katsu_headers, "test_authorized_ingest_donor")
        delete_response = requests.delete(
            f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/{test_id}/",
            headers=katsu_headers,
        )

        assert (
            delete_response.status_code == HTTPStatus.NO_CONTENT
        ), f"CLEAN_UP_PROGRAM Expected status code {HTTPStatus.NO_CONTENT}, but got {delete_response.status_code}."
        f" Response content: {delete_response.content}"


def test_setup_katsu():
    test_loc = "https://raw.githubusercontent.com/CanDIG/katsu/develop/chord_metadata_service/mohpackets/data/small_dataset/synthetic_data/Program.json"
    response = requests.get(test_loc)
    assert response.status_code == 200

    site_admin_token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.post(
        f"{ENV['CANDIG_URL']}/katsu/v2/ingest/programs",
        headers=headers,
        json=response.json(),
    )
    print(response.json())
    if response.status_code >= 400:
        errors = response.json()["error during ingest_programs"]
        assert (
            "code='unique'" in errors and "program_id" in errors
        )  # this means that the error was just that the program IDs already exist
    else:
        assert response.status_code >= 200 and response.status_code < 300

    test_loc = "https://raw.githubusercontent.com/CanDIG/katsu/develop/chord_metadata_service/mohpackets/data/small_dataset/synthetic_data/Donor.json"
    response = requests.get(test_loc)
    assert response.status_code == 200
    response = requests.post(
        f"{ENV['CANDIG_URL']}/katsu/v2/ingest/donors",
        headers=headers,
        json=response.json(),
    )
    print(response.json())
    if response.status_code >= 400:
        errors = response.json()["error during ingest_donors"]
        assert (
            "code='unique'" in errors and "donor_id" in errors
        )  # this means that the error was just that the program IDs already exist
    else:
        assert response.status_code >= 200 and response.status_code < 300


# Can each user only see results from their authorized datasets?
def user_auth_datasets():
    return [
        ("CANDIG_SITE_ADMIN", "SYNTHETIC-2", "SYNTHETIC-1"),
        ("CANDIG_NOT_ADMIN", "SYNTHETIC-1", "SYNTHETIC-2"),
    ]


@pytest.mark.parametrize("user, dataset, not_dataset", user_auth_datasets())
def test_katsu_users(user, dataset, not_dataset):
    username = ENV[f"{user}_USER"]
    password = ENV[f"{user}_PASSWORD"]
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {get_token(username=username, password=password)}",
    }

    response = requests.get(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/", headers=headers
    )
    programs = list(map(lambda x: x["program_id"], response.json()["results"]))
    print(programs)
    assert dataset in programs
    assert not_dataset not in programs

    response = requests.get(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/donors/", headers=headers
    )
    assert len(response.json()) > 0
    print(response.json())
    donors = list(map(lambda x: x["program_id"], response.json()["results"]))
    print(donors)
    assert dataset in donors
    assert not_dataset not in donors


def test_katsu_delete():
    test_loc = "https://raw.githubusercontent.com/CanDIG/katsu/develop/chord_metadata_service/mohpackets/data/small_dataset/synthetic_data/Program.json"
    response = requests.get(test_loc)
    assert response.status_code == 200

    site_admin_token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    program_data = response.json()
    program_ids = [item["program_id"] for item in program_data]

    for program_id in program_ids:
        response = requests.delete(
            f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/{program_id}/",
            headers=headers,
        )
        assert (
            response.status_code == 204
        ), f"Failed to delete program '{program_id}'. Status code: {response.status_code}"
        print(f"Deletion of program '{program_id}' was successful.")


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
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/datasets/{first_sample['program_id']}",
        headers=headers,
    )

    assert response.status_code == 200

    assert len(response.json()["drsobjects"]) > 0
    drs_obj = response.json()["drsobjects"].pop(0)
    drs_obj_match = re.match(r"^(.+)\/(.+?)$", drs_obj)
    if drs_obj_match is not None:
        host = drs_obj_match.group(1)
        drs_obj_name = drs_obj_match.group(2)

        # assign the first member of this dataset to the sample
        sample_drs_obj = {
            "id": first_sample["submitter_sample_id"],
            "contents": [{"drs_uri": [drs_obj], "name": drs_obj_name, "id": "genomic"}],
            "version": "v1",
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
