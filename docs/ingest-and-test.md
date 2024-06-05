# Testing the installation

These instructions describe some basic functionality tests and the ingestion of a test dataset to ensure your local installation is working properly.

## Automatic testing

The easiest way to test your local installation is to run the integration tests.

This requires:
- An activated conda environment (`(candig)` showing up on the left of your command line).
- Installation of some extra python requirements.

This can be done automatically:
```bash
source ./etc/venv/activate.sh
```
or separately:
```commandline
cd CanDIGv2
conda activate candig
pip install -r etc/venv/requirements
```
Run the tests with:
```bash
make test-integration
```


## Manual tests

Check that you can see the data portal in your browser at [http://candig.docker.internal:5080](http://candig.docker.internal:5080). If not, refer to the instructions in the [Docker Deployment Guide](./install-docker.md).

Check that you can generate a bearer token for user2 with the following call, substituting usernames, secrets and passwords from `TEST_USER_2` in .env, `tmp/secrets/keycloak-client-secret` and `tmp/secrets/keycloak-test-user2-password`.

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

## Federation Service Errors

The federation service is required to run most CanDIG operations.  It is included with `make install-all`, but sometimes glitches.  Federation errors look like:

```commandline
FAILED etc/tests/test_integration.py::test_server_count - assert 0 > 0
FAILED etc/tests/test_integration.py::test_services_count - assert 0 > 0
FAILED etc/tests/test_integration.py::test_federation_call - AssertionError: assert 'results' in {'error': 'There was a problem proxying the request'}
FAILED etc/tests/test_integration.py::test_add_server - IndexError: list index out of range
```

To solve these errors:
1. Ensure `federation` is in the list of `CANDIG_AUTH_MODULES` in `.env` (though it is present by default).

2. If you already have federation running, restart the container with:
```commandLine
make clean-federation
make build-federation
make compose-federation
```


## Ingest the synthetic clinical dataset

Synthetic data is ingested as part of the integration tests. By default, this data is deleted after tests are run. If you'd like to keep the data in the platform, ensure the [`KEEP_TEST_DATA`](https://github.com/CanDIG/CanDIGv2/blob/c2339c685720b327ca02ea6bb9d442e253cdb562/etc/env/example.env#L20) variable in your .env file is set to `true`.

If you would like to ingest the data separately, from the CanDIGv2 directory:
```commandline
python settings.py
source env.sh
cd lib/candig-ingest/candigv2-ingest/
pip install -r requirements.txt
python katsu_ingest.py --input tests/clinical_ingest.json
```
You should now see the ingested data in the [data portal](http://candig.docker.internal:5080).

[Clinical data](https://github.com/CanDIG/candigv2-ingest#1-clinical-data) and [Genomic data](https://github.com/CanDIG/candigv2-ingest#2-genomic-data) describe the data ingestion process and include descriptions of ingestable test datasets.
