#! /usr/bin/env bash
# This script will set up a full vault environment on your local CanDIGv2 cluster

# Automates instructions written at
# https://github.com/CanDIG/CanDIGv2/blob/stable/docs/configure-vault.md

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
echo "enabling jwt"
docker exec -it vault sh -c "vault auth enable jwt"

# audit file
echo
echo ">> setting up tyk policy"
docker exec -it vault sh -c "echo 'path \"identity/oidc/token/*\" {capabilities = [\"create\", \"read\"]}' >> vault-policy.hcl; vault policy write tyk vault-policy.hcl"

# user claims
echo
echo ">> setting up user claims"
docker exec -it vault sh -c "vault write auth/jwt/role/test-role user_claim=preferred_username bound_audiences=cq_candig role_type=jwt policies=tyk ttl=1h"

# user claims
echo
echo ">> configuring jwt stuff"
docker exec -it vault sh -c "vault write auth/jwt/config oidc_discovery_url=\"${KEYCLOAK_SERVICE_PUBLIC_URL}/auth/realms/candig\" default_role=\"test-role\""


# ---


# sudo rm -r data/ ;sudo rm -r logs/ ; sudo rm -r policies/