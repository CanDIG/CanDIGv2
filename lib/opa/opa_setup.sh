#!/usr/bin/env bash

set -Eeuo pipefail

LOGFILE=$PWD/tmp/progress.txt


opa_runner=$(docker ps | grep "opa-runner" | awk '{print $1}')

docker exec $opa_runner python3 app/permissions_engine/fetch_keys.py

opa=$(docker ps | grep "candigv2_opa_1" | awk '{print $1}')

docker restart $opa
