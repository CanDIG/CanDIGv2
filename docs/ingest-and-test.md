# Testing local installation

These instructions will lead you through some basic functionality tests, ingesting some sample data, and running some tests of the data services to make sure your local installation is working as expected.

## Initial tests

Check that you can see the data portal in your browser at `http://candig.docker.internal:5080/`. If not, you may need to follow the instructions in the [Docker Deployment Guide](./install-docker.md)

Check that you can generate a bearer token for user2 with the following call, substituting usernames, secrets and passwords from `tmp/secrets/keycloak-test-user2`, `tmp/secrets/keycloak-client-local_candig-secret` and `tmp/secrets/keycloak-test-user2-password`.

```bash
## user2 bearer token
curl -X "POST" "http://candig.docker.internal:8080/auth/realms/candig/protocol/openid-connect/token" \
     -H 'Content-Type: application/x-www-form-urlencoded; charset=utf-8' \
     --data-urlencode "client_id=local_candig" \
     --data-urlencode "client_secret=<client_secret>" \
     --data-urlencode "grant_type=password" \
     --data-urlencode "username=user2" \
     --data-urlencode "password=<user2-password>" \
     --data-urlencode "scope=openid"
```

Doing much else will require test data.

## Setup Federation Service

Federation service is required to run most of CanDIG operations.

- add `federation` to the list of `CANDIG_AUTH_MODULES` in .env

If you already have federation running, delete the container then run
`make build-federation` and `make compose-federation` to recreate it.


## Install test data

Clone the [candigv2-ingest](https://github.com/CanDIG/candigv2-ingest) repo:

```
https://github.com/CanDIG/candigv2-ingest.git
```

Create a virtual environment named `.venv`:

```bash
# Linux
sudo apt-get install python3-venv    # If needed
python3 -m venv .venv
source .venv/bin/activate

# macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
py -3 -m venv .venv
.venv\scripts\activate
```

Install the requirements:

```
pip install -r requirements.txt
```

Generate a file env.sh:

```bash
cd CanDIGv2/
python settings.py
source env.sh
```

Download [synthetic data](https://github.com/CanDIG/mohccn-data) and follow the instructions there.

## Test data services

Follow [Integration testing](https://candig.atlassian.net/wiki/spaces/CA/pages/665518081/Integration+testing) instructions to exercise your Docker installation.