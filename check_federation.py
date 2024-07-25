#!/usr/env python
import os
import re
import requests

from authx.auth import get_access_token
from settings import get_env_value

def add_server(token, id, url, name, province, code, keycloak):
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
            "issuer": keycloak,
            "token": token
        }
    }
    token = get_access_token(
            username=os.getenv("CANDIG_SITE_ADMIN_USER"),
            password=os.getenv("CANDIG_SITE_ADMIN_PASSWORD"))
    headers = {}
    headers["Authorization"] = f"Bearer {token}"

    print(f"Adding {id} to federation...")
    url = f"{get_env_value('FEDERATION_SERVICE_URL')}/federation/v1/servers"
    response = requests.request("POST", url, headers=headers, json=server)
    if response.status_code != 200:
        print(f"POST response: {response.status_code} {response.text}")
        exit(1)

def get_loaded_servers():
    token = get_access_token(
            username=os.getenv("CANDIG_SITE_ADMIN_USER"),
            password=os.getenv("CANDIG_SITE_ADMIN_PASSWORD"))
    headers = {}
    headers["Authorization"] = f"Bearer {token}"
    url = f"{get_env_value('FEDERATION_SERVICE_URL')}/federation/v1/servers"
    response = requests.request("GET", url, headers=headers)
    return response.json()

# Check to see if we have any unknown tokens
def main():
    # Check which servers currently exist
    servers = get_loaded_servers()
    servers_dict = {}
    for server in servers:
        servers_dict[server["id"]] = server

    # Check which results we have so far in the channel history
    BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
    if not BOT_TOKEN:
        print('Please have BOT_TOKEN set before running this script')
        exit(1)
    params = {'Authorization': f'Bearer {BOT_TOKEN}'}
    response = requests.get("https://slack.com/api/conversations.history?channel=C0287431S10", params)

    # parse through the results: if response["ok"]: loop through response["results"][i]["text"] and find something from the bot user that matches token: "{}"
    if not response.ok or not response.json()['ok']:
        print(f"Error while obtaining slack channel history: {response.text}")
        exit(1)

    test_re = re.compile(r"federate (.+)\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)\|(.+)$")
    print(response.json())
    for result in response.json()['results']:
        matched = test_re.match(result["text"])
        if matched is not None:
            id = matched.group(1)
            if id in servers_dict:
                continue
            token = matched.group(0)
            url = matched.group(2)
            name = matched.group(3)
            province = matched.group(4)
            code = matched.group(5)
            keycloak = matched.group(6)
            add_server(token, id, url, name, province, code, keycloak)

if __name__ == '__main__':
    main()