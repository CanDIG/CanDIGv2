import datetime
import os
import re
import requests

from add_federated_server import add_federated_server
from site_admin_token import get_site_admin_token

# We need a unix timestamp from the start of the day
today = datetime.datetime.combine(
        datetime.date.today(),
        datetime.datetime.min.time()
        ).timestamp()

# Request all messages since the start of the day
headers = { "Authorization": f"Bearer {os.environ['BOT_TOKEN']}" }
r = requests.get(f"https://slack.com/api/conversations.history" +
        f"?channel=C0287431S10&oldest={int(today)}",
        headers=headers)

# Parse all messages looking for a federation string
messages = r.json()['messages']
federation_re = r'```federate (.+)```'  # Find messages about federation
url_re = r'<(.+)>'  # URLs from Slack always end up enclosed in <>s
for message in messages:
    match = re.match(federation_re, message['text'])
    if match:
        groups = match.group(1).split('|')

        # For ease of understanding
        token = groups[0]
        name = groups[1]
        url = re.match(url_re, groups[2]).group(1)
        client_id = groups[3]
        province = groups[4]
        province_code = groups[5]
        server_id = groups[6]
        keycloak_url = re.match(url_re, groups[7]).group(1)

        # Don't overwrite our own federation
        if os.environ['FEDERATION_SELF_SERVER_ID'] == server_id:
                continue

        # Actually add the server
        add_federated_server(token, server_id, url, keycloak_url, server_id, province,
                province_code, verbose=False)

# Check the federation
site_token = get_site_admin_token()
candig_headers = { "Authorization": f"Bearer {site_token}" }
servers = requests.get(f"{os.environ['CANDIG_URL']}/federation/v1/servers",
        headers=candig_headers).json()
server_ids = [server['id'] for server in servers]

success_payload = {
    "text": f"{os.environ['FEDERATION_SELF_SERVER_ID']} successfully added: " +
            f"{', '.join(server_ids)}"
}
requests.post(os.environ['HOOK_URL'], json=success_payload)

