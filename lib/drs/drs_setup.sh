#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for drs to start"
drs=$(docker ps --format "{{.Names}}" | grep drs)
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  drs=$(docker ps --format "{{.Names}}" | grep drs)
done

python settings.py
source env.sh
bash $PWD/create_service_store.sh "drs"
