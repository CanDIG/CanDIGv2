#! /usr/bin/env bash
set -e

# This script will set up all of the arbiters needed on your local CanDIGv2 cluster


ARBITER_IMAGES=$(echo $(docker ps | grep arbiter | wc -l))
if [[ $ARBITER_IMAGES -eq 0 ]]; then
   echo "Building Arbiter Image!"
   docker build --tag ${DOCKER_REGISTRY}/arbiter:latest --build-arg venv_python=3.7 ${PWD}/lib/authz/arbiter
fi



# Verify if arbiter container is running
ARBITER_CONTAINERS=$(echo $(docker ps | grep arbiter | wc -l))
echo "Number of arbiter containers running: ${ARBITER_CONTAINERS}"
if [[ $ARBITER_CONTAINERS -eq 0 ]]; then
   echo "Booting candig server arbiter container!"
   docker-compose -f ${PWD}/lib/candig_server/docker-compose.yml up -d candig-server-arbiter
   sleep 5
fi

echo "-- Arbiter Setup Done! --"