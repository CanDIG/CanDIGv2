#!/usr/bin/env bash

export VAULT_APPROLE_TOKEN=$(cat /run/secrets/vault-approle-token)
export VAULT_S3_TOKEN=$(cat /run/secrets/vault-s3-token)
export KEY_ROOT=$(tail -n 1 /vault/config/keys.txt)


echo "renewing aws token"
curl --request POST --header "X-Vault-Token: ${VAULT_S3_TOKEN}" $VAULT_URL/v1/auth/token/renew-self > finish1.json
grep "error" finish1.json
if [[ $? -eq 0 ]]; then
    echo "creating aws token"
    echo "{\"id\": \"${VAULT_S3_TOKEN}\", \"policies\": [\"aws\"], \"periodic\": \"24h\"}" > token.json
    curl --request POST --header "X-Vault-Token: ${KEY_ROOT}" --data @token.json $VAULT_URL/v1/auth/token/create
fi
rm finish1.json

echo "renewing approle token"
curl --request POST --header "X-Vault-Token: ${VAULT_APPROLE_TOKEN}" $VAULT_URL/v1/auth/token/renew-self > finish.json
grep "error" finish.json
if [[ $? -eq 0 ]]; then
    echo "creating approle token"
    echo "{\"id\": \"${VAULT_APPROLE_TOKEN}\", \"policies\": [\"approle\"], \"periodic\": \"24h\"}" > token.json
    curl --request POST --header "X-Vault-Token: ${KEY_ROOT}" --data @token.json $VAULT_URL/v1/auth/token/create/approle
fi
rm finish.json
