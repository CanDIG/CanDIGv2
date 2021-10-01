#! /usr/bin/env bash
set -e

# This script will set up a full tyk environment on your local CanDIGv2 cluster

# ** Be sure to invoke this from the Makefile at the project's root directory [CanDIGv2] **

# Load Tyk template (.tpl) files, populate them
# with project .env variables, and then spit
# them out to ./lib/authentication/tyk/tmp/*

CONFIG_DIR="$PWD/tmp/configs/tyk-gateway"

mkdir -p $CONFIG_DIR

# api_auth.json
echo "Working on api_auth.json .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/api_auth.json.tpl > ${CONFIG_DIR}/apps/api_auth.json

# api_candig.json
echo "Working on api_candig.json .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/api_candig.json.tpl > ${CONFIG_DIR}/apps/api_candig.json

# policies.json
echo "Working on policies.json .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/policies.json.tpl > ${CONFIG_DIR}/policies/policies.json

# tyk.conf
echo "Working on tyk.conf .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/tyk.conf.tpl > ${CONFIG_DIR}/tyk.conf

echo "Working on authMiddleware.js .."
envsubst < ${PWD}/lib/authentication/tyk/configuration_templates/authMiddleware.js > ${CONFIG_DIR}/middleware/authMiddleware.js

## TODO: tyk_analytics.conf , key_request.json.tpl


# Copy files from template configs

echo "Copying permissionsStoreMiddleware.js .."
cp ${PWD}/lib/authentication/tyk/configuration_templates/permissionsStoreMiddleware.js ${CONFIG_DIR}/middleware/permissionsStoreMiddleware.js

echo "Copying virtualLogin.js .."
cp ${PWD}/lib/authentication/tyk/configuration_templates/virtualLogin.js ${CONFIG_DIR}/middleware/virtualLogin.js

echo "Copying virtualLogout.js .."
cp ${PWD}/lib/authentication/tyk/configuration_templates/virtualLogout.js ${CONFIG_DIR}/middleware/virtualLogout.js

echo "Copying virtualToken.js .."
cp ${PWD}/lib/authentication/tyk/configuration_templates/virtualToken.js ${CONFIG_DIR}/middleware/virtualToken.js


echo "-- Tyk Setup Done! --"
