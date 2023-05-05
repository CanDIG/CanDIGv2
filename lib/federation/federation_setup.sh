#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for federation to start"
docker ps --format "{{.Names}}" | grep federation_1
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  docker ps --format "{{.Names}}" | grep federation_1
done

source env.sh
python $PWD/lib/federation/initialize.py
