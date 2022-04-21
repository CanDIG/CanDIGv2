#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt


opa_runner=$(docker ps --format "{{.Names}}" | grep "opa-runner" | awk '{print $1}')
opa_container=$(docker ps --format "{{.Names}}" | grep "opa_" | awk '{print $1}')

docker exec $opa_runner python3 app/permissions_engine/fetch_keys.py
docker restart $opa_container

# docker exec $opa_runner python3 app/tests/create_katsu_test_datasets.py
