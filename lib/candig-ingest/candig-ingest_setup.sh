#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for candig-ingest to start"
docker ps --format "{{.Names}}" | grep candig-ingest_1
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  docker ps --format "{{.Names}}" | grep candig-ingest_1
done
sleep 5


bash $PWD/create_service_store.sh "candig-ingest"

