#!/usr/bin/env bash

set -Euo pipefail

LOGFILE=tmp/progress.txt

# make sure we have all the env vars:
source env.sh

# this is the name of the ingest service (in case it changes)
ingest="candig-ingest"

# This script runs after the container is composed.

# This script will set up a full vault environment on your local CanDIGv2 cluster

# Automates instructions written at
# https://github.com/CanDIG/CanDIGv2/blob/stable/docs/configure-vault.md

# Related resources:
# https://www.bogotobogo.com/DevOps/Docker/Docker-Vault-Consul.php
# https://learn.hashicorp.com/tutorials/vault/identity
# https://stackoverflow.com/questions/35703317/docker-exec-write-text-to-file-in-container
# https://www.vaultproject.io/api-docs/secret/identity/entity#batch-delete-entities

vault=$(docker ps -a --format "{{.Names}}" | grep vault_1 | awk '{print $1}')
docker cp lib/vault/tmp/vault-config.json $vault:/vault/config/

# if vault isn't started, start it:
docker restart $vault

echo ">> waiting for vault to start"
docker ps --format "{{.Names}}" | grep vault_1
while [ $? -ne 0 ]
do
  echo "..."
  sleep 1
  docker ps --format "{{.Names}}" | grep vault_1
done
sleep 10

# gather keys and login token
stuff=$(docker exec $vault vault operator init) # | head -7 | rev | cut -d " " -f1 | rev)
if [[ $? -eq 0 ]]; then
  echo ">> initialized vault, saving keys"

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
  touch tmp/vault/keys.txt
  echo -e "keys: \n${key_1}" > tmp/vault/keys.txt
  echo -e "${key_2}" >> tmp/vault/keys.txt
  echo -e "${key_3}" >> tmp/vault/keys.txt
  echo -e "${key_4}" >> tmp/vault/keys.txt
  echo -e "${key_5}" >> tmp/vault/keys.txt
  echo -e "root: \n${key_root}" >> tmp/vault/keys.txt

  docker cp tmp/vault/keys.txt $vault:/vault/config/

else
  echo ">> retrieving keys"
  key_1=$(head -n 2 tmp/vault/keys.txt | tail -n 1)
  key_2=$(head -n 3 tmp/vault/keys.txt | tail -n 1)
  key_3=$(head -n 4 tmp/vault/keys.txt | tail -n 1)

  key_root=$(tail -n 1 tmp/vault/keys.txt)
fi
echo $key_root
echo ">> attempting to automatically unseal vault:"
docker exec $vault sh -c "vault operator unseal ${key_1}"
docker exec $vault sh -c "vault operator unseal ${key_2}"
docker exec $vault sh -c "vault operator unseal ${key_3}"

# login
echo
echo ">> logging in automatically -- " #copy and paste this: ${key_root}"
docker exec $vault sh -c "vault login ${key_root}"

# configuration
# audit file
echo
echo ">> enabling audit file"
docker exec $vault sh -c "vault audit enable file file_path=/vault/vault-audit.log"

# enable jwt
echo
echo ">> enabling jwt"
docker exec $vault sh -c "vault auth enable jwt"

# enable approle
echo
echo ">> enabling approle"
docker exec $vault sh -c "vault auth enable approle"

# tyk policy
echo
echo ">> setting up tyk user-claims policy"
docker exec $vault sh -c "echo 'path \"identity/oidc/token/*\" {capabilities = [\"create\", \"read\"]}' > tyk-claims-policy.hcl; vault policy write tyk-claims tyk-claims-policy.hcl"

echo
echo ">> setting up aws policy"
docker exec $vault sh -c "echo 'path \"aws/*\" {capabilities = [\"create\", \"update\", \"read\", \"delete\"]}' > aws-policy.hcl; vault policy write aws aws-policy.hcl"

echo
echo ">> enable kv store for aws secrets"
docker exec $vault vault secrets enable -path="aws" -description="AWS-style ID/secret pairs" kv

echo ">> setting up approle policy"
docker exec $vault sh -c "echo 'path \"auth/approle/role/*\" {capabilities = [\"create\", \"update\", \"read\", \"delete\"]}' > approle-policy.hcl; vault policy write approle approle-policy.hcl"

echo
echo ">> setting up approle role"
cidr_block=$(docker network inspect --format "{{json .IPAM.Config}}" candigv2_default | jq '.[0].Gateway')
cidr_block=$(echo ${cidr_block} | tr -d '"')
cidr_block="${cidr_block}/27"
if [ $CANDIG_DEBUG_MODE -eq 1 ]; then
  echo "{}" > lib/vault/tmp/temp.json
else
  echo "{\"bound_cidrs\": [\"${cidr_block}\"]}" > lib/vault/tmp/temp.json
fi
curl --request POST --header "X-Vault-Token: ${key_root}" --data @lib/vault/tmp/temp.json $VAULT_SERVICE_PUBLIC_URL/v1/auth/token/roles/approle
rm lib/vault/tmp/temp.json

echo
echo ">> setting up approle token"
approle_token=$(cat tmp/secrets/vault-approle-token)
echo "{\"id\": \"${approle_token}\", \"policies\": [\"approle\"], \"periodic\": \"24h\"}" > lib/vault/tmp/temp.json
curl --request POST --header "X-Vault-Token: ${key_root}" --data @lib/vault/tmp/temp.json $VAULT_SERVICE_PUBLIC_URL/v1/auth/token/create/approle
rm lib/vault/tmp/temp.json

## SPECIAL STORES ACCESS
# Ingest needs access to the opa store's access path:
docker exec $vault sh -c "echo 'path \"opa/access\" {capabilities = [\"update\", \"read\", \"delete\"]}' >> ${ingest}-policy.hcl; vault policy write ${ingest} ${ingest}-policy.hcl"

# Federation needs access to the opa store's data path (to add servers):
docker exec $vault sh -c "echo 'path \"opa/data\" {capabilities = [\"update\", \"read\", \"delete\"]}' >> federation-policy.hcl; vault policy write federation federation-policy.hcl"


# user claims
echo
echo ">> setting up user claims"
docker exec $vault sh -c "vault write auth/jwt/role/researcher user_claim=preferred_username bound_audiences=${KEYCLOAK_CLIENT_ID} role_type=jwt policies=tyk-claims ttl=1h"

# site admin should always be able to access aws secrets
docker exec $vault sh -c "vault write auth/jwt/role/site_admin user_claim=site_admin bound_audiences=${KEYCLOAK_CLIENT_ID} role_type=jwt policies=aws ttl=1h"

# configure jwt
echo
echo ">> configuring jwt stuff"
docker exec $vault sh -c "vault write auth/jwt/config oidc_discovery_url=\"${KEYCLOAK_PUBLIC_URL}/auth/realms/candig\" bound_issuer=\"${KEYCLOAK_PUBLIC_URL}/auth/realms/candig\" default_role=\"researcher\""

# create users
echo
KEYCLOAK_TEST_USER="$(cat tmp/secrets/keycloak-test-user)"
echo ">> creating user $KEYCLOAK_TEST_USER"
export TEMPLATE_DATASET_PERMISSIONS=4
TEST_USER_PERMISSIONS_DATASTRUCTURE=$(envsubst < lib/vault/configuration_templates/vault-entity-entitlements.json.tpl)

test_user_output=$(docker exec $vault sh -c "echo '${TEST_USER_PERMISSIONS_DATASTRUCTURE}' > ${KEYCLOAK_TEST_USER}.json; vault write identity/entity @${KEYCLOAK_TEST_USER}.json; rm ${KEYCLOAK_TEST_USER}.json;")

ENTITY_ID=$(echo "${test_user_output}" | grep id | awk '{print $2}')
echo ">>> found entity id : ${ENTITY_ID}"


KEYCLOAK_TEST_USER_TWO="$(cat tmp/secrets/keycloak-test-user2)"
echo ">> creating user $KEYCLOAK_TEST_USER_TWO"
export TEMPLATE_DATASET_PERMISSIONS=1
TEST_USER_TWO_PERMISSIONS_DATASTRUCTURE=$(envsubst < lib/vault/configuration_templates/vault-entity-entitlements.json.tpl)

test_user_output_two=$(docker exec $vault sh -c "echo '${TEST_USER_TWO_PERMISSIONS_DATASTRUCTURE}' > ${KEYCLOAK_TEST_USER_TWO}.json; vault write identity/entity @${KEYCLOAK_TEST_USER_TWO}.json; rm ${KEYCLOAK_TEST_USER_TWO}.json;")

ENTITY_ID_TWO=$(echo "${test_user_output_two}" | grep id | awk '{print $2}')
echo ">>> found entity id 2: ${ENTITY_ID_TWO}"



# setup aliases
echo
echo ">> setting up alias for $KEYCLOAK_TEST_USER"
AUTH_LIST_OUTPUT=$(docker exec $vault sh -c "vault auth list -format=json")

JWT_ACCESSOR_VALUE=$(echo "${AUTH_LIST_OUTPUT}" | grep accessor | head -1 | awk '{print $2}' | tr -d '"' | tr -d ',' | tr -d '[:space:]')
echo ">>> found jwt accessor : ${JWT_ACCESSOR_VALUE}"

echo
echo ">> writing alias"
# echo "using ${KEYCLOAK_TEST_USER}"
# echo "using ${JWT_ACCESSOR_VALUE}"
# echo "using ${ENTITY_ID}"
STRUCTURE="{\\\"name\\\":\\\"${KEYCLOAK_TEST_USER}\\\",\\\"mount_accessor\\\":\\\"${JWT_ACCESSOR_VALUE}\\\",\\\"canonical_id\\\":\\\"${ENTITY_ID}\\\"}"
docker exec $vault sh -c "echo ${STRUCTURE} | tr -d '[:space:]' > alias.json; echo 'catting alias.json'; cat alias.json ; vault write identity/entity-alias @alias.json;" # rm alias.json;"

STRUCTURE="{\\\"name\\\":\\\"${KEYCLOAK_TEST_USER_TWO}\\\",\\\"mount_accessor\\\":\\\"${JWT_ACCESSOR_VALUE}\\\",\\\"canonical_id\\\":\\\"${ENTITY_ID_TWO}\\\"}"
docker exec $vault sh -c "echo ${STRUCTURE} | tr -d '[:space:]' > alias.json; echo 'catting alias.json'; cat alias.json ; vault write identity/entity-alias @alias.json;" # rm alias.json;"


# enable identity tokens
echo
echo ">> enabling identity tokens"
docker exec $vault sh -c "echo '{\"rotation_period\":\"24h\",\"allowed_client_ids\":[\"${KEYCLOAK_CLIENT_ID}\"]}' > test-key.json; vault write identity/oidc/key/test-key @test-key.json; rm test-key.json;"
echo


# match key and insert custom info into the jwt
echo
echo ">> matching key and inserting custom info into the jwt"
# vault-datastructure.json.tpl has the template parameter which is supposed to be
# json escaped or base64 escaped string and the braces have to be spaced apart
# because templating code requres {{}} which when followed by another brace
# messes up Vault and it complains that there is a mismatch in balance of braces
VAULT_IDENTITY_ROLE_TEMPLATE=$(envsubst < lib/vault/configuration_templates/vault-datastructure.json.tpl)
docker exec $vault sh -c "echo '${VAULT_IDENTITY_ROLE_TEMPLATE}' > researcher.json; vault write identity/oidc/role/researcher @researcher.json; rm researcher.json;"

vault_runner=$(docker ps -a --format "{{.Names}}" | grep vault-runner_1 | awk '{print $1}')
docker restart $vault_runner

if [ -f tmp/vault/service_stores.txt ]; then
    echo ">> creating service stores"
    while read service; do
        bash create_service_store.sh $service
    done <tmp/vault/service_stores.txt
fi
