# Testing local installation

These instructions will lead you through some basic functionality tests, ingesting some sample data, and running some tests of the data services to make sure your local installation is working as expected.

## Automatic testing

The easiest way to test your local installation is to run the integration tests.

```bash
make test-integration
```

If you get an error about missing python requirements such as `dotenv` ensure the `candig` conda environment is activated, it should be in brackets beside your username. If it isn't run

```commandline
conda activate candig
```

If the error persists, try:

```commandline
pip install -r etc/venv/requirements.txt
```

If you want to run the tests manually, follow the instructions below.
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

## Rebuild Federation Service

Federation service is required to run most of CanDIG operations. It should have gotten set up when you ran `make install-all`. But if you are getting errors such as the following:

```commandline
FAILED etc/tests/test_integration.py::test_server_count - assert 0 > 0
FAILED etc/tests/test_integration.py::test_services_count - assert 0 > 0
FAILED etc/tests/test_integration.py::test_federation_call - AssertionError: assert 'results' in {'error': 'There was a problem proxying the request'}
FAILED etc/tests/test_integration.py::test_add_server - IndexError: list index out of range
```

You might need to rebuild federation service. First check whether `federation` is in the list of `CANDIG_AUTH_MODULES` in your `.env` file. If it isn't, add it.

Then run
```commandline
make clean-federation
make build-federation
make compose-federation
```


## Ingest synthetic clinical data

```commandline
python settings.py
source env.sh
cd lib/candig-ingest/candigv2-ingest
# should be pip install -r requirements.txt, but that didn't seem to work last I checked -- dependency errors?
pip install -r requirements.txt
python katsu_ingest.py --input tests/clinical_ingest.json

```
You should then be able to visit the data portal and ingested data.



Follow the instructions for [Clinical data](https://github.com/CanDIG/candigv2-ingest#1-clinical-data) and [Genomic data](https://github.com/CanDIG/candigv2-ingest#2-genomic-data)
