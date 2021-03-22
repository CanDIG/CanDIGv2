#! /usr/bin/env bash
set -e

# This script will set up all of the arbiters needed on your local CanDIGv2 cluster


ARBITER_IMAGES=$(echo $(docker ps | grep arbiter | wc -l))
if [[ $ARBITER_IMAGES -eq 0 ]]; then
   echo "Building Arbiter Image!"
   docker build --tag ${DOCKER_REGISTRY}/arbiter:latest --build-arg venv_python=3.7 ${PWD}/lib/authorization/arbiter
fi



# Verify if any arbiter containers are running
ARBITER_CONTAINERS=$(echo $(docker ps | grep arbiter | wc -l))
echo "Number of arbiter containers running: ${ARBITER_CONTAINERS}"
if [[ $ARBITER_CONTAINERS -eq 0 ]]; then
   # First arbiter of potentially many..
   echo "Booting candig server arbiter container!"
   docker-compose -f ${PWD}/lib/compose/docker-compose.yml -f ${PWD}/lib/candig-server/docker-compose.yml up -d candig-server-arbiter
fi

echo "-- Arbiter Setup Done! --"