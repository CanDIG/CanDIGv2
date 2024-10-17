#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for katsu to start"
katsu=$(docker ps --format "{{.Names}}" | grep katsu_1)
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  katsu=$(docker ps --format "{{.Names}}" | grep katsu_1)
done
sleep 5


bash $PWD/create_service_store.sh "katsu"

docker restart $katsu
