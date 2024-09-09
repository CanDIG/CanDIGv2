import argparse
import jwt
import os
import re
import requests
import subprocess

parser = argparse.ArgumentParser(
    prog="test-endpoints-all.py",
    description="""
Batch endpoint stress-tester

Floods each URL in the given file with requests, ensuring that the return is
consistent"""
    )

parser.add_argument(
    '--input',
    help='URLs to hit, line-delimited. Additional arguments are space delimited',
    required=True,
    type=argparse.FileType('r')
    )
parser.add_argument(
    '--out',
    help='output files prefix',
    required=True
)
parser.add_argument(
    '--token',
    help='refresh token for the target url',
    required=True
)
parser.add_argument(
    '--secret',
    help='client secret for the target',
    required=True
)


def grab_new_refresh_token(refresh_token, secret):
    decoded_token = jwt.decode(refresh_token, options={"verify_signature": False})
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = [
        ("grant_type", "refresh_token"),
        ("client_id", decoded_token["azp"]),
        ("client_secret", secret),
        ("refresh_token", refresh_token),
        ("scope", "openid")
    ]

    retval = requests.post(
        decoded_token["iss"] + "/protocol/openid-connect/token",
        headers=headers,
        data=data
        )

    token_re = re.search(r'refresh_token":"([a-zA-Z0-9._\-]+)"', retval.text)
    token = token_re.group(1)
    return token

def stress_test():
    args = parser.parse_args()
    refresh_token = args.token
    for line in args.input:
        # Allow other methods
        split = line.strip().split(" ")
        if line.strip() == "":
            continue
        url = split[0]
        extra = split[1:]
        sanitized_url = re.sub(r'https?://', "", url)
        sanitized_url = re.sub(r'/', "-", sanitized_url)
        print(url)

        refresh_token = grab_new_refresh_token(refresh_token, args.secret)

        rc = subprocess.run(
            ['python', os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test-endpoint.py'),
            '--url', url,
            '--out', os.path.join(args.out, sanitized_url + ".csv"),
            '--silent',
            '-H', f"Authorization: Bearer {refresh_token}"] + extra)

if __name__ == "__main__":
    stress_test()
