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
from copy import deepcopy
import helper_functions as helpers
import pprint
import time

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../..")
sys.path.insert(0, os.path.abspath(f"{REPO_DIR}"))

from settings import get_env

ENV = get_env()


def test_keycloak():
    """ Test whether keycloak responds
    
    If passing asserts:
        *
    """
    response = requests.get(
        f"{ENV['KEYCLOAK_PUBLIC_URL']}/auth/realms/candig/.well-known/openid-configuration"
    )
    assert response.status_code == 200
    assert "grant_types_supported" in response.json()


def test_get_token():
    """ Test whether getting a site admin token works
    
    If passing asserts:
        * A token is returned for CANDIG_SITE_ADMIN credentials
    """
    assert helpers.get_user_type_token("CANDIG_SITE_ADMIN")


def test_tyk():
    """ Test whether tyk can communicate with all running services 
    
    If passing asserts:
        * Tyk can communicate with:
          * htsget drs API
          * katsu API
          * Federation API
          * Opa API
          * Query API
    """
    headers = {
        "Authorization": f"Bearer {helpers.get_user_type_token('CANDIG_SITE_ADMIN')}"
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


def user_programs() -> list:
    """ Returns List of users with programs that they are authorized for in Opa """
    return [
        ("CANDIG_SITE_ADMIN", "SYNTHETIC-2"),
        ("CANDIG_NOT_ADMIN", "SYNTHETIC-1"),
    ]


@pytest.mark.parametrize("user, program", user_programs())
def test_opa_programs(user: str, program: str):
    """ Test that CANDIG users have the expected authorization permissions in Opa

    Args:
        user: One of CANDIG_SITE_ADMIN or CANDIG_NOT_ADMIN
        program: Name of the program that should be authorized

    If passing asserts:
        * The given user has authorization for the given program
    """
    token = helpers.get_user_type_token(user)
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
    assert program in response.json()["result"]


## Can we add a program to one of the users?
def test_add_opa_program():
    """ Test that the site admin user can add program authorization for a user
    
    If passing asserts:
        * A site admin can add authorization to itself for a program
    """
    token = helpers.get_token(
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

    test_opa_programs("CANDIG_SITE_ADMIN", test_data["program"])

    response = requests.delete(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}/email/{test_data['email']}", headers=headers)
    assert response.status_code == 200
    assert test_data['program'] not in response.json()["access"]["controlled_access_list"][test_data["email"]]


def user_admin() -> list:
    """ Returns list of CANDIG users and whether or not they are site admins """
    return [
        ("CANDIG_SITE_ADMIN", True),
        ("CANDIG_NOT_ADMIN", False),
    ]


@pytest.mark.parametrize("user, is_admin", user_admin())
def test_site_admin(user: str, is_admin: bool):
    """ Test whether each CANDIG user type has the correct user permissions 
    
    Args:
        user: user type, one of CANDIG_SITE_ADMIN or CANDIG_NOT_ADMIN
        is_admin: Boolean indicating whether or not ther user is a site administrator
    """
    payload = {"input": {}}
    token = helpers.get_user_type_token(user)

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


def test_vault():
    """ Test whether a site admin can add a aws access key to Vault
    
    If passing asserts:
        * The vault aws s3 token can be deleted (if it already exists)
        * The vault aws s3 token can be added to the vault (when it doesn't exist)
        * The vault aws s3 token can be retreived and matches what was sent

    """
    site_admin_token = helpers.get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    # confirm that this works with the CANDIG_S3_TOKEN:
    headers["X-Vault-Token"] = ENV["VAULT_S3_TOKEN"]
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


def test_ingest_katsu():
    """ Test ingesting synthetic clinical data into katsu 
    
    If passing asserts:
        * Non site admin user cannot ingest clinical data 
        * Site admin user can ingest clinical data
        * There are no errors in the ingested clinical data
        * The expected number of objects from the clinical data were ingested
        * The ingested programs are returned from katsu
    """
    helpers.clean_up_katsu_program("SYNTHETIC-2", "CANDIG_SITE_ADMIN")
    helpers.clean_up_katsu_program("SYNTHETIC-1", "CANDIG_NOT_ADMIN")

    with open("lib/candig-ingest/candigv2-ingest/tests/small_dataset_clinical_ingest.json", 'r') as f:
        test_data = json.load(f)

    token = helpers.get_user_type_token("CANDIG_NOT_ADMIN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/clinical", headers=headers, json=test_data)
    # when the user has no admin access, they should not be allowed
    assert response.status_code == 401

    token = helpers.get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/clinical", headers=headers, json=test_data)
    # when the user has admin access, they should be allowed
    print(response.json())
    assert response.status_code == 201
    assert len(response.json()["SYNTHETIC-2"]["errors"]) == 0
    assert len(response.json()["SYNTHETIC-1"]["errors"]) == 0
    assert len(response.json()["SYNTHETIC-2"]["results"]) == 15
    assert len(response.json()["SYNTHETIC-1"]["results"]) == 14
    katsu_response = helpers.get_katsu_programs_info()
    assert len(katsu_response) == 2
    katsu_programs = [x['program_id'] for x in katsu_response]
    assert 'SYNTHETIC-1' in katsu_programs
    assert 'SYNTHETIC-2' in katsu_programs


## Run the main htsget test suite
# def test_htsget():
#     old_val = os.environ.get("TESTENV_URL")
#     os.environ[
#         "TESTENV_URL"
#     ] = f"{ENV['CANDIG_ENV']['HTSGET_PUBLIC_URL']}"
#     retcode = pytest.main(["-x", "lib/htsget/htsget_app/tests/test_htsget_server.py", "-k", "test_remove_objects or test_post_objects or test_index_variantfile"])
#     if old_val is not None:
#         os.environ["TESTENV_URL"] = old_val
#     print(retcode)
#     assert retcode == pytest.ExitCode.OK


## Can we add samples to Opa-controlled dataset?
# def test_htsget_add_sample_to_dataset():
#     site_admin_token = helpers.get_user_type_token("CANDIG_SITE_ADMIN")
#     headers = {
#         "Authorization": f"Bearer {site_admin_token}",
#         "Content-Type": "application/json; charset=utf-8",
#     }

#     TESTENV_URL = (
#         ENV["CANDIG_ENV"]["HTSGET_PUBLIC_URL"]
#         .replace("http://", "drs://")
#         .replace("https://", "drs://")
#     )
#     # Delete cohort SYNTHETIC-1
#     response = requests.delete(
#         f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTHETIC-1",
#         headers=headers,
#     )

#     # Add NA18537 and multisample_1 to cohort SYNTHETIC-1, which is only authorized for user1:
#     payload = {
#         "id": "SYNTHETIC-1",
#         "drsobjects": [f"{TESTENV_URL}/NA18537", f"{TESTENV_URL}/multisample_1"],
#     }

#     response = requests.post(
#         f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts",
#         headers=headers,
#         json=payload,
#     )
#     response = requests.get(
#         f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTHETIC-1",
#         headers=headers,
#     )
#     print(response.json())
#     assert f"{TESTENV_URL}/multisample_1" in response.json()["drsobjects"]
#     assert f"{TESTENV_URL}/multisample_2" not in response.json()["drsobjects"]

#     # Delete cohort SYNTHETIC-2
#     response = requests.delete(
#         f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTHETIC-2",
#         headers=headers,
#     )

#     # Add NA20787 and multisample_2 to cohort SYNTHETIC-2, which is only authorized for user2:
#     payload = {
#         "id": "SYNTHETIC-2",
#         "drsobjects": [f"{TESTENV_URL}/NA20787", f"{TESTENV_URL}/multisample_2"],
#     }

#     response = requests.post(
#         f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts",
#         headers=headers,
#         json=payload,
#     )
#     response = requests.get(
#         f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTHETIC-2",
#         headers=headers,
#     )
#     print(response.json())
#     assert f"{TESTENV_URL}/multisample_2" in response.json()["drsobjects"]
#     assert f"{TESTENV_URL}/multisample_1" not in response.json()["drsobjects"]


def user_access_list() -> list:
    """ Returns list of user, genomic object and boolean """
    return [
        (   # user1 can access multisample_1 as part of SYNTHETIC-1
            "CANDIG_NOT_ADMIN",
            "multisample_1",
            True,
        ),  
        (   # user1 cannot access chr22-v5a-phase3.vcf as part of SYNTHETIC-2
            "CANDIG_NOT_ADMIN", 
            "chr22-v5a-phase3.vcf", 
            False
        ),
        (   # user2 cannot access multisample_1 as part of SYNTHETIC-1
            "CANDIG_SITE_ADMIN",
            "multisample_1",
            False,
        ),  
        (   # user2 can access chr22-v5a-phase3.vcf as part of SYNTHETIC-2
            "CANDIG_SITE_ADMIN", 
            "chr22-v5a-phase3.vcf", 
            True
        )
    ]


@pytest.mark.parametrize("user, obj, access", user_access_list())
def test_htsget_access_data(user: str, obj: str, access: bool):
    """ Tests whether users can access the expected htsget genomic objects
    
    Args:
        user: The user type, not of CANDIG_NOT_ADMIN or CANDIG_SITE_ADMIN
        obj: The genomic_file_id for an ingested genomic object
        access: Whether or not the user should have access to the given object

    If passing asserts:
        * The user has the expected access to the genomic object
    """
    headers = {
        "Authorization": f"Bearer {helpers.get_user_type_token(user)}",
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


def test_ingest_htsget():
    """ Test ingesting genomic data that links to the clinical synthetic data already ingested in `test_ingest_katsu()`
    
    If passing asserts:
        * Non site admin user cannot ingest genomic data
        * Genomic data ingests as expected
        * Ingested genomic data has no errors
    """
    assert(helpers.clean_up_htsget_program('SYNTHETIC-1', "multisample_1", "CANDIG_NOT_ADMIN").status_code == 200)
    assert(helpers.clean_up_htsget_program('SYNTHETIC-2', "chr22-v5a-phase3.vcf", "CANDIG_SITE_ADMIN").status_code == 200)

    # Wait to make sure deletion is completed
    time.sleep(10)

    with open("lib/candig-ingest/candigv2-ingest/tests/small_dataset_genomic_ingest.json", 'r') as f:
        test_data = json.load(f)

    token = helpers.get_user_type_token("CANDIG_NOT_ADMIN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/genomic", headers=headers, json=test_data)
    # when the user has no admin access, they should not be allowed to ingest
    assert response.status_code == 403

    token = helpers.get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/genomic", headers=headers, json=test_data)
    # when the user has admin access, they should be allowed to ingest
    assert response.status_code == 200
    # print(response.json())

    user_dict = {
        "SYNTHETIC-1": "CANDIG_NOT_ADMIN",
        "SYNTHETIC-2": "CANDIG_SITE_ADMIN"
    }

    # For each file ingested, check for errors and correct object structure is returned
    for id, ingest_response in response.json().items():
        user_type = user_dict[ingest_response['genomic']['cohort']]
        for sample in ingest_response['sample']:
            print("get sample:")
            print(helpers.get_htsget_sample_metadata(sample['name'], user_type))
            for file in sample['contents']:
                print("get object")
                print(helpers.get_drs_object(file['id'], user_type))
        if len(ingest_response['errors']) > 0:
            print(id)
            print("ingest response errors:")
            print(ingest_response['errors'])
        # TODO: Uncomment when this bug is fixed
        # assert len(ingest_response['errors']) == 0
        assert "genomic" in ingest_response
        assert "sample" in ingest_response
    

def test_sample_metadata():
    """ Test whether the site admin can access sample metadata from htsget
    
    If passing asserts:
        * Site admin can access SAMPLE_REGISTRATION_NULL_01 and gets a valid response
        * The expected genomic object is linked to the sample
    """
    token = helpers.get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/samples/SAMPLE_REGISTRATION_NULL_01", headers=headers)
    print(response.json())
    assert "genomes" in response.json()
    assert "HG00100-cram" in response.json()["genomes"]


def test_index_success():
    """ Test that indexing an ingested vcf was indexed
    
    If passing asserts:
        * The response for the file `chr22-v5a-phase3.vcf` has the `indexed` item
        * The indexing for that file is complete
    """
    token = helpers.get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    time.sleep(60)
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects/chr22-v5a-phase3.vcf", headers=headers)
    print(response.json())
    assert "indexed" in response.json()
    assert response.json()['indexed'] == 1


## Does Beacon return the correct level of authorized results?
def beacon_access():
    return [
        (
            "CANDIG_NOT_ADMIN",
            "NC_000021.9:g.5030847T>A",
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
        "Authorization": f"Bearer {helpers.get_token(username=username, password=password)}",
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


def samples_to_verify() -> list:
    """ Returns list of ingested genomic files and permission associations to test """
    return [
        (
            "HG00100-cram",
            "HG00100.mapped.ILLUMINA.bwa.GBR.exome.20121211.bam.cram",
            "read",
            "user2"
        ),
        (
            "HG00100-chrom20-bam",
            "HG00100.chrom20.ILLUMINA.bwa.GBR.exome.20121211.bam",
            "read",
            "user2"
        ),
        (
            "chr22-v5a-phase3.vcf",
            "ALL.chr22.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz",
            "variant",
            "user2"
        )  
    ]


@pytest.mark.parametrize("genomic_file_id, main_file_name, data_type, user", samples_to_verify())
def test_verify_htsget(genomic_file_id: str, main_file_name: str, data_type: str, user: str):
    """ Verify all genomic objects from the test data have been uploaded and have appropriate permissions 
    
    Args:
        genomic_file_id: genomic_file_id specified in the genomic json
        main_file_name: main.name specified in the genomic json
        data_type: data type specified in the genomic json (read or variant)
        user: user with access to the given genomic object (user1 or user2)
    
    If passing asserts:
        * that the given user can retreive the given genomic object
        * that calling the verify endpoint on an object with invalid url will return False
        * that calling the verify endpoint on an object with valid url will return True
    """
    if user == "user1":
        token = helpers.get_token(
            username=ENV["CANDIG_NOT_ADMIN_USER"],
            password=ENV["CANDIG_NOT_ADMIN_PASSWORD"],
        )
    elif user == "user2":
        token = helpers.get_token(
            username=ENV["CANDIG_SITE_ADMIN_USER"],
            password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    # get a GenomicDataDrsObject
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects/{main_file_name}", headers=headers)
    assert response.status_code == 200
    new_json = response.json()
    print(new_json)

    # mess up its access_url
    if new_json['access_methods'][0]['type'] == 's3':
        old_url = new_json["access_methods"][0]["access_id"]
        new_json["access_methods"][0]["access_id"] = \
        f"{new_json["access_methods"][0]["access_id"][:10]}/test/{new_json["access_methods"][0]["access_id"]}"
    elif new_json['access_methods'][0]['type'] == 'file':
        old_url = new_json["access_methods"][0]["access_url"]["url"]
        new_json["access_methods"][0]["access_url"]["url"] += "test"

    post_token = helpers.get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    post_headers = {
        "Authorization": f"Bearer {post_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects", headers=post_headers, json=new_json)

    # verification should give us a False result
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/{data_type}s/{genomic_file_id}/verify", headers=headers)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["result"] == False

    # fix it back
    if new_json['access_methods'][0]['type'] == 's3':
        new_json["access_methods"][0]["access_id"] = old_url
    else:
        new_json["access_methods"][0]["access_url"]["url"] = old_url
    response = requests.post(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects", headers=post_headers, json=new_json)

    # verification should give us a True result
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/{data_type}s/{genomic_file_id}/verify", headers=headers)
    assert response.status_code == 200
    assert response.json()["result"] == True


def test_cohort_status():
    token = helpers.get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/SYNTHETIC-2/status", headers=headers)
    assert "index_complete" in response.json()
    assert len(response.json()['index_complete']) > 0


## Federation tests:


# Do we have at least one server present?
def test_server_count():
    token = helpers.get_token(
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
    token = helpers.get_token(
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

    token = helpers.get_token(
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
    token = helpers.get_token(
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
    """ Test all ingested clinical data for expected summary counts
    
    If passing asserts:
        * Query returns a valid response on the query/query endpoint (response: 200)
        * The expected number of donors in authorised for CANDIG_SITE_ADMIN_USER is 7
        * The expected counts of summary stats for CANDIG_SITE_ADMIN_USER matches the true counts
    """
    token = helpers.get_token(
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
    assert response and len(response["results"]) == 7

    # Check the summary stats as well
    summary_stats = response["summary"]
    print(summary_stats)
    expected_response = {
        'age_at_diagnosis': {
            '0-19 Years': 1,
            '50-59 Years': 2,
            '60-69 Years': 1
        },
        'cancer_type_count': {
            'Adrenal gland': 1,
            'Base of tongue': 1,
            'Floor of mouth': 2,
            'Hypopharynx': 1,
            'Other and unspecified female genital organs': 1,
            'Other and unspecified major salivary glands': 1,
            'Other and unspecified parts of biliary tract': 1,
            'Other and unspecified parts of mouth': 3,
            'Other endocrine glands and related structures': 2,
            'Pancreas': 1,
            'Penis': 1,
            'Skin': 1,
            'Testis': 2
        },
        'patients_per_cohort': {
            'SYNTHETIC-2': 7
        },
        'treatment_type_count': {
            'Bone marrow transplant': 1,
            'Chemotherapy': 2,
            'Hormonal therapy': 2,
            'Immunotherapy': 2,
            'No treatment': 1,
            'Other targeting molecular therapy': 1,
            'Photodynamic therapy': 2,
            'Radiation therapy': 4,
            'Stem cell transplant': 2,
            'Surgery': 2
        }
    }
    for category in expected_response.keys():
        for value in expected_response[category].keys():
            assert summary_stats[category][value] == expected_response[category][value]

# Test 2: Search for a specific donor
def test_query_donor_search():
    """ Test specific query result
    
    If passing asserts:
        * Query returns a valid response on the query/query endpoint with treatment param (response: 200)
        * The expected number of donors with treatment.treatment_type == "Chemotherapy" for CANDIG_SITE_ADMIN_USER is 2
        * The expected counts of summary stats for donors with treatment.treatment_type == "Chemotherapy" for 
            CANDIG_SITE_ADMIN_USER matches the true counts
    """
    token = helpers.get_token(
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
    assert response and len(response["results"]) == 2

    # Check the summary stats as well
    summary_stats = response["summary"]
    print(summary_stats)
    expected_response = {
        'age_at_diagnosis': {
            '50-59 Years': 2
        },
        'cancer_type_count': {
            'Floor of mouth': 2,
            'Other and unspecified parts of mouth': 2
        },
        'patients_per_cohort': {
            'SYNTHETIC-2': 2
        },
        'treatment_type_count': {
            'Bone marrow transplant': 1,
            'Chemotherapy': 2,
            'Hormonal therapy': 2,
            'Immunotherapy': 2,
            'No treatment': 1,
            'Other targeting molecular therapy': 1,
            'Photodynamic therapy': 2,
            'Radiation therapy': 3,
            'Stem cell transplant': 2,
            'Surgery': 2
        }
    }
    for category in expected_response.keys():
        for value in expected_response[category].keys():
            assert summary_stats[category][value] == expected_response[category][value]
    assert True


def test_query_genomic():
    # tests that a request sent via query to htsget-beacon properly prunes the data
    token = helpers.get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    params = {
        "chrom": "chr22:16050000-16050600",
        "assembly": "hg38"
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/query/query", headers=headers, params=params
    )
    print(response.json()["results"])
    assert response and len(response.json()["results"]) == 1


def test_query_discovery():
    katsu_response = requests.get(
        f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v2/discovery/programs/"
    ).json()
    query_response = requests.get(
        f"{ENV['CANDIG_ENV']['TYK_QUERY_API_TARGET']}/discovery/programs"
    ).json()

    # Ensure that each category in metadata corresponds to something in the site
    for category in query_response["site"]["required_but_missing"]:
        for field in query_response["site"]["required_but_missing"][category]:
            for total_type in query_response["site"]["required_but_missing"][category][field]:
                total = query_response["site"]["required_but_missing"][category][field][total_type]
                for program in katsu_response:
                    if category in program["metadata"]['required_but_missing'] and field in program["metadata"]['required_but_missing'][category]:
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


def test_clean_up_program(program_id: str, genomic_object_id: str, user_type: str):
    """ Tests deleting a program and all related objects in katsu and htsget

    Args:
        program_id: the program to be deleted
        genomic_object_id: a genomic object in the program to check deletion
        user_type: A user with access to the program to check deletion

    If passing asserts:
        * The program deletion returns the expected success response code in katsu and htsget
    """

    delete_response = helpers.clean_up_katsu_program(program_id, user_type)
    assert (
        delete_response.status_code == HTTPStatus.NO_CONTENT or delete_response.status_code == HTTPStatus.NOT_FOUND
    ), f"CLEAN_UP_PROGRAM Expected status code {HTTPStatus.NO_CONTENT}, but got {delete_response.status_code}."
    f" Response content: {delete_response.content}"
    # Check the deleted program has no items in katsu
    assert(len(helpers.get_katsu_authorised_program(user_type, program_id)['items']) == 0)

    delete_response = helpers.clean_up_htsget_program(program_id, genomic_object_id, user_type)
    assert delete_response.status_code == 200


def test_clean_up():
    """ Clean up all data ingested into the platform during the running of all tests in this file.
    
    Can be toggled on and off with the `KEEP_TEST_DATA` argument in the .env file

    If passing asserts:
        * data was cleaned from katsu
        * data was cleaned from htsget
    """

    test_clean_up_program("SYNTHETIC-1", "multisample_1", "CANDIG_NOT_ADMIN")
    test_clean_up_program("SYNTHETIC-2", "chr22-v5a-phase3.vcf", "CANDIG_SITE_ADMIN")

    # clean up test_htsget
    # old_val = os.environ.get("TESTENV_URL")
    # os.environ["TESTENV_URL"] = f"{ENV['CANDIG_ENV']['HTSGET_PUBLIC_URL']}"
    # pytest.main(["-x", "lib/htsget/htsget_app/tests/test_htsget_server.py", "-k", "test_remove_objects"])
    # if old_val is not None:
    #     os.environ["TESTENV_URL"] = old_val

