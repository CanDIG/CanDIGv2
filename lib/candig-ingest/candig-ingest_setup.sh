#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.

echo ">> waiting for candig-ingest to start"
ingest=$(docker ps --format "{{.Names}}" | grep candig-ingest_1)
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  ingest=$(docker ps --format "{{.Names}}" | grep candig-ingest_1)
done
sleep 5


bash $PWD/create_service_store.sh "candig-ingest"

docker restart $ingest

bin/miniconda3/bin/python -m pip install GitPython
# bin/miniconda3/bin/python -m pip install clinical_etl@git+https://github.com/CanDIG/clinical_ETL_code.git@v2.2.0
bin/miniconda3/bin/python $PWD/lib/candig-ingest/candigv2-ingest/generate_test_data.py --output tmp/data/synthdata
