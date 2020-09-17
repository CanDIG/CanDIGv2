#! /usr/bin/env bash
# This script will set up a full vault environment on your local CanDIGv2 cluster

# Automates instructions written at
# https://github.com/CanDIG/CanDIGv2/blob/stable/docs/configure-vault.md

# Related resources:
# https://www.bogotobogo.com/DevOps/Docker/Docker-Vault-Consul.php
# https://learn.hashicorp.com/tutorials/vault/identity
# https://stackoverflow.com/questions/35703317/docker-exec-write-text-to-file-in-container
# https://www.vaultproject.io/api-docs/secret/identity/entity#batch-delete-entities


# vault-config.json
echo "Working on vault-config.json .."
mkdir ${PWD}/lib/vault/config
envsubst < ${PWD}/etc/setup/templates/configs/vault/vault-config.json.tpl > ${PWD}/lib/vault/config/vault-config.json

# boot container
docker-compose -f ${PWD}/lib/vault/docker-compose.yml up -d

# -- todo: run only if not already initialized --
# gather keys and login token
stuff=$(docker exec -it vault sh -c "vault operator init") # | head -7 | rev | cut -d " " -f1 | rev)

echo "found stuff as ${stuff}"

key_1=$(echo -n "${stuff}" | grep 'Unseal Key 1: ' | awk '{print $4}' | tr -d '[:space:]')
key_2=$(echo -n "${stuff}" | grep 'Unseal Key 2: ' | awk '{print $4}' | tr -d '[:space:]')
key_3=$(echo -n "${stuff}" | grep 'Unseal Key 3: ' | awk '{print $4}' | tr -d '[:space:]')
key_4=$(echo -n "${stuff}" | grep 'Unseal Key 4: ' | awk '{print $4}' | tr -d '[:space:]')
key_5=$(echo -n "${stuff}" | grep 'Unseal Key 5: ' | awk '{print $4}' | tr -d '[:space:]')
key_root=$(echo -n "${stuff}" | grep 'Initial Root Token: ' | awk '{print $4}' | tr -d '[:space:]')

echo "found key1: ${key_1}"
echo "found key2: ${key_2}"
echo "found key3: ${key_3}"
echo "found root: ${key_root}"


echo
echo "Please provide the above keys to the following prompts in order to unseal the vault and login as root;"
echo


# result=$(docker exec -it -e key=$key_1 vault sh -c "echo \${key}; # vault operator unseal \${key}")
# echo $result
# todo: automate key inputs
docker exec -it vault sh -c "vault operator unseal \${key_1}"
docker exec -it vault sh -c "vault operator unseal \${key_2}"
docker exec -it vault sh -c "vault operator unseal \${key_3}"

# login
echo
echo ">> logging in with ${key_root}"
docker exec -it vault sh -c "vault login \${key_root}"

# configuration
# audit file
echo
echo ">> enabling audit file"
docker exec -it vault sh -c "vault audit enable file file_path=/tmp/vault-audit.log"

# enable jwt
echo
echo ">> enabling jwt"
docker exec -it vault sh -c "vault auth enable jwt"

# tyk policy
echo
echo ">> setting up tyk policy"
docker exec -it vault sh -c "echo 'path \"identity/oidc/token/*\" {capabilities = [\"create\", \"read\"]}' >> vault-policy.hcl; vault policy write tyk vault-policy.hcl"

# user claims
echo
echo ">> setting up user claims"
docker exec -it vault sh -c "vault write auth/jwt/role/test-role user_claim=preferred_username bound_audiences=cq_candig role_type=jwt policies=tyk ttl=1h"

# configure jwt
echo
echo ">> configuring jwt stuff"
docker exec -it vault sh -c "vault write auth/jwt/config oidc_discovery_url=\"${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/realms/candig\" default_role=\"test-role\""


# create user
echo
echo ">> creating user $KC_TEST_USER"
test_user_output=$(docker exec -it vault sh -c "echo '{\"name\":\"${KC_TEST_USER}\",\"metadata\":{\"dataset123\":4}}' > bob.json; vault write identity/entity @bob.json; rm bob.json;")

ENTITY_ID=$(echo "${test_user_output}" | grep id | awk '{print $2}' | tr -d '[:space:]')
echo ">>> found entity id : ${ENTITY_ID}"

# setup alias
echo ">> setting up alias for $KC_TEST_USER"
AUTH_LIST_OUTPUT=$(docker exec -it vault sh -c "vault auth list -format=json")
#echo "auth list output:"
#echo "${AUTH_LIST_OUTPUT}"

JWT_ACCESSOR_VALUE=$(echo "${AUTH_LIST_OUTPUT}" | grep accessor | head -1 | awk '{print $2}' | tr -d '"' | tr -d ',' | tr -d '[:space:]')
echo ">>> found jwt accessor : ${JWT_ACCESSOR_VALUE}"

#exit 0

echo ">> writing alias"
docker exec -it vault sh -c "echo '{\"name\":\"${KC_TEST_USER}\",\"mount_accessor\":\"${JWT_ACCESSOR_VALUE}\",\"canonical_id\":\"${ENTITY_ID}\"}' > alias.json; vault write identity/entity-alias @alias.json; rm alias.json;"



# enable identity tokens
echo ">> enabling identity tokens"
docker exec -it vault sh -c "echo '{\"rotation_period\":\"24h\",\"allowed_client_ids\":[\"cq_candig\"]}' > test-key.json; vault write identity/oidc/key/test-key @test-key.json; rm test-key.json;"
echo


# match key and insert custom info into the jwt
echo ">> matching key and inserting custom info into the jwt"
docker exec -it vault sh -c "echo '{\"key\":\"test-key\",\"client_id\":\"${KC_CLIENT_ID}\",\"template\":\"{\\\"permissions\\\":{{identity.entity.metadata}} }\"}' > test-role.json; vault write identity/oidc/role/test-role @test-role.json; rm test-role.json;"
echo


# ---


