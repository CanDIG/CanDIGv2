#!/usr/bin/env bash

set -Euo pipefail
source env.sh

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

# If present, create and authorize default site admin as CanDIG authorized user:
site_admin_token=$(python site_admin_token.py)
if [[ $CANDIG_SITE_ADMIN_USER != "" ]]; then
  bash $PWD/exec_with_expected.sh "curl -si \"${CANDIG_URL}/ingest/service-info\" -H \"Authorization: Bearer ${site_admin_token}\"" "200 OK"
  while [ $? -ne 0 ]
  do
    echo "..."
      sleep 1
      bash $PWD/exec_with_expected.sh "curl -si \"${CANDIG_URL}/ingest/service-info\" -H \"Authorization: Bearer ${site_admin_token}\"" "200 OK"
  done

  echo ">> approving $CANDIG_SITE_ADMIN_USER as a CanDIG authorized user"
  bash $PWD/exec_with_expected.sh "curl -sX \"POST\" \"${CANDIG_URL}/ingest/user/pending/request\" -H \"Authorization: Bearer ${site_admin_token}\"" "$CANDIG_SITE_ADMIN_USER"
  bash $PWD/exec_with_expected.sh "curl -sX \"POST\" \"${CANDIG_URL}/ingest/user/pending/${CANDIG_SITE_ADMIN_USER}\" -H \"Authorization: Bearer ${site_admin_token}\"" "$CANDIG_SITE_ADMIN_USER"
fi

python $PWD/lib/candig-ingest/candigv2-ingest/generate_test_data.py --commit 921b35d --prefix $CANDIG_SITE_LOCATION --tmp tmp/data/synthdata --delete
