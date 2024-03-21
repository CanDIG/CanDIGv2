
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
import pprint

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../..")
sys.path.insert(0, os.path.abspath(f"{REPO_DIR}"))

from settings import get_env

ENV = get_env()


def get_token(username: str=None, password: str=None) -> str:
    """ Get an access token user a user id and password
    
    Args:
        username: The identifier for the user
        password: The password for the user
    
    Returns:
        A jwt access token string for the specified user
    """
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
    else:
        return None
    

def get_user_type_token(user_type):
    """ Get a token for a particular CANDIG user type
    
    Args:
        user_type: one of CANDIG_SITE_ADMIN or CANDIG_NOT_ADMIN

    Returns:
        access token for that user type
    """
    token = get_token(
        username=ENV[f"{user_type}_USER"],
        password=ENV[f"{user_type}_PASSWORD"],
    )
    return token
    

def add_program_authorization(program_id, user_email=ENV["CANDIG_SITE_ADMIN_USER"] + "@test.ca"):
    """ Add program authorisation for a particular user_email

    Args:
        program_id: The program identifier to authorize
        user_email: The user email of the user to give access

    Returns:
        The response from the API call showing updated authorization
    
    """
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    test_data = {
        "email": user_email,
        "program": program_id
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}/email/{test_data['email']}", headers=headers)
    # when the user has admin access, they should be allowed
    print(f"129 {response.json()}, {response.status_code}")
    return response

def remove_program_authorization(program_id, user_email):
    """ Remove program authorisation for a particular user_email

    Args:
        program_id: The program identifier to remove authorization
        user_email: The user email of the user to give access

    Returns:
        The response from the API call showing updated authorization
    
    """
    token = get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.delete(f"{ENV['CANDIG_URL']}/ingest/program/{program_id}/email/{user_email}", headers=headers)
    return response

def show_authorized_programs(user_type):
    """ Show authorized programs for a particular CanDIG user type
    
    Args: 
        user_type: one of CANDIG_SITE_ADMIN or CANDIG_NOT_ADMIN

    Returns:
        Response showing the user permissions to programs
    """
    token = get_user_type_token(user_type)
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
    return response

def clean_up_program(program_id):
    """
    Deletes a program and all related objects in katsu and htsget. 

    Args:
        program_id: The program identifier to be deleted
    """
    site_admin_token = get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    clean_up_katsu_program(program_id)
    clean_up_htsget_program(program_id)


def ingest_test_data():
    clean_up_program("SYNTHETIC-1")
    clean_up_program("SYNTHETIC-2")

    with open("lib/candig-ingest/candigv2-ingest/tests/small_dataset_clinical_ingest.json", 'r') as f:
        test_data = json.load(f)

    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/clinical", headers=headers, json=test_data)
    print(response.json())

    with open("lib/candig-ingest/candigv2-ingest/tests/genomic_ingest.json", 'r') as f:
        test_data = json.load(f)

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
    

def get_katsu_programs_info() -> dict:
    response = requests.get(
        f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v2/discovery/programs/"
    ).json()
    return response


def get_katsu_authorised_program(user_type, program) -> dict:
    token = get_user_type_token(user_type)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/?program_id={program}", headers=headers
    ).json()
    return response


def get_htsget_sample_metadata(sample_id, user_type):
    token = get_user_type_token(user_type)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/samples/{sample_id}", headers=headers)
    print(response.json())
    return response.json()


def get_beacon_variant(chrom: str, start: int, end: int, user_type: str) -> dict:
    token = get_user_type_token(user_type)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    
    payload = {
        'query': {
            'requestParameters': {
                'assemblyId': 'hg38',
                'referenceName': chrom,
                'start': [start],
                'end': [end]
            }
        },
        'meta': {
            'apiVersion': 'v2'
        }
    }
    print(f"Querying: {ENV['CANDIG_URL']}/genomics/beacon/v2/g_variants")
    print(f"with payload: {payload}")
    response = requests.post(f"{ENV['CANDIG_URL']}/genomics/beacon/v2/g_variants",
        headers=headers,
        json=payload)
    print(response.json())
    return response.json()


def get_beacon_gene(gene: str, user_type: str) -> dict:
    token = get_user_type_token(user_type)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    
    payload = {
        'query': {
            'requestParameters': {
                'assemblyId': 'hg38',
                'geneId': gene
            }
        },
        'meta': {
            'apiVersion': 'v2'
        }
    }
    print(f"Querying: {ENV['CANDIG_URL']}/genomics/beacon/v2/g_variants")
    print(f"with payload: {payload}")
    response = requests.post(f"{ENV['CANDIG_URL']}/genomics/beacon/v2/g_variants",
        headers=headers,
        json=payload)
    print(response.json())
    return response.json()


def clean_up_katsu_program(program_id, user_type):
    """
    Deletes a program from katsu. Expected 204

    Args:
        program_id: the program identifier to be deleted from katsu
        user_type: The type of user with access to the program
    """
    print(f"katsu program metadata to be deleted: {program_id}:")
    print(get_katsu_authorised_program(user_type, program_id))

    site_admin_token = get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    print(f"requests.delete on endpoint: {ENV['CANDIG_URL']}/katsu/v2/authorized/program/{program_id}/")
    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/program/{program_id}/",
        headers=headers,
    )
    print(delete_response.status_code)
    return(delete_response)


def clean_up_htsget_program(program_id, object_id, user_type):
    """
    Deletes a htsget program and all related objects. Expected 200
    """
    site_admin_token = get_user_type_token("CANDIG_SITE_ADMIN")
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/{program_id}",
        headers=headers
    )
    return(delete_response)


def index_variant_file(genomic_file_id):
    site_admin_token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/{genomic_file_id}/index",
        headers=headers)
    
    print(response.json())
    return response.json()

def ingest_htsget():
    with open("lib/candig-ingest/candigv2-ingest/tests/genomic_ingest.json", 'r') as f:
        test_data = json.load(f)
        synth_2_test_data = [x for x in test_data if x['program_id'] == "SYNTHETIC-2"]

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

def get_drs_object(genomic_file_id, user_type):
    token = get_user_type_token(user_type)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    print(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects/{genomic_file_id}")
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/objects/{genomic_file_id}",
        headers=headers)
    return response.json()


def get_htsget_program(program_id, user_type):
    token = get_user_type_token(user_type)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/{program_id}",
                            headers=headers)
    return response.json()

