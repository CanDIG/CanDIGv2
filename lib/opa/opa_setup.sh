#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt


opa_runner=$(docker ps | grep "opa-runner" | awk '{print $1}')

docker exec $opa_runner python3 app/permissions_engine/fetch_keys.py
docker restart candigv2_opa_1

docker exec $opa_runner python3 app/tests/create_katsu_test_datasets.py
