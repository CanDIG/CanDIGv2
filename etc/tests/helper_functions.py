
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
    

def add_opa_dataset(program_id):
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
        "program": program_id
    }

    response = requests.post(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}/email/{test_data['email']}", headers=headers)
    # when the user has admin access, they should be allowed
    print(f"129 {response.json()}, {response.status_code}")

def remove_opa_dataset(program_id):
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
        "program": program_id
    }

    requests.delete(f"{ENV['CANDIG_URL']}/ingest/program/{test_data['program']}/email/{test_data['email']}", headers=headers)

def show_opa_datasets(user):
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

def clean_up_program(program_id):
    """
    Deletes a dataset and all related objects. Expected 204
    """
    site_admin_token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {site_admin_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/program/{program_id}/",
        headers=headers,
    )

    delete_response = requests.delete(
        f"{ENV['CANDIG_URL']}/genomics/ga4gh/drs/v1/cohorts/{program_id}",
        headers=headers
    )


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
    

def show_katsu_programs_info():
    response = requests.get(
        f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v2/discovery/programs/"
    ).json()
    print(response)

def show_katsu_authorised_program(user_type, program):
    token = get_token(
        username=ENV[f"{user_type}_USER"],
        password=ENV[f"{user_type}_PASSWORD"],
    )
    print(token)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    print(f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/?program_id={program}")
    response = requests.get(
        f"{ENV['CANDIG_URL']}/katsu/v2/authorized/programs/?program_id={program}", headers=headers
    ).json()
    print(response)

def get_htsget_sample_metadata(sample_id):
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/genomics/htsget/v1/samples/{sample_id}", headers=headers)
    print(response.json())
    return response.json()


def get_htsget_variant(chrom: str, start: int, end: int):
    token = get_token(
        username=ENV["CANDIG_SITE_ADMIN_USER"],
        password=ENV["CANDIG_SITE_ADMIN_PASSWORD"],
    )
    
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
    response = requests.post(f"{ENV['CANDIG_URL']}/genomics/beacon/v2/g_variants",
        headers=headers,
        json=payload)
    
    print(response.json())