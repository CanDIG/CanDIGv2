# Testing local installation

These instructions will lead you through some basic functionality tests, ingesting some sample data, and running some tests of the data services to make sure your local installation is working as expected.

## Initial tests

Check that you can see the data portal in your browser at `http://docker.localhost:5080/`. If not, you may need to follow the instructions in the [Docker Deployment Guide](./install-docker.md)

Check that you can generate a bearer token for user2 with the following call, substituting usernames, secrets and passwords from `tmp/secrets/keycloak-test-user2`, `tmp/secrets/keycloak-client-local_candig-secret` and `tmp/secrets/keycloak-test-user2-password`.

```
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

```
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

```
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

## Install test data

Clone the [candig-ingest](https://github.com/CanDIG/candigv2-ingest) repo:

```
https://github.com/CanDIG/candigv2-ingest.git
```

Create a virtual environment named `.venv`:

```
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

Generate a file env.sh in the `candig2-ingest` repo:

```
python settings.py ../CanDIGv2/
source env.sh
```

Create opa dataset policy based on the dataset name and the email 
address of the user (for example, dataset_name=SYNTHETIC_1 and user_name=user2@test.ca)

```
python opa_ingest.py --dataset <dataset_name> --user <user_name> > access.json
```

Copy the access.json file to the docker:

```
docker cp access.json candigv2_opa_1:/app/permissions_engine/access.json
```

Get the `Synthetic_Clinical_Data.json` file from @daisieh (Daisie Huang) and copy it into the root folder in the docker container:

```
docker cp '/local_path_to_file/Synthetic_Clinical_Data.json' candigv2_chord-metadata_1:/Synthetic_Clinical_Data.json
```

Then run ingest command (katsu and federation should be running):

```
python katsu_ingest.py --dataset <dataset_name> --input /Synthetic_Clinical_Data.json 
```

## Test data services
To be continue
