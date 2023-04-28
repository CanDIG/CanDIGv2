#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for federation-service to start"
docker ps --format "{{.Names}}" | grep federation-service_1
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  docker ps --format "{{.Names}}" | grep federation-service_1
done

source env.sh
python $PWD/lib/federation-service/initialize.py
