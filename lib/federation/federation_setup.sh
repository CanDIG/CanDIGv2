#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for federation to start"
federation=$(docker ps --format "{{.Names}}" | grep federation)
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  federation=$(docker ps --format "{{.Names}}" | grep federation)
done

python settings.py
source env.sh
bash $PWD/create_service_store.sh "federation"
docker restart $federation

python $PWD/lib/federation/initialize.py
