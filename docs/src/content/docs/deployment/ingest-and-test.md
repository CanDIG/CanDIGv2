---
title: Testing
description: How to test your running deployment
---

These instructions describe some basic functionality tests and the ingestion of a test dataset to ensure your local installation is working properly.

## Automatic testing

The easiest way to test your local installation is to run the integration tests.

This requires:
- An activated conda environment `(candig)` showing up on the left of your command line.
- Installation of some extra python requirements.

This can be done automatically:
```bash
source ./etc/venv/activate.sh
```
or separately:
```bash
cd CanDIGv2
conda activate candig
pip install -r etc/venv/requirements
```
Run the tests with:
```bash
make test-integration
```

:::note
These tests will not work if the default site administrator has been changed.
:::

## Manual tests

These tests assume you are on a local deployment with default `.env` values. If not, you will need to update some of the values to suit your deployment. Check that you can see the data portal in your browser at [http://candig.docker.internal:5080](http://candig.docker.internal:5080). If not, refer to the instructions in the [deployment guide](local).

Check that you can generate a bearer token for user2 with the following call, substituting usernames, secrets and passwords from `env.sh`.

```bash
## user2 bearer token
curl -X "POST" "http://candig.docker.internal:8080/auth/realms/candig/protocol/openid-connect/token" \
     -H 'Content-Type: application/x-www-form-urlencoded; charset=utf-8' \
     --data-urlencode "client_id="$CANDIG_CLIENT_ID \
     --data-urlencode "client_secret="$CANDIG_CLIENT_SECRET \
     --data-urlencode "grant_type=password" \
     --data-urlencode "username="$CANDIG_NOT_ADMIN2_USER \
     --data-urlencode "password="$CANDIG_NOT_ADMIN2_PASSWORD \
     --data-urlencode "scope=openid"
```

## Federation Service Errors

The federation service is required to run most CanDIG operations.  It is included with `make install-all`, but sometimes glitches.  Federation errors look like:

```bash
FAILED etc/tests/test_integration.py::test_server_count - assert 0 > 0
FAILED etc/tests/test_integration.py::test_services_count - assert 0 > 0
FAILED etc/tests/test_integration.py::test_federation_call - AssertionError: assert 'results' in {'error': 'There was a problem proxying the request'}
FAILED etc/tests/test_integration.py::test_add_server - IndexError: list index out of range
```

To solve these errors:
1. Ensure `federation` is in the list of `CANDIG_AUTH_MODULES` in `.env` (though it is present by default).

2. If you already have federation running, restart the container with:
```bash
make clean-federation
make build-federation
make compose-federation
```

## Ingest the synthetic clinical dataset

Synthetic data is ingested as part of the integration tests. By default, this data is deleted after tests are run. If you'd like to keep the data in the platform, ensure the `KEEP_TEST_DATA` variable in your .env file is set to `true`.

If you would like to ingest the data separately, follow the [clinical ingest](../guides/ingest/ingest-clinical#ingesting-clinical-data-into-candig) and [genomic ingest](../guides/ingest/ingest-genomic) instructions using the test files in `lib/candig-ingest/candigv2-ingest/tests`,  using `small_dataset_clinical_ingest.json` for clinical ingest and `small_dataset_genomic_ingest.json` for genomic ingest.

You should now see the ingested data in the [data portal](http://candig.docker.internal:5080).
