import json
import os
import pytest
import re
import requests
import subprocess
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
def get_token(username=None, password=None, access_token=False, realm=ENV['KEYCLOAK_REALM']):
    payload = {
        "client_id": ENV["CANDIG_CLIENT_ID"],
        "client_secret": ENV["CANDIG_CLIENT_SECRET"],
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "openid",
    }
    response = requests.post(
        f"{ENV['KEYCLOAK_PUBLIC_URL']}/auth/realms/{realm}/protocol/openid-connect/token",
        data=payload,
    )

    assert response.status_code == 200, f"Getting token for {username} failed with: {response.text}"

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
    # Step 1: Get Keycloak admin token
    with open(f"{REPO_DIR}/tmp/keycloak/admin-password") as f:
        admin_pass = f.read()
    
    # Step 2: Create user
    # NB: We can't use the usual OIDC flow to grab an admin token, because we
    # cannot retrieve the admin token without a client, and don't have one
    # initially setup. Because of this, we have to go through the command-line
    # admin tools to create our user
    # i.e. going through kcadm.sh. We had the code already for this in
    # keycloak_setup.sh and it's a pain to work with here so...

    # Find the docker container
    docker_ps = subprocess.run(["docker", "ps"], capture_output=True)
    split_docker = docker_ps.stdout.decode('utf8').split("\n")
    container_name = ""
    for container in split_docker:
        if re.search(r"keycloak\/keycloak", container):
            container_name = container.split()[-1]
    
    assert container_name != "", "Coult not find the keycloak/keycloak container"

    # Run the commands to create the user
    # a. login as admin
    run = subprocess.run(["docker", "exec", container_name, "/opt/keycloak/bin/kcadm.sh",
                   "config", "credentials", "--server", f"{ENV["KEYCLOAK_PUBLIC_URL"]}/auth",
                   "--user", "admin", "--password", admin_pass, "--realm", "master"])
    assert run.returncode == 0, "Could not login as admin for into Keycloak"
    # b. create the user
    run = subprocess.run(["docker", "exec", container_name, "/opt/keycloak/bin/kcadm.sh",
                   "create", "users", "-r", ENV["KEYCLOAK_REALM"], "-s", f"username=\"{username}\"",
                   "-s", f"email=\"{email}\"", "-s", f"firstName=\"{first_name}\"", "-s", f"lastName=\"{last_name}\""])
    assert run.returncode == 0, "Could not create user with the admin Keycloak session"
    # c. set their password --username "$USERNAME" --new-password "$PASSWORD"
    run = subprocess.run(["docker", "exec", container_name, "/opt/keycloak/bin/kcadm.sh",
                   "set-password", "-r", ENV["KEYCLOAK_REALM"], "--username", username,
                   "--new-password", password])
    assert run.returncode == 0, "Could not change password for the new user with Keycloak admin"


# Need to call this from the other server somehow?
def approve_user_into_candig(username, password):
    # Step 1: preapprove user
    headers = {
        "Authorization": f"Bearer {get_site_admin_token()}"
    }
    body = [username]
    preapproval_url = f"{ENV['CANDIG_URL']}/ingest/user/preapproved"
    response = requests.post(
        preapproval_url, headers=headers, json=body, timeout=10
    )
    assert response.status_code == 200, f"Preapproval to {preapproval_url} failed with: {response.text}"

    # Step 2: request approval via user
    headers = {
        "Authorization": f"Bearer {get_token(username, password, True)}"
    }
    request_url = f"{ENV['CANDIG_URL']}/ingest/user/pending/request"
    response = requests.post(
        request_url, headers=headers, timeout=10
    )
    assert response.status_code == 200, f"Requesting user {username} approval failed with: {response.text}"

    # Step 3: check that requests are ok
    response = requests.get(
        f"{ENV['CANDIG_ENV']['QUERY_INTERNAL_URL']}/discovery/programs", headers=headers)
    assert response.status_code == 200, f"User {username} went through approval but did not succeed: {response.text}"

#### RUN ONLY AT TARGET SITE

def test_ingest_local_test_dataset():
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


### RUN ONLY ON QUERYING SITE

def test_create_federated_user():
    create_keycloak_user("federated@test.ca", "testfederation", "federated@test.ca", "federated", "test")
    approve_user_into_candig("federated@test.ca", "testfederation")


def test_create_unfederated_curator():
    create_keycloak_user("unfederated@test.ca", "testfederation", "unfederated@test.ca", "unfederated", "test")
    approve_user_into_candig("unfederated@test.ca", "testfederation")


def test_query_authorized_remote_test_dataset():
    # Get user3@test.ca token
    headers = {
        "Authorization": f"Bearer {get_token('user3@test.ca', 'testfederation')}"
    }
    # Step 1: can we do a discovery query successfully to all sites?
    body = {
        "method": "GET", 
        "path": "discovery/programs",
        "payload": {},
        "service": "query"
    }
    response = make_fanout(headers, body)
    
    # Verify response
    assert response.status_code == 200, f"Query discovery endpoint failed with: {response.text}"
    
    programs = set(())
    try:
        r = response.json()
        print(r)
        for server in r:
            assert server["status"] == 200, f"Server {server['location']['name']} failed with: {server['message']}"
            for program in server['results']['programs']:
                programs |= {program['program_id']}
            # TODO: Check that the result is sane
        # assert len(r) > 1, f"Only one server found? This is not a federated environment"
    except requests.JSONDecodeError:
        assert False, f"Invalid JSON response: {response.text}"

    # Step 2: can we do a query and grab responses (only include the ones from the TEST_FEDERATE set)
    programs -= {"TEST_FEDERATE"}
    body = {
        "method": "GET", 
        "path": "query",
        "payload": {"exclude_programs": ",".join(programs)},
        "service": "query"
    }
    response = make_fanout(headers, body)
    
    # Verify response
    assert response.status_code == 200, f"Query authorized failed with: {response.text}"
    try:
        r = response.json()
        print(r)
        for server in r:
            assert server["status"] == 200, f"Server {server['location']['name']} failed with: {server['message']}"
            assert server["results"]["count"] == 24, f"Server {server['location']['name']} had a strange number of results in query"
    except requests.JSONDecodeError:
        assert False, f"Invalid JSON response: {response.text}"


def test_query_unauthorized_remote_test_dataset():
    # Get user4@test.ca token
    headers = {
        "Authorization": f"Bearer {get_token('user4@test.ca', 'testfederation')}"
    }

    # Step 1: can we do a discovery query successfully to all sites?
    body = {
        "method": "GET", 
        "path": "discovery/programs",
        "payload": {},
        "service": "query"
    }
    response = make_fanout(headers, body)
    
    # Verify response
    assert response.status_code == 200, f"Query discovery endpoint failed with: {response.text}"
    
    programs = set(())
    try:
        r = response.json()
        print(r)
        for server in r:
            assert server["status"] == 200, f"Server {server['location']['name']} failed with: {server['message']}"
            for program in server['results']['programs']:
                programs |= {program['program_id']}
            # TODO: Check that the result is sane
        # assert len(r) > 1, f"Only one server found? This is not a federated environment"
    except requests.JSONDecodeError:
        assert False, f"Invalid JSON response: {response.text}"

    # Step 2: can we do a query and fail to grab responses (only include the ones from the TEST_FEDERATE set)
    programs -= {"TEST_FEDERATE"}
    body = {
        "method": "GET", 
        "path": "query",
        "payload": {"exclude_programs": ",".join(programs)},
        "service": "query"
    }
    response = make_fanout(headers, body)
    
    # Verify response
    assert response.status_code == 200, f"Query authorized failed with: {response.text}"
    try:
        r = response.json()
        print(r)
        for server in r:
            assert server["status"] == 200, f"Server {server['location']['name']} failed with: {server['message']}"
    except requests.JSONDecodeError:
        assert False, f"Invalid JSON response: {response.text}"