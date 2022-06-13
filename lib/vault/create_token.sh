#!/usr/bin/env bash

set -Euo pipefail


export ROOT=$(tail -n 1 /vault/config/keys.txt)
export VAULT_S3_TOKEN=$(cat /run/secrets/vault-s3-token)
echo '{ "id": "'$VAULT_S3_TOKEN'", "policies": ["aws"], "period":"5h" }' > token.json
curl --request POST --header "X-Vault-Token: "$ROOT"" --data @token.json http://$VAULT_URL/v1/auth/token/create
