import argparse
import json
import os
import requests

from site_admin_token import get_site_admin_token
#from authx.auth import get_access_token
from settings import get_env_value

def add_federated_server(token, id, url, keycloak_url, name, province, code, verbose=False):
    server = {
        "server": {
            'id': id,
            'url': url,
            'location': {
                'name': name,
                'province': province,
                'province-code': code
            }
        },
        "authentication": {
            "issuer": keycloak_url,
            "token": token
        }
    }
    site_token = get_site_admin_token()
#    site_token = get_access_token(
#            username=os.getenv("CANDIG_SITE_ADMIN_USER"),
#            password=os.getenv("CANDIG_SITE_ADMIN_PASSWORD"))
    headers = { "Authorization": f"Bearer {site_token}"}

    if verbose:
        print(f"Adding {id} to federation...")
    url = f"{get_env_value('FEDERATION_SERVICE_URL')}/federation/v1/servers"
    response = requests.request("POST", url, headers=headers, json=server)
    if response.status_code != 200 and verbose:
        print(f"POST response: {response.status_code} {response.text}")
        return response.status_code, response.text
    url = f"{get_env_value('FEDERATION_SERVICE_URL')}/federation/v1/servers"
    response = requests.request("GET", url, headers=headers)
    if verbose:
        print(response.text)
    return 200, 'ok'

def main():
    parser = argparse.ArgumentParser(
        prog='Add Federated Server',
        description='Adds a given server')
    parser.add_argument(
        '-token',
        help='Bearer token for the target CanDIG server',
        required=True)
    parser.add_argument(
        '-id',
        help='Internal ID for the target CanDIG server (e.g. uhn-federation-1)',
        required=True)
    parser.add_argument(
        '-url',
        help='URL for the target CanDIG server (e.g. http://candig.docker.internal:5080/federation)',
        required=True)
    parser.add_argument(
        '-keycloak',
        help='URL for the target''s keycloak domain (e.g. http://candig.docker.internal:8080/auth/realms/candig)',
        required=True)
    parser.add_argument(
        '-name',
        help='Name for the target CanDIG server (e.g. UHN Federation 1)',
        required=True)
    parser.add_argument(
        '-province',
        help='Province for the target CanDIG server (e.g. ON)',
        default='ON')
    parser.add_argument(
        '-code',
        help='Province code for the target CanDIG server (e.g. ca-on)',
        default='ca-on')

    args = parser.parse_args()
    add_federated_server(args.token, args.id, args.url, args.keycloak,
            args.name, args.province, args.code, verbose=True)

if __name__ == "__main__":
    main()

