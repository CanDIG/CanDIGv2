#! /usr/bin/env bash
set -e

# This script will set up a full opa environment on your local CanDIGv2 cluster

#mkdir -p ${PWD}/lib/authz/opa/data

# -- TEMP:
mkdir -p ${PWD}/lib/candig_server/authz/opa
$PROD_SUDO chown -R $USER ${PWD}/lib/candig_server/authz
$PROD_SUDO chgrp -R $USER ${PWD}/lib/candig_server/authz
# --

# policy.rego
echo "Working on candig_server_policy.rego .."
envsubst < ${PWD}/etc/setup/templates/configs/opa/candig_server_policy.rego.tpl > ${PWD}/lib/candig_server/authz/opa/policy.rego


# Verify if opa container is running
OPA_CONTAINERS=$(echo $(docker ps | grep candig-server-authorization | wc -l))
echo "Number of candig_server_policy containers running: ${OPA_CONTAINERS}"
if [[ $OPA_CONTAINERS -eq 0 ]]; then
   echo "Booting opa container!"
   docker-compose -f ${PWD}/lib/candig_server/docker-compose.yml up -d candig-server-authorization
   sleep 5
fi

echo "-- Opa Setup Done! --"