import json
import os
import pytest
import requests
import sys

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../..")
sys.path.insert(0, os.path.abspath(f"{REPO_DIR}"))

from settings import get_env
from site_admin_token import get_site_admin_token

ENV = get_env()

def test_get_token():
    assert get_site_admin_token()

def make_fanout(headers, body):
    return requests.post(
        f"{ENV['CANDIG_URL']}/federation/v1/fanout", headers=headers, json=body, timeout=10
    )

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
        f"{ENV['KEYCLOAK_PUBLIC_URL']}/auth/realms/{ENV['KEYCLOAK_REALM']}/protocol/openid-connect/token",
        data=payload,
    )
    if response.status_code == 200:
        if access_token:
            return response.json()["access_token"]
        return response.json()["refresh_token"]


## Service info test: can we get a response from Tyk for all of our services?
def test_service_info():
    modules = ENV['CANDIG_ENV']['CANDIG_MODULES'].split(" ")
    headers = {
        "Authorization": f"Bearer {get_site_admin_token()}"
    }
    endpoints = {
        # all of these endpoints should return JSON
        "htsget": f"ga4gh/drs/v1/service-info",
        "katsu": f"v3/service-info",
        # "rnaget": f"service-info",
        # "federation": f"v1/service-info",
        # "opa": f"v1/data/service/service-info",
        "query": f"service-info",
        # "candig-ingest": f"service-info",
    }
    responses = []
    for module in modules:
        if module in endpoints:
            endpoint = endpoints[module]
            body = {
                "method": "GET",
                "path": endpoint,
                "payload": {},
                "service": module
            }
            response = make_fanout(headers, body)
            # Three things to catch:
            # 1: The entire request failed
            status_code = response.status_code
            if status_code != 200:
                print(f"Entire request failed: {status_code} {response.text}")
                continue

            # 2: A particular server errored out
            servers_ok = {}
            try:
                r = response.json()
                for server in r:
                    if server["status"] != 200:
                        servers_ok[server["location"]["name"]] = server["message"]
                    else:
                        servers_ok[server["location"]["name"]] = "ok"
                responses.append(servers_ok)
            except requests.JSONDecodeError as e:
                status_code = 500
                responses.append("Entire request failed: " + response.text)
            print(f"{module}: {status_code}")
    assert all(response[server] == "ok" for response in responses for server in response)


# Need to call this from the other server somehow?
def test_preapprove_user():
    headers = {
        "Authorization": f"Bearer {get_site_admin_token()}"
    }
    body = ["user3@test.ca"]
    preapproval_url = f"{ENV['CANDIG_URL']}/ingest/user/preapproved"
    response = requests.post(
        preapproval_url, headers=headers, json=body, timeout=10
    )
    assert response.status_code == 200, f"Preapproval to {preapproval_url} failed with: {response.text}"


def test_query_endpoint():
    # Create user3@test.ca (should be preapproved)
    # create_keycloak_user("user3@test.ca", "testfederation", "user3@test.ca", "user3", "test")

    # Get user3@test.ca token
    headers = {
        "Authorization": f"Bearer {get_token('user3@test.ca', 'testfederation')}"
    }

    # Request authorization
    response = requests.post(
        f"{ENV['CANDIG_URL']}/ingest/user/pending/request", headers=headers, timeout=10
    )
    assert response.status_code == 200, f"Could not request authorization: {response.status_code} {response.text}"

    # Test query endpoint
    body = {
        "method": "GET", 
        "path": "query",
        "payload": {},
        "service": "query"
    }
    response = make_fanout(headers, body)
    
    # Verify response
    assert response.status_code == 200, f"Query endpoint failed with: {response.text}"
    
    try:
        r = response.json()
        for server in r:
            assert server["status"] == 200, f"Server {server['location']['name']} failed with: {server['message']}"
    except requests.JSONDecodeError:
        assert False, f"Invalid JSON response: {response.text}"

def create_keycloak_user(username, password, email, first_name, last_name):
    """
    Create a user in Keycloak directly using the admin API.
    
    Args:
        username (str): The username for the new user
        password (str): The password for the new user
        email (str): The email address for the new user
        first_name (str): The first name of the user
        last_name (str): The last name of the user
    
    Returns:
        dict: The response from the Keycloak API
    """
    # Step 1: Get admin token
    admin_token = get_site_admin_token()
    
    # Step 2: Create user
    users_url = f"{ENV["KEYCLOAK_PUBLIC_URL"]}/auth/admin/realms/{ENV["KEYCLOAK_REALM"]}/users"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    user_data = {
        "username": username,
        "enabled": True,
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "credentials": [
            {
                "type": "password",
                "value": password,
                "temporary": False
            }
        ]
    }
    
    create_response = requests.post(users_url, headers=headers, json=user_data)
    if create_response.status_code not in [201, 204]:
        raise Exception(f"Failed to create user: {create_response.text}")
    
    # Get the user ID from the Location header
    user_id = None
    if "Location" in create_response.headers:
        location = create_response.headers["Location"]
        user_id = location.split("/")[-1]
    
    return {
        "status": "success",
        "user_id": user_id,
        "message": f"User {username} created successfully"
    }

def test_ingest_federated_dataset():
    # Get admin token for authorization
    token = get_site_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # Create program authorization for TEST_FEDERATE
    test_program = {
        "program_id": "TEST_FEDERATE",
        "program_curators": [],
        "team_members": ["user3@test.ca"]
    }

    # Add the program
    response = requests.post(
        f"{ENV['CANDIG_URL']}/ingest/program",
        headers=headers,
        json=test_program
    )
    assert response.status_code == 200

    # Load the test data file
    data_file = f"{REPO_DIR}/lib/candig-ingest/candigv2-ingest/tests/{ENV['CANDIG_ENV']['CANDIG_SITE_LOCATION']}-SYNTH_01.json"
    with open(data_file) as f:
        ingest_data = json.load(f)

    # Update the program ID in the data
    for donor in ingest_data["donors"]:
        donor["program_id"] = "TEST_FEDERATE"

    # Ingest the dataset
    response = requests.post(
        f"{ENV['CANDIG_URL']}/ingest/clinical",
        headers=headers,
        json=ingest_data
    )
    assert response.status_code == 200

