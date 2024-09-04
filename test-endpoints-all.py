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
    for line in args.input:
        # Allow other methods
        split = line.strip().split(" ")
        if line.strip() == "":
            continue
        url = split[0]
        extra = split[1:]
        sanitized_url = re.sub(r'https?://', "", url)
        sanitized_url = re.sub(r'/', "_", sanitized_url)
        token = get_token(args.username, args.password, args.secret, args.loginurl)
        print(url)

        rc = subprocess.run(
            ['python', 'test-endpoint.py',
            '--url', url,
            '--out', args.out + sanitized_url + ".csv",
            '--silent',
            '-H', f"Authorization: Bearer {token}"] + extra)

if __name__ == "__main__":
    stress_test()
