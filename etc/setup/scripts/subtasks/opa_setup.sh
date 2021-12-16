#! /usr/bin/env bash
set -e

# This script will set up a full opa environment on your local CanDIGv2 cluster

mkdir -p ${PWD}/lib/candig-server/authorization/tmp

# policy.rego
echo "Working on candig-server.policy.rego .."
envsubst < ${PWD}/lib/candig-server/authorization/configuration_templates/candig-server.policy.rego.tpl > ${PWD}/lib/candig-server/authorization/tmp/policy.rego


# Verify if opa container is running
OPA_CONTAINERS=$(echo $(docker ps | grep candig-server-opa | wc -l))
echo "Number of candig-server_policy containers running: ${OPA_CONTAINERS}"
if [[ $OPA_CONTAINERS -eq 0 ]]; then
   echo "Booting opa container!"
   export SERVICE=candig-server-opa && make compose-candig-server
   sleep 5
fi

echo "-- Opa Setup Done! --"
