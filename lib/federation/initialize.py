import json
import os
import requests
import sys

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../..")
sys.path.insert(0, os.path.abspath(f"{REPO_DIR}"))

from settings import get_env_value
from site_admin_token import get_site_admin_token


def get_default_services():
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


def get_default_server():
    token = get_site_admin_token()
    server = {
        "server": json.loads(get_env_value("FEDERATION_SELF_SERVER").replace('\'', '"')),
        "authentication": {
            "issuer": get_env_value("KEYCLOAK_REALM_URL"),
            "token": token
        }
    }
    return server


def main():
    token = get_site_admin_token()

    server = {
        "server": json.loads(get_env_value("FEDERATION_SELF_SERVER").replace('\'', '"')),
        "authentication": {
            "issuer": get_env_value("KEYCLOAK_REALM_URL"),
            "token": token
        }
    }
    headers = {}
    headers["Authorization"] = f"Bearer {token}"

    print("Register existing servers")
    url = f"{get_env_value('FEDERATION_PUBLIC_URL')}/v1/servers"
    response = requests.request("POST", url, headers=headers, params={"register": True})
    if response.status_code != 200:
        print(f"POST response: {response.status_code} {response.text}")

    print("Making sure our server is in federation...")
    server = get_default_server()
    response = requests.request("POST", url, headers=headers, json=server)

    if response.status_code != 200:
        print(f"POST response: {response.status_code} {response.text}")
    url = f"{get_env_value('FEDERATION_PUBLIC_URL')}/v1/servers"
    response = requests.request("GET", url, headers=headers)
    print(response.text)

    print("Adding services to federation...")
    services = get_default_services()
    url = f"{get_env_value('FEDERATION_PUBLIC_URL')}/v1/services"
    for service in services:
        response = requests.request("POST", url, headers=headers, json=service)

    url = f"{get_env_value('FEDERATION_PUBLIC_URL')}/v1/services"
    response = requests.request("GET", url, headers=headers)
    print(response.text)


if __name__ == "__main__":
    main()
