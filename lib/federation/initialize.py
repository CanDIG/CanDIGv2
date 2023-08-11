import json
import os
import re
import requests
import sys
from authx.auth import get_access_token
import tempfile

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../..")
sys.path.insert(0, os.path.abspath(f"{REPO_DIR}"))

from settings import get_env_value


def find_services():
    raw_services = get_env_value("FEDERATION_SERVICES").split(" ")
    services = []
    for s in raw_services:
        service = {
            'id': s
        }
        service_port = f"{s.upper()}_PORT"
        service_version = f"{s.upper()}_VERSION"
        service['url'] = f"http://{get_env_value('CANDIG_DOMAIN')}:{get_env_value(service_port)}"
        service['version'] = get_env_value(service_version)
        services.append(service)
    return services

def main():
    token = get_access_token(username=os.getenv("CANDIG_SITE_ADMIN_USER"), password=os.getenv("CANDIG_SITE_ADMIN_PASSWORD"))

    server = {
        "server": json.loads(get_env_value("FEDERATION_SELF_SERVER").replace('\'', '"')),
        "authentication": {
            "issuer": get_env_value("KEYCLOAK_REALM_URL"),
            "token": token
        }
    }
    token = get_access_token(username=os.getenv("CANDIG_SITE_ADMIN_USER"), password=os.getenv("CANDIG_SITE_ADMIN_PASSWORD"))
    headers = {}
    headers["Authorization"] = f"Bearer {token}"

    print("Adding servers to federation...")
    url = f"http://localhost:{get_env_value("FEDERATION_PORT")}/federation/v1/servers"
    response = requests.request("POST", url, headers=headers, json=server)
    # add other federated servers here
    if response.status_code != 200:
        print(f"POST response: {response.status_code} {response.text}")
    url = f"http://localhost:4232/federation/v1/servers"
    response = requests.request("GET", url, headers=headers)
    print(response.text)

    print("Adding services to federation...")
    services = find_services()
    url = f"http://localhost:{get_env_value("FEDERATION_PORT")}/federation/v1/services"
    for service in services:
        response = requests.request("POST", url, headers=headers, json=service)

    url = f"http://localhost:{get_env_value("FEDERATION_PORT")}/federation/v1/services"
    response = requests.request("GET", url, headers=headers)
    print(response.text)


if __name__ == "__main__":
    main()





