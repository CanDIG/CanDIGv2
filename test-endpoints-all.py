import argparse
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
    '--in',
    help='URLs to hit, line-delimited. Additional arguments are space delimited',
    required=True,
    type=argparse.FileType('r')
    )
parser.add_argument(
    '--out',
    help='output files prefix',
    required=False
)
parser.add_argument(
    '--username',
    help='username to login as'
)
parser.add_argument(
    '--password',
    help='password to login as'
)
parser.add_argument(
    '--loginurl',
    help='URL to hit when grabbing a token'
)
parser.add_argument(
    '--secret',
    help='URL to hit when grabbing a token'
)

def get_token(username, password, secret, login_url):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = [
        ("grant_type", "password"),
        ("client_id", "local_candig"),
        ("client_secret", secret),
        ("username", username),
        ("password", password),
        ("scope", "openid")
    ]
    retval = requests.post(login_url, headers=headers, data=data)
    print(retval.text)

    token_re = re.search(r'refresh_token":"([a-zA-Z0-9._\-]+)"', retval.text)
    token = token_re.group(1)
    return token


def stress_test():
    args = parser.parse_args()
    print(get_token(args.username, args.password, args.secret, args.loginurl))

    rc = subprocess.run(["python", "test-endpoint.py", "--help"])
    print(rc.stdout)

if __name__ == "__main__":
    stress_test()
