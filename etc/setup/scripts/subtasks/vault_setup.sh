#! /usr/bin/env bash
set -e

# This script will set up a full vault environment on your local CanDIGv2 cluster

# Automates instructions written at
# https://github.com/CanDIG/CanDIGv2/blob/stable/docs/configure-vault.md

# Related resources:
# https://www.bogotobogo.com/DevOps/Docker/Docker-Vault-Consul.php
# https://learn.hashicorp.com/tutorials/vault/identity
# https://stackoverflow.com/questions/35703317/docker-exec-write-text-to-file-in-container
# https://www.vaultproject.io/api-docs/secret/identity/entity#batch-delete-entities

mkdir -p ${PWD}/lib/authorization/vault/tmp

# vault-config.json
echo "Working on vault-config.json .."
envsubst < ${PWD}/etc/setup/templates/configs/vault/vault-config.json.tpl > ${PWD}/lib/authorization/vault/tmp/vault-config.json

# boot container
docker-compose -f ${PWD}/lib/compose/docker-compose.yml -f ${PWD}/lib/authorization/docker-compose.yml up -d vault

# -- todo: run only if not already initialized --
# --- temp
echo ">> waiting 3 seconds to let vault start"
sleep 3
# ---

# gather keys and login token
stuff=$(docker exec vault sh -c "vault operator init") # | head -7 | rev | cut -d " " -f1 | rev)
echo "found stuff as ${stuff}"

key_1=$(echo -n "${stuff}" | grep 'Unseal Key 1: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
key_2=$(echo -n "${stuff}" | grep 'Unseal Key 2: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
key_3=$(echo -n "${stuff}" | grep 'Unseal Key 3: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
key_4=$(echo -n "${stuff}" | grep 'Unseal Key 4: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
key_5=$(echo -n "${stuff}" | grep 'Unseal Key 5: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')
key_root=$(echo -n "${stuff}" | grep 'Initial Root Token: ' | awk '{print $4}' | sed 's/[^a-zA-Z0-9\.\/\+]//g' | sed -e 's/\(0m\)*$//g' | tr -d '[:space:]')

echo "found key1: ${key_1}"
echo "found key2: ${key_2}"
echo "found key3: ${key_3}"
echo "found key4: ${key_4}"
echo "found key5: ${key_5}"
echo "found root: ${key_root}"

# save keys
touch ${PWD}/lib/authorization/vault/tmp/keys.txt
echo -e "key1: ${key_1}" >> ${PWD}/lib/authorization/vault/tmp/keys.txt
echo -e "key2: ${key_2}" >> ${PWD}/lib/authorization/vault/tmp/keys.txt
echo -e "key3: ${key_3}" >> ${PWD}/lib/authorization/vault/tmp/keys.txt
echo -e "key4: ${key_4}" >> ${PWD}/lib/authorization/vault/tmp/keys.txt
echo -e "key5: ${key_5}" >> ${PWD}/lib/authorization/vault/tmp/keys.txt
echo -e "root: ${key_root}" >> ${PWD}/lib/authorization/vault/tmp/keys.txt


echo ">> attempting to automatically unseal vault:"
docker exec vault sh -c "vault operator unseal ${key_1}"
docker exec vault sh -c "vault operator unseal ${key_2}"
docker exec vault sh -c "vault operator unseal ${key_3}"


# login
echo
echo ">> logging in automatically -- " #copy and paste this: ${key_root}"
docker exec vault sh -c "vault login ${key_root}"

# configuration
# audit file
echo
echo ">> enabling audit file"
docker exec vault sh -c "vault audit enable file file_path=/tmp/vault-audit.log"

# enable jwt
echo
echo ">> enabling jwt"
docker exec vault sh -c "vault auth enable jwt"

# tyk policy
echo
echo ">> setting up tyk policy"
docker exec vault sh -c "echo 'path \"identity/oidc/token/*\" {capabilities = [\"create\", \"read\"]}' >> vault-policy.hcl; vault policy write tyk vault-policy.hcl"

# user claims
echo
echo ">> setting up user claims"
docker exec vault sh -c "vault write auth/jwt/role/test-role user_claim=preferred_username bound_audiences=${KEYCLOAK_CLIENT_ID} role_type=jwt policies=tyk ttl=1h"

# configure jwt
echo
echo ">> configuring jwt stuff"

docker exec vault sh -c "vault write auth/jwt/config oidc_discovery_url=\"${TEMP_KEYCLOAK_SERVICE_PUBLIC_URL}/auth/realms/candig\" default_role=\"test-role\""
#http://${CANDIG_AUTH_CONTAINER_NAME}:8081/auth/realms/candig

# create users
echo
echo ">> creating user $KEYCLOAK_TEST_USER"

export TEMPLATE_USER=$(echo $KEYCLOAK_TEST_USER)
export TEMPLATE_DATASET_PERMISSIONS=4
TEST_USER_PERMISSIONS_DATASTRUCTURE=$(envsubst < ${PWD}/etc/setup/templates/configs/vault/vault-entity-entitlements.json.tpl)

test_user_output=$(docker exec vault sh -c "echo '${TEST_USER_PERMISSIONS_DATASTRUCTURE}' > ${KEYCLOAK_TEST_USER}.json; vault write identity/entity @${KEYCLOAK_TEST_USER}.json; rm ${KEYCLOAK_TEST_USER}.json;")

ENTITY_ID=$(echo "${test_user_output}" | grep id | awk '{print $2}')
echo ">>> found entity id : ${ENTITY_ID}"


echo
echo ">> creating user $KEYCLOAK_TEST_USER_TWO"

export TEMPLATE_USER=$(echo $KEYCLOAK_TEST_USER_TWO)
export TEMPLATE_DATASET_PERMISSIONS=1
TEST_USER_TWO_PERMISSIONS_DATASTRUCTURE=$(envsubst < ${PWD}/etc/setup/templates/configs/vault/vault-entity-entitlements.json.tpl)

test_user_output_two=$(docker exec vault sh -c "echo '${TEST_USER_TWO_PERMISSIONS_DATASTRUCTURE}' > ${KEYCLOAK_TEST_USER_TWO}.json; vault write identity/entity @${KEYCLOAK_TEST_USER_TWO}.json; rm ${KEYCLOAK_TEST_USER_TWO}.json;")

ENTITY_ID_TWO=$(echo "${test_user_output_two}" | grep id | awk '{print $2}')
echo ">>> found entity id 2: ${ENTITY_ID_TWO}"



# setup aliases
echo
echo ">> setting up alias for $KEYCLOAK_TEST_USER"
AUTH_LIST_OUTPUT=$(docker exec vault sh -c "vault auth list -format=json")

JWT_ACCESSOR_VALUE=$(echo "${AUTH_LIST_OUTPUT}" | grep accessor | head -1 | awk '{print $2}' | tr -d '"' | tr -d ',' | tr -d '[:space:]')
echo ">>> found jwt accessor : ${JWT_ACCESSOR_VALUE}"

echo
echo ">> writing alias"
# echo "using ${KEYCLOAK_TEST_USER}"
# echo "using ${JWT_ACCESSOR_VALUE}"
# echo "using ${ENTITY_ID}"
STRUCTURE="{\\\"name\\\":\\\"${KEYCLOAK_TEST_USER}\\\",\\\"mount_accessor\\\":\\\"${JWT_ACCESSOR_VALUE}\\\",\\\"canonical_id\\\":\\\"${ENTITY_ID}\\\"}"
docker exec vault sh -c "echo ${STRUCTURE} | tr -d '[:space:]' > alias.json; echo 'catting alias.json'; cat alias.json ; vault write identity/entity-alias @alias.json;" # rm alias.json;"

STRUCTURE="{\\\"name\\\":\\\"${KEYCLOAK_TEST_USER_TWO}\\\",\\\"mount_accessor\\\":\\\"${JWT_ACCESSOR_VALUE}\\\",\\\"canonical_id\\\":\\\"${ENTITY_ID_TWO}\\\"}"
docker exec vault sh -c "echo ${STRUCTURE} | tr -d '[:space:]' > alias.json; echo 'catting alias.json'; cat alias.json ; vault write identity/entity-alias @alias.json;" # rm alias.json;"


# enable identity tokens
echo
echo ">> enabling identity tokens"
docker exec vault sh -c "echo '{\"rotation_period\":\"24h\",\"allowed_client_ids\":[\"${KEYCLOAK_CLIENT_ID}\"]}' > test-key.json; vault write identity/oidc/key/test-key @test-key.json; rm test-key.json;"
echo


# match key and insert custom info into the jwt
echo
echo ">> matching key and inserting custom info into the jwt"
# vault-datastructure.json.tpl has the template parameter which is supposed to be
# json escaped or base64 escaped string and the braces have to be spaced apart 
# because templating code requres {{}} which when followed by another brace
# messes up Vault and it complains that there is a mismatch in balance of braces
VAULT_IDENTITY_ROLE_TEMPLATE=$(envsubst < ${PWD}/etc/setup/templates/configs/vault/vault-datastructure.json.tpl)
docker exec vault sh -c "echo '${VAULT_IDENTITY_ROLE_TEMPLATE}' > test-role.json; vault write identity/oidc/role/test-role @test-role.json; rm test-role.json;"
echo

# ---


