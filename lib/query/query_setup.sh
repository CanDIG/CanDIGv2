#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

# make sure we have all the env vars:
python settings.py
source env.sh

echo ">> waiting for query to start"
docker ps --format "{{.Names}}" | grep query_1
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  docker ps --format "{{.Names}}" | grep query_1
done
sleep 5


bash $PWD/create_service_store.sh "query"

