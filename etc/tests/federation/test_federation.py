import json
import os
import pytest
import re
import requests
import subprocess
import sys

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../../..")
sys.path.insert(0, os.path.abspath(f"{REPO_DIR}"))

from settings import get_env
from site_admin_token import get_site_admin_token

ENV = get_env()

def test_all_get_token():
    """
    Test to see if the local site admin token can be obtained.

    Raises:
        AssertionError: If token request fails
    """
    assert get_site_admin_token()

def make_fanout(headers, body):
    """
    Make a fanout call to the local Federation.

    Args:
        headers: Headers (usually must include an access token)
        body: Body to call with (see federation.yaml in the Federation microservice for details)

    Returns:
        A Requests object with the response
    """
    return requests.post(
        f"{ENV['CANDIG_URL']}/federation/v1/fanout", headers=headers, json=body, timeout=10
    )

def get_token(username=None, password=None, access_token=False, realm=ENV['KEYCLOAK_REALM']):
    """
    Get a token from Keycloak for a user.

    Args:
        username: Username to get token for
        password: Password for the user
        access_token: If True, return access token instead of refresh token
        realm: Keycloak realm to authenticate against (defaults to ENV['KEYCLOAK_REALM'])

    Returns:
        str: Either the refresh token (default) or access token if access_token=True

    Raises:
        AssertionError: If token request fails
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
        f"{ENV['KEYCLOAK_PUBLIC_URL']}/auth/realms/{realm}/protocol/openid-connect/token",
        data=payload,
    )

    assert response.ok, f"Getting token for {username} failed with: {response.text}"

    if access_token:
        return response.json()["access_token"]
    return response.json()["refresh_token"]


def test_all_service_info():
    """
    Test whether we can get a response from Federation for all of our services.

    Raises:
        AssertionError: If any of the services are unavailable
    """
    modules = ENV['CANDIG_ENV']['CANDIG_MODULES'].split(" ")
    headers = {
        "Authorization": f"Bearer {get_site_admin_token()}"
    }
    endpoints = {
        # all of these endpoints should return JSON
        "htsget": f"ga4gh/drs/v1/service-info",
        "katsu": f"v3/service-info",
        # "rnaget": f"service-info",
        "query": f"service-info",
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
    Create a user in Keycloak directly using the Keycloak CLI.
    
    Args:
        username (str): The username for the new user
        password (str): The password for the new user
        email (str): The email address for the new user
        first_name (str): The first name of the user
        last_name (str): The last name of the user
    
    Returns:
        None
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
                   "create", "users", "-r", ENV["KEYCLOAK_REALM"], "-s", f"username=\"{username}\"", "-s", "enabled=true",
                   "-s", f"email=\"{email}\"", "-s", f"firstName=\"{first_name}\"", "-s", f"lastName=\"{last_name}\""])
    assert run.returncode == 0, "Could not create user with the admin Keycloak session"
    # c. set their password --username "$USERNAME" --new-password "$PASSWORD"
    run = subprocess.run(["docker", "exec", container_name, "/opt/keycloak/bin/kcadm.sh",
                   "set-password", "-r", ENV["KEYCLOAK_REALM"], "--username", username,
                   "--new-password", password])
    assert run.returncode == 0, "Could not change password for the new user with Keycloak admin"


def approve_user_into_candig(username, password):
    """
    Approve a user into the local CanDIG instance by preapproving them and having them request access.

    Args:
        username (str): The username of the user to approve
        password (str): The password of the user to approve

    Raises:
        AssertionError: If any step of the approval process fails
    """
    # Step 1: preapprove user
    headers = {
        "Authorization": f"Bearer {get_site_admin_token()}"
    }
    body = [username]
    preapproval_url = f"{ENV['CANDIG_URL']}/ingest/user/preapproved"
    response = requests.post(
        preapproval_url, headers=headers, json=body, timeout=10
    )
    assert response.ok, f"Preapproval to {preapproval_url} failed with: {response.text}"

    # Step 2: request approval via user
    headers = {
        "Authorization": f"Bearer {get_token(username, password, True)}"
    }
    request_url = f"{ENV['CANDIG_URL']}/ingest/user/pending/request"
    response = requests.post(
        request_url, headers=headers, timeout=10
    )
    assert response.ok, f"Requesting user {username} approval failed with: {response.text}"

    # Step 3: check that requests are ok
    response = requests.get(
        f"{ENV['CANDIG_ENV']['QUERY_INTERNAL_URL']}/discovery/programs", headers=headers)
    assert response.ok, f"User {username} went through approval but did not succeed: {response.text}"


def check_unauthorized_user(username, password):
    # Ensure that we cannot access the frontend
    headers = {
        "Authorization": f"Bearer {get_token(username, password, True)}"
    }
    response = requests.get(f"{ENV['CANDIG_URL']}/ingest/user/me", headers=headers)
    assert response.status_code == 404, f"User {username} can access the frontend without being authorized"


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
        "team_members": ["federated@test.ca"]
    }

    # Add the program
    response = requests.post(
        f"{ENV['CANDIG_URL']}/ingest/program",
        headers=headers,
        json=test_program
    )
    assert response.ok

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
    assert response.ok


### RUN ONLY ON QUERYING SITE

def test_querying_site_create_federated_user():
    create_keycloak_user("federated@test.ca", "testfederation", "federated@test.ca", "federated", "test")
    check_unauthorized_user("federated@test.ca", "testfederation")
    approve_user_into_candig("federated@test.ca", "testfederation")


def test_querying_site__unfederated_curator():
    create_keycloak_user("unfederated@test.ca", "testfederation", "unfederated@test.ca", "unfederated", "test")
    check_unauthorized_user("unfederated@test.ca", "testfederation")
    approve_user_into_candig("unfederated@test.ca", "testfederation")


def test_querying_site_query_authorized_remote_test_dataset():
    """
    Test querying the TEST_FEDERATE dataset with a user that should have access, seeing whether or not we can access it
    """
    # Get token for 'federated@test.ca' user
    headers = {
        "Authorization": f"Bearer {get_token('federated@test.ca', 'testfederation')}"
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
    assert response.ok, f"Query discovery endpoint failed with: {response.text}"
    
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
    assert response.ok, f"Query authorized failed with: {response.text}"
    try:
        r = response.json()
        print(r)
        for server in r:
            assert server["status"] == 200, f"Server {server['location']['name']} failed with: {server['message']}"
            # NB: I do not currently ingest the federated dataset at the same location that the querying tests are run from
            # There is no reason for this to be the case, other than for speed's sake. Thus, the local server will not have anything here
            if server['location']['name'] != 'LOCAL':
                assert server["results"]["count"] == 24, f"Server {server['location']['name']} had a strange number of results in query"
    except requests.JSONDecodeError:
        assert False, f"Invalid JSON response: {response.text}"


def test_querying_site_query_unauthorized_remote_test_dataset():
    """
    Test querying the TEST_FEDERATE dataset with a user that should not have access, seeing whether or not we can access it
    """
    # Get unfederated@test.ca token
    headers = {
        "Authorization": f"Bearer {get_token('unfederated@test.ca', 'testfederation')}"
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
    assert response.ok, f"Query discovery endpoint failed with: {response.text}"
    
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
    assert response.ok, f"Query authorized failed with: {response.text}"
    try:
        r = response.json()
        print(r)
        for server in r:
            assert server["status"] == 200, f"Server {server['location']['name']} failed with: {server['message']}"

            # Ensure that we do not have access to this dataset
            assert len(server["results"]["results"]) == 0, f"Server {server['location']['name']} improperly authorized unfederated@test.ca"
    except requests.JSONDecodeError:
        assert False, f"Invalid JSON response: {response.text}"
