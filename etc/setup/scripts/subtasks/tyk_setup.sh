#! /usr/bin/env bash
set -e

# This script will set up a full tyk environment on your local CanDIGv2 cluster

# ** Be sure to invoke this from the Makefile at the project's root directory [CanDigV2] **

# Load Tyk template (.tpl) files, populate them
# with project .env variables, and then spit
# them out to ./lib/authentication/tyk/tmp/*

mkdir -p ${PWD}/lib/authentication/tyk/tmp

# api_auth.json
echo "Working on api_auth.json .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/api_auth.json.tpl > ${PWD}/lib/authentication/tyk/tmp/api_auth.json

# api_candig.json
echo "Working on api_candig.json .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/api_candig.json.tpl > ${PWD}/lib/authentication/tyk/tmp/api_candig.json

# policies.json
echo "Working on policies.json .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/policies.json.tpl > ${PWD}/lib/authentication/tyk/tmp/policies.json

# tyk.conf
echo "Working on tyk.conf .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/tyk.conf.tpl > ${PWD}/lib/authentication/tyk/tmp/tyk.conf

echo "Working on authMiddleware.js .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/authMiddleware.js > ${PWD}/lib/authentication/tyk/tmp/authMiddleware.js

## TODO: tyk_analytics.conf , key_request.json.tpl


# Copy files from template configs

echo "Copying permissionsStoreMiddleware.js .."
cp ${PWD}/lib/authentication/tyk/configuration_templates/permissionsStoreMiddleware.js ${PWD}/lib/authentication/tyk/tmp/permissionsStoreMiddleware.js

echo "Copying virtualLogin.js .."
cp ${PWD}/lib/authentication/tyk/configuration_templates/virtualLogin.js ${PWD}/lib/authentication/tyk/tmp/virtualLogin.js

echo "Copying virtualLogout.js .."
cp ${PWD}/lib/authentication/tyk/configuration_templates/virtualLogout.js ${PWD}/lib/authentication/tyk/tmp/virtualLogout.js

echo "Copying virtualToken.js .."
cp ${PWD}/lib/authentication/tyk/configuration_templates/virtualToken.js ${PWD}/lib/authentication/tyk/tmp/virtualToken.js


echo "-- Tyk Setup Done! --"
echo


# Verify if tyk container is running
TYK_CONTAINERS=$(echo $(docker ps | grep tyk | wc -l))
echo "Number of tyk containers running: ${TYK_CONTAINERS}"
if [[ $TYK_CONTAINERS -eq 0 ]]; then
   echo "Booting tyk container!"
   docker-compose -f ${PWD}/lib/compose/docker-compose.yml -f ${PWD}/lib/authentication/docker-compose.yml up -d tyk
   sleep 5
fi
