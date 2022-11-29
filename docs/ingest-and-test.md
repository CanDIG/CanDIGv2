# Testing local installation

These instructions will lead you through some basic functionality tests, ingesting some sample data, and running some tests of the data services to make sure your local installation is working as expected.

## Initial tests

Check that you can see the data portal in your browser at `http://docker.localhost:5080/`.

Check that you can generate a bearer token for user2 with the following call, substituting secrets and passwords from `tmp/secrets/keycloak-client-local_candig-secret` and `tmp/secrets/keycloak-test-user2-password`.

```
## user2 bearer token
curl -X "POST" "http://docker.localhost:8080/auth/realms/candig/protocol/openid-connect/token" \
     -H 'Content-Type: application/x-www-form-urlencoded; charset=utf-8' \
     --data-urlencode "client_id=local_candig" \
     --data-urlencode "client_secret=<client_secret" \
     --data-urlencode "grant_type=password" \
     --data-urlencode "username=user2" \
     --data-urlencode "password=<user2-password>" \
     --data-urlencode "scope=openid"
```

Doing much else will require test data.

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

Generate a file env.sh

```
python settings.py ../CanDIGv2/
source env.sh
```

Create opa dataset policy (for example, dataset_name=SYNTHETIC_1 and user_name=user2)

```
python opa_ingest.py --dataset <dataset_name> --user <user_name> > access.json
```

Copy the access.json file to the docker:

```
docker cp access.json candigv2_opa_1:/app/permissions_engine/access.json
```

Get the `Synthetic_Clinical_Data.json` file from @daisieh (Daisie Huang) and place in the root folder, then copy it over to docker:

```
docker cp '/local_path_to_file/Synthetic_Clinical_Data.json' candigv2_chord-metadata_1:/app/chord_metadata_service/Synthetic_Clinical_Data.json
```

Then run ingest command (katsu should be running):

```
python katsu_ingest.py --dataset <dataset_name> --input Synthetic_Clinical_Data.json --katsu_url http://docker.localhost:5080/katsu
```

## Test data services
