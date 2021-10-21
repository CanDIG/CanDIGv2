#!/usr/bin/env bash

set -Eeuo pipefail

# This script will set up a full tyk environment on your local CanDIGv2 cluster.
# Be sure to invoke this from the Makefile at the project's root directory [CanDIGv2].
# Load Tyk template (.tpl) files, populate them with project .env variables, and then spit
# them out to ./lib/tyk/tmp/*.

# TODO: this image uses temp dir inside the lib/tyk which breaks the convention of this repo
CONFIG_DIR="$PWD/lib/tyk/tmp"

KEYCLOAK_SECRET_VAL=$(cat $PWD/tmp/secrets/keycloak-client-local-candig-secret)
export KEYCLOAK_SECRET=$KEYCLOAK_SECRET_VAL

KEYCLOAK_CLIENT_ID_64_VAL=$(cat $PWD/tmp/secrets/keycloak-client-local-candig-id-64)
export KEYCLOAK_CLIENT_ID_64=$KEYCLOAK_CLIENT_ID_64_VAL

TYK_SECRET_KEY_VAL=$(cat $PWD/tmp/secrets/tyk-secret-key)
export TYK_SECRET_KEY=$TYK_SECRET_KEY_VAL

TYK_NODE_SECRET_KEY_VAL=$(cat $PWD/tmp/secrets/tyk-node-secret-key)
export TYK_NODE_SECRET_KEY=$TYK_NODE_SECRET_KEY_VAL

TYK_ANALYTIC_ADMIN_SECRET_VAL=$(cat $PWD/tmp/secrets/tyk-analytics-admin-key)
export TYK_ANALYTIC_ADMIN_SECRET=$TYK_ANALYTIC_ADMIN_SECRET_VAL

mkdir -p $CONFIG_DIR $CONFIG_DIR/apps $CONFIG_DIR/policies $CONFIG_DIR/middleware

echo "Working on tyk.conf"
envsubst < ${PWD}/lib/tyk/configuration_templates/tyk.conf.tpl > ${CONFIG_DIR}/tyk.conf

echo "Working on authMiddleware.js"
envsubst < ${PWD}/lib/tyk/configuration_templates/authMiddleware.js > ${CONFIG_DIR}/middleware/authMiddleware.js

echo "Working on api_auth.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/api_auth.json.tpl > ${CONFIG_DIR}/apps/api_auth.json

echo "Working on api_candig.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/api_candig.json.tpl > ${CONFIG_DIR}/apps/api_candig.json

echo "Working on policies.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/policies.json.tpl > ${CONFIG_DIR}/policies/policies.json

echo "Working on key_request.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/key_request.json.tpl > ${CONFIG_DIR}/key_request.json

echo "Working on tyk_analytics"
envsubst < ${PWD}/lib/tyk/configuration_templates/tyk_analytics.conf.tpl > ${CONFIG_DIR}/tyk_analytics.conf

# Copy files from template configs

echo "Copying virtualLogin.js"
cp ${PWD}/lib/tyk/configuration_templates/virtualLogin.js ${CONFIG_DIR}/middleware/virtualLogin.js

echo "Copying virtualLogout.js"
cp ${PWD}/lib/tyk/configuration_templates/virtualLogout.js ${CONFIG_DIR}/middleware/virtualLogout.js

echo "Copying virtualToken.js"
cp ${PWD}/lib/tyk/configuration_templates/virtualToken.js ${CONFIG_DIR}/middleware/virtualToken.js

echo "Copying permissionsStoreMiddleware.js"
cp ${PWD}/lib/tyk/configuration_templates/permissionsStoreMiddleware.js ${CONFIG_DIR}/middleware/permissionsStoreMiddleware.js



echo "Tyk configuration generated!"
