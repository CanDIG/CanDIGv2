#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=$PWD/tmp/progress.txt

# This script runs before the container is composed.

# This script will set up a full tyk environment on your local CanDIGv2 cluster.
# Be sure to invoke this from the Makefile at the project's root directory [CanDIGv2].
# Load Tyk template (.tpl) files, populate them with project .env variables, and then spit
# them out to ./lib/tyk/tmp/*.

# TODO: this image uses temp dir inside the lib/tyk which deviates from convention of this repo
# see Makefile.authx for other details.
export CONFIG_DIR="$PWD/lib/tyk/tmp"

KEYCLOAK_SECRET_VAL=$(cat $PWD/tmp/secrets/keycloak-client-${KEYCLOAK_CLIENT_ID}-secret)
export KEYCLOAK_SECRET=$KEYCLOAK_SECRET_VAL

KEYCLOAK_CLIENT_ID_64_VAL=$(cat $PWD/tmp/secrets/keycloak-client-${KEYCLOAK_CLIENT_ID}-id-64)
export KEYCLOAK_CLIENT_ID_64=$KEYCLOAK_CLIENT_ID_64_VAL

TYK_SECRET_KEY_VAL=$(cat $PWD/tmp/secrets/tyk-secret-key)
export TYK_SECRET_KEY=$TYK_SECRET_KEY_VAL

TYK_ANALYTIC_ADMIN_SECRET_VAL=$(cat $PWD/tmp/secrets/tyk-analytics-admin-key)
export TYK_ANALYTIC_ADMIN_SECRET=$TYK_ANALYTIC_ADMIN_SECRET_VAL

KEYCLOAK_PUBLIC_KEY_VAL=$(cat $PWD/tmp/secrets/keycloak-public-key)
export KEYCLOAK_PUBLIC_KEY=$KEYCLOAK_PUBLIC_KEY_VAL

REDIS_SECRET_KEY_VAL=$(cat $PWD/tmp/secrets/redis-secret-key)
export REDIS_SECRET_KEY=$REDIS_SECRET_KEY_VAL

mkdir -p $CONFIG_DIR $CONFIG_DIR/apps $CONFIG_DIR/policies $CONFIG_DIR/middleware

# Copy files from template configs

echo "Working on tyk.conf"  | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/tyk.conf.tpl > ${CONFIG_DIR}/tyk.conf

echo "Working on authMiddleware.js" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/authMiddleware.js > ${CONFIG_DIR}/middleware/authMiddleware.js

echo "Working on backendAuthMiddleware.js" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/backendAuthMiddleware.js > ${CONFIG_DIR}/middleware/backendAuthMiddleware.js

echo "Working on frontendAuthMiddleware.js" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/frontendAuthMiddleware.js > ${CONFIG_DIR}/middleware/frontendAuthMiddleware.js

echo "Working on tyk_analytics" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/tyk_analytics.conf.tpl > ${CONFIG_DIR}/tyk_analytics.conf

echo "Copying virtualLogin.js" | tee -a $LOGFILE
cp ${PWD}/lib/tyk/configuration_templates/virtualLogin.js ${CONFIG_DIR}/middleware/virtualLogin.js

echo "Copying virtualLogout.js" | tee -a $LOGFILE
cp ${PWD}/lib/tyk/configuration_templates/virtualLogout.js ${CONFIG_DIR}/middleware/virtualLogout.js

echo "Copying virtualToken.js" | tee -a $LOGFILE
cp ${PWD}/lib/tyk/configuration_templates/virtualToken.js ${CONFIG_DIR}/middleware/virtualToken.js

echo "Copying permissionsStoreMiddleware.js" | tee -a $LOGFILE
cp ${PWD}/lib/tyk/configuration_templates/permissionsStoreMiddleware.js ${CONFIG_DIR}/middleware/permissionsStoreMiddleware.js

echo "Working on api_auth.json" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/api_auth.json.tpl > ${CONFIG_DIR}/apps/${TYK_AUTH_API_ID}.json

echo "Creating policies.json.tpl"
cp lib/tyk/configuration_templates/policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_katsu.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/api_katsu.json.tpl > ${CONFIG_DIR}/apps/${TYK_KATSU_API_ID}.json
cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
{"${TYK_KATSU_API_ID}": {
    "allowed_urls": [],
    "api_id": "${TYK_KATSU_API_ID}",
    "api_name": "${TYK_KATSU_API_SLUG}",
    "versions": [
        "Default"
    ]
}
}
' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_candig_data_portal.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/api_mcode_candig_data_portal.json.tpl > ${CONFIG_DIR}/apps/${TYK_CANDIG_DATA_PORTAL_API_ID}.json
cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
{"${TYK_CANDIG_DATA_PORTAL_API_ID}": {
    "allowed_urls": [],
    "api_id": "${TYK_CANDIG_DATA_PORTAL_API_ID}",
    "api_name": "${TYK_CANDIG_DATA_PORTAL_API_SLUG}",
    "versions": [
        "Default"
    ]
}
}
' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_ingest.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/api_ingest.json.tpl > ${CONFIG_DIR}/apps/${TYK_INGEST_API_ID}.json
cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
{"${TYK_INGEST_API_ID}": {
    "allowed_urls": [],
    "api_id": "${TYK_INGEST_API_ID}",
    "api_name": "${TYK_INGEST_API_SLUG}",
    "versions": [
        "Default"
    ]
}
}
' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_graphql.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/api_graphql.json.tpl > ${CONFIG_DIR}/apps/${TYK_GRAPHQL_API_ID}.json
cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
{"${TYK_GRAPHQL_API_ID}": {
    "allowed_urls": [],
    "api_id": "${TYK_GRAPHQL_API_ID}",
    "api_name": "${TYK_GRAPHQL_API_SLUG}",
    "versions": [
        "Default"
    ]
}
}
' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_htsget.json" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/api_htsget.json.tpl > ${CONFIG_DIR}/apps/${TYK_HTSGET_API_ID}.json
cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
{"${TYK_HTSGET_API_ID}": {
    "allowed_urls": [],
    "api_id": "${TYK_HTSGET_API_ID}",
    "api_name": "${TYK_HTSGET_API_SLUG}",
    "versions": [
        "Default"
    ]
}
}
' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_opa.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/api_opa.json.tpl > ${CONFIG_DIR}/apps/${TYK_OPA_API_ID}.json
cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
{"${TYK_OPA_API_ID}": {
    "allowed_urls": [],
    "api_id": "${TYK_OPA_API_ID}",
    "api_name": "${TYK_OPA_API_SLUG}",
    "versions": [
        "Default"
    ]
}
}
' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_vault.json"
envsubst < ${PWD}/lib/tyk/configuration_templates/api_vault.json.tpl > ${CONFIG_DIR}/apps/${TYK_VAULT_API_ID}.json
cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
{"${TYK_VAULT_API_ID}": {
    "allowed_urls": [],
    "api_id": "${TYK_VAULT_API_ID}",
    "api_name": "${TYK_VAULT_API_SLUG}",
    "versions": [
        "Default"
    ]
}
}
' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_federation.json" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/api_federation.json.tpl > ${CONFIG_DIR}/apps/${TYK_FEDERATION_API_ID}.json
cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
{"${TYK_FEDERATION_API_ID}": {
    "allowed_urls": [],
    "api_id": "${TYK_FEDERATION_API_ID}",
    "api_name": "${TYK_FEDERATION_API_SLUG}",
    "versions": [
        "Default"
    ]
}
}
' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_query.json" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/api_query.json.tpl > ${CONFIG_DIR}/apps/${TYK_QUERY_API_ID}.json
cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
{"${TYK_QUERY_API_ID}": {
    "allowed_urls": [],
    "api_id": "${TYK_QUERY_API_ID}",
    "api_name": "${TYK_QUERY_API_SLUG}",
    "versions": [
        "Default"
    ]
}
}
' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on api_query.json" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/configuration_templates/api_query.json.tpl > ${CONFIG_DIR}/apps/${TYK_QUERY_API_ID}.json

# Extra APIs can be added here
# echo "Working on api_example.json"
# envsubst < ${PWD}/lib/tyk/configuration_templates/api_example.json.tpl > ${CONFIG_DIR}/apps/${TYK_EXAMPLE_API_ID}.json
# cat lib/tyk/tmp/policies.json.tpl | jq '.["${TYK_POLICY_ID}"]["access_rights"] +=
# {"${TYK_EXAMPLE_API_ID}": {
#     "allowed_urls": [],
#     "api_id": "${TYK_EXAMPLE_API_ID}",
#     "api_name": "${TYK_EXAMPLE_API_SLUG}",
#     "versions": [
#         "Default"
#     ]
# }
# }
# ' > lib/tyk/tmp/tmp_policies.json.tpl
mv lib/tyk/tmp/tmp_policies.json.tpl lib/tyk/tmp/policies.json.tpl

echo "Working on policies.json" | tee -a $LOGFILE
envsubst < ${PWD}/lib/tyk/tmp/policies.json.tpl > ${CONFIG_DIR}/policies/policies.json

echo "Tyk configuration generated!" | tee -a $LOGFILE
