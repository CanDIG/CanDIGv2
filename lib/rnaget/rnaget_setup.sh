#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for rnaget to start"
rnaget=$(docker ps --format "{{.Names}}" | grep rnaget_1)
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  rnaget=$(docker ps --format "{{.Names}}" | grep rnaget_1)
done
sleep 5

python settings.py
source env.sh
bash $PWD/create_service_store.sh "rnaget"

