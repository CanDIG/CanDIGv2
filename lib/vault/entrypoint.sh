#!/usr/bin/env bash

set -Euo pipefail


if [[ -f "initial_setup" ]]; then
    rm initial_setup
else
    sleep 10
    # unseal vault
    KEY=$(head -n 2 /vault/config/keys.txt | tail -n 1)
    echo '{ "key": "'$KEY'" }' > payload.json
    curl --request POST --data @payload.json http://vault:8200/v1/sys/unseal
    KEY=$(head -n 3 /vault/config/keys.txt | tail -n 1)
    echo '{ "key": "'$KEY'" }' > payload.json
    curl --request POST --data @payload.json http://vault:8200/v1/sys/unseal
    KEY=$(head -n 4 /vault/config/keys.txt | tail -n 1)
    echo '{ "key": "'$KEY'" }' > payload.json
    curl --request POST --data @payload.json http://vault:8200/v1/sys/unseal
    
fi

ROOT=$(tail -n 1 /vault/config/keys.txt)
export VAULT_S3_TOKEN=$(cat /run/secrets/vault-s3-token)
echo '{ "id": "'$VAULT_S3_TOKEN'", "policies": ["aws"], "period":"5h" }' > token.json
curl --request POST --header "X-Vault-Token: "$ROOT"" --data @token.json http://vault:8200/v1/auth/token/create

top