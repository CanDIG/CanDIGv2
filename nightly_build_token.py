import argparse
import json
import re
import requests
import sys
import time

parser = argparse.ArgumentParser(
    prog="Nightly build token analyzer",
    description="Finds a token among the given messages in recent Slack history"
    )
parser.add_argument(
    '--token',
    help='Slack bot user OAUTH token',
    required=True
    )
parser.add_argument(
    '--channel',
    help='Slack channel ID to search through',
    default="C0287431S10"
    )

# 20 hours ago in unix time is the cutoff
oldest = int(time.time()) - 20 * 60 * 60
args = parser.parse_args()
r = requests.get(
    f'https://slack.com/api/conversations.history?channel={args.channel}&oldest={oldest}',
    headers={'Authorization': f'Bearer {args.token}'}
    )
r.json()

if 'messages' in r:
    for message in r['messages']:
        test = re.search('token: (.+)', message)
        if test:
            print(test.group(1))
            sys.exit(0)
sys.exit(1)
