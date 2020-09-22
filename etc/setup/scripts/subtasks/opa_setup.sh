#! /usr/bin/env bash
# This script will set up a full opa environment on your local CanDIGv2 cluster

# Verify if opa container is running
OPA_CONTAINERS=$(echo $(docker ps | grep opa | wc -l))
echo "Number of opa containers running: ${OPA_CONTAINERS}"
if [[ $OPA_CONTAINERS -eq 0 ]]; then
   echo "Booting opa container!"
   docker-compose -f ${PWD}/lib/authz/docker-compose.yml up -d opa
   sleep 5
fi

echo "-- Opa Setup Done! --"