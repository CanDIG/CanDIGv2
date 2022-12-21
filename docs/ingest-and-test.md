# Testing local installation

These instructions will lead you through some basic functionality tests, ingesting some sample data, and running some tests of the data services to make sure your local installation is working as expected.

## Initial tests

Check that you can see the data portal in your browser at `http://docker.localhost:5080/`. If not, you may need to follow the instructions in the [Docker Deployment Guide](./install-docker.md)

Check that you can generate a bearer token for user2 with the following call, substituting usernames, secrets and passwords from `tmp/secrets/keycloak-test-user2`, `tmp/secrets/keycloak-client-local_candig-secret` and `tmp/secrets/keycloak-test-user2-password`.

```bash
## user2 bearer token
curl -X "POST" "http://docker.localhost:8080/auth/realms/candig/protocol/openid-connect/token" \
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

Federation service is required to run most of CanDig operations. The following example will add 1 UHN node to simulate the network calls.

- add `federation-service` to the list of `CANDIG_MODULES` in .env
- add to /tmp/federation/ the file `servers.json`

```json
{
    "servers": [
        {
            "url": "http://docker.localhost:4232/federation/search",
            "location": [
                "UHN",
                "Ontario",
                "ca-on"
            ]
        }
    ]
}
```

and `services.json`

```json
{
    "services": {
        "katsu": "http://docker.localhost:5080/katsu",
        "candig-server": "http://docker.localhost:5080/candig",
        "htsget-app": "http://docker.localhost:5080/genomics"
    }
}
```

If you already have federation-service running, delete the container then run
`make build-federation-service` and `make compose-federation-service` to recreate it.

## WSL Federation Configuration Errors

<details open>
<summary>WSL Errors</summary>

```bash
Creating candigv2_federation-service_1 ... error

ERROR: for candigv2_federation-service_1  Cannot create container for service federation-service: not a directory

ERROR: for federation-service  Cannot create container for service federation-service: not a directory
ERROR: Encountered errors while bringing up the project.
make: *** [Makefile:378: compose-federation-service] Error 1
```
If you are seeing the above directory not found error in WSL it is a issue with the communication between WSL and Windows docker in relation to the tmp folder. To get past this you need to do the following:

Current directory: **../CanDIGv2**
```bash
#Copy the servers.json and services.json into the config folder instead:
cp tmp/federation/* lib/federation-service/federation_service/configs
```
You will need to comment out the 'secrets' section in the lib/federation-service/docker-compose.yml file. It will look like the code chunk below:

```yml
    ...
    # secrets:
    #   - source: federation-servers
    #     target: /app/federation_service/configs/servers.json
    #   - source: federation-services
    #     target: /app/federation_service/configs/services.json
    entrypoint: ["uwsgi", "federation.ini", "--http", "0.0.0.0:4232"]
```
Start the federation-service up:
```bash
make build-federation-service
make compose-federation-service
```
To check that it is running you can look at the candigv2_federation-service_1 container in your Window Docker GUI. You can also run the following in terminal:
```bash
curl http://docker.localhost:4232/federation/services
```
The below is an example of what will return it should be what is in your services.json
```json
{
  "candig-server": "http://docker.localhost:5080/candig",
  "htsget-app": "http://docker.localhost:5080/genomics",
  "katsu": "http://docker.localhost:5080/katsu"
}
```
</details>

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