#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs after the container is composed.
# make sure we have all the env vars:
python settings.py
source env.sh

echo ">> waiting for opa_runner to start"
docker ps --format "{{.Names}}" | grep opa-runner
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  docker ps --format "{{.Names}}" | grep opa-runner
done
sleep 5

opa_runner=$(docker ps -a --format "{{.Names}}" | grep "opa-runner" | awk '{print $1}')
opa_container=$(docker ps -a --format "{{.Names}}" | grep "opa_" | awk '{print $1}')

bash $PWD/create_service_store.sh "opa"
python -c "from site_admin_token import get_site_admin_token
print(get_site_admin_token())" > bearer.txt
docker cp bearer.txt $opa_runner:/app/
rm bearer.txt

docker exec $opa_runner touch /app/initial_setup

docker restart $opa_runner
docker restart $opa_container

