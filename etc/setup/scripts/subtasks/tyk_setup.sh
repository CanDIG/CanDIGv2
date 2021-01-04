#! /usr/bin/env bash
set -e

# This script will set up a full tyk environment on your local CanDIGv2 cluster

# ** Be sure to invoke this from the Makefile at the project's root directory [CanDigV2] **

# Load Tyk template (.tpl) files, populate them 
# with project .env variables, and then spit 
# them out to ./lib/authz/tyk/data/*

mkdir -p ${PWD}/lib/authz/tyk/data
$PROD_SUDO chown -R $USER ${PWD}/lib/authz/tyk
$PROD_SUDO chgrp -R $USER ${PWD}/lib/authz/tyk

# api_auth.json
echo "Working on api_auth.json .."
envsubst < ${PWD}/etc/setup/templates/configs/tyk/confs/api_auth.json.tpl > ${PWD}/lib/authz/tyk/data/api_auth.json

# api_candig.json
echo "Working on api_candig.json .."
envsubst < ${PWD}/etc/setup/templates/configs/tyk/confs/api_candig.json.tpl > ${PWD}/lib/authz/tyk/data/api_candig.json

# policies.json
echo "Working on policies.json .."
envsubst < ${PWD}/etc/setup/templates/configs/tyk/confs/policies.json.tpl > ${PWD}/lib/authz/tyk/data/policies.json

# tyk.conf
echo "Working on tyk.conf .."
envsubst < ${PWD}/etc/setup/templates/configs/tyk/confs/tyk.conf.tpl > ${PWD}/lib/authz/tyk/data/tyk.conf

echo "Working on authMiddleware.js .."
envsubst < ${PWD}/etc/setup/templates/configs/tyk/confs/authMiddleware.js > ${PWD}/lib/authz/tyk/data/authMiddleware.js

## TODO: tyk_analytics.conf , key_request.json.tpl


# Copy files from template configs

echo "Copying permissionsStoreMiddleware.js .."
cp ${PWD}/etc/setup/templates/configs/tyk/confs/permissionsStoreMiddleware.js ${PWD}/lib/authz/tyk/data/permissionsStoreMiddleware.js

echo "Copying virtualLogin.js .."
cp ${PWD}/etc/setup/templates/configs/tyk/confs/virtualLogin.js ${PWD}/lib/authz/tyk/data/virtualLogin.js

echo "Copying virtualLogout.js .."
cp ${PWD}/etc/setup/templates/configs/tyk/confs/virtualLogout.js ${PWD}/lib/authz/tyk/data/virtualLogout.js

echo "Copying virtualToken.js .."
cp ${PWD}/etc/setup/templates/configs/tyk/confs/virtualToken.js ${PWD}/lib/authz/tyk/data/virtualToken.js


echo "-- Tyk Setup Done! --"
echo


# Verify if tyk container is running
TYK_CONTAINERS=$(echo $(docker ps | grep tyk | wc -l))
echo "Number of tyk containers running: ${TYK_CONTAINERS}"
if [[ $TYK_CONTAINERS -eq 0 ]]; then
   echo "Booting tyk container!"
   docker-compose -f ${PWD}/lib/authz/docker-compose.yml up -d tyk
   sleep 5
fi
