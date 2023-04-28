from dotenv import dotenv_values
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
        service_tyk_listen_path = f"TYK_{s.upper()}_API_LISTEN_PATH"
        service_version = f"{s.upper()}_VERSION"
        service['url'] = f"{get_env_value('TYK_LOGIN_TARGET_URL')}/{get_env_value(service_tyk_listen_path)}"
        service['version'] = get_env_value(service_version)
        services.append(service)
    return services

def main():

    servers = json.loads(get_env_value("FEDERATION_SELF_SERVER").replace('\'', '"'))
    services = find_services()

    token = get_access_token(username=os.getenv("CANDIG_SITE_ADMIN_USER"), password=os.getenv("CANDIG_SITE_ADMIN_PASSWORD"))
    headers = {}
    headers["Authorization"] = f"Bearer {token}"
    url = f"{get_env_value('FEDERATION_PUBLIC_URL')}/servers"
    for server in servers:
        response = requests.request("POST", url, headers=headers, json=server)

    url = f"{get_env_value('FEDERATION_PUBLIC_URL')}/services"
    for service in services:
        response = requests.request("POST", url, headers=headers, json=service)

    url = f"{get_env_value('FEDERATION_PUBLIC_URL')}/servers"
    response = requests.request("GET", url, headers=headers)
    print(response.text)
    url = f"{get_env_value('FEDERATION_PUBLIC_URL')}/services"
    response = requests.request("GET", url, headers=headers)
    print(response.text)


if __name__ == "__main__":
    main()





