#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for opa_runner to start"
docker ps --format "{{.Names}}" | grep opa-runner
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  docker ps --format "{{.Names}}" | grep opa-runner
done
sleep 5

opa_runner=$(docker ps -a --format "{{.Names}}" | grep "opa-runner" | awk '{print $1}')
opa_container=$(docker ps -a --format "{{.Names}}" | grep "opa_" | awk '{print $1}')

docker exec $opa_runner python3 app/permissions_engine/fetch_keys.py
docker start $opa_container

# docker exec $opa_runner python3 app/tests/create_katsu_test_datasets.py
