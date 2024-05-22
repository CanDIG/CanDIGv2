#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for htsget to start"
htsget=$(docker ps --format "{{.Names}}" | grep htsget)
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  htsget=$(docker ps --format "{{.Names}}" | grep htsget)
done

python settings.py
source env.sh
bash $PWD/create_service_store.sh "htsget"
docker restart $htsget
